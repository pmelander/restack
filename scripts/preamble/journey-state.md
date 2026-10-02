## Journey State (read at start, write at end)

Architectural journeys span weeks, survive breaks, change hands, and need an
audit trail. Conversation memory does not carry that. **File state is the
single source of truth for where a journey is** — this section is the contract,
and every command in this skill honours it.

### Read first

Before doing anything else, read whichever of these exist:

| File | Carries |
|---|---|
| `docs/journey/journey-state.md` | terrain, aspiration, current phase, artifacts, gaps |
| `docs/journey/stressor-iteration-history.md` | per-iteration impact matrices and residuals |
| `docs/journey/decisions-log.md` | every gate passed, with rationale |
| `docs/journey/assumptions-register.md` | unverified beliefs and their validation status |

If `journey-state.md` is absent and the work is clearly mid-journey, say so and
reconstruct it retrospectively from what exists in the repo before proceeding.
Do not start a fresh journey over the top of an in-flight one.

**Two fields bound every probe.** Read `Implementation status:` and `Design
boundary:` from `journey-state.md` before investigating anything. In a
design-only engagement, do not search for repositories or work items. Past the
design boundary, record what the neighbour's system visibly does and turn
every question about its internals into a handoff ask. Do not investigate
there. If either field is missing, ask before probing (a one-line confirm is
enough) and write the answer in.

### Write last

Update state **at the end of every command**, not only `/restack-journey` commands.
A command that produced an artifact, passed a gate, identified a residual, or
registered an assumption and did not write it down has lost that work.

Writes are append-only in spirit: never delete iteration history, never
overwrite a prior decision — supersede it with a new dated entry that references
the one it replaces. The trail is the point, especially in minefield terrain.

### Canonical shapes (so any agent can append in one line)

- **Assumptions register:** one table, for the whole journey:
  `ID | Assumption | Source | Validates it | Depends on it | Status | Status date`.
  Status is exactly one of `Open`, `Partly resolved`, `Resolved`,
  `Resolved by design (test pending)`, `Withdrawn`, `Superseded by D<n>`. A
  status change appends `- A-<n> · <status> · <date> · <why>` under
  `## Status lines` and updates the row's two status cells. Never start a
  second table, and never add an "Update" heading.
- **Decisions log:** one `## D<n> · <date> · <question>` entry per answered
  brief, appended at the end. It records whether the decision changed the actor
  set, because that makes earlier matrices `scored pre-D<n>`.
- **Journey history** in `journey-state.md`: an append-only list at the **end**
  of the file, one line per entry: `- <date> · <command> · <outcome> · <D<n>>`.

`/restack-journey` carries the full templates. When an existing file uses
another shape, append in its shape and register the drift once. Do not
restructure someone's register in the middle of a journey without asking.

### Timestamps

Use absolute dates (`2026-09-05`), never relative ones. "Last week" is unusable
to the architect who picks this up in November.
