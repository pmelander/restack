# ADR-024: Report Old ReStack Skill Copies at Session Open, and Retire Them by Moving, Never Deleting

**Status:** Accepted

**Date:** 2026-10-03

**Deciders:** ReStack maintainers

**Technical Story:** field observation on the reference engagement, 2026-10-03:
a run under ReStack 2.11 still closed with reflection prompts that 2.10
removed; the project carried old copies of the skills

**Implementation Status:** implemented

**Implemented Date:** 2026-10-03

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-03

## Context

Claude Code loads skills from the user profile (`~/.claude/skills/`) and from
the project (`<project>/.claude/skills/`, `.claude/commands/`). Before ReStack
installed into the profile under the `restack-` prefix
([ADR-009](ADR-009-prefix-skill-names.md), [ADR-019](ADR-019-copy-only-install.md)),
projects carried their own copies: `journey`, `adr`, `stressor` and so on.

The reference engagement still had 14 of them. They load beside the installed
`restack-*` skills without any error, and either can answer the same request.
In a field run on 2026-10-03, with 2.11 installed, the session closed with
reflection prompts, a behaviour removed in 2.10
([ADR-022](ADR-022-working-toolkit-not-training-pack.md)). Nothing in ReStack
could see this: `setup` and `/restack-upgrade` only look at the profile's
`restack-*` folders.

The profile has the same problem. An install from before the prefix left
unprefixed copies in `~/.claude/skills/`. The installation guide told users to
inspect them by hand, and ADR-009 deliberately deleted nothing, because an
unprefixed `design-review` may belong to another suite.

## Decision

1. **Detect copies by name and content, not name alone.** A folder or
   command file counts when its name is a ReStack skill's, with or without
   the prefix, **and** its content is ReStack's: the same title as the
   installed skill, or the residuality vocabulary. A `restack-*` folder inside
   a project always counts. In the profile, `restack-*` folders are the
   install and never count. A project's own skill that shares a name (say an
   unrelated `excel`) is left alone, and so is anything that is not a ReStack
   skill name (`md2pdf`).
2. **Only where Claude Code loads from**: `.claude/skills/` and
   `.claude/commands/`. Other tools' configuration (an OpenCode `commands/`
   folder) is not ReStack's business.
3. **Report at session open**, through the existing update check: one line for
   the project and one for the profile, each at most once a day under its own
   key, silent when there are none, and off under the same opt-out. The check
   is local: it needs no install record and no network. `/restack-upgrade
   check` lists the copies in full.
4. **Retire by moving, never by deleting.** `/restack-upgrade retire-local`
   (and `--profile`) lists, shows a dry run, and **stops on a brief**; on yes
   it moves each copy to `.claude/skills-retired-<date>/`, which Claude Code
   does not load, with a README saying how to move one back. A second
   retirement on the same day never overwrites the first.
5. **It lives in `/restack-upgrade`** (`scripts/local_copies.py`, standard
   library), beside the update check, because it is about the installed skill
   set, not about a journey.

## Consequences

### Positive

- A stale copy no longer answers in place of the installed skill unnoticed.
  On the reference engagement: 14 copies found, the two look-alikes left
  alone.
- The profile clean-up ADR-009 left as a manual note is now a command with a
  dry run and an undo.

### Negative

- Detection is heuristic at the edges. A project's own skill that shares a
  ReStack name and mentions residuals would be listed. The list says why each
  one counts, and the brief stands between the list and the move.
- One more line can appear at session open. It is once a day, per project,
  and covered by the opt-out.
- The current session may still hold the old skill's text after retiring.
  The command says so: a new session is needed.

### Neutral

- Retired folders stay until the architect deletes them.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| `scripts/shared/update-check.md` | one line, about updates only | updated: a second kind of line |
| `/restack-upgrade` | "touches nothing that is not restack-*" without exception | updated: the retire-local exception, the command, a repair row |
| `docs/INSTALLATION.md` | inspecting unprefixed copies by hand as the only path | updated |
| CLAUDE.md, QUICKREF.md, README.md | | updated |
| `tests/test_update_check.py` | tests that ran `check` against the real home and the repo root | updated: scratch `HOME`, `USERPROFILE` and working directory |

## Alternatives considered

### Only in `/restack-upgrade check`

- **Pros:** no session-open line.
- **Cons:** nobody runs `check` in a project, so the reference engagement's
  copies would have stayed invisible.
- **Why rejected:** the problem is silent by nature, and only a notice where
  the work happens surfaces it.

### Report only, never move

- **Pros:** ReStack never touches a project's `.claude` folder.
- **Cons:** the architect has to find and move 14 folders by hand, correctly.
- **Why rejected:** moving with a dry run, a brief and an undo note is safer
  than leaving it to a manual clean-up.

### Delete instead of moving

- **Pros:** tidier.
- **Cons:** irreversible, on files the architect may have changed.
- **Why rejected:** a move costs nothing and keeps the undo.

## References

- [ADR-009](ADR-009-prefix-skill-names.md), [ADR-016](ADR-016-update-awareness.md),
  [ADR-019](ADR-019-copy-only-install.md), [ADR-022](ADR-022-working-toolkit-not-training-pack.md)
- `skills/restack-upgrade/scripts/local_copies.py`, `tests/test_local_copies.py`
