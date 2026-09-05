# Residuality Measurement Framework

**Version:** 1.0  
**Date:** 2026-05-17  
**Purpose:** Measure persistent value and capability transfer from using ReStack

## Introduction

Traditional software metrics measure outputs (documents created, tasks completed, time saved). Residuality metrics measure **lasting capability** - what persists after the tool is no longer used.

This framework provides concrete ways to measure if the toolkit is building lasting architectural capability in individuals, teams, and organizations.

## Core Residuality Principle

> "Success is measured not by tool usage, but by reduced tool dependency as capabilities internalize."

**The Paradox:** The most successful capability-building tool is one that becomes less necessary over time because users have internalized the capabilities.

---

## Measurement Levels

### Level 1: Individual Architect Capability
Capabilities built in individual Solution Architects

### Level 2: Team Capability
Capabilities built at the team level

### Level 3: Organizational Capability
Capabilities built at the organizational level

---

## Phase 1 Metrics (Individual Capability)

### 1. ADR Skill - Decision-Making Capability

**Baseline Questions:**
- Do you document architectural decisions?
- Do you consider alternatives systematically?
- Do you articulate trade-offs clearly?

**Capability Metrics:**

| Metric | Novice | Competent | Proficient | Expert |
|--------|--------|-----------|------------|--------|
| **Decision Documentation** | Rare or never | Sometimes with prompting | Regularly without prompting | Always, teaches others |
| **Alternative Analysis** | Single option considered | 2-3 alternatives | Multiple with deep analysis | Anticipates alternatives proactively |
| **Trade-off Articulation** | Vague or missing | Basic pros/cons | Nuanced understanding | Strategic trade-off thinking |
| **Outcome Review** | Never reviews | Rarely reviews | Systematically reviews | Creates feedback loops |

**Measurement Methods:**
- **Self-Assessment:** Monthly capability self-rating
- **ADR Quality:** Review ADRs for depth, alternatives, consequences
- **Outcome Tracking:** % of decisions reviewed for outcomes after 3-6 months
- **Tool Independence:** Can make strong decisions without creating ADRs

**Residuality Success Indicator:**
Architect makes well-reasoned decisions with clear trade-offs articulated, even in conversations or informal settings, without needing to create an ADR.

---

### 2. Solution Documentation Skill - Communication Capability

**Baseline Questions:**
- Can you explain complex systems clearly?
- Do you think about multiple audiences?
- Does documentation reveal gaps in your understanding?

**Capability Metrics:**

| Metric | Novice | Competent | Proficient | Expert |
|--------|--------|-----------|------------|--------|
| **Clarity of Thought** | Struggles to articulate | Can explain with effort | Explains clearly | Effortlessly clear |
| **Audience Awareness** | One-size-fits-all | Adjusts somewhat | Tailored to audience | Multi-level communication |
| **Systems Thinking** | Detailed-focused only | Sees components | Holistic view | Abstract and concrete fluently |
| **Operational Awareness** | Design only | Some ops consideration | Ops integrated | Designs with ops in mind |

**Measurement Methods:**
- **Documentation Quality:** Assessed by readers (clear? complete? useful?)
- **Presentation Clarity:** Can explain architecture verbally without docs
- **Design Improvement:** Documentation process reveals design flaws
- **Teaching Ability:** Can teach others architectural thinking

**Residuality Success Indicator:**
Architect naturally thinks with documentation clarity and can explain complex architecture fluently to any audience, with or without formal documentation.

---

### 3. Tech Stack Skill - Strategic Thinking Capability

**Baseline Questions:**
- Do you evaluate technology systematically?
- Do you resist hype and bandwagon thinking?
- Do you consider context over generic "best practices"?

**Capability Metrics:**

| Metric | Novice | Competent | Proficient | Expert |
|--------|--------|-----------|------------|--------|
| **Hype Resistance** | Follows trends | Some skepticism | Critical evaluation | Immune to hype |
| **Context Awareness** | Generic recommendations | Considers basics | Deep context analysis | Context-first thinking |
| **Multi-Dimensional Thinking** | Technical only | Technical + team | All dimensions | Strategic integration |
| **Long-term Thinking** | Initial appeal focus | Some TCO consideration | Total cost of ownership | Strategic alignment |

