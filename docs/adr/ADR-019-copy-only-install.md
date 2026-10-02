# ADR-019: The Install Is a Copy in the User Profile; Upgrades Come From a Temporary Clone

**Status:** Accepted. Supersedes parts of [ADR-011](ADR-011-setup-script-and-upgrade-skill.md) and [ADR-016](ADR-016-update-awareness.md)

**Date:** 2026-10-02

**Deciders:** ReStack maintainers

**Technical Story:** Maintainer request: "ReStack should always install on the user profile. Updating should not pull a remote into, or symlink to, a working directory."

**Implementation Status:** implemented

**Implemented Date:** 2026-10-02

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-02

## Context

Until 2.6, an install was a checkout plus a copy or symlink step.
`/restack-upgrade` pulled `main` into the recorded checkout and re-ran `setup`,
and the update check fetched inside that checkout. That model assumes everyone
keeps a clone, and nobody but the maintainer does: an installer clones, runs
`setup`, and has no reason to keep the clone. For them:

- **Deleting the clone broke the upgrade path.** `/restack-upgrade` could no
  longer find a checkout, and the update check went silent for good. The notice
  ADR-016 built was dead on arrival for most installs.
- **Deleting the clone of a symlinked install broke every skill.** The links
  pointed at nothing, and all `/restack-*` commands vanished.

For the maintainer, the symlinked development install cost more than it saved:

- **Work in progress leaked into every session.** Another session's
  uncommitted edits in the checkout were live in the maintainer's skills the
  moment they were saved. It happened during this change itself: the
  in-progress `/restack-upgrade` was what the maintainer's sessions loaded.
- **Symlinks need privileges on Windows.** A shell without Developer Mode or
  elevation, including the sandbox agents run in, could not create them. setup
  degraded to a copy and replaced the links. Restoring them took an elevated
  shell, twice in one afternoon.
- **Removing a link is hazardous.** The "removed upstream" loop deleted a link
  by `rm -rf` with a trailing slash. In Git Bash that deleted the contents of
  the directory a junction pointed at, which was confirmed by test against the
  2.5.3 script. In practice the target was usually gone already, because a pull
  had removed the skill's source, but a link into any other directory would
  have been emptied. Windows PowerShell 5.1's `Remove-Item -Recurse` is widely
  reported to follow directory links the same way. That did not reproduce
  against a junction on the test machine, and a real symbolic link could not be
  created there to test, so it is unconfirmed.

## Decision

1. **setup always installs a copy into `$HOME/.claude/skills`**
   (`$env:USERPROFILE\.claude\skills` for `setup.ps1`). `--symlink`, `--target`
   and `CLAUDE_SKILLS_DIR` are removed. The first two are refused with a message
   naming this ADR. The variable is ignored, with a note saying so.
2. **The install does not depend on the checkout it came from.** Deleting the
   checkout leaves every skill working. A test asserts it.
3. **setup records `source`**, the checkout's `origin` URL, or the project URL
   for a download. That is where releases come from. `repo` is kept as
   provenance: where the install was last copied from, which may no longer
   exist.
4. **`/restack-upgrade` never touches a checkout.** It clones `main` from
   `source` at depth 1 into a `restack-upgrade.*` temporary directory, runs that
   clone's `setup`, verifies, summarises the changelog, and deletes the
   directory. If the installed version is ahead of the release, as with an
   unreleased install from a maintainer's branch, it stops and asks before
   downgrading.
5. **The update check needs no checkout.** It fetches `main` from `source` at
   depth 1 into a bare cache at `~/.restack/upstream.git`. Throttle, snooze,
   opt-out and timeouts are unchanged from ADR-016. A record from before 2.7.0
   has no `source`, so it falls back to the origin of the checkout the record
   names, while that checkout still exists.
6. **A link left by an old symlinked install is replaced by a copy, and removed
   as a link.** POSIX: `rm -f` on the link, never `rm -rf` and never with a
   trailing slash. PowerShell: `Directory.Delete(path, $false)` on any reparse
   point. Tests cover both a link to an installed skill and a link to a skill
   removed upstream, and assert the target survives.
7. **The maintainer installs edits with `python scripts/gen_skills.py &&
   ./setup`.** It is one command instead of none, and it is explicit: what the
   maintainer's sessions load is what they last installed, never what another
   session is half-way through.

### Decision-point accounting: ADR-011

