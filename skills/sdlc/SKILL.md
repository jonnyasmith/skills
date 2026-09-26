---
name: sdlc
description: Router for the AI-native SDLC playbook's chain - which skill to run at each stage, from first idea to a built change.
disable-model-invocation: true
---

A **change** moves through a chain of artifacts, each an HTML file committed under `changes/<slug>/`. Each stage ends by writing an artifact; the next stage starts by reading it. The shared rules (location, format, diagrams) are in [ARTIFACTS.md](ARTIFACTS.md).

| Stage | Run | Reads | Writes |
| --- | --- | --- | --- |
| Talk the idea through | `/grilling` | the idea, a ticket, or an incident | shared understanding, nothing on disk |
| Capture the intent | `/to-intent` | the conversation | `intent.html` |
| Product owner accepts | a PR or review of `intent.html` | `intent.html` | an accepted intent |
| Requirements and design | `/to-design` | the accepted `intent.html` and the policy skills | `spec.html` |
| Product owner accepts | review of `spec.html`, concerns resolved with policy owners | `intent.html`, `spec.html` | a go or no-go |
| Plan | Claude Code plan mode, then `/to-plan` | `intent.html`, `spec.html`, the approved plan | `plan.html` |
| Build | `/build-change` | `plan.html`, `spec.html` | commits on `feat/<slug>`, reviewed until clean |
| User tries it | merge or request changes | the running change | a merged change |

None of the `to-*` skills interviews; each writes up what its inputs already hold. When a stage needs more thinking first, run `/grilling` before it.

Tell the user where the change is in the chain and which skill comes next.
