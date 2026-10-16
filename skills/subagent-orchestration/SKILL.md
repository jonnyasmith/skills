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
| Acceptance criteria and failing checks | `opus` | Never the implementer |
| Grading, refuting and critique | `opus` | Fresh context, see Reviews |
| Planning, specs, final branch review | `opus` | |
| Rote work: search, lookups, test runs, gates | `haiku` | No edits |
| Commits | `sonnet` | Uses /conventional-commits |

Escalation: when an implementer fails twice (tests still failing, or the same blocking finding comes back), retry with `opus`.

## Unit of work

Each unit (a milestone, module or fix) runs: acceptance criteria and failing checks → build → grade and refute → fix → test gate → commit. The composition can vary by task; every unit ends with the full test suite passing and one commit.

## Reviews

A review exists to stop bad work, so build it so that passing is hard. A reviewer that passes everything is broken, not reassuring.

- **Criteria and checks first.** Before building, turn each requirement or finding into concrete acceptance criteria and, wherever possible, a check that fails now: a test, a script or a reproduction. An agent other than the implementer writes the checks and runs them to show they fail. Prefer these deterministic checks; use model judgement only for what a check can't cover.
- **The burden of proof is on the work.** Graders start from "not met". A criterion is met only with evidence the grader produced itself (a command and its output, a test, a screenshot). Unknown counts as not met.
- **Cold, narrow graders.** A grader sees the diff, the criteria and the code, never the implementer's report or reasoning. Give each grader one lens (correctness and races; the requirement as written; regressions in the running app; the domain risk, such as security or privacy), with a verdict per criterion, instead of one reviewer for a whole unit. Group small criteria under a lens rather than spawning an agent per line.
- **A refuter.** Separately, one agent per unit tries to break the change by writing a new failing test or reproduction. A break that holds is a failure.
- **The script decides, not the reviewer.** Graders return pass, fail or unknown per criterion with evidence, plus every other observation. They don't return a pass flag of their own choosing. In code: any fail or unknown goes back to the fixer; other observations are kept and listed in the final report, never dropped. Grade correctness and the stated requirements, not style.
- **Calibrate.** In each run, give one grader a copy of the work with a known planted defect (in a worktree, never committed) and check it is caught. If it isn't, stop and report: the review can't be trusted.
- **Read before trusting.** If every grader passes first time, check what they actually ran before reporting success.
- **Rounds.** Fix and re-grade until every criterion passes. Stop after 5 rounds, or 2 rounds in a row with no progress, and report what is unresolved.

## Test gate

Before each commit, a `haiku` agent runs the full test suite and checks that no data or constrained files changed. Give it the exact commands, including any environment setup a fresh shell needs (for example loading `JAVA_HOME`). A gate that can't run is a broken gate command: fix the command, and don't count it as a pass or a code failure. If the code fails the gate, one `opus` repair attempt, then stop and report.

## Prompting subagents

- Point to the spec and files by path instead of pasting them.
- State the hard constraints, the scratch directory, and what the agent must not touch.
- Never pass an implementer's report or reasoning to a grader or refuter.
- Ask for a short report that ends with a "Deviations" list; the commit body carries it.

