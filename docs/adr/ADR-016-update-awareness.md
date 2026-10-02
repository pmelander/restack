# ADR-016: Update Awareness: a Throttled, Opt-Out Notice at Session Open, Never a Self-Upgrade

**Status:** Accepted

**Date:** 2026-10-02

**Deciders:** ReStack maintainers

**Technical Story:** [ROADMAP](../../ROADMAP.md) item 6, "Update awareness"

**Implementation Status:** implemented

**Implemented Date:** 2026-10-02

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-02

## Context

An install learns it is stale only when someone remembers to run
`/restack-upgrade`. [ADR-011](ADR-011-setup-script-and-upgrade-skill.md)
accepted that and declined gstack's update check as ceremony for a suite this
size.

2.4.0 changed the cost of that position. It fixed defects that were invisible
from the install. The outside opinion never ran for a copy install, and section
paths resolved against the wrong root
([ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md)). An install
that never upgrades keeps those defects, and because each one fails silently,
nothing in a session tells the architect. A stale install is not merely a
missing feature. It runs the method with a step quietly removed.

A check also brings costs, and they shape the design:

- **Interruption.** A notice that lands inside a gate competes with the
  decision being asked for.
- **Audit trail.** A journey's decisions log records which method produced each
  gate. If the skills change under an in-flight journey, that record stops
  meaning anything.
- **Egress.** In some environments, NLTG among them, any outbound fetch from a
  skill needs to be justified, and there must be a way to switch it off.
- **Windows.** The maintainer runs Git Bash and Windows PowerShell 5.1. Paths
  recorded by one shell are read by a different runtime.

## Decision

1. **The check runs at session-opening commands only:**
   `/restack-journey start`, `/restack-journey where` and
   `/restack-discover paths`. Its instructions live once, in a shared section
   (`scripts/shared/update-check.md`) that is vendored into the two consuming
   skills ([ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md)).
   Each command's first step reads the section. The section says to **skip the
   check if a decision brief is open or the conversation is inside a stop
   gate**. `where` is often asked in the middle of one.
2. **At most once a day, for the check and the notice together.** The script
   records a timestamp in `~/.restack/update-check.json` *before* it fetches, so
   an offline machine pays one timeout a day, not one per session. If the
   timestamp cannot be written, the script does not fetch, because "at most once
   a day" is the promise. A timestamp more than five minutes in the future is
   ignored, so a clock that was set back cannot silence the check for good.
3. **What it compares.** It reads `repo`, `method` and `version` from
   `~/.restack/install.json`, runs `git fetch origin main` in that checkout, and
   compares `origin/main:VERSION` with the installed version. The installed
   version is install.json's `version` for a copy install, and the checkout's
   own `VERSION` for a symlinked one. Versions compare numerically, and the
   notice fires only when the remote is strictly newer.
4. **What it prints.** One line, and the snooze offer is part of that line:
   `ReStack v2.5.0 available (installed v2.4.0): /restack-upgrade  (snooze a week: /restack-upgrade snooze)`.
   The skill shows it verbatim and carries on. It never asks a question about
   it. Snooze lasts seven days by default (1–90 with an argument) and holds one
   version, so a newer release breaks through it.
5. **It never upgrades.** The notice points at `/restack-upgrade`, which the
   architect runs between sessions.
6. **Opt-out.** Two switches, either of which turns the check off, and both are
   read before anything touches the network:
   - `{"update_check": false}` in `~/.restack/config.json`, written by
     `/restack-upgrade off`. `config.json` is the user's file. `setup` never
     writes it, and the script's own state goes in a separate file.
   - `RESTACK_UPDATE_CHECK=off` in the environment, which wins over the file. It
     is for managed machines, where setting a variable by policy is easier than
     writing a file into every home directory.

   A `config.json` that exists but cannot be read counts as **off**. Whoever
   wrote it meant to set something, and the safe reading in an environment that
   restricts egress is "no fetch".
7. **Failure is silent at session open and visible in `status`.** These all
   print nothing and exit 0: no `install.json`, no git checkout, no git, no
   Python, offline, credentials required, a slow network, or an unparseable
   version. An unexpected exception does the same, but it is recorded, and
   `/restack-upgrade check` shows it as `FAILED`.
8. **The script ships in `/restack-upgrade`** (`scripts/update_check.py`, standard
   library only), resolved from `$HOME/.claude/skills/restack-upgrade/...` with
   the repository path as a fallback
   ([ADR-010](ADR-010-skills-are-self-contained.md)). The shared section carries
   a POSIX-sh form, which runs in Git Bash, and a PowerShell 5.1 form.

