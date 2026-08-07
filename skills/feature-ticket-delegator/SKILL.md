---
name: feature-ticket-delegator
description: "Resolve and deterministically plan the descendants of a supplied root issue, feature, or local Markdown item, then delegate each ready work item to a fresh /implement worker one at a time and run a final whole-branch review. Use when the user wants a spec-backed hierarchy implemented sequentially with isolated workers and independent review."
---

# Feature Ticket Delegator

Coordinate the workflow. Do not implement or verify individual items in the host.

## 1. Resolve and plan the hierarchy

Read the repository's issue-tracker convention from its routed instructions. Use that configured source: GitHub Issues, Azure DevOps Boards, local Markdown, or another documented tracker.

Load the supplied root item and discover its descendants using the tracker's documented hierarchy relationships. Preserve each item's actual type; it may be a bug, issue, story, PBI, requirement, or Markdown file.

Include every governed leaf work item in the planner input, including completed items and blockers of pending work. Exclude hierarchy containers that are not themselves implementation units. Represent hosted items as a JSON array of `{id|number, title, body, state?, url?}` using each item's full body; use local Markdown items in place. A temporary hosted-item export may live outside the repository, but do not create ticket copies, journals, or planning scripts in the repository.

Resolve `<plan.mjs>` to the sibling `../implementation-loop/scripts/plan.mjs` in this skill collection and run it without a journal:

- For local Markdown, run `node <plan.mjs> --dir <items-directory>`.
- For hosted items, run `node <plan.mjs> --json <temporary-export>`.

Treat planner errors, dangling blockers, and dependency cycles as blockers. Use the emitted `tickets` order and skip entries whose `done` field is non-null. Do not improvise a second ordering algorithm. If the planner is unavailable, stop and report that dependency rather than silently changing semantics.

Record the current `HEAD` as `branch_base` before starting the first worker. If no items remain, report `completed: true` with `final_review: not_run_no_changes` and stop.

## 2. Delegate one item

For each remaining item, record the current `HEAD` as `item_base`, then start one fresh sub-agent with this prompt:

`Use /implement to implement <item reference>. Read the item and its governing root specification <root reference> using the repository's configured issue tracker before changing code. Your reported base_sha must equal <item_base>.`

Pass no pasted item body unless the tracker is inaccessible. Do not begin another item while that worker is active.

## 3. Advance on the worker result

Require the worker to report the structured `/implement` outcome: `completed`, `summary`, `base_sha`, `commits`, `verification`, `review`, `finding_actions`, and `blocker`.

Treat `completed: true` as the item's completion signal only when `base_sha` equals `item_base`, verification passed, both review axes completed, every finding was fixed or rejected with evidence, and at least one commit was reported. The `/implement` skill owns those operations; do not reimplement the item or rerun its checks in the host.

If the worker reports a failure, blocker, or required user decision, stop the sequence and report it. Send a concise follow-up to the same worker only when it identifies a concrete, addressable failure.

After a successful result, delegate the next ready item. Continue until every in-scope item has completed.

## 4. Review the whole branch

After every item succeeds, invoke `/code-review` with fixed point `branch_base` and the root item as the explicit governing specification. Wait for both the Standards and Spec reviews. A skipped or failed axis is a blocker, not a clean review.

If neither review reports findings, finish. Otherwise start one fresh fix sub-agent. Give it `branch_base`, the root specification, both review reports, and this contract:

1. Inspect the whole branch diff from `branch_base`.
2. Fix each valid finding or reject it with concrete code evidence.
3. Run the repository's required verification after all fixes.
4. Commit verified fixes using `/conventional-commits`.
5. Report `completed`, `commits`, `verification`, `finding_actions`, and `blocker`.

Do not implement final-review fixes in the host. Stop and report the blocker if the fix worker cannot complete the contract.

## 5. Finish

Report these top-level fields:

- `completed`: true when no work remained, or when every pending item worker, both final review axes, and any required final fix worker completed
- `branch_base`: the recorded pre-workflow commit
- `planned_order`: the planner's complete order
- `skipped`: items the planner marked done or the workflow excluded, with reasons
- `items`: each delegated item's structured `/implement` outcome
- `final_review`: Standards and Spec outcomes
- `final_finding_actions`: each final finding fixed or rejected, with evidence
- `commits`: all item and final-fix commit SHAs in order
- `blocker`: null on success, otherwise the exact unresolved condition
- `not_reached`: planned pending items not attempted because the workflow halted
