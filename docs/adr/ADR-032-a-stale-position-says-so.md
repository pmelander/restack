# ADR-032: A Stale Position Says So, and Only `where` Rewrites It

**Status:** Proposed

**Date:** 2026-10-07

**Deciders:** ReStack maintainers

**Technical Story:** one brownfield journey's Position tab, 2026-10-03 to
2026-10-07. Feedback from that engagement, anonymised.

**Implementation Status:** implemented

**Implemented Date:** 2026-10-07

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-07

## Context

The restack-view mod's Position tab and band offered
`/restack-design-review complete` as the next move four days after that
review had run. The mod read the file correctly. The file was out of date.

`journey-state.md` holds two kinds of content:

- **an assessment**: `Last Updated`, the `Current Phase` line, *Current
  Position* with its next move, the Iteration Log, Known Gaps and Journey
  Health. `/restack-journey where` writes it (`start` writes the first one).
- **a record**: the *Journey History*. Every command appends to it.

Nothing connected the two. On the reference engagement, `where` wrote the
position on 2026-10-03 and recommended the complete design review. The review
ran the same day. Over the next four days the history grew by 38 entries and
the decisions log by 20 answered decisions (one falsified the main conversion
assumption), and the same file still said `Last Updated: 2026-10-03` and
recommended the review. Its phase line named next moves that had been done on
10-04 and 10-05. Its Iteration Log stopped at iteration 2 of 7.

Every part did its job: `where` wrote a sound assessment, each later command
logged itself, and the mod showed what the file said. What was missing was
anything that compared the assessment's date with the record written after it.

## Decision

### 1. The assessment stays `where`'s

Only `/restack-journey where` and `start` rewrite Current Position, the phase
line and `Last Updated`. No other command, and not `journey.py`, brings them
up to date. Bumping `Last Updated` on every history entry, or rewriting the
phase from the latest command, would make the file look current while the
assessment underneath it stayed old. That is worse than an obviously old
date. The next move is the architect's call, made in `where`.

### 2. The age of the position is computed, the same way everywhere

`journey.py` (`position_age`) and the mod (`positionAge`) read the same three
things, and are tested on the same fixture (`tests/fixtures/journey/stale/`):

- **The position's date:** the first date in the newest `###` subsection of
  *Current Position*, else the header's `Last Updated`.
- **The history after it:** every entry on a later date, and on the same date
  every entry after that date's last `/restack-journey start` or `where`, in
  file order. With no such entry the same-day entries are left out: nothing
  says which side of the position they fall on. Histories are not always in
  date order after a migration, so dates decide, not position in the file.
- **Whether the next move ran:** the first entry after the position whose
  command is the recorded move, perhaps with more arguments after it
  (`/restack-adr update 0007` ran `/restack-adr update`; `00071` did not).
- **The decisions since:** the decisions answered on a later date than the
  position. Same-day decisions are left out for the same reason.

### 3. Stale means the move ran or a decision came after it

A position is **stale** when its recorded next move has run, or a decision was
answered after it. Both mean the route may have changed under it. Other
history after the position is counted and shown, never called stale: an
architect may well do other work before the recorded move, and a warning
that fires after nearly every command would stop being read.

### 4. Where it is said

- **`journey.py check`** prints a `position:` line for the state file: the
  date, the history and decisions since, whether the move ran, and when stale,
  that `/restack-journey where` rewrites it.
- **`journey.py history add`** prints the same line as a `note:` whenever the
  position is stale, except when the command being recorded is `where` or
  `start`. It writes nothing beyond the entry.
- **The mod** shows the line under the next move on the Position tab. When the
  position is stale, the band reads `position stale since <date> · next
  /restack-journey where`, and the pane's button fills `/restack-journey
  where`. The recorded move stays visible in the position text itself.
- **The handoff** (`journey-files.md`): a skill that gets the note makes
  `/restack-journey where` its `Next:` move, unless its own work has a step
  that must come first, and then names `where` as the alternative.

### 5. Every ReStack command records history

The journey-files fragment told only `/restack-journey` commands to run
`history add`. In practice every skill on the reference engagement wrote
history, and the rule above depends on it. The fragment now says any ReStack
command that finishes records its entry.

### 6. `where` dates what it writes

`where` runs `check` first and reads everything after the position's date
before trusting the file above its history. It writes a new dated `###`
subsection, updates `Last Updated` and the phase line to match, names any
other section it found older than the history (rewriting it when the
assessment covers it), and records its own history entry, which is what later
reads date the position from.

