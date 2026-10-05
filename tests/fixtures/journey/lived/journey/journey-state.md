# Journey State

**Last Updated:** 2026-04-20
**Implementation status:** Design-only. Nothing implemented (architect, 2026-04-02: "paper only").
**Design boundary:** the reservation service and the locker controller, ending at the courier app's API (D2). The courier app's internals are handoff asks.
**Terrain Type:** Greenfield service, but its unlock half is brownfield: it runs inside the existing depot controller chain, which has not been discovered. Reclassification pending D3.
**Current Phase (2026-04-20, end of session):** Documentation/Review. The review is worked through:
- **Resolved in the documents:** SYS-1 and SYS-2.
- **Next ReStack moves when work resumes:** SYS-3 (`/restack-adr update 0007`), then iteration 3.
**Previous phase line (2026-04-18, `/restack-journey where`):** Stressor loop, iteration 2, parked at D3's trigger.
**Previous phase line (2026-03-20, after D2):** Discovery. Next: `/restack-stressor walk courier-fill`.

---

## Aspiration

Couriers can drop a parcel at any locker bank, even when the bank is offline.

---

## Current Position

### 2026-04-20 (`/restack-journey where`), supersedes the 2026-03-20 position below

- **Where we are:** iteration 2 scored; the residual ADRs are written; the design loop is parked at D3.
- **External asks: none sent** (architect, 2026-04-20). Depot operations and the locker vendor hold the open conditions.
- **Next move:** `/restack-design-review complete`, while the asks are out. Rejected for now: `/restack-journey review`.

### 2026-03-20 (superseded)

- **Where we are:** discovery complete for two paths.
- **What's next:** `/restack-stressor walk courier-fill`
- **Confidence level:** Low — the controller is undiscovered

---

## Journey History

- 2026-03-01 · `/restack-journey start` · terrain Greenfield, route discover-stress-decide · D1
- 2026-03-20 · `/restack-journey iterate` · iterate: two new actors · D2
- 2026-04-18 · `/restack-journey iterate` · gate opened: offline unlock · D3
