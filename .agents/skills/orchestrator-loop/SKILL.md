---
name: orchestrator-loop
description: Orchestrate or execute a bounded code change through planning, implementation, independent review, verification, and commit. When collaboration tools are available, the primary/root agent delegates each delivery loop to a worker and remains an orchestrator; use this for one implementation request or a hierarchy of nested issues.
---

# Orchestrator Loop

Close a bounded implementation request through one **delivery loop**: set
verifiable goals, build, independently review, rectify, verify, and hand off.

## Route ownership first

Determine the current agent's role before taking any implementation action.

- **Primary/root agent with collaboration tools:** orchestrate only. Do not edit
  files, install dependencies, run implementation tests, stage, or commit. Read
  enough repository and issue context to map scope and dependencies, create the
  visible task list, delegate each bounded delivery loop to a worker, inspect
  handoffs, resolve blockers, and report progress.
- **Delivery worker:** own the complete bounded loop below, including edits,
  focused evidence, independent reviews, rectification, final verification,
  staging, and commit. A worker may spawn review-only agents as required by
  [reviews.md](references/reviews.md); do not delegate its implementation back
  to the primary agent.
- **Review worker:** review only the named diff and report findings; never edit,
  verify, stage, or commit unless explicitly reassigned as the delivery worker.
- **No collaboration tools:** execute the loop directly as the delivery worker.

For a parent issue, epic, task list, or request to run nested issues:

1. Resolve the full descendant hierarchy and dependency edges before dispatch.
2. Give each issue to a distinct delivery worker with its issue/spec, baseline,
   applicable repository instructions, dependencies, and required commit
   boundary. One issue equals one complete delivery loop and one commit.
3. Dispatch in dependency order. In a shared worktree, run delivery workers
   sequentially unless their changes are proven disjoint and their commits
   cannot race. Use parallel workers only with isolated worktrees or an equally
   explicit integration plan.
4. Require each handoff to name the commit, acceptance evidence, independent
   review outcomes, rectifications, and anything unverified. Update the visible
   task list from that evidence; never mark an issue complete from activity
   alone.
5. If a worker is blocked, the primary agent resolves the approval, user choice,
   or dependency and resumes that worker. The primary agent must not silently
   take over implementation.

These ownership rules are part of the skill's correctness. Do not begin the
steps below until the work is held by a delivery worker.

## 1. Establish the goals

- Read applicable repository instructions. In a repository, record and resolve
  the starting commit with `git rev-parse HEAD`.
- Keep one named diff for the loop: `git diff <baseline>` before committing, or
  `git diff <baseline>...HEAD` after committing. Do not review an empty or
  invalid diff. Preserve unrelated worktree changes.
- Find the spec in this order: linked issue, user-supplied path, matching
  project spec, then the original request and agreed decisions. If none exists,
  say that the Spec review is unavailable rather than inventing one.
- Identify changed public contracts, persisted data, migrations, and external
  tools. Make an explicit compatibility decision and name its proof before
  editing.
- Stop and ask before an irreversible external action, production access, a
  new credential or permission, or a user choice that materially changes the
  outcome.
- Define verifiable goals that make progress and dependencies visible. Each
  goal states an observable end state, preserved invariants, acceptance
  evidence, and remaining uncertainty. Split only for independent evidence or
  blocking relationships. Do not impose a numeric task cap: use as many tasks
  as the work needs to make progress and dependencies legible. Never mark a
  goal complete until its evidence passes.
- Before substantive work, turn those goals into a living task list in the
  environment's available progress-tracking surface. Keep every task's status
  current as work, review, and verification proceed; add, split, or retire
  tasks when discovery changes the delivery loop. If the environment has no
  such surface, maintain an equivalent concise checklist in the conversation.
  Do not rely on unrecorded mental progress.
- If discovery changes a goal or invariant, record why, revise its evidence,
  and surface the decision; never silently drift scope.

Completion: the work has a baseline, bounded goals, current visible task
states, and acceptance evidence.

## 2. Route the delivery loop

- For documentation, comments, formatting, or a mechanical move with no
  behaviour, build, configuration, generated-artifact, or contract change,
  read [lightweight-lane.md](references/lightweight-lane.md) now, then read
  [finalise.md](references/finalise.md) after its checks pass.
- Otherwise, read [execution.md](references/execution.md) now. For each goal,
  load the applicable verification reference:
  [web](references/web-verification.md), [API](references/api-verification.md),
  [firmware](references/firmware-verification.md),
  [data](references/data-verification.md), or, only when existing
  infrastructure cannot prove the goal,
  [harnesses](references/verification-harnesses.md).
- After all goals have focused evidence, read [reviews.md](references/reviews.md).
  After reviews complete, read [finalise.md](references/finalise.md).

Never bypass a repository's mandatory gate or `git diff --check`.
