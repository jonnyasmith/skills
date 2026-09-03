---
name: to-gauntlet
description: Turn an answer key — or a rough goal — into one paste-ready prompt that runs a gauntlet loop in a fresh session.
argument-hint: "The answer key to run, or what you want built"
disable-model-invocation: true
---

You hand back **one prompt**, plus the lines that arm its driver. The user pastes it into a fresh session, and that session does the work.

**You are not running the loop.** A gauntlet loop gives a lead agent a goal and a real quality bar, lets it split the work, and puts every piece through a separate critic that compares the actual output against the bar. Your job is the bar, the brief, and the driver. Everything else is the receiving agent's decision — and its independence comes from starting blank, which is exactly what a fresh session gives it.

For that reason: **don't offer to run it here.** This session wrote the standard; judging work against a standard you authored is not judging.

## Two entries

### An answer key exists — the normal case

Glob `.bar/*/ANSWER-KEY.md`. If one covers the goal in front of you, **do not interview**. Everything but the constraints is already settled, and re-asking it invites answers that contradict the file:

- **Goal** ← its `Destination`, plus the features under the bar that make the artifact recognisably itself.
- **Bar** ← **the answer key is the instrument.** Name its absolute path in the brief and tell the critic to grade every row of `The bar` table, verdict by verdict, in the form the key's own `How to use this document` section sets out. Each `A/B pick` row also carries a `reference` — those are the external artifacts the critic opens.
- **Out of scope** ← its `Out of scope` list, verbatim. Adding these makes the result worse.
- **Stop condition** ← the key's `Unknown` section. `RESULT: BLOCKED` means a person has to decide something; the loop ends and hands back. Say that in the brief, or the driver will grind on an item nobody has decided.
- Ask the user for two things only: the **constraints** that are genuinely fixed (stack, hosting, data to import) and the **budget**.

Read `DECISIONS.md` beside it if a bar row looks arbitrary. Don't restate its reasoning in the brief — the critic follows the link when it needs it.

### Only a rough goal

Interview until you can name all four, using the round format in `../survey/commands/interview.md`:

**Goal** — the artifact, and what makes it worth building.
**Bar** — a real, inspectable thing a critic can hold the work against, side by side.
**Scope** — what is in, and what is explicitly out.
**Constraints** — the facts that are genuinely fixed.

Find facts yourself with sub-agents; the decisions are the user's. When the user answers with an implementation choice, ask once what outcome that choice protects: the outcome goes under Goal or Scope, the choice under Constraints when it is genuinely fixed.

Done when all four are named and every open question is answered. If the goal deserves a real standard rather than an analogy, say so — `survey` or `interrogate` produce an answer key, and an answer key is a stronger bar than any single reference.

## The bar is the whole trick

Everything else is scaffolding. The loop only produces quality if the thing it compares against is real. A bar has to pass three tests:

- **Named.** A specific thing, not a category. "Stripe's pricing page" works. "Award-winning SaaS sites" does not.
- **Fetchable.** The critic can actually get it — screenshot the live page, read the published piece, run the binary, open the repo, open the answer key. If the agent cannot obtain it, it will hallucinate the comparison.
- **Comparable.** Both can sit side by side and a judge can pick one. If you cannot imagine the A/B, it is not a bar.

Bars that work, when there's no answer key:

| Goal | Bar |
| --- | --- |
| Website, app, UI | The live site of a specific best-in-class product, screenshotted at the same viewport |
| Game, 3D, visual | Real footage or screenshots from a named shipped title |
| Writing | A specific published piece by a named author or publication, same length and format |
| Code, tooling | A named repo's implementation, plus its benchmark or test suite as the measurable half |
| Research, analysis | A named analyst report or a paper's methods section, judged on rigour and coverage |
| Deck, doc, deliverable | A real artifact from a firm known for it, same page count |

Prefer the hardest bar the agent can genuinely reach — a bar that is too easy makes the loop exit on round one. For a replacement product, the product being replaced is exact rather than analogical. When the user has none, propose the strongest inspectable comparison you can and justify it in one sentence. A bar guides the loop; it does not have to be reachable.

If the goal has a measurable half — load time, token cost, benchmark score, pass rate — name it alongside the reference. Taste plus a number beats taste alone.

## Write the prompt

Follow `GAUNTLET-PROMPT.md`: it holds the six moves of the brief, the driver table, and the rules. Print the brief and its arming lines in the chat inside one fenced block, and write nothing to disk.

Keep the brief under 200 words. Give the destination, the bar, and the instrument each critic inspects reality with; leave the route, the decomposition, and the number of rounds to the agent that receives it.

Finish by telling the user how to start the driver they chose — the budget included — that `--advisor` adds a second critic over the lead itself, that they stop the run when they are happy with the result, and that `learn` turns the run's lessons into a reusable skill afterwards.

## What breaks a gauntlet loop

- **A vague bar.** The critic invents a comparison and approves everything. Most common failure by far.
- **The builder judging its own work.** The critic must be a separate agent with fresh context. It should not know how hard the builder tried.
- **A soft critic.** Say "harsh" in the brief and give it a binary job: which one is better, or does this row pass. Scores out of ten drift upward every round.
- **A named exit after N rounds.** The exit is winning the comparison, the answer key passing, or the user stopping the run. Never a round count.
- **Over-specifying.** Every extra instruction is one fewer decision the agent makes with its own judgment. Minimal wins.
- **Grinding on an unknown.** If the answer key says `BLOCKED`, the loop is finished and a person decides. Looking harder is exactly what produces an invented answer.
