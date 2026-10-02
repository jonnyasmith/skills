---
name: review-pr
description: Review an Azure DevOps pull request by id and produce a visual HTML page that explains it (what changed and why, diagrams, the diff grouped by concern with notes, test coverage, and what the CI Terraform plan will change) and shows its CI results and the manual checks it still needs. Use when the user passes a PR id or link and asks to review, explain, walk through or understand it, or asks for a PR review page.
disable-model-invocation: true
---

# Review a pull request

The user reviews agent-written PRs and is a visual reader. The page has to make a PR quick to understand and honest about its problems. It is a report: it describes the PR and flags problems, and fixing them is the PR author's job. Three rules shape everything:

- **Diffs come from git, never from you.** `render.py` takes them from `files.json`, and a Terraform plan's resource list from the CI log. You write the explanation and pin notes to lines; you never retype code or plan output.
- **No reviewer agents.** Do not spawn reviewer, critic or adversarial agents, and do not hunt for issues by reading code. Code-reading reviews list problems the PR didn't cause and never converge. An issue goes on the page only with a reproduction: a red CI build or failing policy, or a test or manual check the user ran and saw fail.
- **Use what the pipeline already does.** The PR's CI build and branch policies already run the build, format check and tests. `prepare.py` reads their results, including the failing task and its log tail, and the page shows them. Nobody reruns them.

Scripts are in `~/.claude/skills/review-pr/scripts/`. They use the Azure DevOps skill's token and client (`~/.claude/skills/azure-devops/`).

## 1. Prepare

```
python3 ~/.claude/skills/review-pr/scripts/prepare.py <PR id>
```

It prints the work directory (`~/.cache/pr-review/<repo>-<id>/`), which holds `context.json` (PR, commits, linked work items with acceptance criteria, comment threads, and `checks`: branch policy results and, for a failed build, the failing tasks with their log tails), `terraformPlans` (see step 3), `diff.patch`, `files.json` (files and hunks), one `terraform-plan-<build>-<n>.txt` per Terraform plan task in CI, and `worktree/`, a detached checkout of the PR's head. It uses the clone in `~/dev/<repo>` when there is one and adds the worktree to it. Read and run code only in the worktree; never switch branches in the user's clone.

## 2. CI results

Read `checks` in `context.json`. **If the CI build failed**, report it as the first blocking issue, exactly as CI gives it: the pipeline, the failing task, its error excerpt and the build link. The page already shows the excerpt and log, so the issue only needs a one-line title and the link. Don't diagnose it: don't reproduce it locally, compare it with other builds, or look for the cause in the code or infrastructure. If `checks.note` says the token lacks Build (Read), report the build result and link without the error.

A failing blocking branch policy (other than a reviewer approval still pending) is also an issue. Nothing else is, unless the user reports a failed test or manual check.

Take the manual checks the PR still needs from the linked work items' acceptance criteria and the PR description's testing section, and list them in `verification` with `passed` left out.

Work alone and keep it short: one pass, no subagents. A small PR should take a few minutes.

## 3. Terraform plan

If `context.json` has `terraformPlans`, the PR's CI ran a Terraform plan, and the page must explain it. Skip this step when the list is empty. Each entry names a plan file (the task output without the state refresh lines), the pipeline, job and build, the `Plan:` summary line, and `resources`: every resource address the plan acts on, with its action (`created`, `updated in-place`, `destroyed`, `replaced`, `moved to ...`). `render.py` builds the resource table from that list. You write what each change does and why it is in the plan.

If the plan task failed, it is a CI failure: report it as step 2 says and don't explain the plan.

Otherwise read the plan file and, for each resource, work out:

- **What changes**, in a short phrase: the attributes that change and their old and new values, such as "removes app settings `StorageAccounts__3__*` and the contributor identity" or "daily cap 0.5 GB to none".
- **The cause**, one of:
  - `this-pr`: the diff changes the code or tfvars behind it. Name the file and line.
  - `target-branch`: the target branch's code already sets the new value, so a change merged earlier has not been applied yet. Name the change with `git log` on the file in the worktree.
  - `outside-terraform`: the code doesn't set the value the resource has now, so someone changed it in the cloud by hand, and applying will undo it.
  - `unclear`: none of the above can be shown. Say what you checked.

The last three are in the plan whatever the PR does. Say so, because merging a PR that triggers an apply applies them too. Check the repo's Terraform pipeline triggers (under `Pipelines/` or `azure-pipelines*.yml`) to see whether a merge applies, and to which environments. Also note which environments CI planned. An environment CI didn't plan, such as production, goes in `verification` as a check of its post-merge plan.

Also explain what the plan leaves out when it matters. For example, a resource removed from the code but not destroyed, because the cloud had already deleted it and the refresh dropped it from state.

Plan contents aren't issues on their own. A change the PR description says won't happen, such as a destroy or replace of something it calls unchanged, is a reproduced issue with the plan as evidence: severity `note`, `foundBy` "CI Terraform plan". Changes from the target branch or from outside Terraform go in the verdict summary, not in `issues`.

When the plan has more than two or three changes, draw one diagram that splits them by cause.

## 4. Write `review.json` in the work directory

