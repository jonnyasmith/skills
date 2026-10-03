---
name: build-change
description: "Build a change from its plan.html as an orchestrator only: a Workflow runs each plan step through fresh implementer, adversarial critic and fixer agents until the critic finds nothing left, behind a commit hook that blocks any commit while the checks fail."
disable-model-invocation: true
argument-hint: "<change slug>"
---

You are the **orchestrator only**. You prepare the run, start the workflow, and report what it did. You never edit code, read code diffs or judge the work yourself (the one diff you read is of the change's docs, after the run): every piece of that is a fresh agent inside the `build-change-run` workflow (`~/.claude/workflows/build-change-run.js`), and the loop, round limits and what each agent is told are fixed in that script.

## Before the run

1. **Find the change.** Read `changes/<slug>/plan.html` and `changes/<slug>/spec.html`. With no plan, stop and tell the user to run plan mode and `/to-plan` first. From the plan's **Order of work**, list the steps as `{id, title}` in order, using the plan's own numbering and wording.

2. **Find the check.** Take the commands that build, lint, type-check and test the project from CLAUDE.md and join them into one command that exits non-zero on failure (`npm run lint && npm test`, or a `scripts/check` the repo already has). If CLAUDE.md names none, ask the user once; a run without a check has no floor under the critic.

3. **Install the commit gate.** [check-gate.py](check-gate.py) is a PreToolUse hook: it runs the check before every `git commit` (including `cd <dir> && git commit` and `git -C <dir> commit`) and blocks the commit while it fails, blocks `--no-verify`, and blocks Edit/Write to itself and to `.claude/settings*.json`. It also blocks a commit that follows, in the same Bash call, any command other than `cd`, `pushd` or a git command that leaves the working tree alone: the hook runs before the whole call, so in `sed -i … && git commit` the check would not see the edit. An agent must commit in its own Bash call. It fires for subagents and workflow agents too, so no agent in the run can commit failing work.
   - If the repo's `.claude/hooks/check-gate.py` differs from the skill's `check-gate.py` (`cmp` the two), copy the skill's over it with `cp` (the gate blocks Edit/Write to it) and commit it. The hook file is read on every call, so this needs no `/hooks` approval.
   - If the repo's `.claude/settings.json` already registers `check-gate.py` with this check, skip to the probe.
   - Otherwise copy `check-gate.py` to `.claude/hooks/check-gate.py`, and add to the `PreToolUse` array of `.claude/settings.json` (merging with what is there):
     ```json
     { "matcher": "Bash|Edit|Write|MultiEdit",
       "hooks": [{ "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/check-gate.py\" '<check>'" }] }
     ```
     Commit both. A session loads hooks when it starts, so ask the user to run `/hooks` and approve the new entry.
   - **Probe it:** run `git commit --no-verify --dry-run`. The hook must block it with a `check-gate:` message. If git runs instead, the hook is not loaded: stop and tell the user.

4. **Prepare the branch.** The working tree must be clean (`git status --porcelain` prints nothing); if it is not, stop and ask the user. Switch to `feat/<slug>`, creating it if needed, and record `git rev-parse HEAD` as the base.

5. **Show the user the run** in a few lines: the steps, the check, the branch, and that each step gets up to 4 review rounds before the run halts. Start it when they confirm.

## The run

Call the Workflow tool with `name: "build-change-run"` and these `args`:

```json
{
  "repo": "<absolute path of the repository>",
  "slug": "<slug>",
  "base": "<base sha>",
  "steps": [{ "id": "1", "title": "..." }],
  "check": "<the check command>",
  "maxRounds": 4
}
```

Two optional args are used only to relaunch after a halt (see After the run): `docs`, the commit whose spec.html and plan.html are the standard (default `base`), and `stepBase`, the commit the first listed step starts from (default `base`).

If the tool reports that `build-change-run` is not found, read `~/.claude/workflows/build-change-run.js` in full and pass its exact contents as `script` with the same `args`. (A `scriptPath` outside the working directory is refused.)

For each step, the workflow runs:

```
implementer ─► critic ─► (clean) adversary ─► (clean) next step
  tests first     └─ findings ─┐     └─ findings ─┐
                               └──► fixer ◄───────┘   max 4 rounds, then halt
                                      │
                                      ├─► next round's critic verifies these fixes
                                      └─► escalated ─► halt for the user

any decision finding ─► halt for the user
every commit ─► check-gate hook runs the check ─► blocked while it fails
```

The critic's standard is spec.html and plan.html **as of the `docs` commit**, read with `git show`, so an agent's edit to plan.html during the run never becomes a requirement. Agents may not edit spec.html, and in plan.html they may only add to a Departures section.

A finding is **substantive** only if it breaks a requirement, a Proof item or a CLAUDE.md code rule and the spec settles the correct behaviour. When the code breaks one but more than one fix fits the spec, the finding is a **decision**, with its options listed. The run halts on it; no agent chooses. The fixer can also **escalate** a finding it cannot fix without choosing behaviour the spec leaves open, which halts the run the same way. Behaviour the spec never defines, where the code breaks nothing, is a **spec gap**: it is collected for the user and never sent to the fixer. From round 2, the critic checks the last round's fixes and the fixer's diff rather than reviewing the whole step again.

When every step passes, a final critic and adversary review the whole change against every requirement in spec.html and every Proof item in plan.html, with the same fixer loop.

If the run is interrupted, relaunch it with the `scriptPath` the first call returned, the same `args`, and `resumeFromRunId`; finished agents return their cached results.

## After the run

1. **Confirm the check yourself.** Run the check command once and show the user the output. The workflow's word is not the definition of done; the output is.

2. **Report**, per step: its outcome, rounds used, substantive and cosmetic findings, and any finding the fixer declined with its reason. Name every departure from the plan: those the agents returned, and every change `git diff <base>..HEAD -- changes/<slug>/` shows. The diff is the record; an agent's silence is not. A change to spec.html, or to plan.html outside its Departures section, broke the rules: name it first. A run of empty reviews is a question about the critic, not a clean bill of health; say so if every step passed in round 1.

   Then list the **spec gaps**, grouped and deduplicated, as questions for the user: each is a case the spec leaves undefined. The answer belongs in spec.html, and a later run builds it.

3. **If the run halted on a decision**, give the step, each decision with its options and who raised it, and any unreviewed fixes the fixer committed in that round. Ask the user to choose; the answer goes in spec.html (or plan.html's Proof), committed by the user or by you at their instruction. Then launch a **new** run (not a resume) with the same `base`, `docs` set to the commit holding the answer, `stepBase` set to the halted step's `from`, and `steps` from the halted step on. The final review still covers the whole change from `base`.

   **If it halted for any other reason**, give the step, the reason and the last findings, and stop. A step that is still failing after its rounds usually means the plan step is too big or the design is wrong. Splitting the step or rethinking the design is the user's call.

4. **Lessons.** List the lessons the fixers returned. When a lesson repeats a mistake already seen (twice in this run, or already corrected once before), propose adding it to CLAUDE.md, so later work avoids it. Add it only when the user agrees.

5. **Hand it to the user to try.** The change is on `feat/<slug>`, committed step by step. Do not merge or push; the user decides after trying it.
