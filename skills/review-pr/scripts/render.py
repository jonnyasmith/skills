#!/usr/bin/env python3
"""Render a pull request review as one self-contained HTML page.

Reads context.json, files.json (from prepare.py) and review.json (written by
the reviewing agent) from the work directory. Diffs come from files.json, that
is from git, never from the agent, so the code shown is exactly what changed.
Every changed file appears on the page: files that review.json doesn't assign
to a concern or mark as mechanical are listed under "Not explained".

Usage: render.py <work dir> [--out page.html]
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

OUT_DIR = Path.home() / "pr-reviews"


# --------------------------------------------------------------------------- #
# Small Markdown subset for agent-written text
# --------------------------------------------------------------------------- #

def inline(text: str) -> str:
    out = html.escape(text, quote=False)
    out = re.sub(r"`([^`]+)`", r"<code>\1</code>", out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<![*\w])\*([^*\s][^*]*)\*(?![*\w])", r"<em>\1</em>", out)
    out = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+|#[^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2))}">{m.group(1)}</a>',
        out,
    )
    return out


def md(text: str | None) -> str:
    if not text:
        return ""
    blocks, para, items, ordered = [], [], [], False

    def flush() -> None:
        nonlocal para, items
        if para:
            blocks.append(f"<p>{inline(' '.join(para))}</p>")
            para = []
        if items:
            tag = "ol" if ordered else "ul"
            blocks.append(f"<{tag}>" + "".join(f"<li>{inline(i)}</li>" for i in items) + f"</{tag}>")
            items = []

    for raw in text.strip().splitlines():
        line = raw.strip()
        bullet = re.match(r"^[-*] (.*)", line)
        number = re.match(r"^\d+[.)] (.*)", line)
        if not line:
            flush()
        elif bullet or number:
            if para:
                flush()
            if items and ordered != bool(number):
                flush()
            ordered = bool(number)
            items.append((bullet or number).group(1))
        elif items and raw.startswith("  "):
            items[-1] += " " + line
        else:
            if items:
                flush()
            para.append(line)
    flush()
    return "\n".join(blocks)


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value))


def anchor(path: str, line: int | None = None) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", path).strip("-")
    return f"f-{slug}" + (f"-L{line}" if line else "")


def build_link(policy: dict) -> str:
    if not policy.get("buildUrl"):
        return ""
    return f'<a href="{esc(policy["buildUrl"])}">build {esc(policy["buildId"])}</a>'


def clean_svg(svg: str) -> str:
    """Keep an agent-written <svg>, minus anything that could run code."""
    svg = (svg or "").strip()
    if not svg.startswith("<svg"):
        return ""
    svg = re.sub(r"<script\b.*?</script>", "", svg, flags=re.S | re.I)
    svg = re.sub(r"<foreignObject\b.*?</foreignObject>", "", svg, flags=re.S | re.I)
    svg = re.sub(r"\son\w+\s*=\s*(\"[^\"]*\"|'[^']*')", "", svg, flags=re.I)
    svg = re.sub(r"(href\s*=\s*[\"'])\s*javascript:[^\"']*", r"\1#", svg, flags=re.I)
    if 'class="dg' not in svg:
        svg = svg.replace("<svg", '<svg class="dg"', 1)
    return svg


# --------------------------------------------------------------------------- #
# Diffs
# --------------------------------------------------------------------------- #

def render_file(f: dict, notes: list[dict], issues_by_line: dict) -> str:
    path = f["path"]
    rename = f' <span class="muted">(from {esc(f["oldPath"])})</span>' if f.get("oldPath") else ""
    status = {"added": "new", "deleted": "deleted", "renamed": "renamed"}.get(f["status"], "")
    badge = f'<span class="tag">{status}</span>' if status else ""
    head = (
        f'<summary><span class="path">{esc(path)}</span>{rename} {badge}'
        f'<span class="stat"><span class="plus">+{f["added"]}</span> <span class="minus">−{f["removed"]}</span></span></summary>'
    )
    if f.get("binary"):
        body = '<p class="muted pad">Binary file.</p>'
    else:
        notes_at: dict[int, list[str]] = {}
        for n in notes:
            notes_at.setdefault(int(n.get("line") or 0), []).append(n.get("text", ""))
        rows = []
        for h in f["hunks"]:
            rows.append(f'<tr class="hunk"><td colspan="3">{esc(h["header"])}</td></tr>')
            old, new = h["oldStart"], h["newStart"]
            for line in h["lines"]:
                kind, code = line[:1], line[1:]
                if kind == "\\":
                    continue
                o = n = ""
                cls = "ctx"
                if kind == "+":
                    cls, n = "add", new
                    new += 1
                elif kind == "-":
                    cls, o = "del", old
                    old += 1
                else:
                    o, n = old, new
                    old += 1
                    new += 1
                line_id = f' id="{anchor(path, n)}"' if n else ""
                flag = ' data-issue="1"' if n and n in issues_by_line else ""
                rows.append(
                    f'<tr class="{cls}"{line_id}{flag}><td class="ln">{o}</td><td class="ln">{n}</td>'
                    f'<td class="code">{esc(code) or " "}</td></tr>'
                )
                if n and n in notes_at and kind != "-":
                    for text in notes_at.pop(n):
                        rows.append(f'<tr class="note"><td colspan="2"></td><td>{inline(text)}</td></tr>')
                if n and n in issues_by_line and kind != "-":
                    for issue in issues_by_line.pop(n):
                        rows.append(
                            f'<tr class="note issue-{esc(issue["severity"])}"><td colspan="2"></td>'
                            f'<td><a href="#{issue["_anchor"]}">{esc(issue["_label"])}</a> {inline(issue.get("title", ""))}</td></tr>'
                        )
        leftover = [t for texts in notes_at.values() for t in texts]
        extra = "".join(f'<div class="note-box">{inline(t)}</div>' for t in leftover)
        body = f'{extra}<div class="diff-wrap"><table class="diff">{"".join(rows)}</table></div>'
    # Every file starts collapsed; following a link to it or one of its lines opens it.
    return f'<details class="file" id="{anchor(path)}">{head}{body}</details>'


# --------------------------------------------------------------------------- #
# Page
# --------------------------------------------------------------------------- #

VERDICTS = {
    "ready": ("Ready to merge", "ok"),
    "minor": ("Ready after small fixes", "warn"),
    "changes": ("Needs changes", "bad"),
    "discuss": ("Needs discussion", "warn"),
}


def check_state(v: dict) -> tuple[str, str]:
    """A check with no `passed` value hasn't been run yet."""
    if "passed" not in v or v["passed"] is None:
        return ("pending", "not run")
    return ("ok", "pass") if v["passed"] else ("bad", "fail")


