# Patterns

Seven shapes of the same diamond. Pick the closest, swap the bracketed parts,
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
HIDDEN EDGE:  [row N of piece A needs piece B's output] — list every one. Until
              B lands, that row is CANNOT JUDGE naming B, never FAIL.
PER PIECE:    an inner loop; every open piece runs its own at the same time
  RULE:       builder returns what it changed. Never a grade, never a
              screenshot.
  VERIFY:     a fresh checker opens the bar and runs every row this piece owns.
              PASS / FAIL / CANNOT JUDGE. No partial credit, no fourth verdict.
              A row checked by more than one lens passes only when every lens
              holds, and its negative control has a veto. Never a majority.
              It never sees the builder's report. A row it cannot run because
              another piece has not landed is CANNOT JUDGE naming that piece,
              never FAIL — no builder can close a gap outside its own.
  REWORK:     a piece that fails any row goes back to a builder carrying the
              checker's single biggest gap.
LOOP:         a piece closes when every row it owns passes. The run ends when
              no piece is open.
CAP:          [M] pieces x [N] attempts x 2 agents = [M*N*2]; no piece past [N]
ON FAIL:      a row nobody could run is CANNOT JUDGE, never a pass. The cap firing
              is a failure and must not report as success.
REPORT:       one row per piece: attempts taken, rows still failing, and
              evidence a reader can chase
HUMAN GATE:   a checker hitting an undecided question stops the run and asks me

(start the prompt with the word "workflow" so Claude builds the graph)
```

The loop is per piece, not per fleet. Build, check and rework are an inner loop
inside one piece, so the fleet is [M] independent gauntlets and its width is
however many pieces are still open. One outer loop that builds every piece and
then grades every piece is a waterfall with a QA gate, repeated, and it makes
every fast piece wait for the slowest.

One thing forces that outer loop back: a shared tree. When the pieces cannot be
isolated, no checker may run while any builder writes, so the barrier is real and
the run becomes rounds. Say so when it happens, and report a piece x round grid
instead. Keep the cap on attempts even then. A round count equals an attempt
count only when every piece runs in every round, and a piece held back to a later
stage, or one that closes early, breaks that in both directions.

The bar is the whole pattern. Named, fetchable, comparable — if a checker cannot
open it, it will invent the comparison and pass round one. An answer key of binary
rows is the strongest form: it works for goals with no existing product to sit
beside.

## Frontier

A fixed set of units that block each other, and too many edges to stage by hand.
The width is never chosen: it is re-derived after every merge.

```text
▸ GRAPH SPEC
GOAL: [every ticket in the spec implemented, on one branch, as one PR]

POINTERS:     the spec, the ticket list, the notes directory, the branch. A
              worker is handed paths and returns paths. Nothing is pasted.
EXPLORE:      one agent, alone, reads what the tickets need and writes notes to
              [a directory outside the repo]. It implements nothing.
FAN OUT:      one agent per ticket whose blockers have already merged, each in
              its own worktree. Re-derive that set after every merge, so the
              width rises and falls with the graph.
PER TICKET:   an inner loop; every ticket on the frontier runs its own at once
  RULE:       a worker returns its branch, its commits, and what it changed.
  VERIFY:     a fresh checker, before that ticket merges. It opens the ticket
              itself and never sees the worker's report.
  REWORK:     a rejected ticket returns to a worker and stays off the frontier
              until it passes. Nothing that depends on it starts.
  MERGE:      one at a time, in completion order. A merge that conflicts or
              breaks the build is rework, not a merge.
LOOP:         a ticket closes when it merges. The run ends when none is open.
CAP:          [N] tickets x [M] attempts x 2 agents = [N*M*2]; none past [M]
ON FAIL:      a ticket nobody could start names the blocker that never landed.
              Tickets still open at the cap are a failure, not a partial pass.
REPORT:       one row per ticket: attempts taken, when it merged, or what
              still blocks it
SAVE:         the PR, draft until every ticket has passed
HUMAN GATE:   nothing is marked ready for review without asking me

(start the prompt with the word "workflow" so Claude builds the graph)
```

The frontier is the whole pattern. Every other shape here fixes its width before
it starts. This one asks after each merge which tickets are now unblocked, so a
ticket becomes available the moment its blockers land rather than when a stage
boundary says so.

It is also the only safe use of one worktree per unit. The edges are real, but
the readiness rule guarantees the other side of each one has already merged.

Use it when the units are known, they block each other, and the graph is too
wide to stage by hand. When the blocking is shallow enough to write out, the
staged `FAN OUT` under **Fixes** is cheaper and easier to read.

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
space, or draw the edge and let them run in sequence. Never isolate two units a
listed hidden edge connects: separate spaces do not remove the edge, they only
hide it until the round is spent. Those units share one tree, so verify on a
quiet one — every builder stopped before any checker runs — or the checks race
the writes and the failures belong to nobody.

```text
FAN OUT:      one agent per [unit], each in its own git worktree, in parallel
MERGE:        merge the worktrees back one at a time
```

Isolation is not always available. When a unit needs another unit's output to
build or to be graded, separate worktrees guarantee it fails, unless a readiness
rule holds the unit back until its blockers have merged — that is **Frontier**.
Without one, draw the edge and run those units in sequence instead, and say so,
because that stage is now one unit wide.

```text
FAN OUT:      [unit A] alone, then [unit B and C] at once, then [unit D] last
STAGE EXIT:   [what must be true before the next stage starts]
```

Name that exit, and make it what the next stage needs — the arrays exist, the
crate builds — never "the piece passes". A unit whose own rows depend on a later
stage cannot pass in its own stage, and a plan that assumes it will spends a
round finding out.

**Mixed isolation.** Usually only part of a graph is connected. A unit is free
only if it appears nowhere in `HIDDEN EDGE`, on either side, **and** writes no
file another unit writes. Both, not either: two units with no edge between them
still collide if they touch the same file, and a worktree merge finds that late.

Split the fleet and run the halves at the same time under different rules.

```text
FAN OUT:      [free units] one worktree each, each running its own build, check
              and rework loop to completion, ungated by any stage
              [connected units] one shared tree, staged, every builder of a
              stage stopped before any checker runs
```

Default a unit to the connected half. A unit wrongly called free is graded in a
worktree where the other piece's output does not exist and nothing marks it
pending, so its checker returns FAIL where the truth is CANNOT JUDGE. A wrong
partition costs a round and a false verdict. An over-cautious one costs only the
barrier.
