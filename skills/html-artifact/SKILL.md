---
name: html-artifact
description: Render a deliverable as one self-contained HTML file rather than markdown. Use when the output is a set of options to choose between, a diff or module map, design tokens or component states, motion or a click-through, a diagram, a deck, an explainer, a status report or post-mortem, or a throwaway editor.
---

# HTML artifact

Markdown is one column of prose. Much of what an agent produces is **spatial** — three options beside each other, a call graph, a timeline, a thing with state you want to poke. Flattening that into the column destroys the part the reader came for, and the document gets skimmed instead of read.

One self-contained `.html` file costs about the same to write and keeps the shape. Reach for it whenever both tests pass:

1. The information is **spatial or interactive** — position, adjacency, or state carries meaning.
2. The artifact is the **deliverable**, something the user will open, not an intermediate you are reasoning through.

Linear prose stays markdown: an answer to a question, a summary, a commit message, a README.

## Shapes

Match the information to its shape. One file per artifact, whichever row fires.

| The information is | Render it as |
| --- | --- |
| Several options to choose between | Columns side by side, trade-offs inline, one chip per option that writes the user's reply |
| A change to code | Annotated diff — margin notes, severity tags, jump links, and where to focus |
| An unfamiliar package | Module map — boxes and arrows, hot path highlighted, entry points listed |
| Design tokens or component states | Contact sheet of swatches and variants, each one copyable |
| Motion, or an interaction | Live sandbox with the real easing curve, or the real screens linked together |
| A process or a pipeline | Inline SVG flowchart; click a step for what runs, timings, failure paths |
| A sequence of claims for an audience | One `<section>` per slide, arrow keys to navigate |
| A topic being explained | Collapsible sections, tabbed code samples, glossary in the margin |
| A status update or a post-mortem | Timeline plus one small chart |
| A set of things to sort, toggle, or tune | A throwaway editor for that exact thing, with a live preview |

Neighbouring skills own two cases: a design question answered by throwaway code belongs to [`prototype`](../prototype/SKILL.md), and a diagram meant to be edited by hand and pasted elsewhere belongs to [`excalidraw-diagram`](../excalidraw-diagram/SKILL.md).

## Rules

1. **One file, opened by double-click.** Inline the CSS, the JS, the SVG, and the data. Plain browser APIs only — a CDN `<script>` makes the artifact a blank page on a plane. It must survive being emailed.
2. **End with a round trip.** Every artifact carries a copy or export button that turns whatever the user did in the UI back into text — markdown, a diff, a prompt — for them to paste to you or commit. The artifact is one leg of a loop; the button is the return leg. Read-only artifacts export their conclusion.
3. **Lead with the question.** The first thing on the page says what this artifact answers, in one line. Where a prompt produced it, show the prompt.
4. **Write for the reader, in their language.** Labels come from the domain, not the code. Assume the reader opens the file with no other context.
5. **Restrained styling.** Clean typography, generous spacing, one accent colour. Motion appears only when motion is the subject.
6. **Disposable by default.** Write it to the OS temporary directory. Put it in the repo only when it belongs to the work there — beside the module or page it describes, named so a casual reader sees what it holds.

## Done

The user can open the file offline and get the artifact's answer out of it as text. Open it and check both before you hand it over.
