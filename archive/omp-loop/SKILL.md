---
name: omp-loop
description: Run the implementation-loop as an executed program rather than followed instructions, using omp's eval runtime to dispatch each ticket, gate it, and resume from a journal. Use when the user wants a spec's tickets implemented end to end in one unattended run, or names this skill directly. Requires omp's eval tool.
disable-model-invocation: true
---

# omp Loop

Runs the `implementation-loop` as a program. Same tickets, same ordering, same gate — but the control flow is a `while` loop in `scripts/driver.mjs` instead of instructions you follow, so no execution path can skip a gate, reorder a frontier, or advance past a failure.

Use `/implementation-loop` when you want to supervise ticket by ticket. Use this when you want to hand over the batch and read a report.

**Requires omp**: the driver needs the `eval` tool's host-side `agent()` and `tool.hub()`. Under any harness without them, use `/implementation-loop` instead — it does the same work by hand.

## What this skill owns

Only the driving. Ticket ordering and completion belong to `implementation-loop`'s `plan.mjs` and `gate.mjs`; the driver executes those scripts and never re-implements their decisions. It defaults to finding them in the sibling skill, so a missing `implementation-loop` skill breaks this one.

## 1. Gather the run inputs

- **Tickets** — a directory of per-ticket markdown (`--dir`), or a tracker dump: `gh issue list --json number,title,body,state`, written to a file. Include every ticket in the set; the planner needs the whole graph to resolve blockers.
- **Journal** — a path that persists for the run, e.g. `.scratch/<slug>/loop-journal.jsonl`. This is what makes an interrupted run resume instead of restart. Reuse the same path across re-runs; a fresh path re-does completed tickets.
- **Verification** — the project's real type-check and test commands. Without them the gate proves only that something was committed to a clean tree, and the run report will say so.
- **Spec reference** — needed only when the tickets do not link the governing spec themselves.

## 2. Preview the plan

Never dispatch before showing the user what will run. This is free — no agents spawn:

```
node <implementation-loop>/scripts/plan.mjs --dir <issues> --journal <journal>
```

Report `order`, `next`, and any already-done tickets. A non-zero exit means the ticket set is unsound — a cycle, a dangling blocker, a duplicate id. Report the `errors` array and stop. Do not repair the graph by inference: a blocker pointing at nothing is a defect in the tickets, and guessing its target silently changes what gets built.

## 3. Run the loop

One `eval` JS cell. Give it a generous `timeout` — the per-cell budget measures runtime work, not wall clock, and pauses while a sub-agent is in flight, so a long run does not exhaust it:

```js
const { runLoop } = await import(
  `${process.env.HOME}/.claude/skills/omp-loop/scripts/driver.mjs`);

return await runLoop(
  { agent, hub: (a) => tool.hub(a), log },
  {
    ticketsDir: ".scratch/<slug>/issues",   // or ticketsJson: "<dump>.json"
    journal:    ".scratch/<slug>/loop-journal.jsonl",
    repo:       process.cwd(),
    verify:     ["<typecheck cmd>", "<test cmd>"],
    specRef:    "<spec path>",              // omit when tickets link the spec
  },
);
```

`journal` and one of `ticketsDir`/`ticketsJson` are required; everything else has a default. Pass `scriptsDir` only when `implementation-loop` lives somewhere other than the sibling directory.

Other options: `order` (explicit user sequence, honoured only within dependency constraints), `requireCriteria` (also demand the ticket's checkboxes be ticked), `agentType`, `maxFollowUps` (default 1), `maxTickets` (runaway guard, default 100).

Do not babysit the cell, and do not run anything else against the repository while it is live — the sub-agents are committing to the working branch.

## 4. Report the outcome

`ok: true` with `remaining: 0` is the only success. Report the execution order, the ticket-to-commit mapping from `completed`, the commands in `verifiedBy`, and `unverifiedNote` when it is set.

Each completed ticket carries `transcript: "agent://Ticket-<id>"`. Read it before explaining what a ticket actually did — do not narrate from the ticket title.

On `abort`, report the reason, the evidence, and the exact condition needed to resume. Never present a partial run as a complete one:

| `abort.reason` | Meaning | Resolution |
| --- | --- | --- |
| `plan-error` | unsound ticket graph | fix the tickets; nothing was dispatched |
| `gate-failed` | ticket still failing after its follow-up | report `abort.failed`; needs a human decision |
| `agent-failed` | the spawn itself errored | usually config; report `detail` verbatim |
| `follow-up-failed` | `hub` could not reach the sub-agent | re-run; finished tickets are preserved |
| `stalled` | a green ticket stayed on the frontier | the journal and planner disagree — check the paths match |

To resume after any abort or interruption, re-run the identical cell. Completed tickets are skipped; at most the in-flight ticket is lost.

## Modifying the driver

`scripts/test.mjs` fakes only `agent` and `hub` — `plan.mjs`, `gate.mjs`, and git are real. Run `node scripts/test.mjs` after any change. It covers the happy path, follow-up repair, persistent gate failure, an unsound graph, and the stall guard.

Fakes cannot catch host-bridge contract errors; those surface only in a live run. Prove any change to the dispatch path against a throwaway git repo with one trivial ticket before using it on real work.
