---
name: to-plan
description: "Turn the plan approved in plan mode into plan.html for its change: no interview, just synthesis."
disable-model-invocation: true
---

This skill takes the implementation plan the user approved in plan mode and writes it up as `plan.html`, next to the intent and spec it came from. Do NOT interview the user or re-plan; synthesize the approved plan. If the conversation holds no approved plan, say so and stop: the plan is made in plan mode, not here.

Read [../sdlc/ARTIFACTS.md](../sdlc/ARTIFACTS.md) before writing. It sets where the file goes, its format, and how to use diagrams.

## Process

1. **Find the change.** Read `changes/<slug>/intent.html` and `changes/<slug>/spec.html` if they exist. If the user passed a plan file (plan mode saves one under `~/.claude/plans/`), read it; otherwise use the plan approved in the conversation.

2. **Write `changes/<slug>/plan.html`** with the sections below, in order. Set `<meta name="artifact" content="plan">`.

   The bar: an engineer who never saw the conversation could implement the change from this file alone. Unlike the spec, a plan names real file paths, because it is read now, against the current code.

3. **Check it against the bar.** Read the file back as that engineer would. Every file the plan touches is listed, every step says what it changes, and every risk names what would go wrong. Fix any gap from the approved plan; if the approved plan itself has the gap, list it for the user rather than inventing an answer.

4. **Commit it**, per ARTIFACTS.md. Tell the user the next step: implement, or `/to-tickets` if the work is too big for one session.

<plan-sections>

## Title

`Plan: <the change>`, with links to `intent.html` and `spec.html` and the date each was committed.

## Files that change

Every file created, modified or deleted, each with one line on why.

## Order of work

Numbered steps, in the order they are done, each small enough to verify on its own.

## Risks

What could break, the riskiest step, and the options considered and rejected, with the reason.

## Proof

The tests and checks that show the change works, mapped to the proposed outcome in the intent.

</plan-sections>
