#!/usr/bin/env python3
"""Fetch an Azure DevOps pull request for review.

Writes into the work directory (default ~/.cache/pr-review/<repo>-<id>/):
  context.json  PR metadata, commits, linked work items, comment threads
  diff.patch    git diff from the merge base to the PR's source commit
  files.json    one entry per changed file, with its hunks
  terraform-plan-<build>-<n>.txt
                the output of each Terraform plan task in the PR's CI builds,
                without the state refresh lines; listed in context.json as
                terraformPlans, with the resources the plan acts on
  worktree/     a detached checkout of the PR's source commit, for reading
                code and running tests without touching the user's clone

Prints a short JSON summary on stdout.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "azure-devops" / "scripts"))
import ado  # noqa: E402

DEV_DIR = Path.home() / "dev"
CACHE_DIR = Path.home() / ".cache" / "pr-review"
# Files a reviewer normally skims: generated, vendored or lock files.
MECHANICAL_PATTERNS = [
    r"(^|/)pnpm-lock\.yaml$", r"(^|/)package-lock\.json$", r"(^|/)yarn\.lock$",
    r"(^|/)packages\.lock\.json$", r"\.min\.(js|css)$", r"(^|/)Migrations/.*\.Designer\.cs$",
    r"ModelSnapshot\.cs$", r"\.snap$", r"(^|/)dist/", r"(^|/)generated/",
]


def run(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise SystemExit(f"error: {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout


def find_clone(repo: str, ssh_url: str, explicit: str | None, work: Path) -> Path:
    if explicit:
        return Path(explicit).expanduser()
    local = DEV_DIR / repo
    if (local / ".git").exists():
        return local
    clone = work / "clone"
    if not (clone / ".git").exists():
        run("git", "clone", "--no-checkout", "--quiet", ssh_url, str(clone))
    return clone


def fetch_commits(clone: Path, ctx: dict) -> None:
    pr_id = ctx["id"]
    needed = [ctx["sourceCommit"], ctx["targetCommit"]]
    have = all(
        subprocess.run(["git", "cat-file", "-e", f"{c}^{{commit}}"], cwd=clone, capture_output=True).returncode == 0
        for c in needed
    )
    if have:
        return
    # The merge ref holds both the target and the source commit as parents.
    refs = [f"+refs/pull/{pr_id}/merge:refs/remotes/pr/{pr_id}/merge"]
    refs.append(f"+{ctx['source']}:refs/remotes/pr/{pr_id}/source")
    refs.append(f"+{ctx['target']}:refs/remotes/pr/{pr_id}/target")
    subprocess.run(["git", "fetch", "--quiet", "origin", *refs], cwd=clone, capture_output=True, text=True)
    for commit in needed:
        run("git", "cat-file", "-e", f"{commit}^{{commit}}", cwd=clone)


def parse_diff(patch: str) -> list[dict]:
    """Split a unified git diff into files and hunks."""
    files: list[dict] = []
    current: dict | None = None
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            match = re.match(r"diff --git a/(.*) b/(.*)$", line)
            current = {
                "path": match.group(2) if match else line,
                "oldPath": match.group(1) if match else None,
                "status": "modified",
                "binary": False,
                "added": 0,
                "removed": 0,
                "hunks": [],
            }
            files.append(current)
            continue
        if current is None:
            continue
        if line.startswith("new file mode"):
            current["status"] = "added"
        elif line.startswith("deleted file mode"):
            current["status"] = "deleted"
        elif line.startswith("rename from "):
            current["status"] = "renamed"
            current["oldPath"] = line[len("rename from "):]
        elif line.startswith("rename to "):
            current["path"] = line[len("rename to "):]
        elif line.startswith("Binary files"):
            current["binary"] = True
        elif line.startswith("@@"):
            match = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(.*)", line)
            if match:
                current["hunks"].append(
                    {
                        "index": len(current["hunks"]),
                        "header": line,
                        "oldStart": int(match.group(1)),
                        "oldLines": int(match.group(2) or 1),
                        "newStart": int(match.group(3)),
                        "newLines": int(match.group(4) or 1),
                        "context": match.group(5).strip(),
                        "lines": [],
                    }
                )
        elif current["hunks"] and line[:1] in ("+", "-", " ", "\\"):
            current["hunks"][-1]["lines"].append(line)
            if line.startswith("+"):
                current["added"] += 1
            elif line.startswith("-"):
                current["removed"] += 1
    for f in files:
        if f["status"] == "modified" and f["oldPath"] == f["path"]:
            f["oldPath"] = None
        f["mechanicalHint"] = any(re.search(p, f["path"]) for p in MECHANICAL_PATTERNS)
    return files

# A Terraform plan task: "Terraform Plan", "Terraform : plan", "terraform plan (dev)".
PLAN_TASK = re.compile(r"terraform.*\bplan\b|\bplan\b.*terraform", re.I)
# State refresh and data source reads: hundreds of lines that say nothing about the plan.
PLAN_NOISE = re.compile(r": (Refreshing state|Reading|Read complete after|Still reading)\.\.\.|: Read complete after ")
PLAN_RESOURCE = re.compile(r"^\s*# ([^(\s].*?) (will be|must be|has moved to) (.+?)\s*$")
PLAN_SUMMARY = re.compile(r"^(Plan: .*|No changes\..*|Error: .*)$", re.M)


def plan_resources(text: str) -> list[dict]:
    """The resources a plan acts on, in plan order: address and action."""
    out = []
    for line in text.splitlines():
        m = PLAN_RESOURCE.match(line)
        if not m:
            continue
        verb, rest = m.group(2), m.group(3)
        action = f"moved to {rest}" if verb == "has moved to" else rest
        out.append({"address": m.group(1), "action": action})
    return out


def fetch_terraform_plans(client: "ado.Client", ctx: dict, work: Path) -> list[dict]:
    """Save the output of every Terraform plan task in the PR's CI builds."""
    plans = []
    for b in (ctx.get("checks") or {}).get("builds", []):
        try:
            records = client.request("GET", client.url(f"build/builds/{b['id']}/timeline")).get("records", [])
        except ado.AdoError:
            continue
        by_id = {r["id"]: r for r in records}
        tasks = [r for r in records if r.get("type") == "Task" and PLAN_TASK.search(r.get("name") or "") and r.get("log")]
        for rec in sorted(tasks, key=lambda r: r.get("startTime") or ""):
            log = client.request("GET", client.url(f"build/builds/{b['id']}/logs/{rec['log']['id']}"), text=True)
            lines = [re.sub(r"^\S+Z ", "", line) for line in str(log).splitlines()]
            if "Starting Command Output" in "\n".join(lines):
                lines = lines[next(i for i, l in enumerate(lines) if "Starting Command Output" in l) + 1 :]
            lines = [l for l in lines if not PLAN_NOISE.search(l)]
            text = "\n".join(lines).strip() + "\n"
            if not re.search(r"Terraform will perform|No changes\.|Error: |Plan: ", text):
                continue
            name = f"terraform-plan-{b['id']}-{len(plans) + 1}.txt"
            (work / name).write_text(text)
            job = by_id.get(rec.get("parentId")) or {}
            summary = PLAN_SUMMARY.findall(text)
            plans.append(
                {
                    "file": name,
                    "buildId": b["id"],
                    "buildUrl": b.get("url"),
                    "pipeline": b.get("pipeline"),
                    "job": job.get("name"),
                    "task": rec.get("name"),
                    "result": rec.get("result"),
                    "summary": summary[0] if summary else None,
                    "resources": plan_resources(text),
                }
            )
    return plans


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("id", type=int, help="pull request id")
    parser.add_argument("--clone", help="local clone of the PR's repository (default: ~/dev/<repo>, else a fresh clone)")
    parser.add_argument("--out", help="work directory (default: ~/.cache/pr-review/<repo>-<id>)")
    parser.add_argument("--org")
    parser.add_argument("--project")
    args = parser.parse_args()

    client = ado.Client(args.org or ado.DEFAULT_ORG, args.project or ado.DEFAULT_PROJECT)
    try:
        ctx = ado.pr_context(client, args.id)
    except ado.AdoError as err:
        raise SystemExit(f"error: {err}")
    if not ctx.get("sourceCommit") or not ctx.get("targetCommit"):
        raise SystemExit("error: the PR has no merge source/target commits yet; try again once Azure DevOps has evaluated it.")

    work = Path(args.out).expanduser() if args.out else CACHE_DIR / f"{ctx['repository']}-{args.id}"
    work.mkdir(parents=True, exist_ok=True)
    clone = find_clone(ctx["repository"], ctx["sshUrl"], args.clone, work)
    fetch_commits(clone, ctx)

    base = run("git", "merge-base", ctx["targetCommit"], ctx["sourceCommit"], cwd=clone).strip()
    patch = run("git", "diff", "-M", "--no-color", "--no-ext-diff", base, ctx["sourceCommit"], cwd=clone)
    files = parse_diff(patch)

    worktree = work / "worktree"
    if worktree.exists():
        subprocess.run(["git", "worktree", "remove", "--force", str(worktree)], cwd=clone, capture_output=True)
    run("git", "worktree", "add", "--detach", "--quiet", str(worktree), ctx["sourceCommit"], cwd=clone)

    ctx["mergeBase"] = base
    ctx["terraformPlans"] = fetch_terraform_plans(client, ctx, work)
    ctx["clone"] = str(clone)
    ctx["worktree"] = str(worktree)
    (work / "context.json").write_text(json.dumps(ctx, indent=2, ensure_ascii=False))
    (work / "diff.patch").write_text(patch)
    (work / "files.json").write_text(json.dumps(files, indent=2, ensure_ascii=False))

    json.dump(
        {
            "workDir": str(work),
            "pr": ctx["id"],
            "title": ctx["title"],
            "repository": ctx["repository"],
            "clone": str(clone),
            "worktree": str(worktree),
            "diff": f"git -C {worktree} diff {base[:12]}..{ctx['sourceCommit'][:12]}",
            "files": len(files),
            "added": sum(f["added"] for f in files),
            "removed": sum(f["removed"] for f in files),
            "mechanicalHints": [f["path"] for f in files if f["mechanicalHint"]],
            "workItems": [w["id"] for w in ctx["workItems"]],
            "commentThreads": len(ctx["threads"]),
            "terraformPlans": [
                {"file": p["file"], "job": p["job"], "summary": p["summary"]} for p in ctx["terraformPlans"]
            ],
        },
        sys.stdout,
        indent=2,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
