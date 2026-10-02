// build-change workflow for omp. An async function body: SKILL.md's eval cell (language "js", timeout: 0)
// runs it with (args, agent, phase, log) from the eval prelude.

// args: {
//   repo: absolute path of the repository,
//   slug: the change slug (changes/<slug>/),
//   base: commit the run starts from; the final review diffs against it,
//   head: commit to build the first listed step on (default base); set it with the remaining steps to resume,
//   steps: [{ id, title }] from plan.html's Order of work, in order,
//   check: the one command check-gate.py runs before every commit; it exits non-zero on failure,
//   maxRounds: review rounds per step before the run halts (default 4),
// }
// Every commit passes the check: the check-gate PreToolUse hook blocks any commit while it fails.
// So the loop never runs the check itself, and a critic can rely on every commit it reviews.
const { repo, slug, steps, check } = args
const MAX_ROUNDS = args.maxRounds || 4
const CHANGE = `${repo}/changes/${slug}`

const SHA = /^[0-9a-f]{7,40}$/

// omp's agent() returns a handle; wait() returns the schema-parsed result and throws when the agent fails.
// Return null on failure, so a dead agent halts the step.
async function spawn(prompt, { label, schema, kind }) {
  try {
    return await agent(prompt, { agent: kind, label, schema }).wait()
  } catch (err) {
    log(`${label}: agent failed: ${err?.message ?? err}`)
    return null
  }
}

const IMPL_SCHEMA = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['done', 'blocked'] },
    blockReason: { type: 'string' },
    head: { type: 'string', description: 'full sha of HEAD after your commit' },
    departures: { type: 'string', description: 'how the work departed from plan.html, or empty' },
  },
  required: ['status', 'head'],
}

const REVIEW_SCHEMA = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: { type: 'object', properties: {
      file: { type: 'string' },
      line: { type: 'integer' },
      requirement: { type: 'string', description: 'the spec requirement, Proof item or rule this breaks' },
      problem: { type: 'string' },
      evidence: { type: 'string', description: 'what you ran or read that shows it' },
      severity: { type: 'string', enum: ['substantive', 'cosmetic', 'spec-gap'] } },
      required: ['file', 'line', 'requirement', 'problem', 'evidence', 'severity'] } },
  },
  required: ['findings'],
}

const FIX_SCHEMA = {
  type: 'object',
  properties: {
    head: { type: 'string', description: 'full sha of HEAD after your commit' },
    declined: { type: 'array', items: { type: 'object', properties: {
      problem: { type: 'string' }, reason: { type: 'string' } },
      required: ['problem', 'reason'] } },
    lessons: { type: 'array', items: { type: 'string' } },
  },
  required: ['head', 'declined', 'lessons'],
}

const COMMIT = `The repository's commit hook runs \`${check}\` and blocks the commit while it fails, so run it yourself first and make it pass. Never skip or work around the hook. After committing, \`git -C ${repo} status --porcelain\` must print nothing: uncommitted work is not done.`

function scopeOf(unit) {
  return unit.final
    ? `the whole change: every requirement in ${CHANGE}/spec.html and every Proof item in ${CHANGE}/plan.html`
    : `step ${unit.id}, "${unit.title}", of the Order of work in ${CHANGE}/plan.html, and the requirements in ${CHANGE}/spec.html and Proof items in plan.html that this step covers`
}

function implPrompt(unit, base) {
  return `Implement ${scopeOf(unit)}. Repository: ${repo}, on the current branch, at ${base}.

Read ${CHANGE}/spec.html and ${CHANGE}/plan.html first. Do only this step; later steps belong to other workers.

1. Write the tests that prove this step's Proof items. Run them and see them fail.
2. Implement until they pass. Do not edit those tests to make them pass; if a test is wrong, fix the test and say why in the commit message.
3. If the work has to depart from plan.html, update plan.html in the same commit to say what changed and why.
4. Commit everything with \`git -C ${repo} commit\`, message \`feat(${slug}): ${unit.title}\`. ${COMMIT}

If the step cannot be done inside this repository, or a pre-condition it depends on is false, report status "blocked" with the reason rather than working around it. Return the full sha of HEAD.`
}

