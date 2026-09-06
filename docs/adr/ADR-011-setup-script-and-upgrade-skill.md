# ADR-011: A Setup Script and an Upgrade Skill, Not `cp -R`

**Status:** Accepted

**Date:** 2026-09-05

**Deciders:** ReStack maintainers

**Technical Story:** Installation and upgrade were manual and lossy

**Implementation Status:** implemented (symlink degradation fixed in 2.1.1 — see Notes)

**Implemented Date:** 2026-09-05

**Implemented By:** ReStack maintainers

**Review Date:** 2027-03-05

## Context

The documented install was `cp -R skills/* ~/.claude/skills/`, and there was no
documented upgrade at all — you pulled and copied again.

That has five problems, in rough order of how much they hurt:

1. **Removed skills linger forever.** A skill renamed or deleted upstream stays
   installed. The user keeps invoking a command the project no longer has, and
   nothing tells them why it behaves oddly. The rename to `restack-*`
   ([ADR-009](ADR-009-prefix-skill-names.md)) left fourteen orphans on every
   existing install, and a plain copy could never clean them up.
2. **No version.** The repository had no `VERSION` file, so nothing could tell
   what was installed or whether it was current.
3. **No record of what changed.** A copy is silent. After an upgrade you cannot
   tell what moved without reading the git log.
4. **No record of where it came from.** Nothing linked the installed skills back
   to a checkout, so an upgrade command would have nowhere to start.
5. **It happily installs a broken tree.** A skill directory with no `SKILL.md`
   is silently ignored by Claude Code — the command simply does not appear, with
   no error to explain it.

gstack solves this with a `setup` script plus a `/gstack-upgrade` skill, and the
shape is right. Its implementation is not transferable: 2,589 lines covering six
hosts, binary builds, a daemon, team mode, migration scripts and snooze
backoff. ReStack is markdown and one Python file.

## Decision

**A `setup` script owns installation; `/restack-upgrade` owns updating.**

`setup` (POSIX sh) and `setup.ps1` (Windows-native) are functionally identical.
They copy or symlink each `skills/restack-*/` directory into the skills
directory, and beyond a copy they:

- **remove ReStack skills that no longer exist upstream** — the problem that
  motivated this
- **report** what was installed, updated, removed and unchanged
- **refuse a broken tree** rather than installing a skill Claude Code will
  ignore
- **record the install** in `~/.restack/install.json` (version, repo path,
  skills directory, method, date)
- **check the optional dependency** and say what it affects
- support `--dry-run`, `--symlink` and `--target`

`/restack-upgrade` reads that state file, compares installed / local / remote
versions, pulls, re-runs `setup`, and summarises the changelog between the two
versions. It is also the documented repair path, since re-running `setup` fixes
almost every partial-install symptom.

`VERSION` and `CHANGELOG.md` now exist, because an upgrade command that cannot
say what changed is not worth invoking.

### The safety property

**`setup` only ever creates, replaces or removes directories whose names begin
with `restack-`.** Nothing else in the skills directory is touched, at all,
under any flag.

This is the direct lesson of [ADR-009](ADR-009-prefix-skill-names.md), where an
unprefixed install silently overwrote another suite's skill. An installer with
a delete step is exactly where that class of damage would recur, so the prefix
scope is the constraint that makes deletion safe to do at all. It is asserted
in both scripts and verified by test: installing over a directory containing
unrelated suites leaves them untouched.

### Installation by reference

`INSTALL.md` carries agent-followable instructions, so "install ReStack from
`https://github.com/pmelander/restack`" is a workable request to a Claude Code
session. It requires explicit consent before writing to `~/.claude/skills/`,
shows `--dry-run` output before installing, refuses to touch anything outside
the prefix, and will not install Python packages without asking.

Installing skills changes how every future session behaves. That is not a change
to make on an implied instruction, which is why consent is a step rather than an
assumption.

### What we did not take from gstack

Update checks in the preamble, snooze with escalating backoff, auto-upgrade,
version migration scripts, team mode, vendored-copy synchronisation, multi-host
support. Each solves a real problem for a large distributed suite and would be
ceremony here — the same reasoning as
[ADR-008](ADR-008-generated-skills-with-tiered-preamble.md).

Migrations are the one worth revisiting if state ever accumulates that `setup`
cannot fix by itself. It does not today: the install is fifteen directories and
one small JSON file.

## Consequences

**Positive**

- Upgrading is one command, and it reports what changed.
- Orphaned skills get cleaned up — including the fourteen unprefixed ones left
  by ADR-009 on any pre-existing install.
- A broken or partial install has a documented repair: re-run `setup`.
- Agent-driven installation is possible without the agent improvising file
  operations.
- `--symlink` makes developing ReStack materially easier: edit the template,
  regenerate, and the change is live with no reinstall.

**Negative**

- Two installer implementations to keep in step. They are ~180 lines each and
  behaviourally identical; a divergence would show up the first time either is
  run. Accepted because requiring a POSIX shell on Windows is a worse tax on the
  primary audience.
- One more skill to maintain (`/restack-upgrade`, tier 1).
- `~/.restack/` is new state outside the repository. It holds one JSON file and
  `INSTALL.md` documents removing it.

**Neutral**

- `cp -R skills/* ~/.claude/skills/` still works and still installs usable
  skills. It just does not clean up, report, or record anything.

## Notes

**2.1.1 — the symlink promise was false on Windows.** `--symlink` used `ln -s`
and trusted its exit status. MSYS/Git Bash without symlink support *silently
copies*: the command succeeds, returns 0, and produces a directory. setup then
printed "Symlinked: edits in the repo are live", which was untrue, and the user
edited the repository and watched nothing happen. Found by using the toolkit —
a skill invocation served content from before an edit, and the install turned
out to be a copy wearing a symlink's name.

Both scripts now probe symlink capability once before installing, degrade to
copy with an explicit warning naming the fix, and verify each link as it is
created. The header reports the method actually used. `setup.ps1` had the same
defect in a different form: `New-Item -ItemType SymbolicLink` throws without
Developer Mode, which under `$ErrorActionPreference = 'Stop'` would have
aborted the install partway through.

The general lesson, which applies beyond this script: **a tool that reports
success for an operation it did not perform is worse than one that fails.**
Failure is visible; a false claim is discovered days later, by which point it
has been trusted.

`/restack-upgrade` is tier 1 rather than tier 2, deliberately. Tier 2 supplies
decision briefs whose format is architecture-shaped — an `Aspiration:` line and
"which actor, which path" — which is nonsense for "shall I pull?". The
destructive confirmation it does need (uncommitted changes, unpushed commits) is
written inline instead.

That is the tier system behaving as intended: a utility does not inherit
machinery built for architectural judgement.
