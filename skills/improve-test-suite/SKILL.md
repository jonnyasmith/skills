---
name: improve-test-suite
description: Audit an existing test suite for seam-quality and coverage gaps, present findings as a visual HTML report, then grill through whichever seam you pick and hand the agreed work off as a spec/tickets.
disable-model-invocation: true
---

# Improve Test Suite

Audit an existing suite and improve it. Coverage points at blind spots; it never validates a test. The goal is **behaviour tested at the seams of deep modules** — not lines covered. A suite at 100% line coverage full of tautological, implementation-coupled tests is worse than a suite with honest gaps.

This command is _informed_ by the same vocabulary as the rest of the review family — it coins no terms of its own:

- Run the `/tdd` skill for what a **good test** is (behaviour through public interfaces, not internals), where tests go (**seam**), and the anti-patterns (**implementation-coupled**, **tautological**, **horizontal-slicing**).
- Run the `/codebase-design` skill for the architecture vocabulary (**module**, **interface**, **depth**, **deep**, **shallow**, **seam**, **locality**, **leverage**) and the **deletion test**. Use these terms exactly — don't drift into "component," "service," "unit," or "boundary."
- The project's domain language names good seams, and its ADRs record decisions this command should not re-litigate. Both arrive through the repo's `AGENTS.md` standing rules.

## Process

### 1. Scope

**Scope before you scan — YAGNI.** Improving tests around code that keeps changing pays off; polishing a mediocre test on a stable, untouched module is churn. Decide *where* to look before you look:

- If the user named a direction — a module, a subsystem, a suite, a pain point — take it, and skip the inference below.
- Otherwise, walk back a good stretch of the commit history (`git log --oneline`) to find the codebase's hot spots — the files and areas that keep coming up — and let those paths pull the deep seam analysis first. If the changes are scattered with no clear hot spot, widen the net.

The split matters: coverage is global and cheap once the suite runs, so the **coverage pass sees the whole suite** (to spot big dark zones), while the **deep seam judgement concentrates on the scoped hot spots**. Wide-but-shallow coverage scan, narrow-but-deep seam analysis.

### 2. Coverage pass — wide and cheap

Detect the coverage tool (`jest --coverage`, `vitest run --coverage`, `pytest --cov`, `go test -cover`, etc.) and run it across the whole suite **only to locate no/low-coverage dark zones**. The percentage is a blind-spot pointer, never the target.

If the suite won't give clean coverage, that is itself the most important finding — report it as a headline, not a blocker:

- **Suite is red** — a suite you can't trust is worse than gaps. Surface it up front, mark every seam-card's coverage badge `n/a — suite not runnable`, and continue on static seam judgement (which needs no execution).
- **No runner / no coverage config** — same: mark coverage `n/a` and continue statically.
- **Flaky** — flag the specific non-deterministic tests as a `Rewrite`/`Relocate` finding; non-determinism is a genuine test defect.

Never abort the audit over a runner problem.

### 3. Seam judgement — narrow and deep

Use the Agent tool with `subagent_type=Explore` to walk the scoped hot spots. The goal is behaviour tested at the seams of deep modules. Every finding resolves to one of four **seam-states**:

- **Fill** — deep module, good seam, no or weak test → a coverage gap worth closing.
- **Rewrite** — a test at the right seam, but it's **implementation-coupled**, **tautological**, or verifies through a side channel → keep the seam, replace the test.
- **Relocate / Delete** — a **shallow** module tested in isolation has no **locality**: the real bug is in how it's *called*, so the test belongs at the caller's seam (relocate). A duplicate or worthless test with nothing to defend → delete.
- **Healthy** — a deep seam already tested through its interface → leave it alone and say so. No churn on tests that work.

Apply the **deletion test** to any test you suspect is worthless: would deleting it lose a real defence, or just remove noise? "Just noise" is a `Delete` candidate.

### 4. Present findings as an HTML report

Write a self-contained HTML file to the OS temp directory so nothing lands in the repo. Resolve the temp dir from `$TMPDIR`, falling back to `/tmp` (or `%TEMP%` on Windows), and write to `<tmpdir>/test-suite-review-<timestamp>.html` so each run gets a fresh file. Open it for the user — `xdg-open <path>` on Linux, `open <path>` on macOS, `start <path>` on Windows — and tell them the absolute path.

The report is **organised by seam**. Each seam-card carries a **coverage badge** (measured, or `n/a`) and a **seam-state badge** (`Fill`, `Rewrite`, `Relocate`, `Delete`, `Healthy`), the evidence, and a before/after sketch of the test surface. See [HTML-REPORT.md](HTML-REPORT.md) for the full scaffold, diagram patterns, and styling.

**Markdown swap:** to produce a plain-text report instead — for a PR, a fresh LLM session, or a repo that shouldn't open browsers — follow [MARKDOWN-REPORT.md](MARKDOWN-REPORT.md) instead. Same content, same seam organisation, Mermaid instead of hand-built SVG.

**Use the project's domain vocabulary for the domain, the `/codebase-design` terms for the architecture, and the `/tdd` terms for the tests.** Talk about "the Order intake seam," not "the FooBarHandler tests."

Do NOT design the replacement tests yet. After the file is written, ask the user: "Which seam would you like to act on?"

### 5. Grilling loop

Once the user picks a seam, run the `/grilling` skill to walk the decision tree with them — which behaviour to test, which seam to test it at, what survives, and for any `Delete`/`Relocate` finding, *why* the test goes and where (if anywhere) its coverage lands instead.

**Never delete a test silently.** Every removal must be named and justified in the grill (tautological / implementation-coupled / duplicate) and confirmed by the user before it enters the work-package.

### 6. Hand off as a spec / tickets

This skill **never writes or deletes tests itself** — it diagnoses, grills, and produces the agreed work-package to run in a fresh session. Once the grill reaches shared understanding, capture the agreed work:

- Run the `/to-spec` skill for a single coherent body of test work, or `/to-tickets` when it splits into independent units.
- Each `Delete`/`Relocate` line-item carries its written justification, so the deletion decision travels with the work rather than happening live.
- When the real fix is deepening a **shallow** module (the test is only bad because the module is), make it a ticket cross-referencing the `/improve-codebase-architecture` skill — deepen the module first, and the test surface fixes itself.

The user then runs the spec/tickets via the `/implement` or `/tdd` skill in a new session.
