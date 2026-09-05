### Path walk protocol

A walk is the act of traversing a path actor by actor, watching what an
intention does as it propagates. It is the foundational move: the matrix
columns come from walks, and a matrix built without walking is a matrix over a
component list.

#### 1. Define the path

- **Which aspiration does this path serve?** A path that serves no stated
  aspiration is either scope creep or evidence the aspiration is incomplete.
- **What intention triggers it?** Name the signal, not the feature. "Customer
  submits an order", not "the checkout feature".
- **Where does it start and where is the intention fully resolved?** A path
  ends when the intention is resolved — not when the HTTP response returns.
  Order paths commonly resolve at settlement or fulfilment, well after the user
  has seen a success page. Ending the walk at the response is how the async
  half of the system stays invisible.

#### 2. List the actors in sequence

Every hop from trigger to resolution is an actor. Include the ones that are
easy to forget: load balancers that terminate TLS, message brokers, scheduled
jobs, the human who approves an exception, the partner system on the other side
of an integration, the database that enforces a constraint.

```
Browser -> API Gateway -> Auth Service -> Order Service -> Inventory DB
        -> Payment Gateway -> Notification Queue -> Email Service
```

#### 3. Characterise each actor

For each, record:

- **Stateful or stateless?** Stateful actors are where corruption, drift and
  inconsistency live; stateless ones are usually replaceable and score lower.
- **What intention does it receive, and what does it propagate?** These are
  often different, and the transformation is where meaning is lost. An actor
  that receives "the customer wants this order" and propagates "row inserted"
  has dropped the intention.
- **What is its failure mode?** Fails loudly, fails silently, degrades, hangs,
  or corrupts. Silent failure and hanging are the two that make downstream
  actors vulnerable, because the path cannot tell that anything is wrong.
- **What does it assume about its upstream?** Ordering, at-most-once delivery,
  a timeout that will fire, a field always being populated. Undeclared upstream
  assumptions are where stressors get in.

Evidence rules apply here in full. A failure mode you inferred from the actor's
name is not a failure mode. Read the config, read the retry policy, or mark it
as an assumption.

#### 4. Walk under a stressor

Apply one stressor and traverse the same path again, asking at each actor:

- Does this actor **fail**, **degrade**, or **pass the stressor onward intact**?
- If it propagates, does it propagate the damage or a *transformation* of it?
  An actor that turns "payment provider slow" into "thread pool exhausted" has
  amplified the stressor, and that amplification is the finding.
- Does the actor **notice**? An actor that fails without signalling makes every
  downstream actor blind.
- Where does the intention **die**? The point where the intention is lost
  without resolution or compensation is where the user experiences the failure,
  and it is usually several hops downstream of the actor that broke.

#### 5. Identify fork points

Where the path branches, a new path begins — paths never fork by definition.
Note each fork and add the new path to the walk queue. Common forks people
miss: the error path after a timeout, the retry path, the compensation path,
the manual-intervention path an operator takes when the automated one fails.

The forks are frequently where the real vulnerability sits, because they are
the paths nobody designed deliberately.

#### 6. Capture residual opportunities as you go

At each actor where the stressor causes harm, note what new actor, intention or
path would prevent it. Do not design the residual yet — `/stressor residues`
does that against the whole matrix, where the leverage is visible. Just record
the opportunity so it is not lost.

#### Walking multiple paths

Most systems have several significant paths: the happy path, the error path,
the async path, the admin path, the batch path, the path during partial outage.
Walk each separately. They expose different vulnerabilities, and an actor's
true vulnerability is the union across every path it appears on.

Walk the happy path first to establish the actor set, then the error path — the
error path is where the largest surprises are, in almost every system.

#### Output

A path map showing actors in sequence, their stateful/stateless nature, the
intentions connecting them, their failure modes, and — when a stressor was
applied — which actors were affected, how the damage transformed as it
propagated, and where the intention died.