### The open question: symlinked development installs

**They report, with different wording, and never point at `/restack-upgrade`.**

A symlinked install *is* its checkout, so the upgrade is a pull. Pointing it at
`/restack-upgrade` would be actively harmful. Step 4 of that skill ran plain
`./setup`, which replaces every link with a copy. A shell that cannot create
symlinks does the same thing to `./setup --symlink`: Git Bash without Developer
Mode does, and so does Claude's own sandboxed shell. The development install is
then gone, and the developer has to restore it from an elevated shell.

- On `main`:
  `ReStack v2.5.0 on origin/main; your symlinked checkout is at v2.4.0: git -C "<repo>" pull --ff-only  (snooze ...)`.
  `--ff-only` refuses anything that is not a clean fast-forward.
- On any other branch:
  `ReStack v2.5.0 on origin/main; your symlinked checkout (branch feature/x) is at v2.4.0  (snooze ...)`,
  with no command. Bringing `main` into a feature branch is the developer's
  merge, not an upgrade.

Staying silent for symlink installs was the alternative. It was rejected
because the maintainer's development checkout is also the install they use on
real engagements. A stale feature branch there runs old method on live work,
which is exactly the failure this feature exists to surface.

`/restack-upgrade` changed to match. Step 3 stops when the checkout is not on
`main`. Step 4 never runs plain `./setup` on a symlinked install: it runs
`--symlink --dry-run` and, if a skill was added or removed, asks the architect
to re-link from a shell that can create symlinks.

### Guards that came from the Windows build

- **MSYS paths.** `setup` run from Git Bash records `/c/Users/...`, which native
  Windows Python reads as `C:\c\Users`. Without conversion the check would be
  silent on exactly the machine it was written for.
- **BOM.** `setup.ps1` writes `install.json` with a UTF-8 byte-order mark.
- **Which install.json.** `setup --target <scratch>` rewrites `install.json` for
  the scratch target. The script reports only when `install.json`'s
  `skills_dir` holds the very `restack-upgrade` it is running from
  (`os.path.samefile`, which follows links). Otherwise it stays silent, because
  silence is better than reporting on an install nobody uses.
  *Fixed at the source in 2.5.1: setup no longer records a `--target` run
  ([ADR-011](ADR-011-setup-script-and-upgrade-skill.md), Notes). The guard
  stays, because records written before then are still on disk.*
- **The timeout must hold.** On a timeout, Python kills git. On Windows it then
  waits for git's pipes to close. The transport helper inherits git's stderr and
  outlives the kill, so with stderr piped a "3-second" timeout took 20 seconds
  in testing. stderr goes to `DEVNULL`, and a test with a transport that never
  answers holds the fix in place.
- **No prompts, no windows.** `GIT_TERMINAL_PROMPT=0`, `GCM_INTERACTIVE=never`
  and `SSH_ASKPASS_REQUIRE=never`, plus `CREATE_NO_WINDOW` on Windows. A
  credential dialog at session open is worse than no notice, so a repository
  that needs credentials counts as offline.

### What we took from gstack, and what we did not

`gstack-update-check` is the reference for the throttle and the snooze. Taken:
version-scoped snooze broken by a newer release, a numeric guard so a remote
behind the install never reports, and rejection of anything that does not parse
as a version. That last one covers an HTML error page or a conflict marker.

Not taken:

- **Running on every skill.** gstack checks in every preamble. Here the check
  runs at three entry points.
- **The 12-hour nag.** gstack replays a cached "upgrade available" within its
  cache window. Here the notice, like the fetch, appears at most once a day.
- **Escalating snooze.** gstack escalates 24h, then 48h, then 7d. A 24-hour
  snooze means nothing when the notice already appears at most daily, so there
  is one level of seven days.
- **Printing on a crash.** gstack prints `CHECK_FAILED` on a crash, because its
  silence was mistaken for "up to date" across 45 releases. Here a crash is
  recorded and reported by `status` instead. Both designs refuse to let a
  broken check pass for a current one. They differ in where the failure shows,
  and here it is not at the start of a journey.
- **Telemetry pings, `JUST_UPGRADED` markers, raw-URL fetches.** These were not
  taken: no telemetry
  ([ROADMAP](../../ROADMAP.md), *Deliberately not doing*), no marker, and no
  second endpoint.

### Egress, for environments that restrict it

