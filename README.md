# AI Skills

A personal library of reusable AI agent **skills** — each a self-contained directory under [`skills/`](skills/) with a `SKILL.md` that tells an agent when and how to apply it.

## What's a skill?

A skill is a directory containing a `SKILL.md` with YAML frontmatter (`name`, `description`, optional invocation hints) followed by the instructions themselves. Supporting files — references, templates, scripts, and per-provider `agents/` configs — live alongside it. Agents load a skill when its `description` matches the task at hand.

## Skills

| Skill | What it does |
| --- | --- |
| [`azure-devops`](skills/azure-devops/) | Open and update Azure DevOps PRs and work items through the REST API. |
| [`conventional-commits`](skills/conventional-commits/) | Write and evaluate commit messages against Conventional Commits 1.0.0. |
| [`harness`](skills/harness/) | Verify a feature locally with ii-test-harness: workspace, runtime, scenario first, accept, attach the report. |
| [`review-pr`](skills/review-pr/) | Review an Azure DevOps PR as a visual Artifact page with CI results. |
| [`subagent-orchestration`](skills/subagent-orchestration/) | Rules for model, effort, review and test gates in subagent work. |
| [`write-pull-requests`](skills/write-pull-requests/) | Draft and verify clear PR titles and descriptions. |

## Install

Clone the repo, then run `install.sh`. It points each agent harness's skills directory at `skills/` with one directory-level link.

```sh
git clone git@github.com:jonnyasmith/skills.git ~/dev/skills
cd ~/dev/skills
./install.sh
```

| Link | Read by |
| --- | --- |
| `~/.claude/skills` | Claude Code |
| `~/.agents/skills` | Codex, Pi, omp, and other tools that read the shared path |

The script also removes this repo's old links in `~/.codex/skills`, `~/.pi/agent/skills` and `~/.omp/skills`. Those tools read `~/.agents/skills`, so the copies would load each skill twice.

### Notes

- This repo is the only place skills live. When an agent creates a skill in its own skills directory, the skill lands in `skills/` and shows in `git status`. Commit it here.
- Changes need no re-run, because every link points at the live directory. Re-run only on a new machine or after adding a harness.
- Re-running is safe. A skills directory that holds anything other than links into this repo is reported and left alone.
- Other tools also write into these directories, so their files land in `skills/`. `.gitignore` excludes the known ones: Claude's `synced/` account skills and Omarchy's `omarchy` and `diagnose-crash` links.
- Per-harness differences live inside the skill: Claude settings in the `SKILL.md` frontmatter, Codex settings in `agents/openai.yaml`, and short per-harness notes in the `SKILL.md` body.

## Checks

