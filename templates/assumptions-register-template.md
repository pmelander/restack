# Assumptions Register

One table, one schema, for the life of the journey. Never start a second table,
and never add an "Update" heading. Both make the file impossible to append to.

**Status vocabulary** (exactly these, nothing else):
`Open` · `Partly resolved` · `Resolved` · `Resolved by design (test pending)` ·
`Withdrawn` · `Superseded by D<n>`

**Rules**

- A new assumption is a new row at the **end of the table**, with the next `A-<n>`.
- A status change does **not** edit the row's history. It appends a status line
  directly under the row's table, keyed by ID:
  `- A-<n> · <new status> · <YYYY-MM-DD> · <what settled it, or what changed>`
  and updates the `Status` and `Status date` cells.
- The table is the last table in the file, and nothing but status lines follows
  it. Scripts append rows by inserting before the first status line, or at the
  end of the file when there are none.

| ID | Assumption | Source | Validates it | Depends on it | Status | Status date |
|---|---|---|---|---|---|---|
| A-1 | [the belief, stated so it can be false] | [where it came from: doc, person, inference] | [the check that would settle it] | [ADRs, residuals, matrix cells resting on it] | Open | YYYY-MM-DD |

## Status lines

- A-1 · Open · YYYY-MM-DD · registered
