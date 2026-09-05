# Usage Guide

Worked examples for every skill, in journey order.

New here? Start with [Getting Started](../GETTING_STARTED.md) for a first
engagement end to end, or [QUICKREF](../QUICKREF.md) for the command list.

## Contents


1. [Orchestration and discovery](#orchestration-and-discovery)
2. [Stressor analysis](#stressor-analysis)
3. [Decide and record](#decide-and-record)
4. [Build it](#build-it)
5. [Get better at it](#get-better-at-it)
6. [Compliance via stressor packs](#compliance-via-stressor-packs)
7. [Workflow examples](#workflow-examples)

> **A note on the gates.** Three commands stop and wait for you rather than
> producing output and moving on: `/restack-discover confidence`,
> `/restack-journey iterate`, and any approach decision where two designs are
> both viable. That is by design — see
> [Getting Started](../GETTING_STARTED.md#what-to-expect-from-these-skills).

---

## Orchestration and discovery


### Architect's Journey (`/restack-journey`)

> **New in v2:** Terrain classification is now a **stop gate** — it presents a decision brief with the evidence and waits for you to confirm before mapping any route. `iterate` separates residuals that are *implemented* from those merely *proposed*; impact reduction from the second kind is a forecast, not a result.

The orchestrating skill — knows which tools to use, when, and in what sequence. Start here when beginning a new engagement, or when you're mid-journey and unsure what comes next.

```
/restack-journey start           # assess terrain (greenfield/brownfield/minefield), map the route
/restack-journey where           # where am I? what have I done? what comes next?
/restack-journey iterate         # is stressor impact low enough to proceed, or iterate again?
/restack-journey review          # health check — what's been skipped, what's at risk?
/restack-journey cadence         # establish an ongoing rhythm for a live system
```

**The three terrains:**
- **Greenfield** — blank canvas, design your paths then walk them
- **Brownfield** — existing system, discover then walk
- **Minefield** — high fragility and complexity, discover extensively before touching anything

**The stressor iteration loop** — the heartbeat of every journey:
```
walk → generate → analyze → residuals → implement → re-walk → is impact low enough? → loop or proceed
```

Iterate until impact is *sufficiently low* — not zero, but low enough given the system's aspiration and the cost of further improvement. `/restack-journey iterate` helps you make that judgment explicitly.

---

### Environment Discovery (`/restack-discover`)

> **New in v2:** `confidence` is now a real gate with terrain-dependent thresholds — in brownfield an unknown becomes a registered assumption, in a **minefield an unknown on a critical path blocks**. "Not ready" routes to a specific command, never to "do more discovery".

Map what actually exists in an existing environment before designing anything new within it. Brownfield, oilfield, and minefield environments rarely match their documentation — discovery produces the confident path maps that feed stressor analysis.

**Discovery walks are different from design walks:**
- In design walks you validate what you designed
- In discovery walks you build your understanding from scratch
- Confidence is earned, not assumed

```
/restack-discover paths                  # map entry points and trace paths forward
/restack-discover actor "Payment Service" # what does it actually do — not what docs say
/restack-discover intentions             # trace how a specific intention propagates
/restack-discover gaps                   # prioritise what you still don't know
/restack-discover organisation           # map resistance patterns as stressors
/restack-discover confidence             # are you ready to hand off to /restack-stressor walk?
```

**Done condition:** You are confident that paths are correct and you know the intention of each actor. Not certainty — confidence. There's a difference.

**Organisational resistance as stressors:** A product owner who cannot get budget, an EA who blocks vendor choices, a team that resists integration — these are stressors on the architecture, not actors on paths. `/restack-discover organisation` translates them into the stressor list where they belong.

**Feeds directly into:**
```
/restack-discover confidence → /restack-stressor walk → /restack-stressor generate → /restack-stressor analyze
```

---

## Stressor analysis


### Walk, stress, and find residuals (`/restack-stressor`)

> **New in v2:** `analyze`, `vulnerabilities`, `residues` and `iterate` now carry full method: binary scoring and why, cluster reading, residual ranking by leverage, and per-actor before/after comparison. Residuals are designed against the *mechanism* a cluster shares, not against individual stressors — that is what produces the compounding.

Walk your system's paths and stress-test each actor to build antifragile systems grounded in Residuality Theory.

**Core vocabulary:**
- **Actor** — any user, application, or module that acts on an intention
- **Intention** — the signal that connects actors and drives flow through the system
- **Path** — a sequence of actors connected by intentions (never forks — forks create new paths)
- **Walk** — traversing a path to evaluate each actor's behaviour as intentions propagate
- **Residual** — a new actor, intention, or path introduced in response to a stressor

```
/restack-stressor walk checkout        # Walk the checkout path — map actors, intentions, stateful/stateless
/restack-stressor generate 30          # Generate 30 diverse stressors (including absurd ones)
/restack-stressor analyze              # Build impact matrix with actors as columns
/restack-stressor vulnerabilities      # Identify most-impacted actors across all paths
/restack-stressor residues             # Suggest residuals — new actors, intentions, or paths
/restack-stressor iterate              # Re-walk after adding residuals, measure improvement
/restack-stressor workshop             # Facilitate team stressor workshop
/restack-stressor import data.xlsx     # Import existing stressor matrix
```

**The right sequence:** Walk paths first → generate stressors → walk under stress → build matrix → identify vulnerabilities → add residuals → re-walk.

**Why walk before generate?** The impact matrix columns are the actors on your paths. Walking first ensures the matrix reflects how intentions actually flow — not an arbitrary component list. Actors later in a path are often more vulnerable because they depend on everything upstream.

**Why include absurd stressors?** Fire-breathing lizards and zombie apocalypses represent *unknown unknowns*. If your architecture can't conceptually handle the absurd, it probably can't handle real surprises. 🐉

**The compound effect:** A single residual — say, an async queue actor added between two services — protects against load spikes, downstream failures, traffic bursts, and more. Residuals compound across iterations.

---

## Decide and record


### Architecture Decision Records (`/restack-adr`)

> **New in v2:** ADRs now record **reversibility** (a one-way door gets one whether or not anyone asked) and **which residual they implement**, with the stressors it clears. `review` separates whether the *outcome* was good from whether the *reasoning* was sound — judging on results alone teaches luck.

Create and manage Architecture Decision Records — the foundation of traceable, principled architecture.

```
/restack-adr create Choose PostgreSQL for primary database

Claude will ask:
- What problem are you solving?
- What alternatives did you consider?
- What are the trade-offs?
- Who are the decision makers?

Generates: docs/adr/ADR-001-choose-postgresql-for-primary-database.md
```

**When to create an ADR:**
- ✅ Technology selections (database, framework, cloud provider)
- ✅ Significant architecture patterns (microservices, event-driven)
- ✅ Security approaches (authentication, encryption strategy)
- ✅ Decisions to *not* do something (as important as decisions to do it)
- ❌ Minor implementation details
- ❌ Easily reversible choices

---

### Solution Documentation (`/restack-solution-doc`)

> **New in v2:** The HLD now has a mandatory section recording **what each residual defends against**. Without it a residual reads as over-engineering, and the first thing a new team does with unexplained complexity is delete it.

Generate comprehensive technical documentation from your architecture.

```
/restack-solution-doc hld          # High-Level Design → docs/architecture/HLD.md
/restack-solution-doc lld          # Low-Level Design → docs/architecture/LLD-*.md
/restack-solution-doc deployment   # Deployment Guide → docs/deployment/DEPLOYMENT.md
/restack-solution-doc runbook      # Operations Runbook → docs/operations/RUNBOOK.md
/restack-solution-doc complete     # All of the above
```

---

### Technology Stack Advisor (`/restack-tech-stack`)

> **New in v2:** Seven evaluation dimensions, including two teams usually skip: **which residuals the design requires** (a technology that makes a required residual awkward is a bad fit however well it scores) and **organisational constraint** as a stressor with a shape. `migrate` starts from the position that the migration should not happen.

Evaluate and select technologies with context-aware, bias-free analysis.

```
/restack-tech-stack recommend                      # Full stack for your context
/restack-tech-stack compare React vs Vue           # Side-by-side comparison
/restack-tech-stack evaluate Kubernetes            # Assess fit for your situation
/restack-tech-stack migrate from MySQL to Postgres # Migration analysis
```

**Best practice:** Always follow a tech decision with `/restack-adr create` to document it.

---

### Design Review (`/restack-design-review`)

> **New in v2:** Every finding is now cross-checked against the stressor matrix and classified: **A** matrix caught it, residual missing · **B** residual present but not working · **C** matrix should have caught it · **D** genuinely new. The distribution is the real finding — mostly **C** means a discovery problem, and fixing the findings individually leaves the cause.

Multi-dimensional architecture review with scored assessment.

```
/restack-design-review complete      # Full review across 8 dimensions
/restack-design-review security      # Security-focused
/restack-design-review performance   # Performance-focused
/restack-design-review api           # API design review
/restack-design-review data          # Data architecture review
```

**Scorecard:**
- 🟢 Strong (8-10) — meets or exceeds standards
- 🟡 Adequate (5-7) — acceptable but has issues
- 🔴 Needs Improvement (0-4) — must be addressed

---

## Build it


### Cloud Architect (`/restack-cloud`)

> **New in v2:** Cloud primitives are treated as the **residuals** they are — a queue, a replica, multi-AZ. Includes the check that finds the most serious defects: does the residual depend on the thing it protects against? DR tier is derived from stressors rather than picked from a table, because replication defends against region loss and against *none* of corruption, ransomware or a bad deploy.

Design cloud-native architectures, generate IaC, and build Well-Architected thinking.

```
/restack-cloud design "e-commerce platform, 10k concurrent users, 99.9% SLA"
/restack-cloud iac terraform           # Generate Terraform for the design
/restack-cloud iac cloudformation      # Or CloudFormation
/restack-cloud review                  # Well-Architected review across all 6 pillars
/restack-cloud cost                    # Cost analysis and optimisation
/restack-cloud migrate to AWS          # Migration strategy using the 6 R's
/restack-cloud dr                      # Disaster recovery strategy (RTO/RPO → tier)
```

**Well-Architected Pillars:**
1. Operational Excellence
2. Security
3. Reliability
4. Performance Efficiency
5. Cost Optimisation
6. Sustainability

**The 6 R's for migration:** Rehost, Replatform, Repurchase, Refactor, Retire, Retain

**DR Tiers:** Backup & Restore → Pilot Light → Warm Standby → Active/Active

---

### Capacity Planner (`/restack-capacity`)

> **New in v2:** Bottlenecks feed back **as stressors** — an actor at its ceiling is a vulnerable actor. Load tests now validate residuals: does the queue absorb the spike, does the circuit breaker close again. Estimates show the arithmetic with assumptions marked inline, so they are not mistaken for measurements.

Estimate resource requirements, design scaling strategies, and validate with load testing.

```
/restack-capacity estimate             # Back-of-envelope resource estimation
/restack-capacity scale horizontal     # Design horizontal scaling approach
/restack-capacity scale database       # Database scaling strategy
/restack-capacity scale auto           # Auto-scaling design
/restack-capacity bottleneck           # Identify where constraints will appear first
/restack-capacity load-test            # Load testing strategy (baseline, load, spike, soak, stress)
/restack-capacity forecast             # Model growth across 3/6/12/24-month horizons
/restack-capacity right-size           # Identify and eliminate over-provisioning
```

**Key principle:** Never trust estimates alone — always validate with load tests.

**Load test scenarios:**
| Scenario | Purpose |
|----------|---------|
| Baseline | Confirm normal operation |
| Load | Validate peak throughput |
| Spike | Test sudden 10x traffic |
| Soak | Find memory leaks over hours |
| Stress | Find the breaking point |

---

## Get better at it


### Architecture Learning Analyzer (`/restack-arch-learning`)

> **New in v2:** Built on the fact that the toolkit produces **written predictions** — ADRs, matrices, residual impact estimates — which makes the architecture falsifiable. Its output is not a lesson but a *correction to the method*: "we consistently miss actors nobody owns, so enumeration now asks who owns each hop".

Build systematic organisational learning from your architectural history.

```
/restack-arch-learning analyze       # Analyze all ADRs for patterns and outcomes
/restack-arch-learning patterns      # Extract recurring decision patterns
/restack-arch-learning outcomes      # Review how past decisions played out
/restack-arch-learning retrospective # Facilitate team architecture retrospective
/restack-arch-learning lessons       # Generate lessons learned report
/restack-arch-learning trends        # Identify trends in decision-making over time
```

**Use on a cadence:** Run quarterly to build institutional knowledge that outlasts individual team members.

---

### Team Capability Assessor (`/restack-capability-assessor`)

> **New in v2:** A capability gap is now a **stressor**, not an HR matter. Ratings come from artefacts and from practice under deadline rather than from knowledge, and development attaches to live work — workshops produce knowledge, and knowledge is not what the assessment measured.

Assess and grow team architectural maturity across 6 dimensions.

```
/restack-capability-assessor assess    # Current maturity across 6 dimensions
/restack-capability-assessor gaps      # Highest-priority improvement areas
/restack-capability-assessor roadmap   # 3-6 month development plan
/restack-capability-assessor track     # Progress since last assessment
/restack-capability-assessor exercises # Concrete capability-building activities
/restack-capability-assessor compare   # Benchmark against maturity model
```

**6 Capability Dimensions:**
1. Decision-Making Quality
2. Documentation Clarity
3. Technology Evaluation
4. Design Quality
5. Evolutionary Thinking
6. Learning Culture

**Maturity Levels:** Ad-hoc → Aware → Defined → Managed → Optimising

---

### Pattern Extractor (`/restack-patterns`)

> **New in v2:** Recurring **residuals** are the richest source, because their effectiveness is already measured — a pattern that says "removed 5-7 matrix points across three systems" beats one asserting a benefit. Anti-patterns now require the field that is always missing: why people keep choosing it.

Extract architectural patterns from your accumulated knowledge and institutionalise them.

```
/restack-patterns extract              # Extract patterns from ADRs, codebase, decisions
/restack-patterns catalog              # View your pattern library
/restack-patterns suggest <scenario>   # Get pattern recommendations for a situation
/restack-patterns effectiveness        # Track which patterns are working
/restack-patterns anti-patterns        # Document what doesn't work in your context
/restack-patterns evolve               # Update patterns based on new learning
```

---

### Evolutionary Architecture Coach (`/restack-evolve`)

> **New in v2:** Owns **brittleness**, which is distinct from vulnerability and interacts with it — a brittle architecture cannot absorb residuals cheaply, so it is what stops the stressor loop converging. Fitness functions are reframed as automated residual validation: residuals erode silently, and one without a check is one you are trusting.

Build the capability to design and maintain architectures that accommodate change gracefully.

```
/restack-evolve assess                 # Assess evolutionary readiness
/restack-evolve fitness-functions      # Define architectural fitness functions
/restack-evolve brittleness            # Identify areas resistant to change
/restack-evolve increment              # Plan safe incremental improvements
/restack-evolve health                 # Track architectural health over time
/restack-evolve coach                  # Guided coaching session
```

**Fitness functions** are automated checks that your architecture still meets its goals — enabling confident change.

---

## Compliance via stressor packs


Compliance is handled through the stressor analysis skill — not a separate checklist process.

**Why?** Every compliance control exists because a real harm occurred. When you understand the harm (not just the control), you design architecture that makes the harm structurally impossible. The residues that emerge from a stressor analysis address compliance requirements *and* protect against unrelated threats simultaneously.

```
/restack-stressor compliance list      # List available compliance packs
/restack-stressor compliance gdpr      # Inject GDPR stressor pack
/restack-stressor walk                 # Walk paths under the compliance stressors
/restack-stressor analyze              # Build impact matrix
/restack-stressor residues             # Residuals naturally address compliance controls
/restack-adr create [document residuals as architectural decisions]
```

**Available packs:** See `skills/restack-stressor/compliance-packs/` — contributions welcome.

---

## Workflow examples


### Brownfield / Existing Environment (Before Any Design)

```
/restack-discover paths                # map what's actually there
/restack-discover actor <critical>     # investigate opaque or critical actors
/restack-discover intentions           # trace primary intentions end-to-end
/restack-discover gaps                 # prioritise what's still unknown
/restack-discover organisation         # translate resistance into stressors
/restack-discover confidence           # explicit go/no-go for proceeding
/restack-stressor walk                 # walk discovered paths
/restack-stressor generate             # include organisational stressors
/restack-stressor analyze              # build matrix on real paths
/restack-stressor residues             # residuals address real vulnerabilities
/restack-adr create [key discoveries and decisions]
```

### New Project (45-60 min)

```
/restack-tech-stack recommend
/restack-adr create [for each major technology decision]
/restack-solution-doc hld
/restack-stressor walk                 # walk primary paths — map actors and intentions
/restack-stressor generate             # generate diverse stressors
/restack-stressor analyze              # build impact matrix
/restack-stressor residues             # identify residuals
/restack-design-review architecture
/restack-cloud design <system>         # if cloud-hosted
/restack-cloud dr                      # define DR upfront
/restack-solution-doc deployment
```

### Pre-Production Review (20-30 min)

```
/restack-design-review complete
/restack-design-review security        # if security was flagged
/restack-design-review performance     # if performance was flagged
/restack-capacity estimate             # validate sizing
/restack-capacity load-test            # get load testing plan
/restack-solution-doc complete
```

### Cloud Migration (30-45 min)

```
/restack-cloud migrate to AWS          # 6 R's disposition for each workload
/restack-cloud design <target>         # target architecture
/restack-cloud review                  # Well-Architected gaps
/restack-cloud iac terraform           # generate IaC
/restack-adr create [key decisions]
/restack-cloud dr                      # DR strategy
/restack-cloud cost                    # cost optimisation
```

### Quarterly Team Review

```
/restack-capability-assessor assess    # re-assess maturity
/restack-capability-assessor roadmap   # next quarter plan
/restack-arch-learning retrospective   # what worked, what didn't
/restack-patterns evolve               # update pattern library
/restack-evolve assess                 # evolutionary health
```

### Compliance-Driven Design

```
/restack-stressor compliance gdpr      # inject regulatory stressors
/restack-stressor walk                 # walk paths under compliance stressors
/restack-stressor analyze              # build impact matrix
/restack-stressor residues             # residuals address compliance structurally
/restack-adr create [document residuals]
```

---

## Tips


### For Architects
- Walk paths during design, not just after — it shapes better decisions from the start
- Create ADRs for decisions *not* to do something — those are often the most important
- Iterate stressor analysis after adding residuals to measure improvement — watch vulnerability scores drop

### For Teams
- Run stressor workshops collaboratively — shared mental models are the output, not just the matrix
- Assess capability before building roadmaps — you need a baseline
- Review ADR outcomes quarterly to build genuine institutional learning

### For Organisations
- Treat the pattern library as a living document — evolve it from real outcomes
- Compliance packs make regulatory requirements visible in your standard process
- Cloud and capacity decisions should be made together — architecture shapes cost

---

For all commands at a glance, see [Quick Reference](../QUICKREF.md).
