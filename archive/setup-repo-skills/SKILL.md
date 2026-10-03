---
name: setup-repo-skills
description: Configure this repo for the engineering skills — scaffold its AGENTS.md routing, issue tracker, triage labels, and per-context docs layout. Idempotent and re-runnable; run it again to add a newly-emerged service or area.
disable-model-invocation: true
---

# Setup Repo Skills

Scaffold and maintain the per-repo structure the engineering skills assume — the recursive documentation-architecture unit, one per context:

```
<context>/
├── AGENTS.md          ← this context's instructions + a routing section
└── docs/
    ├── adr/           ← decisions scoped to this context (numbered; amended in place to stay current)
    └── agents/        ← the context's reference library:
        ├── domain.md  ← glossary (created lazily by /domain-modeling, not here)
        └── …          ← conventions / process (issue-tracker, triage, design-system…)
```

A **context** is any node that owns a bounded domain: the repository root (the _solution_) or a **working target** (an app, package, or service) nested inside it. Every context has this same shape; only content and reach change. The root `AGENTS.md` is the one file the harness auto-loads, so everything deeper is reached by **explicit routing** from it.

This skill is **idempotent and re-runnable**:

- **First run** scaffolds the root context.
- **Later runs** add a newly-emerged working target, or heal drift — always additively, never clobbering user edits.

It is prompt-driven, not a deterministic script. Explore, present what you found, confirm, then write.

## What this skill writes vs. what it doesn't

- **Writes:** the structure — `AGENTS.md` (instructions + routing), the `CLAUDE.md` → `@AGENTS.md` shim, the `docs/agents/` and `docs/adr/` shape, and the convention docs (issue-tracker, triage labels). It authors the routing lines. See [ROUTING.md](./ROUTING.md) for how to write routing that actually fires.
- **Doesn't write:** `docs/agents/domain.md` (the glossary — created lazily by `/domain-modeling` when the first term resolves) or any ADR (appended when a decision is made). A missing file means "nothing to say yet", not "incomplete". Because a context is scaffolded before it holds any ADRs, drop a `.gitkeep` in each `docs/adr/` so the empty directory survives in git — at the root and at every target.

## Process

### 1. Explore

Read the current state; don't assume:

- `git remote -v` and `.git/config` — is this a GitHub, GitLab, or Azure DevOps repo? Which one? Azure DevOps remotes look like `dev.azure.com`, `ssh.dev.azure.com`, or `*.visualstudio.com`. On an Azure DevOps remote, run read-only discovery to **populate** Section A's questions — never to answer them: the project's process and its work-item types/states (`az devops invoke --area wit --resource workitemtypes --route-parameters project="<PROJECT>" --api-version 7.1`), `az boards area project list`, `az boards iteration project list`, and the open Epics (`az boards query --wiql "SELECT [System.Id], [System.Title] FROM workitems WHERE [System.WorkItemType] = 'Epic' AND [System.State] <> 'Closed'"`). If the CLI is missing or unauthenticated, skip discovery and ask outright.
- `AGENTS.md` and `CLAUDE.md` at the repo root — do either exist? Is `CLAUDE.md` already a `@AGENTS.md` shim, or does it hold real content? Is there already a routing section in `AGENTS.md`?
- `docs/agents/` and `docs/adr/` at the root — has this skill already run?
- **Legacy layout** — `CONTEXT.md`, `CONTEXT-MAP.md`, or `src/*/CONTEXT.md`. Their presence means the repo predates this pattern and is a candidate for migration (Section D).
- `.scratch/` — sign that a local-markdown issue tracker convention is already in use.
- Is the `triage` skill installed? (a `triage` folder alongside this one, or `triage` in your available skills.) Decides whether Section B runs.
- **Working targets** — nested contexts that deserve their own `AGENTS.md`: workspace members (`pnpm-workspace.yaml`, a `workspaces` field, `packages/*`/apps with their own `src/`), or a path the user names explicitly. Their presence means the repo is multi-context.

### 2. Present findings and ask

Summarise what's present and what's missing. Then take the sections in order — one section, one answer, then the next. Lead each section with the recommended answer so the user can accept it in a word. Skip a section entirely when exploration already settled it (B when `triage` isn't installed; C when there are no working targets; D when there's no legacy layout).

**Section A — Issue tracker.**

> Explainer: the "issue tracker" is where issues live for this repo. Skills like `to-tickets`, `triage`, `to-spec`, and `qa` read from and write to it — they need to know whether to call `gh issue create`, `glab issue create`, `az boards work-item create`, write a markdown file under `.scratch/`, or follow some other workflow.

