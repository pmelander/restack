# ADR-026: Asks to People Outside the Design Are Routed in the Register and Written Out as a Send-Ready Pack

**Status:** Accepted

**Date:** 2026-10-03

**Deciders:** ReStack maintainers

**Technical Story:** the reference engagement's Documentation/Review phase.
Seven recipients were waiting on asks, and only one document was ready to send.

**Implementation Status:** implemented

**Implemented Date:** 2026-10-03

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-03

## Context

The method keeps making asks and never writes them out.

- `/restack-journey start` and `/restack-discover` set a **design boundary**.
  Anything beyond it "becomes a handoff ask rather than something to
  investigate".
- `/restack-stressor walk` treats an actor beyond the boundary as a black box
  and turns "each question about its internals into a handoff ask".
- The journey-state contract says the same, and the assumptions register is
  where each ask ends up: an unverified belief, with the check that would
  settle it.

Nothing between the register and the person who has to answer turns those
rows into something that can be sent. At the end of the reference
engagement's design review, the architect had asks waiting for seven
recipients: a data team, the pricing team, security, change management, the
owner of an authorisation system, and two neighbouring delivery teams. A
send-ready document existed for three of them, and it had been written by
hand. The rest were spread across a register of about 150 rows, two review
reports and that day's decisions. The architect's question was "do we have a
skill to summarise the separate asks?", and the answer was no.

Three things make this harder than a summary:

