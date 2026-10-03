# survey

The first of three stages: **survey** (route not visible) or **interrogate** (destination settled) produce the artifacts; **to-gauntlet** turns them into the prompt you paste into a fresh session.

Adapted from Matt Pocock's `wayfinder` skill (`github.com/mattpocock/skills`), stripped of the parts built for multi-week, multi-person efforts, and renamed because the pipeline around it is our own.

The answer-key output is not part of his design and he has not endorsed it. His own guidance is to use a single conversation when the work fits in one — this deliberately runs the heavier interview on smaller work, because the thoroughness and the honesty about unknowns are what we're here for.

Files:

- `SKILL.md` — the run loop.
- `CHECKS.md` — what a legal check is. Single source; the rest defer to it.
- `commands/interview.md` — the interview technique. `interrogate` runs this too.
- `commands/prototype.md` — build something rough to react to.
- `commands/to-bar.md` — emit the answer key. `interrogate` runs this too.

Output lands in `.bar/<slug>/`: `DECISIONS.md` while the questions are being worked, `ANSWER-KEY.md` at the end.
