---
name: implement-spec
description: "Implement a specification in code."
disable-model-invocation: true
---

You have been provided a spec. This spec should have tickets associated with it, describing how to implement the spec.

The goal is a PR which implements the entire spec on a single branch.

The tickets are not a list of steps. They are a **task graph** with blocking relationships between them. This means there is always a **frontier** of tickets which are ready to be grabbed.

Communication to and from subagents should be sparse. Communicate primarily through **context pointers**: to the spec, tickets, research notes, and previous commits. Don't duplicate information already available via pointers.

**Builder subagents** should be run in the background where possible for **maximum concurrency**.

## Steps

1. Read the spec and tickets. Read enough to understand the task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Create a branch. Create the PR as a **draft**, marked as 'closing' the spec issue and tickets. A draft PR is a place to put work, not a claim that the work is done: it stays draft until the review loop below closes clean.

4. Use **Builder subagents** to implement each ticket. Each implementer subagent should work in its own worktree, on its own branch.

5. Once an **Builder subagent** completes, merge its work to the PR branch with a **merger subagent**.

6. If this changes the **frontier** of available tickets, kick off more **builder subagents** to work on the new tickets. This allows for maximum concurrency.

7. **Review each build unit, not the branch.** One **Critic subagent** per unit, all dispatched in one batch, each in a fresh context with no knowledge of any other review. A unit is one builder's assignment, named by its commits. Scope each critic to those commits and tell it which sibling commits belong to other units, so it reads them as context and does not review them. A critic that sees the whole branch lets a weak unit hide behind a strong one. Give every critic the spec as the authority, and require `file:line` evidence and a severity of `blocker`, `major` or `minor` for each finding.

8. **Adjudicate every finding yourself, against the spec, before dispatching any fix.** Critics over-reach: they infer requirements the spec does not state, and they contradict each other. For each finding decide upheld or rejected, and record the reason. Pass the rejected list to the fix agents explicitly, or they will implement it anyway. You hold the spec and the conversation; the critics hold neither.

9. **Fix upheld findings with Builder subagents, one per repository or other disjoint ownership boundary.** Require each builder to prove every test it adds or changes fails before its change and passes after, and to report that mutation by name. "Tests added" is not evidence. Require it to report defects it finds but was not assigned, without repairing them.

10. **A fix is a new build unit, so it gets its own review round.** Return to step 7 with the fix commits as the units, plus any defect a fix agent reported. Loop until a round upholds no `blocker` and no `major`. Rounds should shrink; a round that grows means the units are wrongly drawn.

11. Re-run the repository's own gates yourself — format, build, full test suite — and read the numbers. A subagent's claim of a green run is not verification.

12. Mark the PR ready for review. Its description must state what the tests do not prove, which questions the spec leaves open, and any limitation accepted rather than fixed. If the loop never closed clean, the PR stays draft and you say why.

13. Clean up all **builder subagent** worktrees.
