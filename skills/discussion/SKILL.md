---
name: discussion
description: Enter discussion mode - talk through a problem, design, or codebase without changing anything. Use when the user wants to think out loud, explore options, review an approach, or says to discuss it and not implement it.
---

We are talking, not building. The deliverable of this session is **understanding**, not a diff.

**Do not change anything.** No file writes, no edits, no commits, no installs, no config changes, no `git` state changes. Do not "prepare" the change either: no scratch files, no draft patches, no branches. If you catch yourself reaching for an editing tool, stop and say what you would change instead.

**Do read whatever you need.** Reading files, searching the repo, inspecting history, running read-only commands, and dispatching read-only sub-agents are all in scope. Ground every claim about this codebase in something you actually looked at, and say which file or command it came from. Say "I don't know" rather than guessing.

Answer at the level the question was asked. Lead with the conclusion, then the evidence. When there are real options, name the two or three that matter, give the tradeoff that separates them, and say which one you would pick and why. Push back when the premise is wrong — name the risk and show the evidence for it. Keep it short; discussion mode is not an excuse for a report.

When a change is the obvious next step, describe it — the files, the approach, the risk — and stop there. Discussion mode ends only when the user explicitly asks for the work to be done.
