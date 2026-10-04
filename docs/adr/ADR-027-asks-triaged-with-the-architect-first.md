# ADR-027: Asks Are Triaged With the Architect Before They Are Packed, and a Send Recorded in Error Can Be Cancelled

**Status:** Accepted

**Date:** 2026-10-04

**Deciders:** ReStack maintainers

**Technical Story:** the first `/restack-journey asks` run on a brownfield
journey, 2026-10-03 to 2026-10-04. Feedback from that engagement, anonymised.

**Implementation Status:** implemented

**Implemented Date:** 2026-10-04

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-04

## Context

[ADR-026](ADR-026-asks-routed-in-the-register.md) routes asks in the
register and writes them out as a send-ready pack, one section per
recipient. Its first real run routed 43 open asks to eight recipients and
wrote a section for each. Then the architect answered the questions,
one choice question each, with an option to defer to the recipient:

- **33 of the 43 were settled by the architect's answers**, and one was
  withdrawn. They spanned sales, the data platform, pricing, security,
  change management, an authorisation system's owner and a platform owner.
- **Nine stayed with the team:** six data questions only BI could answer,
  two load and timeline figures, and one legal decision.
- **Three decisions came straight out of the answers**: price caps fixed, a
  four-eyes control narrowed, and a per-market sign-off dropped, which
  superseded an earlier decision. One answer exposed a structural fact no
  pack asked about: today's traffic mix meant the feature reached no
  customer prices yet.

The pack had been written for the wrong first reader. The `Ask <recipient>:`
prefix says someone outside the design *can* settle a row. It does not say
the architect can't. Packing first would have sent 36 questions to eight
teams and surfaced three decisions and a structural finding weeks later.

Two more faults showed in the same run:

1. **The send record went wrong three times.** The skill recorded sends from
   the architect's answer to "which sections are going out". Those sends had
   not happened. `journey.py` had `assume asked` but no way to take one
   back. The corrections were status lines that repeated the status, and
   `asks` still counted the rows as asked.
2. **Routing was a guess where the owner was unclear.** The architect
   re-routed straight away: questions about the booking platform were the
   architect's own team's concern, and one item belonged to another team.

## Decision

1. **Triage before packing.** After routing is confirmed,
   `/restack-journey asks` puts every routed ask to the architect: one choice
   question per ask, with two or three plausible answers drawn from the row
   and the evidence, and `Defer to <recipient>` always as the last option.
   - An answer is written to the register as it comes:
     `assume status A-<n> Resolved | Partly resolved | Withdrawn` with a
     `--why` that cites the architect and the date.
   - A deferral writes nothing. The row stays routed.
   - **Only deferred asks go into the pack.** Its summary shows how many the
     architect answered next to how many were deferred.
   - The architect can skip triage for one named recipient with
     `--no-triage`, for asks they know must go to that team. Never for the
     whole pack, and never on the skill's judgement.
2. **An architect's answer is Medium confidence.** In the evidence table it
   is "a person who operates it, asked directly", not High. The status line
   says so. Where a wrong answer would be a one-way door, the `--why` names
   the check that would catch it, and a check the design will not wait for
   is registered as its own assumption.
3. **A decision surfaced by an answer is a brief, issued in place.** An
   answer that contradicts a logged decision or withdraws an ADR's point
   stops the triage, and the brief is numbered and asked then
   (`decision open`). It is not queued behind the pack.
4. **A send is recorded only on an explicit "it went".** After writing the
   pack, the skill asks "has any of these sections been sent?" as a question
   of its own. "Which sections are going out" is a plan, not a send.
5. **A send recorded in error is cancelled, not deleted.**
   `journey.py assume unasked A-<n>... --why "..."` appends
   `- A-<n> · <status> · <date> · unasked <recipient>: <why>`. Like `asked`,
   it copies the row's status, so it cannot change one. `asks` reads it as
   cancelling the row's last send: a row sent once is never asked again, and
   a row sent twice goes back to its first send. `assume sync` ignores it, as
   it ignores `asked`. It refuses a row with no send left to cancel.
