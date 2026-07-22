---
name: dev-wiki
description: Query the user's dev-wiki when they explicitly ask to use their dev-wiki or personal developer wiki, including by supplying its path. Apply its read-only boundary to explicit mutation requests; do not invoke for general repository or web research.
---

# Dev wiki query

Use the dev-wiki as a read-only knowledge source. This skill contains retrieval behaviour only, not domain knowledge.

## Resolve and validate the root

Choose exactly one candidate in this precedence order:

1. A dev-wiki root path explicitly supplied in the current user request.
2. The non-empty `DEV_WIKI_ROOT` environment variable.
3. `/Users/jonny/dev/dev-wiki`.

Expand `~` in a supplied path, but do not search the filesystem or inspect the current repository to discover alternatives. Validate the selected candidate before reading content: `<root>/index.md` must be a file and `<root>/wiki/` and `<root>/raw/` must be directories. If any check fails, name the failed candidate and missing entries, ask for a valid root, and stop. Do not silently fall through to a lower-precedence candidate.

## Query protocol

1. **Route from the root index.** Read `<root>/index.md` first. Select only categories relevant to the question; do not scan the whole wiki.
2. **Narrow through the category index.** Follow the selected category link to its index and use its summaries and dates to choose the smallest relevant page set. If the root index links directly to a page, treat that direct link as the routing result rather than inventing a category index.
3. **Inspect page shape before prose.** For each selected page, read its frontmatter and headings first. Use metadata such as `summary`, `updated`, `status`, `sources`, and `tags` for relevance, freshness, and provenance. Then read only the sections needed to answer the question, following relevant internal links when required.
4. **Consult raw material only when needed.** Read narrowly within `<root>/raw/` only to resolve an ambiguity, verify a detail material to the answer, investigate an apparent contradiction, or fill a gap that a selected page explicitly points toward. Do not browse raw material speculatively or inspect unrelated repositories or working copies.
5. **Synthesize, do not merely quote.** Give a direct answer supported by the retrieved material. Every substantive conclusion must have an inline citation to a root-relative wiki or raw path and the relevant heading or line range. Clearly distinguish sourced facts from inference.
6. **Disclose evidence quality.** Surface stale, draft, deprecated, or otherwise qualified page status and relevant `updated` dates. If sources disagree, cite both and describe the contradiction without silently choosing one. State unresolved uncertainty and missing coverage; never fill a gap from model memory.

## Read-only boundaries

- Do not create, edit, move, or delete anything in the dev-wiki through this skill.
- Do not compile, refresh, re-index, restamp, health-check, or otherwise maintain the wiki.
- Do not read or write `log.md` or other maintenance/activity logs, and do not create logs.
- Do not stage or commit files, run mutating Git commands, or alter raw material.
- Do not use web research or external sources to supplement the wiki.
- Do not inspect the caller's repository, adjacent repositories, or unrelated files as evidence.
- Do not present model memory, assumptions, or uncited general knowledge as dev-wiki knowledge.
- If the user asks to update or maintain the wiki, explain that this adapter is query-only and do not perform the mutation as part of this skill.

## Answer contract

Lead with the answer. Cite substantive claims inline using root-relative paths, for example `wiki/<category>/<page>.md § <heading>` or `raw/<path>:<lines>`. End with a short **Evidence quality** section whenever any source is stale or qualified, raw evidence was needed, sources conflict, or the wiki leaves uncertainty or gaps. State explicitly when the wiki does not support an answer.