---
name: implement
description: "Implement a piece of work based on a spec or set of tickets."
---

Implement the work described by the user in the spec or tickets.

Use /tdd where possible, at pre-agreed seams.

Run typechecking regularly, single test files regularly, and the full test suite once at the end.

Once done, use /code-review to review the work.

Act on the review before you finish. Fix every finding that leaves an acceptance criterion
of the assigned work unmet — an unmet criterion is not a follow-up, it is this ticket. Apply
the review's judgement calls and refinements only where they are cheap and clearly correct;
say which ones you declined and why. Never leave placeholder or stub values where the work
called for real ones.

Re-run typechecking and the full test suite after those fixes.

Commit your work to the current branch. A run that ends without a commit is an incomplete
run — report it as a failure and say what blocked the commit, rather than returning the
review as the result.
