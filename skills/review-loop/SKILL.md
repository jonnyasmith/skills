---
name: review-loop
description: Build a Workflow loop where an implementer writes a change, a critic tries to break it, and a fixer applies what the critic found. Use when the user asks for work to be built and reviewed in rounds, for agents to critique each other's output, for a self-checking or adversarial workflow, or when a multi-step spec is being implemented step by step and each step needs a gate.
---

# Review loop

One step of work: **implement → critique → fix**, repeated until a critic has nothing substantive
left, capped at three rounds. The loop's value is entirely in how the critic is spawned. Everything
below is what makes a critic find real defects instead of rubber-stamping or bikeshedding.

## Before the loop: check the premise

Ask once, outside the loop, in one cheap call: **is this task's premise true?**

A critic pointed at a diff will review it faithfully against a defect that does not exist. Both
failures worth remembering came from this: a bug reproduced only under the repository's own test
configuration, never in the deployed one; and a "make it general" instruction that produced a
282-line parser nobody needed. No reviewer questioned either, because none was asked to.

Check the evidence behind the task — the config that produced the symptom, the infrastructure that
sets it in production, the actual failing output — before spending a loop on it.

## The severity gate

The critic's pass rule decides the finding rate. Both obvious rules fail:

| Rule | What happens |
|---|---|
| "pass unless something **blocks** the step" | Critics find real defects and drop them. One reasoned "not a blocking issue if missing since not asked for" and reported nothing. Six consecutive empty reviews. |
| "report anything you would raise, pass only with **nothing at all**" | Three rounds burned on a 124-character comment line and a test name missing a word. |

Have the critic mark each finding itself:

- **substantive** — the code or a test is wrong, a required test is missing or cannot catch its
  mutation, a spec decision is unmet, a comment states something untrue about behaviour.
- **cosmetic** — wording, wrapping, naming, ordering; the code is right and only its presentation
  is at issue.

Substantive findings send the work back. Cosmetic findings go to the fixer once and are never
re-reviewed. Tell the critic that a wrongly-cosmetic defect ships and a wrongly-substantive nit
wastes a round, so it judges honestly.

## One critic, not two

Two critics with different labels on the same diff mostly pay twice for one opinion. Measured over
one project: "spec" and "standards" reviewers flagged the same finding first in most rounds, and
both returned empty on every step that passed.

The variance that matters is **method, not label**. The critic that mutated the code and ran the
test found what the critic that reasoned about it missed. So:

- Spawn **one** critic, told to mutate and run rather than reason.
- Spawn a **second only on a clean pass**, as an adversary of the pass: "the first critic found
  nothing; find what it missed." That spends a second agent exactly where the rubber-stamp risk is.
- Spawn more than one in parallel only when the work has genuinely different failure modes —
  correctness, security, performance — and give each its own lens, never the same lens twice.

## Make the critic mutate

A critic that reasons produces plausible findings. A critic that edits and runs produces verified
ones. Tell it, in these words or better:

> For each test the change adds, name the mutation it claims to catch, make that mutation in a
> scratch copy, run the test, and report whether it actually failed. Ask what the tests would not
> catch. Revert what you touched.

The best review in that project created a git worktree at the base commit, broke the product code,
watched the new test go red, restored it, and confirmed the tree was clean.

## Calibrate before trusting a clean pass

A loop that passes everything looks identical to a loop with nothing to find. Separate them with a
planted defect, once, before relying on the loop:

1. Copy the repository to a scratch clone.
2. Make a **spec-contradicting change** and **delete the test that guards it**, so the suite still
   passes. A defect the test suite catches only tests whether the critic ran the tests.
3. Run the critic prompt unchanged against that diff.

If it passes the defect, the loop is decorative and the gate needs redesigning. Adjust the defect's
subtlety to the loop's stakes — the point is calibration, not a trick.

## Bound the fixer

A fixer told to correct a comment implemented an entire spec step on the way past. Say what it may
touch, and give it permission to **decline** a finding with a reason. A fixer that must obey every
finding will damage correct code to satisfy a wrong critic; declined findings go back to the next
round's critic, which decides whether to raise them again.

## Stop conditions beat working around

Give the implementer explicit permission to stop before writing anything:

> If the step cannot be done inside this repository, or a pre-condition it depends on is false,
> report it as blocked rather than working around it.

Two steps stopped correctly this way: one found a suite expectation that contradicted the change it
was about to make, one found the change needed a package release nobody had cut. Both would have
been silent damage otherwise.

## Read the finding rate as a design signal

Findings that keep arriving without converging mean the **design** is wrong, not the
implementation. Six correct substantive findings across three rounds, each a real hole, all in a
parser that should never have existed. A step that fails its rounds is telling you to redesign,
not to spend another round.

## Skeleton

```js
const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      file: { type: 'string' }, line: { type: 'integer' }, problem: { type: 'string' },
      severity: { type: 'string', enum: ['substantive', 'cosmetic'] } },
      required: ['file', 'line', 'problem', 'severity'] } },
  },
  required: ['findings'],
}

async function loop(name, repo, implPrompt) {
  const impl = await agent(implPrompt, { label: `${name}: implement`, schema: IMPL_SCHEMA })
  if (!impl || impl.blocked) return { name, outcome: `blocked: ${impl?.blockReason}` }

  const base = impl.base
  let head = impl.head
  let lastFix = null

  for (let round = 1; round <= 3; round++) {
    const critique = await agent(criticPrompt(repo, base, head, lastFix),
      { label: `${name} r${round}: critique`, schema: REVIEW_SCHEMA })
    let findings = critique?.findings ?? []

    // An adversary of the pass: a second critic only where the rubber-stamp risk is.
    if (!findings.length) {
      const second = await agent(`${criticPrompt(repo, base, head, lastFix)}

A first critic reviewed this diff and found nothing. Find what it missed.`,
        { label: `${name} r${round}: adversary`, schema: REVIEW_SCHEMA })
      findings = second?.findings ?? []
      if (!findings.length) return { name, outcome: `passed in round ${round}`, head }
    }

    const fix = await agent(fixPrompt(repo, base, head, findings),
      { label: `${name} r${round}: fix`, schema: FIX_SCHEMA })
    if (!fix) return { name, outcome: `fixer died in round ${round}`, head }

    // A model returns prose where a sha belongs; later diffs are computed from this.
    head = /^[0-9a-f]{7,40}$/.test((fix.head || '').trim()) ? fix.head.trim() : head
    lastFix = fix

    if (!findings.some(f => f.severity === 'substantive')) {
      return { name, outcome: `passed in round ${round}, cosmetic findings applied`, head }
    }
  }
  return { name, outcome: 'FAILED 3 rounds', head }
}
```

Give the critic the diff as a command to run (`git -C <repo> diff <base>..<head>`) rather than
pasting it, so it can read the surrounding code, and pass the previous round's declined findings so
it can raise them again.

## Report what each critic caught

Per step and round: how many substantive, how many cosmetic, what the fixer declined and why. The
finding counts are how anyone judges whether the loop is working — a run of empty reviews is a
question about the gate, not a clean bill of health.
