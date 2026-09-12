# The kit's shape

One directory in the repository being worked on, under whatever reference path that repository already uses. Everything in it is committed.

```
docs/reference/<slug>/
  BAR.md          the ruler: published facts verbatim, captured truth, the target's limits, the rows
  PROMPT.md       the run prompt, so the brief and its ruler travel together
  source/         mirrored specifications, docs, schemas, registry entries
    MANIFEST.json url + sha256 per mirrored file, and the date captured
  fixtures/       real instances exactly as the source serves them
    MANIFEST.json url + sha256 per fixture, and why that instance was chosen
  truth.json      derived ground truth: per-fixture statistics, checksums, samples, recipes
  render/         the picture side, one image per fixture, reproducible from truth.json
```

Name `fixtures/` and `render/` for the domain when a domain word is clearer (`tiles/`, `hillshade/`, `screenshots/`). Keep the manifests where the assets are.

## BAR.md's sections

In this order, because a critic reads top to bottom and needs the instrument before the rows:

1. **What this file is** — one paragraph: the single graded reference, every number quoted from a mirror, every measurement dated, graded against the files beside it and never against memory.
2. **The mirror table** — kit path against origin URL, one row per mirrored file.
3. **The published facts, verbatim** — block-quoted from the mirror, with the mirror's path named. Formulas as formulas. The bar's own worked example, stated as input and exact expected output.
4. **The captured truth** — one table row per fixture with its identity and its headline statistics, plus a sentence naming the byte layout the checksums cover.
5. **The defect fixture** — what is wrong with it, counted exactly, how the defect was confirmed independently, and one sentence saying an implementation that trusts this input is wrong.
6. **What the target can represent** — the limits, each with the code path or document that sets it, then the fixtures measured against those limits. Close with what is therefore graded and what is not.
7. **The rows** — numbered, binary, each with its negative control indented beneath it.

## truth.json's shape

Data a critic loads, not prose it reads:

```json
{
  "captured": "2026-09-12",
  "recipe": { "derivation": "…", "byte_layout": "float32 little endian, row major, north-west first", "render": "…" },
  "fixtures": {
    "<name>": {
      "identity": { },
      "sources": ["<fixture path>"],
      "stats": { "min": 0, "p50": 0, "max": 0 },
      "derived_sha256": "…",
      "sample": [[]]
    }
  }
}
```

- `identity` is whatever addresses the instance: coordinates and zoom, a URL and viewport, a commit and a path.
- `derived_sha256` is the row-1 instrument. State the byte layout in `recipe`, or the checksum is unreproducible and therefore ungradeable.
- `sample` is small and human-readable, for the case where a checksum disagrees and somebody has to see why.
- `recipe.render` is what makes `render/` reproducible, so a critic can regenerate the picture side rather than trust it.

## A row's shape

```
N. **<One word: what property.>** <The check, with the kit file it reads and the exact expected value.>
   *Negative control:* <a concrete mutation of the work, and the failure it must produce.>
```

Rows worth having, roughly in this order of value:

| Row | Grades |
| --- | --- |
| Derivation | the checksums and the bar's published worked example |
| Addressing | the work reaches the same instance the truth names |
| Defects | the defect fixture is refused or repaired, and counted |
| Shape | rank order and relief against truth, not absolute values a lossy target cannot hold |
| Refusal | the thing that must not be accepted is not accepted |
| Invariants | the target's own consistency checks still pass with the work in place |
| Determinism | same input, same output, across every environment the project ships to |
| Budget | the project's standing resource checks still pass |
| The look, blind | the work's own render beside `render/<fixture>`, labels stripped, taken by the critic |
| Provenance | every shipped asset names its URL and hash, and the attribution the source requires ships with it |
