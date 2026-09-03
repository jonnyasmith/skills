---
name: wayfinder
description: Decide what you're building, and write the standard for judging it.
disable-model-invocation: true
---

An idea has arrived, and the way from here to the finished thing isn't visible yet. This skill finds that way by naming where you're going, laying out the questions standing between here and there, and working them one at a time.

The output is **not a plan for building**. It's an **answer key** — a written standard for judging whether the finished thing came out right, including an honest list of what nobody has decided yet.

That distinction is the whole point. A plan says what to build. An answer key says how you'd know it came out wrong. If a reviewer — human or agent — is handed a plan and asked "is this good?", it has nothing to check against, so it invents a standard and approves whatever it sees. The answer key exists so nobody has to invent one.

## Plan, don't do

This skill **decides**. It does not build. Every question resolves into a decision plus a check, and the work is finished when nothing is left to decide before someone goes and builds the thing.

The pull to just start building is the signal you've reached the edge of the map and it's time to stop and hand off. **This is absolute — there is no note, instruction, or exception that turns this into an execution skill.** If the user wants it built, that's a separate session, after the answer key exists.

## The file

Everything lives in **one markdown file**: `.wayfinder/<slug>/MAP.md`. No issue tracker, no ticket files, no dependency graph — one person, one sitting, one effort.

The **slug** names the thing, not the sentence: two to four words, kebab-cased — `annual-billing-upgrade`, `crash-triage-tui`. Say it once when you first write the file so the user can rename it; after that it's fixed, because it's how a later sitting finds this map again.

```markdown
# MAP — <thing>

## Destination

<one or two lines: what reaching the end looks like>

## Open questions

<!-- ordered. This list is the running order — re-sort it when new questions arrive. -->

1. [ ] <question> — grilling
2. [ ] <question> — research
3. [ ] <question> — prototype

## Not yet specified

<!-- the fog: in-scope, but you can't phrase the question sharply yet -->

## Out of scope

<!-- ruled beyond the destination. Adding these makes the result worse. -->

## Answers

<!-- the detail. One section per answered question: the answer, the reasoning, and the check. -->

### <question>

**Answer:** <what was decided>

**Why:** <the reasoning — this is the primary source a reviewer reads when the summary isn't enough>

**Source:** <citation for every outside fact this rests on — url, file path, spec section — or "—">

**Check:** <how you'd know if this came out wrong — or `unknown: <why nobody can judge this yet>`>
**Judged by:** run it | A/B pick | unknown
**Reference:** <a named, fetchable thing — or "—">
```

## Running order, not blocking

The **Open questions** list is ordered, and its order is the running order. Take the top one. When new questions arrive — and they will — put them where they belong in the list rather than appending them to the end. There are no blocking edges to wire; the list position says everything a dependency graph would.

Grilling works a **frontier** inside a single conversation (`commands/grill.md`) — that tree is round-local and never gets written down. The map itself stays flat.

## The three question types

- **grilling** — the default. A question that can be settled by talking it through with the user. Use `commands/grill.md`. The user answers; you never answer for them.
- **research** — a fact outside this project is blocking a decision. You go and find out; the user isn't involved. Dispatch a background agent so the interview keeps moving, and point it at primary sources — the actual documentation, spec, or code — with a citation for every claim. Those citations land in the answer's **Source** line. Run these in parallel; they're the one question type that doesn't wait its turn.

  Two things follow. **A found fact usually makes a `run it` check**, because the fact is the check — that's most of why this type exists. And **if the research doesn't settle it** ("the docs don't say," "it depends how you configure it"), don't decide for the user: convert it into a grilling question and put it in the running order. If the honest finding is "you'd only know by running it," that's an unknown.
- **prototype** — "how should this look" or "how should this behave," which talking cannot settle. Use `commands/prototype.md`. Build something rough, react to it together. **The rough thing then becomes the reference** in the answer key — which is how you get a fetchable standard for something that has no famous example to point at.

## Every answer produces a check

This is the one thing that makes the output an answer key instead of notes.

