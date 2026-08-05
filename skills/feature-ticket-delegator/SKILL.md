---
name: feature-ticket-delegator
description: "Resolve the ordered work items under an Azure DevOps feature, then delegate each ready PBI to a fresh /implement worker one at a time. Use when the user gives a feature reference and wants its children implemented sequentially without the host reimplementing, re-verifying, or maintaining a ticket journal."
---

# Feature Ticket Delegator

Coordinate a feature's implementation; do not implement or verify individual PBIs in the host.

## 1. Resolve the feature

Load the feature and its descendant work items from the tracker. Keep only implementation-ready PBIs in scope; report missing, ambiguous, blocked, or non-PBI items instead of guessing.

Determine a deterministic sequence from explicit dependencies or blocker links. If no dependency data exists, use the tracker order and state that assumption. Do not create local ticket copies, JSON staging files, journals, or planning scripts.

## 2. Delegate one PBI

For the next PBI, start one fresh sub-agent with this prompt:

`Use /implement to implement <PBI reference>. Read the PBI and its parent feature <feature reference> in Azure DevOps before changing code.`

Pass no pasted ticket body unless the tracker is inaccessible. Do not begin another PBI while that worker is active.

## 3. Advance on the worker result

Treat a completed /implement result as the PBI's completion signal. The /implement skill owns implementation, tests, review, and commit; do not rerun those checks, inspect the working tree, or add a second gate.

If the worker reports a failure, blocker, or required user decision, stop the sequence and report it. Send a concise follow-up to the same worker only when it identifies a concrete, addressable failure.

After a successful result, delegate the next ready PBI. Continue until every in-scope PBI has completed.

## 4. Finish

Report the completed PBIs, their implementation-worker outcomes, and anything blocked or excluded. A top-level caller may request one final batch review; do not perform it implicitly.
