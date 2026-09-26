---
name: sdlc
description: Router for the change-artifact chain - which skill to run at each stage, from first idea to tickets.
disable-model-invocation: true
---

A **change** moves through a chain of artifacts, each an HTML file committed under `changes/<slug>/`. Each stage ends by writing an artifact; the next stage starts by reading it. The shared rules (location, format, diagrams) are in [ARTIFACTS.md](ARTIFACTS.md).

| Stage | Run | Reads | Writes |
| --- | --- | --- | --- |
| Talk the idea through | `/grilling` | the idea, a ticket, or an incident | shared understanding, nothing on disk |
| Capture the intent | `/to-intent` | the conversation | `intent.html` |
| Product owner accepts | a PR or review of `intent.html` | `intent.html` | an accepted intent |
| Requirements and design | `/to-spec` | `intent.html` and the conversation | `spec.html` |
| Plan | Claude Code plan mode, then `/to-plan` | `intent.html`, `spec.html`, the approved plan | `plan.html` |
| Split the work | `/to-tickets` (optional, for work too big for one session) | `plan.html` or `spec.html` | `tickets/*.html` |

Each `to-*` skill writes up what the conversation already holds; none of them interviews. When a stage needs more thinking first, run `/grilling` again before it.

Tell the user where the change is in the chain and which skill comes next.
