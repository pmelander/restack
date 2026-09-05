### The six pillars

A structured pass over a cloud design. Rate each **Strong / Needs attention /
Gap**, with specific evidence — a pillar rated without evidence is an opinion
with a badge.

**1. Operational excellence.** Infrastructure defined as code and actually
applied that way (drift means the code is fiction). Observability that answers
"is this path failing" rather than "is this box up". Runbooks that exist and
have been used. Post-incident review that changes something.

**2. Security.** Zero-trust networking — no implicit trust from network
position. Least-privilege IAM, checked rather than assumed. Encryption at rest
and in transit. Secrets in a managed store, never in code, images, or
environment variables committed anywhere. Audit logging that would let you
reconstruct events afterwards.

**3. Reliability.** Multi-AZ or multi-region as appropriate to the actual
requirement. Self-healing and auto-scaling. Graceful degradation and circuit
breaking. **Tested** disaster recovery — untested is a belief. Known behaviour
under partial failure.

**4. Performance efficiency.** Right-sized compute and storage against measured
demand. Caching and CDN where access patterns justify them. Async processing
for work the user is not waiting for. Data store chosen for the access pattern
rather than familiarity. A performance baseline that exists.

**5. Cost optimisation.** Committed-use discounts where the load is predictable.
Auto-scaling that scales *in* as well as out. Storage lifecycle policies. Cost
allocation tags that make spend attributable. A rightsizing cadence with an
owner.

**6. Sustainability.** Utilisation high enough that you are not paying to idle.
Managed and serverless services where they genuinely reduce idle compute.
Region choice where carbon intensity is a real input and latency permits.
Workload consolidation.

---

### What the pillars are good for, and what they miss

The pillars are a genuinely useful structured sweep. They are also a
**checklist**, and this toolkit is explicit about what checklists do: they
enumerate what is conventionally known to matter and produce confidence
proportional to coverage rather than to actual exposure. That is the argument
in [ADR-006](../../../docs/adr/ADR-006-exclude-risk-assessor-skill.md), and it
applies here.

A design can score Strong across all six pillars and still be fragile in the
way that will actually take it down, because the pillars do not know:

- which actors *this* system's intentions flow through, or which of them is on
  the critical path
- which stressors are live in *this* environment — a regulator, a partner's
  release cycle, a team that will not expose an endpoint
- that the organisational constraint blocking a residual is the highest-impact
  stressor in the matrix

**So cross-check.** After the pillar pass, take every finding and classify it
against the stressor matrix using the same four classes as design review —
`/restack-design-review`'s `matrix-crosscheck.md` defines them. Then ask the
question the pillars cannot:

> Which vulnerabilities in the matrix does the pillar review not surface at all?

Those are the findings worth leading with, because nothing else will catch them.

Where no stressor analysis exists, say so and rate the review's own confidence
accordingly. A Well-Architected review presented as a completeness statement,
over a system whose paths nobody has walked, is exactly the false confidence
this toolkit was built to avoid.

#### Report shape

```markdown
# Well-Architected review — <system>
**Date:**   **Design version:**   **Stressor analysis:** iteration N | none

## Pillar assessment
| Pillar | Rating | Evidence |

## Findings, cross-checked
[each finding with its matrix class A/B/C/D]

## What the pillars did not cover
[matrix vulnerabilities the pillar pass does not reach — usually
organisational, regulatory, or specific to this system's paths]

## Top three improvements
[by risk reduced per unit of effort, with reversibility noted]

## Quick wins vs strategic
```

Lead with the third section when it is non-empty. It is the part a vendor's own
review will never give them.
