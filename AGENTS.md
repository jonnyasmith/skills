# Skills Repository

This repository holds personal agent skills and nothing else. Global agent instructions and harness config files live in the dotfiles repository, which chezmoi manages (`~/.local/share/chezmoi`). Do not add them here.

## Layout

- `skills/<name>/` — one installed skill: `SKILL.md`, `agents/openai.yaml`, and any supporting files.
- `archive/<name>/` — retired and parked skills, including most manual-only ones. No harness loads them.
- `skills.py` — checks and fixes skills. Needs `uv`.
- `install.sh` — links the harnesses to `skills/` and enables the pre-commit hook.
- `.githooks/pre-commit` — runs `./skills.py check`.
- `research/` — research notes about skills. These are not skills.

## How skills reach the harnesses

`install.sh` makes two directory-level links:

| Link | Read by |
| --- | --- |
| `~/.claude/skills` → `skills/` | Claude Code |
| `~/.agents/skills` → `skills/` | Codex, Pi, omp |

Because the links point at the whole directory:

- An edit to a skill is live at once. No sync step is needed.
- A skill that an agent creates in `~/.claude/skills` or `~/.agents/skills` lands in `skills/`. Commit it like any other change.
- Other tools also write into `skills/`, such as Claude's account-synced `synced/` directory and Omarchy's links. `.gitignore` excludes them. Do not commit, move, or delete them.

Do not create skills in `~/.codex/skills`, `~/.pi/agent/skills`, or `~/.omp/agent/skills`. The harnesses do not need these locations, and `./skills.py check` warns about any skill it finds there.

## Rules for changing skills

- **Frontmatter.** Use `name` and `description`, plus only known harness fields such as `disable-model-invocation` and `argument-hint`. `name` must match the directory name. `description` must be 1,024 characters or fewer, and must say what the skill does and when to use it.
- **Manual-only invocation.** Most skills are manual-only. Set `disable-model-invocation: true` in the frontmatter, then run `./skills.py fix`. The frontmatter is the only source. `fix` writes the Codex equivalent (`policy.allow_implicit_invocation`) into `agents/openai.yaml`. Do not edit that value by hand. Only `conventional-commits`, `write-pull-requests` and `subagent-orchestration` run automatically.
- **New skill.** Create `skills/<name>/SKILL.md` and `agents/openai.yaml` with `interface.display_name` and `interface.short_description`. Make it manual-only unless an agent must find it without being asked. Then run `./skills.py fix`.
- **Per-harness differences.** Keep one `SKILL.md` for all harnesses. Put harness settings in the frontmatter or in `agents/openai.yaml`. Put short behaviour notes in the body, for example "In Codex, …". Make a separate skill with a different name only when the procedure itself is different.
- **Retiring a skill.** Run `git mv skills/<name> archive/<name>`. Do not delete it.
- **README.** When you add, rename, or retire a skill, update the table in `README.md`.

## Verification

Run `./skills.py check` before you commit. The pre-commit hook also runs it. It checks the frontmatter rules, unknown fields, and `agents/openai.yaml` against the frontmatter.

Do not use the official `skills-ref` validator. It rejects harness fields such as `disable-model-invocation`.

## Harness facts

- omp does not enforce `disable-model-invocation`, so manual-only skills can still trigger there. Claude Code, Pi, and Codex enforce it.
- omp is set (in chezmoi) not to read `~/.claude/skills`, so it loads each skill only once.
- Claude Code has no setting for extra skill directories. Codex reads only `~/.agents/skills` and its own built-in locations. This is why the links exist.
