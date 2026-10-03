# ADR-0005: Couriers sign in with a per-shift code

**Status:** Proposed

**Date:** 2026-04-06

**Deciders:** Lockerline architect

## Context

Couriers share handsets. A long-lived login on a shared handset is a login
anyone on the next shift can use.

## Decision

We will issue a code per shift, valid for twelve hours. Revisit at D9.
