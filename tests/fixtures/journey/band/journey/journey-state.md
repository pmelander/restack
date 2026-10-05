# Journey State: Lockerline

**Last Updated:** 2026-04-20 16:05
**Terrain Type:** Brownfield
**Current Phase:** Stressor Analysis
**Implementation status:** Design-only — nothing implemented
**Design boundary:** the reservation service and the locker controller; the courier app is a handoff ask

---

## Aspiration

Couriers can drop a parcel at any locker bank, even when the bank is offline.

---

## Current Position

**Where we are:** `/restack-stressor analyze`, iteration 2

**What we've completed:**
- ✅ `/restack-discover paths` — three paths through the depot
- ✅ `/restack-stressor walk courier-fill` — two new actors

**What's next:** `/restack-stressor analyze` — score iteration 2 against the new actors before the iterate gate

**Confidence level:** Medium — the controller's offline behaviour is still vendor-reported

---

## Journey History

- 2026-03-01 · `/restack-journey start` · terrain Brownfield, route discover-stress-decide · D1
- 2026-03-20 · `/restack-journey iterate` · iterate: two new actors · D2
- 2026-04-18 · `/restack-journey iterate` · gate opened: offline unlock · D3
