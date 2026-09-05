---
name: graph-spec
description: Turn a plain-language job into a paste-ready GRAPH SPEC prompt.
argument-hint: "What do you want the fleet to do?"
disable-model-invocation: true
---

# Graph Spec

The user describes a job in their own words. You return **one fenced block** they
paste into a fresh session. The deliverable is the prompt — this session produces
text only, and the fleet runs later, elsewhere, under the user's eye.

Two words carry the whole skill. A **fake edge** is two jobs running in order
only because they were typed in order. An **anchor** is a fact that cannot argue
back: a test that ran, a link that resolves, a number from outside the graph.

## 1. Find the shape

Name the **unit of work** — the thing there are many of (file, competitor,
angle, route, ticket, question). The unit is what fans out.

Then get, by inference or by one round of short questions, only what you cannot
guess: the scope boundary, the final artifact, and whether the user must approve
anything mid-run. Ask at most one round; assume defaults and state them.

Done when you can name the unit and say how many of it this run covers.

## 2. Run the fake-edge test

Walk the steps. For each arrow ask: **does this step read the output of the one
before it?** Yes → keep the edge. No → delete it; those jobs run at once.

Then check the fan-out for **hidden edges**: does any unit need another unit's
output before it can be graded? Every one you find goes in the block under
`HIDDEN EDGE`, named. An edge you found and did not write down is an edge the
fleet spends a round rediscovering.

Then count the **widest stage** — the most units that genuinely run together
once the edges are drawn. Carry that number to section 5. Below about four, work
out what the graph buys over a plain loop and carry that too, because a staged
plan presented as a fan-out costs fleet money for loop speed.

Done when every remaining arrow carries named data. If no two jobs are left
without an edge between them, the work is not wide: say so and hand back a
normal single-agent prompt. A loop is fine. Forcing a graph onto sequential work
buys cost, not speed.

## 3. Place the checker

Every finding crosses an independent verifier before it reaches the report, and
that verifier gets a **fresh context** — it reads the finding alone. A worker
sharing context with its checker is one loop grading its own homework.

Split the check by lens where the finding can fail more than one way: is it
correct, is it current, is the source real. Majority keeps it alive. Point each
lens at an **anchor** where one exists — "the test passes", not "the agent says
it passes".

Done when every finding has a verifier and every verifier has something to
check against.

## 4. Write the spec

Every spec is a **diamond**: fan out for breadth, reduce in plain code, verify
on fresh context, synthesize once. Emit exactly this shape, filled in. Drop the
fields the job does not need rather than leaving them blank.

```text
▸ GRAPH SPEC
GOAL: <one sentence, the finished artifact>

BAR:          <what the checker opens; the anchor it grades against>  (gauntlet)
ANCHORS:      <fixed numbers carried in that may not move>            (gauntlet)
FAN OUT:      <one agent per UNIT, in parallel>
HIDDEN EDGE:  <what a unit needs from another, and its verdict until then>
POINTERS:     <what each worker is handed as a path or link, never pasted>
RULE:         <the contract each worker returns — fields, sources, dates>
VERIFY:       <independent checker, fresh context, what it tries to kill>
REWORK:       <what a rejected unit carries back to a builder>        (gauntlet)
LOOP:         <what ends it — never a round count>                  (loop shapes)
DEDUPE:       <what counts as a duplicate>          (when finds can repeat)
MERGE:        <how the results become one thing>
CAP:          <hard limit on units / agents this run>
ON FAIL:      flag any unit that returns nothing, never skip it silently
REPORT:       <what lands in front of me, and how it is ranked>
SAVE:         <path>                                 (when files are written)
HUMAN GATE:   <what must not happen without asking me>

(start the prompt with the word "workflow" so Claude builds the graph)
```

`GOAL`, `FAN OUT`, `VERIFY`, `CAP`, `ON FAIL` and `REPORT` always appear. `BAR`,
`REWORK` and `LOOP` appear together or not at all — a rework edge with no bar is
a loop with no exit. `ANCHORS` is separate from `BAR`: the bar is where the rows
live, anchors are numbers that predate the work and may not be restated,
relaxed or recomputed. `HIDDEN EDGE` is dropped only when section 2 found no
edge; finding one and omitting it is the failure this field exists to stop. A
fleet burns tokens in proportion to its width, so `CAP` keeps the first run
cheap and `ON FAIL` keeps its report honest. `POINTERS` is the other half of
that arithmetic: every worker pays for what it is handed, so hand it the path
to the spec, the notes and the prior commits, never their contents. It appears
whenever more than about three workers read the same source.

Open [`PATTERNS.md`](PATTERNS.md), read every shape, and adapt the closest one.
Read its **Fixes** section in the same pass: those are repairs bolted onto a
spec that has the matching weakness. A real job usually takes one shape and
more than one fix, so do not stop at the first heading that matches.

Done when the block reads as instructions to a fleet, with no bracket left
unfilled.

## 5. Hand it over

Return the block in a fence, plus at most three lines: the assumptions you made,
the cap you chose, and the widest stage with what the graph buys over a plain
loop at that width. The width line is not optional — it is the only place the
hidden-edge finding of section 2 reaches the user.

Done when the user has a block they can paste with no edits.
