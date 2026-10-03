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
  end of the file when there are none. `journey.py assume add` and
  `assume status` do both; `journey.py migrate register` converts a register
  in an older shape.
- **An ask** is an assumption only someone outside the design can settle. Its
  `Validates it` cell starts with `Ask <recipient>:`, as in
  `Ask BI: row counts per market`. A row without the prefix is settled inside
  the design. `assume add --ask <recipient>` writes the prefix, and
  `assume route A-<n> <recipient>` adds it to an existing row (ADR-026).
- **Sending an ask** appends a status line that repeats the row's status:
  `- A-<n> · Open · <YYYY-MM-DD> · asked <recipient>`. The row is not changed.
  Its `Status date` stays the date the status last changed.
  `journey.py assume asked A-<n> --to <recipient>` writes it, and
  `journey.py asks` lists the open asks by recipient.

| ID | Assumption | Source | Validates it | Depends on it | Status | Status date |
|---|---|---|---|---|---|---|
| A-1 | [the belief, stated so it can be false] | [where it came from: doc, person, inference] | [the check that would settle it] | [ADRs, residuals, matrix cells resting on it] | Open | YYYY-MM-DD |
| A-2 | [a belief about a neighbour's system] | [where it came from] | Ask [recipient]: [what they would have to tell us] | [what rests on it] | Open | YYYY-MM-DD |

## Status lines

- A-1 · Open · YYYY-MM-DD · registered
- A-2 · Open · YYYY-MM-DD · registered
- A-2 · Open · YYYY-MM-DD · asked [recipient]
