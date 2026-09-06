### Actor investigation protocol

You are establishing what an actor *actually does*, which is reliably different
from what it is documented to do and from what the team believes it does.

#### 1. Collect the claims, and label their sources

Gather documentation, code, dashboards, and what people say — and record which
is which. Do not merge them into one description yet. Where two sources
disagree, that disagreement is a finding, not a problem to tidy away: it
usually marks where the system changed and one source did not.

#### 2. Intentions in

What signals trigger this actor? For each: who sends it, how often, and
synchronously or not? Watch for the ones nobody lists — a scheduled job, a
retry from an upstream actor, a manual replay someone runs after incidents, an
operations script.

#### 3. Intentions out

What does it propagate, and under what conditions? Separate:

- the **primary** output everyone knows about
- **conditional** outputs — only on failure, only over a threshold, only for
  certain tenants
- **side effects** — audit writes, cache invalidations, notifications,
  metrics that something else alerts on

Side effects are where the surprises are. An actor that "returns a credit
score" and also writes an audit record and pings a fraud queue has three
outputs, and two of them are invisible to the team that owns the caller.

#### 3b. Trace where each value comes from, not just that it exists

A field that *looks* like an attestation may be an input you supply.

Manifests, headers and metadata carry fields that appear to record what the
upstream actor did — a spec version, a producer id, a generated-at timestamp.
Before relying on one as evidence of the actor's behaviour, find where the value
originates. If your own side supplies it, it records **what you asked for**, not
**what they did** — and it cannot detect their drift, because it changes only
when you change.

Observed: a snapshot manifest carried `extract_spec_version`, which read exactly
like the control that would catch an upstream team silently redefining a metric.
Tracing it showed the value came from the consumer's own orchestrator config and
was used only as an idempotency key. A redefinition upstream would have left the
manifest identical in every field anything checked.

The distinction is worth stating precisely, because the fix differs:

| | |
|---|---|
| **Attestation** | the actor asserts something about its own behaviour; you can validate it and refuse |
| **Input echo** | you supplied it and it came back; it proves nothing about the actor |

An input echo is not useless — it is usually half a control, and completing it
is cheaper than building one. Say which you have.

#### 4. State

Does it hold state, and does that state change its behaviour on the next call?
Caches, idempotency tables, in-flight buffers, circuit-breaker state, feature
flags. Stateful actors behave differently on the second identical request, and
that is exactly what a stressor exploits.

Ask specifically: **what is the state's lifetime, and who can reset it?**

#### 5. Failure modes — probe, do not assume

For each, get evidence rather than a plausible story:

- What happens on unexpected or malformed input?
- What happens when a dependency is slow rather than down? Slow is worse than
  down and is the case nobody designed for.
- What is the timeout, and what does the caller see when it fires?
- Does it fail **loudly**, **silently**, **partially**, or by **hanging**?
- On retry, is the operation idempotent, and how do you know?

Silent failure and hanging are the two that make every downstream actor blind,
so establish those with evidence — a log line, a trace, a config value, or a
probe you ran. A failure mode inferred from the actor's name is not a failure
mode.

#### 6. Hidden behaviour

Look specifically for what nobody would think to tell you:

- undocumented outputs and consumers you did not know existed
- behaviour that differs by environment, tenant, region, or time of day
- manual steps a person performs that the diagram shows as automated
- a batch window that makes a "real-time" actor not real-time

#### 7. Rate every claim

Attach a confidence level to each statement, not to the actor as a whole.
"Timeout is 30s — **Confirmed**, observed in traces. Cache TTL is 24h —
**Inferred** from code, not observed." Mixed confidence within one actor is
normal and useful; a single blanket rating hides where the risk is.

#### Output

An actor profile: intentions in, intentions out (including side effects),
state and its lifetime, failure modes with evidence, hidden behaviour, and a
confidence level per claim. Register every unresolved claim in
`docs/journey/assumptions-register.md` with what would settle it.

#### Example

```
/restack-discover actor "Credit Scoring Service"

Documented:  receives application, returns credit score.

Discovered:
  - Also writes to the audit log                     Confirmed (code + log sample)
  - Caches responses 24h; repeat calls return stale  Inferred (code, not observed)
  - Silent timeout at 30s: HTTP 200, empty score     Confirmed (traces, 14 cases)
  - Notifies the fraud team downstream               Confirmed (asked ops)
                                                     - product team unaware

Implication: the empty-score-on-200 path means callers cannot distinguish
"no score" from "score of zero". Any actor downstream that treats a missing
score as a decline is silently rejecting applicants during a slow dependency.
```

That implication line is the point of the exercise. An actor profile that
stops at description has not yet earned its cost.
