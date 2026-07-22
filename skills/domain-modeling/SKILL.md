---
name: domain-modeling
description: Build and sharpen a project's domain model. Use when the user wants to pin down domain terminology or a ubiquitous language, record an architectural decision, or when another skill needs to maintain the domain model.
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. This is the *active* discipline — challenging terms, inventing edge-case scenarios, and writing the glossary and decisions down the moment they crystallise. (Merely *reading* the glossary for vocabulary is not this skill — the repo's `AGENTS.md` standing rules already make every skill do that. This skill is for when you're *changing* the model, not just consuming it.)

## Where the model lives

You're already in a context (the repo root, or a working target within it), and its `AGENTS.md` routing has pointed you at that context's files. You don't need to reason about the tree:

- **Glossary** → `docs/agents/domain.md` for the context you're working in. Root holds solution-wide terms; a working target holds its inner terms and defers solution-wide ones upward.
- **Decisions** → `docs/adr/` for the context (root for system-wide, a target's for its internal ones).

Create files **lazily** — only when you have something to write, never scaffolded empty. If no `domain.md` exists, create it when the first term is resolved. If no `docs/adr/` exists, create it when the first ADR is needed.

**Making a new glossary reachable.** If you create the *first* `domain.md` for a nested working target that has no `AGENTS.md` of its own yet (an embryonic target), add a single in-route line to the parent's `AGENTS.md` routing section pointing at the new `domain.md` — otherwise nothing will find it. That one line is the only structural edit this skill makes; growing the target into a full `AGENTS.md` is `setup-repo-skills`' job, not yours.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `domain.md`, call it out immediately. "Your glossary defines 'cancellation' as X, but you seem to mean Y — which is it?"

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account' — do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible — which is right?"

### Update domain.md inline

When a term is resolved, update `domain.md` right there. Don't batch these up — capture them as they happen. Use the format in [DOMAIN-FORMAT.md](./DOMAIN-FORMAT.md).

`domain.md` should be totally devoid of implementation details. Do not treat `domain.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse** — the cost of changing your mind later is meaningful
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off** — there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