6. **Where the owner is unclear and the design boundary names the
   architect's team,** routing proposes the architect first. The row is
   triaged unrouted, and its defer option names the outside team; it is
   routed only if deferred.

## Consequences

### Positive

- The questions that leave the design are the ones only someone outside it
  can answer. On the reference run, 9 instead of 43.
- Decisions hidden in "questions for other teams" surface while the
  architect is answering, not when a reply arrives weeks later.
- Every answer is in the register with who gave it, when and at what
  confidence, so a later contradiction can be traced to it.
- The send record can be corrected without editing history, and `asks`
  counts what actually went.

### Negative

- A run with many asks is many questions. On the reference run that was 43,
  answered in minutes, but it is still the architect's time. `--no-triage`
  exists for the recipients where the answer is known to be "send it".
- A deferral is not recorded. A triage interrupted and resumed asks the
  deferred rows again. That costs one click per row and keeps deferral from
  becoming a status of its own.
- An answer from the architect closes a row at Medium. A row that needed
  High stays exposed until its check runs, and only the `--why` says so.

### Neutral

- The status vocabulary does not change, and neither do the register's
  columns. `unasked` is a status-line reason, like `asked`.
- Trace gets no new check. Its REG check compares a row with its last status
  line, and an `unasked` line repeats the status.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| `skills/restack-journey/scripts/journey.py` | no way to cancel a send | `assume unasked`; `asks` and `assume sync` read it |
| `skills/restack-journey/sections/asks-pack.md` | pack first, sends recorded from "going out" | routing default, triage, deferred-only pack, the send question, cancelling |
| `/restack-journey` (`asks`) 2.4.0 | the same | the command's steps and output |
| `templates/assumptions-register-template.md` | `asked` as the only send line | the `unasked` line |
| `scripts/preamble/journey-files.md`, `journey-state.md` | no command to cancel a send | the `unasked` row and line |
| `tests/test_journey.py` | | `unasked`: never asked again, the last send only, refusals, sync and trace |
| CLAUDE.md, QUICKREF.md, GETTING_STARTED.md, CHANGELOG.md | | updated |

## Alternatives considered

### Triage after the pack is written

- **Pros:** the pack is ready to send for anything the architect does not
  answer; the flow ADR-026 shipped stays as it is.
- **Cons:** the pack is written for asks that never go out, and the
  sections have to be rewritten after the answers.
- **Why rejected:** this is what the reference run did, by accident. Most of
  the pack was thrown away.

### Defer by default; the architect picks which asks to answer

- **Pros:** fewer questions; the architect answers only what they choose to.
- **Cons:** an ask the architect could have settled in a second gets sent
  because nobody looked at it, and the decisions hidden in it surface late.
- **Why rejected:** the reference run settled three quarters of the asks.
  The default should match the common case.

### A `Deferred` status

- **Pros:** an interrupted triage would not ask a deferred row again.
- **Cons:** a sixth status means nothing to anyone but this command, and a
  deferred ask is still Open in every sense the method cares about.
- **Why rejected:** ADR-026 kept the vocabulary unchanged for sends for the
  same reason.

### Delete the wrong `asked` line by hand

- **Pros:** no new command.
- **Cons:** the register's status lines are append-only history, and a hand
  edit of it is the kind of write ADR-023 moved into the helper.
- **Why rejected:** a cancellation is a fact about the record and belongs in
  it, with its reason.

## References

- [ADR-022](ADR-022-working-toolkit-not-training-pack.md): the architect owns
  the decisions
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): what a write to
  the journey files may change
- [ADR-026](ADR-026-asks-routed-in-the-register.md): routing, `asked`, and
  the pack
- `scripts/preamble/evidence.md`: "a person who operates it, asked directly"
  is Medium
