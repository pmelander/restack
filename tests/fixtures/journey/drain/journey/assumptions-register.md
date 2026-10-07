# Assumptions Register

Beliefs the Lockerline design relies on that have not been verified. Every
kind is here: beliefs, an ask, a design question, a build test and a shadow
observation. A-3 was settled by D3 and never closed; A-4 waited for an
iteration that has run; A-7 and A-8 rest on what was superseded.

| ID | Assumption | Source | Validates it | Depends on it | Status | Status date |
|---|---|---|---|---|---|---|
| A-1 | Locker controllers accept one command at a time | vendor sheet | a bench test of two concurrent commands | ADR-0002, 0004 | Open | 2026-03-10 |
| A-2 | Door state is reported within a second | vendor sheet | Ask Locker vendor: the firmware's reporting interval | ADR-0004 | Open | 2026-04-05 |
| A-3 | Couriers reserve before they leave the depot | depot manager | a week of reservation logs | courier app | Open | 2026-03-20 |
| A-4 | Lockers stay shut after a power cut until a courier unlocks them | design workshop | Decide: decide in iteration 2 residues | R-2 | Open | 2026-03-25 |
| A-5 | Door-state latency stays under a second under load | inference | Test: measure on the bench with forty doors | ADR-0002 | Resolved by design (test pending) | 2026-04-12 |
| A-6 | Fewer than one reservation in fifty is abandoned | inference | Observe: count abandoned reservations during shadow | — | Open | 2026-04-18 |
| A-7 | The depot cache holds a full day of reservations | design | a sizing check against March volumes | ADR-0003 | Partly resolved | 2026-04-01 |
| A-8 | One event store per depot keeps writes local | design | D4 decides it | D2 | Open | 2026-04-02 |
| A-9 | The depot cache survives a restart | design | a restart test | ADR-0003 | Resolved | 2026-04-03 |
| A-10 | Couriers share lockers across depots | sales | the sales forecast | D2 | Withdrawn | 2026-04-04 |

## Status lines

- A-1 · Open · 2026-03-10 · registered
- A-3 · Open · 2026-03-20 · registered
- A-4 · Open · 2026-03-25 · registered
- A-7 · Open · 2026-03-28 · registered
- A-7 · Partly resolved · 2026-04-01 · March volumes fit; April unknown
- A-8 · Open · 2026-04-02 · registered
- A-9 · Open · 2026-04-02 · registered
- A-9 · Resolved · 2026-04-03 · restart test passed on the bench
- A-10 · Open · 2026-04-02 · registered
- A-10 · Withdrawn · 2026-04-04 · sales dropped cross-depot sharing
- A-2 · Open · 2026-04-05 · registered
- A-2 · Open · 2026-04-06 · asked Locker vendor
- A-5 · Open · 2026-04-10 · registered
- A-5 · Resolved by design (test pending) · 2026-04-12 · ADR-0002 sizes the controller queue
- A-6 · Open · 2026-04-18 · registered
