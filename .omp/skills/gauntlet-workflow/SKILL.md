---
name: gauntlet-workflow
description: Runs a gauntlet loop as a workflowz eval cell instead of a pasted prompt - a deterministic outer loop that builds each piece, grades it with a fresh harsh critic against a concrete bar, feeds the critic's single biggest gap back to the builder, and keeps going until every piece passes. Use when the goal has a real inspectable bar and you want the rounds enforced by code rather than by an agent's good intentions. Triggers on "/gauntlet-workflow", "gauntlet workflow", "gauntlet this as a workflow", "loop until it beats X, deterministically".
---

# Gauntlet Workflow

Same method as `gauntlet-loop`. Different machine.

`gauntlet-loop` hands the user a prompt and trusts a lead agent to split the work, spawn critics, and go back round when a critic says no. That trust is where it fails: the lead builds instead of orchestrating, runs one critic at the end, and calls a waterfall a loop.

This skill writes the loop as code. The attempts, the rework edge, the routing and the exit are code in an omp `eval` cell, so no execution path can skip them.

**You do the work here.** You write the cell and you run it with the `eval` tool. You are not handing back a prompt. You are not using Claude's Workflow tool, `export const meta`, `effort`, or a two-argument `pipeline`.

**Requires omp `eval`.** Helpers: `agent()`, `parallel()`, `phase()`, `log()`, `budget`. Under any harness without them, use `gauntlet-loop`.

## When to use which

| | `gauntlet-loop` | this |
|---|---|---|
| Bar | a reference you eyeball | a reference, or an answer key with rows |
| Attempts | the lead decides | a `while` per piece, enforced |
| Rework edge | the lead remembers to | code passes `biggestGap` to the next builder |
| Critic form | prose, can drift soft | a JSON schema, enum verdicts, one row each |
| Human in the middle | yes, every round | no, until the run returns |
| Cost | visible as it goes | committed up front |

Use `gauntlet-loop` when the goal is fuzzy and you want to steer between rounds. Use this when the bar is settled and you want to leave.

## Flow

1. **Read the goal.** One line restatement in your head, not on screen.
2. **Set the bar.** If the user supplied one, use it. If not, offer **2 or 3 candidates**, one line each, and stop. Wait for their pick.
3. **Split the work yourself, from the bar.** Not from a guess about the architecture. Each piece owns a named subset of the bar - specific rows, or a specific property of the reference. A piece nobody can grade is not a piece.
4. **Write the cell.** Follow the template below.
5. **Run it** as one `eval` call: `language="py"`, `timeout=0`, `reset=true`. Invoking this skill is the user's opt-in; you do not need to ask again.
6. **Report the result table**, the attempts each piece took, and anything still open. Relay it - the cell's return value is not shown to the user.

## The bar is the whole trick

Unchanged from `gauntlet-loop`, and it matters more here, because nothing stops a bad bar for six rounds instead of one.

- **Named.** A specific thing, not a category. "Stripe's pricing page" works. "Award-winning SaaS sites" does not.
- **Fetchable.** The critic can actually get it - screenshot the live page, read the published piece, run the binary, open the repo, open the file. If the agent cannot obtain it, it will hallucinate the comparison.
- **Comparable.** Both can sit side by side and a judge can pick one.

**An answer key is the strongest bar this skill takes.** A file of binary rows with a fixed verdict form removes the critic's last degree of freedom, and it works for novel goals that have no existing product to sit beside. If one exists for the goal, name its absolute path and let it supply the rows, the verdict form, the out-of-scope list, and the `BLOCKED` stop condition. If one does not exist and the goal deserves one, say so before writing the cell.

If the goal has a measurable half - frame time, p95 latency, benchmark score, pass rate - name it alongside the reference. Taste plus a number beats taste alone.

## How omp workflowz runs this