Default posture: these skills were designed for GitHub. If a `git remote` points at GitHub, propose that; at GitLab, propose GitLab; at Azure DevOps, propose Azure DevOps Boards. Otherwise (or if the user prefers), offer:

- **GitHub** — issues in GitHub Issues (uses the `gh` CLI)
- **GitLab** — issues in GitLab Issues (uses the [`glab`](https://gitlab.com/gitlab-org/cli) CLI)
- **Azure DevOps Boards** — work items in Azure Boards (uses `az` with the `azure-devops` extension)
- **Local markdown** — issues as files under `.scratch/<feature>/` (good for solo projects or repos without a remote)
- **Other** (Jira, Linear, etc.) — ask for a one-paragraph description; record it as freeform prose. If the tracker has work-item *types*, mandatory fields, or a parent hierarchy above the spec, model the doc on [issue-tracker-azure-devops.md](./issue-tracker-azure-devops.md) — it is the worked example for trackers richer than a flat issue list.

Record the choice in `docs/agents/issue-tracker.md`. The GitHub, GitLab, and Azure DevOps templates carry a "PRs as a request surface" flag, defaulted **off** — leave it off and don't raise it.

**Azure DevOps needs more than a template copy.** It has no single "issue" primitive, so four things must be resolved to concrete values before the doc is written — proposing defaults from discovery, but letting the user decide each:

1. **Classification fields** — the Area path and Iteration path every work item must carry.
2. **Type mapping** — which type is a spec and which is a ticket. Default proposal: spec → `Feature`, ticket → the process's requirement tier (`User Story` for Agile, `Product Backlog Item` for Scrum, `Requirement` for CMMI, `Issue` for Basic), defect → `Bug`. Never map a ticket to `Task`: a ticket is a vertical slice, and `Task` sits below the board's requirement tier.
3. **Epic hierarchy** — ask whether every spec must be parented to an Epic. On yes, list the discovered Epics, have the user pick the valid parents, and collect a one-clause "use for" per Epic. On no, delete that section from the doc.
4. **Completed states** — the terminal state per mapped type (they differ by process: `Closed` for Agile, `Done` for Scrum/Basic), so the doc never says a bare "close".

Write the resolved values into `docs/agents/issue-tracker.md` as flat statements. Never leave a placeholder or a conditional in the emitted doc — an agent cannot distinguish "unconfigured" from "configured as `<EPIC_ID>`".

**Section B — Triage label vocabulary.** Skip entirely if `triage` isn't installed.

If it is, ask one question:

> Keep the default triage labels? (recommended: **yes**)

Defaults are the five canonical roles, each label equal to its name: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. On **yes**, write them as-is. Only on **no** — usually because the tracker already uses other names (e.g. `bug:triage` for `needs-triage`) — collect the overrides so `triage` applies existing labels instead of creating duplicates.

**Section C — Working targets.** Skip if exploration found none. Default to **root-only** — one context at the repo root.

When working targets exist (or the user names one), confirm which ones to create now. Each confirmed target gets **the same unit as the root** — its own `AGENTS.md` + `docs/adr/` + `docs/agents/` — and is wired into its parent's routing. The structure is identical at every level; only content and reach differ. It recurses: a target may itself have working targets, scaffolded the same way, as deep as the repo nests.

**Section D — Legacy migration.** Skip if no legacy files were found.

If `CONTEXT.md`/`CONTEXT-MAP.md`/`src/*/CONTEXT.md` exist, offer to migrate:

- `CONTEXT.md` → `docs/agents/domain.md` (a straight move; content unchanged — it's already a glossary)
- `src/<ctx>/CONTEXT.md` → `<ctx>/docs/agents/domain.md`
- `CONTEXT-MAP.md` → **dissolved**: its per-context pointers become routing lines in the root `AGENTS.md`; the map file is deleted (the tree is the map now)

Present the moves; migrate only on confirmation.

### 3. Confirm and edit

Show a draft of everything before writing:

- The root `AGENTS.md` — its **Routing section** (leading) plus any genuine invariants / migrated `CLAUDE.md` content after it
- The `CLAUDE.md` shim (if applicable)
- The contents of `docs/agents/issue-tracker.md` and `docs/agents/triage-labels.md` (the latter only when `triage` is installed)
- For each new working target: its `AGENTS.md` + `docs/adr/` + `docs/agents/`, and the parent's down-route to it

Let the user edit before writing.

### 4. Write

**Pick the instructions file.** `AGENTS.md` is the single home for instructions; `CLAUDE.md` is only a `@AGENTS.md` import shim:

- If `AGENTS.md` exists, edit it. Ensure `CLAUDE.md`, if present, is the one-line shim `@AGENTS.md`.
- If only `CLAUDE.md` exists: create `AGENTS.md` as the real file. If `CLAUDE.md` holds real content, migrate that content into `AGENTS.md` (with confirmation — never silently relocate someone's root instructions) and reduce `CLAUDE.md` to `@AGENTS.md`. If it's already thin, just add the shim import.
- If neither exists, create `AGENTS.md`, plus a `CLAUDE.md` shim so Claude Code loads it too.

**The root `AGENTS.md` leads with routing.** This layer is paid for on every task, so its primary payload is the index — put it first, right after the title, with no preamble (no orientation sentence explaining what an `AGENTS.md` is or how routing works — agents already know; see [ROUTING.md](./ROUTING.md)). Write lines as **triggers, not labels**:

```markdown
# Solution Wide Instructions   ← root title; a target's is its capitalised name + " Instructions" (Web Instructions, Db Instructions)

## Routing — read only what the task needs, when it needs it

### Working targets ← this whole subsection only when targets exist; omit it otherwise

- Working on <target's job, in task terms> → <target>/AGENTS.md

### This context

- Solution-wide vocabulary → docs/agents/domain.md
- System-wide decisions → docs/adr/
- Issue tracker (<one-clause note on where issues live>) → docs/agents/issue-tracker.md
- Triage labels (<list the five labels>) → docs/agents/triage-labels.md ← only when triage is installed
```

The `domain.md` and `docs/adr/` lines are **bare where-pointers**, not prose rules. Do **not** author `Read before you name` / `Read before you decide` standing-rule essays — that discipline is carried by the routing line itself, and any nuance (use exact terms, don't coin, surface ADR contradictions) lives thinly in the routed file, never in this always-on layer. Keeping Tier 0 to routing-plus-invariants is the whole point of progressive disclosure.

_Genuine invariants (optional, after routing)._ If the repo keeps always-on working rules that apply whatever path a task takes — a commit protocol, a review loop, a comment-discipline rule — place them **after** the routing section, kept terse. Preserve any the repo already has; migrate real `CLAUDE.md` content here rather than into a preamble. Never invent invariants the repo hasn't asked for.

Each target's own `AGENTS.md` repeats this shape and leads the same way, titled with its capitalised name:

```markdown
# Web Instructions

## Routing — read only what the task needs, when it needs it

### This context

- Web vocabulary → docs/agents/domain.md
- Web decisions → docs/adr/
- <a real local convention> → docs/agents/<name>.md
```

It routes **only to its own local docs** — never back up to the root's. Do not add `solution-wide vocabulary → ../docs/agents/domain.md` or `system-wide decisions → ../docs/adr/` lines: the root `AGENTS.md` is always loaded first, so its solution-wide pointers are already in context as the agent descends, and re-pointing at them from a target is pure duplication. Keep any target-local invariants (its verify gate) terse after the index, never as a preamble.

**Wire every new target into its parent.** Each target you create gets a matching down-route in its parent's routing section — a trigger line stating _when_ to descend, in task terms ("Working on the store of record / a migration → `db/AGENTS.md`"), never a bare label. A target nobody routes to is unreachable, so this edit is not optional. (`domain.md` itself is never written here — it's created lazily by `/domain-modeling` at whichever level the first term resolves.)

Write the convention docs from the seed templates:

- [issue-tracker-github.md](./issue-tracker-github.md) — GitHub issue tracker
- [issue-tracker-gitlab.md](./issue-tracker-gitlab.md) — GitLab issue tracker
- [issue-tracker-azure-devops.md](./issue-tracker-azure-devops.md) — Azure DevOps Boards issue tracker
- [issue-tracker-local.md](./issue-tracker-local.md) — local-markdown issue tracker
- [triage-labels.md](./triage-labels.md) — label mapping (only if `triage` is installed)

For "other" trackers, write `docs/agents/issue-tracker.md` from scratch using the user's description.

**On a re-run, be additive.** Create only what's missing. If a routing section already exists, update it in place — never append a duplicate, never clobber surrounding edits. Surface drift as an offer ("the root `AGENTS.md` still leads with a routing-system preamble instead of the index — tighten it?"), not an automatic rewrite.

### 5. Done

Tell the user what was set up (or added) and which engineering skills now read from it. They can edit `docs/agents/*.md` and `AGENTS.md` directly later; re-run this skill to add a new working target, migrate legacy files, or heal drift.
