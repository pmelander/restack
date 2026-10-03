# ADR-023: The Journey Files Are Written by a Helper, and Old Shapes Migrate Without Material Change

**Status:** Accepted

**Date:** 2026-10-03

**Deciders:** ReStack maintainers

**Technical Story:** [ROADMAP](../../ROADMAP.md) item 3, "Journey state as
tooling rather than prose", the writing half; part of item 9, "Restyle an
existing project", for the journey files; 2.4.0 field feedback items 9, 11
and 14

**Implementation Status:** implemented

**Implemented Date:** 2026-10-03

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-03

## Context

The journey-state contract defines one shape for each of three files (the
decisions log, the assumptions register, the journey history) so that "any
agent can append in one line". Until now the line was prose that the model
followed. On the reference brownfield engagement it was followed partly:

- the register ended with 18 tables of different columns, 30 "Update"
  headings, and 59 rows that scripted appends had landed outside any table;
- 17 rows still said Open in the table after a later update in the same file
  had closed or falsified them;
- the decisions log mixed `## <date>: D<n>, ...` and `## D<n> · <date> · ...`
  headings, and 18 decisions never recorded whether they changed the actor
  set;
- the journey history was a table in the middle of `journey-state.md`, not an
  append-only list at the end.

[ADR-021](ADR-021-trace-checks-as-a-worklist.md) made the damage visible. It
does not stop it, because the damage enters at the write.

D-numbering had a gap the prose could not close. The contract said a brief
that was never answered keeps its number, but only answered briefs were
logged, so no file recorded which numbers were taken. Field feedback item 14
(an interrupted brief must be re-issued, never inferred) had nowhere to look.

## Decision

1. **`journey.py` writes the three files**, shipped in `/restack-journey`
   (`scripts/journey.py`, standard library, no network), because that skill
   owns the journey-state contract. Commands: `assume add`, `assume status`,
   `decision next | open | answer`, `history add`, `check`, `migrate`.
2. **Every skill from tier 2 up uses it** through a new tier-2 preamble
   fragment, `journey-files.md`: the snippet that finds it, the command for
   each moment, and the rules. Tier 2 is where skills start writing decisions
   and assumptions. The dependency is optional by construction
   ([ADR-016](ADR-016-update-awareness.md)): with no script or no Python, the
   snippet says so and the files are written by hand in the canonical shape.
3. **A brief takes its number when it is issued.** `decision open` writes the
   entry with `**Answer:** (open)` before the brief is asked; `decision answer`
   fills it. The next number is one past every `D<n>` in any heading of the
   log, so a number mentioned in an event entry is not reused either. An entry
   still open at resumption is re-issued unchanged. An answered entry cannot be
   answered again: a reversal is a new entry that supersedes it.
4. **Writes refuse a non-canonical file.** The helper never guesses where a row
   goes in a register with 18 tables. It says what is not canonical and points
   at `migrate`; until then the agent appends by hand in the file's shape, as
   the contract always said.
5. **`migrate` converts structure, never substance, and proves it.**
   - Register: every row from every table and every stranded row group goes
     into the one canonical table, columns mapped by header, unmapped columns
     kept in Source with their header as a label. Rows already in the
     canonical seven-column shape are recognised as such. A status cell's
     leading vocabulary term stays the status; the rest moves to a status
     line. Canonical status lines found anywhere move under `## Status lines`.
     Everything else is kept verbatim in an "Earlier notes" section above the
     table, headings flattened, each moved table replaced by a line naming its
     columns and rows.
   - Log: `## <date>: D<n>, ...` headings become `## D<n> · <date> · ...`.
     Entries without a number are events, and stay as they are.
   - State: a history table becomes list lines, and the section moves to the
     end of the file.
   - **The material check gates the write**: every word of the old file must
     occur at least as often in the new one, every register row must survive,
     and every decision reference must survive. If any fails, nothing is
     written.
   - **What needs judgement is reported, not done**: statuses outside the
     vocabulary, notes that read as a status change, assumptions defined only
     in a note, rows mapped by position, decisions that do not record an
     actor-set change. Migration never changes a status, a decision or a date.
   - A dry run unless `--write`. Outside a clean git work tree it leaves a
     `*.pre-migration-<date>.md` backup. `/restack-journey migrate` stops on a
     brief before writing: restructuring the journey files is the architect's
     call.
6. **trace reads a migrated register correctly** (trace 1.0.2): notes in an
   "Earlier notes" section count as later than the rows they mention, so its
   status-drift heuristic keeps working after migration.

## Consequences

### Positive

- The canonical shapes hold because one script writes them, not because
  every agent remembers them over a long session.
- Interrupted briefs are recorded, numbered, and re-issued rather than lost or
  answered on inference.
- A legacy project can be brought into shape in one reviewed step. On the
  reference engagement's journey files (read-only copy): 123 rows from 18
  tables and 12 stray groups, 18 headings, 151 history rows, every word kept;
  trace's structural `REG` items disappeared and the content items remained.

### Negative

- The canonical check is strict: a register with anything but status lines
  after its table is refused. A project that annotates its register there has
  to move the annotation or migrate.
- The word check proves nothing was lost, not that nothing was distorted: a
  row mapped by position can put the right words in the wrong column. The
  report names every such row, and the architect checks them.
- A migrated register carries its history as an "Earlier notes" section that
  can be long. It is honest, and it is not tidy.

### Neutral

- Sub-briefs (`D<n>.1`) are recorded in the parent's entry; the helper does
  not number them.
- Restyling ADRs and descriptive documents (ROADMAP item 9) stays open. There
  "no word lost" is the wrong guard, because restyling means rewording.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| `scripts/preamble/decision-brief.md` | numbering from the log by hand | updated: number from `decision open` |
| `scripts/preamble/journey-state.md` | "append in its shape" as the only path for old files | updated: refuse, append by hand, offer migrate |
| `templates/decisions-log-template.md` | only answered briefs are logged | updated: open entries, events allowed |
| `templates/assumptions-register-template.md`, `journey-state-template.md` | scripts as a hypothetical | updated: name the helper |
| `/restack-journey` | no migration command | `migrate` added |
| CLAUDE.md, QUICKREF.md, ROADMAP.md | the helper as future work | updated |

## Alternatives considered

### Append canonically to legacy files

- **Pros:** the helper always works.
- **Cons:** every legacy file becomes mixed-shape, and the next agent faces
  two conventions in one file.
- **Why rejected:** refusing is honest about the file, and migration fixes it
  once.

### A new utility skill owning the helper

- **Pros:** a direct command for the architect, like `/restack-trace`.
- **Cons:** one more skill, and the contract would live in one skill while its
  writer lived in another.
- **Why rejected:** `/restack-journey` owns the contract, and the preamble
  already reaches every skill that writes.

### Log only answered briefs

- **Pros:** no change to the log's contract.
- **Cons:** the number of an unanswered brief is recorded nowhere, and can be
  reused without anyone noticing.
- **Why rejected:** field feedback item 14 needs the open brief on disk.

## References

- [ADR-016](ADR-016-update-awareness.md): an optional cross-skill script dependency
- [ADR-021](ADR-021-trace-checks-as-a-worklist.md): trace, the reading half
- `skills/restack-journey/scripts/journey.py`, `scripts/preamble/journey-files.md`, `tests/test_journey.py`
