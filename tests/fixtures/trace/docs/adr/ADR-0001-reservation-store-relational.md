# ADR-0001: Reservations in a relational table, updated in place

**Status:** Superseded by ADR-0003

**Date:** 2026-03-01

**Deciders:** Lockerline architect

## Context

A courier reserves a locker compartment before arriving. Reservations change
state three times: held, filled, collected.

## Decision

We will keep one row per reservation and update its state in place.

## Consequences

### Negative
- The history of a reservation is lost when it changes state.
