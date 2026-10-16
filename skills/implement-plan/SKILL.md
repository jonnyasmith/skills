---
name: implement-plan
description: Implement a plan published as a claude.ai Artifact end to end with multi-agent workflows - build it, have fresh agents adversarially review it, fix and re-review in bounded rounds, verify by running things, then commit, open a PR and report. Use when the user passes a plan Artifact URL and asks to implement or build it.
disable-model-invocation: true
argument-hint: <plan artifact URL>
---

# Implement a plan

Implement the plan at `$ARGUMENTS`. If no URL was given, ask for it.

This skill opts in to multi-agent orchestration: use the Workflow tool, as if the user had typed "ultracode".

Read the plan in full first, with the Artifact tool's `read` action, including its acceptance criteria and constraints. Then design and run whatever workflows you judge best to deliver it: how to split the work, what runs in parallel, and how many review rounds it needs.

## Requirements

- Review as the Reviews section of /subagent-orchestration says: acceptance criteria and failing checks written before the build by an agent other than the implementer, cold graders per lens that default to "not met", a refuter, a planted-defect calibration, and the script deciding what goes back for fixing. Grade correctness and the plan's acceptance criteria, not style.
- Fix every failed or unknown criterion and re-grade. Stop after 5 rounds, or after 2 rounds in a row with no progress, and report what is still unresolved instead of looping.
- Verify by running things, not by reading code: tests, build, lint, and the running app for UI changes. Show the evidence.
- Do not change anything outside the plan's scope.

## When done

Commit using Conventional Commits, open a PR, and give a short report covering:

- what was built
- what the reviewers found and how each finding was resolved
- the evidence it works
- anything unverified or left open
