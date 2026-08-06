---
name: implement-tickets
description: "Implement every ticket behind a spec in one workflow run, one /implement worker per ticket."
disable-model-invocation: true
---

# Implement Tickets

Hand over the batch. The user supplies one spec reference; a single workflow run
takes its tickets from ordered to committed. Never implement, verify, or review
a ticket in the host — the workflow's workers own that.

## 1. Resolve the ticket set

The user's argument is the spec. Read the repository's issue-tracker convention
from its routed instructions to find the tickets it governs.

Collect them into one of the two forms the planner accepts:

- **Local markdown** — the directory of per-ticket files, normally `issues/`
  beside the spec. Pass it as `--dir`.
- **Tracker tickets** — dump the whole set to a JSON array of
  `{number, title, body, state}` first, e.g.
  `gh issue list --json number,title,body,state ...`. Pass the file as `--json`.

Include every ticket in the set; the planner needs the whole graph to resolve
blockers.

## 2. Compute the order

```
node "$HOME/.claude/skills/implementation-loop/scripts/plan.mjs" --dir <issues-dir>
node "$HOME/.claude/skills/implementation-loop/scripts/plan.mjs" --json <tickets.json>
```

The planner resolves blockers, rejects cycles, dangling references, self-blocks
and duplicate ids, and emits a total order. Same input, same order — no model
judgement participates, so do not reorder its output.

**Non-zero exit means the ticket set is unsound.** Report the `errors` array and
stop. A blocker pointing at nothing is a defect in the tickets; guessing its
target silently changes what gets built.

## 3. Show the plan

Report `order`, `next`, and any tickets already done. This is free — no agents
spawn until step 4, and it is the user's last cheap look before the run costs
money.

## 4. Run the workflow

```
Workflow({
  scriptPath: "<this skill>/workflow.mjs",
  args: { specRef: "<spec reference>", tickets: [ /* the planner's `tickets` */ ] },
})
```

Pass the planner's `tickets` entries through unchanged — the script reads `id`,
`title`, `source` and `done`. The run is sequential by construction: one worker
at a time, each inheriting its predecessors' commits from the shared branch.

Workflows run in the background. Tell the user the run has started and that
`/workflows` shows live progress, then stop — do not poll it or start other
ticket work while it runs.

## 5. Report the result

The workflow returns `implemented`, `halted`, `notReached` and `order`. Relay the
ticket-to-commit mapping, anything it halted on, and the blocker it named.

State plainly that every claim came from the workers' own reports. `/implement`
owns tests, review and commit for its ticket and nothing external re-checks
them, so a clean report is not the same as verified work.

To resume an interrupted run, re-invoke with `resumeFromRunId` rather than
starting again: without a journal the planner cannot tell which tickets already
landed, so a fresh run rebuilds them.
