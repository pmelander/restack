# ADR-014: A Decision Model for Matrix Cells, With a Validation That Can Withdraw It

**Status:** Accepted

**Date:** 2026-09-19

**Deciders:** ReStack maintainers

**Technical Story:** Jev cell scoring for `/restack-stressor`

**Implementation Status:** implemented

**Implemented Date:** 2026-09-19

**Implemented By:** ReStack maintainers

**Review Date:** 2027-03-19

## Context

The impact matrix is the instrument the whole method reads from, and it is built
by one model making the same narrow judgement a few hundred times. Twelve actors
against thirty stressors is 360 cells. Each one is binary, each one is the same
shape, and none of them is interesting on its own.

That work is mechanical in a way almost nothing else in this toolkit is. Terrain
classification, the confidence gate, naming the mechanism behind a cluster —
those are judgements that need the architect's knowledge of their own system.
Scoring a cell needs the path map and the stressor and nothing else.

**The problem is not that the model scores cells badly. It is that the same
model generates the stressors, scores them, and reads the result.** Three roles,
one judgement, and the middle one is the least defensible. A model that
generated "region-wide AZ failure" has an account of what that means already
loaded when it scores the Order Service cell, and no amount of instruction
separates the two.

TypeSafe's Jev is a System One model: it takes a state and typed questions and
returns calibrated probabilities. A `noul` — their yes/no primitive — returns
the probability the answer is yes. That is a better-shaped instrument for a
binary cell than a language model producing the character `1`, for one reason
that matters more than calibration: **it reports when it is unsure**, and a
number near 0.5 is information the current method throws away.

It is also cheap in the way this matrix needs. Jev ingests the state once and
evaluates every question against it in parallel, so a stressor row is one
request carrying one question per actor — thirty requests for a 30×12 matrix,
not 360.

## Decision

**Cells can be scored by Jev. Nothing else can.**

Available at `/restack-stressor analyze` (building the matrix) and at
`/restack-stressor residues` (re-scoring each proposed residual against the full
stressor set, which is the largest scoring job in the method and the one most
often skipped). The protocol is `scripts/shared/jev-scoring.md`; the transport
is `skills/restack-stressor/scripts/jev_score.py`, standard library only, shipped
and installed with the skill per
[ADR-010](ADR-010-skills-are-self-contained.md).

Refused everywhere else, on the same reasoning as
[ADR-013](ADR-013-outside-opinion.md) and more firmly. Jev returns a number and
cannot explain itself. That is the right output for a cell and the wrong output
for a gate, a terrain classification, or a cluster diagnosis — and a gate
answered by a probability is precisely the false confidence this toolkit exists
to avoid.

**Optional, informational, never a gate.** No key, no `python3`, no scoring —
and the run says nothing about it. An optional enhancement that announces its
own absence is a nag, and an architect who has never heard of Jev should not be
able to tell from the output that any of this exists.

### Three bands, and the middle one comes back

| Probability | Cell |
|---|---|
| `p >= 0.8` | `1` |
| `p <= 0.2` | `0` |
| between | the model scores it, as it always has |

The bands are the whole design. A decision model's value here is not that it is
right more often; it is that **it says which cells it is not sure about**, and
those are exactly the cells worth a human-shaped judgement. The confident band
is where the mechanical work lives, and handing it over is what buys attention
for the rest.

**Jev never produces a `?` and never clears one.** A `?` means *this
architecture is not understood well enough to answer* — a claim about the state
of the analysis, carrying a discovery step that would settle it. A probability
near 0.5 is a different statement: the model is confident the answer is
genuinely balanced. Collapsing the two would convert an architect's registered
ignorance into a model's calibrated hedge, and the assumptions register — which
is how `/restack-discover` knows what to go and look at — would quietly stop
filling up.

### The version is pinned, because the thresholds are tuned

`jev-1.13.0`, not the `jev-latest` alias. TypeSafe's own guidance is to pin once
thresholds are tuned against a version, and the 0.8/0.2 bands are tuned
thresholds. An alias moves when a release ships; scoring would change with
nothing in this repository changing, and the validation below would stop
describing the model actually in use.

