#!/usr/bin/env python3
"""Small Azure DevOps REST client for pull requests and work items.

Standard library only. The personal access token is read at run time from,
in order: the AZURE_DEVOPS_PAT environment variable, the desktop keyring
(secret-tool, attributes service=azure-devops org=<org>), or the file
~/.config/azure-devops/pat. It is never printed.

Every command prints JSON on stdout. Errors go to stderr with exit code 1.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_VERSION = "7.1"
DEFAULT_ORG = "datumplatforminteractive"
DEFAULT_PROJECT = "Platform Interactive"
# Work items land here unless --area / --iteration say otherwise. The
# iteration changes yearly: update it when the new roadmap iteration starts.
DEFAULT_AREA = r"Platform Interactive\Infrastructure Intelligence"
DEFAULT_ITERATION = r"Platform Interactive\2026 Roadmap"
PAT_FILE = Path.home() / ".config" / "azure-devops" / "pat"
# Azure Repos rejects pull request descriptions longer than this.
MAX_PR_DESCRIPTION = 4000
REMOTE_PATTERN = re.compile(
    r"(?:ssh\.dev\.azure\.com:v3/|dev\.azure\.com/(?:[^/@]+@)?)"
    r"(?P<org>[^/]+)/(?P<project>[^/]+)/(?:_git/)?(?P<repo>[^/]+?)(?:\.git)?/?$"
)


class AdoError(Exception):
    pass


# --------------------------------------------------------------------------- #
# Context: organisation, project, repository, token
# --------------------------------------------------------------------------- #

def git(*args: str, cwd: str | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise AdoError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def remote_context(cwd: str | None) -> dict[str, str] | None:
    """Return org, project and repo parsed from the origin remote, if any."""
    try:
        url = git("remote", "get-url", "origin", cwd=cwd)
    except AdoError:
        return None
    match = REMOTE_PATTERN.search(url)
    if not match:
        return None
    return {k: urllib.parse.unquote(v) for k, v in match.groupdict().items()}


def resolve_context(args: argparse.Namespace) -> dict[str, str | None]:
    remote = remote_context(getattr(args, "cwd", None)) or {}
    return {
        "org": args.org or os.environ.get("AZURE_DEVOPS_ORG") or remote.get("org") or DEFAULT_ORG,
        "project": args.project
        or os.environ.get("AZURE_DEVOPS_PROJECT")
        or remote.get("project")
        or DEFAULT_PROJECT,
        "repo": getattr(args, "repo", None) or remote.get("repo"),
    }


def read_token(org: str) -> str:
    token = os.environ.get("AZURE_DEVOPS_PAT", "").strip()
    if token:
        return token
    try:
        result = subprocess.run(
            ["secret-tool", "lookup", "service", "azure-devops", "org", org],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    if PAT_FILE.is_file():
        token = PAT_FILE.read_text().strip()
        if token:
            return token
    raise AdoError(
        "No Azure DevOps token found. Store one with:\n"
        f"  secret-tool store --label='Azure DevOps PAT ({org})' service azure-devops org {org}\n"
        "(or set AZURE_DEVOPS_PAT, or write it to ~/.config/azure-devops/pat with mode 600)."
    )


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #

class Client:
    def __init__(self, org: str, project: str | None):
        self.org = org
        self.project = project
        token = read_token(org)
        self._auth = "Basic " + base64.b64encode(f":{token}".encode()).decode()

    def url(self, path: str, project_scoped: bool = True, **query: str) -> str:
        base = f"https://dev.azure.com/{urllib.parse.quote(self.org)}"
        if project_scoped:
            base += "/" + urllib.parse.quote(self.project or "")
        query = {"api-version": API_VERSION, **query}
        return f"{base}/_apis/{path}?{urllib.parse.urlencode(query)}"

    def request(
        self,
        method: str,
        url: str,
        body: object | None = None,
        content_type: str = "application/json",
        text: bool = False,
    ) -> dict | str:
        data = None if body is None else json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Authorization", self._auth)
        req.add_header("Accept", "text/plain" if text else "application/json")
        if data is not None:
            req.add_header("Content-Type", content_type)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = resp.read().decode(errors="replace")
                if text and resp.status == 200 and "html" not in (resp.headers.get("Content-Type") or ""):
                    return payload
                # An invalid token makes Azure DevOps redirect to a sign-in page.
                if "json" not in (resp.headers.get("Content-Type") or ""):
                    raise AdoError(
                        f"{method} {url} returned non-JSON (HTTP {resp.status}); "
                        "the token is probably invalid, expired or for another organisation."
                    )
                return json.loads(payload) if payload else {}
        except urllib.error.HTTPError as err:
            detail = err.read().decode(errors="replace")
            try:
                detail = json.loads(detail).get("message", detail)
            except (ValueError, AttributeError):
                pass
            if err.code in (401, 203):
                detail = f"authentication failed ({detail or 'check the token'})"
            if err.code == 403:
                detail = f"forbidden; the token may lack the scope for this call ({detail})"
            raise AdoError(f"{method} {url} -> HTTP {err.code}: {detail}") from None


# --------------------------------------------------------------------------- #
# Formatting
# --------------------------------------------------------------------------- #

def pr_web_url(org: str, project: str, repo: str, pr_id: int) -> str:
    return (
        f"https://dev.azure.com/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}"
        f"/_git/{urllib.parse.quote(repo)}/pullrequest/{pr_id}"
    )


def summarise_pr(pr: dict, org: str, project: str) -> dict:
    repo = pr.get("repository", {}).get("name", "")
    return {
        "id": pr.get("pullRequestId"),
        "url": pr_web_url(org, project, repo, pr["pullRequestId"]),
        "repository": repo,
        "status": pr.get("status"),
        "isDraft": pr.get("isDraft"),
        "title": pr.get("title"),
        "source": pr.get("sourceRefName"),
        "target": pr.get("targetRefName"),
        "createdBy": pr.get("createdBy", {}).get("displayName"),
        "creationDate": pr.get("creationDate"),
        "mergeStatus": pr.get("mergeStatus"),
        "autoComplete": bool(pr.get("autoCompleteSetBy")),
        "reviewers": [
            {"name": r.get("displayName"), "vote": r.get("vote"), "required": r.get("isRequired", False)}
            for r in pr.get("reviewers", [])
        ],
    }


def summarise_work_item(item: dict, org: str, project: str) -> dict:
    fields = item.get("fields", {})
    return {
        "id": item.get("id"),
        "url": f"https://dev.azure.com/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}/_workitems/edit/{item.get('id')}",
        "type": fields.get("System.WorkItemType"),
        "title": fields.get("System.Title"),
        "state": fields.get("System.State"),
        "areaPath": fields.get("System.AreaPath"),
        "iterationPath": fields.get("System.IterationPath"),
        "assignedTo": (fields.get("System.AssignedTo") or {}).get("displayName"),
        "tags": fields.get("System.Tags"),
    }


def ref(branch: str) -> str:
    return branch if branch.startswith("refs/") else f"refs/heads/{branch}"


def read_text(path: str | None) -> str | None:
    if path is None:
        return None
    return sys.stdin.read() if path == "-" else Path(path).read_text()


def emit(value: object) -> None:
    json.dump(value, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def require_repo(ctx: dict) -> str:
    if not ctx["repo"]:
        raise AdoError("No repository: pass --repo, or run inside a clone whose origin is Azure Repos.")
    return ctx["repo"]


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def connection_data(client: Client) -> dict:
    # connectionData is only served under a preview api-version.
    return client.request("GET", client.url("connectionData", project_scoped=False, **{"api-version": "7.1-preview"}))


def current_user_email(client: Client) -> str:
    user = connection_data(client).get("authenticatedUser", {})
    email = user.get("properties", {}).get("Account", {}).get("$value")
    if not email:
        raise AdoError("Could not find the token owner's account name to assign the work item to.")
    return email


def cmd_check(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    client = Client(ctx["org"], ctx["project"])
    user = connection_data(client).get("authenticatedUser", {})
    project = client.request("GET", client.url(f"projects/{urllib.parse.quote(ctx['project'])}", project_scoped=False))
    emit(
        {
            "org": ctx["org"],
            "project": project.get("name"),
            "user": user.get("providerDisplayName"),
            "account": user.get("properties", {}).get("Account", {}).get("$value"),
            "repo": ctx["repo"],
        }
    )


def cmd_list_prs(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    client = Client(ctx["org"], ctx["project"])
    query = {"searchCriteria.status": args.status, "$top": str(args.top)}
    if args.source:
        query["searchCriteria.sourceRefName"] = ref(args.source)
    if args.repo or ctx["repo"]:
        path = f"git/repositories/{urllib.parse.quote(require_repo(ctx))}/pullrequests"
    else:
        path = "git/pullrequests"
    data = client.request("GET", client.url(path, **query))
    emit([summarise_pr(pr, ctx["org"], ctx["project"]) for pr in data.get("value", [])])


def cmd_get_pr(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    client = Client(ctx["org"], ctx["project"])
    pr = client.request("GET", client.url(f"git/pullrequests/{args.id}"))
    summary = summarise_pr(pr, ctx["org"], ctx["project"])
    summary["description"] = pr.get("description")
    refs = client.request(
        "GET",
        client.url(
            f"git/repositories/{urllib.parse.quote(summary['repository'])}/pullRequests/{args.id}/workitems"
        ),
    )
    summary["workItems"] = [int(w["id"]) for w in refs.get("value", [])]
    emit(summary)


def pr_context(client: Client, pr_id: int) -> dict:
    """Everything a reviewer needs from the API about one pull request."""
    org, project = client.org, client.project or ""
    pr = client.request("GET", client.url(f"git/pullrequests/{pr_id}"))
    repo = pr["repository"]
    repo_path = f"git/repositories/{repo['id']}/pullRequests/{pr_id}"
    commits = client.request("GET", client.url(f"{repo_path}/commits", **{"$top": "200"})).get("value", [])
    threads = client.request("GET", client.url(f"{repo_path}/threads")).get("value", [])
    item_ids = [w["id"] for w in client.request("GET", client.url(f"{repo_path}/workitems")).get("value", [])]
    work_items = []
    if item_ids:
        items = client.request(
            "GET",
            client.url("wit/workitems", ids=",".join(str(i) for i in item_ids)),
        ).get("value", [])
        for item in items:
            summary = summarise_work_item(item, org, project)
            fields = item.get("fields", {})
            summary["description"] = fields.get("System.Description")
            summary["acceptanceCriteria"] = fields.get("Microsoft.VSTS.Common.AcceptanceCriteria")
            work_items.append(summary)
    comments = []
    for thread in threads:
        human = [c for c in thread.get("comments", []) if c.get("commentType") != "system"]
        if not human:
            continue
        context = thread.get("threadContext") or {}
        comments.append(
            {
                "status": thread.get("status"),
                "file": context.get("filePath"),
                "line": (context.get("rightFileStart") or {}).get("line"),
                "comments": [
                    {"author": c.get("author", {}).get("displayName"), "content": c.get("content")}
                    for c in human
                ],
            }
        )
    summary = summarise_pr(pr, org, project)
    summary["checks"] = pr_checks(client, pr)
    summary.update(
        {
            "description": pr.get("description"),
            "repositoryId": repo.get("id"),
            "sshUrl": repo.get("sshUrl"),
            "sourceCommit": (pr.get("lastMergeSourceCommit") or {}).get("commitId"),
            "targetCommit": (pr.get("lastMergeTargetCommit") or {}).get("commitId"),
            "mergeCommit": (pr.get("lastMergeCommit") or {}).get("commitId"),
            "commits": [
                {
                    "id": c.get("commitId"),
                    "author": c.get("author", {}).get("name"),
                    "date": c.get("author", {}).get("date"),
                    "message": c.get("comment"),
                }
                for c in commits
            ],
            "workItems": work_items,
            "threads": comments,
        }
    )
    return summary


def error_excerpt(lines: list[str], after: int = 6) -> str | None:
    """The first error block in a task log: the error line and a few after it."""
    for i, line in enumerate(lines):
        if re.match(r"\s*(Error:|error |ERROR|##\[error\]|.*: error [A-Z]+\d+)", line):
            return "\n".join(lines[i : i + after + 1]).strip()
    return None


def pr_checks(client: Client, pr: dict, log_lines: int = 60) -> dict:
    """Branch policies (build, reviewers, work items) and, for failed builds,
    the failing tasks and the tail of their logs. Build details need the
    token's Build (Read) scope; without it only the policy results are returned."""
    org, project = client.org, client.project or ""
    project_id = pr["repository"]["project"]["id"]
    artifact = f"vstfs:///CodeReview/CodeReviewId/{project_id}/{pr['pullRequestId']}"
    evaluations = client.request(
        "GET", client.url("policy/evaluations", artifactId=artifact, **{"api-version": "7.1-preview"})
    ).get("value", [])
    policies, builds, note = [], [], None
    for e in evaluations:
        cfg = e.get("configuration", {})
        settings = cfg.get("settings", {})
        build_id = (e.get("context") or {}).get("buildId")
        policies.append(
            {
                "policy": cfg.get("type", {}).get("displayName"),
                "name": settings.get("displayName"),
                "status": e.get("status"),
                "blocking": cfg.get("isBlocking"),
                "buildId": build_id,
                "buildUrl": f"https://dev.azure.com/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}/_build/results?buildId={build_id}" if build_id else None,
            }
        )
        if not build_id or note:
            continue
        try:
            build = client.request("GET", client.url(f"build/builds/{build_id}"))
        except AdoError as err:
            if "HTTP 401" in str(err) or "HTTP 403" in str(err):
                note = "Build details need the token's Build (Read) scope."
                continue
            raise
        entry = {
            "id": build_id,
            "pipeline": build.get("definition", {}).get("name"),
            "status": build.get("status"),
            "result": build.get("result"),
            "sourceVersion": build.get("sourceVersion"),
            "finished": build.get("finishTime"),
            "failedTasks": [],
            "url": f"https://dev.azure.com/{urllib.parse.quote(org)}/{urllib.parse.quote(project)}/_build/results?buildId={build_id}",
        }
        if build.get("result") not in (None, "succeeded"):
            timeline = client.request("GET", client.url(f"build/builds/{build_id}/timeline")).get("records", [])
            for rec in timeline:
                if rec.get("type") != "Task" or rec.get("result") not in ("failed", "canceled"):
                    continue
                task = {
                    "name": rec.get("name"),
                    "result": rec.get("result"),
                    "issues": [i.get("message") for i in rec.get("issues") or [] if i.get("type") == "error"][:10],
                    "logTail": None,
                }
                log_id = (rec.get("log") or {}).get("id")
                if log_id:
                    log = client.request("GET", client.url(f"build/builds/{build_id}/logs/{log_id}"), text=True)
                    lines = [re.sub(r"^\S+Z ", "", line) for line in str(log).splitlines()]
                    task["logTail"] = "\n".join(lines[-log_lines:])
                    task["errorExcerpt"] = error_excerpt(lines)
                entry["failedTasks"].append(task)
        builds.append(entry)
    return {"policies": policies, "builds": builds, "note": note}