const SEVERITY = `Mark each finding:
- **substantive**: it breaks a requirement in spec.html, a Proof item in plan.html, or a rule for code in AGENTS.md or CLAUDE.md, shown with a concrete input that the spec covers. A test meant to prove a requirement or Proof item that stays green under its mutation is substantive. So is a comment that states something untrue about behaviour.
- **cosmetic**: wording, naming, wrapping, ordering; the code is right and only its presentation is at issue.
- **spec-gap**: behaviour the spec does not define, such as an input or case it never mentions. These go to the user as questions about the spec; nobody changes code for them.
A defect wrongly marked cosmetic ships. A gap wrongly marked substantive sends the fixer past the spec and the review never ends. Judge honestly.

Review the code and tests only. Commit messages, history and process are not findings. The check command already passes on every commit, so do not report its result; if \`git -C ${repo} status --porcelain\` prints anything, that uncommitted work is substantive.
Every finding names a file, a line, the requirement or rule it breaks (or the case the spec leaves undefined), and the evidence: what you ran or read.`

// Round 1 (and any adversary) reviews the whole scope; later rounds verify the last fixes.
function criticPrompt(unit, base, head, prev) {
  const intro = `You are reviewing ${scopeOf(unit)}, in ${repo}. You did not write this code and have no stake in it. Leave ${repo} exactly as you found it: you change nothing there.`
  if (!prev) {
    return `${intro}

The change is \`git -C ${repo} diff ${base}..${head}\`. Read every changed file in full, and two or three neighbouring files of the same kind so you judge against what this repository actually does.

Check, in this order:
1. **Complete.** For every requirement and Proof item in scope, find the code and the test that meet it. Anything in scope that is not met is substantive, placed at the file and line where it belongs.
2. **Tests catch what they claim.** For each test that proves a requirement or Proof item, name the mutation it should catch. Make that mutation in a scratch worktree (\`git -C ${repo} worktree add <tmp> ${head}\`), run the test, and record whether it failed. Remove the worktree afterwards.
3. **Correct within the spec.** Inputs the spec covers, error paths it names, and the rules in AGENTS.md or CLAUDE.md.

${SEVERITY}

Return an empty list only when nothing in scope is unmet or wrong.`
  }
  const declined = prev.declined.length
    ? `\nThe fixer declined these, with its reasons. Uphold one only if the reason does not hold:\n${prev.declined.map(d => `- ${d.problem} (declined: ${d.reason})`).join('\n')}\n`
    : ''
  return `${intro}

Last round's review raised these findings:
${JSON.stringify(prev.findings, null, 2)}
${declined}
A fixer then changed the code: \`git -C ${repo} diff ${prev.from}..${head}\`.

1. **Verify each finding** at ${head}: re-run its evidence, or the mutation, and see whether it still holds. Return each finding that is not resolved, unchanged except for updated evidence.
2. **Review the fixer's diff** for anything it broke or got wrong.

Raise a new finding outside the fixer's diff only if it is substantive. This round checks the fixes; it is not a fresh review of the whole step.

${SEVERITY}

Return an empty list when every finding is resolved and the fixer's diff is sound.`
}

const ADVERSARY = `\n\nA first reviewer checked this change and found nothing substantive. Assume it missed something within the spec. Find what it missed.`

function fixPrompt(unit, head, findings) {
  return `You are fixing ${scopeOf(unit)}, in ${repo}, at ${head}.

For each finding, fix it or decline it. Decline only with evidence: a file and line showing the claim is wrong, a test that proves the behaviour, or a rule in AGENTS.md or CLAUDE.md or spec.html that sanctions the current code. "I think it is fine" is not a reason.

Findings:
${JSON.stringify(findings, null, 2)}

Fix the root cause, not the symptom. Change only what the findings require. Do not edit a test unless the finding is about that test. If a fix departs from ${CHANGE}/plan.html, update plan.html in the same commit.
Commit with \`git -C ${repo} commit\`, message \`fix(${slug}): <root cause in a few words>\`. ${COMMIT}

Return the full sha of HEAD, the findings you declined with the reason, and for each substantive finding you fixed, one sentence that would have prevented it.`
}

function sha(value, fallback) {
  const v = (value || '').trim()
  return SHA.test(v) ? v : fallback
}

