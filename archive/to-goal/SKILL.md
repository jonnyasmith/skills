---
name: to-goal
description: Turn a task with an existing verifier, or a task that builds its verifier, into a paste-ready Claude Code /goal prompt that runs a verification loop — the session orchestrates, fans out to an implementer subagent, runs the verifier itself, and sends green work to a fresh adversarial reviewer subagent. Use when the user wants a /goal, a verifier-first loop, or an implementer/reviewer loop for a plan, spec, stage or ticket.
argument-hint: "Which task, and what command proves it is done?"
disable-model-invocation: true
---

# Goal Prompt

The user names a task. You return **one fenced block per goal** holding a `/goal`
command. They paste it into a fresh Claude Code session, in auto mode. Goal generation produces text only, unless the user also asks for file changes.

**The loop lives in the prompt.** Do not create agent definition files, loop documents,
scripts or any other files unless the user asks for them. "Fan out to an implementer
subagent" and "spawn a fresh adversarial reviewer subagent" are enough; the session
creates general-purpose subagents from that text.

## Facts the prompt must respect

- After each turn a small model judges the condition. It reads **only the
  conversation**. It cannot run commands or open files. A done clause therefore names a
  command and the output it must print, and requires that the orchestrator runs it
  **itself** after the last change. A subagent's claim that something passed is not
  evidence.
- One goal per session. The condition may be up to **4,000 characters**.
- While a subagent or background command is still running, the check is skipped.
- The goal ends when the judge says met or impossible, or on an error the user must
  fix. It also stops if turns make no progress. `/goal` shows status and `/goal clear`
  stops it.
- `/goal` does not change the permission mode. Unattended runs need auto mode.

## 1. Gather the inputs

Take them from the plan, spec or ticket the user points at. Ask one round of short
questions only for what you cannot find, and state the defaults you assume.

| Input | What you need |
| --- | --- |
| Task source | The file and section that define the work. The prompt points at it; it does not copy it |
| Verifier | Select existing-verifier or verifier-building mode. Name the command, exact success output and final mode. For a verifier being built, identify it as proposed and define its acceptance contract and required negative controls first. |
| Worker bounds | What the implementer may write and what is locked. In verifier-building mode, tests/verifier code are in scope; the approved criteria, required scenario coverage and success contract remain locked. |
| Reviewer view | What the reviewer is given. In pass 1: criteria, locked tests, diff. Never the builder's notes or summaries |
| Attack list | Five to ten domain-specific ways the work could pass the verifier without meeting the criteria |
| Human channel | Where the worker records a spec problem instead of working round it (a questions file or change requests), and what "blocked" means |
| Caps | Review rounds (default 3) and turns (roughly 20 for a spec, 60 for tests or infrastructure, 80 for a build) |
| Impossible | Environment failures that no amount of work fixes: a missing service, failed authentication, a held port |

### Select the verification mode

**Existing verifier:** use the established command throughout the loop. Identify which
tests and verifier paths are locked, and do not let the worker weaken them.

**Verifier being built:** use this mode when the requested work includes a test suite,
harness, verifier, or its required setup. Do not reject the goal merely because its
final command does not exist yet. Generate a prompt with a bootstrap phase followed
by the implementation/verification loop, within the same goal when they share one
acceptance contract.

Before implementation, define the proposed final command, exact success output,
required scenarios and evidence. Label the command as not yet implemented. Take the
contract from the supplied requirements; clarify only material gaps. The worker may
build the tests/verifier, but may not remove required coverage or redefine success.
Before the final command exists, the orchestrator runs available baseline checks and
reports bootstrap progress; missing commands are not passing results.

Before trusting a green result, require the orchestrator to run negative controls:
deliberately introduce representative failures in isolated disposable state and prove
the verifier exits non-zero and identifies the failed criterion. Cover skipped or
missing required stages, failure propagation and fabricated/stale evidence where
relevant. Then restore valid state and run the full final verifier after the last
change. A printed success marker alone is insufficient; it must be derived from
executed assertions and fresh evidence. Changes to the verifier invalidate prior
integrity results and require relevant negative controls to run again.

If neither a runnable verifier nor a concrete, runnable acceptance contract can be
defined from the task, explain the missing information and ask one concise question.
Do not invent a verifier, claim a proposed command already exists, or substitute an
unrelated passing baseline for the requested proof.

## 2. Fill the template

