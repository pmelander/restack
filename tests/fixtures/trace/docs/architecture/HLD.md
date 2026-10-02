# Lockerline: high-level design

**Version:** 1.2

## 1. Purpose

Couriers reserve a compartment, fill it, and the recipient collects with a code.

## 2. Actors

Courier app, reservation service, locker controller, notification sender.

## 3. Reservation store

Reservations are stored as described in ADR-0001.
ADR-0001 (superseded by ADR-0003) kept one row per reservation.

### 3.1 Expiry (amended 2026-04-02)

Held reservations expire 30 minutes after they were made.

## 4. Impact

Total system impact is 6, from `matrix-2026-04-01-iter2.md`.
