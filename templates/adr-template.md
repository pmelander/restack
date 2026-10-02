# ADR Template

**Status:** [Proposed | Accepted | Deprecated | Superseded by ADR-YYYY]

**Date:** YYYY-MM-DD

**Deciders:** [List of people involved in the decision]

**Technical Story:** [Optional ticket/issue reference]

**Implementation Status:** [not-started | in-progress | implemented | abandoned]

**Implemented Date:** [YYYY-MM-DD when implemented, empty if not yet]

**Implemented By:** [Team/Person who implemented, empty if not yet]

**Review Date:** [YYYY-MM-DD for post-implementation review, typically 3-6 months after implementation]

## Context

[Describe the context and problem statement. What forces are at play? What are the concerns and constraints?]

## Decision

[Describe the decision that was made. Use active voice: "We will..."]

### Derived details

[Details decided while writing that the brief never settled. A one-way door or Low-confidence detail is a decision brief, not a row here.]

| Detail | Derived from | Overturnable |
|---|---|---|
| [detail] | [aspiration, constraint or ADR-NNN] | yes / no |

### Decision-point accounting

[Only when this ADR supersedes, amends or deprecates another. One row per decision point in the old ADR.]

| # | Decision point in ADR-NNN | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| 1 | [point] | holds / replaced by ADR-x / withdrawn | [failure] | [mechanism, or a link to the decision brief] |

## Consequences

### Positive
- [List positive outcomes and benefits]

### Negative
- [List negative outcomes, risks, and trade-offs]

### Neutral
- [List neutral consequences that are neither good nor bad]

## Knock-on changes

[Every descriptive document this decision invalidates, handled in the same step. "None" only after grepping docs/ for the mechanism this changes.]

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| [HLD / LLD / deployment guide / runbook / config manifest / test strategy] | [section and claim] | updated / bannered / ticketed [ref] |

## Alternatives Considered

### [Alternative 1]
- **Pros:** [List benefits]
- **Cons:** [List drawbacks]
- **Why rejected:** [Reason]

### [Alternative 2]
- **Pros:** [List benefits]
- **Cons:** [List drawbacks]
- **Why rejected:** [Reason]

## References

- [Links to supporting documentation, RFCs, articles, etc.]

---

## Outcome (Post-Implementation Review)

**Fill this section 3-6 months after implementation to track what actually happened.**

**Review Date:** [Date this review was conducted]

**Reviewed By:** [Name/Team who conducted review]

### Baseline Metrics

[What we measured before implementing this decision. Examples: deployment time, error rate, team velocity, cost, performance metrics]

### Collected Metrics

[What we measured after implementation. Use same metrics as baseline for comparison]

### What Worked

[Positive outcomes that matched or exceeded expectations. What consequences from above actually happened as predicted?]

### What Didn't Work

[Negative outcomes, failed assumptions, unexpected problems. What consequences didn't happen as expected?]

### Surprises

[Unexpected consequences - both good and bad. What happened that we didn't anticipate at all?]

### Lessons Learned

[What would we do differently next time? What did this decision teach us about our architecture, team, or process?]

### Follow-up Actions

- [ ] [Any follow-up work needed based on outcomes]
- [ ] [Updates to related ADRs or architecture]
- [ ] [Pattern to add to organizational knowledge]
