### Low-level design structure

An LLD covers one component — one actor, or a tight cluster of them. Its
audience is whoever implements or changes it, and its job is to answer the
questions that would otherwise be settled by guessing during implementation.

```markdown
# Low-Level Design — <component>

**Status:** Draft | Agreed | Superseded
**Date:**    **Authors:**
**Part of:** [link to the HLD]
**Actor role:** [what this actor does on which paths]

## 1. Responsibility
## 2. Interfaces — intentions in and out
## 3. Internal structure
## 4. State and data
## 5. Failure behaviour
## 6. Concurrency
## 7. Configuration and operational levers
## 8. Testing approach
## 9. Open questions
```

#### 1. Responsibility

One paragraph, and one sentence of it should be what this component is *not*
responsible for. Scope creep in a component starts as an unwritten boundary.

#### 2. Interfaces — intentions in and out

For each intention received: who sends it, its shape, its expected rate, and
what this component does with it. For each propagated: to whom, under what
conditions, and whether it is synchronous.

Include the **side effects** — audit writes, cache invalidations, notifications.
These are the outputs that get forgotten and then break someone downstream who
did not know they existed.

#### 3. Internal structure

Modules and their relationships, at the level someone needs to find their way
around. Not a class listing — the code is better at that and stays current.

#### 4. State and data

What this component holds, its lifetime, and what resets it. Schema or data
shapes with their ownership. If it holds state affecting the next call —
caches, idempotency records, in-flight buffers, circuit-breaker state — say so
explicitly. That is where the surprising behaviour lives.

#### 5. Failure behaviour

The section that most repays being written before the code, because writing it
afterwards means documenting whatever happened to be built.

For each dependency: timeout, retry policy, and behaviour when it is **slow**
rather than down. Slow is the case nobody designs for and the one that takes
systems out.

Then state, explicitly:

- Does this component fail **loudly, silently, partially, or by hanging**?
- What does its caller observe in each case?
- Which operations are idempotent, and by what mechanism?
- What is the degraded mode, if there is one?

#### 6. Concurrency

How many instances can run at once, and what breaks if the answer is more than
one? Locks, leader election, ordering assumptions, singleton schedulers. An
undocumented single-instance assumption is discovered during the first scaling
attempt, usually in production.

#### 7. Configuration and operational levers

Every setting that changes behaviour, with its default and its safe range.
Specifically: what can an operator change at 3am to reduce blast radius —
a timeout, a feature flag, a rate limit, a circuit breaker? A component with no
operational levers gives its operators nothing to do but restart it.

#### 8. Testing approach

What is unit-tested, what needs integration, and — most usefully — **how the
failure modes in section 5 are tested**. Failure paths that are documented but
untested are aspirations. If a residual lives in this component, say how you
would demonstrate it works, because an untested residual is a belief and the
matrix is counting on it.

#### 9. Open questions

With owners. Register them in `docs/journey/assumptions-register.md` too.

---

### When an LLD is worth writing

Not for every component. Write one where the component is complex enough that
implementers would otherwise guess, where it is a residual whose failure
behaviour is the whole point, where several people will work on it in parallel,
or where it is a one-way door — a contract or data model others will depend on.

Skip it for a component whose behaviour is obvious from its interface. An LLD
written for completeness rather than need is documentation debt: it will drift,
and a drifted LLD is worse than none because people trust it.
