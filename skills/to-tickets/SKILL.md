---
name: to-tickets
description: Break a plan, spec, or the current conversation into a set of tracer-bullet tickets, each declaring its blocking edges, written as one HTML file per ticket under the change's tickets/ directory.
disable-model-invocation: false
---

# To Tickets

Break a plan, spec, or conversation into a set of **tickets**: tracer-bullet vertical slices, each declaring the tickets that **block** it.

Read [../sdlc/ARTIFACTS.md](../sdlc/ARTIFACTS.md) before writing. It sets where the files go, their format, and how to use diagrams.

## Process

### 1. Gather context

Work from whatever is already in the conversation context. Read the change's `plan.html` and `spec.html` under `changes/<slug>/` if they exist; the plan is the primary source when there is one. If the user passes a different reference as an argument, read it in full.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code. Ticket titles and descriptions should use the project's domain glossary vocabulary, and respect ADRs in the area you're touching.

Look for opportunities to prefactor the code to make the implementation easier. "Make the change easy, then make the easy change."

### 3. Draft vertical slices

Break the work into **tracer bullet** tickets.

<vertical-slice-rules>

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests): vertical, NOT a horizontal slice of one layer
- A completed slice is demoable or verifiable on its own
- Each slice is sized to fit in a single fresh context window
- Any prefactoring should be done first

</vertical-slice-rules>

Give each ticket its **blocking edges**: the other tickets that must complete before it can start. A ticket with no blockers can start immediately.

**Wide refactors are the exception to vertical slicing.** A **wide refactor** is one mechanical change (rename a column, retype a shared symbol) whose **blast radius** fans across the whole codebase, so a single edit breaks thousands of call sites at once and no vertical slice can land green. Don't force it into a tracer bullet; sequence it as **expand–contract**. First expand: add the new form beside the old so nothing breaks. Then migrate the call sites over in batches sized by blast radius (per package, per directory), each batch its own ticket blocked by the expand, keeping CI green batch to batch because the old form still exists. Finally contract: delete the old form once no caller remains, in a ticket blocked by every migrate batch. When even the batches can't stay green alone, keep the sequence but let them share an integration branch that all block a final integrate-and-verify ticket; green is promised only there.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each ticket, show:

- **Title**: short descriptive name
- **Blocked by**: which other tickets (if any) must complete first
- **What it delivers**: the end-to-end behaviour this ticket makes work

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Are the blocking edges correct: does each ticket only depend on tickets that genuinely gate it?
- Should any tickets be merged or split further?

Iterate until the user approves the breakdown.

### 5. Write the tickets

Write the approved tickets under `changes/<slug>/tickets/`, one file per ticket, never a single combined file:

- Name each file `<NN>-<ticket-slug>.html`, numbered from `01` in dependency order (blockers first), so a purely linear chain reads top to bottom.
- Use the ticket sections below, in order. Link each blocker to its file.
- Set these `<meta>` tags, so tooling can build the dependency graph without reading prose:

```html
<meta name="artifact" content="ticket">
<meta name="change" content="<slug>">
<meta name="status" content="ready-for-agent">
<meta name="blocked-by" content="01, 02">   <!-- ticket numbers; empty when none -->
```

Then write `changes/<slug>/tickets/index.html`: a dependency diagram of every ticket and its blocking edges (the one diagram this skill always draws), and a list linking each ticket file with its title and what it delivers.

The step is done when every approved ticket has a file, every file's `blocked-by` matches the approved breakdown, and the index links every ticket. Commit them, per ARTIFACTS.md.

<ticket-sections>

## Title

`<NN>: <Ticket title>`, in the `<h1>` and the `<title>`, with a link to the change's `plan.html` or `spec.html`.

## What to build

The end-to-end behaviour this ticket makes work, from the user's perspective, not a layer-by-layer implementation list.

## Blocked by

A link to each ticket that gates this one, or "None (can start immediately)".

## Acceptance criteria

A checklist of the observable conditions that make this ticket done.

</ticket-sections>

Avoid specific file paths or code snippets: they go stale fast. Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.
