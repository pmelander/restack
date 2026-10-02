# ADR-0002: Held reservations expire after 30 minutes

**Status:** Proposed

**Date:** 2026-03-10

**Deciders:** Lockerline architect

## Context

A held compartment that is never filled blocks the locker for everyone else.

## Decision

We will expire a held reservation 30 minutes after it was made, by polling the
reservation table every minute. The grace period for late couriers is TBD.

## Consequences

### Positive
- Abandoned holds free themselves.

## Amendment (2026-04-02)

Expiry is now driven by the event stream (ADR-0003), not by polling.
