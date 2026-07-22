# Standard Execution

- Inspect existing seams and tests before editing.
- For a behaviour change at a pre-agreed seam, prefer red-first: add or adjust
  an external-behaviour test, observe it fail, then implement. Skip this only
  for documentation, mechanical moves, or genuinely untestable hardware work.
- Implement the smallest coherent change. Run type checks after interface,
  type, or build-graph changes, and the narrowest single test after each
  behaviour slice.
- Follow repository requirements for formatting, generated files, size
  baselines, documentation, and architecture records.

Do not begin review before all goals have focused evidence.

Completion: every goal is implemented, revised explicitly, or rejected as out
of scope; focused evidence passes.
