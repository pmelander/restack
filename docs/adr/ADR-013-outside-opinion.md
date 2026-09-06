# ADR-013: An Outside Opinion in Three Places, Behind a Data Gate

**Status:** Accepted

**Date:** 2026-09-06

**Deciders:** ReStack maintainers

**Technical Story:** Cross-model second opinion — roadmap item 6

**Implementation Status:** implemented

**Implemented Date:** 2026-09-06

**Implemented By:** ReStack maintainers

**Review Date:** 2027-03-06

## Context

A single model generates from its own distribution. Where the method depends on
reaching *outside* a distribution — which is most of what stressor analysis is
for — that is a structural limitation rather than a quality problem, and no
amount of prompting fixes it.

gstack solves this with a Codex pass that falls back to a fresh same-model
session. The shape is right and worth taking: probe for an outside model, ask
the user first, send a structured summary rather than raw conversation, write
the prompt to a file instead of the command line, sandbox the call, treat every
error as non-blocking, present the result verbatim, and state which model
actually answered.

It does not transfer unchanged, for one reason that dominates the design.

**What ReStack would send is not a brainstorm summary.** It is a path map of a
real system, its actors, its failure modes, and a ranked account of where it is
weakest. For a production system that is among the more sensitive documents an
organisation holds — arguably more so than the source code, because it is the
analysis of where the system breaks and in what order. gstack's consent prompt
is proportionate to a product idea. It is not proportionate to this.

## Decision

**An outside opinion is available in three places, and refused in three others.**

Available:

1. **Stressor generation** — the strongest case, and the only one where the
   value is structural rather than incidental. A different model asked for the
   *complement* of an existing list attacks the "comfortable stressors" failure
   directly.
2. **Residual identification** — two independent diagnoses of the same cluster,
   with our own diagnosis withheld so the answer is not anchored.
3. **Design review** — adversarial read, and only on a one-way door. Routine
   review findings are checkable against the design and the matrix, so the
   marginal value is low while the data leaving is not.

Refused at **terrain classification, the confidence gate and the iterate gate**.
Those are judgements about what you do not know about your *own* system, where
an outside model knows strictly less than the architect. A model answering there
produces confident noise, and a model auto-answering a gate is the specific
false confidence this toolkit was built to avoid.

### The data gate is the part that differs

Before anything is sent, a decision brief with three real options:

- **Send anonymised (recommended default)** — actors replaced with roles, vendor
  and product names removed, as a *consistent mapping the architect keeps* so
  returned stressors can be mapped back.
- **Send as-is** — only where the system is public, the environment is
  synthetic, or the architect confirms the classification permits it.
- **Skip** — always available, and correct whenever the answer is unclear.

The reason anonymising is the default rather than a caution: **the method does
not need identity.** Stressor analysis operates on mechanism. "Payment Gateway"
carries every bit of the analytical weight the real vendor name does, and the
returned stressors are just as useful. There is no accuracy cost to pay, which
makes the safer option also the free one — an unusual position, and worth taking
when it occurs.

Where the architect cannot say whether the classification permits it, that is a
skip, and the question goes to whoever owns the data.

### Same-family fallback is a weaker residual

When Codex is unavailable, a subagent with fresh context stands in. It removes
conversation bias, which is one real failure mode, but it shares training and
therefore shares blind spots. In this toolkit's own terms: **it defends against
fewer stressor classes.**

The practical rule, stated in the section: its *agreement* is close to
worthless, its *disagreement* still valuable. Which one ran is reported every
time, so the reader can discount accordingly.

### Shared sections

The method is one thing used by several skills, so it lives once at
`scripts/shared/second-opinion.md`. `gen_skills.py` gained a `"shared": true`
manifest flag: the content sits in `scripts/shared/`, the section index renders
the real path, and it is still read on demand rather than inlined.

This is the first shared section. The alternative — duplicating the method into
each consuming skill — would reintroduce exactly the two-sources-of-truth
problem that converting the skills to templates removed, and the alternative
after that — a skill owning it and others cross-referencing — puts the data gate
somewhere arbitrary.

## Consequences

**Positive**

- The one structural limitation of a single model is addressed where it actually
  bites, and nowhere else.
- Sending a production system's weakest points to a third party is now a
  deliberate, defaulted-safe decision rather than an implicit one.
- Stressors from outside are tagged `external`, so at iteration three you can
  ask how many of the ones that mattered came from outside your own generation.
- The shared-section mechanism is available for the next piece of method that
  legitimately spans skills.

**Negative**

- One more optional step in two workflows, and optional steps get skipped. Its
  placement is deliberate rather than universal for that reason.
- Anonymising is real work, and doing it badly — inconsistently — produces
  stressors that cannot be mapped back. The section requires a kept mapping.
- Codex availability is not something ReStack can guarantee, so most runs will
  get the weaker same-family fallback. Reporting which one ran is what keeps
  that honest.

**Neutral**

- Nothing waits on this and nothing fails without it. Every error is
  non-blocking by construction.

## Notes

Worth recording the shape of the adaptation, because it is the third time the
same move has paid off: take the *mechanism* from gstack and re-derive the
*axes* for this domain.

Decision briefs became confidence and reversibility rather than completeness
([ADR-008](ADR-008-generated-skills-with-tiered-preamble.md)). Design review
findings gained a triage step because half of them were about documents rather
than the system ([ADR-012](ADR-012-artifact-consistency-as-a-review-dimension.md)).
Here the consent prompt became a data-classification gate with anonymisation as
the default, because what ReStack sends is categorically more sensitive than
what gstack sends.

Copying the mechanism without re-deriving the axes would have produced something
that looked right and was wrong in the way that matters.
