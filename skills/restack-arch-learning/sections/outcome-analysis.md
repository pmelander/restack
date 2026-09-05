### Outcome analysis

The whole point is a comparison: **what did we predict, and what happened?**
Without the first half you are describing events, not learning from them.

#### 1. Gather what was predicted

The predictions are already written down, which is why this skill depends on
the rest of the toolkit having been used:

| Source | The prediction it holds |
|---|---|
| `docs/adr/` | consequences, positive and negative, per decision |
| `docs/adr/` outcome reviews | what a prior review already established |
| `docs/stressor-analysis/` | which actors were vulnerable to what |
| `docs/journey/stressor-iteration-history.md` | how much impact each residual was expected to remove |
| `docs/journey/assumptions-register.md` | what was believed without evidence |
| `docs/reviews/` | what design review flagged, and at what severity |

**Read these before talking to anyone.** Hindsight rewrites memory reliably and
quickly; people recall having anticipated things they did not. A retrospective
run from memory produces a story in which the team was wiser than it was.

#### 2. Gather what happened

Incidents, outages, near-misses, the changes that took far longer than
estimated, the components that had to be rewritten, the costs that surprised
someone.

Include the **non-events**: the feared thing that never occurred. Those matter
because they are where effort may have been wasted defending against a stressor
that was never real.

#### 3. Compare — the four cases

For each significant event:

| | Meaning | What to do |
|---|---|---|
| **Predicted, happened, residual held** | the method worked | record it; this is the evidence the approach is worth its cost |
| **Predicted, happened, residual did not hold** | mechanism misdiagnosed | back to `/restack-stressor residues` |
| **Not predicted, happened** | a gap in the analysis | the highest-value finding — diagnose which gap |
| **Predicted, never happened** | possibly wasted effort, possibly a residual quietly working | distinguish, honestly |

The third row is the one to spend time on.

#### 4. Diagnose the misses specifically

"We did not think of it" is not a diagnosis. For each unpredicted event, work
out which mechanism failed:

- **Missing actor** — it was never a column in the matrix. Why? Usually an
  actor nobody owns: a scheduled job, a manual step, a partner system.
- **Missing path** — the failure ran along a path nobody walked. Almost always
  an error, retry, or recovery path.
- **Missing stressor class** — the category was never generated. Overwhelmingly
  organisational, regulatory, or human.
- **Stressor present, scored zero** — it was in the matrix and someone judged
  it did not reach this actor. Why was that judgement wrong?
- **Correctly analysed, consciously accepted** — not a miss at all. Check
  whether an ADR records the acceptance; if not, the gap is documentation.

Each diagnosis is a correction to how the next analysis runs, and that is the
output that compounds.

#### 5. Check the residuals that quietly worked

Look for stressors that occurred and caused no harm. Those are residuals
earning their cost, and nobody notices them because nothing happened.

Say so explicitly. Teams under cost pressure remove residuals precisely because
they have never seen them do anything, and this is the only record that they
did.

#### 6. Separate outcome from reasoning

The same distinction `/restack-adr review` makes, applied across the whole
history: a sound decision can have a bad outcome and vice versa. Judging on
results alone teaches the team to be lucky.

Across many decisions the pattern is what matters — and the dangerous cell is
**poor reasoning with good outcomes**, because it gets reinforced and repeated
until the luck runs out.

---

### Trends across time

One analysis tells you about one system. The value is in the series.

Look for:

- **Recurring miss types.** Consistently missing organisational stressors, or
  error paths, or third-party behaviour. This is the single most actionable
  output: it names the specific blind spot to correct.
- **Estimate bias.** Are effort estimates consistently low, and by roughly what
  factor? A team that knows its own multiplier estimates better immediately.
- **Iteration counts falling.** Fewer stressor iterations to reach acceptable
  impact suggests residual selection is improving.
- **Class C findings falling.** Fewer design-review findings that the matrix
  should have caught means the path maps are getting better.
- **Decisions revisited.** Which areas keep being superseded? That is where the
  problem was genuinely hard or the context keeps moving — both worth naming.

Report trends with the underlying data visible. A trend asserted without the
instances behind it is an opinion with a chart.
