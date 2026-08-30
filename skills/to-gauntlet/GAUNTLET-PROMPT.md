# Gauntlet prompt format

What you hand over has two parts: the **brief** the agent reads, and the **driver** that keeps re-submitting it until the bar is met.

## The brief

Six moves, in this order. Write it as flowing prose, not headings. Under 200 words.

1. **The goal**, in one or two sentences, stated as what must be true when it is done. Fold the Scope you settled into this — the features that make the artifact recognisably itself.
2. **The constraints**, in the same breath. Stack, hosting, data to import. Only the ones that are genuinely fixed.
3. **The bar**, named as a thing the critic can open and look at.
4. **The loop**: the lead agent splits the goal into the smallest pieces that can be improved and judged separately, and decides that split itself. Each important piece gets a builder and a separate harsh critic — a fresh subagent starts blank, and that blankness is the independence. Name the **instrument** each critic inspects reality with: screenshots through `browser` and `inspect_image` for anything visual, the test or benchmark command for behaviour, real measurements for performance. The critic compares against the bar blind where possible, names the single biggest gap when ours loses, and sends it back.
5. **A scoreboard** the lead agent keeps current as the work evolves: `todo` phases plus a `local://<slug>-progress.md` page.
6. **Out of scope**, as a short list, then the trailer: `orchestrate`, lowercase, as a standalone word.

## The driver

| Bar | Driver | Stops on |
| --- | --- | --- |
| An inspectable artifact — product, screenshots, reference set | goal mode | the agent's own verified `goal({op:"complete"})`, the token budget, `--max-time` |
| A single number — fps, p95 latency, benchmark score | `/autoresearch` | max iterations per segment; the metric decides keep or revert per run |
| A critic prompt you want re-run verbatim | `/loop <count\|duration>` | the count or the clock |

Arm goal mode in two lines — objective first, since the budget attaches to an existing goal — then send the brief as the next message:

```text
/goal <one-line objective>
/goal budget 40000000
```

Arming does not start a turn, so the brief is the first thing the agent reads. Bare `/goal` opens an editor when the objective runs long. Goal mode then re-injects the objective after every yield, holds the agent to the full objective rather than an easier subset, and refuses "done" without current-state evidence; when the budget runs out it forces a wrap-up instead of a fake success. `/autoresearch` instead has the agent write `./autoresearch.sh` (exit 0, print `METRIC <name>=<value>`), commits it as a baseline, then keeps or reverts each experiment on the metric and flags runs that look reward-hacked.

Outside omp — Claude Code, Codex — the brief is unchanged, the driver is that harness's own continuation, and the stop condition is the user.

## Rules

**Give the destination, never the route.** No architecture, no file layout, no library choices beyond the fixed constraints, no list of the pieces to build, no fixed number of rounds. Prescribing those replaces the model's judgement with the user's.

**Name the bar as an artifact, not an adjective.** "The real Todoist web app and screenshots of it" is a bar. "Polished and professional" is not.

**Name the instrument, not the intention.** "Inspects the real running output" only becomes real when you say screenshot, test, or measurement. A critic with no instrument is another model with an opinion.

**Slash commands belong outside the brief.** They are the user's keystrokes; a `/loop` written into the prose is inert text to the model. The brief says what winning is; the driver does the re-submitting.

**Keep it short.** Matt Shumer's original was one paragraph of goal and two of method. Length here is a symptom of over-prescription.

## Example

Settled from an interview about replacing a Todoist subscription:

```text
/goal Self-hosted Todoist replica a Todoist user could switch to without noticing
/goal budget 40000000

Build a self-hosted Todoist replica that a Todoist user could switch to
without noticing. Tasks, projects, sections, labels, saved filters,
natural-language due date entry, recurring rules, and the full keyboard-first
interaction model. Single user. Runs as one Docker container with SQLite.
Imports a Todoist CSV export.

The bar is Todoist itself. Use the real web app and screenshots of it as the
reference for every visual and interaction decision.

Break this into the smallest pieces that can be improved and judged
separately, and decide that split yourself. Fan out a builder for each
important piece, and a separate harsh critic with fresh context. Each critic
drives the real running app in `browser`, screenshots it, and puts that image
side by side with Todoist blind — never the builder's summary. When ours
loses, name the single biggest gap and send it back.

Keep `todo` current and a `local://todoist-progress.md` page showing the work
evolving.

Out of scope: collaboration, karma, third-party integrations, push
notifications, native mobile apps.

Fan out subagents: orchestrate.
```

## Source

The method is Matt Shumer's, from [Claude of Duty](https://github.com/mshumer/Claude-of-Duty) and [How to Run a Gauntlet Loop](https://somethingbig.ai/gauntlet-loop).
