---
name: research
description: Investigate a question against high-trust primary sources and capture the findings as a Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered, or reading legwork delegated to a background agent.
---

Spin up a **background agent** to do the research, so you keep working while it reads.

Its job:

1. Investigate the question against **primary sources** — official docs, source code, specs, first-party APIs — not a secondary write-up of them. Follow every claim back to the source that owns it.
2. Write the findings to a single file, citing each claim's source. Default to Markdown following [MARKDOWN-REPORT.md](MARKDOWN-REPORT.md) — cited notes that live in the repo and stay digestible for a human and another LLM. For a shareable, visual briefing for someone who won't open the repo, produce the HTML swap following [HTML-REPORT.md](HTML-REPORT.md) instead. If the user wants both, write the Markdown to the repo and the HTML to the temp dir.
3. Save the Markdown where the repo already keeps such notes; match the existing convention, and if there is none, put it somewhere sensible and say where.