- One Python `eval` cell. The outer `while` lives in that cell, not in your chat turns.
- Build, grade and rework for one piece are **one function**. `parallel()` those functions so each piece loops at its own speed and none waits for the slowest.
- Do **not** use `pipeline()`. Later pipeline stages receive only the prior result, not the original piece, and the barrier waits for every builder before any critic starts.
- `agent(prompt, agent=..., label=..., schema=...)` - Python kwargs. `schema=` returns parsed data.
- Spawn `agent="builder"` and `agent="critic"` so each starts blank. If those agents are missing in this repo, omit `agent`.
- `phase()` / `log()` for the stage. Do not pass `phase` or `effort` into `agent()` - those are Claude Workflow fields.
- `parallel()` pool width is `task.maxConcurrency`. Do not hand-tune it.
- Host-bridge time in `agent()` / `parallel()` does not consume the cell timeout; `log()` / `phase()` do. Use `timeout=0`.
- Put shared background that would bloat every prompt in `local://` and name that URI in `COMMON`.

## The cell

Adapt every string. Keep the shape.

```py
BAR = "<absolute path, URL, or repo the critic opens>"
MAX_ATTEMPTS = 3

COMMON = """
...
"""

# Numbers carried in from before this work. Restating, relaxing or recomputing one
# is a failure, not a result. Empty string if the goal has none.
ANCHORS = """
...
"""

INSTRUMENT = """
...
"""

VERDICT = {
    "type": "object",
    "properties": {
        "verdicts": {"type": "array", "items": {"type": "object", "properties": {
            "check":   {"type": "string", "description": "the bar row or property being graded"},
            "verdict": {"type": "string", "enum": ["PASS", "FAIL", "CANNOT JUDGE"]},
            "why":     {"type": "string", "description": "one line: what was observed"},
            "blocks":  {"type": "string", "description": "CANNOT JUDGE only: the piece whose output is missing"},
        }, "required": ["check", "verdict", "why"]}},
        "result":     {"type": "string", "description": "the bar's own RESULT line"},
        "biggestGap": {"type": "string", "description": "the single biggest thing to fix next, concrete; empty if none"},
        "evidence":   {"type": "string", "description": "raw measurements, paths, outputs a reader can chase"},
    },
    "required": ["verdicts", "result", "biggestGap", "evidence"],
}

PIECES = [
    {"key": "<piece>", "owns": "<rows 3 and 8>", "must": "<what must be true when it is done>"},
]

state = {p["key"]: {"attempts": 0, "status": "open", "gap": "",
                    "blockers": "", "result": "", "rows": []} for p in PIECES}
history = []
RUN = {"blocked": None}

def build(p, gap):
    rework = ""
    if gap:
        rework = "A critic rejected the last attempt. The single biggest gap was:\n" + gap + "\nFix that first."
    return agent(
        COMMON + f"""
You are the builder for "{p['key']}". {p['must']}
""" + rework + """
Verify your own work runs before returning. Return a terse summary of what you changed.""",
        agent="builder",
        label="build:" + p["key"],
    )

def grade(p):
    return agent(
        COMMON + f"""
You are a harsh critic with fresh context. You did not build this, and you will not be shown the builder's report.
The bar is {BAR}. Open it. Grade ONLY {p['owns']}, in the bar's own verdict form, and nothing else.
""" + ANCHORS + INSTRUMENT + """
Run every check yourself. Never grade from a summary, a log the builder wrote, or a screenshot the builder took.
Return one verdict per row you own. No partial credit, no fourth verdict, no overall grade.
A row graded by more than one lens passes only when every lens holds, and a negative control that does not fail
vetoes that row on its own. Never a majority.
A row you cannot run because another piece has not landed is CANNOT JUDGE naming that piece in "blocks",
never FAIL. No builder can close a gap outside its own piece.
Praise is not useful. If you cannot obtain the bar, say so - do not guess.""",
        agent="critic",
        label="critic:" + p["key"],
        schema=VERDICT,
    )

# The routing rule. This cell counts the rows; the critic never returns an overall grade.
def route(p, v):
    s = state[p["key"]]
    rows = v.get("verdicts") or []
    history.append({"piece": p["key"], "attempt": s["attempts"],
                    "result": v["result"], "gap": v["biggestGap"]})
    s["result"] = v["result"]
    s["rows"] = rows
    if "BLOCKED" in v["result"]:
        RUN["blocked"] = RUN["blocked"] or (p["key"] + ": " + v["result"])
        s["status"] = "blocked"
        return
    if all(r["verdict"] == "PASS" for r in rows):
        s["status"] = "closed"
        return
    if any(r["verdict"] == "FAIL" for r in rows):
        s["status"] = "open"
        s["gap"] = v["biggestGap"]
        return
    s["status"] = "waiting"
    s["blockers"] = ", ".join(r.get("blocks") or r["check"]
                              for r in rows if r["verdict"] == "CANNOT JUDGE")

# One piece runs its own build / grade / rework loop, to completion, at its own speed.
def run_piece(p):
    s = state[p["key"]]
    while s["status"] == "open" and s["attempts"] < MAX_ATTEMPTS and not RUN["blocked"]:
        s["attempts"] += 1
        build(p, s["gap"])
        v = grade(p)
        if not v or not v.get("verdicts"):
            v = grade(p)                      # an empty verdict list is never a pass
        if not v or not v.get("verdicts"):
            s["status"] = "ungraded"
            return
        route(p, v)
    if s["status"] == "open":
        s["status"] = "capped"

phase("Build and grade")
parallel([lambda p=p: run_piece(p) for p in PIECES])

# A waiting piece is blocked on another piece, so it is re-graded and never rebuilt.
# When a pass re-grades nothing, nothing more will land: stop rather than spin.
while not RUN["blocked"]:
    waiting = [p for p in PIECES if state[p["key"]]["status"] == "waiting"]
    if not waiting:
        break
    phase("Settle")
    log("re-grading pieces blocked on another piece: " + ", ".join(p["key"] for p in waiting))
    graded = parallel([lambda p=p: (p, grade(p)) for p in waiting])
    moved = False
    for g in graded:
        if not g:
            continue
        p, v = g
        if not v or not v.get("verdicts"):
            continue
        route(p, v)
        if state[p["key"]]["status"] != "waiting":
            moved = True
    if not moved:
        break
    reopened = [p for p in PIECES if state[p["key"]]["status"] == "open"]
    if reopened:
        parallel([lambda p=p: run_piece(p) for p in reopened])

pieces = [dict(state[p["key"]], piece=p["key"]) for p in PIECES]
unfinished = [r for r in pieces if r["status"] != "closed"]
if RUN["blocked"]:
    log("BLOCKED - a person has to decide: " + RUN["blocked"])
if unfinished:
    log("not closed: " + ", ".join(r["piece"] + " (" + r["status"] + ")" for r in unfinished))

{"blocked": RUN["blocked"], "closed": len(pieces) - len(unfinished),
 "total": len(pieces), "pieces": pieces, "history": history}
```

