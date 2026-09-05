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

### Write last

Update state **at the end of every command**, not only `/restack-journey` commands.
A command that produced an artifact, passed a gate, identified a residual, or
registered an assumption and did not write it down has lost that work.

Writes are append-only in spirit: never delete iteration history, never
overwrite a prior decision — supersede it with a new dated entry that references
the one it replaces. The trail is the point, especially in minefield terrain.

### Timestamps

Use absolute dates (`2026-09-05`), never relative ones. "Last week" is unusable
to the architect who picks this up in November.
