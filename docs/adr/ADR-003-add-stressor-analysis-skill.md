# ADR-003: Add Stressor Analysis Skill to Phase 1

**Status:** Accepted

**Date:** 2026-05-17

**Deciders:** Solution Architect Team

**Technical Story:** Adding Stressor Analysis technique from Residuality Theory

## Context

After successfully integrating residuality principles into Phase 1 and redesigning Phase 2 for organizational capability building, we discovered another powerful concept from Barry O'Reilly's Residuality Theory: **Stressor Analysis**.

**What is Stressor Analysis?**

A technique for stress-testing architecture by:
1. Generating diverse, random stressors (including absurd ones like "Fire breathing Lizards")
2. Mapping which architecture components each stressor affects
3. Calculating vulnerability scores for components and impact scores for stressors
4. Identifying high-leverage architectural improvements (residues)
5. Iterating to reduce overall system vulnerability

**The Key Insight:**

Architectural improvements made to handle one stressor often protect against MANY unrelated stressors. As you iterate and add residues, the system becomes increasingly antifragile - fewer and fewer stressors affect it, even completely unexpected ones.

**Why This Matters:**

Current Phase 1 skills help architects make better decisions, document clearly, evaluate technologies, and review designs. But we lack a skill for **stress-testing** architecture against unknown unknowns and building antifragile systems.

**The Fire Breathing Lizard Principle:**

The most important stressors are the absurd ones - they represent unknown unknowns. If your system can't conceptually handle fire breathing lizards, it can't handle black swan events, zero-day exploits, or unpredictable market shifts.

## Decision

We will **add Stressor Analysis as a Phase 1 skill**, making it the **5th core capability-building skill**.

### What It Does

**Commands:**
- `/restack-stressor generate` - Generate creative stressors (realistic + absurd)
- `/restack-stressor analyze` - Map impacts to architecture components
- `/restack-stressor vulnerabilities` - Identify high-impact areas
- `/restack-stressor residues` - Suggest architectural improvements
- `/restack-stressor iterate` - Re-analyze after adding residues
- `/restack-stressor workshop` - Facilitate team workshop

**Capability Built:**
- **Antifragility Thinking** - Designing systems that benefit from stress
- **Creative Stress-Testing** - Imagining wild failure scenarios
- **Impact Analysis** - Understanding cascades through architecture
- **Strategic Resilience** - Finding high-leverage improvements
- **Iterative Hardening** - Systematically reducing vulnerability

**Unique Value:**
- Only skill focused on **unknown unknowns**
- Quantifiable resilience improvement (before/after scores)
- Builds antifragile systems, not just robust ones
- Works for solo architects OR team workshops

### Why Phase 1, Not Phase 2?

**Could be Phase 2 because:**
- More advanced concept
- Involves iteration and learning
- Has workshop format (team-level)

**Should be Phase 1 because:**
- Individual architects need this capability
- Complements other Phase 1 skills perfectly
- Used during design, not just after
- Foundation for resilient thinking
- Doesn't require organizational maturity

**Decision:** Phase 1, because it's a fundamental individual capability that enhances all other Phase 1 skills.

### Integration with Existing Skills

**Stressor Analysis + ADR:**
- Stressor analysis reveals needed resilience patterns
- Document high-leverage residues as ADRs
- Example: `/restack-stressor analyze` → identifies need for circuit breakers → `/restack-adr create Add circuit breakers for API resilience`

**Stressor Analysis + Solution Doc:**
- Include stressor analysis results in HLD
- Document residues in architecture docs
- Show how system handles failure modes

**Stressor Analysis + Tech Stack:**
- Evaluate technologies for resilience properties
- Choose tech that supports needed residues
- Example: Need async processing → evaluate queue technologies

**Stressor Analysis + Design Review:**
- Add antifragility to review dimensions
- Check if system handles unknown unknowns
- Review residue effectiveness

**Together:** The 5 Phase 1 skills provide complete individual architect capability.

## Consequences

### Positive

**For Architects:**
- **Think about unknown unknowns** systematically
- **Build antifragile systems** from the start
- **Quantify resilience** improvement over time
- **Identify high-leverage** architectural improvements
- **Have fun** with absurd stressors (lizards!)

**For Systems:**
- **Increasingly resilient** with each iteration
- **Handle surprises** gracefully
- **Compound protection** from multiple improvements
- **Evolve toward antifragility** naturally

**For the Toolkit:**
- **Unique capability** not found in other tools
- **Completes Phase 1** with resilience thinking
- **Playful yet rigorous** approach
- **Workshop-friendly** for team use

**For Residuality Integration:**
- **Directly from theory** - authentic residuality concept
- **Demonstrates compound value** - each residue helps with multiple stressors
- **Embodies antifragility** - systems benefit from stress

### Negative

**Complexity:**
- Most abstract Phase 1 skill
- Requires creative thinking (some struggle with absurd scenarios)
- Matrix format can be overwhelming initially
- Iteration required to see full value

**Learning Curve:**
- Harder to explain than other Phase 1 skills
- "Fire breathing Lizards" seems silly until you understand it
- Workshop facilitation requires skill
- Results depend on quality of stressor generation

