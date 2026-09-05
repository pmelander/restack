# Usage Guide

Detailed examples and best practices for ReStack.

## Table of Contents

1. [Phase 1: Individual Capabilities](#phase-1-individual-capabilities)
2. [Phase 2: Organisational Capabilities](#phase-2-organisational-capabilities)
3. [Phase 3: Specialised Tools](#phase-3-specialised-tools)
4. [Compliance via Stressor Packs](#compliance-via-stressor-packs)
5. [Workflow Examples](#workflow-examples)

---

## Phase 1: Individual Capabilities

### Architecture Decision Records (`/adr`)

Create and manage Architecture Decision Records — the foundation of traceable, principled architecture.

```
/adr create Choose PostgreSQL for primary database

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

### Solution Documentation (`/solution-doc`)

Generate comprehensive technical documentation from your architecture.

```
/solution-doc hld          # High-Level Design → docs/architecture/HLD.md
/solution-doc lld          # Low-Level Design → docs/architecture/LLD-*.md
/solution-doc deployment   # Deployment Guide → docs/deployment/DEPLOYMENT.md
/solution-doc runbook      # Operations Runbook → docs/operations/RUNBOOK.md
/solution-doc complete     # All of the above
```

---

### Technology Stack Advisor (`/tech-stack`)

Evaluate and select technologies with context-aware, bias-free analysis.

```
/tech-stack recommend                      # Full stack for your context
/tech-stack compare React vs Vue           # Side-by-side comparison
/tech-stack evaluate Kubernetes            # Assess fit for your situation
/tech-stack migrate from MySQL to Postgres # Migration analysis
```

**Best practice:** Always follow a tech decision with `/adr create` to document it.

---

### Design Review (`/design-review`)

Multi-dimensional architecture review with scored assessment.

```
/design-review complete      # Full review across 8 dimensions
/design-review security      # Security-focused
/design-review performance   # Performance-focused
/design-review api           # API design review
/design-review data          # Data architecture review
```

**Scorecard:**
- 🟢 Strong (8-10) — meets or exceeds standards
- 🟡 Adequate (5-7) — acceptable but has issues
- 🔴 Needs Improvement (0-4) — must be addressed

---

### Stressor Analysis (`/stressor`)

Walk your system's paths and stress-test each actor to build antifragile systems grounded in Residuality Theory.

**Core vocabulary:**
- **Actor** — any user, application, or module that acts on an intention
- **Intention** — the signal that connects actors and drives flow through the system
- **Path** — a sequence of actors connected by intentions (never forks — forks create new paths)
- **Walk** — traversing a path to evaluate each actor's behaviour as intentions propagate
- **Residual** — a new actor, intention, or path introduced in response to a stressor

```
/stressor walk checkout        # Walk the checkout path — map actors, intentions, stateful/stateless
/stressor generate 30          # Generate 30 diverse stressors (including absurd ones)
/stressor analyze              # Build impact matrix with actors as columns
/stressor vulnerabilities      # Identify most-impacted actors across all paths
/stressor residues             # Suggest residuals — new actors, intentions, or paths
/stressor iterate              # Re-walk after adding residuals, measure improvement
/stressor workshop             # Facilitate team stressor workshop
/stressor import data.xlsx     # Import existing stressor matrix
```

**The right sequence:** Walk paths first → generate stressors → walk under stress → build matrix → identify vulnerabilities → add residuals → re-walk.

**Why walk before generate?** The impact matrix columns are the actors on your paths. Walking first ensures the matrix reflects how intentions actually flow — not an arbitrary component list. Actors later in a path are often more vulnerable because they depend on everything upstream.

**Why include absurd stressors?** Fire-breathing lizards and zombie apocalypses represent *unknown unknowns*. If your architecture can't conceptually handle the absurd, it probably can't handle real surprises. 🐉

**The compound effect:** A single residual — say, an async queue actor added between two services — protects against load spikes, downstream failures, traffic bursts, and more. Residuals compound across iterations.

---

## Phase 2: Organisational Capabilities

### Architecture Learning Analyzer (`/arch-learning`)

Build systematic organisational learning from your architectural history.

```
/arch-learning analyze       # Analyze all ADRs for patterns and outcomes
/arch-learning patterns      # Extract recurring decision patterns
/arch-learning outcomes      # Review how past decisions played out
/arch-learning retrospective # Facilitate team architecture retrospective
/arch-learning lessons       # Generate lessons learned report
/arch-learning trends        # Identify trends in decision-making over time
```

**Use on a cadence:** Run quarterly to build institutional knowledge that outlasts individual team members.

---

### Team Capability Assessor (`/capability-assessor`)

Assess and grow team architectural maturity across 6 dimensions.

```
/capability-assessor assess    # Current maturity across 6 dimensions
/capability-assessor gaps      # Highest-priority improvement areas
/capability-assessor roadmap   # 3-6 month development plan
/capability-assessor track     # Progress since last assessment
/capability-assessor exercises # Concrete capability-building activities
/capability-assessor compare   # Benchmark against maturity model
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

### Pattern Extractor (`/patterns`)

Extract architectural patterns from your accumulated knowledge and institutionalise them.

```
/patterns extract              # Extract patterns from ADRs, codebase, decisions
/patterns catalog              # View your pattern library
/patterns suggest <scenario>   # Get pattern recommendations for a situation
/patterns effectiveness        # Track which patterns are working
/patterns anti-patterns        # Document what doesn't work in your context
/patterns evolve               # Update patterns based on new learning
```

---

### Evolutionary Architecture Coach (`/evolve`)

Build the capability to design and maintain architectures that accommodate change gracefully.

```
/evolve assess                 # Assess evolutionary readiness
/evolve fitness-functions      # Define architectural fitness functions
/evolve brittleness            # Identify areas resistant to change
/evolve increment              # Plan safe incremental improvements
/evolve health                 # Track architectural health over time
/evolve coach                  # Guided coaching session
```

**Fitness functions** are automated checks that your architecture still meets its goals — enabling confident change.

---

## Phase 3: Specialised Tools

### Architect's Journey (`/journey`)

The orchestrating skill — knows which tools to use, when, and in what sequence. Start here when beginning a new engagement, or when you're mid-journey and unsure what comes next.

```
/journey start           # assess terrain (greenfield/brownfield/minefield), map the route
/journey where           # where am I? what have I done? what comes next?
/journey iterate         # is stressor impact low enough to proceed, or iterate again?
/journey review          # health check — what's been skipped, what's at risk?
/journey cadence         # establish an ongoing rhythm for a live system
```

**The three terrains:**
- **Greenfield** — blank canvas, design your paths then walk them
- **Brownfield** — existing system, discover then walk
- **Minefield** — high fragility and complexity, discover extensively before touching anything

**The stressor iteration loop** — the heartbeat of every journey:
```
walk → generate → analyze → residuals → implement → re-walk → is impact low enough? → loop or proceed
```

Iterate until impact is *sufficiently low* — not zero, but low enough given the system's aspiration and the cost of further improvement. `/journey iterate` helps you make that judgment explicitly.

---

### Environment Discovery (`/discover`)

Map what actually exists in an existing environment before designing anything new within it. Brownfield, oilfield, and minefield environments rarely match their documentation — discovery produces the confident path maps that feed stressor analysis.

**Discovery walks are different from design walks:**
- In design walks you validate what you designed
- In discovery walks you build your understanding from scratch
- Confidence is earned, not assumed

```
/discover paths                  # map entry points and trace paths forward
/discover actor "Payment Service" # what does it actually do — not what docs say
/discover intentions             # trace how a specific intention propagates
/discover gaps                   # prioritise what you still don't know
/discover organisation           # map resistance patterns as stressors
/discover confidence             # are you ready to hand off to /stressor walk?
```

**Done condition:** You are confident that paths are correct and you know the intention of each actor. Not certainty — confidence. There's a difference.

**Organisational resistance as stressors:** A product owner who cannot get budget, an EA who blocks vendor choices, a team that resists integration — these are stressors on the architecture, not actors on paths. `/discover organisation` translates them into the stressor list where they belong.

**Feeds directly into:**
```
/discover confidence → /stressor walk → /stressor generate → /stressor analyze
```

---

## Phase 3: Specialised Tools

### Cloud Architect (`/cloud`)

Design cloud-native architectures, generate IaC, and build Well-Architected thinking.

```
/cloud design "e-commerce platform, 10k concurrent users, 99.9% SLA"
/cloud iac terraform           # Generate Terraform for the design
/cloud iac cloudformation      # Or CloudFormation
/cloud review                  # Well-Architected review across all 6 pillars
/cloud cost                    # Cost analysis and optimisation
/cloud migrate to AWS          # Migration strategy using the 6 R's
/cloud dr                      # Disaster recovery strategy (RTO/RPO → tier)
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

### Capacity Planner (`/capacity`)

Estimate resource requirements, design scaling strategies, and validate with load testing.

```
/capacity estimate             # Back-of-envelope resource estimation
/capacity scale horizontal     # Design horizontal scaling approach
/capacity scale database       # Database scaling strategy
/capacity scale auto           # Auto-scaling design
/capacity bottleneck           # Identify where constraints will appear first
/capacity load-test            # Load testing strategy (baseline, load, spike, soak, stress)
/capacity forecast             # Model growth across 3/6/12/24-month horizons
/capacity right-size           # Identify and eliminate over-provisioning
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

## Compliance via Stressor Packs

Compliance is handled through the stressor analysis skill — not a separate checklist process.

**Why?** Every compliance control exists because a real harm occurred. When you understand the harm (not just the control), you design architecture that makes the harm structurally impossible. The residues that emerge from a stressor analysis address compliance requirements *and* protect against unrelated threats simultaneously.

```
/stressor compliance list      # List available compliance packs
/stressor compliance gdpr      # Inject GDPR stressor pack
/stressor walk                 # Walk paths under the compliance stressors
/stressor analyze              # Build impact matrix
/stressor residues             # Residuals naturally address compliance controls
/adr create [document residuals as architectural decisions]
```

**Available packs:** See `skills/stressor/compliance-packs/` — contributions welcome.

---

## Workflow Examples

### Brownfield / Existing Environment (Before Any Design)

```
/discover paths                # map what's actually there
/discover actor <critical>     # investigate opaque or critical actors
/discover intentions           # trace primary intentions end-to-end
/discover gaps                 # prioritise what's still unknown
/discover organisation         # translate resistance into stressors
/discover confidence           # explicit go/no-go for proceeding
/stressor walk                 # walk discovered paths
/stressor generate             # include organisational stressors
/stressor analyze              # build matrix on real paths
/stressor residues             # residuals address real vulnerabilities
/adr create [key discoveries and decisions]
```

### New Project (45-60 min)

```
/tech-stack recommend
/adr create [for each major technology decision]
/solution-doc hld
/stressor walk                 # walk primary paths — map actors and intentions
/stressor generate             # generate diverse stressors
/stressor analyze              # build impact matrix
/stressor residues             # identify residuals
/design-review architecture
/cloud design <system>         # if cloud-hosted
/cloud dr                      # define DR upfront
/solution-doc deployment
```

### Pre-Production Review (20-30 min)

```
/design-review complete
/design-review security        # if security was flagged
/design-review performance     # if performance was flagged
/capacity estimate             # validate sizing
/capacity load-test            # get load testing plan
/solution-doc complete
```

### Cloud Migration (30-45 min)

```
/cloud migrate to AWS          # 6 R's disposition for each workload
/cloud design <target>         # target architecture
/cloud review                  # Well-Architected gaps
/cloud iac terraform           # generate IaC
/adr create [key decisions]
/cloud dr                      # DR strategy
/cloud cost                    # cost optimisation
```

### Quarterly Team Review

```
/capability-assessor assess    # re-assess maturity
/capability-assessor roadmap   # next quarter plan
/arch-learning retrospective   # what worked, what didn't
/patterns evolve               # update pattern library
/evolve assess                 # evolutionary health
```

### Compliance-Driven Design

```
/stressor compliance gdpr      # inject regulatory stressors
/stressor walk                 # walk paths under compliance stressors
/stressor analyze              # build impact matrix
/stressor residues             # residuals address compliance structurally
/adr create [document residuals]
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
