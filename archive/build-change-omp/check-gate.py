#!/usr/bin/env python3
"""PreToolUse hook: no commit lands unless the repository's checks pass.

Registered in a repository's .claude/settings.json by the build-change skill:

    python3 "$CLAUDE_PROJECT_DIR/.claude/hooks/check-gate.py" "<check command>"

The check command is one shell command that exits non-zero on failure.

- Bash `git commit` runs the check command from the repository root first,
  and is blocked (exit 2, output shown to Claude) when it fails.
- Bash `git commit --no-verify` / `-n` is always blocked.
- Edit/Write to this hook or to .claude/settings*.json is blocked, so the
  gate cannot be switched off from inside a session.
"""
import json
import os
import re
import shlex
import subprocess
import sys

GUARDED = re.compile(r"(^|/)\.claude/(settings(\.local)?\.json|hooks/check-gate\.py)$")


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def commit_repo(command, cwd):
    """The repository a `git commit` in this command runs in, or None if it doesn't commit."""
    for segment in re.split(r"&&|\|\||;|\|", command):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        # `cd <dir> && git commit` commits in <dir>, not in the session's directory.
        if len(words) >= 2 and words[0] in ("cd", "pushd"):
            cwd = os.path.join(cwd, os.path.expanduser(words[1]))
            continue
        if "git" not in words:
            continue
        i = words.index("git") + 1
        repo = cwd
        while i < len(words) and words[i].startswith("-"):
            if words[i] == "-C" and i + 1 < len(words):
                repo = os.path.join(repo, words[i + 1])
                i += 2
            else:
                i += 1
        if i < len(words) and words[i] == "commit":
            args = words[i + 1:]
            if "--no-verify" in args or any(re.fullmatch(r"-[a-zA-Z]*n[a-zA-Z]*", a) for a in args):
                block("check-gate: commits may not skip verification (--no-verify / -n).")
            return repo
    return None


def main():
    event = json.load(sys.stdin)
    tool = event.get("tool_name")
    tool_input = event.get("tool_input", {})

    if tool in ("Edit", "Write", "MultiEdit"):
        if GUARDED.search(tool_input.get("file_path", "")):
            block("check-gate: the check gate and Claude settings cannot be changed from inside a session. Ask the user.")
        return

    if tool != "Bash" or len(sys.argv) < 2:
        return

    repo = commit_repo(tool_input.get("command", ""), event.get("cwd") or os.getcwd())
    if repo is None:
        return

    top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    root = top.stdout.strip() if top.returncode == 0 else repo
    check = sys.argv[1]
    result = subprocess.run(check, shell=True, cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        tail = "\n".join((result.stdout + result.stderr).splitlines()[-40:])
        block(f"check-gate: `{check}` failed (exit {result.returncode}) in {root}, so the commit is blocked. Fix the failure, then commit.\n\n{tail}")


if __name__ == "__main__":
    main()