1. **The register does not say who to ask.** Its seven columns are ID,
   Assumption, Source, Validates it, Depends on it, Status and Status date.
   The recipient is sometimes implied by the "Validates it" text ("confirm
   with BI") and often not at all. Routing every row from scratch on every
   pack gives a different answer each time, and nobody can check it.
2. **The register does not say what was already asked.** "Waiting on your
   sends" and "asked three weeks ago with no answer" call for different
   actions, and the files cannot tell them apart.
3. **The register is written for the architect.** Its rows say "residual",
   "S-114", "D29". A recipient outside the design needs the question, why it
   matters to them, and what is held up while it stays open.

## Decision

1. **The recipient is recorded in the register, in the "Validates it" cell,
   as a leading `Ask <recipient>:`.** For example: `Ask BI: row counts per
   market for Q3, from the warehouse`. The canonical seven columns stay as
   they are. A row without the prefix is settled inside the design (a test, a
   code read, our own analysis) and is never an ask. `journey.py` reads the
   prefix and does not interpret anything after it.
2. **Asks are routed when they are made.**
   - `assume add` takes `--ask <recipient>` and writes the prefix.
   - `/restack-discover`, `/restack-stressor walk` and the journey-state
     fragment, which say "turn it into a handoff ask", now say to register it
     with `--ask`.
   - A new command, `assume route A-<n> <recipient>`, adds the prefix to an
     existing row, for registers written before this decision. It changes
     only the start of that one cell. It never changes a status, a decision or
     a date, and it never runs without the architect confirming the recipient
     ([ADR-023](ADR-023-journey-files-written-by-a-helper.md)'s rule for the
     helper).
3. **Sending is recorded as a status line that keeps the status:**
   `- A-<n> · Open · <date> · asked <recipient>`. The status vocabulary does
   not change. An ask is Open until its answer settles it, whether or not it
   has been sent. `assume asked A-<n>... --to <recipient>` writes these lines.
   It copies each row's current status rather than taking one, so recording a
   send cannot change a status. It refuses a row that is not routed to that
   recipient, or that is no longer Open or Partly resolved. `assume status`
   could write the same line, but only if the caller restates the current
   status correctly every time.
4. **`journey.py asks` is read-only and lists the asks** for every Open or
   Partly resolved row with an `Ask` prefix, grouped by recipient. Each ask
   carries its assumption, its check, what depends on it, its source, and when
   it was last asked, or "never". The command also lists open rows whose
   "Validates it" text names someone outside the design but has no prefix,
   and leaves those for the architect to route. Like trace
   ([ADR-021](ADR-021-trace-checks-as-a-worklist.md)), the output is a
   worklist and not a verdict. The script groups and dates the asks; it does
   not decide who should answer or what to ask.
5. **`/restack-journey asks [recipient]` writes the pack:**
   `docs/journey/asks-<YYYY-MM-DD>.md`, one document with a section per
   recipient. Each section stands on its own, so it can be forwarded without
   the rest. A section covers:
   - **what we need**, as a question whose answer settles the check;
   - **why it matters to the recipient**, translated out of the method's
     vocabulary;
   - **what it holds up**: the gate, decision or iteration waiting on it;
   - **what we already know**: the source, with a link wherever the recipient
     can open it;
   - **the assumption IDs it closes**, kept as a reference line so an answer
     can be matched back;
   - **when it was last asked**, and a line saying the ask is being repeated
     when it has been asked before.

   A send that closes no assumption, such as an updated document delivered to
   a neighbouring team, goes in a separate **Also going out** list with no
   A-ID. If it is really a question, it is registered first and then packed.
   This keeps the register as the only record of what is outstanding.
6. **The skill never sends anything and never marks an ask as sent on its
   own.** After the architect says a section has gone out, the skill records
   `asked <recipient>` for each A-ID in that section. Sending, and to whom, is
   the architect's call.

## Consequences

### Positive

- Every ask that reaches a recipient traces to a register row, and every
  routed open row reaches a pack. The pack can be checked against the
  register, not trusted.
- "Never asked", "asked and waiting" and "asked twice" are visible. The pack
  can tell the architect who to chase.
- Routing happens once, when the ask is made and its context is fresh,
  instead of being rebuilt at the end of a phase from a 150-row file.
- Packs are dated and kept, so what was asked of whom, and when, survives the
  engagement.

### Negative

- The `Ask <recipient>:` prefix now matters to the tooling, as the residual
  format did in [ADR-025](ADR-025-matrix-arithmetic-by-script.md). An ask
  written as prose in the cell will not be packed. `journey.py asks` lists the
  likely ones instead of guessing.
- Recipient names are free text. "BI", "BI team" and "Data/BI" become three
  sections. The script lists the recipient names it found so the architect
  can merge them with `assume route`. It does not normalise them.
- A long-running engagement gets many status lines that only say "asked".
  They are history, and the register's rules already put them below the
  table.

### Neutral

- Trace gets no new check. An ask that has gone unanswered is a follow-up,
  not drift between documents.
- The existing hand-written handoff document in an engagement stays as it is.
  The pack does not replace or rewrite it, and can link to it from the
  matching sections.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| `skills/restack-journey/scripts/journey.py` | no recipient, no `asks` | `assume add --ask`, `assume route`, `assume asked`, `asks` |
| `templates/assumptions-register-template.md` | "Validates it" as free text only | the `Ask <recipient>:` prefix, and the `asked` status line |
| `scripts/preamble/journey-files.md` | no command for an ask, or for sending one | rows for `--ask`, `route`, and recording a send |
| `scripts/preamble/journey-state.md` | "turn it into a handoff ask" with no shape | register it with `--ask` |
| `/restack-discover` (step 2), `/restack-stressor walk` | the same | the same |
| `/restack-journey` | no `asks` command | `asks [recipient]` added; `where` mentions asks that were never sent |
| `tests/test_journey.py`, `tests/fixtures/journey/` | | routed, unrouted and asked rows; `route` changes one cell only |
| CLAUDE.md, QUICKREF.md, README.md, GETTING_STARTED.md, CHANGELOG.md | | updated |

## Alternatives considered

### An eighth register column, "Ask of"

- **Pros:** explicit, and easy to read in a table.
- **Cons:** every existing register fails `journey.py check` until it is
  migrated, and most rows would leave the column empty, because most
  assumptions are settled inside the design.
- **Why rejected:** it is a schema change for every engagement to serve the
  rows that need it, and the "Validates it" cell already holds the who-and-how
  in prose.

### A separate asks register

- **Pros:** the assumptions register is untouched, and asks could carry
  fields assumptions do not need.
- **Cons:** the same open question would live in two files that can disagree,
  which is the drift trace exists to find.
- **Why rejected:** one record of what is outstanding.

### Route at write time, with nothing recorded

- **Pros:** no format change at all; the model reads "Validates it" and
  groups the rows.
- **Cons:** the routing is redone on every pack and can differ between runs;
  a pack cannot be checked against anything; nothing records what was sent.
- **Why rejected:** this is what the reference engagement did by hand. It
  produced one send-ready document out of seven.

### A mode of `/restack-solution-doc`

- **Pros:** it already writes documents meant for other people.
- **Cons:** its documents describe the system. The asks pack is derived from
  journey state, which `/restack-journey` owns.
- **Why rejected:** the writer belongs with the owner of the files it reads,
  for the same reason as in
  [ADR-023](ADR-023-journey-files-written-by-a-helper.md).

## References

- [ADR-021](ADR-021-trace-checks-as-a-worklist.md): output as a worklist, not
  a verdict
- [ADR-022](ADR-022-working-toolkit-not-training-pack.md): the architect owns
  the decisions
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): the helper, the
  canonical register, and what a write may change
- `scripts/preamble/journey-state.md`: the design boundary and handoff asks
