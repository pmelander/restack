### Stressor generation method

A stressor is any fact or external influence outside your current understanding
of the system. The word "outside" is doing the work: a stressor you already
designed for is not a stressor, it is a requirement. Generation exists to reach
the ones nobody has thought of.

**Default: 20-30 stressors.** Fewer produces a matrix too sparse to show
clusters. Many more, and the matrix stops being rebuildable each iteration.

#### Generate across all seven categories

Do not stop when the technical ones are exhausted — that is where most teams
stop, and it is why most matrices under-report the vulnerabilities that
actually bite.

| Category | Reaches | Examples |
|---|---|---|
| **Technical** | infrastructure, dependencies, data | region loss, dependency deprecated overnight, clock skew, schema drift, certificate expiry |
| **Business** | demand, money, strategy | 40x demand spike, a competitor makes the feature free, funding cut mid-build, acquisition of a key partner |
| **Social / human** | operators and users | the only person who understands the batch job leaves, users adopt it for something you did not design, a support team routes around the workflow |
| **Organisational** | delivery and governance | architecture board rejects the vendor, the owning team refuses the change, budget approval takes two quarters, a hiring freeze |
| **Regulatory** | law and contract | new data residency rule, an audit during an outage, a partner contract requires 4-hour RTO, a right-to-erasure request mid-transaction |
| **Natural / physical** | the world | datacentre flood, undersea cable cut, pandemic-scale absence, power grid instability |
| **Absurd** | your assumptions | fire-breathing lizards, the moon, everyone's clocks run backwards, all customers named Dave act simultaneously |

**Organisational stressors are mandatory, not optional.** A matrix with no
organisational rows is describing a system that will be built in a vacuum.
Teams routinely find their single highest-impact stressor is a governance
process, not a technology.

#### Every safety lever gets three stressors

Mandatory, under technical and organisational, for every kill switch, mode,
break-glass or manual failover in the design. Ask:

1. **Ineffective lever.** It is pulled and has no effect. Example: the operator
   turns the feature off, the write to the control record fails, and the
   feature keeps running.
2. **Unconfirmable lever.** It has the effect and no one can confirm it.
   Example: the stop worked, but the status signal was emitted by the component
   the switch just stopped.
3. **Wrong actor.** It is pulled by the wrong actor, or by the right actor at
   the wrong time. Examples: a neighbour team's automation, a stale runbook
   step, a break-glass used for convenience.

A stressor set that covers "the feature fails off" thoroughly can still miss all
three. In one field session, both of the first two were found while writing the
runbook, not by the matrix. Generate at least one ineffective-lever and one
unconfirmable-lever row per lever, and walk each with the lever template in
the walk protocol.

#### The absurd stressors are load-bearing

Include at least one genuinely ridiculous stressor per generation. This is not
a joke about the method, it is the method.

Plausible stressors are drawn from what you already fear, and things you
already fear are things you have already partly designed for. The absurd
stressor breaks the frame: "fire-breathing lizards melt the inventory
datacentre" is functionally "sudden total physical loss of one component with no
warning and no failover window" — a scenario a team will happily reason about
when it arrives dressed as a lizard, and will wave away as unrealistic when it
arrives dressed as a datacentre fire.

When an absurd stressor lands a hit, translate it before it goes in the matrix:
keep the absurd label for the team's benefit, and note the mechanism next to it.

#### Make each stressor a scenario, not a category

| Weak (a category) | Strong (a scenario) |
|---|---|
| "Security" | "A valid API key is leaked in a public repo and used for 6 hours before detection" |
| "Performance issues" | "Inventory queries slow to 8s during the 20:00 replication window" |
| "Compliance" | "A regulator requests full transaction history for one customer during a partial outage" |
| "Third-party risk" | "The payment provider deprecates the API version with 30 days' notice" |

A category cannot be walked. A scenario can: you can take it to each actor in
sequence and ask what happens. If a stressor cannot be walked, it is not
finished — rewrite it until it can be.

#### Generating for a system you already know

The hard part after iteration two is that you start generating stressors your
existing residuals already handle, and the matrix looks great while learning
nothing. Counter it deliberately:

- Generate against the **residuals themselves**. Every residual added actors and
  paths; what stresses those? A queue that absorbs load spikes is an actor that
  can fill, stall, reorder, or silently drop.
- Generate from **incidents**, yours and other people's. A real incident is a
  stressor with a known outcome — the highest-quality input this method gets.
  Check whether your matrix would have predicted it. If not, the gap is in the
  path map.
- Generate from **what changed in the environment** since the last iteration —
  new partner, new regulation, new traffic profile, new team.
- Ask: **what would have to happen for this system to be shut down?** Then work
  backwards to the stressors that produce it.
