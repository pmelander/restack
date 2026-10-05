#!/usr/bin/env python3
"""Find, and retire, old copies of ReStack skills inside a project.

Before ReStack installed into the user profile, projects carried their own
copies in `<project>/.claude/skills/<name>/` (`journey`, `adr`, ...), and
some still do. Claude Code loads them beside the installed `restack-*`
skills, so an old `journey` can answer a request meant for
`/restack-journey`, with method two releases out of date. Nothing tells the
architect: both load without error.

    python local_copies.py list [--project P]            what is there, and why it counts
    python local_copies.py retire [--project P] [--yes]  move them aside (dry run without --yes)

A copy counts when its folder (or command file) has a ReStack skill's name,
with or without the `restack-` prefix, and its content is ReStack's: the same
title as the installed skill, or the residuality vocabulary. A project's own
skill that happens to share a name is left alone. Only `.claude/skills/` and
`.claude/commands/` are looked at, the places Claude Code loads from; other
tools' folders are not ReStack's business.

Retiring moves each copy to `<project>/.claude/skills-retired-<date>/`, which
Claude Code does not load, with a README saying how to move it back. Nothing
is deleted. `update_check.py` prints one line at session open when the current
project has copies (ADR-024). Standard library only (ADR-010).
"""

from __future__ import annotations

import datetime as dt
import os
import re
import shutil
import sys
from pathlib import Path

# The skill set, used when the installed skills cannot be listed (for example
# when this file runs from somewhere unusual). The installed set wins.
KNOWN = ["journey", "discover", "stressor", "events", "adr", "solution-doc", "tech-stack",
         "design-review", "cloud", "capacity", "arch-learning", "capability-assessor",
         "patterns", "evolve", "excel", "trace", "upgrade"]
VOCABULARY = re.compile(r"residualit|\bresiduals?\b|\bstressors?\b|antifragil", re.IGNORECASE)


def installed_skills() -> dict[str, str]:
    """Short name -> title (the first `# ` heading) of each installed restack-* skill."""
    root = Path(__file__).resolve().parent.parent.parent      # .../skills
    found = {}
    for skill in sorted(root.glob("restack-*")):
        # A mod installs beside the skills (ADR-029) and has no SKILL.md. It is
        # not a skill, so nothing can be an old copy of it.
        if not (skill / "SKILL.md").is_file():
            continue
        title = ""
        try:
            for line in (skill / "SKILL.md").read_text(encoding="utf-8").splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
        except OSError:
            pass
        found[skill.name[len("restack-"):]] = title
    return found or {name: "" for name in KNOWN}


