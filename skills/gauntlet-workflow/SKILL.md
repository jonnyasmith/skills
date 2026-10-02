---
name: gauntlet-workflow
description: Runs a gauntlet loop as a Workflow script instead of a pasted prompt - a deterministic outer loop that builds each piece, grades it with a fresh harsh critic against a concrete bar, feeds the critic's single biggest gap back to the builder, and keeps going until every piece passes. Use when the goal has a real inspectable bar and you want the rounds enforced by code rather than by an agent's good intentions. Triggers on "/gauntlet-workflow", "gauntlet workflow", "gauntlet this as a workflow", "loop until it beats X, deterministically".
disable-model-invocation: true
---

# Gauntlet Workflow

Same method as `gauntlet-loop`. Different machine.

`gauntlet-loop` hands the user a prompt and trusts a lead agent to split the work, spawn critics, and go back round when a critic says no. That trust is where it fails: the lead builds instead of orchestrating, runs one critic at the end, and calls a waterfall a loop.

This skill writes the loop as code. The rounds, the rework edge and the exit are a `while` in a Workflow script, so no execution path can skip them.

**You do the work here.** You write the script and you run it. You are not handing back a prompt.

## When to use which

| | `gauntlet-loop` | this |
|---|---|---|
| Bar | a reference you eyeball | a reference, or an answer key with rows |
| Rounds | the lead decides | a `while`, enforced |
| Rework edge | the lead remembers to | code passes `biggestGap` to the next builder |
| Critic form | prose, can drift soft | a JSON schema, enum verdicts |
| Human in the middle | yes, every round | no, until the run returns |
| Cost | visible as it goes | committed up front |

Use `gauntlet-loop` when the goal is fuzzy and you want to steer between rounds. Use this when the bar is settled and you want to leave.

## Flow

1. **Read the goal.** One line restatement in your head, not on screen.
2. **Set the bar.** If the user supplied one, use it. If not, offer **2 or 3 candidates**, one line each, and stop. Wait for their pick.
3. **Split the work yourself, from the bar.** Not from a guess about the architecture. Each piece owns a named subset of the bar - specific rows, or a specific property of the reference. A piece nobody can grade is not a piece.
4. **Write the script.** Follow the template below. Load `workflow-authoring` first if you have not this session.
5. **Run it** with the Workflow tool. Invoking this skill is the user's opt-in; you do not need to ask again.
6. **Report the result table**, the rounds each piece took, and anything still open. Relay it - the workflow's return value is not shown to the user.

## The bar is the whole trick

Unchanged from `gauntlet-loop`, and it matters more here, because nothing stops a bad bar for six rounds instead of one.

- **Named.** A specific thing, not a category. "Stripe's pricing page" works. "Award-winning SaaS sites" does not.
- **Fetchable.** The critic can actually get it - screenshot the live page, read the published piece, run the binary, open the repo, open the file. If the agent cannot obtain it, it will hallucinate the comparison.
- **Comparable.** Both can sit side by side and a judge can pick one.

**An answer key is the strongest bar this skill takes.** A file of binary rows with a fixed verdict form removes the critic's last degree of freedom, and it works for novel goals that have no existing product to sit beside. If one exists for the goal, name its absolute path and let it supply the rows, the verdict form, the out-of-scope list, and the `BLOCKED` stop condition. If one does not exist and the goal deserves one, say so before writing the script.

If the goal has a measurable half - frame time, p95 latency, benchmark score, pass rate - name it alongside the reference. Taste plus a number beats taste alone.

## The script

Adapt every string. Keep the shape.

```js
export const meta = {
  name: '<slug>',
  description: '<one line, shown in the permission dialog>',
}

const BAR = '<absolute path, URL, or repo the critic opens>'

// Everything every agent needs: the goal, the fixed constraints, the out-of-scope
// list, where the bar is, and which items are undecided and must not be decided.
const COMMON = `
...
`

// How a critic inspects reality. Name the commands, the tool, the file paths.
// A critic with no instrument is another model with an opinion.
const INSTRUMENT = `
...
`

const VERDICT = {
  type: 'object',
  properties: {
    verdicts: { type: 'array', items: { type: 'object', properties: {
      check:   { type: 'string', description: 'the bar row or property being graded' },
      verdict: { type: 'string', enum: ['PASS', 'FAIL', 'CANNOT JUDGE'] },
      why:     { type: 'string', description: 'one line: what was observed' },
    }, required: ['check', 'verdict', 'why'] } },
    result:     { type: 'string', description: 'the bar\'s own RESULT line' },
    biggestGap: { type: 'string', description: 'the single biggest thing to fix next, concrete; "" if none' },
    evidence:   { type: 'string', description: 'raw measurements, paths, outputs a reader can chase' },
  },
  required: ['verdicts', 'result', 'biggestGap', 'evidence'],
}

// One entry per independently judgeable piece. `owns` must name real rows of the bar.
const PIECES = [
  { key: '<piece>', owns: '<rows 3 and 8>', must: '<what must be true when it is done>' },
]

const open = new Map(PIECES.map(p => [p.key, '']))   // piece -> the last gap a critic named
const history = []
let round = 0
let blocked = null

while (open.size && round < 6 && !blocked) {
  round++
  const tag = 'Round ' + round
  phase(tag)
  log(tag + ': ' + [...open.keys()].join(', '))

  const work = PIECES.filter(p => open.has(p.key)).map(p => ({ ...p, gap: open.get(p.key) }))

  const graded = await pipeline(
    work,
    p => agent(`${COMMON}
