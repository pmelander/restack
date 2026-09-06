# ADR-012: Artifact Consistency Is a Review Dimension, Not a Matrix Class

**Status:** Accepted

**Date:** 2026-09-06

**Deciders:** ReStack maintainers

**Technical Story:** First field evidence — a real engagement run with ReStack v1

**Implementation Status:** implemented

**Implemented Date:** 2026-09-06

**Implemented By:** ReStack maintainers

**Review Date:** 2027-03-06

## Context

This is the first decision in ReStack driven by evidence from a real
engagement rather than by reasoning about the toolkit in isolation.

A dynamic-packaging repricing design was built from scratch using ReStack v1
over roughly two weeks: 42 ADRs, an HLD, 9 LLDs, a deployment guide, a runbook,
a configuration manifest, 2 stressor iterations and 5 design reviews. Reviewing
what it produced tested two v2 mechanisms against something they had never seen.

**What held.** The residual-traceability fields v2 added to `/restack-adr` are
justified: 5 of the 42 v1 ADRs mention a residual id and none record
reversibility. The best of them carried the analysis-to-decision link in prose —
ADR-0026 names the specific stressors it answers — but 37 did not, and for those
the reason the decision exists is recoverable only by reading the whole set.

**What did not.** v2's matrix cross-check assumes every design-review finding is
about system vulnerability, and classifies each as A (matrix caught it, residual
missing), B (residual present but not working), C (matrix should have caught it)
or D (genuinely new).

Across the 5 reviews there were 32 findings and **4 citations of any stressor or
residual id** — confirming the disconnection between review and analysis that
the cross-check was built to fix. But most of those findings were not about the
system at all:

- The *critical* finding of review 5 was `DEPLOYMENT.md §2.2 contradicts
  ADR-0041` — two documents disagreeing about where a UI is hosted. An engineer
  following the deployment guide would have provisioned a resource the design
  had explicitly rejected, added unnecessary CORS, and potentially broken the
  internal-only ingress posture.
- Of review 4's ten findings, roughly half were documents out of step with each
  other: the HLD not reflecting the background-refresh model, two actors from
  iteration 2 absent from the container view, ADR-0003's invariants left stale
  by ADR-0029.

None of these classify as A, B, C or D. The matrix has nothing to say about two
documents contradicting each other. Forcing them into the scheme produces
nonsense, and leaving them out means the classification covers a minority of
what a review on a mature design actually finds.

The mechanism was right and the scope was wrong.

## Decision

**Triage before classification.** The cross-check now begins by splitting
findings into **system** findings, which classify A/B/C/D against the matrix, and
**artifact** findings, which do not. Artifact findings are reported in their own
section of the review.

**Artifact consistency becomes a review dimension**, with its own section and its
own scoped command, `/restack-design-review consistency`. It runs six checks:
ADR against ADR, ADR against design documents, actors against the HLD, residuals
against their records, placeholders and empty evidence tables, and operational
documents against the current design.

Two rules make its output actionable:

- **Say which document is wrong**, not merely that two disagree. ADRs are
  authoritative; design and operational documents describe. Where a design
  document is right and the ADR is stale, the finding is that a decision was made
  without being recorded — worse than drift, and it routes to `/restack-adr`.
- **Severity comes from who acts on it.** Rate by what happens if someone follows
  the stale document. A deployment guide is executed by someone under time
  pressure and earns critical readily; a stale background section does not.

`/restack-design-review complete` runs consistency **last**, because drift is
measured against what the earlier passes established the design currently is.
`/restack-solution-doc review` hands off to it rather than duplicating it: a
document reviewed against itself cannot reveal drift, because drift is a property
of the set.

### Why a dimension rather than a fifth class or a new skill

A **fifth matrix class** would be wrong in kind. The other four answer "why did
the analysis miss this?"; artifact drift was never in the analysis's scope, so
the question does not apply.

A **new skill** would be disproportionate. Design review already found this five
times unaided — it is the natural home, and the scoped command makes it cheap to
run on its own between full reviews.

## Consequences

**Positive**

- A review over a mature design now handles the majority of what it finds,
  instead of forcing half the findings through a scheme built for the other half.
- The distribution gains a second meaning: mostly-artifact findings say the
  analysis is probably sound and the descriptive documents are not keeping up —
  which points at a missing step in the iteration loop rather than at a need to
  review harder.
- Drift can be checked cheaply and often, rather than only inside a full review.

**Negative**

- One more dimension in `complete`, on a design where it may find as much as all
  the system dimensions together. That is real cost, and it is the correct cost:
  on the reference engagement those findings were being made anyway, by hand,
  five times.
- The consistency pass is the most mechanical thing in the toolkit and the least
  about building architectural judgement. It earns its place on consequence, not
  on capability transfer.

**Neutral**

- Early-stage designs will find almost nothing here. Drift is a function of
  document count, so the pass is close to free until it is needed.

## Notes

Worth recording how this was found, because it is the argument for field
validation over more design.

The gap was invisible from inside the repository. Every v2 mechanism is
internally coherent, and the four-class scheme reads as complete until you put it
next to 32 real findings and discover that most of them are a kind the scheme
does not admit. No amount of further reasoning about the toolkit would have
surfaced it — it required a design with enough documents to have drifted, which
is a state you only reach by doing the work.

The corresponding lesson for the roadmap: the remaining items are guesses until
something similar tests them.