// Critic (and an adversary on a clean pass), then fixer, until clean or out of rounds.
// Spec gaps are collected for the user and never sent to the fixer.
async function reviewLoop(unit, base, head, phase) {
  const rounds = []
  const lessons = []
  const gaps = []
  let prev = null
  let lastFindings = []
  const tag = unit.final ? 'final' : `step ${unit.id}`
  const actionable = fs => fs.filter(f => f.severity !== 'spec-gap')
  const keepGaps = fs => gaps.push(...fs.filter(f => f.severity === 'spec-gap'))

  for (let round = 1; round <= MAX_ROUNDS; round++) {
    const critic = await spawn(criticPrompt(unit, base, head, prev), { label: `${tag} r${round}: ${prev ? 'verify' : 'critic'}`, schema: REVIEW_SCHEMA, kind: 'task' })
    if (!critic) return { ok: false, head, rounds, lessons, gaps, outcome: `critic died in round ${round}` }
    keepGaps(critic.findings)
    let findings = actionable(critic.findings)
    if (!findings.length) {
      const adversary = await spawn(criticPrompt(unit, base, head, null) + ADVERSARY, { label: `${tag} r${round}: adversary`, schema: REVIEW_SCHEMA, kind: 'task' })
      if (adversary) keepGaps(adversary.findings)
      findings = adversary ? actionable(adversary.findings) : []
      if (!findings.length) {
        rounds.push({ round, substantive: 0, cosmetic: 0, declined: 0 })
        return { ok: true, head, rounds, lessons, gaps }
      }
    }

    const substantive = findings.filter(f => f.severity === 'substantive').length
    const fix = await spawn(fixPrompt(unit, head, findings), { label: `${tag} r${round}: fix`, schema: FIX_SCHEMA, kind: 'builder' })
    if (!fix) return { ok: false, head, rounds, lessons, gaps, outcome: `fixer died in round ${round}` }

    prev = { findings, declined: fix.declined, from: head }
    head = sha(fix.head, head)
    lessons.push(...fix.lessons)
    lastFindings = findings
    rounds.push({ round, substantive, cosmetic: findings.length - substantive, declined: fix.declined.length, declinedFindings: fix.declined })
    log(`${tag} round ${round}: ${substantive} substantive, ${findings.length - substantive} cosmetic, ${fix.declined.length} declined`)

    // Cosmetic findings are fixed once and never re-reviewed. The hook has already checked the fix's commit.
    if (substantive === 0) return { ok: true, head, rounds, lessons, gaps }
  }
  return { ok: false, head, rounds, lessons, gaps, lastFindings, outcome: `not clean after ${MAX_ROUNDS} rounds` }
}

async function buildUnit(unit, base) {
  const impl = await spawn(implPrompt(unit, base), { label: `step ${unit.id}: implement`, schema: IMPL_SCHEMA, kind: 'builder' })
  if (!impl) return { id: unit.id, title: unit.title, ok: false, head: base, outcome: 'implementer died' }
  if (impl.status === 'blocked') return { id: unit.id, title: unit.title, ok: false, blocked: true, head: base, outcome: `blocked: ${impl.blockReason || 'no reason given'}` }

  const head = sha(impl.head, base)
  const result = await reviewLoop(unit, base, head, 'Build')
  return { id: unit.id, title: unit.title, departures: impl.departures || '', ...result, outcome: result.outcome || `passed in round ${result.rounds.length}` }
}

const results = []
let head = args.head || args.base
let halted = null

for (const step of steps) {
  phase('Build')
  const result = await buildUnit(step, head)
  results.push(result)
  head = result.head
  if (!result.ok) {
    halted = { step: step.id, reason: result.outcome, findings: result.lastFindings || [] }
    break
  }
  log(`✓ step ${step.id} ${step.title}: ${result.outcome}`)
}

let final = null
if (!halted) {
  phase('Final review')
  final = await reviewLoop({ final: true, id: 'final', title: 'the whole change' }, args.base, head, 'Final review')
  head = final.head
  if (!final.ok) halted = { step: 'final', reason: final.outcome, findings: final.lastFindings || [] }
}

return {
  complete: !halted,
  halted,
  base: args.base,
  head,
  steps: results.map(r => ({ id: r.id, title: r.title, outcome: r.outcome, departures: r.departures || '', rounds: r.rounds || [] })),
  final: final && { outcome: final.ok ? `passed in round ${final.rounds.length}` : final.outcome, rounds: final.rounds },
  lessons: results.flatMap(r => r.lessons || []).concat(final ? final.lessons : []),
  specGaps: results.flatMap(r => r.gaps || []).concat(final ? final.gaps : []),
}
