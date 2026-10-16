---
name: subagent-orchestration
description: Rules for composing subagent and workflow work — model and effort per role, review policy, test gates, commits, and blocked steps. Use before spawning a subagent or writing a Workflow script.
---

# Subagent orchestration

## Models and effort

Set the model on every subagent explicitly. Reasoning effort is `medium` for all subagents unless the user asked for a different level.

| Role | Model | Notes |
|---|---|---|
| Implementation: clear, narrow task | `sonnet` | One module, a fix, a well-specified milestone |
| Implementation: large or judgement-heavy | `opus` | Multi-file features, UI and visual work, unclear specs |
| Implementation: UI changes | `opus` | Anything to do with UI work |
| Fix after review | Same as the implementer | Escalate to `opus` on the second round |
| Review and critique | `opus` | Fresh context |
| Planning, specs, final branch review | `opus` | |
| Rote work: search, lookups, test runs, gates | `haiku` | No edits |
| Commits | `sonnet` | Uses /conventional-commits |

Escalation: when an implementer fails twice (tests still failing, or the same blocking finding comes back), retry with `opus`.

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
- **One verdict per requirement:** met, not met or can't tell, each with evidence. Split a large unit between two or three reviewers by area.
- **Keep every finding.** The reviewer reports everything with a severity. The script decides what goes back for fixing: correctness, requirement and guardrail gaps do, style doesn't. Notes that don't go back are listed in the final report, never dropped.
- **Can't tell isn't a pass,** but it isn't a fix round either. Report it to the user as unverified.
- **Be suspicious of a clean sweep.** If every reviewer passes first time, read what they did before reporting success.
- **Rounds.** At most two fix rounds per unit, unless the task sets its own limit.

## Test gate

Before each commit, a `haiku` agent runs the full test suite and checks that no data or constrained files changed. Give it the exact commands, including any environment setup a fresh shell needs (for example loading `JAVA_HOME`). A gate that can't run is a broken gate command: fix the command, and don't count it as a pass or a code failure. If the code fails the gate, one `opus` repair attempt, then stop and report.

## Prompting subagents

- Point to the spec and files by path instead of pasting them.
- State the hard constraints, the scratch directory, and what the agent must not touch.
- Ask for a short report that ends with a "Deviations" list; the commit body carries it.

