# The run prompt

Six moves, in this order. Write it into the kit as `PROMPT.md`. Keep the goal and the bar tight; the graph, the rules and the constraints are complete, because they are what the receiving agent cannot discover by reading the code.

1. **The goal**, in a short paragraph, ending with the sentence that hands over the approach: what is fetched, what is stored, what reaches the runtime, what the user sees, all its decision. No architecture.
2. **The bar**, by absolute path, with one sentence per thing the kit contains and one sentence saying the picture side is graded blind. "Read it before you plan. It is the ruler, not a suggestion."
3. **The constraints that are not in the code.** Only the ones a reader of the repository would not find: the dependency policy, the things that must never be run, the standing checks and how they are invoked, the documents that govern documents, what counts as evidence.
4. **The graph**, verbatim from below, with the bar path, the page path and the cap filled in.
5. **The rules**, verbatim from below.
6. **The progress page**, by path, with its contents named and its re-read discipline stated.

## The graph

The shape is fixed and the piece list is not. What the lead decides is the decomposition, the sequence, the ownership and every question the goal left open. What it does not decide is whether a piece gets its own critic, whether a critic sees the builder's report, or what a score means. Emit this block with only the bracketed parts filled in.

```
▸ THE GRAPH

You are the lead. You run this graph by spawning subagents and steering them with
messages. You never build.

BAR:          <kit>/BAR.md — every critic opens it itself. It supplies the rows,
              the verdict form and the out-of-scope list.
ANCHORS:      the published numbers in BAR.md and the checksums in truth.json.
              Restating, relaxing or recomputing one is a failure, not a result.
DECOMPOSE:    you name the pieces: the smallest units that can be built and
              graded independently, each owning a named subset of the bar's rows.
              You sequence them, including which has to land before which.
OWNERSHIP:    before any builder starts, every piece owns a named set of files,
              including the check that grades it. Anything shared is owned by
              exactly one named piece. Post the list before dispatching.
FAN OUT:      one `builder` subagent per open piece, at once. Never one builder
              for two pieces, never two builders in one piece's files.
HIDDEN EDGE:  where a row of piece A needs piece B's output, name it in the
              ownership post. Until B lands, that row is CANNOT JUDGE naming B,
              never FAIL.
PER PIECE:    an inner loop; every open piece runs its own at the same time.
  RULE:       the builder returns what it changed and which files it touched.
              Never a grade, never a screenshot of its own work. It keeps its
              remaining items and its current gap written in its piece's files
              or notes, not only in its head.
  VERIFY:     one `critic` subagent per round, fresh context, no sight of the
              builder's reasoning or report. It opens the bar, inspects the real
              output itself, and runs every row the piece owns. Blind and with
              labels stripped wherever a blind A/B is possible. PASS / FAIL /
              CANNOT JUDGE per row, no fourth verdict and no partial credit. A
              row with more than one lens passes only when every lens holds, and
              its negative control has a veto. Never a majority. The score is
              the count of rows that passed, out of the rows it owns; about 8 of
              10 is a pass. Its last act is to send the lead its score, its
              per-row verdicts and its single biggest remaining gap.
  REWORK:     a piece below a pass goes back to a builder carrying that one gap
              and nothing else.
BARRIER:      the pieces share one working tree and one build. Where a critic's
              rows read shared build output, stop that piece's builder before the
              critic runs. Otherwise the checks race the writes and the failures
              belong to nobody.
LOOP:         a piece closes when every row it owns passes. The run ends when no
              piece is open, the cap fires, or I stop it.
STALL:        a gap a critic names twice running is a stall. Say so and stop that
              piece instead of spending another round on it.
CAP:          <M> pieces x <N> rounds x 2 agents; no piece past <N> rounds.
ON FAIL:      a row nobody could run is CANNOT JUDGE, never a pass. A builder or
              critic that returns nothing is flagged, never silently skipped. The
              cap firing is a failure and must not report as success.
STEERING:     between rounds you may message any live agent to redirect it,
              re-grant a file, or answer a blocker. Steering is how you adapt;
              it is not how you build.
REPORT:       the progress page below is the report. One row per piece: rounds
              taken, rows still failing, and evidence a reader can chase.
HUMAN GATE:   an open question the bar can settle, you settle, and record. One
              the bar cannot settle stops the run and comes to me.
```

The graph is run by an agent, not by a workflow cell, which is the point: a cell needs the piece list before the first dispatch, and a real run discovers half of it in round two. Everything a cell would fix in code is fixed in this block instead, and only the piece list is left open.

## The rules

Verbatim. Each one exists because a run paid for its absence, and each one is a prohibition the graph above cannot express as a field.

```
1. The lead owns no files. It never edits and never runs a fix itself. Where a change is shared
   infrastructure, it spawns one builder that owns those files and steers it like the others. The
   lead's only outputs are decisions, messages and the progress page.
2. The builders share one working tree, so they will see each other's half-finished edits. Expect
   it, and do not diagnose another piece's breakage as your own.
3. A critic is read-only. It may run and read anything and must modify nothing. It proves a
   negative control in a scratch copy it can throw away, never in the tree.
4. A builder cannot close a gap outside its own piece. It reports the gap to the lead instead.
5. A run that ends without every verdict reaching the lead has produced nothing.
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