def cmd_pr_checks(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    client = Client(ctx["org"], ctx["project"])
    pr = client.request("GET", client.url(f"git/pullrequests/{args.id}"))
    emit(pr_checks(client, pr))


def cmd_pr_context(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    emit(pr_context(Client(ctx["org"], ctx["project"]), args.id))


def cmd_create_pr(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    repo = require_repo(ctx)
    source = args.source or git("branch", "--show-current", cwd=args.cwd)
    if not source:
        raise AdoError("Detached HEAD: pass --source.")
    target = args.target
    if not target:
        try:
            target = git("symbolic-ref", "--short", "refs/remotes/origin/HEAD", cwd=args.cwd).removeprefix("origin/")
        except AdoError:
            raise AdoError("Could not find the default branch: pass --target.") from None
    description = read_text(args.description_file) or ""

    problems = []
    if len(description) > MAX_PR_DESCRIPTION:
        problems.append(
            f"description is {len(description)} characters; Azure Repos allows {MAX_PR_DESCRIPTION}"
        )
    if source == target:
        problems.append("source and target are the same branch")
    remote_head = git("ls-remote", "origin", ref(source), cwd=args.cwd)
    try:
        local_head = git("rev-parse", "--verify", f"refs/heads/{source}", cwd=args.cwd)
    except AdoError:
        local_head = ""  # no local branch of that name; trust origin
    if not remote_head:
        problems.append(f"branch {source} is not on origin; push it first")
    elif local_head and remote_head.split()[0] != local_head:
        problems.append(f"origin/{source} ({remote_head.split()[0][:8]}) differs from local {source} ({local_head[:8]}); push first")

    payload = {
        "sourceRefName": ref(source),
        "targetRefName": ref(target),
        "title": args.title,
        "description": description,
        "isDraft": args.draft,
        "workItemRefs": [{"id": str(w)} for w in args.work_item],
    }
    plan = {
        "org": ctx["org"],
        "project": ctx["project"],
        "repository": repo,
        "source": payload["sourceRefName"],
        "target": payload["targetRefName"],
        "title": args.title,
        "titleLength": len(args.title),
        "descriptionLength": len(description),
        "isDraft": args.draft,
        "workItems": args.work_item,
        "problems": problems,
    }
    if args.dry_run:
        emit({"dryRun": True, **plan})
        if problems:
            raise AdoError("dry run found problems: " + "; ".join(problems))
        return
    if problems:
        raise AdoError("Not creating the pull request: " + "; ".join(problems))

    client = Client(ctx["org"], ctx["project"])
    repo_path = f"git/repositories/{urllib.parse.quote(repo)}/pullrequests"
    existing = client.request(
        "GET",
        client.url(
            repo_path,
            **{
                "searchCriteria.status": "active",
                "searchCriteria.sourceRefName": payload["sourceRefName"],
                "searchCriteria.targetRefName": payload["targetRefName"],
            },
        ),
    ).get("value", [])
    if existing:
        found = summarise_pr(existing[0], ctx["org"], ctx["project"])
        raise AdoError(f"An active pull request already exists for this branch: {found['url']}")
    pr = client.request("POST", client.url(repo_path), payload)
    emit(summarise_pr(pr, ctx["org"], ctx["project"]))


def cmd_update_pr(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    client = Client(ctx["org"], ctx["project"])
    current = client.request("GET", client.url(f"git/pullrequests/{args.id}"))
    repo = current["repository"]["name"]
    body: dict[str, object] = {}
    if args.title:
        body["title"] = args.title
    description = read_text(args.description_file)
    if description is not None:
        if len(description) > MAX_PR_DESCRIPTION:
            raise AdoError(
                f"description is {len(description)} characters; Azure Repos allows {MAX_PR_DESCRIPTION}"
            )
        body["description"] = description
    if args.publish:
        body["isDraft"] = False
    if args.draft:
        body["isDraft"] = True
    if not body:
        raise AdoError("Nothing to update: pass --title, --description-file, --publish or --draft.")
    if args.dry_run:
        emit({"dryRun": True, "id": args.id, "repository": repo, "changes": {k: (v if k != "description" else f"<{len(v)} characters>") for k, v in body.items()}})
        return
    pr = client.request(
        "PATCH",
        client.url(f"git/repositories/{urllib.parse.quote(repo)}/pullrequests/{args.id}"),
        body,
    )
    emit(summarise_pr(pr, ctx["org"], ctx["project"]))


def cmd_get_work_item(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    client = Client(ctx["org"], ctx["project"])
    item = client.request("GET", client.url(f"wit/workitems/{args.id}", **{"$expand": "relations"}))
    summary = summarise_work_item(item, ctx["org"], ctx["project"])
    summary["description"] = item.get("fields", {}).get("System.Description")
    emit(summary)


def cmd_create_work_item(args: argparse.Namespace) -> None:
    ctx = resolve_context(args)
    ops: list[dict[str, object]] = [
        {"op": "add", "path": "/fields/System.Title", "value": args.title},
    ]
    fields = {
        "System.Description": read_text(args.description_file),
        "Microsoft.VSTS.Common.AcceptanceCriteria": read_text(args.acceptance_criteria_file),
        "System.AreaPath": args.area,
        "System.IterationPath": args.iteration,
        "System.Tags": "; ".join(args.tag) if args.tag else None,
    }
    client = None
    assignee = args.assign_to
    if assignee == "me":
        client = Client(ctx["org"], ctx["project"])
        assignee = current_user_email(client)
    if assignee:
        fields["System.AssignedTo"] = assignee
    for name, value in fields.items():
        if value is None:
            continue
        ops.append({"op": "add", "path": f"/fields/{name}", "value": value})
        if args.markdown and name in ("System.Description", "Microsoft.VSTS.Common.AcceptanceCriteria"):
            ops.append({"op": "add", "path": f"/multilineFieldsFormat/{name}", "value": "Markdown"})
    if args.parent:
        ops.append(
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": f"https://dev.azure.com/{urllib.parse.quote(ctx['org'])}/_apis/wit/workItems/{args.parent}",
                },
            }
        )
    if args.dry_run:
        emit({"dryRun": True, "org": ctx["org"], "project": ctx["project"], "type": args.type, "operations": ops})
        return
    client = client or Client(ctx["org"], ctx["project"])
    item = client.request(
        "POST",
        client.url(f"wit/workitems/${urllib.parse.quote(args.type)}"),
        ops,
        content_type="application/json-patch+json",
    )
    emit(summarise_work_item(item, ctx["org"], ctx["project"]))


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--org", help=f"organisation (default: from origin, else {DEFAULT_ORG})")
    common.add_argument("--project", help=f"project (default: from origin, else {DEFAULT_PROJECT})")
    common.add_argument("--cwd", help="git clone to read the origin remote and branches from (default: current directory)")

    parser = argparse.ArgumentParser(description="Azure DevOps pull requests and work items.")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("check", parents=[common], help="verify the token and show who it authenticates as")
    p.add_argument("--repo")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("list-prs", parents=[common], help="list pull requests")
    p.add_argument("--repo", help="repository (default: from origin; omit outside a clone for the whole project)")
    p.add_argument("--status", default="active", choices=["active", "completed", "abandoned", "all"])
    p.add_argument("--source", help="only pull requests from this branch")
    p.add_argument("--top", type=int, default=20)
    p.set_defaults(func=cmd_list_prs)

    p = sub.add_parser("get-pr", parents=[common], help="show one pull request, with description and linked work items")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_get_pr)

    p = sub.add_parser("pr-context", parents=[common], help="pull request, commits, linked work items and comment threads, for review")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_pr_context)

    p = sub.add_parser("pr-checks", parents=[common], help="branch policy and CI build results, with failing task logs")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_pr_checks)

    p = sub.add_parser("create-pr", parents=[common], help="open a pull request for a pushed branch")
    p.add_argument("--repo", help="repository (default: from origin)")
    p.add_argument("--source", help="source branch (default: current branch)")
    p.add_argument("--target", help="target branch (default: origin's default branch)")
    p.add_argument("--title", required=True)
    p.add_argument("--description-file", help="Markdown file with the description, or - for stdin")
    p.add_argument("--work-item", type=int, action="append", default=[], help="work item id to link (repeatable)")
    p.add_argument("--draft", action="store_true", help="open as a draft")
    p.add_argument("--dry-run", action="store_true", help="validate and print what would be sent; send nothing")
    p.set_defaults(func=cmd_create_pr)

    p = sub.add_parser("update-pr", parents=[common], help="change a pull request's title, description or draft state")
    p.add_argument("id", type=int)
    p.add_argument("--title")
    p.add_argument("--description-file")
    group = p.add_mutually_exclusive_group()
    group.add_argument("--publish", action="store_true", help="mark a draft ready for review")
    group.add_argument("--draft", action="store_true", help="turn back into a draft")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_update_pr)

    p = sub.add_parser("get-work-item", parents=[common], help="show one work item")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_get_work_item)

    p = sub.add_parser("create-work-item", parents=[common], help="create a work item (default type: Product Backlog Item)")
    p.add_argument("--type", default="Product Backlog Item")
    p.add_argument("--title", required=True)
    p.add_argument("--description-file", help="file with the description, or - for stdin")
    p.add_argument("--acceptance-criteria-file")
    p.add_argument("--area", default=DEFAULT_AREA, help=f"area path (default: {DEFAULT_AREA})")
    p.add_argument("--iteration", default=DEFAULT_ITERATION, help=f"iteration path (default: {DEFAULT_ITERATION})")
    p.add_argument("--tag", action="append", default=[])
    p.add_argument("--assign-to", default="me", help="user email, or 'me' for the token's owner (default); pass '' to leave unassigned")
    p.add_argument("--parent", type=int, help="parent work item id (e.g. a Feature)")
    p.add_argument("--html", dest="markdown", action="store_false", help="send description as HTML instead of Markdown")
    p.add_argument("--dry-run", action="store_true")
    p.set_defaults(func=cmd_create_work_item)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        args.func(args)
    except AdoError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
