---
name: gauntlet-kit
description: Turn a goal plus whatever reference material the user supplies into a bar that builders and critics grade against, and hand back the prompt that runs the loop in a fresh session.
argument-hint: "The goal, and the reference to verify it against"
disable-model-invocation: true
---

The user gives you a goal and some reference material. You give back two things:

1. **`BAR.md`**, written into the run's own directory. Every builder and every critic in the run opens this one file.
2. **`PROMPT.md`** beside it, and the same text in a fenced block for the user to paste into a fresh session. That session runs the loop. You do not.

Then you stop. This session wrote the standard, so it cannot also judge work against it.

## Where the run lives

One directory per run, named for when it started and what it is for:

```
.loops/<YYYY-MM-DD-HHMM>-<feature_name>/
  BAR.md      the ruler
  PROMPT.md   the brief that points at it
  <anything the bar grades against: captured instances, reference images, mirrored pages>
```

Create it, and make sure `.loops/` is in the repository's `.gitignore`. Add the line if it is not there.

Ignoring it is deliberate. The bar is not work product: it existed before the run and it must not appear in the diff a critic grades, or a critic starts reading the ruler as part of the change and a builder starts editing the ruler to pass it. Ignored, `git status` during the run shows only what the builders made.

A bar worth keeping past its run gets copied into the repository's own reference path and committed there, as a deliberate act, after the run.

## The one rule

**The bar says what must be true of the finished thing. It never says how to build it.**

A bar row describes an outcome anybody can check from outside the work: a value, a behaviour, a refusal, a look. It never names a design, a data structure, a library, a file, or an order of work. The whole point of the loop is that the model decides all of that and is measured only on what came out.

Test every row you write: could two completely different implementations both pass this? If only one could, you have written a design and it goes in the bin.

## Build the bar

### 1. Read what the user gave you

Every file, every link, every image they passed. That material is the only source of graded facts. Nothing in the bar comes from your own memory of the subject, and anything you cannot point at in the reference does not become a row.

If the reference is thin, say what is missing and ask for it once. A bar built on guesses grades confidently and wrongly.

### 2. Pull out the checkable facts

From the reference, quote every fact a critic could measure against: numbers, thresholds, rules, formulas, limits, and any example the source itself publishes as correct. Quote them verbatim in `BAR.md`, each with the file or URL it came from.

If the reference includes instances - data, pages, captures, images - copy them into the run directory and list each with where it came from and its hash. The run then grades against fixed bytes, so round twelve measures the same thing round one did, and nothing depends on the network being up. Reference material the user already keeps in the repository stays where it is: cite its path in `BAR.md` rather than duplicating it.

Where the goal has a look, the reference images are the picture side: a critic puts the work's own output beside them with labels stripped and says which is which.

### 3. Say what the target can express

Find the real limits of the thing being built: its resolution, its storage, its budget, its published constraints. Write them down with the code path or document that sets each one, then measure the reference against them.

This is what stops a row demanding fidelity the system cannot hold. Such a row fails every round no matter how good the work is, and it teaches the critic to distrust its own verdicts.

### 4. Write the rows

Ten or so, each binary, each in this shape:

```
N. **<What property.>** <What to open, and the value or behaviour expected, with its tolerance.>
   *Negative control:* <a concrete edit to the work that must make this row fail.>
```

The negative control is the row's proof of life. A check a broken system can satisfy is not a check, and without a control every round passes it. The control must be a real edit somebody could make, not a hope.

Spread the rows across what actually breaks: correct values, the shape and order of the result, handling of bad input, what must be refused, provenance, and the blind look. Not ten flavours of the happy path.

If the reference contains an instance where the source's own data is wrong, misleading or out of its published range, keep it and quantify what is wrong with it. It is the one instance an implementation that merely trusts its input cannot pass.

Mark any row that only the finished system can satisfy - determinism across environments, a whole-project budget, the blind look. No single piece can pass those alone, and unmarked they burn a round with every piece claiming them.

### 5. State the scoring

In `BAR.md`, at the end:

- Every row is PASS, FAIL, or CANNOT JUDGE. No fourth verdict and no partial credit on a row.
- A row with more than one lens passes only when every lens holds. A negative control that does not fail kills the row on its own.
- A piece is done when every row it owns passes. Not most of them.
- A row that cannot be run because another piece has not landed is CANNOT JUDGE, naming that piece. It never counts as passed.

### 6. Grade the bar before you hand it over

Everything above was written and checked by you. Check it from outside: give a fresh critic subagent the bar and the repository as it stands, with none of the work done, and have it grade every row.

