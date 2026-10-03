---
name: to-design
description: "Turn an accepted intent.html into spec.html, a combined requirements and design spec held to the organisation's policy skills, with areas of concern flagged."
disable-model-invocation: true
---

This skill takes an accepted `intent.html` and writes `spec.html`: one combined requirements and design spec the engineering team can plan against, with areas of concern flagged. Requirements and design happen in this one pass, not as separate phases.

The intent is the source. Use the current conversation as well when there is one, but the skill must also work with none: its end state is a job that runs when an intent is accepted. Do NOT interview; where the intent leaves something undecided, the spec says so.

Read [../sdlc/ARTIFACTS.md](../sdlc/ARTIFACTS.md) before writing. It sets where the file goes, its format, and how to use diagrams.

## Process

1. **Read the intent.** Read `changes/<slug>/intent.html` in full. If there is no intent, stop and tell the user to run `/to-intent` first: the spec answers an intent.

2. **Read the codebase** the change touches, so the design fits what exists. Use the project's vocabulary and respect any ADRs in the area.

3. **Load the policies.** Load every available skill that encodes a policy relevant to the change: brand, security, compliance, UX, or any other the organisation has written. These are constraints on the spec, applied while writing it, not checked afterwards. Note each one's name and version (the commit of its skill file, where it is in Git) for **Policies applied**.

4. **Write `changes/<slug>/spec.html`** with the sections below, in order. Set `<meta name="artifact" content="spec">` and `<meta name="status" content="draft">`, and link to `intent.html`.

   Every requirement traces back to the intent's problem or proposed outcome. Where meeting the intent would break a policy, or two policies contradict each other, record it under **Areas of concern** rather than choosing silently. A concern is what an analyst would have escalated.

5. **Check it against the intent**, the way the product owner will: does the spec solve the stated problem, and does it answer or carry forward every open question from the intent? Fix any gap before handing it over.

6. **Commit it** next to the intent, per ARTIFACTS.md. Tell the user what happens next: the product owner reviews the spec, resolves each area of concern with its policy owner, and decides go or no-go, with a technical lead for higher-risk work. Acceptance starts plan mode, then `/to-plan`.

<spec-sections>

## Title

`Spec: <the change>`, with a link to `intent.html`.

## Requirements

What the change must do and the conditions it must meet, each traceable to the intent's problem, proposed outcome or constraints.

## Design

How the change fits the existing system: the components involved, how they interact, the data that moves between them, and what the user sees. Name modules and interfaces; leave file paths to the plan.

## Policies applied

Each policy skill loaded, with its version, and what it required of this spec.

## Areas of concern

Every policy conflict, every place the intent cannot be met within a policy, and every risk to route to a policy owner before engineering sees the spec. Name the policy each concern comes from, and its owner where the policy skill names one. If there are none, say so.

## Intent's open questions

Each open question from `intent.html`, and whether the spec answers it (with the answer) or carries it forward (with who decides).

</spec-sections>
