# ADR-010: Skills Ship Their Own Runtime Dependencies

**Status:** Accepted

**Date:** 2026-09-05

**Deciders:** ReStack maintainers

**Technical Story:** `/restack-excel` was broken for every user outside the repository

**Implementation Status:** implemented

**Implemented Date:** 2026-09-05

**Implemented By:** ReStack maintainers

**Review Date:** 2027-03-05

## Context

`/restack-excel` shelled out to a Python helper as
`python helpers/read_spreadsheet.py` — a path relative to the working
directory.

The documented install is `cp -R skills/* ~/.claude/skills/`, which copies
`skills/` and nothing else. So after a normal installation the helper was not
in `~/.claude/skills/` at all, and the relative path resolved only when the
user's working directory happened to be the ReStack checkout.

The skill therefore worked while you were sitting in the repository and failed
everywhere else — including the normal case, which is using it on an
architecture project in some other directory. Reproduced against a simulated
install: `can't open file '<project>/helpers/read_spreadsheet.py'`.

This was not a typo. It was a structural assumption — that the repository
layout is present at runtime — and it would recur in any future skill that
acquires a runtime dependency. `/restack-excel` was simply the only skill that
had one.

## Decision

**A skill's runtime dependencies live inside the skill's own directory.**

`helpers/read_spreadsheet.py` moved to
`skills/restack-excel/read_spreadsheet.py`, so `cp -R skills/*` carries it and
the symlink method picks it up unchanged. The `helpers/` directory is gone.

The skill resolves the helper explicitly rather than assuming a working
directory, preferring the installed location and falling back to a repository
checkout:

```bash
RS="$HOME/.claude/skills/restack-excel/read_spreadsheet.py"
[ -f "$RS" ] || RS="skills/restack-excel/read_spreadsheet.py"
```

The general rule, which applies to any skill added later:

**A skill must work when its directory is the only thing that was installed.**
Anything it needs at runtime — a script, a data file, a reference document —
ships inside `skills/<name>/`. Anything needed only to *develop* the toolkit —
the generator, the validator, the preamble fragments — stays in `scripts/` and
never appears on a runtime path.

`templates/` is the one deliberate exception. Skills reference it for canonical
document formats, but only ever to *read a format while producing a document*,
and a missing template degrades to the skill describing the structure inline
rather than failing. It is not a hard runtime dependency, and duplicating four
large templates into the skills that reference them would reintroduce exactly
the two-sources-of-truth problem removed when those skills were converted.

## Consequences

**Positive**

- `/restack-excel` works from any working directory, which is where it is
  actually used.
- The rule is structural rather than a matter of care: a skill directory is now
  the unit of installation, so a future skill with a helper cannot repeat this
  by accident.
- Nothing changes for users. The documented install command is unchanged; it
  now simply carries what it should always have carried.

**Negative**

- A runtime script lives next to instruction files, which is slightly untidy —
  the alternative is a skill that does not work.
- If two skills ever need the same helper, this rule implies duplicating it.
  That would be worth revisiting at the time; with one such helper today, the
  cost is hypothetical and the failure it prevents is not.

**Neutral**

- `requirements.txt` remains at the repository root. It is an install-time
  concern (`pip install openpyxl`), not something the skill reads at runtime.

## Notes

The bug had existed since the Excel utility was added
([ADR-004](ADR-004-add-excel-reading-utility.md)) and survived the reorganisation
into `skills/<name>/`, the rename to ReStack, and the prefixing
([ADR-009](ADR-009-prefix-skill-names.md)) — every one of which touched the
invocation path without anyone noticing it could not resolve.

It surfaced only when someone asked what the Python scripts were for, which is
a reasonable argument for occasionally explaining your own repository out loud.
