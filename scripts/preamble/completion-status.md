## Completion Status Protocol

Close every command with exactly one status line:

- **DONE** — completed, with the artifact path or matrix inline as evidence.
- **DONE_WITH_CONCERNS** — completed; list each concern as a one-line
  `CONCERN:` entry and register it in `docs/journey/assumptions-register.md`.
- **BLOCKED** — cannot proceed. State the blocker, what you attempted, and the
  one thing that would unblock it.
- **NEEDS_DISCOVERY** — the analysis cannot be trusted because the system is
  not sufficiently known. Name the specific unknown (which actor, which path,
  which integration) and route to the `/restack-discover` command that closes it.

`NEEDS_DISCOVERY` is not a failure. Producing a confident-looking impact matrix
over a path map you do not believe is the failure.

Escalate after three failed attempts at the same analysis, rather than
producing a fourth variation of it.