# --------------------------------------------------------------------------- #
# Terraform plans
# --------------------------------------------------------------------------- #

CAUSES = {
    "this-pr": ("ok", "this PR"),
    "target-branch": ("warn", "already on the target branch"),
    "outside-terraform": ("warn", "changed outside Terraform"),
    "unclear": ("", "unclear"),
}


def plan_action_cls(action: str) -> str:
    if "replaced" in action or "destroyed" in action:
        return "bad"
    if "created" in action:
        return "ok"
    return "warn"


def terraform_section(ctx: dict, review: dict, warnings: list[str]) -> str:
    """One panel per Terraform plan task in CI. The resources and actions come from
    the plan log (context.json); the explanation and cause of each come from review.json."""
    plans = ctx.get("terraformPlans") or []
    if not plans:
        return ""
    work = Path(ctx.get("_workDir", "."))
    written = {p.get("file"): p for p in review.get("terraformPlans", [])}
    panels = []
    for plan in plans:
        mine = written.get(plan["file"], {})
        if not mine:
            warnings.append(f"review.json has no terraformPlans entry for {plan['file']}")
        explained = {c.get("address"): c for c in mine.get("changes", [])}
        in_plan = {r["address"] for r in plan.get("resources", [])}
        for addr in explained:
            if addr not in in_plan:
                warnings.append(f"terraformPlans entry names {addr}, which is not in {plan['file']}")
        rows = []
        for r in plan.get("resources", []):
            c = explained.get(r["address"])
            if c is None and mine:
                warnings.append(f"{plan['file']}: {r['address']} is not explained")
            cause_cls, cause_label = CAUSES.get((c or {}).get("cause"), ("", "not explained"))
            rows.append(
                f'<tr><td><code>{esc(r["address"])}</code></td>'
                f'<td><span class="pill {plan_action_cls(r["action"])}">{esc(r["action"])}</span></td>'
                f'<td>{md((c or {}).get("change"))}</td>'
                f'<td><span class="pill {cause_cls}">{esc(cause_label)}</span>{md((c or {}).get("detail"))}</td></tr>'
            )
        raw_path = work / plan["file"]
        raw = raw_path.read_text() if raw_path.exists() else ""
        failed = plan.get("result") not in (None, "succeeded")
        summary_cls = "bad" if failed else ("ok" if (plan.get("summary") or "").startswith("No changes") else "warn")
        where = " · ".join(esc(x) for x in (plan.get("pipeline"), plan.get("job")) if x)
        panels.append(
            f'<div class="panel"><h3>{esc(mine.get("title") or plan.get("task"))} '
            f'<span class="pill {summary_cls}">{esc(plan.get("summary") or plan.get("result"))}</span></h3>'
            f'<p class="muted">{where} · <a href="{esc(plan.get("buildUrl"))}">build {esc(plan.get("buildId"))}</a> · task “{esc(plan.get("task"))}”</p>'
            f'{md(mine.get("explanation"))}'
            + (
                '<div class="table-wrap"><table class="grid"><thead><tr><th>Resource</th><th>Action</th><th>What changes</th><th>Cause</th></tr></thead>'
                f'<tbody>{"".join(rows)}</tbody></table></div>'
                if rows else ""
            )
            + (f'<details><summary>Plan output</summary><pre class="log">{esc(raw)}</pre></details>' if raw else "")
            + "</div>"
        )
    return '<section id="terraform"><h2>Terraform plan</h2>' + "".join(panels) + "</section>"


