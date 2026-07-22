# Lightweight Lane

Use this only after the entrypoint classified the change as non-behavioural.

- Keep the diff within that classification. If it changes behaviour, build
  wiring, configuration, generated artefacts, or a contract, switch to the
  standard lane.
- Run the repository's mandatory gate and `git diff --check`.
- State why independent review was skipped and what remains unverified.

Completion: mandatory checks pass and the reported scope still qualifies as
lightweight.
