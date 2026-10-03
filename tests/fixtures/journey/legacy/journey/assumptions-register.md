# Assumptions Register

Beliefs the Lockerline design relies on. Created 2026-03-10.

| ID | Assumption the design relies on | Current source | Evidence against / for | Validates it | Spec that depends on it | Status |
|---|---|---|---|---|---|---|
| A-01 | Couriers arrive within 30 minutes of reserving | depot manager | **Against:** two depots report 45 minutes | a week of logs | ADR-0002 | **Open: highest leverage** |
| A-02 | Controllers report door state within a second | vendor sheet | — | a bench test | ADR-0004 | Open |

### Updates 2026-03-25 (bench test)
- **A-02: FALSIFIED (High).** The bench test measured 4 seconds on firmware 2.1.
- **A-03 (new):** recipients have a phone that receives SMS. Owner: architect.

### Update 2026-04-02 (iteration 2 walks)

| ID | Unknown | Settles it | Status |
|---|---|---|---|
| A-04 | Whether the depot Wi-Fi reaches the back row of lockers | a site survey | Open |
- A-04 · Partly resolved · 2026-04-03 · survey covered two of three depots
| A-05 | Whether a parcel can be reassigned while held | the reservation API owner | Recorded |
| A-06 | The SMS gateway sends within a minute | gateway SLA | depot ops | Open |
