# Verification Harnesses

Use this only when existing repository infrastructure cannot prove a goal.

- Build the smallest isolated harness that observes the external contract.
- Keep it temporary or scratch-scoped unless it is reusable verification
  infrastructure. Never turn it into a second product or production path.
- Use an independent oracle where practical: a visible result, contract
  consumer, golden output, or separate fake.
- Control fixtures, time, randomness, and cleanup. Record the command and
  evidence in the final report.
