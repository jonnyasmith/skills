---
name: implementation-loop
description: Sequentially implement a spec-backed set of tickets by resolving their dependency order and delegating each ready ticket to a fresh sub-agent using the implement skill. Use when the user provides a spec or spec reference plus ticket references and wants the complete ticket set implemented one ticket at a time with no concurrent ticket work.
disable-model-invocation: true
---

# Implementation Loop

Orchestrate the work; do not implement tickets in the host agent. Keep exactly one ticket implementation in flight at a time.

## 1. Resolve the work

Read the full spec and every supplied ticket. Follow a ticket's spec reference when the user supplies only tickets. Fetch referenced issue bodies and relevant comments when the sources live in an issue tracker.

For each ticket, record its identifier, acceptance criteria, status, blockers, and source reference. Treat a ticket as complete only when its source marks it complete or the repository contains clear evidence that its acceptance criteria already pass.

## 2. Determine the sequence

Build a dependency graph from the tickets' blocking edges. Reject cycles, missing ticket references, and any ordering that would begin blocked work.

Use blockers as hard constraints. When several incomplete tickets are ready, choose the next ticket by this order:

1. Honour an explicit user-specified order.
2. Prefer prerequisite, prefactoring, expand, or shared-foundation work that unlocks downstream tickets.
3. Prefer the ticket that unlocks the most remaining work or reduces the greatest integration risk.
4. Use the tickets' published order or identifier as the stable tie-breaker.

Add a missing execution dependency when the codebase or acceptance criteria prove that one ticket cannot safely precede another. Record the reason so it can be reported. Do not redesign or repartition approved tickets unless the user asks.

## 3. Delegate one ticket

Spawn one fresh sub-agent for the selected ready ticket. Give it a compact prompt:

`Use /implement to implement <ticket reference>.`

If the ticket does not itself link to the governing spec, append `The governing spec is <spec reference>.` Do not paste the ticket or spec into the prompt when the references are accessible; the delegated agent must load the authoritative sources itself.

Do not ask the sub-agent to use this orchestration skill. Do not delegate multiple tickets to one agent. Do not spawn another implementation agent or begin other ticket work while this agent is active.

## 4. Close the ticket loop

Wait for the sub-agent to finish. Confirm from its result and the repository that:

- the ticket's acceptance criteria are satisfied;
- the relevant tests, type checks, and final review required by `/implement` succeeded;
- the implementation was committed to the current branch; and
- no reported issue leaves the ticket incomplete.

If the result is incomplete but recoverable, send the same sub-agent a concise follow-up naming only the unmet criterion or failing verification, then wait again. Never advance the frontier while the current ticket is incomplete.

If the ticket is blocked by missing authority, inaccessible context, an external dependency, or a failure that cannot be resolved safely, stop the loop. Report the ticket, evidence, and exact condition needed to resume; do not skip ahead.

## 5. Repeat sequentially

Record the ticket and commit as complete in the execution state, recompute the ready frontier, and repeat from step 3. Later agents inherit earlier committed work through the shared repository.

Finish only when every supplied ticket is either already complete or completed by the loop. Report the execution order, ticket-to-commit mapping, verification performed, and anything that remains unverified. Do not close or mutate tracker tickets unless the user separately authorises that workflow.
