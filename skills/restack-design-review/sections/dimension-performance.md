### Performance and scale dimension

The first job here is to stop the review being an optimisation exercise. Most
performance findings in a design review should be about *shape* — structural
choices that cap what the system can ever do — not about speed.

**Establish the actual requirement first.** Ask for numbers: expected load,
peak-to-average ratio, latency budget, growth over the next year. If nobody can
answer, that is the finding, and it outranks everything below it. Without a
target, "is this fast enough" is unanswerable and any optimisation is guesswork
dressed as engineering.

**Latency budget across the path.** Take the critical path from the path map
and assign each hop a budget. The budgets must sum to less than the requirement.
This exercise reliably finds the hop nobody accounted for, and it converts a
vague worry into a specific one.

**Count the synchronous hops.** Each one multiplies latency and failure
probability. Four or more on a user-facing path is a structural finding, not a
tuning issue.

**Find the N+1 shapes.** Anywhere the design does work proportional to result
count — a query per item, a call per row. These are invisible at development
volume and fatal at production volume, and they are cheap to fix at design time.

**Identify the bottleneck deliberately.** Every system has one. If the team
cannot name theirs, they will optimise the wrong thing. Ask what saturates
first as load rises: a connection pool, a single writer, a rate limit, a lock,
a thread pool.

**Scaling shape.** For each actor: does it scale horizontally, vertically, or
not at all? An actor that cannot scale horizontally is a ceiling on the whole
path, and its ceiling is the system's ceiling regardless of what surrounds it.

**Statefulness against scaling.** Sticky sessions, in-memory caches, local
files and singleton schedulers all constrain how an actor can be scaled. Note
each one; they are the usual reason "just add instances" does not work.

**Caching, examined.** For each cache: what invalidates it, what does a stale
read cost, and what happens on a cold start after deploy? A cache that hides a
capacity problem is a residual with a known failure mode — say so, and check
whether the system survives it being empty.

**Behaviour under overload.** The important question is not how fast it is at
target load but what it does at 10x. Does it shed load, queue, degrade, or
collapse? Collapse under overload is a structural finding, and it is what turns
a spike into an outage.

**Cost as a scale property.** What does 10x traffic cost? A design that scales
technically but not economically has a ceiling too — it just arrives as a
budget conversation instead of an outage.

#### Premature optimisation

Complexity added for performance that nobody required is a finding in its own
direction. Ask what the measurement was that justified it. If there was none,
the complexity is cost with no demonstrated benefit, and it will make every
future change slower.

The distinction to hold: **structural choices that cap the ceiling are worth
raising at design time; constant-factor speed is not.** You can make a slow
implementation faster later. You cannot cheaply undo a synchronous chain, a
single-writer bottleneck, or a data model that forces a scan.
