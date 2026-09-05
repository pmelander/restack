### Load testing

A load test exists to replace assumptions with evidence. Design it around the
assumption you most want to kill, not around producing a reassuring graph.

#### Start from the estimate's weakest assumption

The demand model closed with a list of what was measured, supplied and assumed.
The test targets the assumption with the highest impact if wrong and the lowest
cost to check. Everything else is secondary.

State the assumption as a falsifiable prediction before running anything:
"Order Service sustains 25 RPS per core at p95 under 200ms". Then the test has
a pass condition, and a result that contradicts it is a finding rather than a
number to interpret afterwards.

#### The scenarios that earn their place

| Scenario | Answers |
|---|---|
| **Steady state at expected peak** | does it meet the latency target at the load we designed for? |
| **Ramp to breaking point** | where is the ceiling, and which resource saturates first? |
| **Spike** | can it absorb an instant jump — and does auto-scaling arrive in time? |
| **Soak** (hours) | are there leaks, unbounded growth, or slow degradation? |
| **Dependency degraded** | what happens when a downstream is slow rather than down? |
| **Recovery** | after overload ends, does it recover on its own or stay wedged? |

The last three are the ones that get skipped and the ones that find the real
defects.

**Slow-dependency testing matters more than dependency-down testing.** Down is
usually handled; slow exhausts thread pools and connection limits upstream and
turns one component's problem into everyone's. If you run only one failure
scenario, run this one.

**Recovery testing catches the wedged state** — the system that survives
overload but never comes back without a restart, because a queue is saturated
or a circuit breaker never closes. Nobody finds this except by testing it.

#### Load testing validates residuals

This is the part specific to this toolkit, and the highest-value use of a load
test here.

The stressor matrix asserts that residuals reduce impact. Until a residual has
absorbed a real stressor, that assertion is a prediction. A load test is where
several of them become evidence:

- Does the **queue** actually absorb the spike, and what is its depth ceiling
  and drain time?
- Does the **circuit breaker** trip, and — the part that usually fails — does
  it close again afterwards?
- Does **auto-scaling** arrive before the latency target is breached, or after?
- Does the **cache** protect the origin, and what happens on cold start?
- Does the **degraded mode** actually engage, and does the system tell anyone?

Record the result per residual and feed it back into
`docs/journey/stressor-iteration-history.md`. A residual that does not work
under test is a class B finding — the mechanism was misdiagnosed — and belongs
back in `/restack-stressor residues`, not in a tuning ticket.

#### Running it honestly

- **Test in an environment shaped like production.** Where it differs, say how,
  and say which results the difference invalidates. A test at a tenth of
  production data volume tells you almost nothing about the database.
- **Use realistic data and access patterns.** Uniform synthetic keys hide hot
  keys and make every cache look excellent.
- **Include the third parties, or stub them at their real latency and rate
  limit.** Stubbing a partner API as instant makes the test meaningless for the
  path that actually matters.
- **Watch the whole path, not the load generator.** The generator tells you
  what you sent. The path tells you where it went wrong, and it is usually two
  hops from where the error surfaced.
- **Never test against production**, or against real customer, booking or
  payment data, without the owner's explicit approval. Synthetic or anonymised
  data in an isolated environment is the default.

#### Reporting

State: what was predicted, what happened, where it broke, which resource
saturated, which residuals held and which did not, and what the test could not
tell you because of how the environment differed.

That last item is what stops a load test result being quoted for eighteen
months as though it proved more than it did.