The only outbound call is `git fetch origin main`, against the remote the
architect cloned from and already pulls from. It is a remote they chose, not a
ReStack endpoint. It sends nothing beyond the git protocol, at most once a day,
capped at five seconds, and cannot prompt. Its only local effect is to update
the checkout's `refs/remotes/origin/main`, which `/restack-upgrade` does anyway.
Both opt-out switches are read before that call.

## Consequences

### Positive

- From 2.5.0 on, a stale install hears about it at the first session open of
  the day. Installs older than 2.5.0 do not have the check, so they still learn
  only by running `/restack-upgrade`. This ADR cannot reach them.
- No new endpoint, no telemetry, and an opt-out that an administrator can set by
  policy.
- The notice cannot land inside a gate, and nothing changes under a journey.
- 34 tests in `tests/test_update_check.py`, which run in CI, cover every silent
  path, the throttle, the snooze, both opt-outs, both symlink wordings, the
  Windows path and BOM cases, a hung transport, and the shared section's
  snippets exactly as written, in `sh`, `bash` and PowerShell.

### Negative

- The check is on by default. A machine where outbound fetches need approval
  must be opted out *before* the first session open. `INSTALL.md` says so
  prominently, and `RESTACK_UPDATE_CHECK=off` exists for fleet-wide policy.
- A skill now writes to the architect's ReStack checkout: it updates
  `origin/main`, never the working tree. That is the same thing an IDE's
  autofetch does, and the reason the opt-out exists.
- `/restack-journey` and `/restack-discover` depend on a file in another skill.
  This is a departure from strict self-containment
  ([ADR-010](ADR-010-skills-are-self-contained.md)). It is accepted because the
  dependency is optional by construction: if the script is missing, the snippet
  prints nothing, which is the same as up to date.
- One more state file in `~/.restack/`, plus a user-owned `config.json`.
  `INSTALL.md` lists both.

### Neutral

- A killed fetch can, in principle, leave a stale ref lock in the checkout. The
  backstop kill fires only when git's own stall abort (three seconds below
  1 KB/s) has not, which in practice is a hung connect, and that happens before
  any ref is locked.

## Alternatives considered

### Put the trigger in a tier-3 preamble fragment
- **Pros:** No template edits.
- **Cons:** It would load into every invocation of `/restack-stressor` and every
  journey command, where it never applies. It also couples a shared fragment to
  three specific command names.
- **Why rejected:** A shared section read by three entry points is the
  mechanism ADR-013 and ADR-015 built for exactly this.

### Offer the snooze through `AskUserQuestion`
- **Pros:** One click.
- **Cons:** It turns a notice into a question at the start of the session, in
  front of the terrain brief. That is the competition with a decision this
  design exists to avoid.
- **Why rejected:** A one-line hint carries the offer without asking anything.

### Fetch `VERSION` over HTTPS from raw.githubusercontent.com
- **Pros:** Touches nothing in the checkout.
- **Cons:** It is a second endpoint, GitHub-specific, and wrong for forks and
  mirrors.
- **Why rejected:** `git fetch` against the architect's own `origin` is the
  smaller egress surface.

### Twin implementations in POSIX sh and PowerShell
- **Pros:** No Python needed.
- **Cons:** It means two copies of the throttle, snooze and comparison logic,
  plus portable epoch arithmetic and timeouts. `timeout` is missing from macOS,
  and `date +%s` is not POSIX. The setup scripts already show what keeping two
  implementations in step costs.
- **Why rejected:** One standard-library Python script, with a short launcher
  in each shell. No Python means no notice, which is silent and harmless.

### Opt-in rather than opt-out
- **Pros:** No fetch without consent.
- **Cons:** The installs that most need the notice are the ones whose owners
  never revisit the settings.
- **Why rejected:** The fetch is small, goes to a remote the architect chose,
  and can be switched off before first use. Revisit this if a deploying
  organisation's policy requires opt-in; flipping the default is one line.

### Upgrade automatically
- **Why rejected:** A skill set that changes under an in-flight journey breaks
  the journey's audit trail, and an upgrade is the architect's decision.

## References

- [ADR-010](ADR-010-skills-are-self-contained.md): skills ship their own runtime dependencies
- [ADR-011](ADR-011-setup-script-and-upgrade-skill.md): setup script and upgrade skill, which declined an update check
- [ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md): vendored shared sections
- `~/.claude/skills/gstack/bin/gstack-update-check`: reference for the throttle and snooze
