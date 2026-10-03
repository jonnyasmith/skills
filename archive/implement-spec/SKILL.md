---
name: implement-spec
description: "Implement a specification in code."
disable-model-invocation: true
---

You have been provided a body of work to complete. It could be a spec with tickets, a single spec, an implementation plan, or something that describes the work that needs implementing.

Your goal is to implement the work and get it into a position where a PR or multiple PRs can be created. The work might span one or many repositories, so take that into account when breaking the work down.

Break the work down and generate a **task graph** with blocking relationships between them. This means there is always a **frontier** of tasks which are ready to be implemented. Understand the relationships for the graph, as some things can be done in parallel and others will be sequential.

Communications to and from you and the subagents must be strictly isolated. Communicate exclusively through **context pointers** (file paths to specs, plans, or research notes) and scope constraints (e.g., "Read `plan.md` and implement Phase 1 ONLY"). 
*   **Do not summarise the work.**
*   **Do not pass one subagent's self-verification or commentary to another subagent.** 
*   **Your prompts to subagents must be entirely objective and pointer-based.**

Your job is to be the orchestrator and not a doer. Use subagents for the work and aim for **maximum concurrency**.

## Steps

1. Understand the ask and generate a task graph.

2. (optional) Use an **exploration subagent** to conduct any exploration required by the tickets - relevant codebase files or external documentation. Ensure the exploration subagent can save files - it should save its markdown notes in a directory outside the repo, accessible by all future subagents. This lets **implementer subagents** focus on implementation rather than exploration.

3. Use branches for the work and worktrees for concurrent work on the same repo. Once tasks are complete, merge the changes back into the root feature branch which will be used for the final repo-level PR. Ensure all new worktrees branch from the latest root feature branch so they inherit previously completed tasks.

4. Use **builder subagents** to implement the tasks. Launch them using only file pointers to the original specification and the specific task boundary they are assigned to. 

5. Once a **builder subagent** completes, merge its work to the PR branch with a **merger subagent**. If merge conflicts occur, the merger subagent must resolve them or instruct the builder subagent to rebase and fix the conflicts.

6. If this changes the **frontier** of available tickets, kick off more **builder subagents** to work on the new tickets. This allows for maximum concurrency. If a builder fails after multiple attempts, mark the node as blocked or failed in the task graph, alert the user, and proceed with the remaining unblocked graph to prevent the orchestrator from stalling.

7. Run the project's test suite or linters against the root feature branch to catch basic syntax errors or failing tests before passing the code to a reviewer.

8. Once a phase or feature is complete, review the PR branches using a **critic subagent**. 
   *   **CRITICAL:** The critic subagent must be launched with a **completely fresh context**. 
   *   You must *only* pass the critic pointers to the original specification files and the branch to review. 
   *   Do not, under any circumstances, pass the builder's self-verification notes, summaries, or fixes to the critic. The critic must evaluate the raw code objectively against the original ask.
   *   Fix all issues raised by the code review using another **builder subagent**, again passing only the critic's output and the original spec. 
   *   **Limit this to exactly ONE round.** Once the builder subagent completes the fixes requested by the critic, consider the phase complete. Do not send the code back to the critic to prevent infinite review loops.

9. Clean up all **subagent** worktrees and worker branches.
