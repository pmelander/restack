### Cloud primitives are residuals

This is the section that connects cloud design to the rest of the toolkit, and
it is the reframe worth internalising.

Most of what a cloud architect reaches for — a queue, a read replica, a
multi-AZ deployment, an auto-scaling group, a circuit breaker — is a
**residual**: a discrete change to actors, intentions or paths, introduced
because something could go wrong, and persisting afterwards. The cloud does not
change the theory; it changes how cheap the residuals are to introduce.

That cheapness is the trap. When a residual costs a checkbox, teams add them
without diagnosing the mechanism, and end up with an expensive architecture
that is defended against the failures the vendor's reference diagram assumed
rather than the ones this system actually has.

#### Map the primitive to the mechanism

| Cloud primitive | Residual shape | Mechanism it addresses |
|---|---|---|
| Managed queue (SQS, Service Bus, Pub/Sub) | queue / buffer actor | temporal coupling to a downstream actor |
| Multi-AZ deployment | bulkhead / partition | correlated failure of one facility |
| Multi-region | bulkhead at a larger radius | correlated failure of one region |
| Auto-scaling group | elastic capacity | demand exceeding fixed provisioning |
| Read replica | cache / alternate read source | single read source as bottleneck or SPOF |
| CDN | cache at the edge | origin load, latency, regional demand spikes |
| Circuit breaker (service mesh, SDK) | circuit breaker | unbounded failure propagation upstream |
| Managed transactional outbox / CDC | outbox | dual-write inconsistency |
| Dead-letter queue | compensating path | intentions that die silently |
| Blue/green or canary deployment | phased-rollout path | change landing everywhere at once |
| Per-tenant account or project | bulkhead | one tenant consuming shared capacity |
| Object storage lifecycle policy | retention path | unbounded data growth, erasure obligations |

Use the table to *name what you are doing*, not as a menu to pick from. The
right residual comes from the cluster of stressors hitting a vulnerable actor —
see `/restack-stressor residues`. The cloud primitive is the implementation of
that decision, not a substitute for making it.

#### The questions to ask of each cloud residual

**Which stressors does it clear?** Score it against the full matrix, not just
the stressor that prompted it. Multi-AZ clears facility loss, some maintenance
events, and part of a capacity spike — three rows, and you should know which.

**What does it create?** Every residual adds actors and paths that are
themselves walkable and stressable:

- A queue can fill, stall, reorder, or silently drop. It converts a synchronous
  failure into a backlog, which is usually better and never free.
- A read replica introduces replication lag, and therefore a read-your-writes
  problem on any path that writes then reads.
- Auto-scaling introduces a scale-up delay — during which you are under-provisioned
  — and a cost profile that can surprise you under attack.
- Multi-region introduces data residency questions and a split-brain scenario.

Name the new paths. They go into the next walk.

**Does it depend on the thing it protects against?** A residual in the same
failure domain as the actor it defends is not a residual. Failover automation
in the region you are failing away from; a dead-letter queue in the account
whose credential was compromised; a runbook stored in the system that is down.
This is the most common serious defect in cloud resilience designs and it is
invisible until the day it matters.

**Is it tested?** An untested residual is a belief, and the matrix is counting
on it. Multi-AZ that has never lost an AZ, a DR tier never exercised, a circuit
breaker never tripped in anger. Say plainly which residuals are validated and
which are assumed — that distinction belongs in the design document.

#### Lift-and-shift is a residuality question

The usual framing is "are we using cloud-native services". The more useful
framing: **which residuals does the current design have, and which of them stop
working in the new environment?**

An on-premise system frequently has residuals nobody documented — a nightly
batch that reconciles inconsistency, an operator who notices and intervenes, a
network that is reliable because it is small. Lifting the workload leaves those
behind and the vulnerability they were quietly covering comes back.

Run `/restack-discover` before a migration for exactly this reason: the
undocumented residual is the one that bites.
