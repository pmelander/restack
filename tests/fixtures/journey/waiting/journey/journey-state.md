# Journey State

**Last Updated:** 2026-04-22
**Implementation status:** Design-only. Nothing implemented (architect, 2026-04-02: "paper only").
**Design boundary:** the reservation service and the locker controller, ending at the courier app's API (D2).
**Terrain Type:** Greenfield
**Current Phase (2026-04-22):** Documentation/Review, waiting on the asks.

---

## Aspiration

Couriers can drop a parcel at any locker bank, even when the bank is offline.

---

## Current Position

### 2026-04-22 (`/restack-journey where`), supersedes the 2026-04-20 position below

- **Where we are:** SYS-1 is resolved (D4); SYS-2 and iteration 3 rest on the asks.
- **Next move:** waiting on depot operations and the locker vendor; when an answer arrives, `/restack-journey where`. Not sent yet: A-3 (locker vendor).

### 2026-04-20 (superseded)

- **Next move:** `/restack-design-review complete`

---

## Journey History

- 2026-03-01 · `/restack-journey start` · terrain Greenfield, route discover-stress-decide · D1
- 2026-03-20 · `/restack-journey iterate` · iterate: two new actors · D2
- 2026-04-20 · `/restack-journey where` · parked at D3; next: the complete review while the asks are out
- 2026-04-20 · `/restack-design-review complete` · not ready to build: SYS-1 and SYS-2
- 2026-04-21 · `/restack-adr update 0007` · SYS-1 resolved in the documents · D4
- 2026-04-22 · `/restack-journey where` · waiting on depot operations and the locker vendor
