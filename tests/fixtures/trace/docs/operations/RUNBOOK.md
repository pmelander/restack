# Lockerline: operations runbook

## 1. Alerts

| Alert | Meaning | First checks |
|---|---|---|
| **LOCKER-STUCK: door open during a fill** | a door open for more than five minutes | ask the courier |
| **LOCKER-GHOST: compartment filled but empty** | the controller and the stream disagree | replay the stream |

## 2. Restoring a reservation by hand

Edit the reservation row and set its state.
