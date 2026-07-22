# Independent Reviews

Review the complete diff against the baseline before the final commit. The
original request is the spec. Reviewers must not see one another's conclusions.

Run the Standards review, the Spec review when a source exists, and the Deslop
review when the diff changes code in parallel when collaboration tools are
available. Otherwise run the applicable passes sequentially.

## Standards

Give the reviewer repository instruction files, applicable architecture
records, and the diff. Ask it to report, per file or hunk:

1. documented-standard violations, citing the rule;
2. structural judgement calls: a concrete code-judo reframing that deletes
   complexity; ad-hoc branching in an unrelated flow; feature logic outside its
   canonical layer; thin abstractions; unclear type or data boundaries; or
   related updates that need atomicity or simpler parallel orchestration;
3. maintainability judgement calls: unclear names, duplication, feature envy,
   data clumps, primitive obsession, repeated dispatch, shotgun surgery,
   divergent change, speculative generality, message chains, or middle men.

When an edited file crosses 1,000 lines or grows materially beyond local norms,
require a decomposition assessment. Check sequencing and atomicity only where
concurrency or durable state makes them relevant. Prefer a few high-conviction
findings over cosmetic nits. Distinguish hard violations from judgement calls;
never present a judgement call as a repository breach.

## Spec

Give the reviewer the original request, agreed decisions, invariants, and the
diff. Ask it to report missing or partial requirements, scope creep, and
implemented-but-wrong behaviour, citing the relevant request or decision.

## Deslop

Give the reviewer the diff and modified files' nearby code. It is review-only:
never edit the shared worktree. Report only high-confidence,
behaviour-preserving cleanups for unnecessary or locally inconsistent comments,
abnormal defensive guards or silent fallbacks, type escapes, needless nesting,
or generated-looking helpers that add no leverage. Do not repeat architecture
or spec findings owned by the other reviews.

## Escalation and report

The Standards review always performs the structural screen. Run a full
thermo-nuclear review only when the user asks, the change is architecture-heavy,
or the structural screen finds a plausible redesign.

Present findings under separate `## Standards`, `## Spec`, and, when run,
`## Deslop` headings. Do not merge or rerank them; state the count and worst
issue within each axis independently. Classify every finding as must-fix,
fixed, accepted judgement call, or future note.