def build(ctx: dict, files: list[dict], review: dict) -> str:
    by_path = {f["path"]: f for f in files}
    notes_by_path: dict[str, list[dict]] = {}
    for n in review.get("notes", []):
        notes_by_path.setdefault(n.get("path", ""), []).append(n)

    issues = review.get("issues", [])
    order = {"blocking": 0, "note": 1}
    issues.sort(key=lambda i: order.get(i.get("severity"), 2))
    issue_lines: dict[str, dict[int, list[dict]]] = {}
    counts = {"blocking": 0, "note": 0}
    for i, issue in enumerate(issues, 1):
        sev = issue.get("severity", "note")
        counts[sev] = counts.get(sev, 0) + 1
        issue["_anchor"] = f"issue-{i}"
        issue["_label"] = f"{'Blocking' if sev == 'blocking' else 'Note'} {i}"
        if issue.get("path") and issue.get("line"):
            issue_lines.setdefault(issue["path"], {}).setdefault(int(issue["line"]), []).append(issue)

    placed: set[str] = set()
    warnings: list[str] = []

    def files_html(paths: list[str]) -> str:
        parts = []
        for p in paths:
            if p not in by_path:
                warnings.append(f"review.json names {p}, which is not in the diff")
                continue
            if p in placed:
                parts.append(f'<p class="muted">See <a href="#{anchor(p)}">{esc(p)}</a> above.</p>')
                continue
            placed.add(p)
            parts.append(render_file(by_path[p], notes_by_path.get(p, []), issue_lines.get(p, {})))
        return "".join(parts)

    # Concerns
    concern_html = []
    for i, c in enumerate(review.get("concerns", []), 1):
        concern_html.append(
            f'<section class="concern" id="concern-{i}"><h3><span class="num">{i}</span>{esc(c.get("title"))}</h3>'
            f'{md(c.get("explanation"))}'
            + (f'<div class="callout">{md(c.get("reviewFocus"))}</div>' if c.get("reviewFocus") else "")
            + files_html(c.get("files", []))
            + "</section>"
        )

    mech = review.get("mechanical", [])
    mech_rows = []
    for m in mech:
        p = m.get("path")
        if p in by_path and p not in placed:
            placed.add(p)
            mech_rows.append(
                f'<li><b>{esc(p)}</b> <span class="muted">{inline(m.get("reason", ""))}</span>'
                + render_file(by_path[p], [], {})
                + "</li>"
            )

    unexplained = [f["path"] for f in files if f["path"] not in placed]
    unexplained_html = files_html(unexplained) if unexplained else ""
    if unexplained:
        warnings.append(f"{len(unexplained)} changed file(s) not covered by any concern")

    # Diagrams
    diagrams = []
    for d in review.get("diagrams", []):
        svg = clean_svg(d.get("svg", ""))
        if not svg:
            warnings.append(f"diagram '{d.get('title')}' has no usable svg")
            continue
        diagrams.append(
            f'<figure class="diagram"><figcaption>{esc(d.get("title"))}</figcaption>'
            f'<div class="svg-wrap">{svg}</div>{md(d.get("caption"))}</figure>'
        )

    # Tests
    test_rows = "".join(
        f'<tr><td>{inline(t.get("behaviour", ""))}</td><td><span class="pill {esc(t.get("status"))}">{esc(t.get("status"))}</span></td>'
        f'<td>{inline(t.get("evidence", ""))}</td></tr>'
        for t in review.get("tests", [])
    )

    # Issues
    issue_cards = []
    for issue in issues:
        where = ""
        if issue.get("path"):
            target = anchor(issue["path"], issue.get("line")) if issue.get("line") else anchor(issue["path"])
            where = f'<a class="where" href="#{target}">{esc(issue["path"])}{":" + esc(issue["line"]) if issue.get("line") else ""}</a>'
        issue_cards.append(
            f'<article class="issue {esc(issue.get("severity"))}" id="{issue["_anchor"]}">'
            f'<header><span class="pill {esc(issue.get("severity"))}">{esc(issue["_label"])}</span> <b>{inline(issue.get("title", ""))}</b> {where}</header>'
            f'{md(issue.get("detail"))}'
            + (f'<h5>Evidence</h5>{md(issue.get("evidence"))}' if issue.get("evidence") else "")
            + (f'<h5>Suggested fix</h5>{md(issue.get("fix"))}' if issue.get("fix") else "")
            + (f'<p class="muted">Found by {esc(issue.get("foundBy"))}</p>' if issue.get("foundBy") else "")
            + "</article>"
        )

    checks = ctx.get("checks") or {}
    status_cls = {"approved": "ok", "rejected": "bad", "broken": "bad", "queued": "warn", "running": "warn", "notApplicable": ""}
    policy_rows = "".join(
        f'<tr><td>{esc(p.get("policy"))}{" · " + esc(p["name"]) if p.get("name") else ""}</td>'
        f'<td><span class="pill {status_cls.get(p.get("status"), "warn")}">{esc(p.get("status"))}</span></td>'
        f'<td>{"blocking" if p.get("blocking") else "optional"}</td>'
        f'<td>{build_link(p)}</td></tr>'
        for p in checks.get("policies", [])
    )
    build_html = ""
    for b in checks.get("builds", []):
        for t in b.get("failedTasks", []):
            task_issues = t.get("issues", [])
            if t.get("errorExcerpt"):
                # "Bash exited with code '1'." says nothing the excerpt doesn't.
                task_issues = [i for i in task_issues if not re.search(r"exit(ed)? (with )?code", i, re.I)]
            issues_list = "".join(f"<li><code>{esc(i)}</code></li>" for i in task_issues)
            excerpt = f'<pre class="log">{esc(t["errorExcerpt"])}</pre>' if t.get("errorExcerpt") else ""
            log = f'<details><summary>Last lines of the log</summary><pre class="log">{esc(t.get("logTail"))}</pre></details>' if t.get("logTail") else ""
            log = excerpt + log
            build_html += (
                f'<div class="issue blocking"><header><span class="pill bad">{esc(t.get("result"))}</span> '
                f'<b>{esc(b.get("pipeline"))}: {esc(t.get("name"))}</b> <a class="where" href="{esc(b.get("url"))}">build {esc(b.get("id"))}</a></header>'
                + (f"<ul>{issues_list}</ul>" if issues_list else "") + log + "</div>"
            )
    ci_failed = any(p.get("status") in ("rejected", "broken") and p.get("buildId") for p in checks.get("policies", []))
    build_policies = [p for p in checks.get("policies", []) if p.get("policy") == "Build" or p.get("buildId")]
    if not build_policies:
        ci_state = "none"
    elif ci_failed:
        ci_state = "failed"
    elif all(p.get("status") == "approved" for p in build_policies):
        ci_state = "passed"
    else:
        ci_state = "running"
    checks_html = ""
    if policy_rows:
        checks_html = (
            '<section id="ci"><h2>CI and branch policies</h2>'
            f'<div class="table-wrap"><table class="grid"><thead><tr><th>Policy</th><th>Status</th><th>Type</th><th>Build</th></tr></thead><tbody>{policy_rows}</tbody></table></div>'
            + build_html
            + (f'<p class="muted">{esc(checks["note"])}</p>' if checks.get("note") else "")
            + "</section>"
        )

    terraform_html = terraform_section(ctx, review, warnings)

    verification = "".join(
        f'<tr><td><code>{esc(v.get("command"))}</code></td><td><span class="pill {state[0]}">{state[1]}</span></td><td>{inline(v.get("result", ""))}</td></tr>'
        for v in review.get("verification", [])
        for state in [check_state(v)]
    )

    premise = review.get("premise") or {}
    premise_html = ""
    if premise:
        cls = {"real": "ok", "partly": "warn", "not real": "bad", "unverified": "warn"}.get(premise.get("verdict", ""), "warn")
        premise_html = (
            f'<div class="panel"><h3>Is the problem real? <span class="pill {cls}">{esc(premise.get("verdict"))}</span></h3>'
            f'{md(premise.get("claim"))}{md(premise.get("evidence"))}</div>'
        )

    verdict_key = review.get("verdict", {}).get("level", "discuss")
    verdict_label, verdict_cls = VERDICTS.get(verdict_key, VERDICTS["discuss"])

    work_items = "".join(
        f'<li><a href="{esc(w["url"])}">{esc(w["type"])} {w["id"]}</a>: {esc(w["title"])} <span class="muted">({esc(w["state"])})</span></li>'
        for w in ctx.get("workItems", [])
    )
    threads = "".join(
        f'<li><span class="muted">{esc(t.get("status"))}{" · " + esc(t["file"]) if t.get("file") else ""}</span>'
        + "".join(f'<div><b>{esc(c["author"])}:</b> {inline((c.get("content") or "")[:600])}</div>' for c in t["comments"])
        + "</li>"
        for t in ctx.get("threads", [])
    )
    commits = "".join(
        f'<li><code>{esc(c["id"][:8])}</code> {esc((c.get("message") or "").splitlines()[0] if c.get("message") else "")}</li>'
        for c in ctx.get("commits", [])
    )
    reading = "".join(f"<li>{inline(r)}</li>" for r in review.get("readingOrder", []))

    added = sum(f["added"] for f in files)
    removed = sum(f["removed"] for f in files)
    src = ctx["source"].removeprefix("refs/heads/")
    tgt = ctx["target"].removeprefix("refs/heads/")

    nav = [("verdict", "Verdict")]
    if checks_html:
        nav.append(("ci", "CI"))
    if terraform_html:
        nav.append(("terraform", "Terraform plan"))
    nav.append(("summary", "What and why"))
    if diagrams:
        nav.append(("diagrams", "Diagrams"))
    nav.append(("changes", "Changes"))
    if test_rows:
        nav.append(("tests", "Tests"))
    nav.append(("issues", f"Issues ({len(issues)})"))
    if verification:
        nav.append(("verification", "Checks"))
    nav_html = "".join(f'<a href="#{i}">{t}</a>' for i, t in nav)

    warn_html = "".join(f"<li>{esc(w)}</li>" for w in warnings)

    build.warnings = warnings
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PR {ctx['id']} review</title>
<style>{CSS}</style>
</head>
<body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
  <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="arrowhead"/></marker>
