# Routing

The whole documentation architecture rests on **progressive disclosure**: a small always-loaded layer, rich enough to decide where to go, and detail that stays on disk until a routing line points at it. This is the same mechanism Agent Skills use — a `description` gates loading a `SKILL.md` body — copied onto plain files. Get the routing wrong and the deeper docs are dead weight nobody reads.

## Three tiers, each paid for only when the path is walked

1. **Tier 0 — always on:** the root `AGENTS.md`. The harness injects it every session; it's the only thing guaranteed loaded. Keep it small — invariants + the routing index, nothing else.
2. **Tier 1 — loaded when routed to:** a working target's `AGENTS.md`. Not auto-loaded; pulled in by an explicit read when a root routing line matches the task. Once loaded it's the local index for that target.
3. **Tier 2 — loaded on demand:** `domain.md`, a specific ADR, a convention doc — read when the target's own routing points at it.

Nothing below the root is paid for until a task walks the path to it. **The directory tree *is* the map**; each `AGENTS.md` is the local index for its level. There is no separate map file to maintain and no reader-rules file.

## What makes lazy loading actually fire

Routing is only as reliable as the trigger that gates it — the same lesson as a skill with a weak `description` that never activates.

- **Write routing lines as triggers, not labels.** State *when* to read the target, in task terms — "Working on the web app or any UI change → `web/AGENTS.md`" — not "web docs → `web/AGENTS.md`". The condition is what lets the agent match task → path.
- **Keep Tier 0 small.** "Always on" is a budget paid on every task. The root `AGENTS.md` earns its place with universal invariants + routing only; everything else sits behind a pointer.
- **ADR filenames *are* the index.** `docs/adr/` is a directory of many files, so its cheap index tier is the titled filenames: the agent lists them, then loads only the relevant bodies. This works only if filenames state the decision — `0002-use-utc-for-all-timestamps.md`, not `0002-adr.md`. Descriptive ADR filenames are a requirement, not a nicety.
- **Recurse.** Each target's `AGENTS.md` is its own Tier-0 index once loaded: instructions + a routing section to its `domain.md`, ADRs, and conventions. The shape never changes, only its content and reach.

## The always-on vs lazy test

Ask: *is this needed on every task, whatever path it takes?*

- **Yes → always-on.** Write it into the root `AGENTS.md`: the non-negotiable invariants (commit protocol, review loop, the standing read-rules) and the routing index itself.
- **No — only when the task touches area X → lazy.** Put it behind a routing line whose trigger names X: a target's conventions, vocabulary, decisions.

## The two core files are the exception

`domain.md` and `docs/adr/` recur in every substantial context, and *when* to read them is identical everywhere. So their trigger is hoisted into a standing rule in the root `AGENTS.md` (`read before you name`, `read before you decide`), and their routing line is just a bare *where*-pointer:

```markdown
- Vocabulary → docs/agents/domain.md (solution-wide terms → ../docs/agents/domain.md)
- Decisions → docs/adr/
```

Every other routing line carries its own trigger.