**Measurement Methods:**
- **Decision Quality:** Technology choices successful 6+ months later?
- **Regret Reduction:** Fewer "we should have chosen X" statements
- **Evaluation Depth:** Comparison matrices show depth of thinking
- **Bias Awareness:** Can articulate own biases in technology selection

**Residuality Success Indicator:**
Architect instinctively thinks "it depends on context" and can quickly evaluate technology choices strategically without formal analysis.

---

### 4. Design Review Skill - Critical Evaluation Capability

**Baseline Questions:**
- Do you review your own designs critically?
- Do you spot issues before others do?
- Do you see patterns across architectures?

**Capability Metrics:**

| Metric | Novice | Competent | Proficient | Expert |
|--------|--------|-----------|------------|--------|
| **Self-Review** | Rarely self-reviews | Basic self-review | Thorough self-review | Harsh self-critic |
| **Pattern Recognition** | Sees individual issues | Recognizes common patterns | Anticipates patterns | Intuitive pattern sense |
| **Multi-Dimensional** | Single-aspect review | Multiple aspects | Holistic evaluation | Integrated thinking |
| **Prevention vs Detection** | Finds issues post-design | Some prevention | Mostly prevents | Designs cleanly first time |

**Measurement Methods:**
- **Self-Review Quality:** Issues caught before external review
- **Review Findings Decline:** External reviews find fewer issues over time
- **Pattern Application:** Uses learned patterns in new designs
- **Teaching**: Can teach others review thinking

**Residuality Success Indicator:**
Architect's designs pass rigorous review with minimal findings because review thinking is automatic during design, not after.

---

## Phase 2 Metrics (Organizational Capability)

### 1. Architecture Learning Analyzer - Organizational Learning

**Capability Metrics:**

| Metric | Ad-hoc | Aware | Defined | Managed | Optimizing |
|--------|--------|-------|---------|---------|------------|
| **Decision Review** | Never | Occasionally | Regular retrospectives | Systematic tracking | Continuous learning |
| **Pattern Recognition** | Repeat mistakes | Some awareness | Patterns documented | Patterns applied | Patterns evolve |
| **Knowledge Sharing** | Siloed | Informal sharing | Documented lessons | Accessible knowledge base | Teaching culture |
| **Improvement** | No change | Reactive fixes | Planned improvements | Data-driven improvement | Continuous evolution |

**Measurement Methods:**
- **Retrospective Frequency:** How often are architectural retrospectives conducted?
- **Lesson Application:** Are lessons from past decisions applied to new ones?
- **Pattern Library Growth:** Is the pattern library actively maintained and used?
- **Mistake Repetition:** Declining rate of repeated architectural mistakes

**Residuality Success Indicator:**
Organization has rich institutional knowledge that new architects inherit, and architectural decisions improve systematically over time.

---

### 2. Team Capability Assessor - Team Growth

**Capability Metrics:**

| Metric | Ad-hoc | Aware | Defined | Managed | Optimizing |
|--------|--------|-------|---------|---------|------------|
| **Self-Awareness** | No assessment | Informal sense | Regular assessment | Tracked metrics | Predictive capability |
| **Development** | Reactive | Some planning | Structured plans | Measured growth | Self-directed growth |
| **Consistency** | Varies widely | Some consistency | Defined standards | Measurable quality | Excellence culture |
| **Collaboration** | Siloed | Some sharing | Team practices | Cross-pollination | Teaching others |

**Measurement Methods:**
- **Capability Assessments:** Regular team capability scoring
- **Growth Tracking:** Improvement in scores over time
- **Consistency Metrics:** Variation in architectural quality decreases
- **Independence:** Team self-assesses and improves without external help

**Residuality Success Indicator:**
Teams proactively assess and improve their architectural capabilities, with declining variation in quality and increasing independence.

---

### 3. Pattern Extractor - Institutional Knowledge

**Capability Metrics:**

