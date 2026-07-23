# Markdown Report Format

The default format for a research write-up — a single Markdown file saved where the repo already keeps such notes (match the existing convention; if there is none, pick somewhere sensible and say where). Markdown keeps the findings readable in any editor, in a PR diff, or on GitHub, and digestible by another LLM with no rendering layer to strip out. Every claim carries its source.

For a shareable, visual read — a briefing for a human who won't open the repo — follow [HTML-REPORT.md](HTML-REPORT.md) instead.

## Document skeleton

```markdown
# Research — {{question}}

`{{scope / what prompted this}}` · {{DD Mon YYYY}}

## Question

One or two lines: exactly what was asked, and any scope boundaries.

## Answer

The bottom line first — the direct answer to the question in 2–4 sentences,
each load-bearing claim carrying an inline citation.

## Findings

### {{sub-question or theme}}

The finding, stated plainly. Every claim is followed by its source:

- Claim about behaviour. [^1]
- Another claim, with the specific detail that matters. [^2]

> **Uncertainty:** where the sources disagree, are silent, or are dated —
> name it rather than papering over it.

## Sources

[^1]: {{title}} — {{URL or `path:line` for source code}}. Primary: official docs / spec / first-party source.
[^2]: {{title}} — {{URL}}. Accessed {{date}}; version {{X}} if the answer is version-sensitive.
```

## Conventions

**Answer first.** Lead with the direct answer, then the findings that support it. A reader who wants only the conclusion should get it in the first section.

**Every claim cites its source.** Use Markdown footnotes (`[^1]`) or inline links — match whatever the repo's existing notes use. A claim without a citation is an inference and must be labelled as one.

**Primary sources only.** Official docs, specs, source code, first-party APIs — not a secondary write-up. Follow every claim back to the source that owns it, and note in the source line when something is primary vs secondary.

**Source code citations** render as inline code with a line anchor: `` `src/foo.ts:42` `` or `` `owner/repo@sha:path/to/file.rs:88` `` for an external repo at a pinned revision.

**Version and date sensitivity.** When the answer depends on a library/API version or could drift, record the version and the access date in the source line, so a future reader knows when to re-check.

**Uncertainty is a finding.** Where sources conflict, are silent, or are stale, say so in a blockquote callout rather than smoothing it over. An honest "the docs don't specify X" is more useful than a confident guess.

## Tone

Plain English, concise, evidence-first. Lead with the conclusion, then the evidence. No hedging, no throat-clearing. If a claim isn't backed by a source you read, either find the source or label it an inference — never present it as established fact.
