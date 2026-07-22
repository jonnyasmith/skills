# Firmware Verification

- Use the repository's host tests, device build, size, and formatting gates.
- Add bench or hardware-in-the-loop proof when the goal depends on real
  silicon, a peripheral, timing, power, or a physical wire contract.
- Treat a successful fake as silicon-model evidence, not bench proof. Record
  every unverified hardware boundary explicitly.
