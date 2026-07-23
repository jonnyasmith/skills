# HTML Report Format

The test-suite review is rendered as a single self-contained HTML file in the OS temp directory. Tailwind and Mermaid both come from CDNs. Mermaid handles graph-shaped diagrams reliably (call flow, seam maps); hand-built divs and inline SVG handle the more editorial visuals (coverage bars, deep-vs-shallow mass diagrams, test-points-at-wrong-seam arrows). Mix the two — don't lean on Mermaid for everything, it'll start to look generic.

The report is **organised by seam**, not by file and not by finding-type. One card per seam.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Test-suite review — {{repo name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer for things Tailwind doesn't cover cleanly:
         dashed seam lines, coverage bars, wrong-seam arrows, etc. */
      .seam { stroke-dasharray: 4 4; }
      .wrong-seam { stroke: #dc2626; }
      .deep { background: linear-gradient(135deg, #0f172a, #1e293b); }
      .cov-bar { height: 0.5rem; border-radius: 9999px; }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>
      <section id="suite-health">...</section>   <!-- only when the suite is red / unrunnable / flaky -->
      <section id="seams" class="space-y-10">...</section>
      <section id="top-recommendation">...</section>
    </main>
  </body>
</html>
```

## Header

Repo name, date, and a compact legend: solid box = module, dashed line = seam, red arrow = test at the wrong seam, thick dark box = deep module, coverage bar = measured line/branch coverage. No introduction paragraph — straight into suite health (if any) then the seams.

## Suite-health banner (conditional)

Render this section **only** when the coverage pass couldn't produce clean numbers. It's the most important thing the audit found, so it goes first:

- **Red suite** — a rose-tinted banner: "Suite not runnable — {{N}} failing tests." One line on the failure, and the consequence: coverage is `n/a`, findings rest on static seam judgement.
- **No runner / no coverage config** — a slate banner: "No coverage tool detected — findings are static."
- **Flaky** — an amber banner listing the non-deterministic tests; each is also a `Rewrite`/`Relocate` seam-card below.

When coverage ran clean, omit this section entirely.

## Seam card

The diagrams carry the weight. Prose is sparse, plain, and uses the `/tdd` and `/codebase-design` terms without ceremony.

Each seam is one `<article>`:

- **Title** — names the seam (e.g. "Order intake seam", "PricingCalculator.quote seam"). Not a file name.
- **Badge row** — two badges:
  - **Seam-state** — `Fill` (indigo), `Rewrite` (amber), `Relocate` (sky), `Delete` (rose), `Healthy` (emerald).
  - **Coverage** — a compact bar + number (`82% branch`), or `n/a` (slate) when the suite didn't run.
- **Files** — monospaced list of the module and its test(s), `font-mono text-sm`.
- **Before / After diagram** — the centrepiece. Two columns, side by side. See patterns below.
- **Problem** — one sentence. What's wrong with the current test (or its absence).
- **Action** — one sentence. What the work-package will do.
- **Why** — bullets, ≤6 words each, in glossary terms. e.g. "Test hits internals, not interface", "No locality — bug is in caller", "Tautological: recomputes the code", "Deep seam, already honest".
- **Removal justification** (for `Delete`/`Relocate` only) — one line in a rose-tinted box naming *why* the test goes: tautological / implementation-coupled / duplicate. This line becomes the ticket's justification.

No paragraphs of explanation. If the diagram needs a paragraph to be understood, redraw the diagram.

## Diagram patterns

Pick the pattern that fits the seam. Mix them. Variety is part of the point.

### Coverage bar (the at-a-glance blind-spot signal)

A hand-built div bar per seam. Green fill for covered, grey track for uncovered; a red notch for an uncovered *branch* on a critical path. Keep it schematic — this is a pointer to a gap, not a dashboard KPI.

```html
<div class="cov-bar bg-slate-200">
  <div class="cov-bar bg-emerald-500" style="width:82%"></div>
</div>
<p class="text-xs uppercase tracking-wider text-slate-500 mt-1">82% branch · 3 uncovered on happy path</p>
```

### Mermaid graph — test points at the wrong seam

Use a `flowchart` when the point is "the test reaches past the public interface into internals," or "the real behaviour is one seam up." Colour the wrong-seam edge red, the deep module dark.

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      T[OrderValidator.test] -.tests internal.-> V[validateLine]
      subgraph Order intake module
        H[OrderHandler] --> V
      end
      classDef wrong stroke:#dc2626,stroke-width:2px;
      class T,V wrong
  </pre>
</div>
```

### Mass diagram — coupled vs behavioural test

Two rectangles per seam: how much the test asserts about *structure* vs *behaviour*. Before (coupled): a tall structure rectangle — the test knows the internals. After (behavioural): a short structure rectangle, a tall behaviour rectangle — the test only knows the interface.

### Before / after test list

The plainest and often the best. Two columns of `font-mono text-sm` test names. Before: `✗ calls repo.save() once`, `✗ private _normalize() returns…` (implementation-coupled). After: `✓ rejects order below minimum`, `✓ splits shipment across warehouses` (behavioural, reads like a spec). Strike-through the ones being deleted.

### Relocation arrow (hand-built SVG)

Two module boxes stacked; an arrow lifting the test from the shallow inner module up to the caller's seam. Use inline SVG `<path>` over a relative container. Reach for this on `Relocate` cards — it shows *where the test is going*, which prose can't.

## Style guidance

- Lean editorial, not corporate-dashboard. Generous whitespace. Serif optional for headings (`font-serif` works well with stone/slate).
- Colour sparingly: one accent (indigo) plus red for wrong-seam/leakage, amber for flaky/rewrite, emerald for healthy/covered, rose for delete.
- Keep diagrams ~320px tall so before/after sits comfortably side by side without scrolling.
- Use `text-xs uppercase tracking-wider` for module and seam labels inside diagrams — they should read as schematic, not as UI.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. The report is otherwise static — no app code, no interactivity beyond Mermaid's own rendering.

## Top recommendation section

One larger card. Which seam to act on first and one sentence on why (usually: highest-value deep seam with the weakest or most coupled test). Anchor link to its card. That's it.

## Tone

Plain English, concise — but the nouns and verbs come straight from `/tdd` and `/codebase-design`. Concision is not an excuse to drift.

**Use exactly:** module, interface, implementation, depth, deep, shallow, seam, locality, leverage · good test, behaviour, implementation-coupled, tautological, horizontal-slicing.

**Never substitute:** component, service, unit (for module) · API, signature (for interface) · boundary (for seam) · "brittle," "fragile" (name the anti-pattern instead) · "flaky" only for genuine non-determinism.

**Phrasings that fit the style:**

- "Test is implementation-coupled — asserts `repo.save` was called, not that the order persisted."
- "Tautological: the assertion recomputes the discount the way the code does."
- "Shallow module tested in isolation — no locality, the bug is in the caller."
- "Deep seam, behavioural test, leave it."

**Why bullets** name the defect or the gain in glossary terms: *"tests internals, not the interface"*, *"no locality — defect hides in the caller"*, *"deep seam, one place to test"*. Don't write *"improves quality"* or *"more robust"* — those aren't in the vocabulary and don't earn their place.

No hedging, no throat-clearing, no "it's worth noting that…". If a sentence could be a bullet, make it a bullet. If a bullet could be cut, cut it.