Keep this order. Leave out a line the task does not need. In verifier-building mode,
insert the bootstrap phase before the normal loop: build the proposed verifier to the
locked contract, run available baseline checks, then demonstrate its negative controls.
Replace locked-verifier worker bounds with explicit permission to implement verifier
code while keeping criteria and required coverage locked. The final done clause must
include the integrity command and its success output as well as full acceptance.
Do not force separate goals or a human approval between these phases unless the user
asks or the requirements need a decision.

```text
/goal <Task in one line> as <source file and sections> describes. Act as the orchestrator: fan the work out to subagents and keep this context for coordination. <Where the requirements are read, e.g. "the spec only at SPEC_BASE">.
Loop: (1) An implementer subagent <does one part at a time / the work>, <writes only X; never touches Y>, <records problems in the human channel instead of reinterpreting>, commits, and replies in under 300 words. (2) Run `<verifier, iterating mode>` yourself after each implementer turn and send the implementer only <the first 20 failures>. Keep a change if the score holds or rises; otherwise revert to the best commit and say why. <Stop at once if an integrity check fails.> (3) When `<verifier, final mode>` passes, spawn a fresh adversarial reviewer subagent. It has not seen the implementation reasoning, gets only <reviewer view>, and must not edit files. Its job is to argue that the work passes the check without meeting <the criteria>: <attack list>. It flags only correctness and requirement gaps. (4) <Optional pass 2: give the same reviewer <the notes and change requests> and have it keep or withdraw each finding, listing withdrawn ones separately.> Write each review to <path>. (5) Send kept findings to an implementer, verify again, then review again. At most <N> review rounds.
Done when this session shows, after the last change: your own `<verifier, final mode>` printing <exact output>; the last review with no kept findings, or <N> rounds done with them listed; `git status --porcelain` printing nothing <in each repository>. Also done, as blocked, when every remaining failure has an open <question or change request>: list them and say "blocked". Never <hard constraints: push, change permissions, edit locked paths, weaken an assertion>. Stop after <T> turns and report progress. Impossible if <environment failures>.
```

## 3. Choose the reviewer

- **Build or code change:** the reviewer gets the criteria at the approved version, the
  locked tests and the diff. It tries to show the work passes without meeting the spec.
- **Tests or acceptance criteria:** the reviewer gets the spec and the tests. It tries
  to show a case could pass without its criterion being met. Look for: values copied from
  output instead of computed; an "expect nothing" check with no reason; untested edge
  cases the spec names.
- **Verifier or harness:** the fresh reviewer gets the approved criteria, verifier/tests,
  diff and commands, without builder notes. It tries to make the verifier pass despite
  missing or broken required behaviour. It may mutate only an isolated scratch clone
  or disposable fixture state, never the implementation checkout or approved criteria.
  It reports demonstrated holes and their reproduction commands. A fix requires the
  orchestrator to rerun relevant negative controls and final acceptance.
- **Spec or design:** the reviewer argues the document is ambiguous, incomplete or not
  testable. Its items go to the human and are **not** applied in the loop.

Use a second pass with context only when silent reinterpretation is a risk. Pass 1 must
finish before the reviewer sees any rationale.

## 4. Check before you hand it over

Check the finished block against every item. Fix it until all hold.

- [ ] Under 4,000 characters. Count with `wc -m`, not by estimate.
- [ ] Every done clause names a command and its expected output, run by the orchestrator
      after the last change. None depends on a subagent's word.
- [ ] The done clause uses the **final** verifier mode, not a fast or filtered one.
- [ ] Verifier-building goals label proposed commands, lock the acceptance contract,
      permit verifier implementation and include negative-control command/output.
- [ ] Bootstrap progress, verifier self-reports and unrelated baseline passes cannot
      satisfy the final done clause.
- [ ] The reviewer is fresh, cannot edit implementation/criteria, and gets no builder notes in pass 1; harness attacks are confined to scratch state.
- [ ] The attack list is specific to this task. A generic "check for bugs" fails this item.
- [ ] The reviewer flags only correctness and requirement gaps, so the loop does not
      over-engineer.
- [ ] Review rounds and turns are capped.
- [ ] The blocked and impossible clauses are there, or were left out for a stated reason.
- [ ] Hard constraints are stated once, as "Never …".
- [ ] The prompt asks for no new files beyond the work itself and the review record.

## 5. Output

For each goal, give one line naming it, the setup the user runs first (for example, installing hooks or stopping a stack), then the fenced `/goal` block and its character count. Add nothing else unless the user asks.
When there are several stages, write one goal per stage, in order. Name the human gate
between each one.
