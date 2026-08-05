---
name: feature-ticket-delegator
description: "Resolve the descendants of a supplied root issue, feature, or local Markdown item, then delegate each ready work item to a fresh /implement worker one at a time. Use when the user wants a hierarchy implemented sequentially without the host reimplementing, re-verifying, or maintaining a ticket journal."
---

# Feature Ticket Delegator

Coordinate a work-item hierarchy; do not implement or verify individual items in the host.

## 1. Resolve the hierarchy

Read the repository's issue-tracker convention from its routed instructions. Use that configured source: GitHub Issues, Azure DevOps Boards, local Markdown, or another documented tracker.

Load the supplied root item and discover its descendants using the tracker's documented hierarchy relationships. Preserve each item's actual type; it may be a bug, issue, story, PBI, requirement, or Markdown file.

Keep only implementation-ready descendants in scope. Determine a deterministic sequence from explicit dependencies or blocker links. If no dependency data exists, use the source order and state that assumption. Do not create local ticket copies, JSON staging files, journals, or planning scripts. Existing local Markdown items are source material, not staging files.

## 2. Delegate one item

For the next item, start one fresh sub-agent with this prompt:

`Use /implement to implement <item reference>. Read the item and its root item <root reference> using the repository's configured issue tracker before changing code.`

Pass no pasted item body unless the tracker is inaccessible. Do not begin another item while that worker is active.

## 3. Advance on the worker result

Treat a completed /implement result as the item's completion signal. The /implement skill owns implementation, tests, review, and commit; do not rerun those checks, inspect the working tree, or add a second gate.

If the worker reports a failure, blocker, or required user decision, stop the sequence and report it. Send a concise follow-up to the same worker only when it identifies a concrete, addressable failure.

After a successful result, delegate the next ready item. Continue until every in-scope item has completed.

## 4. Finish

Report the completed items, their implementation-worker outcomes, and anything blocked or excluded. A top-level caller may request one final batch review; do not perform it implicitly.
