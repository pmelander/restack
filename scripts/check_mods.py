#!/usr/bin/env python3
"""Hold every mod in mods/ to the contract ADR-029 sets: a view, never more.

A mod is read-only on the engagement. What it can do is what
`claude plugin validate` says its code calls and hooks, so that report is the
contract: a call outside ALLOWED_CALLS, a hook in FORBIDDEN_HOOKS, any
environment access, or a package to install fails the check.

Needs the Claude Code CLI on PATH (CI installs it). Standard library only.

    python scripts/check_mods.py
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODS = ROOT / "mods"
SKILLS = ROOT / "skills"

# ADR-029, decision point 2. `$.ui.*` is every drawing call; the rest by name.
ALLOWED_CALLS = {
    "$.fs.read", "$.fs.stat", "$.fs.exists", "$.fs.ancestors",
    "$.command.register", "$.prompt.read", "$.prompt.fill",
    "$.store.get", "$.store.set", "$.state.get", "$.state.set",
    "$.session.root", "$.session.cwd", "$.session.surfaces", "$.clock.after", "$.clock.now",
}
ALLOWED_PREFIXES = ("$.ui.",)

# Hooks that would let a view change what Claude does or reads.
FORBIDDEN_HOOKS = {
    "tool.call", "tool.check", "prompt.submit", "prompt.compose", "prompt.section",
    "prompt.context", "prompt.attachment", "skill.prompt", "session.append",
    "session.send", "session.receive", "plugin.register", "engine.create", "agent.spawn",
}


def notes(report: dict) -> list[str]:
    found = list(report.get("manifest", {}).get("notes", []))
    for part in report.get("contents", []):
        found += part.get("notes", [])
    return found


def listed(lines: list[str], label: str) -> list[str]:
    """The items of every `<module> <label>: a, b (via f), c` line."""
    items = []
    for line in lines:
        m = re.match(rf"^\S+ {label}: (.*)$", line)
        if m:
            items += [re.sub(r"\s*\(via [^)]*\)$", "", i.strip()) for i in m.group(1).split(", ")]
    return items


def check(mod: Path, claude: str) -> list[str]:
    problems = []
    for name in ("package.json", "node_modules", "package-lock.json", "bun.lock"):
        if (mod / name).exists():
            problems.append(f"{name}: a mod imports only its own files and `claude-code`, no packages")
    run = subprocess.run([claude, "plugin", "validate", "--strict", "--json", str(mod)],
                         capture_output=True, text=True, encoding="utf-8")
    try:
        report = json.loads(run.stdout)
    except json.JSONDecodeError:
        return problems + [f"`claude plugin validate` gave no report:\n{run.stdout}{run.stderr}"]
    if not report.get("success"):
        errors = report.get("manifest", {}).get("errors", []) + [
            e for part in report.get("contents", []) for e in part.get("errors", []) + part.get("warnings", [])]
        problems.append("`claude plugin validate --strict` failed: " + "; ".join(map(str, errors)))
    lines = notes(report)
    for call in listed(lines, "calls"):
        if call not in ALLOWED_CALLS and not call.startswith(ALLOWED_PREFIXES):
            problems.append(f"calls {call}, which is outside the view's allowlist (ADR-029)")
    for hook in listed(lines, "hooks"):
        event = hook.split("{", 1)[0]
        if event in FORBIDDEN_HOOKS:
            problems.append(f"hooks {event}, which would let a view change what Claude does (ADR-029)")
    for label in ("env reads", "env writes"):
        if listed(lines, label):
            problems.append(f"{label}: a view reads no environment variables (ADR-029)")
    return problems


def main() -> int:
    stray = [p.parent.relative_to(ROOT) for p in SKILLS.glob("*/.claude-plugin/plugin.json")]
    if stray:
        print("mods belong in mods/, not skills/: " + ", ".join(map(str, stray)), file=sys.stderr)
        return 1
    mods = sorted(p.parent.parent for p in MODS.glob("*/.claude-plugin/plugin.json"))
    if not mods:
        print("no mods under mods/")
        return 0
    claude = shutil.which("claude")
    if claude is None:
        print("the Claude Code CLI is not on PATH; install it to check mods", file=sys.stderr)
        return 1
    failed = False
    for mod in mods:
        problems = check(mod, claude)
        if problems:
            failed = True
            print(f"{mod.relative_to(ROOT)}:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
        else:
            print(f"{mod.relative_to(ROOT)}: within the view's contract")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
