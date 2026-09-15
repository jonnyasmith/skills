---
name: know-your-unknowns
disable-model-invocation: true
description: Find what you don't know about a piece of work before it costs you, using the cheapest technique for the phase you're in.
---

# Know your unknowns

The map is not the territory. The gap between how the work was planned and what the code actually does is the **unknowns**, and they surface either now, cheaply, or later, expensively. This skill buys one deliberately.

Sort by the quadrant before picking a technique — it decides which technique can even reach:

- **Known unknowns** — the questions already named. A direct answer reaches these: read the code, ask the user, run the thing.
- **Unknown knowns** — facts the user holds and hasn't said. An **interview** reaches these; the user cannot volunteer what they don't know you're missing.
- **Unknown unknowns** — the ones with no name yet. Only a **fan-out** reaches these: several options beside each other, a scan for blindspots, a prototype you can react to. Recognition is cheap where recall is impossible.

Unknown unknowns are where the cost is. Weight the pick towards them.

## Pick a technique

Find the row that matches the situation. Cost rises down the table.

| The situation | Technique | Where |
| --- | --- | --- |
| You're about to change code you don't know | Blindspot pass | [`TECHNIQUES.md`](TECHNIQUES.md) |
| The user lacks the vocabulary to say what they want | Teach me my unknowns | [`teach`](../teach/SKILL.md) |
| Nobody knows what good looks like yet | Four design directions | [`prototype`](../prototype/UI.md) |
| Placement or interaction is in doubt | Mock before you wire | [`prototype`](../prototype/UI.md) |
| The goal is agreed, the move isn't | Brainstorm the intervention | [`TECHNIQUES.md`](TECHNIQUES.md) |
| The request is ambiguous and the user is reachable | The interview | [`grilling`](../grilling/SKILL.md) |
| You're porting or copying an implementation | Point at a reference | [`TECHNIQUES.md`](TECHNIQUES.md) |
| The plan is ready but parts of it will move | The tweakable plan | [`TECHNIQUES.md`](TECHNIQUES.md) |
| You're mid-build and the code keeps arguing back | Implementation notes | [`TECHNIQUES.md`](TECHNIQUES.md) |
| The change needs other people to say yes | The buy-in doc | [`TECHNIQUES.md`](TECHNIQUES.md) |
| The diff is large and about to merge | Quiz me before I merge | [`TECHNIQUES.md`](TECHNIQUES.md) |

Two or more rows can fire. Run them one at a time, cheapest first, and stop as soon as the work is clear enough to start — the goal is a decision, not a full sweep.

When the work is a whole effort rather than one task — too big for a session, many decisions deep — [`wayfinder`](../wayfinder/SKILL.md) charts it instead.

## Rules for every technique

1. **Render it, don't write it up.** Each technique produces one self-contained HTML artifact — see [`html-artifact`](../html-artifact/SKILL.md). These outputs are option sets, maps, and tables; markdown flattens them into the wall of text the user will skim.
2. **End in a round trip.** The artifact's export button hands back a prompt, a decisions table, or a reply that goes straight into the next turn. The point of finding an unknown is acting on it in the same session.
3. **Show the question at the top.** State what this artifact is trying to find out, so a wrong target is visible before the user reads the whole thing.
4. **Ground every item in the repo.** Cite the file and the line that made you raise it. An invented risk costs the user the same attention as a real one and teaches them to discount the next artifact.
5. **Make it answerable by pointing.** Chips, checkboxes, toggles — the user reacts to concrete things. Open questions in prose return nothing.

## Done

The user has named at least one thing they didn't know before, and the artifact has handed back the text that acts on it.
