# ADR-006: Exclude Risk Assessor Skill from Phase 3

**Status:** Accepted

**Date:** 2026-05-18

**Deciders:** ReStack maintainers

**Technical Story:** Phase 3 planning — evaluating which specialized skills to build

**Implementation Status:** implemented

**Implemented Date:** 2026-05-18

**Implemented By:** ReStack team

**Review Date:** 2026-11-18

## Context

ReStack's Phase 3 originally planned a **Risk Assessor** skill to help architects identify architectural risks, build risk registers, define mitigation strategies, and track risk over time.

This was a carry-over from conventional Solution Architect practice, where risk management typically involves:
- Probability × Impact matrices
- Risk registers with owners and mitigations
- Periodic risk reviews
- Known-threat cataloguing

However, the toolkit is built on **Residuality Theory** — a philosophy that fundamentally challenges the premise of traditional risk management.

### The Problem with Traditional Risk Assessment

Traditional risk management assumes you can:
1. **Enumerate risks** — identify what can go wrong in advance
2. **Predict impact** — estimate probability and severity
3. **Pre-plan mitigations** — define responses before events occur

This works for **known unknowns** but fails entirely for **unknown unknowns** — the threats you didn't see coming, which are historically the most damaging.

Risk registers give a false sense of security. Teams that have "managed their risks" may be less vigilant about threats not on the register. The process optimises for the risks you imagined, not the ones that actually materialise.

### What Residuality Theory Offers Instead

Residuality Theory, as embedded throughout the toolkit (especially in the Stressor Analysis skill), takes a fundamentally different approach:

- **Design for unknown unknowns** — build systems that can absorb and benefit from unexpected stress
- **Antifragility over mitigation** — rather than trying to prevent harm from specific risks, build residues that make the system stronger under any stress
- **Stressor analysis** — generate creative, diverse, even absurd stressors to discover high-leverage architectural improvements (residues)
- **Compound protection** — a single architectural residue (e.g., circuit breaker, decoupled data store) protects against many unrelated stressors simultaneously
- **Tool Independence** — capability is built so architects think this way naturally, not only when running a risk process

The `/restack-stressor` skill already provides a richer, philosophically consistent alternative to risk assessment.

## Decision

We will **not build a Risk Assessor skill** for Phase 3 or any future phase. The capability is intentionally covered by the Stressor Analysis skill (`/restack-stressor`) and the antifragility thinking built across all Phase 1 skills.

If architects trained with this toolkit encounter traditional risk management requirements (e.g., risk registers for compliance or governance), they should:
1. Use `/restack-stressor` to identify high-leverage architectural improvements
2. Map residues to risk language for compliance purposes if required
3. Recognise that the stressor/residue model is a **superset** of traditional risk management — it covers known risks and unknown ones

## Consequences

### Positive
- Maintains philosophical consistency with Residuality Theory throughout the toolkit
- Avoids training architects in a reductive mental model (probability × impact) that creates false confidence
- Keeps Phase 3 focused on genuinely differentiated, high-value capabilities
- The existing `/restack-stressor` skill already provides a superior alternative
- Architects build antifragility thinking rather than risk catalogue thinking

### Negative
- Organisations with mandatory risk register processes may need to translate stressor analysis outputs into traditional risk formats manually
- Some stakeholders and governance functions expect traditional risk artefacts — architects may need to bridge this gap themselves

### Neutral
- Phase 3 is reduced from 4 skills to 3 skills (Cloud Architect, Compliance Checker, Capacity Planner)
- The roadmap should be updated to reflect this decision

## Alternatives Considered

### Build the Risk Assessor as planned
- **Pros:** Familiar to architects trained in traditional SA practice; meets governance expectations directly
- **Cons:** Contradicts Residuality Theory; trains architects to think in risk catalogues rather than antifragility; adds a skill that duplicates and undermines the Stressor Analysis skill's philosophy
- **Why rejected:** Philosophical inconsistency is too high a cost; the toolkit's value is in building a better mental model, not reinforcing the old one

### Build a "Risk Translation" utility (stressor outputs → risk register format)
- **Pros:** Bridges the gap for compliance requirements without changing the thinking model
- **Cons:** Adds complexity; encourages architects to think in risk registers again even if starting from stressors
- **Why rejected:** The translation can be done ad-hoc when needed; a dedicated skill risks normalising the old model

## References

- [ADR-001: Incorporate Residuality Theory](ADR-001-incorporate-residuality-theory.md)
- [ADR-003: Add Stressor Analysis Skill](ADR-003-add-stressor-analysis-skill.md)
- Residuality Theory — Barry O'Reilly
- *Antifragile* — Nassim Nicholas Taleb

---

## Outcome (Post-Implementation Review)

**Fill this section 3-6 months after implementation to track what actually happened.**

**Review Date:** [To be completed 2026-11-18]

**Reviewed By:** [Name/Team who conducted review]

### Baseline Metrics

- Risk Assessor skill: not built
- Stressor Analysis skill: available and active

### Collected Metrics

[To be completed at review date]

### What Worked

[To be completed at review date]

### What Didn't Work

[To be completed at review date]

### Surprises

[To be completed at review date]

### Lessons Learned

[To be completed at review date]

### Follow-up Actions

- [ ] Review whether architects trained with the toolkit are successfully handling governance risk requirements via stressor outputs
- [ ] Assess if a lightweight "stressor → risk register" translation guide would be useful as a doc (not a skill)
