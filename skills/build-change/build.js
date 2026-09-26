export const meta = {
  name: 'build-change',
  description: 'Build a change from its plan.html: implement, check, adversarially review and fix each step until the reviewer finds nothing left',
  whenToUse: 'Run by the build-change skill with args {repo, slug, base, steps, checks, maxRounds}',
  phases: [
    { title: 'Build', detail: 'per plan step: tests and implement, checks, critic, fixer, until clean' },
    { title: 'Final review', detail: 'the whole change against every requirement and Proof item' },
  ],
}

// args: {
//   repo: absolute path of the repository,
//   slug: the change slug (changes/<slug>/),
//   base: commit the run starts from,
//   steps: [{ id, title }] from plan.html's Order of work, in order,
//   checks: [command] run from the repo root, each exits non-zero on failure,
//   maxRounds: review rounds per step before it is split (default 4),
// }
const { repo, slug, steps, checks } = args
const MAX_ROUNDS = args.maxRounds || 4
const CHANGE = `${repo}/changes/${slug}`

const SHA = /^[0-9a-f]{7,40}$/

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

const CHECKS_SCHEMA = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    failures: { type: 'array', items: { type: 'object', properties: {
      command: { type: 'string' }, exitCode: { type: 'integer' }, output: { type: 'string' } },
      required: ['command', 'exitCode', 'output'] } },
  },
  required: ['pass', 'failures'],
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
      severity: { type: 'string', enum: ['substantive', 'cosmetic'] } },
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

const SPLIT_SCHEMA = {
  type: 'object',
  properties: {
    steps: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' }, title: { type: 'string' } },
      required: ['id', 'title'] } },
  },
  required: ['steps'],
}

const checkList = checks.map(c => `- \`${c}\``).join('\n')

function scopeOf(unit) {
  return unit.final
    ? `the whole change: every requirement in ${CHANGE}/spec.html and every Proof item in ${CHANGE}/plan.html`
    : `step ${unit.id}, "${unit.title}", of the Order of work in ${CHANGE}/plan.html, and the requirements in ${CHANGE}/spec.html and Proof items in plan.html that this step covers`
}

function implPrompt(unit, base) {
  return `Implement ${scopeOf(unit)}. Repository: ${repo}, on the current branch, at ${base}.
${unit.parent ? `\nThis is part of step ${unit.parent}, which was split because it failed review. Earlier parts are already committed.\n` : ''}
Read ${CHANGE}/spec.html and ${CHANGE}/plan.html first. Do only this step; later steps belong to other workers.

1. Write the tests that prove this step's Proof items. Run them and see them fail.
2. Implement until they pass. Do not edit those tests to make them pass; if a test is wrong, fix the test and say why in the commit message.
3. Run every check and make them pass:
${checkList}
4. If the work has to depart from plan.html, update plan.html in the same commit to say what changed and why.
5. Commit everything with \`git -C ${repo} commit\`, message \`feat(${slug}): ${unit.title}\`.

If the step cannot be done inside this repository, or a pre-condition it depends on is false, report status "blocked" with the reason rather than working around it. Return the full sha of HEAD.`
}

function checksPrompt() {
  return `In ${repo}, run each command from the repository root, in order, and report its exit code:
${checkList}

Change nothing. For each command that exits non-zero, report the command, its exit code and the last 40 lines of its output.
Then run \`git -C ${repo} status --porcelain\`. If it prints anything, add a failure with command "git status --porcelain", exit code 1 and that output: work that is not committed is not done.
pass is true only when there are no failures.`
}

