#!/usr/bin/env bash
# Link every skill in ./skills into each agent's skills directory.
#
# Per-skill links, not one directory-level link: the agent skill directories are
# real directories that Omarchy provisions with its own links (omarchy,
# diagnose-crash). Replacing a directory with a link to this repo would make
# Omarchy write its links into the working tree.
#
# Safe to re-run. Links this repo owns are refreshed, links to skills that no
# longer exist are removed, and anything else in the directory is left alone.
#
# Usage: ./install.sh [ROOT ...]   (default: the four roots below)

set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")/skills" && pwd)"

roots=("$@")
if [[ ${#roots[@]} -eq 0 ]]; then
  roots=(
    "$HOME/.agents/skills"
    "$HOME/.claude/skills"
    "$HOME/.codex/skills"
    "$HOME/.pi/agent/skills"
  )
fi

skills=()
for dir in "$src"/*/; do
  [[ -f "$dir/SKILL.md" ]] || continue
  skills+=("${dir%/}")
done

if [[ ${#skills[@]} -eq 0 ]]; then
  echo "no skills with a SKILL.md found in $src" >&2
  exit 1
fi

for root in "${roots[@]}"; do
  mkdir -p "$root"
  linked=0 pruned=0 skipped=0

  # Drop links this repo owns up front, so renamed and deleted skills do not
  # leave danglers behind. Links to anywhere else are not ours to touch.
  for entry in "$root"/*; do
    [[ -L "$entry" ]] || continue
    target="$(readlink "$entry")"
    [[ "$target" == "$src/"* ]] || continue
    # An existing target is a link we are about to rewrite anyway; a missing one
    # is a skill that was renamed or deleted, and worth reporting.
    [[ -e "$target" ]] || pruned=$((pruned + 1))
    rm "$entry"
  done

  for skill in "${skills[@]}"; do
    link="$root/$(basename "$skill")"
    if [[ -e "$link" && ! -L "$link" ]]; then
      echo "  skip $(basename "$skill"): $link exists and is not a symlink" >&2
      skipped=$((skipped + 1))
      continue
    fi
    ln -sfn "$skill" "$link"
    linked=$((linked + 1))
  done

  printf '%s: %d linked' "$root" "$linked"
  [[ $pruned -gt 0 ]] && printf ', %d stale removed' "$pruned"
  [[ $skipped -gt 0 ]] && printf ', %d skipped' "$skipped"
  printf '\n'
done
