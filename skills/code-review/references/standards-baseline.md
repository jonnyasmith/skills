# Standards baseline

On top of whatever the repo documents, the Standards axis always carries this baseline — a fixed set of quality heuristics that applies even when a repo documents nothing. Two rules bind all of it:

- **The repo overrides.** A documented repo standard always wins; where it endorses something the baseline would flag, suppress it.
- **Always a judgement call.** Every baseline item is a labelled heuristic ("possible Feature Envy"), never a hard violation — only documented-standard breaches are hard. Like any standard here, skip anything tooling already enforces.

The baseline has three lists. Each entry reads _what it is_ → _how to fix_; match them against the diff.

**Structural screen** — always run this pass; it looks for shape problems the change introduces:

- **Code-judo reframing** — the change adds complexity that reframing the problem would delete outright. → restate the problem so the hard case disappears instead of being handled.
- **Ad-hoc branching** — a new special-case branch bolted into an otherwise unrelated flow. → route it through the flow's real abstraction, not a side branch.
- **Misplaced layer** — feature logic living outside its canonical layer (e.g. domain rules in a controller). → move it to the layer that owns that concern.
- **Thin abstraction** — a wrapper or indirection that earns nothing over calling its target directly. → inline it until a real need justifies the seam.
- **Unclear type or data boundary** — a type or interface whose responsibility or ownership is muddy. → sharpen the boundary so each side's contract is obvious.
- **Atomicity / orchestration** — related updates that must land together, or parallel work a simpler orchestration would tame. → make the set atomic, or simplify the coordination.

**Maintainability smells** — Fowler code smells (_Refactoring_, ch.3):

- **Mysterious Name** — a function, variable, or type whose name doesn't reveal what it does or holds. → rename it; if no honest name comes, the design's murky.
- **Duplicated Code** — the same logic shape appears in more than one hunk or file in the change. → extract the shared shape, call it from both.
- **Feature Envy** — a method that reaches into another object's data more than its own. → move the method onto the data it envies.
- **Data Clumps** — the same few fields or params keep travelling together (a type wanting to be born). → bundle them into one type, pass that.
- **Primitive Obsession** — a primitive or string standing in for a domain concept that deserves its own type. → give the concept its own small type.
- **Repeated Switches** — the same `switch`/`if`-cascade on the same type recurs across the change. → replace with polymorphism, or one map both sites share.
- **Shotgun Surgery** — one logical change forces scattered edits across many files in the diff. → gather what changes together into one module.
- **Divergent Change** — one file or module is edited for several unrelated reasons. → split so each module changes for one reason.
- **Speculative Generality** — abstraction, parameters, or hooks added for needs the spec doesn't have. → delete it; inline back until a real need shows.
- **Message Chains** — long `a.b().c().d()` navigation the caller shouldn't depend on. → hide the walk behind one method on the first object.
- **Middle Man** — a class or function that mostly just delegates onward. → cut it, call the real target direct.
- **Refused Bequest** — a subclass or implementer that ignores or overrides most of what it inherits. → drop the inheritance, use composition.

**Slop** — AI-generated residue that survives the other two lists:

- **Inconsistent comments** — comments that restate the code, or clash with the file's commenting style. → delete them; keep only what explains non-obvious intent.
- **Abnormal defensive guards** — try/catch or null-guards abnormal for a trusted code path, or silent fallbacks that swallow errors. → remove the guard, or let the error surface.
- **Type escapes** — casts to `any` or unsafe casts used only to bypass a type the code should satisfy honestly. → fix the type, drop the cast.
- **Needless nesting** — deep nesting that early returns would flatten. → guard-clause the edge cases and return early.
- **Generated-looking helpers** — helpers or abstractions that add no leverage and read as boilerplate. → inline them; keep only what pulls its weight.

When an edited file crosses ~1,000 lines or grows materially beyond local norms, add a decomposition assessment to the Standards findings.

**Escalation.** The structural screen always runs. Escalate to a **full structural review** — an exhaustive pass proposing concrete redesigns, cross-file architecture, and decomposition plans rather than flag-and-cite — only when the user asks, the change is architecture-heavy, or the structural screen surfaces a plausible redesign.