Their published jaggedness notes for `jev-1.13` argue the same thing from the
other end: a threshold tuned on a `noul` does not transfer to their other
primitives, and separate questions are not held to arithmetic identities — the
same question and its negation, asked as two nouls, were observed summing to
1.19. Nothing here may be built on the assumption that these probabilities
compose.

### The data gate is ADR-013's, with one thing made stricter

`scripts/shared/second-opinion.md`'s "Before anything is sent" step applies
unchanged: anonymised by default, as-is only where the classification permits
it, skip whenever the answer is unclear, and an architect who cannot answer has
answered skip. What leaves is the same document, and it does not become less
sensitive for going to a scoring model rather than a chat model.

One delta. Under option A, anonymisation is **mandatory rather than merely
recommended**, because the actor set travels three times in every request: in
the state, across the question map as ids, and inside each question's
instruction text. That third one is not optional — TypeSafe do not use the
question id in inference, so an actor that is not named in its own instructions
produces a question identical to every other question in the request. A request
with an anonymised path map and real actor ids is not anonymised.

The audit trail records the request count and the egress choice. Nothing else.

### Validation, with a number that can end this

On the README `checkout` example and the GDPR compliance pack, scored both ways:

- **Jev's confident band agrees with model scoring on at least 90% of cells.**
- **At most 20% of cells land in the escalation band.**

Miss the first and the thresholds are wrong or the instrument is; miss the
second and it is not saving anything, because a matrix where a quarter of the
cells come back for hand-scoring costs a round trip and buys a smaller share of
the work than it appears to.

Either miss: tighten the thresholds and re-run, or withdraw the feature. It is
optional by construction, so withdrawing it costs one section, one script, and
nothing else.

`/restack-arch-learning` can run this check without re-scoring anything — the
raw probabilities are written to `docs/stressor-analysis/matrix-<date>.jev.json`
beside each matrix, and the matrix carries a per-row scoring source. Both
numbers are recoverable from artifacts that already exist, which is the point of
writing them down.

## Consequences

**Positive**

- The one mechanical judgement in the method is separated from the model that
  generates and interprets it.
- Uncertainty becomes visible where it previously was not: a cell the scorer
  was unsure about is now routed rather than silently resolved.
- The `residues` re-score against the full stressor set — the step that exposes
  the compound effect, and the one most often cut short — gets materially
  cheaper, which is the best argument for doing it properly.
- The prediction is falsifiable from artifacts the toolkit already writes, so
  this decision can be checked rather than believed.

**Negative**

- A third party now sees path maps and failure modes in the ordinary course of
  building a matrix, rather than only when an architect opts into an outside
  opinion. The data gate is the same, but it is reached far more often, and a
  gate reached often is a gate answered carelessly. Worth watching at review.
- Two scoring paths means two ways a matrix can be wrong, and the provenance
  column exists because otherwise nobody could tell which.
- The budget check is an estimate — there is no tokenizer in the standard
  library — so it refuses slightly early rather than slightly late. A very large
  path map will be refused when it might have fit.
- Cost is real and per-token, where every other part of this toolkit is free.

**Neutral**

- Nothing waits on it and nothing fails without it. Every error falls back to
  model scoring for that row and is recorded as having done so.
- TypeSafe ship an agent skill for Claude Code. It was not used: ADR-010 wants
  the executable shipped and installed with the skill that calls it, and a
  second skill in the tree is a second thing to keep current.

## Notes

The shape is ADR-013's, applied to a different failure. There, the problem was
that a single model generates from its own distribution, and the answer was an
outside voice at the points where reaching outside a distribution is the whole
job. Here the problem is that the same model occupies three roles around one
instrument, and the answer is a different kind of model at the one role that is
mechanical enough to hand over.

The move worth recording is the band in the middle. The obvious design is a
threshold at 0.5 and a scored matrix with no human in it, which is faster and
would have been wrong — it would have produced a matrix with no `?` cells, an
empty assumptions register, and a confident account of a system nobody had
looked at closely. **The escalation band is what keeps the architect in the
loop, and the ≤ 20% target is what stops it being a fig leaf in either
direction.** A band nobody lands in is not a safety mechanism; a band everyone
lands in is not a saving.

Second time a validation in this repository has been written with a number that
can withdraw the feature rather than a number that confirms it. Worth keeping
up.
