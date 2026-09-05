# ADR-005: Add Architecture Learning Analyzer (Phase 2 Skill #1)

**Status:** Accepted

**Date:** 2026-05-18

**Deciders:** Solution Architect Team

**Technical Story:** Beginning Phase 2 development with organizational learning capabilities

**Implementation Status:** implemented

**Implemented Date:** 2026-05-18

**Implemented By:** Solution Architect Team

**Review Date:** 2026-11-18

## Context

After completing Phase 1 (5 capability-building skills) and establishing the Utilities category (Excel reader), we're ready to begin Phase 2: **Organizational Capabilities**.

**Phase 1 Success:**
- Built individual architect capabilities (decision-making, systems thinking, evaluation, self-review, antifragility)
- Established residuality principles (tools build lasting capabilities)
- Created rich architectural artifacts (ADRs, docs, stressor matrices)
- All skills designed with reflection prompts, learning capture, capability rubrics

**The Gap:**
Phase 1 builds individual capabilities. But organizations need **team-level and organizational-level meta-capabilities**:
- How do teams learn from their architectural history?
- How do patterns get recognized and institutionalized?
- How do decisions get better over time?
- How does knowledge persist beyond individuals?

**Current State of ADRs:**
We have 4 ADRs (including this one), rich with:
- Metadata (Status, Date, Deciders)
- Sections (Context, Decision, Consequences, Alternatives)
- Success Metrics, Risks, Next Actions
- Cross-references to other ADRs

**What's Missing:**
- No systematic way to learn from these decisions
- No tracking of "what actually happened" after implementation
- No pattern extraction across decisions
- No organizational retrospectives or lessons learned
- No feedback loop from outcomes to future decisions

**Why Start with Learning Analyzer:**
- Foundation for organizational learning
- Uses existing Phase 1 artifacts (ADRs already created)
- Enables systematic learning from history
- Other Phase 2 skills can build on its capabilities

## Decision

We will **create Architecture Learning Analyzer as Phase 2's first skill**, and **extend the ADR template to support outcome tracking**.

**What We're Building:**

### 1. Enhanced ADR Template
Add to `templates/adr-template.md`:

**New Metadata Fields:**
- `Implementation Status` - [not-started | in-progress | implemented | abandoned]
- `Implemented Date` - When decision was actually implemented
- `Implemented By` - Team/person responsible
- `Review Date` - When to conduct post-implementation review (3-6 months after)

**New Section: Outcome (Post-Implementation Review)**
```markdown
## Outcome (Post-Implementation Review)
- Baseline Metrics (before)
- Collected Metrics (after)
- What Worked
- What Didn't Work
- Surprises
- Lessons Learned
- Follow-up Actions
```

### 2. Architecture Learning Analyzer Skill
Create `skills/phase-2/arch-learning.md` with 6 commands:

- `/restack-arch-learning analyze` - Analyze all ADRs, extract patterns, show timeline
- `/restack-arch-learning patterns` - Extract and catalog recurring patterns
- `/restack-arch-learning outcomes` - Review and track decision outcomes
- `/restack-arch-learning retrospective` - Facilitate team retrospective
- `/restack-arch-learning lessons` - Generate lessons learned report
- `/restack-arch-learning trends` - Identify trends over time

**Follows Phase 1 patterns:**
- Capability Being Built section
- Reflection prompts at each stage
- Learning capture template
- Capability rubric (Novice → Expert)
- Integration with Phase 1 skills
- Output conventions (docs/arch-learning/)

**Capability Being Built:**
- Organizational learning
- Pattern recognition
- Feedback loop creation
- Knowledge compounding
- Historical context awareness
- Continuous improvement mindset

**Residuality Goal:** Organizations that systematically learn from architectural decisions and build institutional knowledge that persists beyond individual architects.

## Consequences

### Positive

**For Organizations:**
- **Systematic learning** from architectural history
- **Pattern recognition** across decisions and projects
- **Feedback loops** that improve decision-making over time
- **Institutional memory** that persists beyond individuals
- **Compound wisdom** - each analysis adds to collective knowledge
- **Better decisions** - informed by past successes and failures

**For Teams:**
- **Shared understanding** of architectural evolution
- **Collective learning** through retrospectives
- **Pattern library** specific to their context
- **Reduced repeated mistakes** - learn from history
- **Faster onboarding** - new architects learn from past decisions
- **Evidence-based** decision-making

**For Phase 2:**
- **Foundation established** for organizational capabilities
- **Pattern validated** for remaining Phase 2 skills
- **Clear distinction** between individual (Phase 1) and organizational (Phase 2) capabilities
- **Outcome tracking infrastructure** supports all future learning