function criticPrompt(unit, base, head, declined) {
  const declinedText = declined.length
    ? `\nThe fixer declined these findings last round. Rule on each: raise it again only if the reason does not hold.\n${declined.map(d => `- ${d.problem} (declined: ${d.reason})`).join('\n')}\n`
    : ''
  return `You are reviewing ${scopeOf(unit)}, in ${repo}. You did not write this code and have no stake in it. Find the reasons it should not be accepted.

The change is \`git -C ${repo} diff ${base}..${head}\`. Read every changed file in full, and two or three neighbouring files of the same kind so you judge against what this repository actually does.
${declinedText}
Check, in this order:
1. **Complete.** For every requirement and Proof item in scope, find the code and the test that meet it. Anything in scope that is not met is a substantive finding, placed at the file and line where it belongs.
2. **Tests catch what they claim.** For each test the change adds, name the mutation it claims to catch. Make that mutation in a scratch worktree (\`git -C ${repo} worktree add <tmp> ${head}\`), run the test, and record whether it failed. Remove the worktree afterwards. A test that stays green under its mutation is a substantive finding.
3. **Correct.** Edge cases, error paths, concurrency, security, and the rules in CLAUDE.md.

Leave ${repo} exactly as you found it. You change nothing there.

Mark each finding:
- **substantive**: the code or a test is wrong, a required test is missing or cannot catch its mutation, a requirement or Proof item is unmet, or a comment states something untrue about behaviour.
- **cosmetic**: wording, naming, wrapping, ordering; the code is right and only its presentation is at issue.
A defect wrongly marked cosmetic ships. A nit wrongly marked substantive wastes a round. Judge honestly.

Every finding names a file, a line, the requirement or rule it breaks, and the evidence: what you ran or read. Return an empty list only when nothing in scope is unmet or wrong.`
}

const ADVERSARY = `\n\nA first reviewer checked this change and found nothing. Assume it missed something. Find what it missed.`

function fixPrompt(unit, head, findings, fromChecks) {
  const decline = fromChecks
    ? 'These are failing checks. Fix every one; none can be declined.'
    : 'For each finding, fix it or decline it. Decline only with evidence: a file and line showing the claim is wrong, a test that proves the behaviour, or a rule in CLAUDE.md or spec.html that sanctions the current code. "I think it is fine" is not a reason.'
  return `You are fixing ${scopeOf(unit)}, in ${repo}, at ${head}.

${decline}

Findings:
${JSON.stringify(findings, null, 2)}

Fix the root cause, not the symptom. Change only what the findings require. Do not edit a test unless the finding is about that test. If a fix departs from ${CHANGE}/plan.html, update plan.html in the same commit.
Run every check afterwards and make them pass:
${checkList}
Commit with \`git -C ${repo} commit\`, message \`fix(${slug}): <root cause in a few words>\`.

Return the full sha of HEAD, the findings you declined with the reason, and for each substantive finding you fixed, one sentence that would have prevented it.`
}

function splitPrompt(unit, head, lastFindings) {
  return `Step ${unit.id}, "${unit.title}", of ${CHANGE}/plan.html failed review ${MAX_ROUNDS} times. The repository ${repo} is at ${head} with the partial work committed.

The last findings were:
${JSON.stringify(lastFindings, null, 2)}

Read spec.html, plan.html and the current code. Split what remains of this step into two to four smaller steps, in order, each small enough that a fresh worker can finish and prove it alone. Give each an id of the form "${unit.id}.1", "${unit.id}.2" and a title that says what it delivers. Change no files.`
}

function sha(value, fallback) {
  const v = (value || '').trim()
  return SHA.test(v) ? v : fallback
}

