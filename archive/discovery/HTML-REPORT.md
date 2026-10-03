# HTML Report Format

The default format for the discovery report — a single self-contained HTML file, Tailwind and Mermaid both from CDNs. It reads as an editorial architecture briefing: a system map up top, one card per flow, compact integration and trust-boundary sections, and a ranked gap list. Mermaid handles the graph-shaped diagrams (system map, sequences, state machines); hand-built divs and inline SVG handle the editorial touches (confidence bars, trust-zone shading).

Unlike the `improve-*` reviews, discovery is a **repo artefact**, not a throwaway. Write it alongside the discovery notes at `docs/<feature_name>/discovery.html` (create the directory if needed), not the temp dir. Print the absolute path and open it — `xdg-open` on Linux, `open` on macOS, `start` on Windows.

For a plain-text version — a PR diff, a fresh LLM session, or a repo that shouldn't carry HTML — follow [MARKDOWN-REPORT.md](MARKDOWN-REPORT.md) instead.

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Discovery — {{feature name}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script type="module">
      import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
      mermaid.initialize({ startOnLoad: true, theme: "neutral", securityLevel: "loose" });
    </script>
    <style>
      /* small custom layer: inference dashing, trust-zone shading, confidence bars */
      .inference { stroke-dasharray: 5 5; }
      .trust-zone { background: repeating-linear-gradient(45deg, #f8fafc, #f8fafc 8px, #f1f5f9 8px, #f1f5f9 16px); }
      .conf-bar { height: 0.5rem; border-radius: 9999px; }
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-5xl mx-auto px-6 py-12 space-y-12">
      <header>...</header>              <!-- feature, codebase, date, confidence summary -->
      <section id="system-map">...</section>
      <section id="flows" class="space-y-8">...</section>
      <section id="integrations">...</section>
      <section id="trust-boundaries">...</section>
      <section id="gaps">...</section>
    </main>
  </body>
</html>
```

## Header

Feature name, codebase, date, and a **confidence summary table** — surfaces / flows / integrations / trust boundaries, each with a confidence badge. No introduction paragraph — straight into the system map.

**Confidence badges** — colour + word, used in the summary table, every flow heading, and the integrations table: 🟢 High (emerald), 🟡 Medium (amber), 🔴 Low (rose). Render as a small pill: `text-xs uppercase tracking-wider rounded-full px-2 py-0.5`.

## System map

One card holding one Mermaid diagram — the whole system at a glance. Default to a `flowchart LR` with three subgraphs: Surfaces (left), Subsystems (middle), Integrations (right). Mark inferred nodes with a dashed `classDef` so the eye separates confirmed structure from reasoning. If the system is better described another way (`architecture-beta` for infra-shaped, `C4Context` for a service-in-environment view), use it.

```html
<div class="rounded-lg border border-slate-200 bg-white p-4">
  <pre class="mermaid">
    flowchart LR
      classDef inference stroke-dasharray:5 5,stroke:#d97706,fill:#fffbeb;
      subgraph Surfaces
        R["POST /orders"]
      end
      subgraph Subsystems
        H["OrderHandler"]
        V["Validator"]:::inference
      end
      subgraph Integrations
        DB["Postgres"]
      end
      R --> H --> V --> DB
  </pre>
</div>
```

Keep it to one screenful. Short labels in the diagram; full file paths in the evidence text around it.

## Flow cards

The heaviest analytical section — one `<article>` per key flow. Flows trace what *happens*, not just what exists.

- **Title + confidence badge** — the flow name (e.g. "Place order") and its badge.
- **Surface** — the entry citation as inline code: `<code class="font-mono text-sm">src/routes/orders.ts:42</code>`.
- **Diagram** — a Mermaid `sequenceDiagram` for a linear call sequence, or `stateDiagram-v2` for a state machine. Wrap in the same bordered card as the system map.
- **Exit** — one line: where the flow ends (response, event, side effect).
- **Inference callouts** — an amber-tinted box beneath the diagram for anything derived rather than observed, naming the evidence it came from.

```html
<article class="space-y-3">
  <div class="flex items-center gap-3">
    <h3 class="font-serif text-xl">Place order</h3>
    <span class="text-xs uppercase tracking-wider rounded-full px-2 py-0.5 bg-emerald-100 text-emerald-800">High</span>
  </div>
  <p class="font-mono text-sm text-slate-600">src/routes/orders.ts:42</p>
  <div class="rounded-lg border border-slate-200 bg-white p-4">
    <pre class="mermaid">
      sequenceDiagram
        Client->>OrderHandler: POST /orders
        OrderHandler->>Validator: validate(body)
        OrderHandler->>DB: insert order
        OrderHandler-->>Client: 201 Created
    </pre>
  </div>
  <p class="text-sm"><span class="font-semibold">Exit:</span> 201 to client; <code>order.created</code> on SQS.</p>
  <div class="rounded border-l-4 border-amber-400 bg-amber-50 p-3 text-sm">
    <span class="font-semibold">Inference:</span> validation is synchronous inside OrderHandler — no separate service call observed, validator not fully inspected.
  </div>
</article>
```

## Integrations

A compact table: Integration | Type | Evidence | Confidence. Types, no others: `database`, `queue`, `api`, `auth`, `storage`. If the data model itself is worth showing, add one Mermaid `erDiagram` below the table. File paths render as inline code; confidence as a badge.

## Trust boundaries

One block per boundary — name where it sits, what it guards, and whether that's evidence or inference. A Mermaid `flowchart` with `subgraph` trust zones makes the boundary visible: nodes inside a zone are trusted, edges crossing a subgraph border are the boundary. Shade the trusted zone with `.trust-zone`. **If no trust boundary is found, say so as a high-impact gap — absence is itself a discovery.**

## Gaps

Ranked list, highest impact × uncertainty first. Each gap names exactly what is missing — not "X is unclear" but a specific missing piece and what it affects. Prefix with a severity dot: 🔴 high · 🟡 medium · ⚪ low. A Mermaid `quadrantChart` (impact × uncertainty) above the list reads well when there are several gaps.

When the Phase 3 gap loop resolves a gap, strike it through (`<del>`) and add the resolution inline, or move it to a "Resolved" subsection at the bottom.

## Style guidance

- Lean editorial, not corporate-dashboard. Generous whitespace. Serif optional for headings (`font-serif` with stone/slate reads well).
- Colour sparingly: the confidence palette (emerald/amber/rose) plus one neutral accent. Reserve amber for inference callouts.
- Keep diagrams to one screenful each; prefer several small diagrams over one dense one.
- Use `text-xs uppercase tracking-wider` for schematic labels inside diagrams.
- Mark inferred nodes/edges distinctly (dashed `classDef`) so confirmed structure and reasoning stay visually separate.
- The only scripts are the Tailwind CDN and the Mermaid ESM import. Otherwise static — no app code, no interactivity beyond Mermaid's rendering.

## Tone and vocabulary

Use the discovery vocabulary from [GLOSSARY.md](GLOSSARY.md) exactly — **surface**, **flow**, **integration**, **trust boundary**, **evidence**, **inference**, **gap**. Never substitute "endpoint," "dependency," "boundary," or "unknown."

Every claim is either **evidence** (a cited file path) or an **inference** (labelled with its basis). If a diagram needs a paragraph of prose to be understood, redraw it. No hedging, no throat-clearing.
