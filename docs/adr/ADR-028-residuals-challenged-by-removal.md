# ADR-028: Adopted Residuals Are Challenged by Removal, and Candidates Are Found by What Actors Share

**Status:** Proposed

**Date:** 2026-10-05

**Deciders:** ReStack maintainers

**Technical Story:** a paper ablation pilot on the reference engagement,
2026-10-05, started by the architect's question about a cluster seen in the
generated system overview. Feedback from that engagement, anonymised.

**Implementation Status:** not implemented. This ADR records the design; the
build follows it.

**Review Date:** 2027-04-05

## Context

Residuality grows a design by iteration. Each iteration finds stressors, and
proposes residuals for them. From the second iteration, the residuals are
themselves stressed, because every residual is an actor with stressors of its
own. Over a long engagement the design accretes.

The toolkit only lets residuals in. Nothing in it removes one:

- `/restack-evolve` writes fitness functions so a residual can't erode
  without anyone deciding;
- `/restack-capacity` warns that removing an idle replica may re-expose
  actors;
- `/restack-journey`'s iterate gate reads "residuals adding complexity faster
  than they remove impact" as **Proceed**: diminishing returns, stop adding.
  It doesn't say "take something out";
- `/restack-design-review` and `/restack-trace` check that the documents
  agree with each other, not that what they describe should exist.

`RESIDUALITY.md` defines a residual as "a specific addition, removal, or
modification". The removal half has never been a move the toolkit makes.

### What the reference engagement showed

Seven iterations, 61 ADRs, nothing implemented:

- like-for-like impact fell 195 → 133 while the full total rose to 244.
  In an earlier iteration, residuals cleared 33 cells and their own actors
  brought 61;
- the gates offered keep-and-extend only. The last iterate gate recorded that
  the loop "now finds second-order surfaces of its own residuals (diminishing
  returns)" and proceeded. An approach gate on a lever that couldn't be
  verified offered four options, and every one kept the lever;
- the engagement **did** remove residuals twice: a lease whose actors carried
  about 32 cells while clearing about 4, and a publish queue. **Both were
  removed while still proposals**, when their first walk showed the cost.
  Nothing re-opens a residual once it is adopted and others are built on it.

### How the candidate was found

The architect questioned a dedicated storage account after looking at the
**generated system overview**. In the picture it is one box, with arrows
arriving from every lane. The matrix could not have pointed at it:

- the matrix splits it into five columns (2, 6, 6, 10 and 11 cells). None of
  them is in the iteration's most-hit list, which starts at 21 and 20;
- **summed, it is the largest concentration in the design: 35 cells on 24
  rows**;
- in the HLD's diagram source it is the node with the most edges (11), and
  the only one with four writers.

The columns followed actors; the hub was a *shared substrate*. The stressors
that cross it (one account's throttling failing two containers' writes, one
lifecycle rule deleting another container's history, one regional loss
taking all of it) are common-mode coupling between actors the matrix treats
as independent.

### What the pilot found

Two cuts were scored on paper against the latest matrix:

- **Cut the whole layer.** A substitute was forced: every other carrier had
  already been rejected by a decision on record. 6 of the 35 cells vanished
  and 29 moved to the substitute. 8–18 new cells came back, some of them on
  the ordinary-pricing column, the aspiration's first axis. **Kept**, now with
  a tested justification the ADRs didn't carry.
- **Keep the carrier and cut the branch built on it** (a reduce-only stop
  pipeline and the probe that defends it, three generations down). 5 cells
  re-open, 14–28 cells are removed, and an accepted security risk closes.
  **A candidate for a gate.**

Doing it by hand showed eight things an ablation gets wrong unless the method
forces them:

1. **Removal is substitution.** The intention still needs a carrier. A cut
   with no named substitute can't be scored.
2. **Column counts overstate the saving.** Most cells on a residual's columns
   describe what the control plane means, not what it is built on, and
   survive the cut (29 of 35).
3. **Credit overlaps.** The HLD's "clears" column credited about a dozen
   stressors to two or three residuals each. As later residuals land on the
   same rows, an earlier one's *unique* contribution shrinks, and its ADR
   still claims the full list.
4. **Credit can be circular.** A residual was credited with clearing
   stressors that exist only because of the subtree it belongs to: a missing
   network route into the private endpoint an earlier residual created.
   Remove the subtree and those stressors vanish rather than re-open.
