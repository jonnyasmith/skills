# AI Skills

A personal library of reusable AI agent **skills** — each a self-contained directory under [`skills/`](skills/) with a `SKILL.md` that tells an agent when and how to apply it.

## What's a skill?

A skill is a directory containing a `SKILL.md` with YAML frontmatter (`name`, `description`, optional invocation hints) followed by the instructions themselves. Supporting files — references, templates, scripts, and per-provider `agents/` configs — live alongside it. Agents load a skill when its `description` matches the task at hand.

## Skills

| Skill | What it does |
| --- | --- |
| [`code-review`](skills/code-review/) | Two-axis (standards + spec) review of a diff, run as parallel sub-agents. |
| [`codebase-design`](skills/codebase-design/) | Shared vocabulary for designing deep modules. |
| [`conventional-commits`](skills/conventional-commits/) | Write and evaluate commit messages against Conventional Commits 1.0.0. |
| [`deslop`](skills/deslop/) | Remove AI-generated code slop and clean up style. |
| [`dev-wiki`](skills/dev-wiki/) | Query your personal dev-wiki as a read-only knowledge source. |
| [`diagnosing-bugs`](skills/diagnosing-bugs/) | Diagnosis loop for hard bugs and performance regressions. |
| [`discovery`](skills/discovery/) | Build a visual, evidence-backed architecture discovery report. |
| [`domain-modeling`](skills/domain-modeling/) | Build and sharpen a project's domain model and decisions. |
| [`excalidraw-diagram`](skills/excalidraw-diagram/) | Create Excalidraw diagram JSON that argues visually. |
| [`grill-me`](skills/grill-me/) | Relentless interview to sharpen a plan or design. |
| [`grill-with-docs`](skills/grill-with-docs/) | Grilling session that also writes ADRs and a glossary. |
| [`grilling`](skills/grilling/) | Stress-test thinking, one round of unblocked questions at a time. |
| [`handoff`](skills/handoff/) | Compact a conversation into a handoff document for another agent. |
| [`implement`](skills/implement/) | Implement work from a spec or set of tickets. |
| [`implementation-loop`](skills/implementation-loop/) | Implement a spec's tickets one at a time in dependency order. |
| [`improve-codebase-architecture`](skills/improve-codebase-architecture/) | Surface deepening opportunities as a visual report, then grill one. |
| [`improve-test-suite`](skills/improve-test-suite/) | Audit a test suite for seam quality and coverage gaps. |
| [`orchestrator-loop`](skills/orchestrator-loop/) | Drive a batch of workitems to commits via fresh sub-agents. |
| [`prototype`](skills/prototype/) | Build throwaway code to answer a design question. |
| [`research`](skills/research/) | Investigate a question against primary sources, capture findings. |
| [`resolving-merge-conflicts`](skills/resolving-merge-conflicts/) | Resolve an in-progress merge/rebase conflict. |
| [`setup-repo-skills`](skills/setup-repo-skills/) | Scaffold a repo's `AGENTS.md` routing, tracker, and docs layout. |
| [`tdd`](skills/tdd/) | Test-driven development reference and loop. |
| [`to-spec`](skills/to-spec/) | Turn a conversation into a spec and publish to the tracker. |
| [`to-tickets`](skills/to-tickets/) | Break a plan into tracer-bullet tickets with blocking edges. |
| [`triage`](skills/triage/) | Move issues and external PRs through a triage state machine. |
| [`wayfinder`](skills/wayfinder/) | Plan huge work as decision tickets, resolve one at a time. |
| [`write-pull-requests`](skills/write-pull-requests/) | Draft and verify clear PR titles and descriptions. |
| [`writing-great-skills`](skills/writing-great-skills/) | Reference for writing predictable skills. |

## Install

Clone the repo, then run `install.sh`. It links each skill individually into every agent's skills directory.

```sh
git clone git@github.com:jonnyasmith/skills.git ~/dev/skills
cd ~/dev/skills
./install.sh
```

Default targets: `~/.agents/skills`, `~/.claude/skills`, `~/.codex/skills`, and `~/.pi/agent/skills`. Pass paths to override them:

```sh
./install.sh ~/.claude/skills
```

Re-run the script after `git pull` adds, renames, or removes a skill. Edits to an existing skill need no re-run, because each link points at the live directory.

### Notes

- The script links per skill instead of pointing one link at the whole `skills/` directory. Those directories are real directories that other tools also provision — Omarchy, for example, writes its own `omarchy` and `diagnose-crash` links into all four. A directory-level link would make those tools write into this working tree.
- Re-running is safe. The script rewrites the links it owns, removes its own links whose skill no longer exists, and never touches an entry that points elsewhere.
- An entry that exists but is not a symlink is reported and skipped, so a real directory of your own is never deleted.
- Verify the links resolve:

  ```sh
  ls -l ~/.agents/skills
  find ~/.agents/skills -maxdepth 1 -xtype l   # dangling links, expect none
  ```
