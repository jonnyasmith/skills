---
name: to-gauntlet
description: Turn a rough goal into a Gauntlet Loop — an interview, a real quality bar, and the brief plus driver that keeps the loop running.
argument-hint: "What do you want built? e.g. a self-hosted Todoist replica"
disable-model-invocation: true
---

Interview the user about **what** they want built, then hand them a Gauntlet Loop: a brief, and the driver that keeps re-submitting it.

A Gauntlet Loop gives a lead agent a goal and a real quality bar, lets it split the work, and puts every piece through a separate critic that compares the actual output against the bar. Your job is the interview, the bar, and the driver. The receiving agent decides everything else.

## Settle the four

Interview until you can name all four:

**Goal** — the artifact, and what makes it worth building.

**Bar** — a real, inspectable thing a critic can hold the work against, side by side. An existing product, a set of reference sites, sample paragraphs, a test suite, a latency target.

**Scope** — what is in, and what is explicitly out.

**Constraints** — the facts that are genuinely fixed: stack, hosting, data to import.

Ask in rounds, using the question format from the `grilling` skill: number each question, put the whole unblocked frontier in one round, attach your recommended answer to each, then wait. Find facts yourself with sub-agents; the decisions are the user's.

**The bar is the part that matters.** Prefer one that already exists — for a replacement product, the product being replaced is exact rather than analogical. When the user has none, propose the strongest inspectable comparison you can and justify it in one sentence. A bar guides the loop; it does not have to be reachable.

When the user answers with an implementation choice, ask once what outcome that choice protects. Record the outcome under Goal or Scope. Keep the choice under Constraints when it is genuinely fixed.

Done when all four are named and the user has answered every open question.

## Pick the driver

Prose alone stops at the first yield. A **driver** re-submits the work after every yield and carries the stop condition, so it is part of what you hand over: goal mode when the bar is an artifact, autoresearch when the bar is one number. The shape of the bar picks it; the user picks the budget. GAUNTLET-PROMPT.md holds both.

## Write the prompt

Follow GAUNTLET-PROMPT.md. Print the brief and its arming lines in the chat inside one fenced block, and write nothing to disk.

Keep the brief under 200 words. Give the destination, the bar, and the instrument each critic inspects reality with; leave the route, the decomposition, and the number of rounds to the agent that receives it.

Finish by telling the user how to start the driver they chose — the budget included — that `--advisor` adds a second critic over the lead itself, that they stop the run when they are happy with the result, and that `learn` turns the run's lessons into a reusable skill afterwards.
