# Decisions Log

Every gate and every brief, numbered journey-wide. A brief takes its number
when it is issued: `journey.py decision open` writes its entry with
`**Answer:** (open)`, and `journey.py decision answer` fills it in when the
architect answers. An entry still `(open)` is a brief that was interrupted: it
is re-issued unchanged under the same number, never answered on the
architect's behalf. Numbers are never reused.

Append-only. Each entry is a level-2 heading, newest at the end. Once
answered, an entry is not edited: a decision that reverses it is a new entry
that names the one it supersedes. Entries without a `D<n>` (events that were
not briefs) are allowed and are not numbered.

## D1 · YYYY-MM-DD · [one-line question]

- **Gate:** [terrain | confidence | iterate | approach | brief]
- **Answer:** [the option chosen, in the architect's words]
- **Rationale:** [one or two lines]
- **Changes the actor set:** [no | yes: added/removed <actor>. Matrices scored before this are `scored pre-D1`]
- **Supersedes:** [— | D<n>]
