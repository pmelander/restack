# ReStack - Roadmap

## Overview

This roadmap outlines the planned development of ReStack across three phases, designed to progressively enhance Solution Architect capabilities with Claude Code.

## Status Legend

- ✅ Complete
- 🔄 In Progress
- 📋 Planned
- 💡 Under Consideration

---

## Phase 1: Immediate Impact ✅

**Goal:** Build individual architect capabilities through residuality-focused skills.

**Status:** ✅ Complete (2026-05-17)

### Completed Skills

| Skill | Status | Description |
|-------|--------|-------------|
| Architecture Decision Records | ✅ | Build decision-making capability through structured ADRs |
| Solution Documentation Generator | ✅ | Build systems thinking and communication capability |
| Technology Stack Advisor | ✅ | Build strategic thinking and evaluation capability |
| Design Review | ✅ | Build self-assessment and pattern recognition capability |
| Stressor Analysis | ✅ | Build antifragility thinking and resilience capability |

### Deliverables ✅

- [x] Five capability-building skills implemented
- [x] Refactored with residuality principles (reflection prompts, learning capture)
- [x] Document templates (ADR, HLD, tech comparison, stressor matrix)
- [x] Example documents (including banking stressor analysis)
- [x] Installation guide
- [x] Usage documentation
- [x] Quick reference guide
- [x] Contributing guidelines
- [x] Three ADRs documenting strategic decisions

### Impact

Phase 1 provides Solution Architects with:
- **Decision-making capability** - Make better architectural decisions independently
- **Systems thinking** - Naturally think in components, interactions, trade-offs
- **Evaluation capability** - Assess technologies without hype or bias
- **Self-review capability** - Spot issues before external review
- **Antifragility thinking** - Design for unknown unknowns, benefit from stress

**Residuality Success:** Architects use tools less as capabilities transfer. Tool Independence Score approaches 1.0.

---

## Utilities: Infrastructure Skills ✅

**Goal:** Provide infrastructure that enables capability-building skills.

**Status:** ✅ Established (2026-05-17)

| Skill | Status | Description |
|-------|--------|-------------|
| Excel Reader | ✅ | Read Excel/CSV files, import to markdown (bridges Excel → markdown workflows) |

**Philosophy:** Utilities provide tooling, not capability-building. Success = seamless integration and workflow efficiency.

**Future Utilities:**
- 📋 Diagram Generator (convert markdown → diagrams)
- 📋 Template Manager (custom org templates)
- 📋 Doc Search (semantic search across architecture docs)

---

## Phase 2: Organizational Capabilities ✅

**Goal:** Build organizational learning capabilities and team-level architectural thinking that compounds over time.

**Tagline:** "Building teams that build better architecture"

**Target:** Q2 2026

**Status:** ✅ Complete (4 of 4 complete)

**Philosophy Shift:** Phase 1 builds individual architect capabilities. Phase 2 builds **team and organizational meta-capabilities** that enable continuous improvement and learning.

### Skills

#### 1. Architecture Learning Analyzer 🎓 ✅

**Status:** ✅ Complete (2026-05-18)

**Purpose:** Help organizations learn systematically from their architectural history and decisions.

**Capability Being Built:**
- Organizational learning from past decisions
- Pattern recognition across projects
- Feedback loop creation
- Knowledge compounding

**What It Does:**
- Analyzes past ADRs and outcomes
- Identifies patterns in successful vs failed decisions
- Extracts learnings from architectural evolution
- Creates organizational pattern library
- Tracks decision outcomes over time
- Generates "What We've Learned" reports
- Facilitates team retrospectives

**Commands:**
```bash
/restack-arch-learning analyze          # Analyze architectural decision history
/restack-arch-learning patterns         # Extract patterns from decisions
/restack-arch-learning outcomes         # Review decision outcomes
/restack-arch-learning retrospective    # Guided architectural retrospective
/restack-arch-learning lessons          # Generate lessons learned
/restack-arch-learning trends           # Identify trends in decisions
```

**Enhancements:**
- Extended ADR template with outcome tracking (Implementation Status, Review Date, Outcome section)
- Learning capture template for session notes
- Capability rubric (Novice → Expert)
- Integration with Phase 1 skills

**Residuality Goal:** Organizations that systematically learn from decisions and build institutional knowledge that persists beyond individual architects.

---

#### 2. Team Capability Assessor 📊 ✅

**Status:** ✅ Complete (2026-05-18)

**Purpose:** Assess and develop team architectural capability maturity systematically.

**Capability Being Built:**
- Self-awareness of capability levels
- Growth mindset and continuous improvement
- Targeted skill development
- Team-level architectural excellence