## Consequences

### Positive

- The mod can no longer show a finished move as the next one without saying
  so, and the band points at the command that fixes it.
- The working session hears that the position is stale at the moment it
  becomes stale, not when someone opens the pane days later.
- `check` gives the same answer without the mod, as ADR-029 requires of
  everything the mod shows.

### Negative

- The move-ran test is textual. A history entry that describes the move in
  other words (`complete review`) is not matched, and the position looks
  fresher than it is until a decision lands. The decision rule is the
  backstop.
- Same-day ordering depends on the `where` entry being in the history. A
  `where` that never recorded itself leaves that day's work out of the count.
- One more line in `check` and, while stale, after every `history add`.

### Neutral

- The canonical shapes don't change. No file needs migrating, and a journey
  with no dated position simply gets no `position:` line.
- The mod stays a view: it computes and shows; it never writes the position.

## Knock-on changes

All done in the same step.

| Document | What this decision requires there | Done |
|---|---|---|
| `skills/restack-journey/scripts/journey.py` | `position_age`, `position_note`; `check` prints it; `history add` notes it | done 2026-10-07 |
| `mods/restack-view/hooks/journey.ts`, `register.tsx`, `types/index.d.ts` | `positionAge`, `positionNote`, `ran`; the band's stale piece; the note and the button on Position | done 2026-10-07 |
| `tests/fixtures/journey/stale/`, `tests/test_journey.py`, the mod's tests | one fixture, the same numbers from both readers, a planted neighbour per rule | done 2026-10-07 |
| `scripts/preamble/journey-files.md` | every command records history; the stale note goes into the handoff | done 2026-10-07, carried by every tier 2 and 3 skill |
| `skills/restack-journey/SKILL.md.tmpl` | `where` steps 1 and 6 | done 2026-10-07: `/restack-journey` 2.7.0 |
| [ADR-029](ADR-029-a-journey-view-as-a-mod.md) | the band's next move can be `where` | marked 2026-10-07 |
| CLAUDE.md, QUICKREF.md, `mods/restack-view/README.md`, CHANGELOG.md | the behaviour and the ADR | done 2026-10-07 |

## Alternatives considered

### Bump `Last Updated` on every write

- **Pros:** one line in `history add`, and the date is never old.
- **Cons:** the date would then describe the file, not the assessment. The
  position, the phase line and the next move would still be four days old,
  under a date that says today.
- **Why rejected:** it hides exactly what this decision exists to show.

### Have each skill rewrite the position when it finishes

- **Pros:** the file would stay current without a separate step.
- **Cons:** sixteen skills writing the route's next move, each from its own
  corner. The position is an assessment of the whole journey, and the next
  move is the architect's to accept.
- **Why rejected:** decisions stay with the architect, and `where` is where
  they make this one.

### A lighter refresh command beside `where`

- **Pros:** cheaper to run after every few commands.
- **Cons:** a second writer of the assessment, with its own rules for what it
  may skip.
- **Why rejected:** the architect chose one writer. Revisit if `where` proves
  too heavy to run as often as the warning asks.

### Warn on any history after the position

- **Pros:** catches every case the textual match misses.
- **Cons:** fires after nearly every command, so it would be muted.
- **Why rejected:** a validator that cries wolf is a failed control. The count
  is shown in the pane instead.

### A trace check

- **Pros:** `/restack-trace` already looks for drift.
- **Cons:** a stale position is journey state, not drift between documents,
  and it needs saying when the work happens, not at review.
- **Why rejected:** as for the register's load in ADR-031, the helper that
  owns the file says it.

## References

- [ADR-020](ADR-020-follow-up-commands-run-without-pause.md): the handoff the
  stale note goes into
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): the helper that
  writes the journey files and never decides for the architect
- [ADR-029](ADR-029-a-journey-view-as-a-mod.md): the mod is a view, and
  everything it shows has a command that answers the same
- [ADR-031](ADR-031-assumptions-drained-where-the-work-settles-them.md): the
  same failure for the register: a step that adds, and none that closes
