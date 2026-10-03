# ADR-025: The Impact Matrix's Arithmetic Is Done by a Script; Scoring Stays With the Architect

**Status:** Accepted

**Date:** 2026-10-03

**Deciders:** ReStack maintainers

**Technical Story:** tool 3 of the tooling review after the reference
engagement; field note in that engagement's iteration-6 residuals: "Every
cleared cell was checked against the matrix by script"

**Implementation Status:** implemented

**Implemented Date:** 2026-10-03

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-03

## Context

The impact matrix is binary and simple per cell, and large in total. The
reference engagement's iteration 7 is 152 stressors by 30 actors. Around it
the method asks for arithmetic that is easy to get wrong by hand:

- row totals, column totals and the grand total, always shown;
- a comparison between iterations, per actor, against **the same stressor
  set**, with the total against the expanded set reported separately: "the
  most common way this analysis is quietly falsified";
- for each residual, the cells it clears, each of which must be a 1 to begin
  with, with a compound forecast that counts a cell claimed by two residuals
  once.

On the reference engagement the model wrote one-off scripts to check the 67
cells five residuals claimed. Those scripts were correct, and they vanished
with the session. A matrix of that size also carried its layout across
iterations (a Lens column added, an actor column dropped), so each ad-hoc
script had to rediscover the shape.

One inconsistency surfaced while building this. The method says an unknown
cell is scored 1 and marked `?`, but trace counted a bare `?` as 0.

## Decision

1. **`matrix.py` in `/restack-stressor` does the arithmetic** (standard
   library, no network), with three commands:
   - `totals`: margins checked (filled with `--write`), cells that are not 0,
     1 or `?`, the unknown cells, and **reading aids**, which are the method's
     four checks as numbers: the top actors' share, stressors hitting the
     identical actor set, the spread of the column totals, zero columns.
   - `compare`: the per-actor before/after table in the method's format, the
     total against the shared stressor set (split into actors in both, removed
     and added) and against the expanded set, cells cleared, cells newly 1,
     and cells that left with a removed actor (not "cleared").
   - `claims`: each residual's `**Clears N cells:**` list checked against the
     matrix (every claimed cell a 1 before; with `--after`, a 0 after, or its
     actor removed), the stated count against the list, overlaps, the distinct
     total, and cells that cleared with no residual claiming them.
2. **It never scores.** Only `totals --write` writes, only the margins, and
   it refuses while any cell is not binary. Clusters are reported as
   candidates (identical actor sets); naming the mechanism, and seeing the
   near-identical clusters, stays with the architect.
3. **A `?` counts as 1** in `matrix.py` and in trace (1.0.3), as the method
   says: unknown exposure is exposure.
4. **The residual format is fixed so it can be checked**: a `## R<n>` section
   per residual, `**Clears N cells:**`, one `- S-<n>: <actor>, <actor>` line
   per stressor, and the cells outside the cluster on an `**Outside the
   cluster:**` line. This is the format the reference engagement already used.
5. **`/restack-stressor` uses it** in `analyze` (fill the margins),
   `vulnerabilities` (start from the reading aids), `residues` (check the
   claims) and `iterate` (compare, and check the claims against the new
   matrix). Owned by the skill that owns the matrix; no other skill calls it.

## Consequences

### Positive

- On the reference engagement's iterations 6 → 7: 195 → 133 against the
  shared stressor set and 244 against the expanded one. 66 cells were cleared
  on shared actors, plus one claimed cell whose actor (QU) was removed: the 67
  the residuals claimed, with none cleared unclaimed. The field reconciled this
  by hand; the script does it in one run.
- A residual's count can no longer drift from its list, and a cell cannot be
  "cleared" that was never a 1.
- Comparing totals across different stressor sets now requires ignoring the
  output, which states both.

### Negative

- The residual format is now load-bearing: a residual written as prose has no
  checkable claim. `claims` refuses a file with no `**Clears N cells:**` list
  rather than guessing.
- Reading aids that are numbers can be mistaken for findings. The output says
  they are not, and the skill text says so too.

### Neutral

- Trace's `MX` check stays: it is the read-only drift check over every matrix
  in `docs/`. `matrix.py` is the working tool inside the stressor loop.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| `/restack-stressor` (`analyze`, `vulnerabilities`, `residues`, `iterate`) | arithmetic by hand | updated |
| `sections/residual-identification.md` | a free-form cell list | updated: the checkable format |
| trace (`score`, fixture) | a bare `?` counted as 0 | updated: counts as 1 (trace 1.0.3) |
| CLAUDE.md, QUICKREF.md | | updated |

## Alternatives considered

### Add the commands to trace

- **Pros:** one script for all document arithmetic.
- **Cons:** trace is read-only by decision
  ([ADR-021](ADR-021-trace-checks-as-a-worklist.md)) and works on the whole
  `docs/` tree; `totals --write` writes, and compare and claims work on
  named files inside the loop.
- **Why rejected:** different jobs, different owners.

### Compute a severity-weighted total

- **Why rejected:** binary scoring is the method's position, argued in
  `matrix-construction.md` and the ROADMAP. The script reports a cell above 1
  instead of weighting it.

## References

- `skills/restack-stressor/sections/matrix-construction.md`: the totals, the
  reading checks, comparing iterations
- [ADR-021](ADR-021-trace-checks-as-a-worklist.md): trace
- `skills/restack-stressor/scripts/matrix.py`, `tests/test_matrix.py`