**What It Does:**
- Assesses team architectural maturity across 6 dimensions
- Identifies capability gaps and strengths
- Creates development roadmaps for teams
- Tracks capability growth over time
- Suggests learning paths and exercises
- Facilitates team architectural skill-building

**Commands:**
```bash
/team-capability assess         # Assess team capability maturity
/team-capability gaps           # Identify capability gaps
/team-capability roadmap        # Generate development roadmap
/team-capability track          # Track growth over time
/team-capability exercises      # Suggest capability-building exercises
/team-capability compare        # Compare against benchmarks
```

**Capability Dimensions:**
1. Decision-Making Quality
2. Documentation Clarity
3. Technology Evaluation
4. Design Quality
5. Evolutionary Thinking
6. Learning Culture

**Maturity Levels:** Ad-hoc → Aware → Defined → Managed → Optimizing

**Residuality Goal:** Teams that continuously assess and improve their architectural capabilities, creating a culture of growth and excellence.

---

#### 3. Pattern Extractor & Institutionalizer 🧩 ✅

**Status:** ✅ Complete (2026-05-18)

**Purpose:** Extract architectural patterns from accumulated knowledge and institutionalize them.

**Capability Being Built:**
- Pattern recognition across projects
- Knowledge codification
- Institutional memory
- Context-aware guidance

**What It Does:**
- Analyzes codebase, decisions, and documentation
- Extracts recurring architectural patterns
- Documents organization-specific patterns and anti-patterns
- Creates pattern catalog with context and trade-offs
- Suggests patterns for new situations
- Tracks pattern effectiveness over time

**Commands:**
```bash
/restack-patterns extract               # Extract patterns from codebase/decisions
/restack-patterns catalog               # View pattern catalog
/restack-patterns suggest <scenario>    # Suggest patterns for situation
/restack-patterns effectiveness         # Track pattern success
/restack-patterns anti-patterns         # Document what doesn't work
/restack-patterns evolve                # Update patterns based on learning
```

**Pattern Types:**
- Architectural Patterns (system design)
- Decision Patterns (how you decide)
- Technology Patterns (what works for you)
- Anti-Patterns (what to avoid)
- Context Patterns (when each applies)

**Residuality Goal:** Organizations with rich, context-specific pattern libraries that represent accumulated wisdom and guide future decisions.

---

#### 4. Evolutionary Architecture Coach 🔄 ✅

**Status:** ✅ Complete (2026-05-18)

**Purpose:** Build capability to design and maintain evolutionary architectures that accommodate change gracefully.

**Capability Being Built:**
- Design for change mindset
- Fitness function thinking
- Continuous architecture improvement
- Technical agility

**What It Does:**
- Teaches evolutionary architecture principles
- Helps define architectural fitness functions
- Guides incremental architecture improvements
- Identifies brittle areas requiring flexibility
- Suggests refactoring strategies for evolvability
- Tracks architectural health over time

**Commands:**
```bash
/restack-evolve assess                  # Assess evolutionary readiness
/restack-evolve fitness-functions       # Define/review fitness functions
/restack-evolve brittleness             # Identify brittle areas
/restack-evolve increment               # Plan incremental improvements
/restack-evolve health                  # Track architectural health
/restack-evolve coach                   # Guided evolutionary thinking
```

**Key Concepts Taught:**
- Fitness Functions (automated governance)
- Incremental Change (small, safe improvements)
- Reversible Decisions (designing for optionality)
- Architectural Seams (where to allow flexibility)
- Strategic vs Tactical Debt Management

**Residuality Goal:** Teams that naturally design for change and maintain healthy, evolvable architectures without major rewrites.

---

### Phase 2 Timeline

| Quarter | Milestone | Status |
|---------|-----------|--------|
| Q2 2026 | Architecture Learning Analyzer | ✅ Complete |
| Q2 2026 | Team Capability Assessor | ✅ Complete |
| Q2 2026 | Pattern Extractor & Institutionalizer | ✅ Complete |
| Q2 2026 | Evolutionary Architecture Coach | ✅ Complete |
| Q2 2026 | Phase 2 release | ✅ Complete |

### Why This Redesign?

**Old Phase 2 Plan (Tool-Centric):**
- Tech Debt Analyzer - finds issues
- System Mapper - visualizes complexity
- Migration Planner - reduces risk
- API Designer - generates code

**Problem:** Tools that DO FOR you, building dependency rather than capability.

**New Phase 2 Plan (Capability-Centric):**
- Learning Analyzer - builds organizational learning
- Capability Assessor - enables team growth
- Pattern Extractor - institutionalizes knowledge
- Evolutionary Coach - enables continuous improvement

**Advantage:** Builds **meta-capabilities** that enable continuous organizational improvement and learning - true residuality at scale.

### Integration with Phase 1

