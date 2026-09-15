# Techniques

The seven techniques [`know-your-unknowns`](SKILL.md) owns, grouped by phase. Run the one the picker chose. Every technique obeys the rules in the skill: one HTML artifact, grounded in the repo, ending in a round trip.

The other four rows of the picker belong to `teach`, `prototype`, and `grilling`.

---

## Pre-implementation

The cheapest phase. An unknown found here costs a paragraph; the same unknown found after merge costs a rewrite.

### Blindspot pass

*You're about to change code you don't know.*

Read the module and its callers first — the pass is only as good as the reading behind it. Then produce a **card per blindspot**, five to eight of them, each carrying:

- The assumption a naive implementation would make.
- What is true instead, with the file and line that proves it.
- The **fix**: a copyable sentence to add to the implementation prompt.

Rank the cards by what they'd cost to discover later, not by how interesting they are. The artifact ends with the accepted fixes assembled into one improved implementation prompt, ready to paste.

### Brainstorm the intervention

*The goal is agreed, the move isn't.*

Produce around ten interventions that would move the metric, every one grounded in code that exists. Plot them on two axes the user can see: **effort**, from ship-this-afternoon to quarter-long bet, and **blast radius**, from one file to a cross-cutting change.

Include the options you expect to lose. A field of ten where two are obviously right tells the user more than three plausible ones, because it shows the edges. Each option carries a *resonates* checkbox; checking assembles the user's reply.

### Point at a reference

*You're porting or copying an implementation.*

Words run out when the user can just point at working code. Before writing a line of the port, prove you read it. The artifact is a **semantics map**:

- Source excerpt beside target excerpt, matched construct by construct.
- A gotcha note wherever the two languages or frameworks diverge.
- An edge-case table: input, what the reference does, what your port will do.

Hand it over and wait. A correction here is free; the same correction after the port is a rewrite.

### The tweakable plan

*The plan is ready but parts of it will move.*

Order the plan by **likelihood of tweaking**, not by execution order. A plan sorted by execution buries the schema choice on line 200, where the user agrees to it by exhaustion.

- Top: the decisions that will change — schema shape, type interfaces, the boundary between modules — each with its alternatives as live toggles and a line on what flips if you switch.
- Middle: the annotated interfaces, so the user reads the contract rather than the steps.
- Bottom, collapsed: the mechanical work. It is real, and nobody needs to review it.

The export hands back the plan with the user's toggles resolved.

---

## During implementation

However good the plan, the territory argues back. Capture it while it happens; the detail is gone by the retro.

### Implementation notes

*You're mid-build and the code keeps arguing back.*

Keep a running log through the build. One entry per **deviation**, written at the moment it happens:

- What the plan assumed.
- What the code forced instead, with the file.
- The call you made, and whether it was the conservative one.

Close the log with the three bullets that would make attempt #2 go straight — the ones worth folding into the plan, the spec, or `CONTEXT.md`. Those three are the deliverable; the log is the evidence.

---

## Post-implementation

Shipping hands your unknowns to other people.

### The buy-in doc

*The change needs other people to say yes.*

Lead with the change working — a demo, a before/after, the thing itself — before any prose. Then answer each objection a reviewer was about to raise, one section each, with the evidence that settles it. Close by naming **who signs off on what**: a person, a question, and what happens if they say no.

Write for the reviewer who has ten minutes and did not read the ticket.

### Quiz me before I merge

*The diff is large and about to merge.*

A merge-readiness report over the diff — what changed, where the risk sits, what to look at — ending in **six questions the reader must pass**. Ask about the consequences a skimmer would miss: what breaks if this config is absent, which caller now gets a different type, what the migration does to existing rows.

A wrong answer links back to the exact section that answers it. Passing is the gate; the artifact says so plainly.
