### Fitness functions

A fitness function is an automated check that an architectural characteristic
still holds. It converts a principle everyone agreed once into something that
fails a build when it stops being true.

#### Fitness functions are automated residual validation

This is the connection worth making, and it is what fitness functions are best
at in this toolkit.

The stressor matrix asserts that a residual reduces impact. That assertion is a
prediction until something checks it — and it decays silently, because
residuals erode without anyone deciding to remove them. A timeout gets raised
during an incident and never lowered. A circuit breaker's threshold drifts. A
bulkhead is bypassed by a "temporary" direct call that stays.

**A fitness function is how a residual stays true.** For each residual in the
design, ask: what automated check would fail if this stopped working?

| Residual | Fitness function |
|---|---|
| Async queue between two actors | no synchronous call path exists from A to B |
| Circuit breaker | breaker trips in the chaos test, and closes again afterwards |
| Idempotency on an intention | replaying a message produces no second effect |
| Bulkhead / tenant isolation | no shared connection pool across tenants |
| Timeout on every dependency | no HTTP client constructed without an explicit timeout |
| Outbox for dual writes | no code path writes both stores directly |
| Read replica for load | primary read QPS stays below threshold |

A residual with no fitness function is a residual you are trusting. Say which
ones those are — the matrix is counting on all of them equally.

#### Designing one

**Start from the characteristic, then find the measurement.** Reversing this —
starting from what is easy to measure — produces checks that pass while the
thing you cared about degrades.

Each needs:

- **The characteristic**, in one sentence, and why it matters here
- **The measurement**, precise enough to implement
- **The threshold**, with the reasoning for that number
- **Where it runs** — build, CI, deploy gate, production monitor
- **What happens on failure** — block, warn, or open a ticket
- **An owner**

**The threshold is the hard part.** A number with no reasoning gets raised the
first time it is inconvenient, which is exactly when it was doing its job.
Record why: "200ms p95 because the checkout path budget is 800ms and this is
four hops."

#### Categories

**Structural** — dependency direction, layering, no circular dependencies, no
forbidden imports, module boundaries. Cheap to automate and among the most
valuable, because structural erosion is invisible until it is expensive.

**Operational** — latency percentiles, error rates, throughput, resource
headroom. Usually production monitors rather than build checks.

**Security** — no secrets in source, dependencies scanned, security headers
present, no wildcard IAM. These are the ones most easily automated and most
often left manual.

**Data** — schema compatibility, migration reversibility, retention enforced,
no unindexed full scans on a hot path.

**Process** — every service has an owner, every alert has a runbook entry,
every ADR past its review date is flagged. Unglamorous and they prevent a lot.

#### Rules that keep them useful

**Automate or delete.** A manual fitness function is a checklist item and will
be skipped under pressure. If it cannot be automated now, mark it explicitly as
manual with a date to automate — an honest gap, not a pretend control.

**Fail loudly, in the right place.** A check nobody sees fail is not a control.
Structural checks belong in the build where they block; operational ones belong
in monitoring where they page.

**Few and meaningful beats many and ignored.** Twenty functions where three
fail intermittently and get muted teaches the team that failures are noise —
and then the real one is muted too. Ten that everyone trusts is a far stronger
position.

**Every failure is investigated, never bypassed.** The first bypass sets the
precedent, and after it the function is decoration. If a function is wrong,
change it deliberately with the reasoning recorded — that is a decision, and
bypassing is not.

**Review the thresholds periodically.** A threshold nobody has revisited since
the system was a tenth of its size is measuring history.