**Phase 1:** Individual architect capabilities (decision-making, documentation, evaluation, review)  
**Phase 2:** Organizational capabilities (learning, improvement, pattern recognition, evolution)

**Together:** Individual excellence + organizational learning = compounding value over time.

### Success Metrics

Phase 2 is successful when:
- Organizations learn systematically from architectural decisions
- Teams self-assess and improve capabilities proactively
- Pattern libraries become central to decision-making
- Architecture evolves incrementally rather than through rewrites
- **Ultimate:** Skills used less because capabilities internalized

---

## Phase 3: Specialized Tools 💡

**Goal:** Provide specialized tools for specific domains and advanced scenarios.

**Target:** Q1-Q2 2027

**Status:** ✅ Complete (3 of 3 complete)

> **Note:** Risk Assessor was removed from Phase 3. Traditional risk management (probability × impact matrices, risk registers) conflicts with the toolkit's Residuality Theory foundation. Antifragile design via `/restack-stressor` is a superset of risk assessment — it covers known and unknown threats. See [ADR-006](docs/adr/ADR-006-exclude-risk-assessor-skill.md) for full rationale.
>
> Compliance Checker was replaced by stressor compliance packs. See [ADR-007](docs/adr/ADR-007-compliance-via-stressor-packs.md).
>
> Environment Discovery was added — the most common real-world challenge for architects is not greenfield design but navigating existing environments where paths are unknown and dependencies are fragile.

### Planned Skills

#### 1. Cloud Architect ✅

**Purpose:** Design cloud-native architectures and generate infrastructure as code.

**Capabilities:**
- Design cloud-native architectures (AWS, Azure, GCP)
- Generate Terraform/CloudFormation/Bicep/CDK
- Well-Architected Framework reviews (6 pillars)
- Cost optimization and FinOps thinking
- Migration planning using the 6 R's framework
- Disaster recovery strategy (Backup → Active/Active)

**Commands:**
```bash
/restack-cloud design <architecture>    # Design cloud architecture
/restack-cloud iac <provider>           # Generate IaC templates
/restack-cloud review                   # Well-Architected review
/restack-cloud cost                     # Cost analysis and optimization
/restack-cloud dr                       # Disaster recovery plan
/restack-cloud migrate <to-cloud>       # Cloud migration strategy
```

---

#### ~~2. Compliance Checker~~ — Replaced by Stressor Compliance Packs

> **Replaced by [ADR-007](docs/adr/ADR-007-compliance-via-stressor-packs.md):** A standalone Compliance Checker would train architects to think in checklists, conflicting with Residuality Theory. Instead, compliance frameworks are expressed as **stressor packs** that feed into the existing `/restack-stressor` skill. Compliance becomes a byproduct of antifragile design. The `/restack-stressor compliance <pack>` command and extension point have been added to the Stressor Analysis skill.

---

#### 3. Capacity Planner ✅

**Purpose:** Estimate resource requirements, design scaling strategies, and build capacity thinking capability.

**Capabilities:**
- Back-of-envelope resource estimation from business requirements
- Scaling strategy design (horizontal, vertical, auto, database, cache, CDN)
- Bottleneck identification using Little's Law and utilisation modelling
- Load test strategy design (baseline, load, spike, soak, stress)
- Growth forecasting across conservative / expected / aggressive scenarios
- Right-sizing to eliminate over-provisioning waste

**Commands:**
```bash
/restack-capacity estimate              # Estimate resource requirements
/restack-capacity scale <strategy>      # Design scaling approach
/restack-capacity bottleneck            # Identify capacity constraints
/restack-capacity load-test             # Design load testing strategy
/restack-capacity forecast              # Model future capacity needs
/restack-capacity right-size            # Identify and reduce over-provisioning
```

---

#### 4. Environment Discovery ✅

**Purpose:** Map what actually exists in brownfield, oilfield, and minefield environments before designing any change within them.

**Capabilities:**
- Discovery walking — tracing paths through unknown environments
- Actor investigation — confirming what actors actually do vs. what they're documented to do
- Intention tracing — following signals through a system to find where they degrade or disappear
- Confidence calibration — knowing when you know enough to act
- Organisational stressor mapping — translating resistance patterns into stressors for analysis

**Commands:**
```bash
/restack-discover paths                 # Map paths through an existing system
/restack-discover actor <name>          # Investigate what an actor actually does
/restack-discover intentions            # Trace how an intention propagates
/restack-discover gaps                  # Identify and prioritise confidence gaps
/restack-discover organisation          # Map organisational resistance as stressors
/restack-discover confidence            # Assess readiness to proceed to stressor analysis
```

---

#### 5. Architect's Journey ✅

