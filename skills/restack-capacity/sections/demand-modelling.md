### Demand modelling

Capacity work fails at the first step far more often than at the arithmetic.
Get the demand numbers honest and the rest is mechanical.

#### 1. Gather the demand signals

Ask for each, and push back on round numbers that appeared without a source:

- **Concurrent users, or requests per second.** These are different questions
  and teams conflate them. Concurrency times request rate per user gives RPS;
  ask which one they actually know.
- **Peak-to-average ratio.** The number that matters most and is asked for
  least. A system averaging 100 RPS with a 20x lunchtime peak is a 2,000 RPS
  system, and sizing to the average guarantees an outage on a schedule.
- **The shape of the peak.** Daily, weekly, seasonal, or event-driven. A Black
  Friday profile and a 9am-Monday profile need different answers — one is
  predictable and can be pre-provisioned, the other must be absorbed.
- **Data volumes:** working set, total stored, growth rate, retention period.
  Retention is the one that turns a storage estimate into a very different
  number.
- **Latency targets at p50, p95 and p99.** An average latency target is not a
  target; the tail is what users experience and what cascades.
- **Availability target**, and what it costs per hour when missed.

**Where a number does not exist, say so and carry it as an assumption** with
what would establish it. An estimate built on invented demand is arithmetic
performed on fiction, and its confident presentation is the danger — it gets
quoted later as though it were measured.

#### 2. Classify the workload

CPU-bound, memory-bound, I/O-bound, or network-bound. This determines which
resource you are actually sizing and which will saturate first. Getting it
wrong means optimising the resource that was never the constraint.

If nobody knows, that is a measurement task, not a guess.

#### 3. Estimate per component

Back-of-envelope, showing the working. The arithmetic must be visible so the
architect can check the assumption rather than the answer.

```
Checkout path, peak 2,000 RPS

Order Service
  per request: ~40ms CPU, ~15MB working set
  one core sustains ~1000/40 = 25 RPS
  2,000 RPS / 25 = 80 cores
  at 60% target utilisation = 133 cores
  = 34 x 4-core instances

Inventory DB
  reads:  2,000 RPS x 3 queries = 6,000 QPS
  writes:   200 RPS x 2 = 400 QPS
  working set 200GB -> must fit in RAM or reads hit disk
  ASSUMPTION: 3 queries per checkout. Source: none. Validate by tracing
  one checkout in staging. Impact if wrong: linear on read capacity.
```

Show the assumption inline, with what would settle it and what it costs if
wrong. That is the difference between an estimate and a number someone will
later mistake for a measurement.

#### 4. Apply headroom deliberately

Not a reflex multiplier — headroom answers two specific questions:

- **How fast can you add capacity?** Auto-scaling with a 4-minute warm-up needs
  enough headroom to survive 4 minutes of growth. Manual provisioning needs
  enough to survive a procurement cycle.
- **What is the cost asymmetry?** Over-provisioning costs money linearly.
  Under-provisioning costs an outage. Where the asymmetry is steep, buy
  headroom; where compute is elastic and cheap, buy less.

Typical: 2–3x peak for stateless with fast scaling; more, and more
conservative, for stateful components where adding capacity means a migration
rather than an instance.

**State the headroom and its reasoning separately from the estimate**, so a
reviewer can disagree with one without rejecting the other.

#### 5. Rate confidence and say what to validate

Every estimate closes with: which numbers were measured, which were supplied,
which were assumed, and the single cheapest test that would most reduce the
uncertainty. That test is the output that matters — an estimate nobody validates
becomes a belief with a spreadsheet behind it.

---

### Forecasting

Same discipline extended over time. Three additions:

**Model the driver, not the metric.** Traffic does not grow; customers grow,
and traffic follows. Forecasting the metric directly loses the ability to
notice when the relationship changes.

**Model a range, not a line.** Give conservative, expected and aggressive
cases, and say what each implies for when you must act. The useful output of a
forecast is not a number but a **trigger**: "at 40,000 daily orders the
Inventory read path saturates — that is roughly Q3 on the expected case, and
the lead time to shard is two months, so the decision point is Q2."

**Name what breaks first, and second.** Growth does not degrade a system
evenly; it hits one constraint, then the next one behind it. Knowing the order
tells you what to fix and in what sequence — and the second bottleneck is
frequently much harder than the first, which is why finding it early matters.
