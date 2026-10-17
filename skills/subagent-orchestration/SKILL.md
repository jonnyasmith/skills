---
name: subagent-orchestration
description: Rules for composing subagent and workflow work — model and effort per role, review policy, test gates, commits, and blocked steps. Use before spawning a subagent or writing a Workflow script.
---

# Subagent orchestration

## Models and effort

Set the model and effort on every subagent explicitly, from this table, unless the user asked for a different level.

| Role | Model | Effort |
|---|---|---|
| Implementation, reviews, planning, specs, final branch review | `opus` | `medium` |
| Fixes | `opus` | Rounds 1–2 `medium`, rounds 3–4 `high`, final round 5 `xhigh` |
| Test gates, checks, search and lookups (no edits) | `haiku` | `medium` |
| Commits (uses /conventional-commits) | `sonnet` | `medium` |

Only fixers escalate. When the task sets a different round limit, its final round runs at `xhigh`.

## Unit of work

Each unit (a milestone, module or fix) runs: build → review → fix → test gate → commit. The composition can vary by task; every unit ends with the full test suite passing and one commit.

## Reviews

A review is an adversarial check of what the implementer did, against the requirements as first written. Implementers game their checks: they edit the spec or plan to fit the code, weaken or delete tests, write tests that pass whatever the code does, and report work as done when it isn't. The reviewer is there to catch that.

- **Give the reviewer everything, and trust none of it.** A fresh context, the original requirements, the full diff (code, tests, docs, config) and the implementer's report. Every claim in the report is something to disprove, not a summary to accept.
- **Read the code.** Check what it actually does against each requirement. Running it backs this up; it doesn't replace it.
- **Audit the guardrails in the diff:**
  - requirements, plans, specs or docs changed to fit the code;
  - tests deleted, skipped or loosened, assertions removed, expected values changed to match the output;
  - new tests that would pass without the fix: in a scratch copy or worktree, undo the fix and check they fail;
  - special cases for tests, silenced warnings or lint, swallowed errors, stubs and TODOs.
- **One verdict per requirement:** met, not met or can't tell, each with evidence. Use one reviewer per unit; split a unit only when it is too big for one reviewer to read.
- **Keep every finding.** The reviewer reports everything with a severity. The script decides what goes back for fixing: correctness, requirement and guardrail gaps do, style doesn't. Notes that don't go back are listed in the final report, never dropped.
- **Can't tell isn't a pass,** but it isn't a fix round either. Report it to the user as unverified.
- **Be suspicious of a clean sweep.** If every reviewer passes first time, read what they did before reporting success.
- **Add agents only on need.** Start from one implementer and one reviewer per unit. A fixer and a re-review run only for a unit whose review found gaps.
- **Rounds.** Fix rounds continue, escalating as above, until the review passes or the round limit is reached: 5 rounds unless the task sets its own. At the limit, stop work on the unit, don't commit it, and report it to the user as blocked with the findings still open.

## Test gate

Before each commit the full test suite passes and no data or constrained files changed. A `haiku` gate agent runs it and reports the output; a `sonnet` agent commits only after the gate passes. Give the exact commands, including any environment setup a fresh shell needs (for example loading `JAVA_HOME`). A gate that can't run is a broken gate command: fix the command, and don't count it as a pass or a code failure.

## Prompting subagents

- Point to the spec and files by path instead of pasting them.
- State the hard constraints, the scratch directory, and what the agent must not touch.
- Ask for a short report that ends with a "Deviations" list; the commit body carries it.