Bind loop variables on the lambda (`lambda p=p`) or every thunk captures the last piece.

## Rules for what you fill in

- **Bake the bar in as a fetchable thing.** Absolute path, URL, repo, product name.
- **Give the builder the destination, not the route.** No file layout, no module list, no API shape, no library choice beyond the fixed constraints. Every extra line is one fewer decision the builder makes, and one fewer thing the critic can find.
- **Name the instrument, not the intention.** "Inspects the real output" becomes real when you write the command, the tool, or the measurement. Put it in `INSTRUMENT` once; do not restate it per agent.
- **Name the anchors.** Fixed numbers that came from before this work go in `ANCHORS`, and moving one is a failure rather than a result. Leave it empty rather than inventing anchors the goal does not have.
- **Never give a critic the builder's return value.** `run_piece` calls the builder and discards what it returns. The critic prompt is built from the piece, not from the build.
- **Never tell a critic to fail a row it could not run.** That is what `CANNOT JUDGE` is for, and an instruction to fail it instead turns another piece's missing output into this piece's defect.
- **Give each piece a file list, not only rows.** Rows say what a critic grades; they do not say who may write where. Two builders editing one file at once lose work, and each verifies against a tree the other has half-edited. Put the owned paths in the piece and say in `COMMON` that another agent owns the rest. Where a boundary is genuinely shared, name the piece that owns it rather than letting two agents assume.
- **For anything visual, make the comparison blind.** Build a composite of ours and the reference with the labels stripped and the answer in a separate key file. Tell the critic to write its pick down before reading the key, and to report both. A sighted A/B is not an A/B.
- **Add tool names only if the goal needs them** - a browser, an image generator, a deploy target.
- Everything else stays out.