Write for someone who knows the product but hasn't read this code. Use plain, direct sentences, no filler. Every field is optional except `headline`, `summary` and `concerns`.

```json
{
  "headline": "One sentence: what the PR changes for users or the system.",
  "verdict": {"level": "ready | changes", "summary": "Two or three sentences: can it merge, and what must happen first."},
  "summary": "Markdown. What changed and why, in a short paragraph or bullets.",
  "why": "Markdown. The problem, taken from the linked work items and description.",
  "readingOrder": ["Start with concern 1: ...", "..."],
  "diagrams": [{"title": "Before and after: saving a group", "svg": "<svg viewBox=\"0 0 940 300\">...</svg>", "caption": "Markdown."}],
  "concerns": [{"title": "Save a group without losing recipient ids", "explanation": "Markdown.", "reviewFocus": "Markdown. What a human should check here.", "files": ["src/path/a.ts", "src/path/a.test.ts"]}],
  "mechanical": [{"path": "pnpm-lock.yaml", "reason": "lock file for the added dependency"}],
  "notes": [{"path": "src/path/a.ts", "line": 42, "text": "Markdown. Why this line matters."}],
  "tests": [{"behaviour": "An existing recipient keeps its id on save", "status": "covered | partial | missing", "evidence": "`form.test.ts` 'saves ... unchanged'"}],
  "terraformPlans": [{"file": "terraform-plan-76809-1.txt", "title": "Development plan", "explanation": "Markdown. What applying this plan does overall, what it leaves out, and whether merging applies it.", "changes": [{"address": "azurerm_user_assigned_identity.storage_identity[\"devicemanager_queue_sender\"]", "change": "Markdown. What changes.", "cause": "this-pr | target-branch | outside-terraform | unclear", "detail": "Markdown. The evidence for the cause."}]}],
  "issues": [{"severity": "blocking | note", "title": "...", "path": "src/path/a.ts", "line": 42, "detail": "Markdown.", "evidence": "Markdown.", "fix": "Markdown.", "foundBy": "CI"}],
  "verification": [{"command": "manual: save a group in the local stack", "passed": true, "result": "only checks outside CI, if any were run"}]
}
```

Guidance:
- **Concerns** group files by purpose, in the order a reviewer should read them, with each test file next to the code it tests. Every changed file belongs to exactly one concern or to `mechanical`. The page lists any leftovers under "Not explained", and `render.py` warns about them, so fix the JSON until the warning goes away.
- **Notes** attach to new-file line numbers, which you can take from the hunks in `files.json`. Use them for the few lines that carry the change, not as a narration of every line.
- **Diagrams** should show the mechanism that changed: before and after, a data flow, or a state machine. One or two good diagrams beat several decorative ones. Leave diagrams out for trivial PRs. Write each one as inline SVG. The page works offline and has no diagram library, so lay the diagram out yourself: build the SVG with a short Python script using `scripts/svg.py` (its docstring shows how), rather than typing coordinates by hand. Its `box()` sizes each box to its longest line and raises an error if a box runs past the diagram width, so text never overflows; pass the same `min_w` to boxes in one column to line them up, set to fit the column's longest label. Style it only with the page's classes, which follow the light and dark theme:
  - `box` on a `<rect rx="8">`, plus `ok`, `bad`, `warn` or `accent` for colour. Use `bad` for the broken path, `ok` for the fixed one and `accent` for the entry point.
  - `edge` on a `<path>` gives a line with an arrowhead; add `ok`, `bad` or `dashed`.
  - `<text>` is plain; add `muted`, `mono` (for code names) or `label` (small caps, for "Before", "After", "yes", "no").
  - `region` on a `<rect>` draws a dashed grouping outline.

  Use a `viewBox` about 940 wide and no fixed width or height; the page scales it. Keep text 13px, keep each box to at most three short lines, and route edges into box edges so arrowheads don't overlap text. No colours, fonts or `<style>` inside the SVG, and no scripts (the renderer strips them).
- **Links:** `[text](#f-<path with each run of non-alphanumerics replaced by ->)` links to a file on the page, and appending `-L<line>` links to a line.
- **Terraform plans:** one entry per file in `context.json`'s `terraformPlans`, with one `changes` item per resource in its `resources`, using the address exactly as listed. `render.py` warns about a plan or resource you didn't explain and about an address that isn't in the plan, so fix the JSON until the warnings go away.
- **The verdict** follows CI and reproduced issues only: a failed build, a failing blocking policy or a reproduced issue means `changes`; otherwise `ready`. Its summary names every check in `verification` that hasn't been run, not a selection of them. When a Terraform plan contains changes not caused by the PR, and merging would apply them, say so in the summary.

## 5. Render and deliver

```
python3 ~/.claude/skills/review-pr/scripts/render.py <workdir>
```

It writes `~/pr-reviews/<repo>-<id>.html` and reports any warnings. Open it for the user with `xdg-open <file>`. In chat, give the verdict, the blocking issues in one line each, the Terraform plan's summary line with how many changes come from the PR and how many don't, and the path. Don't repeat the page.

Only when the user asks, publish the page as a private Artifact, or post the issues as PR comments. Posting comments is visible to the team, so confirm first.

When the user is done with the review, remove the worktree: `git -C <clone> worktree remove <workdir>/worktree`.
