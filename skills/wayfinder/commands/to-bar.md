# to-bar — emit the answer key

Turn the finished map into `.wayfinder/<slug>/ANSWER-KEY.md`.

Don't interview here. Everything in this document was already decided; you're rewriting it into the form a reviewer can use.

## The one rule

**This is not a spec.** A spec tells someone what to build. An answer key tells someone how to know it came out wrong. They are different documents and the failure mode is drifting from the second into the first.

The test, applied to every single line before you write it:

> Could a stranger who has never seen this project **check** this against a finished thing, and get a yes or a no?

If the line describes what to build — "add a login page," "the schema stores a plan tier," "as a customer I want to see my balance" — it has drifted. Cut it or rewrite it into something checkable.

**The file contains exactly five sections: `How to use this document`, `Destination`, `The bar`, `Out of scope`, `Unknown`.** That list is closed. Anything you're tempted to add as helpful context is build-instruction, and it gives a reviewer something to nod along to instead of something to check.

## The format

````markdown
# ANSWER KEY — <thing>

## How to use this document

You are judging finished work against this standard. Read these rules before you judge anything.

1. Judge **only** the checks in "The bar" below. Do not judge anything else, however obviously good or bad it looks.
2. Every check is **binary** — it passes or it fails. Never give a score, a rating, or a percentage. There is no partial credit.
3. Do not invent a standard. If something matters and isn't on this list, that is deliberate — it is either out of scope or undecided, both of which are listed below.
4. **Items under "Unknown" may not be judged.** They are numbered `U1`, `U2`, and so on. If the work touches one, report `U<number>: CANNOT JUDGE` and stop on that item. Do not guess, do not infer what was probably intended, do not pass it because it looks reasonable. Reporting that you cannot judge something is a correct and expected outcome, not a failure.
5. Items under "Out of scope" must not be rewarded. Work that adds them is **worse**, not better, no matter how impressive it looks.
6. If a check looks arbitrary, open `MAP.md` in this same folder. It holds the reasoning behind every check, linked from the last column. Read the reasoning before deciding a check is wrong.
7. An `A/B pick` row is judged on the property the check names, and on nothing else. If a person is available, they should see both artifacts unlabelled and pick one; judging it yourself, compare on the named property only.
8. Verdicts refer to this file's numbering. If this answer key is re-emitted, every earlier verdict is void — grade again from the top.
9. If you built any of this work yourself, stop and say so. Judging your own output is not judging.

### Report your verdict exactly like this

One line per bar check, in order, then one line for each Unknown item the work touched. Nothing else:

```
1: PASS
2: FAIL — <what was wrong, in one line>
3: PASS
U2: CANNOT JUDGE
```

`PASS`, `FAIL` and `CANNOT JUDGE` are the only three verdicts. Bar checks are numbered plain (`1`, `2`); Unknown items carry their `U` (`U1`, `U2`). A bar check is never `CANNOT JUDGE` — every one of them was written to be gradeable, so if you can't grade one, say which and why in a `FAIL` line rather than inventing a verdict.

Then one final line:

```
RESULT: PASS                  — every bar check passed and no Unknown was touched
RESULT: FAIL                  — any bar check failed
RESULT: BLOCKED — U2, U5      — no bar check failed, but the work touched these Unknowns
```

`BLOCKED` means the work cannot be signed off until a person decides the listed items. It is **not** a failure of the work, and it is **not** something you can resolve by looking harder — looking harder is exactly what produces an invented answer. If you are running in a loop, `BLOCKED` ends the loop and hands back to a human; it does not mean try again.

## Destination

<one or two lines: what done looks like>

## The bar

| # | check | judged by | reference | from decision |
|---|-------|-----------|-----------|---------------|
| 1 | <what must be true, stated so it can be checked> | run it | — | [<question>](MAP.md#<anchor>) |
| 2 | <what must be true> | A/B pick | <named, fetchable thing> | [<question>](MAP.md#<anchor>) |

## Out of scope

Adding any of these makes the result **worse**. Do not reward them.

1. <thing> — <why it's out>

## Unknown

**These are not gradeable.** Nobody has decided them yet. If the work touches one, report `U<number>: CANNOT JUDGE` and stop on that item.

- **U1** — <the undecided question, stated plainly>
- **U2** — <the undecided question, stated plainly>
````

## Filling in the columns

**check** — one thing that must be true, phrased so someone can verify it without asking a follow-up question. Take it from the decision's **Check** line in the map. A decision whose check is `unknown` produces no bar row — it becomes a `U` item. A decision that produced two checks is two rows.

`../CHECKS.md` is the single source for what a legal check looks like — the observable-outcome test, numbers, one-thing-per-row, and legal references. Grade every row against it as you write.

Two things this file adds, because the reader here is a stranger in a fresh session who re-reads the document on every round of a loop:

- **Keep each row to one line.** Length is a running cost and long rows get skimmed.
- **`judged by` is exactly `run it` or `A/B pick`.** Nothing else reaches the bar. If a check fits neither, leave it off and say which one you dropped and why.

**reference** — `—` for every `run it` row, always. For `A/B pick`, the artifact named in the decision, which `../CHECKS.md` requires to open without a build step.

**from decision** — a link back to that decision's section in `MAP.md`. This is the part people skip and it does real work: a reviewer that can read *why* a decision was made judges better than one reading a one-line summary. When a check looks arbitrary, the link is what explains it.

## Unknown is the most important section

Everything else on the page has an equivalent somewhere. This doesn't.

It's a **pre-registered, enumerated list of what nobody has decided**, written before any judging starts. A reviewer with no such list, handed something it can't properly assess, will assess it anyway — that's the whole problem. This makes not-judging an available, legitimate, named outcome.

Fill it from two places:

- **Not yet specified** in the map — fog that never cleared.
- Any decision whose **Judged by** is `unknown`.

Number them `U1`, `U2`, … — the `U` prefix keeps them from colliding with the bar's numbering when a verdict names one. State each as a plain question, and don't soften them into things that sound decided. "How aggressively to retry failed payments" is right. "Retry behaviour to be refined" is not — it reads like a plan and a reviewer will grade it.

**An empty Unknown section is a warning sign.** It usually means the interview stopped early or the fog got quietly filled in with plausible answers. Say so rather than shipping a document that claims certainty nobody has.

## Before you write the file

Check each of these, and report anything that fails rather than fixing it silently:

- Every `judged by` is `run it` or `A/B pick`. No exceptions.
- Every row passes `../CHECKS.md`: observable outcome, numbers where numbers exist, no "and", legal reference.
- Every `run it` has `—` in the reference column.
- Every `A/B pick` check names the property being compared.
- Every row links back to a decision.
- Every row is one line. This file is re-read on every round of the loop.
- Unknown items are numbered `U1`, `U2`, … so a verdict can name one without colliding with a bar number.
- Nothing on the bar describes what to build rather than how to check it.
- Out of scope and Unknown both hold something. If either is empty, **say so out loud rather than filling it** — an invented boundary and an invented certainty are both worse than a stated gap.

Then write the file and stop. Building is a separate session.