**Purpose:** Orchestrate the full architectural journey — sequencing skills, managing iteration, and knowing when enough is enough.

**Capabilities:**
- Terrain assessment (greenfield / brownfield / minefield) and route mapping
- Mid-journey positioning — where am I, what comes next, what has been skipped?
- Stressor iteration loop management — explicit iterate vs. proceed decisions
- Journey health checks — completeness and quality assessment
- Ongoing cadence design for live systems

**Commands:**
```bash
/restack-journey start           # Begin a new journey — assess terrain, map the route
/restack-journey where           # Where am I in the journey? What comes next?
/restack-journey iterate         # Should I iterate stressor analysis or proceed?
/restack-journey review          # Journey health check — completeness and quality
/restack-journey cadence         # Establish an ongoing iteration rhythm
```

> **Excluded by [ADR-006](docs/adr/ADR-006-exclude-risk-assessor-skill.md):** Traditional risk assessment contradicts Residuality Theory. The `/restack-stressor` skill (Phase 1) already provides an antifragility-based alternative that is philosophically consistent and architecturally superior.

---

### Phase 3 Timeline

| Quarter | Milestone |
|---------|-----------|
| Q1 2027 | Cloud Architect | ✅ Complete |
| Q1 2027 | Compliance → Stressor Packs extension | ✅ Complete |
| ~~Q1 2027~~ | ~~Compliance Checker~~ | ❌ Replaced (see ADR-007) |
| Q2 2027 | Capacity Planner | ✅ Complete |
| Q2 2027 | Environment Discovery | ✅ Complete |
| Q2 2027 | Architect's Journey | ✅ Complete |
| ~~Q2 2027~~ | ~~Risk Assessor~~ | ❌ Removed (see ADR-006) |
| Q2 2027 | Phase 3 release | ✅ Complete |

---

## Future Considerations 💡

These features are under consideration for future phases:

### Potential Phase 4 Features

1. **Security Architect**
   - Threat modeling
   - Security architecture design
   - Penetration test planning
   - Security policy generation

2. **Performance Optimizer**
   - Performance bottleneck detection
   - Optimization recommendations
   - Benchmark generation
   - Performance testing strategies

3. **Cost Optimizer**
   - Cloud cost analysis
   - Cost reduction strategies
   - Resource rightsizing
   - Reserved instance recommendations

4. **Team Architect**
   - Team topology design (Team Topologies framework)
   - Conway's Law analysis
   - Communication pattern analysis
   - Organizational design

5. **Integration Architect**
   - Integration pattern recommendations
   - ESB design
   - Event-driven architecture
   - Message queue design

6. **Data Architect**
   - Data modeling tools
   - Data governance frameworks
   - Master data management
   - Data lake design

### Integration Possibilities

1. **IDE Integration**
   - VS Code extension
   - IntelliJ plugin
   - Direct code analysis

2. **CI/CD Integration**
   - Automated architecture reviews
   - ADR validation in PR checks
   - Documentation generation in pipeline

3. **Monitoring Integration**
   - Real-time architecture drift detection
   - Automated compliance checking
   - Performance trend analysis

4. **Collaboration Tools**
   - Slack/Teams integration
   - Architecture decision voting
   - Collaborative reviews

---

## Community Feedback

We want your input! Please share:

- **What's working well?** What skills are most valuable?
- **What's missing?** What skills would help you most?
- **Prioritization feedback:** Which Phase 2/3 skills are most important?
- **New ideas:** What other skills should we consider?

### How to Provide Feedback

1. Open an issue with the `feedback` label
2. Participate in discussions
3. Vote on feature requests
4. Share your use cases

---

## Success Metrics

We'll measure success by:

### Phase 1 Metrics ✅
- [x] Skills are installable and usable
- [x] Documentation is comprehensive
- [x] Examples demonstrate value
- [ ] User adoption and feedback (ongoing)

### Phase 2 Metrics 📋
- Skills provide actionable insights
- Reduce time to understand complex systems
- Improve migration success rates
- API quality improvements

### Phase 3 Metrics 💡
- Cost optimization achieved
- Compliance gaps identified and closed
- Resource planning accuracy
- Risk mitigation effectiveness

---

## Contributing to the Roadmap

Want to help shape the future of this toolkit?

1. **Propose new skills:** Open an issue with your idea
2. **Implement Phase 2/3 skills:** See [CONTRIBUTING.md](CONTRIBUTING.md)
3. **Provide use cases:** Share how you'd use these tools
4. **Beta testing:** Volunteer for early testing

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-17 | Initial roadmap with Phase 1 complete, Phase 2 & 3 planned |

---

## Contact

For roadmap questions or suggestions:
- Open an issue
- Start a discussion
- Contact maintainers

**Let's build the best ReStack together!** 🚀
