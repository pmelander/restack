# ADR-0007: Recipients are notified by SMS

**Status:** Proposed

**Date:** 2026-04-08

**Deciders:** Lockerline architect

## Context

Recipients need the pickup code when the parcel is in the locker, not before.
The courier app is a D365 integration owned by another team.

## Decision

We will send the pickup code by SMS when the fill event is recorded.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| RUNBOOK | §4, resending a pickup code | ticketed LL-112 |
