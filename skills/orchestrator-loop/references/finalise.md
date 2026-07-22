# Finalise

- Fix every hard finding and any inexpensive, valid drift found in review. Do
  not add speculative machinery for a future-only judgement call; record it as
  a future note.
- Classify every failed check as a product regression, flaky test, environment
  or tooling failure, or pre-existing failure. Capture evidence; never waive or
  relabel it without a reason.
- Re-read the original request against the final diff for stale assumptions,
  safety regressions, unrelated edits, and policy violations.
- Run every goal's stated acceptance evidence, then the repository's full
  required gate. If none exists, run the narrowest useful formatter, tests,
  build/type check, and `git diff --check`.
- If rectification changes code, repeat relevant checks; if it changes a
  required artefact or baseline, repeat the complete gate.
- Follow the repository's commit policy. Commit only verified, in-scope work;
  stage only files belonging to this delivery loop.
- Report goals completed, changes, all review outcomes, verification run, size
  or generated-file changes, and unverified real-world boundaries. Include an
  evidence matrix: goal, verification, and remaining uncertainty.

Completion: the required gate passes on the final diff and the user can see
the commit, evidence, and remaining uncertainty.
