---
name: implementation-loop
description: Sequentially implement a spec-backed set of tickets by resolving their dependency order and delegating each ready ticket to a fresh sub-agent using the implement skill. Use when the user provides a spec or spec reference plus ticket references and wants the complete ticket set implemented one ticket at a time with no concurrent ticket work.
disable-model-invocation: true
---

# Implementation Loop

Orchestrate the work; do not implement tickets in the host agent. Keep exactly one ticket implementation in flight at a time.

Ordering, completion, and resume are decided by the scripts in `scripts/`, not by your judgement. You supply the sources and perform the dispatch; everything else is computed. Do not reorder, skip, or declare a ticket done by reading prose — if you find yourself reasoning about which ticket "feels" next, you have left the loop.

## 1. Resolve the work

Collect the ticket set into one of the two forms the planner accepts:

- **Local tickets** — a directory of per-ticket markdown files (`.scratch/<slug>/issues/`). Pass it as `--dir`.
- **Tracker tickets** — dump them to a JSON array of `{number, title, body, state}` first, e.g. `gh issue list --json number,title,body,state ...`, including every ticket in the set. Pass the file as `--json`.

Fetch each ticket's full body, plus the governing spec and any comments that change acceptance criteria. Do not summarise the sources into the planner — it parses the real bodies.

Choose a journal path that persists for the run (`.scratch/<slug>/loop-journal.jsonl` is fine; the gate exempts it from its own clean-tree check). The journal is what makes an interrupted loop resume rather than re-decide.

## 2. Compute the sequence

```
node <skill>/scripts/plan.mjs --dir <issues-dir> --journal <journal> [--order <ids>]
node <skill>/scripts/plan.mjs --json <tickets.json> --journal <journal> [--order <ids>]
```

The planner resolves blockers by number, `#number`, or exact title; rejects cycles, dangling references, self-blocks, and duplicate ids; and emits a total order. Ties among ready tickets break by explicit `--order`, then by transitive unlock count descending, then by id ascending — so the same inputs always produce the same order.

Pass `--order` only when the user gave an explicit sequence. It is a preference within the dependency constraints, never an override of them.

**Non-zero exit means the ticket set is unsound.** Report the `errors` array and stop. Do not repair the graph by inference; a missing blocker reference is a defect in the tickets, and guessing its target silently changes what gets built.

Tickets already marked done — journal entry, closed tracker state, or a `Status:` of done/complete/closed/merged — are excluded from the frontier. `next` is the ticket to dispatch.

## 3. Delegate one ticket

Record the dispatch baseline before spawning:

```
git rev-parse HEAD
```

Spawn one fresh sub-agent for `next` with a compact prompt:

`Use /implement to implement <ticket reference>.`

If the ticket does not itself link the governing spec, append `The governing spec is <spec reference>.` Do not paste the ticket or spec into the prompt when the references are accessible; the delegated agent must load the authoritative sources itself.

Do not ask the sub-agent to use this orchestration skill. Do not delegate multiple tickets to one agent. Do not spawn another implementation agent or begin other ticket work while this agent is active.

## 4. Close the ticket loop

Wait for the sub-agent, then gate on repository facts:

```
node <skill>/scripts/gate.mjs --ticket <id> --baseline <sha> --journal <journal> \
  [--criteria <ticket.md>] [--verify "<cmd>"]...
```

The gate checks new commits on the current branch since the baseline, a clean working tree, optionally that the ticket's acceptance-criteria checkboxes are ticked, and that each supplied verification command exits 0. Pass the project's real type-check and test commands as `--verify`; passing none means the loop trusts only that work was committed.

**Exit 0 is the only definition of done.** The gate appends the journal entry itself. The sub-agent's report is evidence for diagnosing a failure, never a substitute for the gate.

On exit 1, send the same sub-agent a concise follow-up naming only the failed checks from the output — nothing else. Then re-run the gate. Never advance the frontier while the gate fails.

Stop the loop and report if the gate keeps failing on the same check after a follow-up, or the ticket is blocked by missing authority, inaccessible context, or an external dependency. Report the ticket, the gate output, and the exact condition needed to resume. Do not skip ahead.

## 5. Repeat sequentially

Re-run the planner with the same journal and dispatch the new `next`. Later agents inherit earlier committed work through the shared repository.

Finish when the planner reports `remaining: 0`. Report the execution order, the ticket-to-commit mapping from the journal, the verification commands the gate ran, and anything that remains unverified — in particular, any acceptance criterion no `--verify` command actually exercised.