After the user settles a question, ask one more: **"How would you know if this came out wrong?"**

The answer to *that* becomes the decision's **Check**, and at emit time it becomes one row on the bar. It takes one of exactly three forms — `run it`, `A/B pick`, or `unknown`.

**`CHECKS.md` is the single source for what each form requires: the wording ladder that turns a vague answer into a usable one, what makes a reference legal, and why a score is never an option. Read it before writing any check.**

## Fog — "Not yet specified"

The map is **deliberately incomplete**. Don't chart what you can't yet see.

Beyond the questions you've written down sit the ones you can tell are coming but can't yet pin down, because they hang on answers you don't have. That's the fog, and it goes in **Not yet specified**.

**Fog or question?** The test is whether you can state it precisely *now* — **not** whether you can answer it now.

- **A question when** you can phrase it sharply, even if you can't answer it yet.
- **Not yet specified when** you can't phrase it that sharply. Don't pre-slice fog into question-sized pieces; one patch may become three questions, or none, once you get there.

Answering a question clears the fog ahead of it. Whatever became sharp gets promoted into the Open questions list, and disappears from **Not yet specified** — it lives in one place, never both.

Fog that never clears is not a failure. It goes into the answer key's **Unknown** section, which is the most valuable thing in the document: a reviewer that hits an undecided item reports *"can't judge this yet"* and stops, instead of guessing and passing.

## Out of scope

Fog only ever gathers **toward** the destination. Work beyond the destination isn't fog — it's out of scope, and it gets its own section.

This section does a job most planning documents have no way to do: it's the only place that can say **adding this makes the result worse**. A reviewer told to beat a standard will try to win by adding things. Out of scope is what stops that.

Out-of-scope items never get promoted. If a question already on the list turns out to sit past the destination, strike it from Open questions and leave one line here — the gist plus why it's out — rather than answering it. It never gets an entry in **Answers**; a scope boundary isn't a step on the route.

## How to run it

### 1. Resume or chart

**First action, every invocation: glob `.wayfinder/*/MAP.md`.** A map whose destination covers the idea in front of you is the map you're working — read it, say in one line where you're resuming (top open question, or ready to emit), and go to stage 2. Chart only when nothing there fits.

To chart:

1. **Name the destination.** Grill until it's one or two lines, then ask what's out of bounds. Seeds Destination and Out of scope.
2. **Grill again, breadth-first.** Sharp questions go to **Open questions**, in running order. Everything you can't phrase sharply goes to **Not yet specified**.
3. **If Not yet specified is empty, stop here.** Tell the user the effort is small enough to just do, and don't write a map.
4. **Write `MAP.md`**, naming the slug you chose. Answers empty.
5. **Start every research question now**, in the background.

Use `commands/grill.md` for steps 1 and 2.

### 2. Work the questions

Repeat until **Open questions** is empty. Several per sitting is expected.

1. **Take the top question.**
2. **Resolve it** — grilling with `commands/grill.md`, prototype with `commands/prototype.md`, research with a background agent.
3. **Ask "how would you know if this came out wrong?"** Settle the check, its judged-by, and its reference against `CHECKS.md`. A question isn't resolved until this exists — and `unknown` is a legitimate resolution.
4. **Write the answer, the why, the source and the check into `Answers`.** Tick the question off.
5. **Update the map.** Promote newly-sharp fog into running order and clear it from Not yet specified; move anything past the destination to Out of scope; rewrite or strike any question this answer invalidated.

### 3. Emit

When **Open questions** is empty, or the user calls it: run `commands/to-bar.md` to write `.wayfinder/<slug>/ANSWER-KEY.md`.

Then **stop**. Building is a separate session.

## Talking to the user

The person running this thinks in outcomes, not files. Ask about what the thing should do and how they'd know it was wrong. Don't narrate file paths, line counts, or mechanisms at them — write the files quietly and talk about the decisions.

## Don't fabricate

If something can only be settled by actually running it, mark it and move on. An invented answer in the map becomes an invented standard in the answer key, which is the exact failure this skill exists to prevent.
