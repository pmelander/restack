# Assumptions Register

Beliefs the Lockerline design relies on that have not been verified. A-1 and
A-2 are asks of people outside the design, A-3 is settled inside it, A-4 is
resolved.

| ID | Assumption | Source | Validates it | Depends on it | Status | Status date |
|---|---|---|---|---|---|---|
| A-1 | Depots open at 06:00 on weekdays | courier interviews | Ask Depot operations: the opening-hours list per depot | ADR-0005 | Open | 2026-03-10 |
| A-2 | A locker bank survives a 30-second power cut | vendor sheet | Ask Locker vendor: the UPS hold-up time | R2 | Partly resolved | 2026-04-10 |
| A-3 | Reservation lookups stay under 50 ms | inference | a load test against the staging API | ADR-0003 | Open | 2026-04-06 |
| A-4 | Couriers carry a phone with mobile data | depot manager | Ask Depot operations: the device policy | ADR-0002 | Resolved | 2026-04-01 |

## Status lines

- A-1 · Open · 2026-03-10 · registered
- A-2 · Open · 2026-03-22 · registered
- A-2 · Partly resolved · 2026-04-10 · vendor confirmed a UPS, not its hold-up time
- A-3 · Open · 2026-04-06 · registered
- A-4 · Open · 2026-03-12 · registered
- A-4 · Resolved · 2026-04-01 · depot operations sent the device policy
