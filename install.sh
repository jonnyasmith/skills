#!/usr/bin/env bash
# Point each agent harness's skills directory at ./skills.
#
# One directory-level link per harness, not one link per skill: a skill that an
# agent creates in its own skills directory then lands in this repo, where git
# sees it, instead of being stranded in that harness's home directory.
#
# Harness skills directories:
#   ~/.claude/skills      Claude Code
#   ~/.agents/skills      Codex, omp, and other tools that read the shared path
#   ~/.pi/agent/skills    Pi (only when ~/.pi exists)
#
# Legacy per-skill links in ~/.codex/skills and the unused ~/.omp/skills link
# are removed: Codex and omp already read ~/.agents/skills, so those copies
# would load every skill twice.
#
# Safe to re-run. A directory that holds anything other than links into this
# repo is reported and left alone.

set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")/skills" && pwd)"

# "<harness home>:<skills directory>". The link is made only when the harness
# home exists, so an uninstalled harness gets nothing.
targets=(
  "$HOME/.claude:$HOME/.claude/skills"
  "$HOME/.agents:$HOME/.agents/skills"
  "$HOME/.pi:$HOME/.pi/agent/skills"
)

# Remove links in $1 that point into this repo, counting them in $pruned.
# Report whether $1 is now empty.
pruned=0
prune_own_links() {
  local dir="$1" entry
  pruned=0
  for entry in "$dir"/* "$dir"/.[!.]*; do
    [[ -L "$entry" ]] || continue
    if [[ "$(readlink "$entry")" == "$src"/* ]]; then
      rm "$entry"
      pruned=$((pruned + 1))
    fi
  done
  [[ -z "$(ls -A "$dir")" ]]
}

for pair in "${targets[@]}"; do
  home="${pair%%:*}" root="${pair#*:}"

  if [[ ! -d "$home" ]]; then
    echo "$root: skipped, $home does not exist"
    continue
  fi

  if [[ -L "$root" ]]; then
    if [[ "$(readlink "$root")" == "$src" ]]; then
      echo "$root: ok"
    else
      echo "$root: skipped, links to $(readlink "$root")" >&2
    fi
    continue
  fi

  if [[ -d "$root" ]]; then
    if ! prune_own_links "$root"; then
      echo "$root: skipped, holds entries that are not links into this repo:" >&2
      ls -A "$root" | sed 's/^/  /' >&2
      continue
    fi
    rmdir "$root"
  fi

  mkdir -p "$(dirname "$root")"
  ln -s "$src" "$root"
  echo "$root: linked"
done

if [[ -d "$HOME/.codex/skills" && ! -L "$HOME/.codex/skills" ]]; then
  prune_own_links "$HOME/.codex/skills" || true
  if [[ $pruned -gt 0 ]]; then
    echo "$HOME/.codex/skills: removed $pruned legacy links"
  fi
fi

if [[ -L "$HOME/.omp/skills" && "$(readlink "$HOME/.omp/skills")" == "$src" ]]; then
  rm "$HOME/.omp/skills"
  echo "$HOME/.omp/skills: removed unused link"
fi
