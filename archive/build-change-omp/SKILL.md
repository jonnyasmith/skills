---
name: build-change
description: "Build a change from its plan.html as an orchestrator only: an eval-cell workflow runs each plan step through fresh implementer, adversarial critic and fixer agents until the critic finds nothing left, behind a commit hook that blocks any commit while the checks fail."
disable-model-invocation: true
argument-hint: "<change slug>"
---

You are the **orchestrator only**. You prepare the run, start the workflow, and report what it did. You never edit code, read diffs or judge the work yourself: every piece of that is a fresh agent inside [build.js](build.js), and the loop, round limits and what each agent is told are fixed in that script.

## Before the run

1. **Find the change.** Read `changes/<slug>/plan.html` and `changes/<slug>/spec.html`. With no plan, stop and tell the user to run plan mode and `/to-plan` first. From the plan's **Order of work**, list the steps as `{id, title}` in order, using the plan's own numbering and wording.

2. **Find the check.** Take the commands that build, lint, type-check and test the project from AGENTS.md or CLAUDE.md and join them into one command that exits non-zero on failure (`npm run lint && npm test`, or a `scripts/check` the repo already has). If neither names any, ask the user once; a run without a check has no floor under the critic.

3. **Install the commit gate.** [check-gate.py](check-gate.py) runs the check before every `git commit` and blocks the commit while it fails, blocks `--no-verify`, and blocks edits to itself and to `.claude/settings*.json`. [check-gate.ts](check-gate.ts) is the omp hook that runs it on every `tool_call` (`bash`, `edit`, `write`) and also blocks edits to itself and to omp settings. Subagents keep the hooks their parent loaded, so no agent in the run can commit failing work.
   - If the repo's `.omp/hooks/pre/check-gate.ts` already exists with this check, skip to the probe.
   - Otherwise copy `check-gate.py` to `.omp/hooks/check-gate.py` and `check-gate.ts` to `.omp/hooks/pre/check-gate.ts`, and in the copy replace `"__CHECK__"` with the check as a JSON string literal. Only `.omp/hooks/pre/` and `.omp/hooks/post/` are scanned; a hook placed directly in `.omp/hooks/` does not load.
   - Commit both. omp loads hooks when a session starts, so this session does not have the gate yet. Ask the user to start a new omp session in the repo and run the skill again there.
   - **Probe it:** run `git commit --no-verify --dry-run`. The hook must block it with a `check-gate:` message. If git runs instead, the hook is not loaded: stop and tell the user.

4. **Prepare the branch.** The working tree must be clean (`git status --porcelain` prints nothing); if it is not, stop and ask the user. Switch to `feat/<slug>`, creating it if needed, and record `git rev-parse HEAD` as the base.

5. **Show the user the run** in a few lines: the steps, the check, the branch, and that each step gets up to 4 review rounds before the run halts. Start it when they confirm.

## The run

Run `build.js` from this skill's directory in one `eval` call with `language: "js"` and `timeout: 0`. Do not paste the script; the cell reads it and runs it as an async function body, with these `args`:

```js
const src = await Bun.file("<this skill's directory>/build.js").text()
const args = {
  "repo": "<absolute path of the repository>",
  "slug": "<slug>",
  "base": "<base sha>",
  "steps": [{ "id": "1", "title": "..." }],
  "check": "<the check command>",
  "maxRounds": 4
}
const AsyncFunction = (async () => {}).constructor
return await new AsyncFunction("args", "agent", "phase", "log", src)(args, agent, phase, log)
```

The cell returns the run's result object. Implementers and fixers run as the `builder` agent; critics and adversaries run as `task` agents, because the prompts in `build.js` define the review completely.

For each step, the workflow runs:

```
implementer ─► critic ─► (clean) adversary ─► (clean) next step
  tests first     └─ findings ─┐     └─ findings ─┐
                               └──► fixer ◄───────┘   max 4 rounds, then halt
                                      │
                                      └─► next round's critic verifies these fixes

every commit ─► check-gate hook runs the check ─► blocked while it fails
```

The critic's standard is the spec. A finding is substantive only if it breaks a requirement, a Proof item or a code rule in AGENTS.md or CLAUDE.md. Behaviour the spec never defines is a **spec gap**: it is collected for the user and never sent to the fixer, so the review cannot drift past the spec. From round 2, the critic checks the last round's fixes and the fixer's diff rather than reviewing the whole step again.

When every step passes, a final critic and adversary review the whole change against every requirement in spec.html and every Proof item in plan.html, with the same fixer loop.

If the run is interrupted, nothing is cached: finished steps survive only as commits. Read `git log <base>..HEAD`, drop the steps that already have a `feat(<slug>)` commit that passed review, and run the cell again with the remaining `steps`, the same `base`, and `"head": "<current HEAD sha>"`. If a step was left half-reviewed, include it again: its review starts from round 1.

## After the run

1. **Confirm the check yourself.** Run the check command once and show the user the output. The workflow's word is not the definition of done; the output is.

2. **Report**, per step: its outcome, rounds used, substantive and cosmetic findings, and any finding the fixer declined with its reason. Name every departure from the plan (the agents record them in plan.html). A run of empty reviews is a question about the critic, not a clean bill of health; say so if every step passed in round 1.

   Then list the **spec gaps**, grouped and deduplicated, as questions for the user: each is a case the spec leaves undefined. The answer belongs in spec.html, and a later run builds it.

3. **If the run halted**, give the step, the reason and the last findings, and stop. A step that is still failing after its rounds usually means the plan step is too big or the design is wrong. Splitting the step or rethinking the design is the user's call.

4. **Lessons.** List the lessons the fixers returned. When a lesson repeats a mistake already seen (twice in this run, or already corrected once before), propose adding it to AGENTS.md (or CLAUDE.md, if that is what the repo uses), so later work avoids it. Add it only when the user agrees.

5. **Hand it to the user to try.** The change is on `feat/<slug>`, committed step by step. Do not merge or push; the user decides after trying it.
