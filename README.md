# AI Skills

A personal library of reusable AI agent **skills** — each a self-contained directory under [`skills/`](skills/) with a `SKILL.md` that tells an agent when and how to apply it.

## What's a skill?

A skill is a directory containing a `SKILL.md` with YAML frontmatter (`name`, `description`, optional invocation hints) followed by the instructions themselves. Supporting files — references, templates, scripts, and per-provider `agents/` configs — live alongside it. Agents load a skill when its `description` matches the task at hand.

## Skills

| Skill | What it does |
| --- | --- |
| [`azure-devops`](skills/azure-devops/) | Open and update Azure DevOps PRs and work items through the REST API. |
| [`build-change`](skills/build-change/) | Build a change from its `plan.html` through an implement, critique and fix workflow. |
| [`code-review`](skills/code-review/) | Two-axis (standards + spec) review of a diff, run as parallel sub-agents. |
| [`codebase-design`](skills/codebase-design/) | Shared vocabulary for designing deep modules. |
| [`conventional-commits`](skills/conventional-commits/) | Write and evaluate commit messages against Conventional Commits 1.0.0. |
| [`deslop`](skills/deslop/) | Remove AI-generated code slop and clean up style. |
| [`dev-wiki`](skills/dev-wiki/) | Query your personal dev-wiki as a read-only knowledge source. |
| [`diagnosing-bugs`](skills/diagnosing-bugs/) | Diagnosis loop for hard bugs and performance regressions. |
| [`discovery`](skills/discovery/) | Build a visual, evidence-backed architecture discovery report. |
| [`domain-modeling`](skills/domain-modeling/) | Build and sharpen a project's domain model and decisions. |
| [`excalidraw-diagram`](skills/excalidraw-diagram/) | Create Excalidraw diagram JSON that argues visually. |
| [`gauntlet-workflow`](skills/gauntlet-workflow/) | Run a gauntlet loop as a deterministic Workflow script. |
| [`graph-spec`](skills/graph-spec/) | Turn a job into a paste-ready GRAPH SPEC prompt for a fleet. |
| [`grill-with-docs`](skills/grill-with-docs/) | Grilling session that also writes ADRs and a glossary. |
| [`grilling`](skills/grilling/) | Stress-test thinking, one round of unblocked questions at a time. |
| [`handoff`](skills/handoff/) | Compact a conversation into a handoff document for another agent. |
| [`html-artifact`](skills/html-artifact/) | Render a deliverable as one self-contained HTML file. |
| [`implement`](skills/implement/) | Implement work from a spec or set of tickets. |
| [`implementation-loop`](skills/implementation-loop/) | Implement a spec's tickets one at a time in dependency order. |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/) | Surface deepening opportunities as a visual report, then grill one. |
| [`improve-test-suite`](skills/improve-test-suite/) | Audit a test suite for seam quality and coverage gaps. |
| [`interrogate`](skills/interrogate/) | Interrogate a known design's edges and emit the answer key. |
| [`know-your-unknowns`](skills/know-your-unknowns/) | Buy the cheapest answer to what you don't know about a piece of work. |
| [`omarchy-extensions`](skills/omarchy-extensions/) | Add a feature to an Omarchy desktop on the cheapest surface that works. |
| [`orchestrator-loop`](skills/orchestrator-loop/) | Drive a batch of workitems to commits via fresh sub-agents. |
| [`prototype`](skills/prototype/) | Build throwaway code to answer a design question. |
| [`research`](skills/research/) | Investigate a question against primary sources, capture findings. |
| [`resolving-merge-conflicts`](skills/resolving-merge-conflicts/) | Resolve an in-progress merge/rebase conflict. |
| [`review-pr`](skills/review-pr/) | Review an Azure DevOps PR as a visual HTML page with CI results. |
| [`sdlc`](skills/sdlc/) | Router for the AI-native SDLC planning chain, and its shared HTML artifact rules. |
| [`setup-repo-skills`](skills/setup-repo-skills/) | Scaffold a repo's `AGENTS.md` routing, tracker, and docs layout. |
| [`survey`](skills/survey/) | Survey an idea whose route isn't visible, and emit the answer key. |
| [`tdd`](skills/tdd/) | Test-driven development reference and loop. |
| [`to-gauntlet`](skills/to-gauntlet/) | Turn an answer key into a paste-ready gauntlet prompt and driver. |
| [`to-design`](skills/to-design/) | Turn an accepted `intent.html` into `spec.html` under the policy skills. |
| [`to-intent`](skills/to-intent/) | Turn a conversation into `intent.html`, the proto-spec that starts a change. |
| [`to-plan`](skills/to-plan/) | Turn a plan approved in plan mode into `plan.html`. |
| [`to-spec`](skills/to-spec/) | Turn a conversation into a spec and publish to the tracker. |
| [`to-tickets`](skills/to-tickets/) | Break a plan into tracer-bullet tickets with blocking edges. |
| [`triage`](skills/triage/) | Move issues and external PRs through a triage state machine. |
| [`write-pull-requests`](skills/write-pull-requests/) | Draft and verify clear PR titles and descriptions. |
| [`writing-great-skills`](skills/writing-great-skills/) | Reference for writing predictable skills. |

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
