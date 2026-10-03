# ADR-0004: Locker telemetry and the stuck-door alert

**Status:** Proposed

**Date:** 2026-04-05

**Deciders:** Lockerline architect

## Context

A door that reports closed while a courier is still holding it open leaves a
compartment marked filled and empty.

## Decision

We will page on LOCKER-STUCK: a door open for more than five minutes during a
fill.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| [HLD / LLD / deployment guide / runbook] | [the section and the claim] | [updated / bannered / ticketed] |
