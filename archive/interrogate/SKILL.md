---
name: interrogate
description: Interrogate a design you already understand until every edge is decided, and write the standard for judging it.
disable-model-invocation: true
---

You know what you're building. The destination isn't in doubt — what's in doubt is the edges: the empty state, the limit, the second click, the thing two users do at once. This skill is one sitting of hard questions over that known ground, and it ends with a written standard for judging the result.

Same output as `survey`, same two files, same check rules. What differs is the front: no fog, no charting, no resume across sittings. **If the destination itself is unclear, or you can feel questions coming that you can't yet phrase, stop and use `survey` instead.** Interrogating fog produces confident answers to the wrong questions.

## Plan, don't do

This skill **decides**. It does not build. Every question resolves into a decision plus a check.

**This is absolute — there is no note, instruction, or exception that turns this into an execution skill.** If the user wants it built, that's a separate session, after the answer key exists. `to-gauntlet` turns the answer key into the prompt that runs it.

## The files

`.bar/<slug>/DECISIONS.md` while the questions are being worked, `.bar/<slug>/ANSWER-KEY.md` at the end. The slug names the thing, not the sentence: two to four words, kebab-cased — `annual-billing-upgrade`, `crash-triage-tui`. Say it once so the user can rename it.

`DECISIONS.md` takes the shape `../survey/SKILL.md` defines, with one difference: **no `Not yet specified` section.** There is no fog here, and an empty heading invites someone to fill it. Everything undecided leaves through a `Check:` of `unknown`.

## The sweep

The destination is given, so the questions don't come from charting — they come from walking the edges of what's already understood. Do this once, before asking anything, and put what you find in **Open questions** in the order you'd hit it while building.

Walk these, out loud, against the thing being built. Most yield nothing; the ones that do are the session.

- **Empty** — nothing there yet. First run, no data, no permission granted, list of zero.
- **One** — the degenerate case that looks like a list but isn't.
- **Many** — the number nobody planned for. Where does it get slow, paginate, or truncate?
- **Wrong** — bad input, malformed import, a value someone typed by hand.
- **Gone** — the thing was deleted, moved, or renamed while in use.
- **Twice** — the same action repeated, submitted twice, or run concurrently by two actors.
- **Interrupted** — closed tab, killed process, lost network, half-written state.
- **Time** — timezones, month ends, expiry, ordering by a clock somebody else controls.
- **Money and counting** — rounding, proration, currency, off-by-one on a boundary.
- **Who** — a second user, a different role, someone who shouldn't see it.
- **Undo** — how the user gets out of it, and what state that leaves.

Say plainly which of these you're skipping and why. A sweep that quietly drops half the list produces an answer key that looks complete.

**Don't pad.** If an edge genuinely doesn't apply, it isn't a question. A manufactured question becomes a manufactured check, and a padded answer key is worse than none.

## Run it

1. **Confirm the destination in one or two lines**, in the user's words, and ask what's out of bounds — *"things that would make this worse if someone added them."* Seeds **Destination** and **Out of scope**.
2. **Sweep**, as above. Write `DECISIONS.md` with the questions in running order and `Answers` empty.
3. **Work the top question** with `../survey/commands/interview.md`. Dispatch background research for any question that needs an outside fact; a taste question that talking can't settle goes to `../survey/commands/prototype.md`.
4. **Ask "how would you know if this came out wrong?"** Settle the check, its judged-by and its reference against `../survey/CHECKS.md`. A question isn't resolved until this exists — and `unknown` is a legitimate resolution.
5. **Write the answer, the why, the source and the check into `Answers`.** Tick the question off. Add any question the answer just exposed, in the right place in the running order.
6. **Repeat until Open questions is empty**, then run `../survey/commands/to-bar.md` to emit `ANSWER-KEY.md`.

Then **stop**.

## Talking to the user

The person running this thinks in outcomes, not files. Ask about what the thing should do and how they'd know it was wrong. Don't narrate file paths or mechanisms at them — write the files quietly and talk about the decisions.

## Don't fabricate

The decisions are the user's; never answer for them. If something can only be settled by actually running it, record it as an unknown and move on. An invented answer here becomes an invented standard in the answer key, which is the exact failure this pipeline exists to prevent.
