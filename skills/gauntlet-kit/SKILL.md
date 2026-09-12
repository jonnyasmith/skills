---
name: gauntlet-kit
description: Forge a committed bar kit — mirrored sources, real fixtures, checksummed ground truth, reference images, binary rows with negative controls — then the prompt that runs a gauntlet loop against it.
argument-hint: "The goal to build a kit for, and any reference you already have"
disable-model-invocation: true
---

You hand back **a kit in the repository** and **one prompt** that points at it. The user pastes the prompt into a fresh session, and that session does the work.

A kit is a **ruler**: a bar captured to disk before the run, so every critic in every round measures against the same thing. A reference an agent fetches per round is not a ruler. It drifts, it rate-limits, it is remembered rather than read, and thirty critics grade thirty slightly different standards.

**You are not running the loop.** You forge the ruler and write the brief. The receiving session splits the work, spawns builders and critics, and decides everything else. Do not offer to run it here: this session authored the standard, and judging work against a standard you wrote is not judging.

## When a kit beats a plain reference

`to-gauntlet` writes a brief around a reference or an existing answer key. Forge a kit instead when any of these hold:

- The bar has **published facts** — a specification, a table, a formula, a rule list — that a critic would otherwise recall from memory.
- The bar has **instances** — real data, real pages, real files — that can be captured once and graded forever.
- A round's verdict depends on a **derived value** (a decode, a parse, a render) that a checksum can settle without trusting anyone's report.
- The work will run for **many rounds**, so per-round fetching is per-round drift.

## Steps

`KIT.md` holds the kit's file layout, `truth.json`'s shape and a row's shape. Open it before step 2 and write into that layout as you go.

### 1. Fix the bar's own truth

Research the bar until you can name the origin of every fact you intend to grade. Primary sources: the specification, the vendor's own docs, the dataset's registry entry, the shipped product. Delegate the reading to scouts; keep the judgement.

_Done when_ every claim you will grade has a URL or a repository path, and you have found the bar's **worked example** — the case its own authors publish as proof of correct handling. That example becomes a row.

### 2. Mirror it

Copy every page, table and schema you rely on into the kit's `source/`, with a manifest giving each file its URL and its SHA-256.

_Done when_ the whole loop can run with the network off.

### 3. Capture fixtures

Real instances, named for what they are, chosen to span the bar rather than to be convenient: the easy case, the hard case, the degenerate case. Capture them raw, exactly as the source serves them, with URL and SHA-256 for each.

Then capture one more: a **defect fixture**, an instance where the bar's own data is wrong, misleading, or out of its published range. Quantify the defect exactly and say in the kit that it is kept on purpose. It is the single highest-value fixture in the kit, because it is the one an implementation that merely trusts its input cannot pass.

_Done when_ every fixture is hashed, one fixture is known-bad with its defect counted, and the reason each place was chosen is written down.

### 4. Decode to ground truth

Derive the truth from the raw fixtures yourself and record it as data, not prose: per-fixture statistics, a **checksum of the derived form** with its byte layout stated, and a small sample a human can read.

_Done when_ a critic can grade a builder's derivation by checksum alone, with no report in the loop.

### 5. Render the picture side

Where the goal has a look, render one image per fixture from the ground truth, by a recipe recorded beside it. These are what a blind A/B holds the work against. Screenshots of a live product are captured at a stated viewport and hashed like any other fixture.

_Done when_ each image is reproducible from the kit alone.

### 6. State what the target can represent

Find the limits of the thing being built — its resolution, its storage, its published constraints — and state them in the kit with the code path or document that sets each one. Then measure the fixtures against those limits.

_Done when_ the kit says plainly which properties are gradeable and which the target cannot express, so no row asks for fidelity the system cannot hold. A row that demands the impossible fails every round and teaches nothing.

### 7. Write the rows

Ten or so binary rows. Each row names the kit file it reads, the value it expects, and its **negative control**: a concrete mutation of the work that must make the row fail.

_Done when_ a stranger can run every row without asking a question, every row has a control that is an actual edit rather than a hope, and the rows grade shape, order, provenance and refusal — not just happy-path values.

Then state the scoring in the kit: the score is the count of rows that passed, no partial credit on a row, a row that cannot run because another piece has not landed is unjudgeable and names the piece it waits on.

### 8. Write the run prompt

Follow `PROMPT-TEMPLATE.md`. Keep the moves it names and cut everything else. Write it into the kit as `PROMPT.md` so the run and its ruler stay together.

### 9. Hand it back

Commit the kit. Tell the user to paste `PROMPT.md` into a fresh session, and give them the arming lines from `RUNNING.md`.

## What breaks a kit

- **A kit the loop still has to fetch around.** If a critic needs the network to grade a row, that row will be graded from memory on the round the site is slow.
- **Rows without negative controls.** A check a broken system can satisfy is not a check, and every round will pass it.
- **Ground truth as prose.** "The median elevation is about 1,250 m" is a claim; a checksum of the decoded grid is an instrument.
- **No defect fixture.** Every fixture clean means the loop grades an implementation that trusts its input, which is the implementation that fails in the real world.
- **Grading what the target cannot represent.** Absolute fidelity against a lossy store produces a row that never passes and a critic that learns to discount its own verdicts.
- **A kit written from the model's memory of the spec.** Quote the mirror, verbatim, with its path beside it. An unsourced number in the ruler is worse than no ruler, because it is graded against confidently.
- **Interviewing when the bar already exists.** If `.bar/*/ANSWER-KEY.md` or `.wayfinder/*/ANSWER-KEY.md` covers the goal, its rows are the rows; capture fixtures for them instead of inventing a second standard.

## Worked example

`~/dev/transport/docs/reference/terrain-tiles/` is a kit forged by this process for importing AWS Terrain Tiles into a game engine: 5 mirrored specification pages, 28 real tiles across 7 named places, `truth.json` with a SHA-256 of each decoded grid, 7 hillshades as the picture side, the engine's own storage limits stated as a table, and 10 rows each with a negative control. Its defect fixture is open ocean at zoom 13, where 98.4 percent of the mosaic is a zero fill rather than the sea floor and 1,536 samples fall outside the published range. Read `BAR.md` there for the shape of a finished ruler.
