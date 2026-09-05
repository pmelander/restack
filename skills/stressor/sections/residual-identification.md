### Residual identification

A residual is a **specific, localised change to the system** — a new actor, a
new intention, or a new path — introduced in response to a stressor and
persisting after it. It is not a mitigation, not a control, not an action item,
and not a process. "Monitor the payment gateway" is not a residual. "Introduce
a payment-intent queue actor between Order Service and Payment Gateway, with the
order path forking to an async settlement path" is.

The test: **can you draw it on the path map?** If it does not change the actors,
the intentions, or the paths, it is not a residual.

#### Work from the matrix, in this order

1. **Take the highest-vulnerability actor.** Not the scariest stressor — the
   most-hit actor. Residuals attach to actors.
2. **Read the cluster.** List the stressors hitting that actor and ask what they
   have in common at the mechanism level. Not "they all cause failure" — what
   specifically arrives at this actor, and why can it not absorb it?
3. **Propose the residual against the mechanism**, not against the stressors.
   A residual designed for one named stressor protects against one named
   stressor. A residual designed for the mechanism protects against the class,
   including the members you never thought of. This is the entire game.
4. **Re-score the residual's row against the full stressor set** — including
   stressors that were not hitting this actor. This is where the compound effect
   shows up, and where you discover a residual is worth more than it looked.
5. **Check what the residual creates.** Every residual adds actors, intentions
   or paths, and those are walkable and therefore stressable. A queue you added
   for resilience is now an actor that can fill, stall, lose messages, or
   reorder them. Name the new paths explicitly — they go into the next walk.

#### Residual shapes

Common shapes, with the mechanism each addresses. Use as a prompt, not a menu —
the right residual is usually a specific instance of one of these, shaped by
the actual path.

| Shape | Mechanism it addresses | Typically clears |
|---|---|---|
| Queue / buffer actor | temporal coupling to a downstream actor | load spikes, downstream outages, slow dependencies, maintenance windows |
| Circuit breaker | unbounded failure propagation upstream | cascading failure, retry storms, thundering herd |
| Cache / read replica | dependence on a single read source | source outage, load, latency, cost spikes |
| Idempotency key + dedup | duplicate intention delivery | retries, network partitions, at-least-once delivery, human replay |
| Bulkhead / partition | one tenant or path consuming shared capacity | noisy neighbour, single-tenant surge, blast-radius containment |
| Outbox / event log | dual-write inconsistency between two actors | partial failure, audit gaps, replay after incident |
| Compensating path | an intention that cannot be rolled back in place | partial completion, downstream rejection, regulatory reversal |
| Explicit contract + version | undeclared coupling between actors | partner change, upgrade skew, unowned integration |
| Degraded-mode path | all-or-nothing behaviour under partial loss | dependency down, capacity loss, regional failure |
| Human-in-the-loop actor | automation with no safe failure behaviour | ambiguous cases, regulatory judgement, exceptional volume |
| Phased-rollout path | change landing everywhere at once | organisational veto, rollback need, unproven residual |

The last two matter more than they look. Organisational stressors need
residuals too, and a phased rollout that gives a nervous system owner a
visible off-ramp is a genuine architectural residual — it changes the paths.

#### Ranking by leverage

Leverage is impact removed per unit of complexity added. Present residuals
ranked, and show the working:

```
R1  Payment-intent queue between Order Service and Payment Gateway
    Clears:      5 cells across 4 stressors (provider down, spike, AZ loss, audit)
    Also helps:  2 cells not in the original cluster
    Adds:        1 actor, 1 new path (async settlement), 2 new stressor surfaces
    Reversible:  yes - can run shadowed before cutover
    Leverage:    HIGH - one actor, seven cells, no data model change

R2  Idempotency keys on the order intention
    Clears:      3 cells across 2 stressors
    Adds:        0 actors, 1 new state store, changes the order contract
    Reversible:  no - contract change, partners depend on it once shipped
    Leverage:    MEDIUM - real gain, but a one-way door on the contract
```

Rank by leverage, then re-rank by reversibility when terrain is minefield: there,
a reversible residual with 70% of the benefit beats a one-way door with 100%.

#### Two failure modes to watch for

**Residual inflation.** Proposing a residual for every high cell produces an
architecture that is a pile of defensive machinery nobody understands. If the
residual list is longer than about five per iteration, you are addressing
stressors individually instead of finding the mechanism they share. Go back to
step 2.

**Residuals as forecasts.** A proposed residual reduces nothing. Until it is
implemented and the path re-walked, the matrix improvement is a prediction.
Always mark residuals `proposed` or `implemented`, and always say which set the
reported total counts — `/journey iterate` depends on that distinction to make
an honest call.
