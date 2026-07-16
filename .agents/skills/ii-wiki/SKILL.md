---
name: ii-wiki
description: "Answer architecture and work-scoping questions about DYWIDAG's Infrastructure Intelligence platform across its multi-repository application estate. Resolve the infrastructure-intelligence-wiki checkout relative to the current repository, use its wiki as the knowledge map, and verify relevant facts against its repository clones. Use when the user asks how an Infrastructure Intelligence application or service works, which repositories a change touches, where a contract or data flow lives, or how to scope work across the platform before building."
---

# Infrastructure Intelligence platform query

Answer questions about DYWIDAG's Infrastructure Intelligence platform: the complete
estate of applications, services, shared libraries, device software, and tooling
spread across roughly 25 repositories. Use the **II Wiki** repository,
`infrastructure-intelligence-wiki`, as the retrieval map. Its `wiki/` directory holds
the derived understanding and `raw/repos/<slug>/` holds the wiki's own clones of the
source repositories. This skill is the complete query protocol; do not load the wiki
repository's `AGENTS.md`, `.claude/`, or any source repo's `AGENTS.md`/`CLAUDE.md`
files just to answer platform questions.

## Locate the II Wiki

The II Wiki's Git repository is named `infrastructure-intelligence-wiki`. Resolve its
location from the current checkout; never assume a user-specific absolute path. The
normal layout places it beside the repository where Codex is working:

```text
<repositories-directory>/
├── <current-repository>/
└── infrastructure-intelligence-wiki/
```

Run this lookup before reading the wiki. It checks the current repository itself,
then the expected sibling location, then repeats from each ancestor to support
repositories opened through a nested worktree directory:

```sh
start="$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)"
cursor="$start"
wiki_root=""

while [ -n "$cursor" ]; do
  if [ "$(basename "$cursor")" = "infrastructure-intelligence-wiki" ]; then
    candidate="$cursor"
  else
    candidate="$(dirname "$cursor")/infrastructure-intelligence-wiki"
  fi

  if [ -f "$candidate/wiki/index.md" ] && [ -d "$candidate/raw/repos" ]; then
    wiki_root="$candidate"
    break
  fi

  parent="$(dirname "$cursor")"
  [ "$parent" = "$cursor" ] && break
  cursor="$parent"
done
```

Use `wiki_root` as `<wiki-root>`. If it is empty, ask the user where
`infrastructure-intelligence-wiki` is checked out; do not guess an obsolete path or
search the entire machine.

## The one rule

**The wiki is the map; the repos are the territory.** Use the wiki to find the
smallest relevant article set, then verify the facts that matter in the live code
under `<wiki-root>/raw/repos/<slug>/`. Never answer a factual architecture, contract,
endpoint, schema, package, config, or data-flow question from the wiki alone.
Articles carry `verified: true|false`; treat `verified: false` as a hypothesis until
checked.

## Query workflow

1. **Start at the wiki index.** Read `<wiki-root>/wiki/index.md` first. It is the
   retrieval substrate: cross-cutting articles explain estate-wide flows,
   repo-container pages describe repo-level shape, and application pages describe
   deployable runtime boundaries.
2. **Select only relevant articles.** Use the index links and `rg` over
   `<wiki-root>/wiki/` to gather the narrow article set needed for the user's
   question. Prefer article frontmatter over prose for routing: `type`, `repos`,
   `verified`, `seed_commit`, `seed_branch`, `covered_paths`, `tags`, and `related`.
3. **Traverse from map to code.** For each selected article, use its `repos` and
   `covered_paths` to jump into `<wiki-root>/raw/repos/<slug>/`. If a repo-container
   page points to application pages, follow the application page before reading code
   unless the question is explicitly repo-level.
4. **Verify only the needed facts.** Read the narrow code, config, project, schema,
   pipeline, or infrastructure files that prove the answer. Use `rg` and targeted
   file reads; avoid broad repo scans. If `<wiki-root>/raw/repos/` is empty or
   missing, ask the user to populate the II Wiki clones before answering.
5. **Report evidence and drift.** Answer with citations to both wiki article paths
   and live code paths. Include the article verification status and the repo commit
   when available. If the wiki and code disagree, say which fact drifted and prefer
   the code for current behaviour.

## Boundaries

- **Query only by default.** Maintaining the wiki (compile, verify-and-upgrade,
  re-index, health-check, commit) is the librarian's job. Do not compile,
  decompose, restamp, file answers, or mutate wiki articles unless the user asks.
- **Never confuse in-progress work for how the platform works.** Read only
  `<wiki-root>/raw/repos/`, never adjacent feature-branch working copies of the
  application repositories.
- **Do not load repo instruction files as domain evidence.** `AGENTS.md`, `CLAUDE.md`,
  and `.claude/` files describe agent behaviour, not the Infrastructure Intelligence
  platform. Skip them unless the user explicitly asks about the II Wiki maintenance
  workflow or agent setup.
- **Keep token use proportional.** The expected path is index -> relevant wiki
  article(s) -> relevant `raw/repos/<slug>/` files, not index -> whole wiki -> whole
  repo.
