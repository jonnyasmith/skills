#!/usr/bin/env bash
# Point each agent harness's skills directory at ./skills.
#
# One directory-level link per harness, not one link per skill: a skill that an
# agent creates in its own skills directory then lands in this repo, where git
# sees it, instead of being stranded in that harness's home directory.
#
# Harness skills directories:
#   ~/.claude/skills      Claude Code
#   ~/.agents/skills      Codex, Pi, omp, and other tools that read the shared path
#
# Older links in ~/.codex/skills, ~/.pi/agent/skills and ~/.omp/skills are
# removed: those tools already read ~/.agents/skills, so the copies would load
# every skill twice.
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

# Remove this repo's links from directories the harnesses no longer need. A
# real directory keeps any other entries, such as Codex's own .system skills.
for legacy in "$HOME/.codex/skills" "$HOME/.pi/agent/skills" "$HOME/.omp/skills"; do
  if [[ -L "$legacy" ]]; then
    if [[ "$(readlink "$legacy")" == "$src" ]]; then
      rm "$legacy"
      echo "$legacy: removed legacy link"
    fi
  elif [[ -d "$legacy" ]]; then
    prune_own_links "$legacy" || true
    if [[ $pruned -gt 0 ]]; then
      echo "$legacy: removed $pruned legacy links"
    fi
  fi
done
