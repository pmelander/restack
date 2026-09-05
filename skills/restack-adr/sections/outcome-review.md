### Outcome review protocol

Revisiting a decision after it has had time to play out is the highest-value
and most-skipped part of ADR practice. Writing the decision builds
articulation; reviewing it is what actually calibrates judgement, because it is
the only step that tells you whether your reasoning was any good.

Run it at the ADR's review date, and always after an incident that touched the
decision.

#### 1. Read the ADR before asking anything

Specifically read what was *uncertain* at the time — the Context section's
fears and unknowns. The point of the review is to compare the prediction
against what happened, and that requires knowing what was actually predicted
rather than what everyone now remembers predicting.

Hindsight rewrites memory fast. People reliably recall having anticipated
things they did not.

#### 2. Establish what happened

- Was the decision actually implemented as written? Frequently it was not, and
  that is the finding — the ADR describes a system nobody built.
- Did the consequences in the Positive section materialise?
- Did the ones in the Negative section? Were they as bad as expected?
- What happened that appears in neither list?

That last question is the valuable one. Consequences nobody listed are where
the model of the system was wrong.

#### 3. If this decision implemented a residual, check it

- Did the residual actually reduce the vulnerability it was designed for?
  `docs/journey/stressor-iteration-history.md` has the before/after.
- Did any stressor it was supposed to clear occur anyway? If so, either the
  residual does not work as designed or the mechanism was misdiagnosed — both
  are worth knowing and neither is visible from the code.
- Did it clear anything unexpected? Compound protection is the mechanism this
  toolkit is built on, and observing it in production is much stronger evidence
  than predicting it in a matrix.
- Did the residual create new paths, and were those ever walked?

#### 4. Assess the reasoning, not just the outcome

This distinction is what makes the review worth running.

A good decision can have a bad outcome and a bad decision a good one. Judging
only by result teaches you to be lucky rather than to think. Ask separately:

- **Was the outcome good?**
- **Was the reasoning sound given what was knowable at the time?**

The four combinations mean different things. Sound reasoning with a bad outcome
means the world was uncertain — record it and change nothing about how you
decide. Poor reasoning with a good outcome is the dangerous case, because it
gets reinforced and repeated; name it explicitly as luck.

#### 5. Write it into the ADR

Append, never overwrite. The original stands.

```markdown
## Outcome review — YYYY-MM-DD

**Implemented as written:** yes | no — [what actually shipped]
**Outcome:** good | mixed | bad
**Reasoning, judged on what was knowable then:** sound | flawed — [why]

**What we predicted and got right:**
**What we predicted and got wrong:**
**What we did not predict at all:**

**Residual effectiveness:** [if applicable — did impact actually fall, did the
stressors recur, did it clear anything unexpected]

**What we would do differently:**
**What this changes about how we decide:** [or: nothing — the process worked]
```

#### 6. Act on it

A review that changes nothing was an exercise. Depending on what you found:

- The decision no longer holds → supersede it with a new ADR.
- The residual did not work → back to `/restack-stressor residues`; the
  mechanism was misdiagnosed.
- A consequence nobody predicted → a stressor nobody generated. Feed it into
  `/restack-stressor generate` as an `incident`-tagged stressor and check
  whether the matrix would have caught it.
- A pattern across several reviews → `/restack-patterns extract`.

#### Reviewing a set rather than one

When several ADRs come due together, read them as a group and look for the
pattern in the misses: consistently underestimating migration effort,
consistently over-trusting vendor roadmaps, consistently missing organisational
constraints. A single review tells you about one decision. A batch tells you
about how this team decides, which is the more useful thing and is invisible
one ADR at a time.
