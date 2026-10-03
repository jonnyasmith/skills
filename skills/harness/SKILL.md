---
name: harness
description: Verify a product feature locally with the ii-test-harness. Use when asked to scope services, create a workspace, start a per-run runtime, write a scenario first, iterate on it, run `bin/harness accept` and attach the report.
disable-model-invocation: true
---

# Harness feature workflow

Work from a checkout of the harness repository (`dywidag/ii-test-harness` on GitHub); if you do not know
where it is checked out, ask. Its README is the reference; this skill only sequences it. Do not
touch primary checkouts, unrelated Docker containers or secrets (see `AGENTS.md`).

1. **Scope.** List the services the feature needs and check each has a `catalogue/<service>.json`.
   If one is missing, or depends on a service with no emulator, follow README "Adding an app"
   (including the product code seams) and "Faking a dependency with no emulator".
2. **Workspace.** Write `features/<name>/workspace.json` (README "Feature workflow", step 2), then
   `bin/harness workspace new features/<name>/workspace.json --dir <dir>`, or `workspace adopt` for
   existing worktrees. Do all edits to product code in `<dir>`.
3. **Feature definition.** Write `feature.json` and its SQL, WireMock, Service Bus, fixtures and suites
   following README "Feature format". Check the limits in "Current limits" before choosing services.
4. **Runtime.** Pick a run ID `hx-$(date -u +%Y%m%dT%H%M%SZ)-$(openssl rand -hex 4)` and run
   `bin/harness runtime start <runId> --workspace <dir> --feature <name> --build` (services default to the feature's `defaultServices`). Use `runtime
   status` and `runtime logs` when a service is not ready.
5. **Scenario first.** Write the scenario before the change (README "Scenarios"), run
   `bin/harness scenario <runId> <scenario.json>`, and confirm it fails for the expected reason.
6. **Iterate.** Change code in the workspace, `runtime restart <runId> --services <name>`, rerun the
   scenario. Do not weaken assertions or skip steps to get a pass.
7. **Accept.** `bin/harness accept --workspace <dir> --feature <name> [--suite s] [--focus x]`; read
   `REPORT_DIR=` from standard output. Use focused runs while iterating and one full run to finish.
8. **Report.** Check `REPORT_DIR/report.json`: `status` is `passed`, and `sources` shows the heads you
   intend to submit with `dirty` false. Attach the report to the pull request; say which checks did
   not run.
9. **Clean up.** `runtime reset <runId> --workspace <dir> --feature <name>` for any run you started
   by hand.