def title_of(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def version_of(text: str) -> str | None:
    m = re.search(r"^version:\s*(\S+)", text[:2000], re.MULTILINE)
    return m.group(1) if m else None


def find(project: Path, profile: bool = False) -> list[dict]:
    """Every ReStack copy under `project/.claude`, with what identifies it.

    With `profile`, `project` is the user's home: the unprefixed copies an
    install from before ADR-009 left in ~/.claude/skills. The real restack-*
    install lives there too, so restack-* folders are never counted.
    """
    skills = installed_skills()
    root = project / ".claude"
    candidates = []
    for d in sorted((root / "skills").glob("*")):
        if d.is_dir() and (d / "SKILL.md").is_file():
            candidates.append((d, d / "SKILL.md", d.name))
    for f in sorted((root / "commands").glob("*.md")):
        candidates.append((f, f, f.stem))
    copies = []
    for path, text_file, name in candidates:
        if profile and name.startswith("restack-"):
            continue                        # the install itself
        short = name[len("restack-"):] if name.startswith("restack-") else name
        if short not in skills:
            continue
        try:
            text = text_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if name.startswith("restack-"):
            why = "a restack-* copy inside the project"
        elif skills[short] and title_of(text).lower() == skills[short].lower():
            why = f"same title as /restack-{short} (\"{skills[short]}\")"
        elif VOCABULARY.search(text):
            why = "a ReStack skill's name and residuality vocabulary"
        else:
            continue                        # the project's own skill with a shared name
        copies.append({"path": path, "rel": path.relative_to(project).as_posix(), "name": name,
                       "replaced_by": f"/restack-{short}", "why": why,
                       "version": version_of(text)})
    return copies


def session_line(project: Path, profile: bool = False) -> str | None:
    """The one line the session-open check prints, or None."""
    if not (project / ".claude").is_dir():
        return None
    copies = find(project, profile)
    if not copies:
        return None
    names = ", ".join(c["name"] for c in copies[:6]) + (" ..." if len(copies) > 6 else "")
    if profile:
        owner, folder, fix = "your profile has", "~/.claude", "/restack-upgrade retire-local --profile"
    else:
        owner, folder, fix = "this project has", ".claude", "/restack-upgrade retire-local"
    noun = "copy" if len(copies) == 1 else "copies"
    return (f"ReStack: {owner} {len(copies)} old ReStack skill {noun} in {folder} ({names}) "
            f"that load beside the installed restack-* skills: {fix}")


def retire(project: Path, today: str, do_move: bool, profile: bool = False) -> tuple[list[str], Path]:
    """Move every copy aside. Returns (report lines, the folder they went to)."""
    copies = find(project, profile)
    target = project / ".claude" / f"skills-retired-{today}"
    report = []
    for c in copies:
        sub = "commands" if c["rel"].startswith(".claude/commands/") else "skills"
        dest = target / sub / c["path"].name
        n = 2
        while dest.exists():
            dest = target / sub / f"{c['path'].name}-{n}"
            n += 1
        report.append(f"{c['rel']} -> {dest.relative_to(project).as_posix()}  "
                      f"({c['why']}; replaced by {c['replaced_by']})")
        if do_move:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(c["path"]), str(dest))
    if do_move and copies:
        readme = target / "README.md"
        lines = [] if not readme.exists() else readme.read_text(encoding="utf-8").splitlines()
        if not lines:
            lines = [f"# Retired ReStack skill copies ({today})", "",
                     "Moved here by `/restack-upgrade retire-local` because they loaded beside",
                     "the installed `restack-*` skills with older method. Claude Code does not load",
                     "this folder. To restore one, move it back to `.claude/skills/` (or",
                     "`.claude/commands/`). Delete this folder when you no longer need it.", ""]
        lines += [f"- {r}" for r in report]
        readme.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return report, target


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass
    import argparse
    parser = argparse.ArgumentParser(prog="local_copies.py", description=__doc__.split("\n\n")[0])
    parser.add_argument("command", choices=["list", "retire"])
    where = parser.add_mutually_exclusive_group()
    where.add_argument("--project", default=".")
    where.add_argument("--profile", action="store_true",
                       help="the unprefixed copies an old install left in ~/.claude/skills")
    parser.add_argument("--yes", action="store_true", help="retire: actually move them")
    parser.add_argument("--date", default=dt.date.today().isoformat())
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    project = (Path.home() if args.profile else Path(args.project)).resolve()
    if not project.is_dir():
        print(f"local_copies: {project} is not a directory", file=sys.stderr)
        return 2
    fix = "`/restack-upgrade retire-local" + (" --profile`" if args.profile else "`")

    if args.command == "list":
        copies = find(project, args.profile)
        if not copies:
            print(f"No ReStack skill copies in {project / '.claude'}.")
            return 0
        print(f"{len(copies)} ReStack skill cop{'y' if len(copies) == 1 else 'ies'} in {project}:")
        for c in copies:
            version = f", v{c['version']}" if c["version"] else ""
            print(f"  {c['rel']}  ({c['why']}{version}; replaced by {c['replaced_by']})")
        print(f"They load beside the installed restack-* skills. {fix} moves them aside.")
        return 1

    report, target = retire(project, args.date, args.yes, args.profile)
    if not report:
        print(f"No ReStack skill copies in {project / '.claude'}; nothing to retire.")
        return 0
    print(("Moved" if args.yes else "Would move") + f" {len(report)} cop"
          f"{'y' if len(report) == 1 else 'ies'}:")
    for line in report:
        print(f"  {line}")
    if args.yes:
        print(f"Claude Code no longer loads them. {target.relative_to(project).as_posix()}/README.md "
              f"says how to move one back. New sessions pick up the change.")
    else:
        print("Dry run: nothing moved. Add --yes to move them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