**Adoption Risk:**
- Some organizations may see this as "too theoretical"
- Engineers may dismiss absurd stressors as waste of time
- Requires buy-in to embrace unknown unknowns
- Time investment for iteration

### Neutral

- Adds 5th skill to Phase 1 (was 4, now 5)
- Changes Phase 1 narrative to include antifragility
- Requires updating all documentation
- Excel example shows practical application

## Alternatives Considered

### Alternative 1: Make it Phase 2 Skill
- **Pros:** 
  - More advanced, fits with organizational skills
  - Workshop format aligns with team focus
  - Could be "Antifragility Coach"
- **Cons:**
  - Individual architects need this NOW, not later
  - Doesn't require organizational maturity
  - Phase 1 needs resilience thinking
- **Why rejected:** Too valuable to delay to Phase 2. Belongs with core individual capabilities.

### Alternative 2: Integrate into Design Review
- **Pros:**
  - Fewer total skills
  - Natural fit with reviewing designs
  - Stressor analysis is a review technique
- **Cons:**
  - Design Review already comprehensive
  - Stressor Analysis deserves focus
  - Different usage pattern (iterative vs one-time)
  - Dilutes unique value
- **Why rejected:** Stressor Analysis is substantial enough to warrant its own skill.

### Alternative 3: Wait and Validate Need
- **Pros:**
  - Reduce risk of adding unnecessary complexity
  - See if users request it
  - Phase 1 already has 4 good skills
- **Cons:**
  - Users won't request what they don't know exists
  - Missing opportunity to differentiate
  - Antifragility is core to residuality theory
- **Why rejected:** This is too valuable and aligns perfectly with residuality principles. Add it now.

### Alternative 4: Simplified Version
- **Pros:**
  - Just generate stressors, skip matrix
  - Easier to understand and use
  - Lower barrier to entry
- **Cons:**
  - Loses quantification (impact scores)
  - Can't track improvement over iterations
  - Less rigorous, less valuable
- **Why rejected:** The matrix and scoring are what make this powerful. Keep full version.

## Implementation Strategy

**Immediate:**
1. ✅ Create stressor-analysis.md skill
2. Document decision in ADR-003
3. Update README and ROADMAP
4. Add to Phase 1 skill list
5. Create example stressor analysis

**Short-term:**
1. Create stressor analysis template
2. Add examples (use the banking example)
3. Update Getting Started guide
4. Add to Quick Reference

**Medium-term:**
1. Gather feedback on skill usage
2. Refine stressor generation prompts
3. Build pattern library of common residues
4. Create workshop facilitation guide

## Success Metrics

**Capability Metrics:**
- Architects naturally think about failure modes during design
- Systems show reduced vulnerability over iterations
- Absurd stressors reveal real architectural gaps
- High-leverage residues identified and implemented

**Usage Metrics:**
- Stressor analyses conducted
- Iterations performed (shows compound improvement)
- Workshop facilitation instances
- Integration with ADR skill (residues → decisions)

**Residuality Metrics:**
- Before/after vulnerability scores
- Number of stressors neutralized per residue
- System resilience improvement over time
- Architect confidence in handling unknowns

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| "Too silly" perception | Medium | Medium | Explain unknown unknowns, show real value |
| Overwhelming complexity | Medium | High | Provide simple starting template, build up |
| Poor stressor generation | High | Medium | Provide stressor categories, examples, prompts |
| Analysis paralysis | Medium | Medium | Emphasize iteration over perfection |
| Workshop facilitation difficulty | Low | Medium | Create facilitation guide, example flows |

## References

- Stressor Analysis.xlsx (banking example)
- Barry O'Reilly, *Residuality Theory* (2026)
- [ADR-001: Incorporate Residuality Theory](ADR-001-incorporate-residuality-theory.md)
- [Antifragile](https://en.wikipedia.org/wiki/Antifragile_(book)) - Nassim Taleb
- Chaos Engineering principles
- Game Day exercises (Netflix, Amazon)

## Open Questions

- [ ] Should we provide industry-specific stressor templates (fintech, healthcare, etc.)?
- [ ] Do we need a web-based matrix tool, or is markdown sufficient?
- [ ] Should stressor analysis integrate with threat modeling?
- [ ] How do we measure long-term system antifragility?
- [ ] Should we create a public stressor library?

## Next Actions

1. ✅ Create stressor-analysis.md skill
2. ✅ Document in ADR-003
3. 📋 Update README.md with 5th Phase 1 skill
4. 📋 Update ROADMAP.md
5. 📋 Add to QUICKREF.md
6. 📋 Create example stressor analysis from banking scenario
7. 📋 Add stressor analysis template
8. 📋 Update Getting Started guide

---

**This ADR adds a unique and powerful capability to Phase 1. Stressor Analysis embodies the essence of residuality theory - building systems that become stronger through iterative improvement and compound resilience.**

**Remember:** Fire breathing Lizards are not a joke. They're a reminder to design for the unknowable. 🐉