// Checks, then critic (and an adversary on a clean pass), then fixer, until clean or out of rounds.
async function reviewLoop(unit, base, head, phase) {
  const rounds = []
  const lessons = []
  let declined = []
  let lastFindings = []
  let cosmeticOnly = false
  const tag = unit.final ? 'final' : `step ${unit.id}`

  for (let round = 1; round <= MAX_ROUNDS; round++) {
    const chk = await agent(checksPrompt(), { label: `${tag} r${round}: checks`, phase, schema: CHECKS_SCHEMA, effort: 'low' })
    const checksPass = !!chk && chk.pass && chk.failures.length === 0
    if (checksPass && cosmeticOnly) {
      rounds.push({ round, checks: 'pass', substantive: 0, cosmetic: 0, declined: 0 })
      return { ok: true, head, rounds, lessons }
    }

    let findings
    if (!checksPass) {
      findings = (chk ? chk.failures : [{ command: 'checks', exitCode: 1, output: 'the checks agent returned nothing' }])
        .map(f => ({ file: '', line: 0, requirement: 'every check passes', problem: `\`${f.command}\` exited ${f.exitCode}`, evidence: f.output, severity: 'substantive' }))
    } else {
      const critic = await agent(criticPrompt(unit, base, head, declined), { label: `${tag} r${round}: critic`, phase, schema: REVIEW_SCHEMA })
      if (!critic) return { ok: false, head, rounds, lessons, outcome: `critic died in round ${round}` }
      findings = critic.findings
      if (!findings.length) {
        const adversary = await agent(criticPrompt(unit, base, head, declined) + ADVERSARY, { label: `${tag} r${round}: adversary`, phase, schema: REVIEW_SCHEMA })
        findings = adversary ? adversary.findings : []
        if (!findings.length) {
          rounds.push({ round, checks: 'pass', substantive: 0, cosmetic: 0, declined: 0 })
          return { ok: true, head, rounds, lessons }
        }
      }
    }

    const substantive = findings.filter(f => f.severity === 'substantive').length
    const fix = await agent(fixPrompt(unit, head, findings, !checksPass), { label: `${tag} r${round}: fix`, phase, schema: FIX_SCHEMA })
    if (!fix) return { ok: false, head, rounds, lessons, outcome: `fixer died in round ${round}` }

    head = sha(fix.head, head)
    declined = fix.declined
    lessons.push(...fix.lessons)
    lastFindings = findings
    rounds.push({ round, checks: checksPass ? 'pass' : 'fail', substantive, cosmetic: findings.length - substantive, declined: fix.declined.length, declinedFindings: fix.declined })
    log(`${tag} round ${round}: ${checksPass ? `${substantive} substantive, ${findings.length - substantive} cosmetic, ${fix.declined.length} declined` : `${findings.length} failing checks`}`)

    // Cosmetic findings are fixed once and never re-reviewed; the next round only re-runs the checks.
    cosmeticOnly = checksPass && substantive === 0
  }
  return { ok: false, head, rounds, lessons, lastFindings, outcome: `not clean after ${MAX_ROUNDS} rounds` }
}

async function buildUnit(unit, base) {
  const impl = await agent(implPrompt(unit, base), { label: `step ${unit.id}: implement`, phase: 'Build', schema: IMPL_SCHEMA })
  if (!impl) return { id: unit.id, title: unit.title, ok: false, head: base, outcome: 'implementer died' }
  if (impl.status === 'blocked') return { id: unit.id, title: unit.title, ok: false, blocked: true, head: base, outcome: `blocked: ${impl.blockReason || 'no reason given'}` }

  const head = sha(impl.head, base)
  const result = await reviewLoop(unit, base, head, 'Build')
  return { id: unit.id, title: unit.title, departures: impl.departures || '', ...result, outcome: result.outcome || `passed in round ${result.rounds.length}` }
}

const results = []
let head = args.base
let halted = null

for (const step of steps) {
  phase('Build')
  const result = await buildUnit(step, head)
  results.push(result)
  head = result.head

  if (result.ok) {
    log(`✓ step ${step.id} ${step.title}: ${result.outcome}`)
    continue
  }
  if (result.blocked || !result.lastFindings) {
    halted = { step: step.id, reason: result.outcome }
    break
  }

  // One split, then stop: findings that keep coming mean the design is wrong, not the implementation.
  log(`step ${step.id} failed review ${MAX_ROUNDS} times; splitting it`)
  const split = await agent(splitPrompt(step, head, result.lastFindings), { label: `step ${step.id}: split`, phase: 'Build', schema: SPLIT_SCHEMA })
  if (!split || !split.steps.length) {
    halted = { step: step.id, reason: 'failed review and could not be split' }
    break
  }
  for (const sub of split.steps) {
    const subResult = await buildUnit({ ...sub, parent: step.id }, head)
    results.push(subResult)
    head = subResult.head
    if (!subResult.ok) {
      halted = { step: sub.id, reason: `${subResult.outcome} (after splitting step ${step.id})` }
      break
    }
    log(`✓ step ${sub.id} ${sub.title}: ${subResult.outcome}`)
  }
  if (halted) break
}

let final = null
if (!halted) {
  phase('Final review')
  final = await reviewLoop({ final: true, id: 'final', title: 'the whole change' }, args.base, head, 'Final review')
  head = final.head
  if (!final.ok) halted = { step: 'final', reason: final.outcome }
}

return {
  complete: !halted,
  halted,
  base: args.base,
  head,
  steps: results.map(r => ({ id: r.id, title: r.title, outcome: r.outcome, departures: r.departures || '', rounds: r.rounds || [] })),
  final: final && { outcome: final.ok ? `passed in round ${final.rounds.length}` : final.outcome, rounds: final.rounds },
  lessons: results.flatMap(r => r.lessons || []).concat(final ? final.lessons : []),
}
