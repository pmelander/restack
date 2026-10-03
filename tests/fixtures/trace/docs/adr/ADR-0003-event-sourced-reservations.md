# ADR-0003: Event-sourced reservations

**Status:** Accepted

**Date:** 2026-04-01

**Deciders:** Lockerline architect

## Context

Disputes about a parcel ("the locker was empty when I arrived") cannot be
settled from a row that was updated in place (ADR-0001). The retention
question is ADR-0009.

## Decision

We will record every reservation change as an append-only event and derive the
current state from the stream. This supersedes ADR-0001.

### Decision-point accounting

| # | Decision point in ADR-0001 | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| 1 | one row per reservation | replaced by ADR-0003 | two live holds on one compartment | a uniqueness check on the stream |

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| HLD | §3, the reservation store | updated |
| RUNBOOK | §2, restoring a reservation by hand | bannered |
| `DEPLOYMENT.md` | §1, the database migration step | updated |
| LLD-04 | the event schema | updated |
| Test strategy | replay tests | pending |
