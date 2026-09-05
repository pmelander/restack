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
        for raw in PATH_TOKEN.findall(f.read_text(encoding="utf-8")):
            token = raw.strip("`\"'()[],")

            if "/" not in token:
                continue                                    # bare filename, not a path
            if any(c in token for c in "<>*") or "NNN" in token:
                continue                                    # placeholder
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
                if mapped.startswith("sections/"):
                    target = skill_dir / mapped             # relative to this skill
                else:
                    target = ROOT / mapped                  # repo-relative

            checked += 1
            if not target.exists():
                errors.append(
                    f"skills/{name}/{f.name}: references '{token}' which does not exist "
                    f"(looked for {target.relative_to(ROOT) if ROOT in target.parents else target}) "
                    f"- the skill would tell Claude to use a path that is not installed"
                )
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
                if sfile:
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
        "sections": len(registered),
        "paths": paths,
    }


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv

    if not SKILLS.is_dir():
        print("no skills/ directory", file=sys.stderr)
        return 1

    results = [check_skill(d) for d in sorted(SKILLS.iterdir()) if d.is_dir()]

    if not quiet:
        converted = [r for r in results if r["generated"]]
        legacy = [r for r in results if not r["generated"]]
        print(f"{len(results)} skills: {len(converted)} generated, {len(legacy)} legacy\n")
        for r in converted:
            print(f"  generated  /{r['name']:<28} {r['sections']} section(s), {r['paths']} path(s)")
        for r in legacy:
            print(f"  legacy     /{r['name']}")
        print(f"\n{sum(r['paths'] for r in results)} install paths verified")

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
