# checks — the two forms of judgment

Every answered question carries exactly one check, and every check takes one of two forms. This file is the single source for what is legal; `SKILL.md`, `commands/grill.md` and `commands/to-bar.md` all defer to it.

| Judged by | Use it when | What the reviewer does | Reference |
|---|---|---|---|
| **run it** | There's a right answer | Runs the thing and checks the outcome | always `—` |
| **A/B pick** | It's a matter of taste or feel | Puts it side by side with the reference and picks one | required |
| **unknown** | Nobody has decided it yet | Nothing — reports `CANNOT JUDGE` | always `—` |

**Never a score.** Not "rate the checkout 1–10," not "assess whether it feels premium." Every check is binary — it passed or it didn't. Wanting a third grade means the check isn't specific enough yet; push it back into the conversation rather than softening the judgment.

## run it

Name the observable outcome, not the topic. Whoever grades this is a stranger in a fresh session with no access to the conversation, so a check that names a subject area makes them invent a procedure — the same invented-standard failure one level down.

The test: **would two different people, given only this line, test it the same way and agree on the result?**

Put a number in it wherever a number exists — amounts, counts, timings, limits. A number is the cheapest way to make a check unarguable.

The ladder, pushing one answer from useless to usable:

- **Too vague:** "the billing should work properly"
- **Still too vague:** "upgrades should charge the right amount"
- **Usable:** "upgrading to annual on day 10 of a 30-day month charges the annual price minus two-thirds of the monthly price already paid"

One thing per check. A check containing "and" can half-pass, and half-pass is the grade this document bans.

## A/B pick

Needs a **named, fetchable** reference: a specific page, product, or artifact someone can actually open. Never a category — "a modern dashboard" is an invitation to invent a standard with extra confidence.

The reference must open **without a build step**: a live URL, a single self-contained file, or a screenshot. Anything needing a server, a database, or the right branch checked out is a dead link by the time someone grades the work. A prototype qualifies only in the form `commands/prototype.md` parks it.

The check line names the property being compared — "reads as trustworthy at a glance," "the empty state explains itself." The reviewer compares on that property alone. A person doing the comparison should see both artifacts unlabelled, which is the stronger form; an agent reading the answer key cannot be blind, so the named property is what keeps the judgment honest.

## Reference beats no reference only when there's no right answer

A right answer beats an example. Reach for `A/B pick` only when nothing observable settles it.

## unknown

If the honest answer is "you'd only know by running it with real users," that's not a check — it's an unknown. Record the decision, write `**Check:** unknown: <why nobody can judge this yet>`, and set `**Judged by:** unknown`.

Unknowns go to the answer key's `Unknown` section, where not-judging is a legitimate named outcome. An invented check here becomes an invented standard there, which is the failure this whole skill exists to prevent.