## The loop

The loop is per piece. `run_piece` builds, grades and reworks one piece to completion, and `parallel()` runs every piece's loop at the same time, so a piece that passes first never waits for the slowest. One outer loop that builds every piece and then grades every piece is a waterfall with a QA gate, repeated.

**When a piece cannot compile without another one, stage them and say so.** `parallel()` is the default because it is right whenever the pieces are separable, and most goals' pieces are. One codebase is the exception: if piece B's code will not build until piece A's function exists, running them at once makes B's builder verify against a broken tree, and the loop reworks it for a defect it did not cause. Then run the stages in dependency order, one `run_piece` each, and keep every other property - the per piece loop, the rework edge, the fresh critic, the three routes. That is not the waterfall this skill warns about: the waterfall is grading every piece behind one barrier, which makes each piece wait for the slowest even when nothing couples them. Do not stage anything the dependency does not force, and tell the user which order you chose and why.

The exit is **every piece passing**, or the user stopping the run. Never an attempt count.

`MAX_ATTEMPTS` is a runaway guard, not the exit. When it fires the piece ends as `capped` and the cell's return value says so - it must never read as success. Prefer the budget form when the user gave a token target:

```py
while s["status"] == "open" and not RUN["blocked"] and budget.total and budget.remaining() > 200_000:
```

Guard on `budget.total`: with no target set, `remaining()` is infinity and only `MAX_ATTEMPTS` stops the loop.

Three verdicts need three routes, and `route()` is where they are decided:

| The rows say | The piece | Why |
|---|---|---|
| every row PASS | closes | nothing left to do |
| any row FAIL | goes back to a builder with the single biggest gap | the gap is inside this piece |
| no FAIL, some CANNOT JUDGE | waits, and is re-graded later without rebuilding | the gap is in another piece, and a builder cannot close it |

The settle loop stops as soon as a full pass moves no waiting piece. Two pieces each waiting on the other never resolve, and spinning on them costs a critic per piece per pass while changing nothing.

`BLOCKED` ends the run and hands back to a person. It is not a failure of the work and it is not something a critic resolves by looking harder - looking harder is exactly what produces an invented answer. Only include the check when the bar has undecided items.

Two agents per attempt per piece. Five pieces at three attempts is thirty agents before any settle pass. Say the arithmetic out loud to the user before you run it.

## What breaks a gauntlet workflow

- **A vague bar.** The critic invents a comparison and passes round one. Most common failure by far, and here it fails silently and expensively.
- **An empty verdict list read as a pass.** `all(...)` over an empty list is `True` in Python, so a critic that returns no rows would close the piece. Check the rows exist before routing them.
- **Routing CANNOT JUDGE to a builder.** It is not a FAIL. The builder cannot close a gap in another piece, so it spends an attempt and the critic returns the same verdict.
- **No rework edge.** A cell that builds, critiques, and returns is a waterfall with a QA gate. The gap has to reach the next builder prompt, or nothing loops.
- **A round barrier around the pieces.** Grading every piece before any piece reworks makes each one wait for the slowest, and it is not what the graph says.
- **Over-specified builder prompts.** Naming the files and the function signatures turns builders into typists and leaves critics nothing to find. The symptom is the first attempt passing everything.
- **The critic seeing the builder's work product instead of the artifact.** It must open the running thing, not the report.
- **Closing a piece on anything but every row passing.** Partial credit is how a gauntlet loop quietly stops being one.
- **Looping on the closed pieces instead of the open ones.** Pieces a critic rejected must come back; pieces it passed must not.
- **A fixed attempt count as the goal.** The cap is a guard. If you find yourself choosing it to control cost, use the budget form instead and say so.
- **A Claude Workflow script.** `export const meta`, `effort`, `phase=` on `agent()`, and `pipeline(work, builder, (_built, p) => critic)` will not run here.
