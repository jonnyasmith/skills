# grill — the interview

Interview the user relentlessly until you reach a shared understanding. This is where the answer key actually comes from: the checks aren't generated at the end, they're extracted here, one at a time, while the decision is still fresh.

**The decisions are the user's. Never answer for them.** An interview where you supply both sides has produced nothing — it's your opinion with extra steps, and it will read as a standard on camera while being a guess underneath.

## The design tree

Map the space as a **design tree**: every decision branches into the decisions that hang off it. The tree lives in this conversation only — it never gets written to the map, which stays a flat running order.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — the questions you can ask *now* without guessing at answers you haven't heard yet. Ask the whole frontier in one round, then wait.

A question whose answer depends on another question still open in this round belongs to a *later* round, not this one.

Format each question like this:

```
❓ **Q1** — **<short title>**: <the question, in plain language. Offer concrete options where there are some.>

➡️ <your recommended answer, and one line on why>
```

Always give a recommendation. A question with no recommendation makes the user do all the work, and the point is to make deciding fast, not to hand them a blank form.

Each round of answers reshapes the tree — settled decisions push the frontier outward. Recompute and ask the next round.

## Finding facts is your job, never the user's

When a question needs a fact — how something currently behaves, what a service actually charges, what's already in the project — go and get it. Dispatch a background agent against primary sources rather than asking the user something you could look up. Keep the citation; it goes in the answer's **Source** line.

Don't block on it. A running lookup is an unsettled prerequisite, so only the questions downstream of it wait. Ask the rest of the frontier now.

## The follow-up that matters

After the user settles a question, ask one more thing before moving on:

> **"How would you know if this came out wrong?"**

This is not optional and it is not a formality. It's the entire difference between notes and an answer key.

Push until the answer is something a stranger could act on, then record it in the legal form. **`../CHECKS.md` holds the three forms, the ladder for sharpening a vague answer, and what makes a reference legal** — work the answer against it before you write it down.

Two things worth knowing while you're still in the conversation:

- The push is the job. "The billing should work properly" is a topic, not a check, and accepting it hands the reviewer an invented standard.
- "You'd only know by running it with real users" is an honest, legal outcome — record it as an unknown rather than manufacturing something gradeable.

## Two modes

**Naming the destination** (first thing, before any question exists). Narrow until you have one or two sentences describing what done looks like. Then ask the scope question explicitly: *"What would you consider out of bounds here — things that would make this worse if someone added them?"* Those seed **Out of scope**, and they're the only defence against a reviewer that tries to win by piling on features.

**Charting breadth-first** (right after). Fan out across the *whole* space rather than going deep on any one thread. You're looking for the shape of what's unknown, not answers yet. Two things come out:

- questions you can phrase sharply now → **Open questions**
- things you can tell are coming but can't phrase sharply → **Not yet specified**

**If nothing lands in the fog, stop.** Tell the user the effort is small enough to just do, and don't write a map. Manufacturing questions to look thorough produces a padded answer key, and a padded answer key is worse than none — it looks like a standard while being filler.

## Done

A round is done when the user has answered and every answer has a check. The whole interview is done when the frontier is empty: every branch visited, nothing silently assumed.

Writing `MAP.md` is part of the interview, not action on it — keep it current as answers land. What waits for the user's confirmation is everything downstream: emitting the answer key, and any building at all.
