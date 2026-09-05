# ADR-007: Compliance via Stressor Packs, Not a Separate Compliance Checker Skill

**Status:** Accepted

**Date:** 2026-05-18

**Deciders:** ReStack maintainers

**Technical Story:** Phase 3 planning — evaluating Compliance Checker skill

**Implementation Status:** implemented

**Implemented Date:** 2026-05-18

**Implemented By:** ReStack team

**Review Date:** 2026-11-18

## Context

Phase 3 originally planned a **Compliance Checker** skill to validate architectures against GDPR, HIPAA, SOC 2, PCI DSS, ISO 27001, and similar frameworks — checking controls, identifying gaps, and generating compliance reports.

On review, a Compliance Checker skill was found to conflict with the toolkit's Residuality Theory foundation for the same reasons as the Risk Assessor (see ADR-006):

**Compliance frameworks are enumerative and backward-looking.** They codify responses to *past* harms. A compliance checklist trains architects to verify they've met known requirements — which is exactly the kind of known-unknown thinking Residuality Theory moves beyond.

However, compliance is often **legally non-negotiable**. Unlike risk management (which can be replaced wholesale by antifragility thinking), compliance requirements must be demonstrably met for regulatory, legal, and contractual reasons.

The question therefore became: **how do we handle compliance in a way that is philosophically consistent with Residuality Theory while still meeting real-world requirements?**

### The Insight

Every compliance control exists because a real harm occurred. GDPR exists because personal data was misused. PCI DSS exists because payment card data was stolen. HIPAA exists because medical records were exposed.

If architects understand the *harm behind the control* rather than the *control itself*, they can design architecture that makes that harm structurally impossible. This is:
1. Philosophically consistent — the architect is thinking in terms of harms (stressors) and protections (residues)
2. Practically superior — the residue addresses the root harm, not just the letter of the control
3. More durable — structural protections outlast regulatory updates

Compliance controls, expressed as stressors, integrate naturally into the existing `/stressor` skill. The residues that emerge from the analysis address the harms — and can be traced back to compliance controls for audit purposes.

## Decision

We will **not build a Compliance Checker skill**. Instead, we will:

1. **Extend the `/stressor` skill** with a `/stressor compliance <pack>` command that injects curated compliance stressor packs into a standard stressor analysis
2. **Define a compliance pack structure** — a clear template for expressing regulatory frameworks as stressor sets
3. **Create a `compliance-packs/` directory** as the extension point for future packs
4. **Leave specific framework packs** (GDPR, HIPAA, PCI DSS, etc.) to be added as future contributions

This approach means:
- Architects continue thinking in stressors and residues — the consistent mental model
- Compliance emerges as a *byproduct* of antifragile design
- Residues protect against compliance scenarios *and* unknown stressors simultaneously
- Compliance evidence maps back from residues to controls, satisfying audit requirements

## Consequences

### Positive
- Maintains philosophical consistency with Residuality Theory
- Architects understand *why* compliance controls exist, not just *what* they require
- A single architectural residue can address multiple compliance frameworks simultaneously (e.g., an audit log satisfies GDPR, HIPAA, SOC 2, and ISO 27001 requirements)
- Extension point is clean — new compliance packs can be added without changing the skill
- Residues improve overall system antifragility, not just compliance posture

### Negative
- Specific compliance packs (GDPR, HIPAA, etc.) are not yet built — architects using the tool today cannot immediately run `/stressor compliance gdpr`
- Organisations with auditors expecting traditional compliance artefacts may need to do additional mapping from residues to controls
- Creating high-quality compliance packs requires deep regulatory knowledge

### Neutral
- Phase 3 is reduced from 3 remaining skills to 2 (Capacity Planner + Cloud Architect already complete)
- The `/stressor` skill grows in scope but retains its core philosophy

## Alternatives Considered

### Build the Compliance Checker as a standalone skill
- **Pros:** Immediately useful for compliance-heavy organisations; familiar format for auditors
- **Cons:** Trains architects to think in checklists; philosophically inconsistent; creates a separate compliance process divorced from architectural thinking
- **Why rejected:** Same reasoning as ADR-006 (Risk Assessor) — the mental model it reinforces is the problem

### Build a "Compliance as Stressors" section within each compliance framework's own skill
- **Pros:** Keeps each framework self-contained
- **Cons:** Duplicates the stressor analysis machinery; architects would need to switch between skills
- **Why rejected:** The existing `/stressor` skill is the right home — compliance packs are just domain-specific stressor inputs

### Build compliance packs immediately for major frameworks
- **Pros:** Immediately actionable
- **Cons:** High effort; risk of getting regulatory details wrong; better done with regulatory expertise input
- **Why rejected:** The extension point is what matters now; specific packs can be contributed over time

## References

- [ADR-001: Incorporate Residuality Theory](ADR-001-incorporate-residuality-theory.md)
- [ADR-003: Add Stressor Analysis Skill](ADR-003-add-stressor-analysis-skill.md)
- [ADR-006: Exclude Risk Assessor Skill](ADR-006-exclude-risk-assessor-skill.md)
- Residuality Theory — Barry O'Reilly

---

## Outcome (Post-Implementation Review)

**Fill this section 3-6 months after implementation to track what actually happened.**

**Review Date:** [To be completed 2026-11-18]

**Reviewed By:** [Name/Team who conducted review]

### Baseline Metrics

- Compliance Checker skill: not built
- `/stressor compliance` command: available, packs pending

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

- [ ] Assess demand for specific compliance packs (GDPR, HIPAA, PCI DSS)
- [ ] Identify contributors with regulatory expertise to build initial packs
- [ ] Review whether residue-to-control traceability guidance is sufficient for audit purposes