</defs></svg>
<header class="top">
  <div class="wrap">
    <p class="eyebrow">{esc(ctx['repository'])} · PR <a href="{esc(ctx['url'])}">{ctx['id']}</a> · {esc(src)} → {esc(tgt)} · by {esc(ctx.get('createdBy'))}</p>
    <h1>{esc(ctx['title'])}</h1>
    <p class="lede">{inline(review.get('headline', ''))}</p>
  </div>
</header>
<nav class="wrap tabs">{nav_html}</nav>
<main class="wrap">
  <div class="cards">
    <div class="card"><strong>{len(files)}</strong><span>files</span></div>
    <div class="card"><strong><span class="plus">+{added}</span> <span class="minus">−{removed}</span></strong><span>lines</span></div>
    <div class="card"><strong class="{ {'failed': 'minus', 'passed': 'plus'}.get(ci_state, '') }">{ci_state}</strong><span>CI build</span></div>
    <div class="card"><strong>{counts.get('blocking', 0)}</strong><span>blocking issues</span></div>
  </div>
  {f'<ul class="warnings">{warn_html}</ul>' if warn_html else ''}

  <section id="verdict" class="verdict {verdict_cls}">
    <h2>{verdict_label}</h2>
    {md(review.get('verdict', {}).get('summary'))}
  </section>

  {checks_html}

  {terraform_html}

  <section id="summary">
    <h2>What this PR does, and why</h2>
    <div class="panel">{md(review.get('summary'))}</div>
    {f'<div class="panel"><h3>Why</h3>{md(review.get("why"))}{f"<ul>{work_items}</ul>" if work_items else ""}</div>' if review.get('why') or work_items else ''}
    {premise_html}
    {f'<div class="panel"><h3>Suggested reading order</h3><ol>{reading}</ol></div>' if reading else ''}
  </section>

  {f'<section id="diagrams"><h2>Diagrams</h2>{"".join(diagrams)}</section>' if diagrams else ''}

  <section id="changes">
    <h2>Changes, by concern</h2>
    {''.join(concern_html)}
    {f'<section class="concern"><h3>Mechanical changes</h3><p class="muted">Generated, formatting or rename-only changes. Collapsed.</p><ul class="mech">{"".join(mech_rows)}</ul></section>' if mech_rows else ''}
    {f'<section class="concern"><h3>Not explained</h3><p class="muted">Changed files the review did not cover.</p>{unexplained_html}</section>' if unexplained_html else ''}
  </section>

  {f'<section id="tests"><h2>What the tests cover</h2><div class="table-wrap"><table class="grid"><thead><tr><th>Behaviour</th><th>Covered</th><th>Evidence</th></tr></thead><tbody>{test_rows}</tbody></table></div></section>' if test_rows else ''}

  <section id="issues">
    <h2>Issues</h2>
    {''.join(issue_cards) or '<p class="panel">No issues found.</p>'}
  </section>

  {f'<section id="verification"><h2>Other checks</h2><div class="table-wrap"><table class="grid"><thead><tr><th>Command</th><th>Result</th><th>Detail</th></tr></thead><tbody>{verification}</tbody></table></div></section>' if verification else ''}

  <section>
    <h2>Context</h2>
    <div class="panel"><h3>PR description</h3>{md(ctx.get('description'))}</div>
    <div class="panel"><h3>Commits</h3><ul>{commits}</ul></div>
    {f'<div class="panel"><h3>Existing comments</h3><ul>{threads}</ul></div>' if threads else ''}
  </section>
  <p class="muted foot">Written by AI from the diff between {esc(ctx['mergeBase'][:8])} and {esc(ctx['sourceCommit'][:8])}. Diffs are taken from git; the explanation is AI-written and can be wrong, so check it against the code.</p>
