---
name: implement
description: "Implement a bounded piece of work from a spec or ticket, verify and commit it, run an independent two-axis code review from the original Git base, action every finding, and report a structured outcome. Use for direct implementation requests and delegated feature-ticket work."
disable-model-invocation: true
---

# Implement

Own implementation, verification, review findings, and commits for the supplied work item.

## 1. Pin the scope and base

Read the work item and its governing specification before changing code. Record the current `HEAD` as `base_sha`. If a delegating caller supplied an expected base, stop and report a blocker when it differs from `base_sha`.

## 2. Implement and verify

Use `/tdd` where possible at pre-agreed seams. Follow the repository's routed implementation and verification instructions.

Run typechecking and focused tests regularly. Run the repository's full required verification once implementation is complete. Do not continue to review with failing required checks unless the failure is demonstrably unrelated and reported as a blocker.

Never leave placeholder or stub values where the work called for real ones.

## 3. Commit the implementation

Commit the verified implementation to the current branch using `/conventional-commits`. The independent review needs a committed diff from `base_sha`; do not review only uncommitted working-tree changes.

## 4. Run independent review

Invoke `/code-review` with fixed point `base_sha`. Designate the root specification as governing and the work item as its scoped acceptance criteria. Wait for both the Standards and Spec axes. A skipped or failed axis is a blocker, not a completed review.

For every finding, either:

- fix it; or
- reject it with concrete evidence from the code or specification.

Fix every finding that leaves an acceptance criterion of the assigned work unmet — an unmet criterion is not a follow-up, it is this ticket.

If any fixes change the tree, rerun the required verification and commit the verified fixes using `/conventional-commits`. Do not mark the item complete while a finding is unaddressed or required verification is failing.

## 5. Report the outcome

Report these fields:

- `completed`: true only when implementation, required verification, both review axes, finding disposition, and all required commits succeeded
- `summary`: concise description of the implemented behavior
- `base_sha`: the recorded pre-implementation commit
- `commits`: implementation and review-fix commit SHAs
- `verification`: commands and outcomes
- `review`: Standards and Spec outcomes
- `finding_actions`: each finding fixed or rejected, with evidence
- `blocker`: null on success, otherwise the exact unresolved condition

A run that ends without a commit is an incomplete run — report it as a failure and say what blocked the commit, rather than returning the review as the result.