| Metric | Ad-hoc | Aware | Defined | Managed | Optimizing |
|--------|--------|-------|---------|---------|------------|
| **Pattern Capture** | None | Informal | Documented | Cataloged | Evolved |
| **Pattern Application** | Start from scratch | Sometimes reference | Regular use | Default approach | Natural application |
| **Context Awareness** | Generic patterns | Some context | Context-specific | Rich context | Pattern evolution |
| **Knowledge Persistence** | Lost with people | Partial retention | Documented | Accessible | Living knowledge |

**Measurement Methods:**
- **Pattern Library Size & Quality:** Growth and refinement over time
- **Pattern Usage:** How often are patterns referenced in new projects?
- **Success Rate:** Do pattern-based decisions succeed more often?
- **Evolution**: Are patterns updated based on outcomes?

**Residuality Success Indicator:**
Organization has rich, context-specific pattern library that guides decisions naturally, and patterns evolve based on learning.

---

### 4. Evolutionary Architecture Coach - Continuous Improvement

**Capability Metrics:**

| Metric | Ad-hoc | Aware | Defined | Managed | Optimizing |
|--------|--------|-------|---------|---------|------------|
| **Change Readiness** | Brittle | Some flexibility | Designed seams | Evolutionary | Graceful evolution |
| **Fitness Functions** | None | Informal | Defined | Automated | Self-healing |
| **Incremental Change** | Big bang changes | Some increments | Regular increments | Continuous | Seamless |
| **Technical Agility** | Slow to change | Reactive | Proactive | Anticipatory | Leading edge |

**Measurement Methods:**
- **Architecture Changes:** Frequency and size of changes (smaller, more frequent = better)
- **Change Impact:** Blast radius of changes (smaller = better)
- **Fitness Function Coverage:** % of architectural concerns governed by fitness functions
- **Rewrite Frequency:** Declining need for major rewrites

**Residuality Success Indicator:**
Architecture evolves incrementally to accommodate business changes without resistance, major rewrites become unnecessary.

---

## Aggregate Residuality Metrics

### Overall Toolkit Success

**Individual Level:**
```
Individual Residuality Score = 
  (ADR Capability + Doc Capability + Tech Stack Capability + Design Review Capability) / 4
```

**Team Level:**
```
Team Residuality Score = 
  (Learning + Capability Growth + Pattern Usage + Evolutionary Readiness) / 4
```

**Organizational Level:**
```
Organizational Residuality Score = 
  Average Team Score × Knowledge Persistence Factor × Improvement Trend
```

### The Ultimate Metric: Tool Independence

**Phase 1:**
```
Independence Score = 
  (Quality of work WITHOUT tool) / (Quality of work WITH tool)
```

**Target:** Approaches 1.0 (same quality with or without tool)

**Phase 2:**
```
Organizational Independence = 
  (Team capability growth rate) / (Tool usage rate)
```

**Target:** Positive and increasing (capability grows faster than tool usage)

---

## Measurement Cadence

### Individual Architects
- **Monthly:** Self-assessment against capability rubrics
- **Quarterly:** Tool usage vs independent capability comparison
- **Semi-Annual:** Deep capability review with examples

### Teams
- **Quarterly:** Team capability assessment
- **Semi-Annual:** Pattern library and learning review
- **Annual:** Comprehensive organizational capability audit

### Organizations
- **Annual:** Full residuality assessment across all levels
- **Multi-Year:** Track long-term trends and compound effects

---

## Data Collection Methods

### Quantitative
- **Tool Usage Metrics:** Frequency of skill invocation
- **Output Quality:** Scored reviews of generated artifacts
- **Time Metrics:** Time to decisions, time to quality output
- **Outcome Tracking:** Success/failure of decisions over time

### Qualitative
- **Self-Assessment:** Capability rubrics
- **Peer Review:** Team member feedback
- **Retrospectives:** Lessons learned sessions
- **Interviews:** Deep capability probing

### Behavioral
- **Observation:** Do architects use learned thinking in daily work?
- **Artifacts**: Quality of work produced without tool assistance
- **Teaching:** Can users teach others? (ultimate capability proof)

