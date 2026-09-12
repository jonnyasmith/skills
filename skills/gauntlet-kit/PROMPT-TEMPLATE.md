# The run prompt

Five moves, in this order. Write it into the kit as `PROMPT.md`. Keep the goal and the bar tight; the constraints and the rules are complete because they are what the receiving agent cannot discover by reading the code.

1. **The goal**, in a short paragraph, ending with the sentence that hands over the approach: what is fetched, what is stored, what reaches the runtime, what the user sees, all its decision. No architecture.
2. **The bar**, by absolute path, with one sentence per thing the kit contains and one sentence saying the picture side is graded blind. "Read it before you plan. It is the ruler, not a suggestion."
3. **The constraints that are not in the code.** Only the ones a reader of the repository would not find: the dependency policy, the things that must never be run, the standing checks and how they are invoked, the documents that govern documents, what counts as evidence.
4. **How to run it** — the loop, then the six rules, verbatim from below.
5. **The progress page**, by path, with its contents named and its re-read discipline stated.

## The loop

```
Divide the goal into the smallest pieces that can be improved and judged independently, and
sequence them yourself, including which piece has to land before which. For each important piece,
fan out a builder subagent and a separate critic subagent, using the `builder` and `critic` agent
types, with fresh context and no sight of the builder's reasoning.

Each builder keeps its own remaining items and its current verdict gap written down in its piece's
file or notes, not only in its head.

Each critic inspects the real output itself, never a report or a screenshot the builder took. It
compares directly with the bar, blind and with the labels stripped wherever a blind A/B is
possible, scores the round 0 to 10 where the score is the count of bar rows that passed with no
partial credit on any row, about 8 being a pass, and names the single biggest remaining gap. Below
a pass, the gap goes back to the builder and the piece runs another round. Keep looping until each
piece wins or I stop the run. A gap a critic names twice running is a stall: say so instead of
spending another round on it.
```

## The six rules

Verbatim. Each one exists because a run paid for its absence.

```
1. Before any builder starts, every builder owns a named set of files, including the test or check
   that grades its own piece. Anything shared is owned by exactly one named piece. Say so up front.
2. The lead owns no files. It never edits and never runs a fix itself. Where a change is shared
   infrastructure, it spawns one builder that owns those files and steers it like the others. The
   lead's only outputs are decisions, messages and the progress page.
3. The builders share one working tree and one build, so they will see each other's half-finished
   edits. Expect it, and do not diagnose another piece's breakage as your own.
4. A critic is read-only. It may run and read anything and must modify nothing. It proves a
   negative control in a scratch copy it can throw away, never in the tree.
5. A check a critic cannot run because another piece has not landed is not a failure of the piece
   it is grading. Report it as unjudgeable and name the piece it waits on. A builder cannot close a
   gap outside its own piece.
6. Every critic's last act is to send its verdict to the lead as a message. A run that ends without
   the verdict reaching the lead has produced nothing.
```

## The progress page

```
Maintain one live progress page at <path> that I can refresh to watch the work evolve: pieces,
rounds, scores, the current biggest gap, every decision you take, who owns which files, and what
you have promised to take. Update it every round and whenever you grant a file. It is your memory,
not a report: re-read it before every dispatch round and write to it before you wait.

Where the goal or the design documents leave something undecided, decide it against the bar and
record the reasoning on that page.
```

The ownership and promise columns are not bookkeeping. They are the only copy of state the lead cannot rebuild by reading the repository, and without them a compacted lead grants the same file twice.
