# ADR-0001: Queue Locker Reservations Behind the Booking API

## Status

Accepted

## Date

2026-03-02

## Deciders

Lockerline platform team

**Technical Story:** LL-114

## Context

As you work through this decision you are building the capability to see
queues as residuals rather than as plumbing. The Booking API calls the Locker
Controller synchronously, and during the S-4 stressor (a firmware push takes
40% of lockers offline for 15 minutes) every reservation on the checkout path
times out at hop 3. Reservations must not be lost when the Locker Controller is
unavailable. See [the stressor matrix](../stressor-analysis/matrix-iteration-1.md)
and A-2.

## Decision

We will put a durable queue, `reservations.v1`, between the Booking API and the
Locker Controller. The Booking API never waits on the controller; it confirms
a reservation only after the queue has accepted it. Messages older than 72
hours are not replayed.

```yaml
queue: reservations.v1
retention_hours: 72
```

| Detail | Derived from | Overturnable |
|---|---|---|
| 72-hour retention | A-2 | yes |

## Consequences

### Positive

- The checkout path no longer depends on the Locker Controller (clears S-4 and S-7).

### Negative

- A reservation can be confirmed and then fail at the locker; the customer is
  told by SMS within 5 minutes, which D3 accepted.

## Alternatives Considered

### Retry the synchronous call

Rejected: it only moves the timeout.

### Reserve in the Booking API's own table

Rejected: two writers to locker state.

## Reflection prompts

- What would have to be true for the queue to be unnecessary?
- Which stressor did the room want to argue down?
