# HTML Report Format

The shareable, visual swap-in for [MARKDOWN-REPORT.md](MARKDOWN-REPORT.md) — a single self-contained HTML file, Tailwind from CDN (and Mermaid, only if a finding is genuinely graph-shaped). Reach for it when the write-up is a briefing for a human who won't open the repo; the Markdown format stays the default for cited notes that live in the repo and get re-ingested.

Research findings are prose + citations, not diagrams, so this report is **editorial, not a dashboard**: a clear answer up top, findings as readable cards, and every claim linked to its source. Don't manufacture diagrams — add a Mermaid graph only where a relationship (a version timeline, a decision tree, a data flow between sources) actually earns one.

Write it to the OS temp directory so nothing lands in the repo unless asked — resolve from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows) — as `<tmpdir>/research-<slug>-<timestamp>.html`. Print the absolute path and open it — `xdg-open` on Linux, `open` on macOS, `start` on Windows. (If the user wants it kept in the repo, save it beside their notes instead.)

## Scaffold

```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Research — {{question}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- include the Mermaid import only if a finding needs a diagram -->
    <style>
      .primary { border-left: 3px solid #059669; }   /* primary source */
      .secondary { border-left: 3px solid #d97706; }  /* secondary — flag it */
    </style>
  </head>
  <body class="bg-stone-50 text-slate-900 font-sans">
    <main class="max-w-3xl mx-auto px-6 py-12 space-y-10">
      <header>...</header>          <!-- question, scope, date -->
      <section id="answer">...</section>
      <section id="findings" class="space-y-6">...</section>
      <section id="sources">...</section>
    </main>
  </body>
</html>
```

Note the narrower column (`max-w-3xl`) — this is a reading document, not a wide report.

## Header

The question, its scope, and the date. No preamble — the answer comes next.

## Answer

The bottom line first, in a visually prominent card (a tinted box, `bg-white rounded-lg border p-5`). Two to four sentences answering the question directly, each load-bearing claim carrying a superscript citation link (`<sup><a href="#s1">1</a></sup>`) to the sources section. A reader who reads only this box should have the answer.

## Finding cards

One `<article>` per sub-question or theme. Prose, not bullets-for-their-own-sake. Each claim links to its source. Where sources disagree, are silent, or are dated, render an amber-tinted **Uncertainty** callout — the same honesty the Markdown format requires.

```html
<article class="space-y-2">
  <h3 class="font-serif text-lg">{{theme}}</h3>
  <p class="text-sm leading-relaxed">
    The finding, stated plainly, with the detail that matters<sup><a href="#s1" class="text-emerald-700">1</a></sup>.
  </p>
  <div class="rounded border-l-4 border-amber-400 bg-amber-50 p-3 text-sm">
    <span class="font-semibold">Uncertainty:</span> the spec is silent on X — behaviour inferred from the reference implementation, not documented.
  </div>
</article>
```

## Sources

A numbered list, each entry anchored (`id="s1"`) so the citation links resolve. Show the title, the URL (or `path:line` for source code), and whether it's **primary** (official docs / spec / first-party source) or **secondary**. Mark the left border green for primary, amber for secondary via `.primary` / `.secondary`, so the trust level is visible at a glance. Record version and access date for anything version-sensitive.

```html
<ol class="space-y-2 text-sm">
  <li id="s1" class="primary pl-3">
    <a href="https://..." class="underline">Official spec — §4.2</a>
    · primary · accessed 2026-07-23
  </li>
  <li id="s2" class="secondary pl-3">
    Blog post — treat as secondary; corroborated against s1.
  </li>
</ol>
```

## Style guidance

- Editorial and readable — narrow column, generous line height, serif headings optional. Not a metrics dashboard.
- Colour carries meaning only: green = primary source, amber = secondary / uncertainty. Otherwise stay neutral.
- No diagrams unless a relationship earns one. If you add Mermaid, include the ESM import and wrap it in a bordered card like the other reports.
- The only scripts are the Tailwind CDN (and Mermaid, if used). Otherwise static.

## Tone

Answer first, then evidence. Every claim links to a source or is labelled an inference. Primary sources only; flag secondaries. Name uncertainty rather than smoothing it over. No hedging, no throat-clearing.
