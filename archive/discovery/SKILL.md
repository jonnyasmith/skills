---
name: discovery
description: 'Build a visual, evidence-backed architecture discovery report for a feature or app area, then interactively resolve the highest-impact gaps.'
disable-model-invocation: true
argument-hint: "<feature_name> [optional: focus area] e.g. 'user_auth auth + billing flow'"
---

# Discovery

Produce a visual architecture discovery report grounded in the current repository, then walk the highest-impact gaps one question at a time until the picture is clear.

Use the vocabulary in [GLOSSARY.md](GLOSSARY.md) exactly — **surface**, **flow**, **integration**, **trust boundary**, **evidence**, **inference**, **gap**. Never substitute "endpoint," "dependency," "boundary," or "unknown."

## Input

The user provides: $ARGUMENTS

- First argument: feature name or topic
- Remaining arguments (optional): focus areas (e.g. auth, deployment, data flow)
- Output path: `docs/<feature_name>/discovery.html` (HTML default; `discovery.md` for the Markdown swap)

If no argument is provided:

- Look in `docs/` for directories containing `spec.md`
- If exactly one exists, use it as the feature name
- If several exist, list them and ask which one
- If none exist, ask for a feature name

If the feature name is not a clean snake_case slug, derive a sensible one and tell the user what path you used.

## Phase 1 — Sweep

Walk the codebase and build an evidence inventory. Every claim must cite a file path or be labelled as an **Inference**. Collect before you synthesise.

Work from the outside in. Label inferences as you go — every claim that lacks a direct file-path citation gets an `Inference:` prefix and a note of which evidence it was derived from.

1. **Find surfaces** — HTTP handlers, queue consumers, cron jobs, CLIs, webhooks. These are the entry and exit points. Start here: `README.md`, `package.json` / `Cargo.toml` / `pyproject.toml`, Dockerfiles, deployment manifests.
2. **Trace flows** — follow each surface inward. What does it call? What state does it touch? Where does it end?
3. **Identify integrations** — external systems: databases, queues, APIs, auth providers, object stores. Look at env var names, ORM config, client initialisations.
4. **Locate trust boundaries** — where does the system validate, authenticate, or sanitise incoming data? Absent trust boundaries are themselves a discovery.

If the repo has more than one obvious subsystem, or if the sweep would need to inspect more than one major surface, you must delegate part of the sweep to the Explore subagent before synthesising. Do not continue to Phase 2 until the subagent sweep returns. If you choose not to use a subagent, record why the repo is small enough that a single-pass sweep is sufficient.

Subagent check: at least one exploration task must be delegated for any repo with multiple surfaces, multiple integrations, or more than about ten relevant files.

At the end of the sweep, build a **confidence inventory**: for each section (surfaces, flows, integrations, trust boundaries), rate confidence as High, Medium, or Low using the definitions in [GLOSSARY.md](GLOSSARY.md).

## Phase 2 — Report

Write a self-contained HTML file to `docs/<feature_name>/discovery.html`. Create the `docs/<feature_name>/` directory if it doesn't exist. See [HTML-REPORT.md](HTML-REPORT.md) for the scaffold, diagram patterns, and styling.

**Markdown swap:** for a PR diff, a fresh LLM session, or a repo that shouldn't carry HTML, write `docs/<feature_name>/discovery.md` instead following [MARKDOWN-REPORT.md](MARKDOWN-REPORT.md). Same sections, same Mermaid, no CSS or SVG — just prose, tables, and fenced blocks that stay digestible for both a human reader and another LLM.

Either way the full range of Mermaid diagram types is available; pick the one that matches the shape of what you're describing rather than forcing everything into a flowchart.

Print the absolute path. Open the HTML report (`xdg-open` on Linux, `open` on macOS, `start` on Windows); for the Markdown swap the path alone is enough since it's meant to be read as text.

The report must contain:

- **Header** — feature name, codebase, date, and a confidence summary table (surfaces / flows / integrations / trust boundaries)
- **System map** — one Mermaid diagram giving the whole system at a glance; default to a `flowchart` with Surfaces / Subsystems / Integrations subgraphs, or another catalogue type if it fits better
- **Flows** — one section per key flow with a Mermaid `sequenceDiagram` (or `stateDiagram-v2` for a state machine), confidence badge, surface citation, exit line, and inference callouts
- **Integrations** — compact table: name, type, evidence file path, confidence
- **Trust boundaries** — one block per boundary; absent boundaries noted as a gap
- **Gaps** — ranked list, highest impact × uncertainty first, each naming exactly what is missing

After writing the report, do not ask what to do next. Proceed directly to Phase 3.

## Phase 3 — Gap Loop

Score each gap: **impact × uncertainty**. Impact = how much resolving this gap would change the discovery. Uncertainty = how weak the current evidence is.

Surface the single highest-scoring gap. Provide your best current answer or hypothesis before asking — the user should be able to confirm or correct, not just answer from scratch. Ask one question at a time — never list them all.

If the question can be resolved by exploring the codebase, explore it instead of asking the user.

After each answer or exploration:

- Update your understanding
- If the gap is resolved, mark it as closed and move to the next highest-scoring gap
- If a new inference surfaces, score it and insert it into the ranked list

When all High and Medium impact gaps are resolved, offer to re-render the report — in whichever format it was written — with resolved gaps struck through and new findings incorporated. Then stop.

## Rules

- Every claim is evidence (cited file path) or an **Inference** (labelled with its basis).
- Use glossary terms exactly. Never drift into synonyms.
- Discovery only — do not propose refactors or implementations.
- Prefer one useful overview over many decorative diagrams.
- Diagrams are Mermaid in both formats; the HTML report may add hand-built SVG/CSS visuals, the Markdown swap stays Mermaid-only. Pick the Mermaid diagram type that fits the structure; the full catalogue is in [MARKDOWN-REPORT.md](MARKDOWN-REPORT.md).
- Validate Mermaid syntax before writing (quote labels that contain spaces or special characters).
- Absent trust boundaries are a finding, not a gap to skip.
