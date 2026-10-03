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
| Fix after review | Same as the implementer | Escalate to `opus` on the second round |
| Review and critique | `opus` | Fresh context |
| Planning, specs, final branch review | `opus` | |
| Rote work: search, lookups, test runs, gates | `haiku` | No edits |
| Commits | `sonnet` | Uses /conventional-commits |

Escalation: when an implementer fails twice (tests still failing, or the same blocking finding comes back), retry with `opus`.

## Unit of work

Each unit (a milestone, module or fix) runs: build → review → fix → test gate → commit. The composition can vary by task; every unit ends with the full test suite passing and one commit.

## Reviews

- Default to one adversarial reviewer per unit, with a fresh context. Give it a short checklist made for what was built: plan coverage, correctness, plus the one risk that matters most here (security, privacy, UI, docs).
- Add another agent only for a distinct job one reviewer can't do in the same pass, such as running real data or checking screenshots.
- Reviewers confirm a finding (run it or reproduce it) before marking it blocking.
- At most two fix rounds per unit.

## Test gate

Before each commit, a `haiku` agent runs the full test suite and checks that no data or constrained files changed. If the gate fails, one `opus` repair attempt, then stop and report.

## Prompting subagents

- Point to the spec and files by path instead of pasting them.
- State the hard constraints, the scratch directory, and what the agent must not touch.
- Ask for a short report that ends with a "Deviations" list; the commit body carries it.

