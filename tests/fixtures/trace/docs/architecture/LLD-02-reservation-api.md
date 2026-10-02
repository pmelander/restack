# LLD-02: Reservation API

> **AMENDED 2026-04-03: read this before the body.** Expiry moved from
> polling to the event stream (ADR-0003). Changes are marked inline.

**Status:** Draft

## 1. Endpoints

`POST /reservations` holds a compartment. `DELETE /reservations/{id}` releases it.

## 2. Expiry

~~A worker polls for expired holds every minute.~~ An expiry event is scheduled
when the hold is recorded. The worker still polls the dead-letter queue.

## Amendment (2026-04-03)

Expiry is event-driven; see the banner.

## Amendment (2026-04-20)

Releases are idempotent: a second `DELETE` returns 204.
