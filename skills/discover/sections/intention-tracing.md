### Intention tracing protocol

Paths tell you which actors are involved. Tracing an intention tells you what
actually survives the journey — and intentions degrade in transit far more
often than they disappear outright.

#### 1. Name the intention precisely

The signal, not the feature. "Customer submits a mortgage application", not
"the application process". Then: where does it originate, and what does the
originator believe happens next? That belief is worth recording separately,
because the gap between it and reality is usually the finding.

#### 2. Trace forward, actor by actor

At each hop, establish which of four things happens:

| | What it means | Why it matters |
|---|---|---|
| **Propagates** | passes onward, materially unchanged | the safe case |
| **Transforms** | passes onward, but different | meaning can be lost or invented here |
| **Forks** | produces additional intentions | each fork is a new path to discover |
| **Absorbs** | stops here | correct if resolved, a defect if not |

**Transformation is the one to slow down on.** Enrichment, normalisation,
truncation, defaulting a missing field, mapping an enum to a narrower set — each
is a place where the intention that arrives is not the intention that was sent.
Ask at every transform: *what information is lost here, and does anyone
downstream need it?*

#### 3. Find where the intention dies

Every trace must answer this. The intention either resolves (the thing the
originator wanted actually happened) or it dies somewhere. Where it dies is
almost never where it broke — a timeout at hop 3 commonly surfaces as an
intention dying unresolved at hop 7, which is where the user experiences it and
where the incident gets filed.

Distinguish:

- **Resolved** — the intention achieved its purpose
- **Compensated** — it failed, and something deliberately unwound it
- **Died silently** — it stopped, nothing was unwound, nobody was told

The third case is the one to hunt. Silent death is invisible in dashboards
built on error rates, because nothing errored.

#### 4. Compare intended against actual

State the path the team believes exists, then the path you traced, and name
every divergence. Divergences are the deliverable — the matching hops are not
news.

#### 5. Trace the error path too

Trace the same intention under one failure. The error path is a separate path
by definition, it is almost never designed with the same care as the happy
path, and it is where the undesigned forks live — the retry, the dead-letter
queue nobody monitors, the manual intervention an operator performs at 3am.

#### Output

An intention trace: origin, every hop with its propagate/transform/fork/absorb
classification, what each transformation loses, where the intention resolves or
dies, and the divergence list between believed and actual. Every fork you found
becomes a new path for `/discover paths`.

#### Example

```
/discover intentions "submit mortgage application"

Believed:  Portal -> Core Banking -> Underwriting

Traced:    Portal
             -> Message Queue        TRANSFORM  retention unknown (gap)
             -> Core Banking         ABSORB     batched, not real-time:
                                                resolves at the 02:00 run
             -> Audit Service        FORK       receives a copy;
                                                owning team unaware
             -> Underwriting         TRANSFORM  enriched with bureau data
                                                by an actor invisible to Portal

Divergences:
  - "real-time" is a batch with up to 14h latency
  - an enrichment actor exists that the Portal team does not know about
  - the audit fork is undocumented and unowned

Dies: on bureau-enrichment failure the record is dropped after 3 retries.
      No compensation, no alert. Silent death, roughly 40/month per ops.
```
