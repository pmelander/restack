### Minefield route

High fragility, high political complexity, severe or irreversible blast radius.
Structurally this is the brownfield route, but the tolerances are different:
discovery runs longer, gaps are treated as blockers rather than assumptions, the
confidence threshold is higher, and every gate is recorded because the trail
itself is a deliverable here.

```
1.  /restack-journey start             aspiration, terrain, and who can stop this
2.  /restack-discover paths            extensive mapping, multiple entry points
3.  /restack-discover actor            EVERY actor touching a critical path
4.  /restack-discover intentions       every intention, including error and recovery paths
5.  /restack-discover gaps             gaps are blockers, not assumptions
6.  /restack-discover organisation     all stakeholders, all resistance, all veto points
7.  /restack-discover confidence       validate at a raised threshold
      |
      +-- CONFIDENCE GATE: not confident --> back to 2. Expect to loop.
      |
8.  /restack-stressor walk             careful, deliberate, one path at a time
9.  /restack-stressor generate         heavy weighting on organisational stressors
10. /restack-stressor analyze          expect high initial impact scores
11. /restack-stressor residues         prioritise residuals that reduce fragility first
      |
      +-- ITERATE GATE: /restack-journey iterate --> explicit decision, every cycle
      |
12. /restack-adr create                document everything, including what you rejected
13. /restack-solution-doc hld          target state, with the migration path made explicit
14. /restack-design-review complete    validate before anything is touched
```

**Expected iterations: 5+.** Plan for it. A minefield journey that reports
sufficiently-low impact after two iterations has almost certainly not found the
paths that matter.

### What changes relative to brownfield

**Gaps block.** In brownfield an unknown becomes a registered assumption and the
journey continues. Here, an unknown on a critical path stops the journey until
it is closed. The assumptions register is for peripheral unknowns only.

**Fragility before optimisation.** Order residuals by how much they reduce the
chance of catastrophic failure, not by how much they reduce total matrix impact.
A residual that shaves 12 points spread across non-critical actors loses to one
that removes a single-point-of-catastrophe on the critical path.

**Every gate is logged with its rationale.** In this terrain someone will ask,
possibly under audit, why a decision was made. `docs/journey/decisions-log.md`
is the answer, and it is worthless if written retrospectively.

**Reversibility dominates the option set.** Prefer residuals that can be
introduced behind a flag, shadowed, or run in parallel with the existing path
before cutover. When comparing options in a decision brief, a reversible option
with 70% of the benefit usually beats a one-way door with 100%.

**Political resistance is architecture.** The stakeholder who can veto this is
as real a constraint as a database that cannot take the write load. Map them in
step 6, put them in the matrix in step 9, and design residuals for them —
a phased rollout that gives a nervous owner an off-ramp is a residual.

### The question that matters most here

At every gate, ask explicitly: *are we proceeding because we are ready, or
because we are impatient?* In greenfield, moving fast is cheap. Here, the cost
of the honest answer being "impatient" is the whole engagement.
