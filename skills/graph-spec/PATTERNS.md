# Patterns

Six shapes of the same diamond. Pick the closest, swap the bracketed parts,
keep `CAP` / `ON FAIL` / `HUMAN GATE`.

## Research desk

Wide questions, external sources, findings that must survive attack.

```text
▸ GRAPH SPEC
GOAL: decision-grade research on [question]

FAN OUT:      split into 5 distinct angles, one researcher per angle, in parallel
RULE:         every finding carries a source url and a date
VERIFY:       a fresh skeptic per finding tries to disprove it — correct, current,
              source resolves. Majority keeps it. Drop what fails.
MERGE:        survivors into one report ranked by confidence
CAP:          5 researchers, 3 skeptics per finding
ON FAIL:      flag any angle that returns nothing
REPORT:       top findings first, with the dropped claims listed at the end
SAVE:         research-report.md
HUMAN GATE:   change nothing else after that without asking me

(start the prompt with the word "workflow" so Claude builds the graph)
```

## Repo sweep

One agent per file. The unit is known up front, so the cap is a file count.

```text
▸ GRAPH SPEC
GOAL: [audit every route under src/routes/ for missing auth checks]

FAN OUT:      one agent per file, in parallel
RULE:         return { file, line, issue, evidence } — no free text
VERIFY:       an independent checker per finding, fresh context, must reproduce
              the issue from the file itself
DEDUPE:       same file + same line = one finding
CAP:          20 files this run
ON FAIL:      flag any file that returns nothing, never skip it silently
REPORT:       one merged list, plus how many files came back out of how many sent

(start the prompt with the word "workflow" so Claude builds the graph)
```

## Discovery loop

The size of the work is unknown until you are in it — finding one thing reveals
three more. Loop until it goes dry.

```text
▸ GRAPH SPEC
GOAL: hunt this repo for [security issues / broken error handling / dead code]

FAN OUT:      finders in parallel, each with a different search angle
DEDUPE:       check each new find against everything already seen, not just
              against what survived
VERIFY:       an independent checker on the fresh finds, three lenses
LOOP:         keep going until two rounds in a row find nothing new
CAP:          hard limit of [N] agents total so it cannot run away
ON FAIL:      report rounds that returned nothing
REPORT:       final list ranked by severity

(start the prompt with the word "workflow" so Claude builds the graph)
```

## Gated multi-phase

Research fans out, the user approves the pivot artifact, then writing fans out
from it. The gate is a real edge — everything downstream reads that one doc.

```text
▸ GRAPH SPEC
GOAL: [full launch kit for product X, aimed at audience Y]

PARALLEL JOBS (research, at once):
  1. [profile the buyer and the words they use]
  2. [map where those buyers spend time]
  3. [collect how competitors pitch them]
MERGE:        a one-page positioning doc
HUMAN GATE:   pause and show me the positioning doc before any writing
PARALLEL JOBS (writing, from that doc only):
  1. [landing page copy]
  2. [a week of launch posts]
  3. [outreach messages]
VERIFY:       a checker compares every asset to the positioning doc, flags drift
CAP:          3 + 3 agents
SAVE:         launch-kit/
HUMAN GATE:   publish nothing

(start the prompt with the word "workflow" so Claude builds the graph)
```

## Content draft

Three blind angles merge into an outline, one writer, one fact-checker.

```text
▸ GRAPH SPEC
GOAL: one ranking-ready draft for [topic]

PARALLEL JOBS (at once):
  1. what the current top-ranking pages cover
  2. the real questions people ask about this topic
  3. what those top pages skip
MERGE:        the three into an outline, then one writer produces a full draft
VERIFY:       a fact-checker flags every claim without a source
CAP:          3 researchers, 1 writer, 1 checker
SAVE:         drafts/, flagged claims listed at the top
HUMAN GATE:   publish nothing

(start the prompt with the word "workflow" so Claude builds the graph)
```

## Gauntlet

Build something and grind it against a fixed bar until it passes. The only shape
with an arrow going backwards: what the checker rejects returns to a builder. Use
it when the bar exists before the work does.

```text
▸ GRAPH SPEC
GOAL: [thing] where every row of the bar passes

BAR:          [absolute path / URL / product] — the checker opens it itself.
              It supplies the rows, the verdict form and the out-of-scope list.
ANCHORS:      [the fixed numbers carried in from before this work] — restating,
              relaxing or recomputing one is a failure, not a result.
FAN OUT:      one builder per [piece]; each owns a named subset of the bar
RULE:         builder returns what it changed. Never a grade, never a screenshot.
VERIFY:       a fresh checker per piece opens the bar and runs every row it owns.
              PASS / FAIL / CANNOT JUDGE. No partial credit, no fourth verdict.
              It never sees the builder's report. A row it cannot run because
              another piece has not landed is CANNOT JUDGE naming that piece,
              never FAIL — no builder can close a gap outside its own.
REWORK:       a piece that fails any row goes back to a builder carrying the
              checker's single biggest gap. It stays open until every row passes.
LOOP:         until no piece is open
CAP:          [N] rounds x [M] pieces x 2 agents = [N*M*2]
ON FAIL:      a row nobody could run is CANNOT JUDGE, never a pass. The cap firing
              is a failure and must not report as success.
REPORT:       piece x round grid, rows still failing, evidence a reader can chase
HUMAN GATE:   a checker hitting an undecided question stops the run and asks me

(start the prompt with the word "workflow" so Claude builds the graph)
```

The bar is the whole pattern. Named, fetchable, comparable — if a checker cannot
open it, it will invent the comparison and pass round one. An answer key of binary
rows is the strongest form: it works for goals with no existing product to sit
beside.

## Fixes

Not patterns — repairs bolted onto a spec that has the matching weakness.

**Layered fan-in.** For a fan-out above about 40 units, one final node cannot
hold every raw output. Summarize in batches first, merge the summaries.

```text
MERGE:        batch the results in groups of 40, summarize each batch, then write
              the answer from the summaries, never from the raw pile
```

**Seam first.** When every unit has to touch one shared boundary — a
registration table, a sized budget, a hash point, a composition root — the first
agent to land it wins and the rest conflict. Build it once, alone, before anything
fans out.

```text
SEAM FIRST:   one agent, alone, builds only the shared boundary every unit
              touches. It builds no unit. Nothing fans out until the tree
              builds and the standing checks still pass.
```

**Isolation.** Two workers that write the same file or hit the same
rate-limited API are not independent — that is a hidden edge. Give each its own
space, or draw the edge and let them run in sequence.

```text
FAN OUT:      one agent per [unit], each in its own git worktree, in parallel
MERGE:        merge the worktrees back one at a time
```

Isolation is not always available. When a unit needs another unit's output to
build or to be graded, separate worktrees guarantee it fails. Draw the edge and
run those units in sequence instead — and say so, because that stage is now one
unit wide.

```text
FAN OUT:      [unit A] alone, then [unit B and C] at once, then [unit D] last
STAGE EXIT:   [what must be true before the next stage starts]
```

Name that exit, and make it what the next stage needs — the arrays exist, the
crate builds — never "the piece passes". A unit whose own rows depend on a later
stage cannot pass in its own stage, and a plan that assumes it will spends a
round finding out.