- The untouched repository must score **zero rows passed**.
- Every row it could not run must name a missing piece, never a missing instruction.

A row the critic had to ask a question about is broken. This is the last moment that is cheap to discover.

## Hand back the prompt

Write it to `PROMPT.md` in the run directory, then emit the same text in one fenced block. Keep the goal and constraints short. Leave the graph exactly as it is: it fixes who judges and what a verdict means, and nothing about the solution.

```text
<The goal, in a short paragraph. What must be true when it is done, and for whom. End with:
"You decide everything about how this works. No architecture is prescribed here.">

THE BAR is .loops/<run>/BAR.md, already on disk: <one line per thing it contains>. Read it before
you plan. It is the ruler, not a suggestion. Nothing in .loops/ is yours to edit.

Constraints that are not in the code and that you cannot discover by reading it:

- <only the facts a reader of this repository would not find: the dependency policy, what must
  never be run, the standing checks and how they are invoked, what counts as evidence>

THE GRAPH

You are the lead. You run this graph by spawning subagents and steering them with messages. You
never build.

DECOMPOSE:    yours. Split the goal into the smallest pieces that can be built and graded
              independently, each owning a named subset of the bar's rows. You choose them,
              sequence them, and change them when the work teaches you something.
OWNERSHIP:    before any builder starts, every piece owns a named set of files, including the
              check that grades it. Anything shared is owned by exactly one named piece. Post the
              list before dispatching.
FAN OUT:      one `builder` subagent per open piece, at once. Never one builder for two pieces,
              never two builders in one piece's files.
BLOCKED ROW:  where a row of piece A needs piece B's output, say so in the ownership post. Until B
              lands, that row is CANNOT JUDGE naming B, never FAIL.
PER PIECE:    an inner loop; every open piece runs its own at the same time.
  BUILD:      the builder returns what it changed and which files it touched. Never a grade, never
              a screenshot of its own work. It keeps its remaining items and its current gap
              written in its piece's files or notes, not only in its head.
  VERIFY:     one `critic` subagent per round, fresh context, no sight of the builder's reasoning
              or report. It opens the bar, inspects the real output itself, and runs every row the
              piece owns, blind and with labels stripped wherever a blind comparison is possible.
              PASS / FAIL / CANNOT JUDGE per row, by the bar's scoring rule. Its last act is to
              send the lead its per-row verdicts and the single biggest remaining gap.
  REWORK:     a piece with any row failing goes back to a builder carrying that one gap and
              nothing else. How it closes the gap is its own.
LOOP:         a piece is done when every row it owns passes. The run ends when no piece is open,
              or when I stop it.
STALL:        a gap a critic names twice running is a stall. Tell me instead of spending another
              round on it.
SHARED TREE:  the pieces share one working tree and one build, so a critic reading shared build
              output while a builder writes is grading a race. Keeping those apart is yours to
              arrange, and another piece's half-finished edits are not your piece's breakage.
READ-ONLY:    a critic modifies nothing. It proves a negative control in a scratch copy it throws
              away, never in the tree.
ON FAIL:      a row nobody could run is CANNOT JUDGE, never a pass. A builder or critic that
              returns nothing is flagged, never silently skipped. Rows still failing when the run
              ends are reported as failing.
STEERING:     you may message any live agent at any time to redirect it, grant a file, answer a
              blocker or kill a piece. Steering is how you adapt. It is not how you build. You own
              no files: where a change is shared infrastructure, spawn a builder that owns those
              files and steer it like the others.

Maintain one live progress page at .loops/<run>/PROGRESS.md that I can refresh to watch the work
evolve: pieces, rounds, verdicts, the current biggest gap, every decision you take, who owns which
files, and what you have promised to take. Update it every round and whenever you grant a file. It
is your memory, not a report: re-read it before every dispatch round and write to it before you
wait.

Where the goal leaves something undecided, decide it against the bar and record the reasoning on
that page. A question the bar cannot settle stops the run and comes to me.
```

Then tell the user: the run directory, its size on disk, and to paste the block into a fresh session.

## What ruins a run

- **A row with no negative control.** It passes from round one and nobody notices.
- **A row that names a solution.** "Uses a cache" is a design. Grade the latency it was supposed to buy.
- **A row demanding what the target cannot express.** It never passes, and the critic learns to discount itself.
- **A fact you remembered instead of quoted.** An unsourced number in a ruler is worse than no ruler.
- **A bar the critic still has to fetch around.** On the round the source is slow, that row gets graded from memory.
- **Every instance clean.** Then the loop grades an implementation that trusts its input, which is the one that fails in the real world.
- **A critic that reads the builder's report.** That is one agent grading its own homework with extra steps.