**For ADRs:**
- **Richer data** - implementation status and outcomes tracked
- **Accountability** - know when to review decisions
- **Learning loop** - capture what actually happened
- **Value validated** - ADRs prove their worth through outcome tracking

### Negative

**Complexity:**
- ADR template more complex (8 metadata fields instead of 4)
- Outcome section requires discipline to fill out
- Six new commands to learn
- More artifacts to maintain (analysis reports, pattern catalog, etc.)

**Discipline Required:**
- Must schedule and conduct outcome reviews
- Must facilitate retrospectives regularly
- Must keep pattern catalog updated
- Must be honest about failures (psychological safety needed)

**Time Investment:**
- Outcome reviews take time
- Retrospectives require team participation
- Pattern extraction requires analysis
- Learning requires ongoing practice

**Adoption Risk:**
- Teams may not see value immediately
- Requires cultural shift (learning from failure)
- May feel like "extra work" initially
- Success depends on regular practice

**Data Quality Risk:**
- Garbage in, garbage out
- If outcomes aren't honest, learning is shallow
- If reviews are skipped, feedback loop breaks
- If patterns aren't validated, catalog becomes noise

### Neutral

- First Phase 2 skill (establishes pattern for remaining 3)
- Extends ADR template (backward compatible - old ADRs still valid)
- Creates new output directory (docs/arch-learning/)
- Longest skill file so far (~600 lines)
- No new dependencies (pure skill, no helpers)

## Alternatives Considered

### Alternative 1: Start with Team Capability Assessor
**What:** Begin Phase 2 with capability assessment instead of learning analyzer

**Pros:**
- Helps teams understand current maturity
- Clear before/after measurements
- Immediate value (know where you are)

**Cons:**
- Assessing without learning foundation is shallow
- Need historical data to assess properly
- Learning Analyzer provides that foundation
- Teams want to learn, not just be measured

**Why rejected:** Learning is more fundamental than assessment. Build learning capability first, then assess it. Assessment without learning is just measurement without improvement.

### Alternative 2: Simpler Outcome Tracking
**What:** Just add "Outcome" section to ADR template, skip full skill

**Pros:**
- Simpler, less to learn
- Lower barrier to adoption
- Still captures outcomes

