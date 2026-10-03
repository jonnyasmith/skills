# Change artifacts

The rules every artifact skill (`to-intent`, `to-design`, `to-plan`) follows. This file is the single source of truth for where artifacts live and what shape they take; the skills only name their own sections.

## Where they live

One **change** per directory, committed to the repo:

```
changes/<slug>/
  intent.html
  spec.html
  plan.html
```

The slug names the change, not the sentence: two to four words, kebab-cased (`claims-status-portal`). A later artifact reuses the slug of the change it belongs to. When no change directory exists yet, pick the slug, say it once so the user can rename it, and create the directory.

## Format

Each artifact is one standalone HTML document that opens correctly from disk in a browser:

- `<!doctype html>`, `<meta charset="utf-8">`, a viewport meta tag, and a `<title>`.
- Styles inline in a `<style>` block. No external scripts, stylesheets or fonts.
- The author chooses the markup and styling. What is fixed is the **sections**: each section the skill names appears as a heading with that name, in the order the skill gives.
- Links to the other artifacts of the change are relative (`<a href="intent.html">`).

Machine-readable facts go in `<meta>` tags in the `<head>`, so later tooling can read them without parsing prose:

```html
<meta name="artifact" content="intent">        <!-- intent | spec | plan -->
<meta name="change" content="claims-status-portal">
<meta name="status" content="draft">
```

## Diagrams

Use inline SVG diagrams wherever a diagram gets the idea across faster than prose. Which diagrams depends on the change, so no skill prescribes them. Good candidates:

- the flow today beside the proposed flow;
- the users, systems and components a change touches, and how they connect;
- a sequence of calls between systems;
- the order of work.

Each diagram:

- uses the real names from the change, not placeholders;
- sits in a `<figure>` with a one-sentence `<figcaption>` saying what it shows;
- keeps its text as SVG `<text>`, has a `viewBox`, and scales to the page width;
- shows something the surrounding prose does not already list. A diagram that restates a bullet list adds nothing.

Hand-write the SVG, or write Mermaid and inline the SVG that `npx -y @mermaid-js/mermaid-cli -i in.mmd -o out.svg -b transparent -t neutral` produces.

## Revisions

Edit an artifact in place. Git history is the revision record, so there are no version suffixes and no change logs inside the file.

Commit each artifact once the user has confirmed it, using the `conventional-commits` skill (`docs(<slug>): add intent`). Do not push or open a PR unless the user asks.
