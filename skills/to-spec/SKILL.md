---
name: to-spec
description: "Turn the current conversation and the change's intent.html into spec.html: no interview, just synthesis of what you've already discussed."
disable-model-invocation: false
---

This skill takes the current conversation context, the change's intent, and codebase understanding and produces a requirements and design spec as `spec.html`. Do NOT interview the user; just synthesize what you already know.

Read [../sdlc/ARTIFACTS.md](../sdlc/ARTIFACTS.md) before writing. It sets where the file goes, its format, and how to use diagrams.

## Process

1. Find the change. If `changes/<slug>/intent.html` exists, read it: the spec answers that intent. If the user passes a different source (a ticket, a document), read it in full. With no intent, the conversation is the source and you pick the slug.

2. Explore the repo to understand the current state of the codebase, if you haven't already. Use the project's domain glossary vocabulary throughout the spec, and respect any ADRs in the area you're touching.

3. Apply the organisation's policies. Load every available skill that encodes a policy relevant to the change (security, compliance, brand, UX) and hold the spec to it. Where two policies contradict each other, or the intent cannot be met within a policy, record it under **Areas of concern** rather than choosing silently.

4. Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

Check with the user that these seams match their expectations.

5. Write `changes/<slug>/spec.html` with the sections of the template below, in order. Set `<meta name="artifact" content="spec">` and link to `intent.html`.

6. Commit it, per ARTIFACTS.md. Tell the user the next step: plan mode, then `/to-plan`.

<spec-template>

## Problem Statement

The problem that the user is facing, from the user's perspective.

## Solution

The solution to the problem, from the user's perspective.

## User Stories

A LONG, numbered list of user stories. Each user story should be in the format of:

1. As an <actor>, I want a <feature>, so that <benefit>

<user-story-example>
1. As a mobile bank customer, I want to see balance on my accounts, so that I can make better informed decisions about my spending
</user-story-example>

This list of user stories should be extremely extensive and cover all aspects of the feature.

## Implementation Decisions

A list of implementation decisions that were made. This can include:

- The modules that will be built/modified
- The interfaces of those modules that will be modified
- Technical clarifications from the developer
- Architectural decisions
- Schema changes
- API contracts
- Specific interactions

Do NOT include specific file paths or code snippets. They may end up being outdated very quickly.

Exception: if a prototype produced a snippet that encodes a decision more precisely than prose can (state machine, reducer, schema, type shape), inline it within the relevant decision and note briefly that it came from a prototype. Trim to the decision-rich parts, not a working demo, just the important bits.

## Testing Decisions

A list of testing decisions that were made. Include:

- A description of what makes a good test (only test external behavior, not implementation details)
- Which modules will be tested
- Prior art for the tests (i.e. similar types of tests in the codebase)

## Areas of Concern

Every policy conflict, every place the intent cannot be met within a policy, and every risk the product owner should route to a policy owner before engineering starts. Name the policy each concern comes from. If there are none, say which policies were applied.

## Intent's Open Questions

Each open question from `intent.html`, and whether the spec answers it (with the answer) or carries it forward (with who decides). Omit this section when there is no intent.

## Out of Scope

A description of the things that are out of scope for this spec.

## Further Notes

Any further notes about the feature.

</spec-template>