---

## Reporting Framework

### Individual Report Card
```markdown
## Architect Capability Report - [Name]

**Assessment Period:** [Dates]

### Phase 1 Capabilities

| Capability | Current Level | Previous | Trend | Target |
|------------|--------------|----------|-------|--------|
| Decision-Making | Proficient | Competent | ↑ | Expert |
| Documentation | Competent | Competent | → | Proficient |
| Tech Evaluation | Expert | Proficient | ↑ | Expert |
| Design Review | Proficient | Proficient | → | Expert |

**Overall Residuality Score:** 3.25/4.0 (Proficient+)

**Independence Indicator:** 0.85 (Good - approaching independence)

### Key Strengths
- [Strengths identified]

### Growth Opportunities
- [Areas for development]

### Recommended Focus
- [Next capability to develop]
```

### Team Report Card
```markdown
## Team Capability Report - [Team Name]

**Assessment Period:** [Dates]

### Phase 2 Capabilities

| Capability | Maturity Level | Previous | Trend |
|------------|---------------|----------|-------|
| Organizational Learning | Managed | Defined | ↑ |
| Team Capability | Defined | Aware | ↑ |
| Pattern Library | Managed | Defined | ↑ |
| Evolutionary Architecture | Defined | Defined | → |

**Overall Team Residuality:** Level 3.25/5.0 (Managed-)

**Capability Growth Rate:** +0.75 levels/quarter

**Tool Independence:** 0.65 (Growing but still dependent)

### Highlights
- [Achievements]

### Focus Areas
- [Improvement opportunities]
```

---

## Success Thresholds

### Individual Architect
- **Novice:** < 1.5 - Needs tool for most tasks
- **Competent:** 1.5-2.5 - Uses tool regularly, some independence
- **Proficient:** 2.5-3.5 - Significant independence, tool enhances
- **Expert:** 3.5-4.0 - Mostly independent, tool optional

**Residuality Achieved:** Expert level (3.5+) maintained without tool usage

### Team
- **Level 1-2:** Ad-hoc to Aware - Tool-dependent
- **Level 3:** Defined - Structured use, building capability
- **Level 4:** Managed - Measured improvement, growing independence
- **Level 5:** Optimizing - Self-sufficient, continuous improvement

**Residuality Achieved:** Level 4+ (Managed or Optimizing)

---

## Long-Term Indicators (2+ Years)

1. **Declining Tool Usage**: As capability builds, need for tool decreases
2. **Increasing Quality**: Architectural quality improves over time
3. **Faster Decisions**: Decision velocity increases as capability grows
4. **Lower Regret**: Fewer "we should have..." statements
5. **Teaching Culture**: Users teach others, spreading capability organically
6. **Pattern Evolution**: Organizational patterns evolve based on learning
7. **Architecture Evolution**: Systems accommodate change gracefully
8. **Independence**: Teams self-assess and improve without external help

---

## Using This Framework

### For Individual Architects
1. Baseline yourself against Phase 1 rubrics
2. Set capability development goals
3. Track monthly progress
4. Measure independence quarterly
5. Aim for expert level across all four capabilities

### For Teams
1. Conduct quarterly team capability assessments
2. Track pattern library growth and usage
3. Measure learning from retrospectives
4. Monitor architectural quality trends
5. Aim for Level 4+ (Managed) maturity

### For Organizations
1. Aggregate team scores
2. Track long-term trends
3. Measure tool independence
4. Document lessons learned
5. Celebrate capability growth, not just tool usage

---

## Conclusion

Residuality measurement shifts focus from **what was produced** to **what persists**. 

**Traditional Success:** "We used the tool 100 times and generated 100 documents"

**Residuality Success:** "We used the tool 20 times, built the capability, and now make great decisions naturally"

The ultimate success: The toolkit becomes less necessary as capabilities internalize, and architectural excellence becomes the norm rather than the exception.

---

**Remember:** If tool usage stays high indefinitely, we've failed to build capability. Success is measured by growing independence coupled with growing quality.
