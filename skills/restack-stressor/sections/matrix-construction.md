### Impact matrix construction

The matrix is the instrument. Everything downstream — which actors are
vulnerable, which residuals have leverage, whether to iterate — is read off it.
A matrix built carelessly produces confident wrong answers, so build it
deliberately.

#### Columns are actors from walked paths

Not a component inventory. Not the boxes on an existing architecture diagram.
The columns are the actors you encountered while walking, in path order, because
position in a path carries information: actors late in a path inherit the
vulnerability of everything upstream of them.

If an actor appears on more than one path, it gets **one** column. Its
vulnerability is the union across paths, and that concentration is usually the
first thing worth noticing.

An actor you leave out scores zero by construction. When a matrix refuses to
improve across iterations, a missing actor is the most common cause.

#### Rows are stressors

One row per stressor, tagged with its source: `generated`, `compliance:<pack>`,
`organisational`, `incident:<date>`. Tagging matters at iteration three, when
you need to know whether the matrix has drifted toward the comfortable
technical stressors and away from the ones that hurt.

#### Scoring

Score each cell **binary — 1 if this stressor affects this actor, 0 if not.**

Resist the urge to introduce a severity scale. Binary scoring is not a
simplification, it is the point:

- Severity estimates are guesses that look like measurements, and they let a
  team argue an uncomfortable stressor down to a 2 instead of confronting it.
- The signal you want is **breadth of exposure** — how many independent things
  can reach this actor — not depth of any one failure.
- Binary keeps the matrix cheap enough to rebuild every iteration. A matrix too
  expensive to rebuild stops being rebuilt, and a stale matrix is worse than
  none.

"Affects" means: under this stressor, this actor fails, degrades materially,
loses correctness, or propagates the damage onward. An actor that notices a
stressor and handles it correctly scores 0 — handling it *is* the residual
working.

When you genuinely cannot tell whether a stressor reaches an actor, score 1 and
mark the cell `?`. Unknown exposure is exposure. Then register the uncertainty
as an assumption with the discovery step that would settle it.

#### The two totals

- **Stressor impact** (row sum) — how many actors this stressor reaches. High
  rows are systemic stressors; they usually indicate a missing cross-cutting
  residual rather than a set of local fixes.
- **Actor vulnerability** (column sum) — how many stressors reach this actor.
  High columns are where residuals earn the most.

**Total system impact** is the sum of all cells. It is the number you track
across iterations. It is meaningful only as a *trend against a stable stressor
set* — adding stressors raises it, which is not a regression. Whenever the
stressor set changes between iterations, report both: total against the
original set, and total against the expanded set. Comparing across different
stressor sets and calling it improvement is the most common way this analysis
is quietly falsified.

#### Output format

```
                       | API GW | Auth | Order | Inventory | Payment | Notify |
-----------------------|--------|------|-------|-----------|---------|--------|
Payment provider down  |   0    |  0   |   1   |     0     |    1    |   1    |  = 3
Region-wide AZ failure |   1    |  1   |   1   |     1     |    1    |   1    |  = 6
Auth token clock skew  |   1    |  1   |   1   |     0     |    0    |   0    |  = 3
Black Friday 40x spike |   1    |  0   |   1   |     1     |    1    |   1    |  = 5
Regulator audit mid-outage | 0  |  0   |   1   |     0     |    1    |   0    |  = 2
Fire-breathing lizards |   0    |  0   |   0   |     1     |    0    |   0    |  = 1
-----------------------|--------|------|-------|-----------|---------|--------|
Vulnerability          |   3    |  2   |   5   |     3     |    4    |   3    |  Total: 20
```

Always show the totals row and column. The matrix without its margins is a
table; with them it is a diagnosis.

### Reading the matrix

Look for four things, in this order:

**1. Concentration.** One or two actors carrying most of the vulnerability is
the best possible finding — it means a small number of residuals will move the
total a long way. In the example, Order Service at 5 is the obvious first
target.

**2. Clusters.** Groups of stressors hitting the same actor set are the same
underlying weakness wearing different clothes. In the example, "AZ failure" and
"Black Friday spike" hit nearly identical columns — that is not two problems,
it is one: nothing in the path degrades gracefully under load loss. One residual
will clear both rows. Clusters are where leverage lives.

**3. Flatness.** Impact spread evenly across all actors usually means the
stressors are too generic ("the network is slow") rather than that the system is
uniformly fragile. Regenerate with more specific stressors before believing a
flat matrix.

**4. Suspicious zeros.** An actor with vulnerability 0 is either genuinely
stateless and trivially replaceable, or you have not understood what it does.
Check which. In brownfield terrain it is usually the second, and it is a signal
to run `/restack-discover actor` against it.

### Comparing iterations

Report the before/after as a table, per actor, not as a single headline number:

```
Actor          | Iter 1 | Iter 2 | Delta | Residual applied
---------------|--------|--------|-------|------------------------------
Order Service  |   5    |   2    |  -3   | async payment queue + timeout
Payment GW     |   4    |   2    |  -2   | async payment queue
Inventory      |   3    |   3    |   0   | none
Total          |  20    |  13    |  -7   | 1 residual, 2 actors changed
```

The per-actor view is what shows the compound effect: one queuing actor took
three points off Order Service *and* two off Payment Gateway, against stressors
that had nothing to do with each other. That is the mechanism the architect
needs to internalise — a residual introduced for one stressor protecting against
several unrelated ones — and it is invisible in a headline total.
