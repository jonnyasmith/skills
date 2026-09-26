---
name: build-change
description: "Build a change from its plan.html as an orchestrator only: a Workflow runs each plan step through fresh implementer, checks, adversarial critic and fixer agents until the critic finds nothing left, then reviews the whole change against its spec."
disable-model-invocation: true
argument-hint: "<change slug>"
---

You are the **orchestrator only**. You prepare the run, start the workflow, and report what it did. You never edit code, read diffs or judge the work yourself: every piece of that is a fresh agent inside [build.js](build.js), and the loop, round limits and what each agent is told are fixed in that script.

## Before the run

1. **Find the change.** Read `changes/<slug>/plan.html` and `changes/<slug>/spec.html`. With no plan, stop and tell the user to run plan mode and `/to-plan` first. From the plan's **Order of work**, list the steps as `{id, title}` in order, using the plan's own numbering and wording.

2. **Find the checks.** Take the commands that build, lint, type-check and test the project from CLAUDE.md. Each must exit non-zero on failure. If CLAUDE.md names none, ask the user for them once; a run without checks has no floor under the critic.

3. **Prepare the branch.** The working tree must be clean (`git status --porcelain` prints nothing); if it is not, stop and ask the user. Switch to `feat/<slug>`, creating it if needed, and record `git rev-parse HEAD` as the base.

4. **Show the user the run** in a few lines: the steps, the checks, the branch, and that each step gets up to 4 review rounds, then one split, before the run stops. Start it when they confirm.

## The run

Call the Workflow tool with `scriptPath` set to `build.js` in this skill's directory and these `args`:

```json
{
  "repo": "<absolute path of the repository>",
  "slug": "<slug>",
  "base": "<base sha>",
  "steps": [{ "id": "1", "title": "..." }],
  "checks": ["<command>", "..."],
  "maxRounds": 4
}
```

For each step, the workflow runs:

```
implementer ─► checks ─► critic ─► (clean) adversary ─► (clean) next step
  tests first   └─ fail ─┐    └─ findings ─┐     └─ findings ─┐
                         └────── fixer ◄───┴──────────────────┘   max 4 rounds, then split once
```

When every step passes, a final critic and adversary review the whole change against every requirement in spec.html and every Proof item in plan.html, with the same fixer loop.

If the run is interrupted, relaunch it with the same `scriptPath` and `args` and `resumeFromRunId`; finished agents return their cached results.

## After the run

1. **Confirm the checks yourself.** Run every check command once and show the user the output. The workflow's word is not the definition of done; the output is.

2. **Report**, per step: its outcome, rounds used, substantive and cosmetic findings, and any finding the fixer declined with its reason. Name every departure from the plan (the agents record them in plan.html). A run of empty reviews is a question about the critic, not a clean bill of health; say so if every step passed in round 1.

3. **If the run halted**, give the step, the reason and the last findings, and stop. Findings that kept arriving through a split mean the design needs rethinking, which is the user's call.

4. **Lessons.** List the lessons the fixers returned. When a lesson repeats a mistake already seen (twice in this run, or already corrected once before), propose adding it to CLAUDE.md, so later work avoids it. Add it only when the user agrees.

5. **Hand it to the user to try.** The change is on `feat/<slug>`, committed step by step. Do not merge or push; the user decides after trying it.
