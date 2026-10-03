# Glossary

Shared vocabulary for every claim this skill makes. Use these terms exactly — don't substitute "endpoint," "component," "dependency," "boundary," or "unknown." Consistent language is the point.

## Terms

**Surface**
Any point where the system receives input from, or sends output to, something outside itself: HTTP handlers, queue consumers, scheduled jobs, CLI arguments, webhooks, UI event handlers. Not internal function calls.
_Avoid_: endpoint (too narrow — HTTP only), entry point (implies input only).

**Flow**
The path a request, event, or message takes from an entry surface through the system to an exit surface or persistent side effect. A flow is what an operator or user experiences end-to-end.
_Avoid_: request lifecycle, call chain (too narrow), pipeline (implies batch data processing).

**Integration**
An external system the codebase depends on: a database, third-party API, message queue, object store, auth provider. Integrations sit at the edges of the system.
_Avoid_: dependency (applies to internal code too), service (overloaded with microservice meaning).

**Trust zone**
A region of the system where data can be treated as already validated and safe. Code inside a trust zone does not re-validate inputs it received from within the same zone.

**Trust boundary**
The edge of a trust zone — the point at which the system must validate, authenticate, or sanitise incoming data before treating it as safe. A system may have multiple trust boundaries at different surfaces.
_Avoid_: security layer (names an implementation choice, not a structural feature), validation layer.

**Evidence**
A claim directly confirmed by a cited file path. The fundamental unit of trustworthy discovery. Every claim should be evidence or explicitly labelled as an Inference.
_Avoid_: fact (implies absolute certainty — evidence can be misread or stale).

**Inference**
A claim derived from evidence by reasoning, not directly confirmed by code. An inference has a basis (the evidence it was derived from) but is not yet confirmed. Always label explicitly with the prefix `Inference:`.
_Avoid_: assumption (implies no basis — inferences have a basis, they just aren't confirmed).

**Gap**
A specific missing piece of evidence that, if filled, would materially change the discovery. Gaps are scored by impact × uncertainty and drive the gap loop.
_Avoid_: unknown (too vague — a gap names what is specifically missing).

## Principles

- **Evidence first.** Every claim cites a file path or is labelled as an Inference.
- **Surfaces before flows.** You cannot trace a flow until you have found its entry and exit surfaces.
- **Integrations anchor uncertainty.** Most inferences live at integration points — prioritise resolving gaps there.
- **Gaps are not failures.** A gap in your discovery is information: it names exactly what needs a deeper dive.
- **Confidence is a first-class output.** Assign High / Medium / Low confidence to each section of the report.

## Confidence levels

Applied per section of the report (surfaces, flows, integrations, trust boundaries).

**High** — every claim in this section is evidence (cited file path). No inferences.
**Medium** — most claims are evidence; one or two are inferences with a strong basis.
**Low** — key claims are inferences; material gaps remain.

## Gap impact levels

Used to rank gaps in the gap loop. Impact = how much resolving this gap would change the overall discovery.

**High impact** — the gap affects a core flow or the system map itself. Resolving it would materially change the confidence of one or more sections.
**Medium impact** — the gap affects a secondary flow or an integration detail. Resolving it would sharpen the picture but not reshape it.
**Low impact** — the gap is a detail (e.g. exact library version, config file location). Safe to leave open.

## Rejected framings

- **"Endpoint" for surface**: too narrow — covers HTTP only.
- **"Dependency" for integration**: applies to internal code too. Use integration for external systems.
- **"Boundary" for trust boundary**: overloaded with DDD's bounded context. Say trust boundary.
- **"Unknown" for gap**: a gap is a specific named missing piece, not a vague mystery.
- **"Fact" for evidence**: implies certainty that evidence cannot guarantee.
