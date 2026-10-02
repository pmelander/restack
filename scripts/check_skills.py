#!/usr/bin/env python3
"""Validate the skills tree.

Complements gen_skills.py --check, which only proves that a generated SKILL.md
matches its template. This checks the things a template cannot: that every
skill is loadable by Claude Code at all, that generated files still declare
themselves generated, and that no section file has been orphaned or
double-registered.

Runs over converted and legacy skills alike, so the mixed state during the
conversion is visible rather than silent.

Usage:
    python scripts/check_skills.py          # report and exit 1 on any error
    python scripts/check_skills.py --quiet  # errors only
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
BANNER = "AUTO-GENERATED"

errors: list[str] = []
warnings: list[str] = []


def frontmatter(text: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 3)
    return None if end == -1 else text[4:end]


# Tokens that look like a file path: something ending in a known extension.
PATH_TOKEN = re.compile(r"[A-Za-z0-9_.$~<>*/-]*\.(?:md|py|json|sh|yml|tmpl)\b")

# Paths a skill writes into the USER's project, not paths inside the install.
# These will not exist in this repository and must never be flagged.
USER_OUTPUT_PREFIXES = ("docs/",)

# Runtime state created at install time, not shipped.
RUNTIME_STATE_PREFIXES = (".restack/", "~/.restack/", "$HOME/.restack/")

# The installed location of the skills tree maps back onto skills/ here.
INSTALLED_PREFIXES = ("~/.claude/skills/", "$HOME/.claude/skills/")

# The skill's own directory, as Claude Code prints it at load.
BASE_PREFIX = "<base>/"

# Section paths that resolve in this checkout and nowhere else. They passed the
# existence check for months because the check ran from the repository root -
# the one place they work. From an install, a Glob for them returns nothing.
REPO_ONLY_SECTION = re.compile(r"^(?:skills/[^/]+/sections/|scripts/shared/|sections/|templates/)")

HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

# Method used by several skills lives here, registered with "shared": true.
SHARED_SECTIONS = ROOT / "scripts" / "shared"


def scan_paths(f: Path, label: str, skill_dir: Path | None) -> int:
    """Check every path-looking token in one file. Returns how many were checked.

    `skill_dir` owns the file, or is None for a shared section's source. A shared
    section is read by several skills, so a `<base>/...` token there has no single
    owner; it is checked in each skill's vendored copy instead.
    """
    checked = 0

    # Generated banners are notes to maintainers, not paths Claude is told to use.
    text = HTML_COMMENT.sub("", f.read_text(encoding="utf-8"))
    for raw in PATH_TOKEN.findall(text):
        token = raw.strip("`\"'()[],")

        if "/" not in token:
            continue                                    # bare filename, not a path
        if token.startswith(BASE_PREFIX):
            rest = token[len(BASE_PREFIX):]
            if skill_dir is None or any(c in rest for c in "<>*"):
                continue                                # per consuming skill / placeholder
            checked += 1
            target = skill_dir / rest
            if not target.exists():
                errors.append(
                    f"{label}: references '{token}' but "
                    f"{target.relative_to(ROOT)} does not exist"
                )
            continue
        if REPO_ONLY_SECTION.match(token):
            checked += 1
            errors.append(
                f"{label}: references '{token}', which resolves only from a "
                f"ReStack checkout - vendor it via sections/manifest.json and "
                f"write it as <base>/sections/<file>"
            )
            continue
        if any(c in token for c in "<>*") or "NNN" in token:
            continue                                    # placeholder
        if token.startswith("$") and not token.startswith("$HOME/"):
            continue                                    # shell variable in a snippet
        if token.startswith(USER_OUTPUT_PREFIXES):
            continue                                    # written into the user's project
        if token.startswith(RUNTIME_STATE_PREFIXES):
            continue                                    # created at install time

        if token.startswith(".."):
            target = (f.parent / token).resolve()       # relative to the file
        else:
            mapped = token
            for prefix in INSTALLED_PREFIXES:
                if mapped.startswith(prefix):
                    mapped = "skills/" + mapped[len(prefix):]
                    break
            target = ROOT / mapped                      # repo-relative

        checked += 1
        if not target.exists():
            errors.append(
                f"{label}: references '{token}' which does not exist "
                f"(looked for {target.relative_to(ROOT) if ROOT in target.parents else target}) "
                f"- it would tell Claude to use a path that is not installed"
            )
    return checked


def check_referenced_paths(skill_dir: Path) -> int:
    """Verify every install path a skill tells Claude to use actually resolves.

    This is the check neither gen_skills.py nor the frontmatter rules can make.
    /restack-excel shipped for months invoking `python helpers/read_spreadsheet.py`
    — a path that was never installed — and it survived three refactors because
    nothing verified that a command a skill instructs Claude to run would work.

    Deliberately conservative: anything ambiguous is skipped. A validator that
    cries wolf gets muted, and a muted check is a failed control.
    """
    name = skill_dir.name
    files = [skill_dir / "SKILL.md"] + sorted((skill_dir / "sections").glob("*.md"))
    checked = 0

    for f in files:
        if not f.exists():
            continue
        checked += scan_paths(f, f"skills/{name}/{f.name}", skill_dir)
    return checked


def check_shared_paths() -> int:
    """Same check for shared sections, which no skill owns.

    `scripts/shared/*.md` is read on demand by every skill whose manifest registers
    it ([ADR-013](docs/adr/ADR-013-outside-opinion.md)), so its paths reach Claude
    exactly as a skill's own do. The manifest check only proves a shared file
    exists; nothing verified the paths inside it. Scanned once here rather than per
    consuming skill, so a broken reference is reported once instead of N times.
    """
    if not SHARED_SECTIONS.is_dir():
        return 0

    checked = 0
    for f in sorted(SHARED_SECTIONS.glob("*.md")):
        checked += scan_paths(f, f"scripts/shared/{f.name}", None)
    return checked


def check_skill(skill_dir: Path) -> dict:
    name = skill_dir.name
    rel = f"skills/{name}"
    skill_md = skill_dir / "SKILL.md"
    template = skill_dir / "SKILL.md.tmpl"
    generated = template.exists()

    if not skill_md.exists():
        errors.append(f"{rel}: no SKILL.md - Claude Code cannot load this skill")
        return {"name": name, "generated": generated, "sections": 0}

    text = skill_md.read_text(encoding="utf-8")
    fm = frontmatter(text)

    if fm is None:
        errors.append(f"{rel}/SKILL.md: missing or unterminated YAML frontmatter")
    elif not re.search(r"^description:", fm, re.MULTILINE):
        errors.append(f"{rel}/SKILL.md: frontmatter has no 'description' - the skill will not be discoverable")

    # A generated file must still say so; the banner is what stops hand edits.
    if generated and BANNER not in text[:1200]:
        errors.append(
            f"{rel}/SKILL.md: has a template but no {BANNER} banner - "
            f"it was probably hand-edited. Run: python scripts/gen_skills.py {name}"
        )
    if not generated and BANNER in text[:1200]:
        errors.append(f"{rel}/SKILL.md: claims to be generated but has no SKILL.md.tmpl")

    # Sections: manifest and directory must agree in both directions.
    sections_dir = skill_dir / "sections"
    registered: set[str] = set()
    if sections_dir.is_dir():
        manifest_path = sections_dir / "manifest.json"
        if not manifest_path.exists():
            errors.append(f"{rel}/sections/: no manifest.json")
        else:
            try:
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}/sections/manifest.json: invalid JSON - {exc}")
                manifest = {"sections": []}
            seen_ids: set[str] = set()
            for entry in manifest.get("sections", []):
                for field in ("id", "file", "title", "trigger"):
                    if not entry.get(field):
                        errors.append(f"{rel}/sections/manifest.json: entry missing '{field}': {entry!r}")
                sid, sfile = entry.get("id"), entry.get("file")
                if sid in seen_ids:
                    errors.append(f"{rel}/sections/manifest.json: duplicate id '{sid}'")
                seen_ids.add(sid)
                source = entry.get("source") or (f"scripts/shared/{sfile}" if entry.get("shared") else None)
                if sfile:
                    if source:
                        if not (ROOT / source).exists():
                            errors.append(
                                f"{rel}/sections/manifest.json: '{sfile}' is vendored from "
                                f"{source}, which does not exist"
                            )
                        # setup installs skills/restack-*/ only, so the skill
                        # needs its own copy. gen_skills.py writes it.
                        vendored = sections_dir / sfile
                        if not vendored.exists():
                            errors.append(
                                f"{rel}/sections/{sfile}: vendored from {source} but has no copy here - "
                                f"it would not be installed. Run: python scripts/gen_skills.py {name}"
                            )
                        elif BANNER not in vendored.read_text(encoding="utf-8")[:400]:
                            errors.append(
                                f"{rel}/sections/{sfile}: vendored copy has no {BANNER} banner - "
                                f"it was probably hand-edited. Edit {source}"
                            )
                        registered.add(sfile)
                    else:
                        registered.add(sfile)
                        if not (sections_dir / sfile).exists():
                            errors.append(f"{rel}/sections/manifest.json: '{sfile}' is registered but missing on disk")

        on_disk = {p.name for p in sections_dir.glob("*.md")}
        for orphan in sorted(on_disk - registered):
            errors.append(
                f"{rel}/sections/{orphan}: on disk but not in manifest.json - "
                f"it will never be read"
            )

    paths = check_referenced_paths(skill_dir)

    return {
        "name": name,
        "generated": generated,
        # Owned sections plus vendored shared ones: what the skill actually reads.
        "sections": len(registered),
        "paths": paths,
    }


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv

    if not SKILLS.is_dir():
        print("no skills/ directory", file=sys.stderr)
        return 1

    results = [check_skill(d) for d in sorted(SKILLS.iterdir()) if d.is_dir()]
    shared_paths = check_shared_paths()

    if not quiet:
        converted = [r for r in results if r["generated"]]
        legacy = [r for r in results if not r["generated"]]
        print(f"{len(results)} skills: {len(converted)} generated, {len(legacy)} legacy\n")
        for r in converted:
            print(f"  generated  /{r['name']:<28} {r['sections']} section(s), {r['paths']} path(s)")
        for r in legacy:
            print(f"  legacy     /{r['name']}")
        shared_count = len(list(SHARED_SECTIONS.glob("*.md"))) if SHARED_SECTIONS.is_dir() else 0
        print(f"\n  shared     scripts/shared/            {shared_count} section(s), {shared_paths} path(s)")
        print(f"\n{sum(r['paths'] for r in results) + shared_paths} install paths verified")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}", file=sys.stderr)

    if errors:
        print(f"\n{len(errors)} error(s)", file=sys.stderr)
        return 1
    print("skills tree OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
