# Residuals, iteration 1 (Lockerline)

| Rank | Residual | Cells cleared |
|---|---|---|
| 1 | R1 Event-sourced reservations | 3 |
| 2 | R2 Depot battery backup | 3 |

## R1: Event-sourced reservations

The reservation service records events instead of updating rows.

**Clears 3 cells:**
- S-1: RS.
- S-2: RS.
- **Outside the cluster:** S-4 (RS; the controller reboot replays from the stream)

**Creates:** the projection rebuilder.

## R2: Depot battery backup

**Clears 3 cells:**
- S-5: LC, NS.
- S-3: CA.
- S-1: RS.

**Leaves:** S-2 (firmware is not a power problem).
