### Architecture dimension

Review the shape of the system, not the code. You are looking for structure
that will resist the changes the system is going to be asked to absorb.

**Boundaries.** Do the component boundaries follow the paths intentions
actually take, or an org chart? A boundary crossed by every significant path is
a boundary in the wrong place, and it shows up later as "every change touches
three services".

**Coupling.** For each pair that talks: is the dependency declared, versioned
and owned? Undeclared coupling — a shared database table, a filename convention,
an assumption about ordering — is where change propagates unexpectedly. Ask what
happens to the caller when the callee is slow rather than down; the answer is
usually worse.

**Cohesion.** Does each actor have one reason to change? An actor that changes
for three unrelated reasons will be a bottleneck for three teams.

**Statefulness.** Where does state live, and is that deliberate? State smeared
across several actors with no owner is the most expensive structural defect to
correct later.

**Failure containment.** Draw the blast radius of each actor failing. If any
single actor takes the whole system down, that is either an accepted design
choice with an ADR behind it, or it is the top finding.

**Evolvability.** Name the change this system is most likely to be asked for in
the next year. Trace what it would touch. If the answer is "most things", the
structure is wrong for its expected future regardless of how clean it looks now.

#### Anti-patterns worth naming explicitly

- **Distributed monolith** — services that must be deployed together. All the
  operational cost of distribution, none of the independence.
- **Shared mutable database** — two actors writing the same table are one actor
  with extra steps and no contract.
- **Chatty synchronous chains** — each hop multiplies latency and failure
  probability. Count the hops on the critical path; four or more synchronous
  hops is a finding.
- **God actor** — everything routes through one component. Look for it in the
  path map: the actor appearing on every path.
- **Missing async boundary** — a request path doing work the user is not
  waiting for.

Name the anti-pattern, then say what it will cost *here*, concretely. The label
alone is not a finding.

---

### Data dimension

**Ownership.** Every piece of data has exactly one owning actor. Where two
actors both write, name it — that is a consistency defect waiting for
concurrent load, not a style preference.

**Consistency requirements, stated.** Ask what guarantee each path actually
needs: strong, read-your-writes, eventual with a bounded window, or
best-effort. Teams routinely build for strong consistency they do not need, and
build eventual consistency where they needed strong. Both are expensive.

**Dual writes.** Any place the design writes to two stores without a
transaction or an outbox is a partial-failure defect. This is one of the most
common serious findings and it is almost always unintentional.

**Schema evolution.** How does a field get added, and what happens to consumers
that do not know about it? If the answer is a coordinated deploy, that is a
one-way door being built accidentally.

**Retention and erasure.** Where does data go to die? A system with no deletion
path acquires a compliance problem the moment anyone asks for erasure, and
retrofitting deletion into a design that never had it is expensive.

**Recovery.** Distinguish backup from recovery. Ask specifically: has a restore
been performed, and how long did it take? An untested backup is a belief, not a
control — and the evidence rules apply here as anywhere.

**Idempotency.** For every path that can be retried, is the operation
idempotent, and by what mechanism? "It should be fine" is not a mechanism.
