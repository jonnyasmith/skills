---
name: grilling
description: Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent to find it; don't ask the user for anything you could look up yourself. The _decisions_ are the user's: put each to them and wait.

**Gather first, then ask.** Each round has two steps, in this order and never overlapped:

1. **Gather.** Dispatch every sub-agent this round needs, in parallel, and _wait for all of them to report_. Sub-agents keep the facts out of your context; they do not run beside the questions. Say one line to the user that you are gathering, then stay silent until the reports are in.
2. **Ask.** With every fact of this round in hand, compute the frontier and post the round. Then wait for the user's answers.

Never post a question while a sub-agent is still running, and never revise or re-ask a question of the round the user is answering. A fact that arrives late is a fact you asked for too late: it belongs to the _next_ round's gather step. If a report genuinely invalidates a question the user already answered, finish the round first, then open the next round by naming what changed and re-asking it once.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

This skill produces **shared understanding**, and nothing on disk. When the deliverable is a written standard for judging finished work, use `interrogate` (destination settled) or `survey` (route not visible yet) instead: they run the same interview and emit an answer key.
