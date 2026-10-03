# Assumptions Register

Beliefs the Lockerline design relies on that have not been verified. A-1 to
A-3 and A-7 are asks of people outside the design; A-5 reads like one but has
not been routed; A-6 is settled inside it.

| ID | Assumption | Source | Validates it | Depends on it | Status | Status date |
|---|---|---|---|---|---|---|
| A-1 | Depots open at 06:00 on weekdays | courier interviews | Ask Depot operations: the opening-hours list per depot | ADR-0005 | Open | 2026-03-10 |
| A-2 | Locker controllers report door state within a second | vendor sheet | Ask Locker vendor: the firmware's reporting interval | ADR-0004, S-12 | Open | 2026-03-20 |
| A-3 | A locker bank survives a 30-second power cut | vendor sheet | Ask Locker vendor team: the UPS hold-up time | R2 | Partly resolved | 2026-04-10 |
| A-4 | Couriers carry a phone with mobile data | depot manager | Ask Depot operations: the device policy | ADR-0002 | Resolved | 2026-04-01 |
| A-5 | Parcel labels carry the locker bank ID | label sample | confirm with the courier partner's integration owner | ADR-0006 | Open | 2026-04-05 |
| A-6 | Reservation lookups stay under 50 ms | inference | a load test against the staging API | ADR-0003 | Open | 2026-04-06 |
| A-7 | Door unlock codes are single use | design | Ask Security: a pen test of the unlock endpoint | R1 | Resolved by design (test pending) | 2026-04-08 |

## Status lines

- A-1 · Open · 2026-03-10 · registered
- A-2 · Open · 2026-03-20 · registered
- A-2 · Open · 2026-04-02 · asked Locker vendor
- A-3 · Open · 2026-03-22 · registered
- A-3 · Open · 2026-03-25 · asked Locker vendor team
- A-3 · Partly resolved · 2026-04-10 · vendor confirmed a UPS, not its hold-up time
- A-3 · Partly resolved · 2026-04-15 · asked Locker vendor team
- A-4 · Open · 2026-03-12 · registered
- A-4 · Resolved · 2026-04-01 · depot operations sent the device policy
- A-5 · Open · 2026-04-05 · registered
- A-6 · Open · 2026-04-06 · registered
- A-7 · Open · 2026-04-07 · registered
- A-7 · Resolved by design (test pending) · 2026-04-08 · single-use codes in the design
