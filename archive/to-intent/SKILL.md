---
name: to-intent
description: "Turn the current conversation into intent.html, the proto-spec that starts a change: no interview, just synthesis of what you've already discussed."
disable-model-invocation: true
---

This skill takes the current conversation and writes it up as `intent.html`: what the originator wants, why, and under which constraints, in the originator's own terms. Do NOT interview the user; synthesize what you already know. The conversation is usually a `/grilling` session; it may also start from a ticket or an incident the user passes as an argument, which you read in full first.

Read [../sdlc/ARTIFACTS.md](../sdlc/ARTIFACTS.md) before writing. It sets where the file goes, its format, and how to use diagrams.

## Process

1. **Pick the change.** Choose the slug and say it once so the user can rename it.

2. **Write `changes/<slug>/intent.html`** with the sections below, in order. Set `<meta name="artifact" content="intent">` and `<meta name="status" content="draft">`.

   An intent says **what** and **why**, never **how**. Implementation design belongs to the spec. Keep the originator's vocabulary: an intent from a claims handler reads like a claims handler wrote it.

   Where the conversation left a section thin, say so under **Open questions** rather than filling the gap yourself. An invented constraint here becomes a requirement in the spec.

3. **Hand it back for correction.** Tell the user the path, and ask them to read it and correct anything misunderstood. Apply their corrections. The step is done when the user confirms the intent says what they meant.

4. **Commit it**, per ARTIFACTS.md. Tell the user the product owner reviews it next, and `/to-design` follows once it is accepted.

<intent-sections>

## Title

`Intent: <the change in a few words>`, in the `<h1>` and the `<title>`.

## Author and status

Who originated the change (name and role), the date, and the status: `draft` until the product owner accepts it.

## Problem

The problem, from the perspective of the people who have it. Include whatever evidence the conversation produced: how often, how costly, who said so.

## Proposed outcome

What is true once the change is done, described as an outcome the originator would recognise, not as a feature list.

## Affected users and systems

The people whose work changes and the systems the change touches.

## Constraints

Limits the change must respect: data, security, cost, time, existing systems.

## Open questions

Everything still undecided, and every section above the conversation did not fully support.

</intent-sections>