5. **Generation depth is the signal.** Four generations hung off the storage
   account, and the third existed to defend the second.
6. **The gates never offered subtraction.** See above.
7. **The baseline is stale by the time a challenge runs.** Two later
   decisions weren't in any cell.
8. **Counts mislead without the lens.** +2 to +12 cells looked like noise.
   The move into the ordinary-pricing column decided it.

## Decision

### 1. A challenge is a command

`/restack-stressor ablate <residual | actor group> [--substitute <carrier>]`
scores a removal and writes
`docs/stressor-analysis/ablation-<date>-<slug>.md`. It ends in a decision
brief. **It never edits an ADR, a matrix or a journey file**, and it never
recommends a removal as a verdict. Keep, cut and substitute are the
architect's, at a gate ([ADR-022](ADR-022-working-toolkit-not-training-pack.md)).

### 2. Every ablation names its substitute

Each intention the removed actors carried gets a carrier, or is explicitly
dropped. The brief says which. A substitute that an earlier decision rejected
cites that decision and says what has changed since, or is struck off.

### 3. The subtree is scored, not the residual

The removal set is the residual plus what depends on it. That comes from the
ADRs' created-actors lists and their amends and supersedes links, and is
shown with its generation depth. Partial cuts of the subtree are named and
scored as separate scenarios: the pilot's useful cut was two generations
below the one the architect asked about.

### 4. The arithmetic is by script, the judgement stays visible

`matrix.py` ([ADR-025](ADR-025-matrix-arithmetic-by-script.md)) gains:

- `rollup MATRIX --groups FILE`: sums columns by declared shared substrate
  (account, identity, host, region, pipeline) and ranks the groups against
  the most-hit single actors. The architect declares the grouping; the script
  never infers it;
- `ablate MATRIX --remove COLS --claims RESIDUALS... [--classify FILE]`:
  - **the re-open set:** cells the removed residuals cleared that no
    remaining residual also claims (unique contribution);
  - the cells on the removed columns, by the classification file's
    `vanish | inherit | morph` per row;
  - the net, by lens and for the aspiration's own column separately.

**Classifying a row is judgement.** The skill proposes a class with a reason
for each row, and the architect confirms it. A row whose stressor exists only
because of the removed subtree is classed `vanish` (circular credit), never
re-opened. New rows from the substitute are generated and walked like any
other stressor. Until they are, the ablation says "named, not scored".

### 5. Candidates are found by what actors share

The ablation section includes a **topology read** of the HLD's diagram
source: edges and distinct writers per node, with subgraphs counted as one
node. It is done by the skill and shown as a worklist. It complements
`rollup`: the matrix finds hubs the architect has grouped, the diagram finds
the ones drawn as one box.

### 6. The baseline is stated

An ablation names the matrix it runs on and lists every decision since that
adds or removes an actor, under the existing "scored pre-D<n>" rule. A
challenge on a stale matrix is allowed, and it says so on its first line.

### 7. The journey proposes a challenge

`/restack-journey` proposes `ablate` at the iterate gate when any of these
holds:

- the full total rose while like-for-like fell;
- a residual's subtree reaches a third generation;
- a `rollup` group outranks the most-hit actor;
- the design is about to be declared the target, or implementation is about
  to start. Removal is cheapest while it costs documents only.

The gate row "residuals adding complexity faster than they remove impact"
changes from **Proceed** to **Challenge, then proceed**. A gate brief about a
residual that defends another residual includes "remove the defended one" as
an option.

### 8. The outcome is recorded either way

A kept residual's ADR gets a dated line: "challenged by removal on <date>;
kept because <cells, lens>". That is the tested justification an inheritor
needs. A cut goes through the gate's decision and supersedes in the usual way
(`/restack-adr`).

## Consequences

### Positive

- The method can shrink a design, not only grow it, and does so on the same
  evidence it grows by.
- A kept residual carries a tested reason. "We tried removing it; these cells
  come back" survives handover better than a list of stressors written when
  it was proposed.
- Credit overlap and circular credit become visible. Today they only inflate
  the case for keeping whatever is already there.
- Hubs that the matrix's columns fragment become findable without relying on
  someone seeing the right picture.

### Negative

- A counterfactual matrix is a forecast of a forecast. Its numbers are
  ranges, and its new rows are unscored until walked. A brief built on it
  must say so, and briefs that say so are read less confidently.
