## Final Review Loop

Before marking any task as complete, execute and explicitly document the following steps in order:

1. **Re-read:** Review the original request against the changes actually made.
2. **Critique:** Check the changes or outputs for correctness, completeness, stale assumptions, and policy violations.
3. **Rectify:** Fix any issues found during the critique step.
4. **Verify:** Re-run the narrowest useful verification applicable to the task (e.g., linter, specific test suite, compiler check).
5. **Report:** Conclude with a clear summary stating:
   - What changed
   - What was verified (and how)
   - What remains unverified

## Git Commit Protocol

If the changes successfully pass verification and are inside a repository, automatically stage and commit them using the /conventional-commits skill.

## PR Instructions

Follow /write-pull-requests skill when creating PRs.