**Cons:**
- No systematic analysis (manual work)
- No pattern extraction (insights lost)
- No retrospectives (team doesn't learn together)
- No trend identification (miss the big picture)
- Misses the "organizational learning" capability entirely

**Why rejected:** Template changes alone don't build learning capability. The skill guides the practice, facilitates workshops, extracts patterns, and builds the learning habit. Template + skill = capability.

### Alternative 3: Build All Phase 2 in Parallel
**What:** Create all 4 Phase 2 skills simultaneously as MVPs

**Pros:**
- See full Phase 2 picture quickly
- Can test integration between skills
- Faster to "done"

**Cons:**
- Spreads effort thin (4 skills at once)
- Can't validate pattern before expanding
- Harder to refine based on feedback
- Quality may suffer

**Why rejected:** User chose sequential development. Better to perfect one skill, validate the approach, then apply learnings to remaining 3 skills. Quality over speed.

### Alternative 4: Helper Script for Analysis
**What:** Create Python helper (`helpers/analyze_adrs.py`) to parse ADRs and extract data

**Pros:**
- Automated data extraction
- Consistent parsing
- Easier pattern identification
- Could power a dashboard

**Cons:**
- Additional complexity
- Another thing to maintain
- May not be needed initially
- Can add later if needed

**Why rejected:** Defer helper script to later. Start with skill guiding manual analysis. If demand emerges for automation, add helper in future iteration. YAGNI principle.

## Implementation Details

### Files Created
- `skills/phase-2/arch-learning.md` - Full skill specification
- `docs/arch-learning/` - Output directory for learning artifacts
- `docs/adr/ADR-005-add-architecture-learning-analyzer.md` - This ADR

### Files Modified
- `templates/adr-template.md` - Added outcome tracking fields

### Commands Added
Six new commands, all under `/restack-arch-learning`:
- `analyze` - Comprehensive ADR analysis
- `patterns` - Pattern catalog extraction
- `outcomes` - Outcome review and tracking
- `retrospective` - Team retrospective facilitation
- `lessons` - Lessons learned aggregation
- `trends` - Trend analysis over time

### Capability Maturity Levels
Defined 4 levels of organizational learning maturity:
- **Novice** - Ad-hoc learning, informal, not documented
- **Competent** - Aware, tracks some outcomes, occasional retros
- **Proficient** - Systematic, regular reviews, rich pattern library
- **Expert** - Continuous, automatic, living knowledge, natural compounding

### Integration Points
- **ADR**: Create ADR → Implement → Review outcomes → Extract lessons
- **Stressor Analysis**: Analyze resilience patterns, track residue effectiveness
- **Design Review**: Compare findings to past learnings
- **Tech Stack**: Technology decisions inform pattern library

## Success Metrics

**Capability Metrics:**
- Organizations conduct regular outcome reviews (quarterly)
- Pattern catalogs actively used in decision-making
- Team retrospectives lead to concrete improvements
- Architectural decisions reference past learnings
- Knowledge persists through team changes

**Usage Metrics:**
- `/restack-arch-learning` commands used regularly
- Outcome sections completed within review period
- Pattern catalog grows and stays current
- Retrospectives attended by team
- Lessons learned referenced in new ADRs

**Quality Metrics:**
- Decision quality improves over time
- Fewer repeated mistakes
- Better outcome predictions (baseline vs actual)
- Faster new architect onboarding
- Measurable architectural improvement

**Residuality Metrics:**
- Tool Independence Score approaches 1.0
- Teams naturally discuss patterns without prompting
- Outcomes tracked without reminders
- Learning happens organically in team discussions
- Architectural wisdom compounds visibly

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Teams don't fill out outcomes | High | High | Set calendar reminders, make reviews part of retro, lead by example |
| Blame culture prevents honest learning | High | Medium | Emphasize psychological safety, focus on learning not blame |
| Outcome reviews skipped | High | Medium | Assign ownership, integrate into team rhythm, celebrate completion |
| Pattern catalog becomes stale | Medium | Medium | Quarterly reviews, version control, team ownership |
| Too much ceremony, low ROI perception | Medium | Medium | Start small (just outcomes), show value, expand gradually |
| Data quality poor (dishonest outcomes) | High | Low | Build trust, normalize failure as learning, model honesty |

## Implementation Strategy

### Phase 1: Foundation (Complete)
1. ✅ Extend ADR template with outcome tracking
2. ✅ Create arch-learning.md skill file
3. ✅ Create docs/arch-learning/ output directory
4. ✅ Document decision in ADR-005

### Phase 2: Documentation (Next)
1. Update README.md (Phase 2 section)
2. Update ROADMAP.md (mark Learning Analyzer ✅)
3. Update QUICKREF.md (arch-learning commands)
4. Update GETTING_STARTED.md (Phase 2 example)
5. Update CLAUDE.md (Phase 2 usage)

### Phase 3: Validation (Future)
1. Apply to existing ADRs (fill outcomes for ADR-001 through ADR-005)
2. Run `/restack-arch-learning analyze` on toolkit's own ADRs
3. Extract patterns from toolkit development
4. Conduct retrospective on Phase 1
5. Refine based on dogfooding

### Phase 4: Expansion (Q3-Q4 2026)
1. Build remaining Phase 2 skills (Capability Assessor, Pattern Extractor, Evolutionary Coach)
2. Optional: Add analyze_adrs.py helper if demand emerges
3. Optional: Create pattern library visualization

## Open Questions

- [ ] Should we mandate outcome reviews or make them optional? → Start optional, build habit
- [ ] How long should Review Date be after implementation? → 3-6 months typical, flexible
- [ ] Should patterns have a formal structure or stay freeform? → Start freeform, formalize if needed
- [ ] Do we need a helper script for parsing? → Defer, add if value is clear

## Next Actions

1. ✅ Create arch-learning.md skill
2. ✅ Extend ADR template
3. ✅ Create ADR-005
4. 📋 Update all documentation (README, ROADMAP, QUICKREF, GETTING_STARTED, CLAUDE.md)
5. 📋 Commit with message: `feat(phase-2): Add Architecture Learning Analyzer`
6. 📋 Dogfood: Apply to toolkit's own ADRs
7. 📋 Begin building remaining Phase 2 skills

---

**This ADR marks the beginning of Phase 2.** We're shifting from building individual architect capabilities (Phase 1) to building organizational meta-capabilities that enable continuous learning and improvement.

**The Vision:** Organizations that learn systematically from their architectural history, compound knowledge over time, and make progressively better decisions - not because individuals are perfect, but because the organization captures and shares wisdom.

**Remember:** Learning is a practice, not an event. Organizations that learn faster than they forget will always have architectural advantage.