</main>
<script>
  // Open a collapsed file when following a link to one of its lines.
  function reveal() {{
    const el = location.hash && document.getElementById(location.hash.slice(1));
    const file = el && el.closest("details");
    if (file) {{ file.open = true; el.scrollIntoView({{ block: "center" }}); el.classList.add("flash"); }}
  }}
  addEventListener("hashchange", reveal); reveal();
</script>
</body>
</html>
"""


CSS = """
:root{--ink:#172438;--muted:#5a6878;--line:#d9e1e8;--paper:#fff;--wash:#f4f7fa;--head:#102b46;--headink:#d0e1f2;--blue:#124f88;
--add:#e6f6ec;--addln:#cdebd8;--del:#fbeaea;--delln:#f3d3d3;--hunk:#eef2f8;--code:#eef2f6;
--ok:#236345;--okbg:#e2f3ea;--warn:#845400;--warnbg:#fdf1d8;--bad:#9b2e2e;--badbg:#fbe7e7;--note:#fff8dc}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--ink:#e3e9f0;--muted:#9fb0c2;--line:#2e3b4a;--paper:#17212c;--wash:#0f161e;--head:#0b1f33;--headink:#b9cde2;--blue:#8cc0f0;
--add:#12301f;--addln:#184029;--del:#3a1d1f;--delln:#4a2427;--hunk:#1c2836;--code:#1f2a36;
--ok:#8fd6ae;--okbg:#16301f;--warn:#f0c878;--warnbg:#352a14;--bad:#f0a0a0;--badbg:#3a1d1f;--note:#2e2a18}}
*{box-sizing:border-box}
body{margin:0;background:var(--wash);color:var(--ink);font:15px/1.6 system-ui,-apple-system,"Segoe UI",sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
header.top{background:var(--head);color:#fff;padding:28px 0 22px}
header.top h1{margin:4px 0 8px;font-size:1.7rem;line-height:1.25}
.eyebrow{margin:0;color:var(--headink);font-size:.9rem}.eyebrow a{color:#fff}
.lede{margin:0;color:var(--headink);max-width:880px;font-size:1.05rem}
nav.tabs{display:flex;gap:6px;flex-wrap:wrap;padding-top:12px;padding-bottom:4px;position:sticky;top:0;background:var(--wash);z-index:5;border-bottom:1px solid var(--line)}
nav.tabs a{color:var(--blue);text-decoration:none;padding:4px 10px;border-radius:6px;font-size:.92rem}nav.tabs a:hover{background:var(--paper)}
h2{font-size:1.3rem;margin:36px 0 10px;padding-bottom:6px;border-bottom:2px solid var(--line)}
h3{font-size:1.05rem;margin:4px 0 8px}h5{margin:10px 0 2px;font-size:.78rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
a{color:var(--blue)}code{font:.87em/1.4 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;background:var(--code);padding:1px 5px;border-radius:4px;overflow-wrap:anywhere}
.muted{color:var(--muted)}.pad{padding:8px 12px}
pre.log{background:var(--code);padding:10px;border-radius:6px;overflow-x:auto;font:.8rem/1.4 ui-monospace,monospace;max-height:420px}
.cards{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:18px 0}
.card{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 14px}.card strong{display:block;font-size:1.4rem}.card span{color:var(--muted);font-size:.9rem}
.plus{color:var(--ok)}.minus{color:var(--bad)}
.panel{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 18px;margin:10px 0}
.verdict{border-radius:10px;padding:12px 18px;margin:10px 0;border-left:6px solid}
.verdict h2{border:0;margin:0 0 4px;padding:0}
.verdict.ok{background:var(--okbg);border-color:var(--ok)}.verdict.warn{background:var(--warnbg);border-color:var(--warn)}.verdict.bad{background:var(--badbg);border-color:var(--bad)}
.warnings{background:var(--warnbg);color:var(--warn);border-radius:8px;padding:8px 28px}
.callout{border-left:4px solid var(--blue);background:var(--wash);padding:6px 14px;margin:8px 0;border-radius:0 6px 6px 0}
.concern{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:14px 18px;margin:14px 0}
.num{display:inline-grid;place-items:center;width:1.6em;height:1.6em;border-radius:50%;background:var(--blue);color:var(--paper);font-size:.85rem;margin-right:8px}
details.file{border:1px solid var(--line);border-radius:8px;margin:10px 0;overflow:hidden;background:var(--paper)}
details.file>summary{cursor:pointer;padding:7px 12px;background:var(--hunk);display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.path{font:600 .88rem ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;overflow-wrap:anywhere}.stat{margin-left:auto;font:.85rem ui-monospace,monospace}
.tag{font-size:.72rem;text-transform:uppercase;letter-spacing:.04em;background:var(--code);border-radius:99px;padding:1px 8px}
.diff-wrap{overflow-x:auto}
table.diff{border-collapse:collapse;width:100%;font:.82rem/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
table.diff td{padding:0 8px;vertical-align:top}
td.ln{width:1%;min-width:3.2em;text-align:right;color:var(--muted);user-select:none;white-space:nowrap}
td.code{white-space:pre;tab-size:4}
tr.add{background:var(--add)}tr.add td.ln{background:var(--addln)}
tr.del{background:var(--del)}tr.del td.ln{background:var(--delln)}
tr.hunk td{background:var(--hunk);color:var(--muted);padding:3px 8px}
tr.note td:last-child{background:var(--note);font-family:system-ui,sans-serif;font-size:.88rem;white-space:normal;padding:6px 12px;border-left:3px solid var(--blue)}
tr.note.issue-blocking td:last-child{border-left-color:var(--bad)}tr.note.issue-note td:last-child{border-left-color:var(--warn)}
tr[data-issue] td.ln{box-shadow:inset 3px 0 var(--bad)}
.note-box{background:var(--note);padding:6px 12px;border-left:3px solid var(--blue);font-size:.9rem}
.flash{outline:2px solid var(--blue)}
.pill{display:inline-block;background:var(--code);color:var(--muted);border-radius:99px;font-size:.72rem;font-weight:700;letter-spacing:.04em;text-transform:uppercase;padding:2px 9px;white-space:nowrap}
.pill.ok,.pill.covered{background:var(--okbg);color:var(--ok)}.pill.warn,.pill.partial,.pill.note{background:var(--warnbg);color:var(--warn)}
.pill.bad,.pill.missing,.pill.blocking{background:var(--badbg);color:var(--bad)}
.pill.pending{background:var(--code);color:var(--muted)}
details.file>summary{list-style:none}details.file>summary::-webkit-details-marker{display:none}
details.file>summary::before{content:"▸";color:var(--muted);width:1em;flex:none}details.file[open]>summary::before{content:"▾"}
.issue{background:var(--paper);border:1px solid var(--line);border-left:5px solid var(--warn);border-radius:8px;padding:10px 16px;margin:10px 0}
.issue.blocking{border-left-color:var(--bad)}.issue header{display:flex;gap:8px;flex-wrap:wrap;align-items:center}.where{margin-left:auto;font:.85rem ui-monospace,monospace}
.table-wrap{overflow-x:auto}table.grid{border-collapse:collapse;width:100%;background:var(--paper)}
table.grid th,table.grid td{border:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}table.grid th{background:var(--hunk)}
figure.diagram{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:12px 16px;margin:12px 0}
figure.diagram figcaption{font-weight:600;margin-bottom:6px}
.svg-wrap{overflow-x:auto}
svg.dg{display:block;width:100%;height:auto;max-width:980px;margin:0 auto;font:13px/1.3 system-ui,-apple-system,"Segoe UI",sans-serif}
svg.dg text{fill:var(--ink)}svg.dg text.muted{fill:var(--muted)}svg.dg text.label{font-size:11px;fill:var(--muted);text-transform:uppercase;letter-spacing:.06em}
svg.dg text.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px}
svg.dg .box{fill:var(--paper);stroke:var(--muted);stroke-width:1.2}
svg.dg .box.ok{fill:var(--okbg);stroke:var(--ok)}svg.dg .box.bad{fill:var(--badbg);stroke:var(--bad)}
svg.dg .box.warn{fill:var(--warnbg);stroke:var(--warn)}svg.dg .box.accent{fill:var(--hunk);stroke:var(--blue)}
svg.dg .edge{fill:none;stroke:var(--muted);stroke-width:1.4;marker-end:url(#arrow)}
svg.dg .edge.ok{stroke:var(--ok)}svg.dg .edge.bad{stroke:var(--bad)}svg.dg .edge.dashed{stroke-dasharray:5 4}
svg.dg .region{fill:none;stroke:var(--line);stroke-dasharray:4 4}
.arrowhead{fill:var(--muted)}
ul.mech{list-style:none;padding:0}
.foot{margin-top:40px;font-size:.85rem}
@media (max-width:760px){.cards{grid-template-columns:repeat(2,1fr)}header.top h1{font-size:1.35rem}}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workdir")
    parser.add_argument("--out", help="output HTML path (default: ~/pr-reviews/<repo>-<id>.html)")
    args = parser.parse_args()
    work = Path(args.workdir).expanduser()
    ctx = json.loads((work / "context.json").read_text())
    ctx["_workDir"] = str(work)
    files = json.loads((work / "files.json").read_text())
    review_path = work / "review.json"
    if not review_path.exists():
        raise SystemExit(f"error: {review_path} not found; write the review first.")
    review = json.loads(review_path.read_text())
    page = build(ctx, files, review)
    out = Path(args.out).expanduser() if args.out else OUT_DIR / f"{ctx['repository']}-{ctx['id']}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(json.dumps({"html": str(out), "bytes": len(page), "warnings": getattr(build, "warnings", [])}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
