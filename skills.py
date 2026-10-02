#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Check and fix the skills in ./skills.

  ./skills.py check   Validate every skill. Exit 1 on an error.
  ./skills.py fix     Rewrite each agents/openai.yaml policy from SKILL.md.

SKILL.md frontmatter is the only source for manual-only invocation:
`disable-model-invocation: true` (Claude Code, Pi). Codex reads
`policy.allow_implicit_invocation` in agents/openai.yaml instead, so that value
is derived from the frontmatter and must not be edited by hand.

The agentskills.io validator (skills-ref) rejects every field outside the base
spec, including disable-model-invocation, so this script applies the spec's
name and description rules itself and allows the known harness fields.
"""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / "skills"

SPEC_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
HARNESS_FIELDS = {
    "disable-model-invocation", "user-invocable", "argument-hint", "arguments",
    "when_to_use", "model", "effort", "context", "agent", "hooks", "paths", "shell",
}
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Harness directories this repo does not link. A real skill directory here was
# written by an agent and never reached the repo.
STRAY_ROOTS = [
    Path.home() / ".codex/skills",
    Path.home() / ".pi/agent/skills",
    Path.home() / ".omp/agent/skills",
]


def skill_dirs():
    return sorted(d for d in SKILLS.iterdir() if (d / "SKILL.md").is_file())


def frontmatter(path):
    text = path.read_text()
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError("SKILL.md does not start with a --- frontmatter block")
    data = yaml.safe_load(match.group(1)) or {}
    if not isinstance(data, dict):
        raise ValueError("frontmatter is not a mapping")
    return data


def manual_only(fm):
    return fm.get("disable-model-invocation") is True


def check_skill(d):
    errors = []
    try:
        fm = frontmatter(d / "SKILL.md")
    except (ValueError, yaml.YAMLError) as e:
        return [str(e)]

    name, desc = fm.get("name"), fm.get("description")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(f"name {name!r} must be 1-64 lowercase letters, digits and single hyphens")
    elif name != d.name:
        errors.append(f"name {name!r} does not match the directory name")
    if not isinstance(desc, str) or not desc.strip():
        errors.append("description is missing")
    elif len(desc) > 1024:
        errors.append(f"description is {len(desc)} characters, the limit is 1024")
    unknown = set(fm) - SPEC_FIELDS - HARNESS_FIELDS
    if unknown:
        errors.append(f"unknown frontmatter fields: {', '.join(sorted(unknown))}")

    oy = d / "agents/openai.yaml"
    if not oy.is_file():
        errors.append("agents/openai.yaml is missing")
        return errors
    try:
        data = yaml.safe_load(oy.read_text()) or {}
    except yaml.YAMLError as e:
        return errors + [f"agents/openai.yaml: {e}"]
    iface = data.get("interface") or {}
    for key in ("display_name", "short_description"):
        if not iface.get(key):
            errors.append(f"agents/openai.yaml: interface.{key} is missing")
    implicit = (data.get("policy") or {}).get("allow_implicit_invocation", True)
    if implicit == manual_only(fm):
        errors.append("agents/openai.yaml: policy does not match disable-model-invocation (run ./skills.py fix)")
    return errors


def stray_skills():
    found = []
    for root in STRAY_ROOTS:
        if not root.is_dir() or root.is_symlink():
            continue
        for d in sorted(root.iterdir()):
            if d.name.startswith(".") or d.is_symlink():
                continue
            if (d / "SKILL.md").is_file():
                found.append(d)
    return found


def check():
    failed = 0
    for d in skill_dirs():
        for error in check_skill(d):
            print(f"{d.name}: {error}")
            failed += 1
    for d in stray_skills():
        print(f"warning: {d} is a skill outside this repo. Move it into skills/ if you want to keep it.")
    count = len(skill_dirs())
    print(f"{count} skills checked, {failed} errors" if failed else f"{count} skills ok")
    return 1 if failed else 0


def fix():
    for d in skill_dirs():
        oy = d / "agents/openai.yaml"
        if not oy.is_file():
            continue
        allow = "false" if manual_only(frontmatter(d / "SKILL.md")) else "true"
        lines, out, skipping = oy.read_text().splitlines(), [], False
        for line in lines:
            if line.startswith("policy:"):
                skipping = True
                continue
            if skipping and (line.startswith((" ", "\t")) or not line.strip()):
                continue
            skipping = False
            out.append(line)
        new = "\n".join(out).rstrip("\n") + f"\npolicy:\n  allow_implicit_invocation: {allow}\n"
        if new != oy.read_text():
            oy.write_text(new)
            print(f"{d.name}: policy set to allow_implicit_invocation: {allow}")
    return 0


if __name__ == "__main__":
    commands = {"check": check, "fix": fix}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    sys.exit(commands[sys.argv[1]]())
