# ADR-0003: Push Locker Status as Events

**Status:** Accepted

**Date:** 2026-04-01

**Deciders:** Lockerline platform team

**Reversibility:** Costly to reverse

**Review date:** 2026-10-01

## Context

Polling (ADR-0002) read stale status for up to a minute.

## Decision

We will publish a status event from each locker on change.

## Consequences

### Positive

- Status is current within seconds.

### Negative

- Every locker firmware version must emit the event.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| HLD | the polling loop in §3 | updated |

## Alternatives considered

### Poll faster

Rejected: load on the controller.

## Editorial notes

- 2026-09-01 · restyled, wording only · reshaped: metadata as fields · dropped: nothing · checked by restyle.py 1.0.0