`./skills.py check` validates every skill. It needs [uv](https://docs.astral.sh/uv/). `install.sh` sets `core.hooksPath` to `.githooks`, so the check also runs before each commit.

- `name` and `description` follow the [Agent Skills spec](https://agentskills.io/specification): the name matches the directory, and the description is 1,024 characters or fewer. The official `skills-ref` validator is not used, because it rejects harness fields such as `disable-model-invocation`.
- Unknown frontmatter fields are errors.
- `agents/openai.yaml` has an `interface` block, and its `policy` matches the frontmatter.
- A real skill directory in `~/.codex/skills`, `~/.pi/agent/skills` or `~/.omp/agent/skills` is a warning. An agent wrote it outside this repo. Move it into `skills/` to keep it.

### Manual-only skills

Set `disable-model-invocation: true` in `SKILL.md` frontmatter, then run `./skills.py fix`. The frontmatter is the only source. `fix` writes the Codex equivalent (`policy.allow_implicit_invocation`) into `agents/openai.yaml`, so do not edit that value by hand.

| Harness | Reads | Enforced |
| --- | --- | --- |
| Claude Code | `disable-model-invocation` | Yes |
| Pi | `disable-model-invocation` | Yes |
| Codex | `agents/openai.yaml` policy | Yes |
| omp | `disable-model-invocation` | No. Its docs say the field is kept as metadata only. |

## Archive

Retire a skill with `git mv skills/<name> archive/<name>`. Nothing in `archive/` is linked, so no harness loads it. To use one again, `git mv` it back to `skills/`.

The manual-only skills are archived because harnesses still read them without being asked.

| Skill | What it does |
| --- | --- |
| [`build-change`](archive/build-change/) | Build a change from its `plan.html` through an implement, critique and fix workflow. |
| [`code-review`](archive/code-review/) | Two-axis (standards + spec) review of a diff, run as parallel sub-agents. |
| [`codebase-design`](archive/codebase-design/) | Shared vocabulary for designing deep modules. |
| [`deslop`](archive/deslop/) | Remove AI-generated code slop and clean up style. |
| [`dev-wiki`](archive/dev-wiki/) | Query your personal dev-wiki as a read-only knowledge source. |
| [`diagnosing-bugs`](archive/diagnosing-bugs/) | Diagnosis loop for hard bugs and performance regressions. |
| [`discovery`](archive/discovery/) | Build a visual, evidence-backed architecture discovery report. |
| [`domain-modeling`](archive/domain-modeling/) | Build and sharpen a project's domain model and decisions. |
| [`excalidraw-diagram`](archive/excalidraw-diagram/) | Create Excalidraw diagram JSON that argues visually. |
| [`gauntlet-workflow`](archive/gauntlet-workflow/) | Run a gauntlet loop as a deterministic Workflow script. |
| [`graph-spec`](archive/graph-spec/) | Turn a job into a paste-ready GRAPH SPEC prompt for a fleet. |
| [`grill-with-docs`](archive/grill-with-docs/) | Grilling session that also writes ADRs and a glossary. |
| [`grilling`](archive/grilling/) | Stress-test thinking, one round of unblocked questions at a time. |
| [`handoff`](archive/handoff/) | Compact a conversation into a handoff document for another agent. |
| [`html-artifact`](archive/html-artifact/) | Render a deliverable as one self-contained HTML file. |
| [`implement`](archive/implement/) | Implement work from a spec or set of tickets. |
| [`implementation-loop`](archive/implementation-loop/) | Implement a spec's tickets one at a time in dependency order. |
| [`improve-codebase-architecture`](archive/improve-codebase-architecture/) | Surface deepening opportunities as a visual report, then grill one. |
| [`improve-test-suite`](archive/improve-test-suite/) | Audit a test suite for seam quality and coverage gaps. |
| [`interrogate`](archive/interrogate/) | Interrogate a known design's edges and emit the answer key. |
| [`know-your-unknowns`](archive/know-your-unknowns/) | Buy the cheapest answer to what you don't know about a piece of work. |
| [`omarchy-extensions`](archive/omarchy-extensions/) | Add a feature to an Omarchy desktop on the cheapest surface that works. |
| [`orchestrator-loop`](archive/orchestrator-loop/) | Drive a batch of workitems to commits via fresh sub-agents. |
| [`prototype`](archive/prototype/) | Build throwaway code to answer a design question. |
| [`research`](archive/research/) | Investigate a question against primary sources, capture findings. |
| [`resolving-merge-conflicts`](archive/resolving-merge-conflicts/) | Resolve an in-progress merge/rebase conflict. |
| [`sdlc`](archive/sdlc/) | Router for the AI-native SDLC planning chain, and its shared HTML artifact rules. |
| [`setup-repo-skills`](archive/setup-repo-skills/) | Scaffold a repo's `AGENTS.md` routing, tracker, and docs layout. |
| [`survey`](archive/survey/) | Survey an idea whose route isn't visible, and emit the answer key. |
| [`tdd`](archive/tdd/) | Test-driven development reference and loop. |
| [`to-gauntlet`](archive/to-gauntlet/) | Turn an answer key into a paste-ready gauntlet prompt and driver. |
| [`to-design`](archive/to-design/) | Turn an accepted `intent.html` into `spec.html` under the policy skills. |
| [`to-intent`](archive/to-intent/) | Turn a conversation into `intent.html`, the proto-spec that starts a change. |
| [`to-plan`](archive/to-plan/) | Turn a plan approved in plan mode into `plan.html`. |
| [`to-spec`](archive/to-spec/) | Turn a conversation into a spec and publish to the tracker. |
| [`to-tickets`](archive/to-tickets/) | Break a plan into tracer-bullet tickets with blocking edges. |
| [`triage`](archive/triage/) | Move issues and external PRs through a triage state machine. |
| [`writing-great-skills`](archive/writing-great-skills/) | Reference for writing predictable skills. |
