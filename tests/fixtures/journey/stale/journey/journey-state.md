# Journey State

**Last Updated:** 2026-04-20
**Implementation status:** Design-only. Nothing implemented (architect, 2026-04-02: "paper only").
**Design boundary:** the reservation service and the locker controller, ending at the courier app's API (D2).
**Terrain Type:** Greenfield
**Current Phase (2026-04-20):** Documentation/Review, parked at D3's trigger.

---

## Aspiration

Couriers can drop a parcel at any locker bank, even when the bank is offline.

---

## Current Position

### 2026-04-20 (`/restack-journey where`), supersedes the 2026-03-20 position below

- **Where we are:** iteration 2 scored; the residual ADRs are written; the design loop is parked at D3.
- **Next move:** `/restack-design-review complete`, while the asks are out. Rejected for now: `/restack-journey review`.

### 2026-03-20 (superseded)

- **What's next:** `/restack-stressor walk courier-fill`

---

## Journey History

- 2026-03-01 · `/restack-journey start` · terrain Greenfield, route discover-stress-decide · D1
- 2026-04-20 · `/restack-design-review consistency` · ran before the position was written: 4 findings fixed
- 2026-04-20 · `/restack-journey where` · parked at D3; next: the complete review while the asks are out
- 2026-04-20 · `/restack-design-review complete` · not ready to build: SYS-1 and SYS-2
- 2026-04-20 · `/restack-journey asks` · asks pack for depot operations and the locker vendor
- 2026-04-21 · `/restack-adr update 0007` · SYS-1 resolved in the documents · D4
- 2026-03-20 · `/restack-journey iterate` · iterate: two new actors · D2