You are the builder for "${p.key}". ${p.must}
${p.gap ? 'A critic rejected the last attempt. The single biggest gap was:\n' + p.gap + '\nFix that first.' : ''}
Verify your own work runs before returning. Return a terse summary of what you changed.`,
      { label: 'build:' + p.key, phase: tag }),
    (_built, p) => agent(`${COMMON}
You are a harsh critic with fresh context. You did not build this, and you will not be shown the builder's report.
The bar is ${BAR}. Open it. Grade ONLY ${p.owns}, in the bar's own verdict form, and nothing else.
${INSTRUMENT}
Run every check yourself. Never grade from a summary, a log the builder wrote, or a screenshot the builder took.
Praise is not useful. If you cannot obtain the bar or run a check, fail that row and say why - do not guess.`,
      { label: 'critic:' + p.key, phase: tag, schema: VERDICT, effort: 'high' })
      .then(v => ({ piece: p.key, v })),
  )

  for (const g of graded.filter(Boolean)) {
    history.push({ round, piece: g.piece, result: g.v.result, gap: g.v.biggestGap })
    if (/BLOCKED/.test(g.v.result)) { blocked = g.piece + ': ' + g.v.result; break }
    if (g.v.verdicts.every(r => r.verdict === 'PASS')) { log(g.piece + ' passed in ' + tag); open.delete(g.piece) }
    else open.set(g.piece, g.v.biggestGap)
  }
}

if (blocked) log('BLOCKED - a person has to decide: ' + blocked)
if (open.size && round >= 6) log('round cap hit with these still failing: ' + [...open.keys()].join(', '))

return { rounds: round, blocked, stillOpen: [...open.keys()], history }
```

## Rules for what you fill in

- **Bake the bar in as a fetchable thing.** Absolute path, URL, repo, product name.
- **Give the builder the destination, not the route.** No file layout, no module list, no API shape, no library choice beyond the fixed constraints. Every extra line is one fewer decision the builder makes, and one fewer thing the critic can find.
- **Name the instrument, not the intention.** "Inspects the real output" becomes real when you write the command, the tool, or the measurement. Put it in `INSTRUMENT` once; do not restate it per agent.
- **Never give a critic the builder's return value.** The pipeline stage receives it - ignore it, as the template does with `_built`.
- **For anything visual, make the comparison blind.** Build a composite of ours and the reference with the labels stripped and the answer in a separate key file. Tell the critic to write its pick down before reading the key, and to report both. A sighted A/B is not an A/B.
- **Add tool names only if the goal needs them** - a browser, an image generator, a deploy target.
- Everything else stays out.

## The outer loop

The exit is **every piece passing**, or the user stopping the run. Never a round count.

The `round < 6` in the template is a runaway guard, not the exit. When it fires, the script logs what is still failing - it must never return looking like success. Prefer the budget form when the user gave a token target:

```js
while (open.size && !blocked && budget.total && budget.remaining() > 200_000) {
```

Guard on `budget.total`: with no target set, `remaining()` is `Infinity` and only the round cap stops the loop.

`BLOCKED` ends the run and hands back to a person. It is not a failure of the work and it is not something a critic resolves by looking harder - looking harder is exactly what produces an invented answer. Only include the check when the bar has undecided items.

Concurrency is capped around ten agents at once, and this session may carry a workflow size guideline. Six rounds over five pieces is sixty agents. Say the arithmetic out loud to the user before you run it.

## What breaks a gauntlet workflow

- **A vague bar.** The critic invents a comparison and passes round one. Most common failure by far, and here it fails silently and expensively.
- **No rework edge.** A script that builds, critiques, and returns is a waterfall with a QA gate. The gap has to reach the next builder prompt, or nothing loops.
- **Over-specified builder prompts.** Naming the files and the function signatures turns builders into typists and leaves critics nothing to find. The symptom is round one passing everything.
- **The critic seeing the builder's work product instead of the artifact.** It must open the running thing, not the report.
- **Deleting a piece from `open` on anything but every row passing.** Partial credit is how a gauntlet loop quietly stops being one.
- **Looping on `confirmed` instead of `open`.** Pieces a critic rejected must come back; pieces it passed must not.
- **A fixed round count as the goal.** The cap is a guard. If you find yourself choosing it to control cost, use the budget form instead and say so.
