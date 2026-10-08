# ADR-033: A Wait Is a Next Move, and a Current Position Is Not Rewritten

**Status:** Proposed

**Date:** 2026-10-07

**Deciders:** ReStack maintainers

**Technical Story:** one brownfield journey, 2026-10-07, straight after an
asks pack. Feedback from that engagement, anonymised.

**Implementation Status:** implemented

**Implemented Date:** 2026-10-07

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-07

> **Amended 2026-10-08:** decisions 4 and 5 added. The first version let a
> command end on a wait over a stale position, and the view still offered a
> command while the journey waited.

## Context

An asks pack ended with everything left waiting on three recipients: one
team's answers (sent the day before) would start the next iteration, a
second team's figures (one ask sent, one not) would feed a number and the
capacity work, and a third team's pack had not gone out. The run said so and
named `/restack-journey where` as the command for when answers arrived.

The architect ran `where` at once, with nothing new. It checked commits, the
register and the asks, found no change, and then asked the architect to choose
between two "close" next moves, recommending a journey review. The two things
the architect could actually do, send the unsent ask and the unsent pack,
appeared only in the question's header.

The skill text produced this faithfully:

- `where` step 5 always recommended a next move. It had no way to say that the
  next step belongs to someone outside the design.
- `next-command.md` ruled out invented moves for utilities only. A tier 3
  command with no real move fell through to "two moves genuinely close", and
  two commands that could run but changed nothing counted as close.
- `where` step 6 always wrote a new position. A second `where` with nothing
  changed would write the same assessment again under a new heading, and its
  history entry would move what ADR-032's position age counts from.

## Decision

### 1. A wait is a next move

When the next gate needs answers only people outside the design can give, and
no ReStack command would change anything that gate needs, `where` says the
journey is waiting. It lists, in order: asks not yet sent, by ID and
recipient (the architect's to send, and the only thing that shortens the
wait); asks pending, with when they were sent and what each answer starts; and
the command for when an answer arrives. It records that as the position's
next move, `waiting on <recipients>; when an answer arrives, /restack-journey
where`, and ends `DONE` with no `Next:` line and no question.

### 2. Only a move that changes what the gate needs is a contender

`next-command.md` (all skills): two moves are close only if each changes
something the next gate needs. A command that merely can run (a review, a
trace, a re-read) is not a contender because nothing else is. "Never invent a
next move" now covers every command whose next step waits on someone outside
the design, not only utilities.

### 3. A current position is restated, not rewritten

`where` checks first whether its own last position still holds: `check` says
nothing in the history and no decision since; the history's last entry is the
`where` or `start` that wrote it; no engagement document is new or changed
since; and the architect brought nothing new into the session. When all four
hold it restates the position and the unsent asks, writes nothing, records no
history entry, and ends. Any doubt about one of them, and it runs the full
assessment.

No history entry, because ADR-032 dates the position from the `where` entry in
the history. An entry from a `where` that wrote nothing would claim a position
that does not exist, and the next read would count from it.

### 4. A stale position comes before the wait *(added 2026-10-08)*

On the same engagement, a session answered a decision while the journey
waited (it re-routed an ask to another team), said everything left was a
wait, and ended with no `Next:`, telling the architect to run `where` when an
answer arrived. The decision made the position stale (ADR-032), and the
restack-view band said so: `position stale since <date> · next
/restack-journey where`. The reply said wait; the file and the view said run
`where` now. The view was right: the recorded wait still named the team the
ask had left.

The two rules disagreed, and the newer one won by accident. Now the stale
note wins: a command that ends on a wait, and got the note from `history
add`, hands off to `/restack-journey where`, which records the wait. Only
`where` ends on a bare wait, because only `where` writes it down.

### 5. A recorded wait reads as one *(added 2026-10-08)*

The wait's field begins `waiting on <recipients>;`. `journey.py check` reads
who from it into the `position:` line (`Current Position of <date>, waiting on
<recipients>: ...`), and restack-view's band shows `waiting on <recipients>` in
place of `next <command>`: there is nothing to run until an answer arrives.
The Position tab keeps the command the wait names behind its button, for when
one does. A stale wait shows as any stale position does. Both read the
`waiting` fixture.

## Consequences

### Positive

- A waiting journey says what it waits on and what the architect can do about
  it, first, instead of offering busywork as a choice.
- A `where` run too early costs one read and changes no file.
- The mod's band reads `next /restack-journey where` from the recorded wait,
  which is the right command once something arrives.

### Negative

- "Nothing the gate needs" is a judgement. A review that would find a real
  defect while the design waits is now not offered; the architect can still
  run it.
- The four conditions for a current position rely on the same-day caveat in
  ADR-032. A history missing its `where` entry makes the full assessment run,
  which is the safe side.
- `journey-files.md` gains an exception to "every command records history".

### Neutral

- No file shape changes. The wait is a sentence in the existing Next move
  field; a journey with none reads as before.

## Knock-on changes

All done in the same step.

| Document | What this decision requires there | Done |
|---|---|---|
| `skills/restack-journey/SKILL.md.tmpl` | `where` step 1 (a current position) and step 5 (a wait) | done 2026-10-07: `/restack-journey` 2.8.0 |
| `scripts/preamble/next-command.md` | contenders change what the gate needs; no invented move while waiting | done 2026-10-07, carried by every skill |
| `scripts/preamble/journey-files.md` | a `where` that wrote nothing records no history | done 2026-10-07 |
| [ADR-020](ADR-020-follow-up-commands-run-without-pause.md) | "two moves genuinely close" narrowed | marked 2026-10-07 |
| CLAUDE.md, QUICKREF.md, CHANGELOG.md | the behaviour and the ADR | done 2026-10-07 |
| `scripts/preamble/next-command.md`, `journey-files.md` | decision 4: a stale position hands off to `where` even on a wait | done 2026-10-08 |
| `skills/restack-journey/scripts/journey.py`, `mods/restack-view/hooks/journey.ts`, `register.tsx`, `types/index.d.ts` | decision 5: `waiting` read from the field; the `position:` line and the band | done 2026-10-08: `/restack-journey` 2.8.1 |
| `tests/fixtures/journey/waiting/`, `tests/test_journey.py`, the mod's tests | one fixture, current and stale, the same text from both readers | done 2026-10-08 |
| `mods/restack-view/README.md` | the waiting band | done 2026-10-08 |

## Alternatives considered

### A `BLOCKED` status for a wait

- **Pros:** the status protocol already has a word for "cannot proceed".
- **Cons:** `where` did its job: the assessment is complete and correct.
  `BLOCKED` reads as a failure of the command, and a chain treats it as one.
- **Why rejected:** the journey waits; the command is done.

### Keep asking, but lead with the unsent asks

- **Pros:** smaller change; the architect still gets a choice.
- **Cons:** the choice is still between moves that change nothing, and every
  wait costs a question.
- **Why rejected:** a question with no real alternative is not the
  architect's call, and ADR-020 pauses only for those.

### Let `where` always rewrite and record

- **Pros:** one path through the command; every run leaves a trace.
- **Cons:** identical positions pile up under new headings, and the history
  entry moves ADR-032's count.
- **Why rejected:** the history records work, and a re-read that found
  nothing is not work.

## References

- [ADR-020](ADR-020-follow-up-commands-run-without-pause.md): only questions
  pause a chain
- [ADR-026](ADR-026-asks-routed-in-the-register.md) and
  [ADR-027](ADR-027-asks-triaged-with-the-architect-first.md): asks, and
  recording a send only when the architect says it went
- [ADR-032](ADR-032-a-stale-position-says-so.md): the position's age, and
  `where` as its only writer