| # | Decision point in ADR-011 | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| 1 | `setup` owns installation, `/restack-upgrade` owns updating | holds | — | — |
| 2 | `setup` and `setup.ps1` are functionally identical | holds | — | Both run the same test cases |
| 3 | Copy **or symlink** each skill | replaced: copy only | Symlink: maintainer edits not reaching the install without a re-run | `gen_skills.py && ./setup`, one explicit command (point 7) |
| 4 | Remove ReStack skills deleted upstream | holds, now link-safe | A command lingering after it was removed | Same, plus links are removed as links |
| 5 | Report installed / updated / removed / unchanged | holds | — | — |
| 6 | Refuse a broken tree | holds | — | — |
| 7 | Record the install, only for the default skills directory | replaced: always the default; adds `source` | A scratch install overwriting the record | No other target exists to overwrite it |
| 8 | Check the optional dependency | holds | — | — |
| 9 | `--dry-run` | holds | — | — |
| 10 | `--symlink` | withdrawn | See 3 | See 3 |
| 11 | `--target DIR` | withdrawn | Testing an install without touching the real profile | Tests point `HOME`/`USERPROFILE` at a scratch directory (`tests/test_setup.py`) |
| 12 | `CLAUDE_SKILLS_DIR` | withdrawn | Installing where Claude Code reads skills when that is not `~/.claude/skills` | **Nothing. Accepted gap:** a Claude Code profile moved with `CLAUDE_CONFIG_DIR` is not supported. setup notes when the variable is set |
| 13 | `/restack-upgrade` pulls into the recorded checkout, then re-runs setup | replaced: temporary clone | Upgrading without re-downloading the repository | A depth-1 clone. ReStack is text, so it is small |
| 14 | Upgrade stops on local changes or unpushed commits | withdrawn | Losing a developer's work to a pull | Structural: the upgrade never touches a checkout |
| 15 | `VERSION` and `CHANGELOG.md` exist | holds | — | — |
| 16 | Only `restack-*` is ever touched | holds | Damaging another skill suite (ADR-009) | Same |
| 17 | Installation by reference, with consent | holds | — | INSTALL.md updated: clone anywhere, run setup, delete the clone if you like |

### Decision-point accounting: ADR-016

| # | Decision point in ADR-016 | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| 1 | Fetch `origin main` in the recorded checkout | replaced: fetch `source` into `~/.restack/upstream.git` | — | — (the old way was the failure: no checkout, no check) |
| 2 | A symlinked install's version is the checkout's `VERSION` | withdrawn | Comparing a stale record against the remote | Installs are copies, so the record is what runs |
| 3 | A symlinked install is told to `git pull`, never sent to `/restack-upgrade` | withdrawn | `/restack-upgrade` replacing a developer's links with copies | Replacing them is now the intended migration, and it removes links as links |
| 4 | Silence when offline, no checkout, or no record | holds, as "no source" | A session opening with an error about an optional notice | Same |
| 5–9 | Throttle, snooze, opt-out, timeouts, never self-upgrade | hold | — | — |

## Consequences

### Positive

- An installer can delete the clone. The skills keep working, the update notice
  keeps working, and `/restack-upgrade` keeps working.
- The maintainer's sessions load what the maintainer installed. Another
  session's work in progress no longer leaks into them.
- No step needs symlink privileges, so nothing needs Developer Mode or an
  elevated shell, and no agent sandbox can replace a link install by accident.
- `/restack-upgrade` cannot damage work in a checkout, because it never opens
  one. The stash-or-abort branch of the skill is gone.
- A data-loss path in the old `setup`, deleting through a link, is closed and
  tested.

### Negative

- The maintainer must run `./setup` after editing. Forgetting it means testing
  stale skills. Mitigation: `setup` says so at the end, and CLAUDE.md puts it in
  the edit loop.
- Every upgrade downloads a fresh depth-1 clone rather than an incremental
  pull. That is small for a text repository, but not nothing on a slow link.
- `CLAUDE_CONFIG_DIR` users cannot install (decision-point 12). If anyone
  needs it, the right fix is to follow `CLAUDE_CONFIG_DIR`, not to bring back a
  free-form target.
- The update check keeps a small bare cache in `~/.restack/upstream.git`.
  `rm -rf ~/.restack` removes it with everything else.

### Neutral

- `install.json` keeps `method`, always `"copy"`, so a reader written for 2.6
  still parses it.
- `--copy` is still accepted and does nothing, so a script that passed the old
  default keeps working.

## Alternatives considered

### Keep `--symlink` as an opt-in for maintainers only
- **Pros:** Edits are live without a re-run.
- **Cons:** It keeps every problem above for the one person most exposed to
  them: work-in-progress leakage, Windows privileges, and link deletion.
- **Why rejected:** The maintainer asked for exactly this to go. One explicit
  command is a better trade than live edits from a shared working tree.

### Keep pulling into the recorded checkout when it exists, and clone only when it does not
- **Pros:** Saves a download for a maintainer.
- **Cons:** Two upgrade paths, and the one that touches a checkout is the one
  that needs the dirty-checkout, branch and unpushed-commit safeguards. The
  maintainer's checkout is on a feature branch more often than not.
- **Why rejected:** A single path that cannot touch a checkout is simpler and
  safer than two paths, one of which can.

### Read the remote `VERSION` over HTTPS from raw.githubusercontent.com
- **Pros:** No cache directory, one small request.
- **Cons:** GitHub-specific. A fork, a mirror or an internal host would silently
  lose the check. It is also a second kind of outbound call to explain on
  egress-restricted machines.
- **Why rejected:** A git fetch works against any host the architect can clone
  from, through the same proxy and credentials.

## References

- [ADR-009](ADR-009-prefix-skill-names.md): the `restack-*` safety scope
- [ADR-010](ADR-010-skills-are-self-contained.md): skills ship what they run
- [ADR-011](ADR-011-setup-script-and-upgrade-skill.md): setup and the upgrade skill
- [ADR-016](ADR-016-update-awareness.md): the update notice
