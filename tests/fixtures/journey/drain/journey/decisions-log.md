# Decisions Log

Every gate and every brief, numbered journey-wide.

## D1 · 2026-03-01 · Terrain

- **Gate:** terrain
- **Answer:** Greenfield
- **Rationale:** no locker system exists yet.
- **Changes the actor set:** no
- **Assumptions:** none
- **Supersedes:** —

## D2 · 2026-03-15 · One event store per depot, or one for all?

- **Gate:** approach
- **Answer:** one per depot
- **Rationale:** keeps writes local to the depot.
- **Changes the actor set:** yes: added the depot event store. Matrices scored before this are `scored pre-D2`
- **Assumptions:** raises A-8
- **Supersedes:** —

## D3 · 2026-03-30 · Iterate after iteration 1

- **Gate:** iterate
- **Answer:** iterate
- **Rationale:** the reservation logs show couriers reserve at the depot door.
- **Changes the actor set:** no
- **Assumptions:** settles A-3
- **Supersedes:** —

## D4 · 2026-04-08 · Keep one event store per depot?

- **Gate:** approach
- **Answer:** one store for all depots
- **Rationale:** couriers move between depots in a shift.
- **Changes the actor set:** yes: removed the depot event store. Matrices scored before this are `scored pre-D4`
- **Assumptions:** none
- **Supersedes:** D2

## D5 · 2026-04-15 · Iterate after iteration 2

- **Gate:** iterate
- **Answer:** (open)
- **Rationale:** —
- **Changes the actor set:** —
- **Supersedes:** —
