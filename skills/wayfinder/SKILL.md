---
name: wayfinder
description: Plan a huge chunk of work (more than one agent session can hold) as one map of open questions, and resolve them one at a time into one answer key until the way to the destination is clear.
disable-model-invocation: true
---

A loose idea has arrived, too big for one agent session, and wrapped in fog: the way from here to the **destination** isn't visible yet. Wayfinding is about finding that way, not charging at the destination. This skill charts the way as a **map** of open questions (questions whose resolution is a decision, not slices of a build to execute), then works them one at a time, recording each answer in a single **answer key**, until the route is clear.

An effort is exactly **two files**, written next to each other in a directory named for the effort:

- `map.md` — where you're going and what's still open.
- `answer-key.md` — what's been settled.

Nothing else is produced. A question is not a file, a ticket, or an issue; it's an entry in the map that moves to the answer key once it's answered. Two reads load the whole effort, and moving a question along is one edit to each file.

The destination varies per effort, and naming it is the first act of charting: it shapes every question. It might be a spec to hand off and iterate on, a decision to lock before planning starts, or a change made in place like a data-structure migration. The map is domain-agnostic: engineering work, course content, whatever fits the shape.

## Plan, don't do

Wayfinder is **planning** by default: each question resolves a decision, and the map is done when the way is clear, with nothing left to decide before someone goes and does the thing. The pull to just do the work is usually the signal you've reached the edge of the map and it's time to hand off. An effort can override this in its **Notes**, carrying execution into the map itself, but absent that, produce decisions, not deliverables.

## The two files

The split is by state, not by detail: the map holds only what's still open, the answer key only what's settled. A question lives in exactly one of the two, never both, so a decision is recorded in exactly one place and the map can't drift out of date. Resolving a question _is_ the move from the one to the other.

Load the map every session, before choosing a question. Load the answer key when prior decisions bear on the question in hand, which is most sessions: keep each answer tight so the key stays loadable for the life of the effort.

Refer to a question by its **name** — its heading — in everything the human reads. The name is the question's identity, carried unchanged from the map into the answer key, so renaming it orphans its answer.

### `map.md`

The whole live effort at low resolution, loaded once per session.

```markdown
# <effort name>

## Destination

<what reaching the end of this map looks like: the spec, decision, or change this effort is finding its way to. One or two lines; every session orients to it before choosing a question.>

## Notes

<domain; skills every session should consult; standing preferences for this effort>

## Open questions

<!-- every question still to answer, frontier first; see "Questions". An answered question is deleted from here -->

### <question name>

- Type: grilling
- Blocked by: <question name>, <question name>
- Claimed: <dev>

<the decision or investigation this question resolves, in a line or two>

## Not yet specified

<!-- see "Fog of war": in-scope fog you can't phrase as a question yet; graduates as the frontier advances -->

## Out of scope

<!-- see "Out of scope": work ruled beyond the destination; never graduates -->
```

### Questions

Each question is one entry under **Open questions**, sized to one 100K token agent session, carrying three fields:

- **Type**: one of `research`, `prototype`, `grilling`, `task` (see [Question Types](#question-types)).
- **Blocked by**: the names of the questions that must be answered first. A question is **unblocked** when every name it lists is in the answer key. Omit the field when nothing blocks it.
- **Claimed**: the dev driving the question, written **first**, before any work, so a concurrent session skips it. No `Claimed` field means unclaimed.

The **frontier** is the open, unblocked, unclaimed entries: the edge of the known. Keep **Open questions** ordered frontier first, so the frontier reads off the top of the map without a search.

The answer isn't part of the entry; it's recorded in the answer key on resolution (see [Work through the map](#work-through-the-map)). Assets created while resolving a question are linked from the answer, not pasted in.

### `answer-key.md`

One entry per answered question, in the order they were answered, each under the question's unchanged name:

```markdown
# <effort name> — answer key

### <question name>

<the answer in one line: the decision, or the fact that was found>

<the detail behind it: what was decided and why, what was ruled out, links to any assets>
```

The one-line answer comes first, so a session skimming the key can judge relevance without reading every entry.

## Question Types

Every question is either **HITL** (human in the loop, worked _with_ a human who speaks for themselves) or **AFK**, driven by the agent alone. A HITL question only resolves through that live exchange; the agent never stands in for the human's side of it (a grilling agent that answers its own questions has broken this).

- **Research** (AFK): Reading documentation, third-party APIs, or local resources like knowledge bases to surface a fact a decision waits on. Resolved by a subagent that calls the Skill tool with "research". Use when knowledge outside the current working directory is required.
- **Prototype** (HITL): Raise the fidelity of the discussion by making a cheap, rough, concrete artifact to react to (an outline, a rough take, a stub, or UI/logic code) by calling the Skill tool with "prototype". Links the prototype as an asset. Use when "how should it look" or "how should it behave" is the key question.
- **Grilling** (HITL): Conversation. The default case. Always call the Skill tool twice, for "grilling" and "domain-modeling".
- **Task** (HITL or AFK): Manual work that must happen before a _decision_ can be made: nothing to decide, prototype, or research, but the discussion is blocked until it's done. Signing up for a service so its API can be judged, provisioning access, moving data so its shape can be seen. This is the one type that _does_ rather than decides, and it earns its place by unblocking a decision, not by delivering the destination. The agent drives it alone where it can (AFK); otherwise it hands the human a precise checklist (HITL). Resolved when the work is done; the answer records what was done and any resulting facts (credentials location, new URLs, row counts) later questions depend on.

## Fog of war

The map is _deliberately_ incomplete: don't chart what you can't yet see. Beyond the open questions lies the **fog of war**: the dim view of decisions and investigations you can tell are coming but can't yet pin down, because they hang on questions still open. Answering a question clears the fog ahead of it, graduating whatever's now specifiable into fresh questions, one at a time, until the way to the destination is clear and no open questions remain.

The map's **Not yet specified** section is where that dim view is written down: the suspected question, the area to revisit later. It's the undiscovered frontier _toward_ the destination: everything here is in scope, just not sharp enough to write as a question. Write as loosely or as fully as the view allows; it doubles as a signpost for collaborators reading where the effort is headed.

**Fog or question?** The test is whether you can state the question precisely now, _not_ whether you can answer it now.

- **A question when** it's already sharp, even if it's blocked and you can't act on it yet.
- **Not yet specified when** you can't yet phrase it that sharply. Don't pre-slice the fog into question-sized pieces: it's coarser than a question, and one patch may graduate into several questions, or none, once the frontier reaches it.

**Not yet specified** excludes what's already answered (the answer key), what's already an open question, and what's out of scope (the next section).

## Out of scope

Fog only ever gathers _toward_ the destination. The destination fixes the scope, so work beyond it is **out of scope**: it isn't fog, and it doesn't belong in **Not yet specified**. It gets its own **Out of scope** section on the map: work you've consciously ruled out of _this_ effort. Scope, not sharpness, lands it here.

Out-of-scope work never graduates (the frontier stops at the destination), so it returns only if the destination is redrawn, and then as a fresh effort, not a resumption.

Ruling something out of scope is a scoping act, not a step on the route. When an open question turns out to sit past the destination (mis-scoped in while charting, or exposed by an answer), **delete it from Open questions** and leave one line in the **Out of scope** section: the gist plus why it's out of scope. It never enters the answer key, which records the route actually walked; a scope boundary isn't a step on it.

## Invocation

Two modes. Either way, **never resolve more than one question per session**, with the exception of research questions.

### Chart the map

User invokes with a loose idea.

1. **Name the destination.** Call the Skill tool twice, for "grilling" and "domain-modeling", to pin down what this map is finding its way to: the spec, decision, or change. The destination fixes the scope, so it's settled first.
2. **Map the frontier.** Grill again, **breadth-first** this time: fan out across the whole space rather than deep on any one thread, surfacing the open decisions and the first steps takeable now. **If this surfaces no fog** (the way to the destination is already clear, the whole journey small enough for one session), you don't need a map. Stop and ask the user how they'd like to proceed.
3. **Write the two files.** `map.md` with Destination and Notes filled in, every question you can specify now under **Open questions** with its `Type` and `Blocked by` fields and no `Claimed` field, frontier first, and the rest of the fog sketched into **Not yet specified**; `answer-key.md` alongside it, holding its title and nothing else. Ask the user where the pair should live if they haven't said; absent an answer, put them in a directory named for the effort.
4. **Fire the research subagents.** For each `research` question, spin up a subagent that calls the Skill tool with "research" to resolve it in parallel. Each subagent **reports back** rather than writing to either file; **this** session writes their answers into the answer key and deletes those questions from the map, so both files keep a single writer and parallel subagents never clobber each other.
5. Stop: charting is one session's work; beyond research it hand-resolves nothing.

### Work through the map

User invokes with a map. A question is **optional**: without one, you pick the next decision, not the user.

1. Read `map.md`: the low-res view of the whole live effort.
2. Choose the question. If the user named one, use it. Otherwise take the first frontier entry: unblocked (every `Blocked by` name is in the answer key) and unclaimed. **Claim it**: add `Claimed: <dev>` to its entry and save the map before any work.
3. Resolve it. Read `answer-key.md` for the decisions already made, and open any asset an answer links on demand; call the Skill tool for whichever skills the `## Notes` block names. If in doubt, call the Skill tool twice, for "grilling" and "domain-modeling".
4. **Move the question.** Append its answer to `answer-key.md` under its unchanged name, then delete its entry from the map's **Open questions**. Both writes belong to this session: a question in neither file is lost, a question in both is ambiguous.
5. Add newly-surfaced questions to **Open questions**; graduate any fog the answer has made specifiable, clearing each graduated patch from **Not yet specified** so it lives only as its question. If the answer reveals that a question (this one or another) sits beyond the destination, **rule it out of scope** rather than answering it on the route. If the answer invalidates other open questions, edit or delete them; if it invalidates an earlier answer, edit that answer key entry in place, never leaving two answers under one name.

The user may run unblocked questions in parallel, so expect other sessions to be editing both files concurrently. Re-read a file immediately before writing it, and keep each write small and separate (the claim, then the answer, then the deletion), so a concurrent session's edit isn't overwritten.