- Row classification is judgement in bulk: 35 rows on the reference
  engagement. The skill proposes and the architect confirms, which costs
  their time.
- Gates get one more option, and a removal can churn: cut now, re-added after
  an incident. The gate's recorded rationale, and
  `/restack-arch-learning` reviewing the outcome, are the brake.
- The substrate grouping is declared by hand, and an ungrouped substrate stays
  hidden. The topology read is the second net.

### Neutral

- Scoring stays binary, and the definition of a residual doesn't change.
  Removal was always in it.
- `/restack-trace` gets no new check. An ablation is a stressor artefact, not
  document drift, though `trace refs` finds what cites a residual being
  challenged.

## Knock-on changes

The build, not this ADR, does these. Each is pending until it ships.

| Document | What this decision requires there | Done in the same step |
|---|---|---|
| `skills/restack-stressor/SKILL.md.tmpl` | the `ablate` command, its steps and gates | pending |
| `skills/restack-stressor/sections/ablation.md` | substitute, subtree, classification, re-open set, topology read, baseline | pending |
| `skills/restack-stressor/scripts/matrix.py` | `rollup`, `ablate` | done 2026-10-05; checked against the reference engagement's pilot: `rollup` gives its hub (35 cells on 24 rows, against 21), `ablate` the pilot's re-open set |
| `tests/test_matrix.py`, `tests/fixtures/matrix/` | invented fixtures: an overlapping claim, a circular row, a grouped substrate | done 2026-10-05 (iteration 3 of the synthetic engagement) |
| `templates/` | an ablation report template, vendored into stressor | pending |
| `skills/restack-journey/SKILL.md.tmpl` | the gate row; the four triggers | pending |
| `skills/restack-adr/SKILL.md.tmpl` | the "challenged by removal" line on a kept residual | pending |
| CLAUDE.md, README.md, QUICKREF.md, GETTING_STARTED.md, CHANGELOG.md | the command and the ADR | pending |

## Alternatives considered

### A challenge mode in `/restack-design-review`

- **Pros:** the review already reads the whole document set and cross-checks
  findings against the matrix.
- **Cons:** an ablation is matrix arithmetic plus new stressors for the
  substitute, generated and walked. That is stressor work, and the review
  doesn't own the matrix.
- **Why rejected:** it would split the matrix between two skills.

### A new skill, `/restack-challenge`

- **Pros:** a clear entry point for a new kind of work.
- **Cons:** an eighteenth skill for what is stressor analysis run in reverse,
  on the same matrix, claims files and script.
- **Why rejected:** the move belongs with the analysis it reverses.

### Rank residuals by cost against benefit and recommend removals

- **Pros:** fast, and it covers every residual at once.
- **Cons:** a verdict built on the counts the pilot showed to be misleading:
  column totals, overlapping credit and unweighted lenses.
- **Why rejected:** [ADR-021](ADR-021-trace-checks-as-a-worklist.md) and
  [ADR-022](ADR-022-working-toolkit-not-training-pack.md). A script lists
  what to confirm, and the architect decides.

### Leave it to the architect's eye and the diagram

- **Pros:** it worked, and costs nothing to build.
- **Cons:** it worked once, on a hub the diagram happened to draw as one box.
  A hub split across boxes, or left out of the overview, stays hidden. The
  reference engagement's overview omitted three of the hub's read edges.
- **Why rejected as the only mechanism.** The diagram stays an input
  (Decision 5).

### Only add a "remove it" option to gate briefs

- **Pros:** the smallest change; the gates are where the decision is made
  anyway.
- **Cons:** without a substitute, row classification and the unique
  contribution, the option is argued from column counts, which counted 35
  cells as saved where 6 actually went on the reference engagement.
- **Why rejected:** the option needs the analysis behind it (Decision 7 adds
  the option *and* the command it points to).

## References

- `RESIDUALITY.md`: a residual is an addition, removal or modification
- [ADR-021](ADR-021-trace-checks-as-a-worklist.md): output is a worklist, not
  a verdict
- [ADR-022](ADR-022-working-toolkit-not-training-pack.md): the architect owns
  the decisions
- [ADR-025](ADR-025-matrix-arithmetic-by-script.md): matrix arithmetic by
  script, claims checked against the matrix
- [ADR-020](ADR-020-follow-up-commands-run-without-pause.md): the journey
  hands off to `ablate` without pausing, except at the gate's question
