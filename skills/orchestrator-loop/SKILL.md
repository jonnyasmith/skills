---
name: orchestrator-loop
description: Work through a set of workitems — a spec's tickets, a task list, or a hierarchy of nested issues — by delegating each one to a fresh sub-agent that uses the implement skill. Use when the user hands you the whole batch and wants it built without invoking implement against each workitem themselves.
disable-model-invocation: true
---

# Orchestrator Loop

Orchestrate the work; never implement a workitem in the host agent. Keep exactly
one workitem in flight at a time. The point is to take the user out of the loop:
they hand you the batch once, you drive every workitem to a commit.

## 1. Resolve the workitems

Read the spec, task list, or issue hierarchy the user supplied. Fetch referenced
issue bodies and their relevant comments. For each workitem, record its
reference, acceptance criteria, blockers, and status. Treat a workitem as
already complete only when its source says so or the repository clearly shows
its acceptance criteria pass.

## 2. Order them

Build a dependency graph from the workitems' blocking edges. Reject cycles and
missing references. Dispatch in dependency order; when several are ready, prefer
the user's explicit order, then prerequisite or foundational work, then whatever
unlocks the most remaining work, then the published order as a tie-breaker.

## 3. Delegate one workitem

Spawn one fresh sub-agent for the selected ready workitem with a compact prompt:

`Use /implement to implement <workitem reference>.`

If the workitem does not itself link the governing spec, append
`The governing spec is <spec reference>.` Do not paste the workitem or spec into
the prompt when the references are accessible — the sub-agent loads the
authoritative sources itself. Do not ask it to use this skill, and do not start
any other workitem while this agent is active.

## 4. Close the loop

Wait for the sub-agent. Confirm from its result and the repository that the
acceptance criteria are met, the verification and review required by `/implement`
succeeded, and the work was committed to the current branch.

If the result is incomplete but recoverable, send the same sub-agent a concise
follow-up naming only the unmet criterion or failing check, then wait again.
Never advance while the current workitem is incomplete.

If it is blocked by missing authority, inaccessible context, or a failure you
cannot resolve safely, stop and report the workitem, the evidence, and the exact
condition needed to resume. Do not skip ahead.

## 5. Repeat

Record the workitem and its commit as done, recompute the ready set, and repeat
from step 3. Later sub-agents inherit earlier committed work through the shared
repository.

Finish when every workitem is complete. Report the execution order, the
workitem-to-commit mapping, and anything left unverified.
