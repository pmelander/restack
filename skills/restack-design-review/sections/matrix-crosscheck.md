### Cross-checking findings against the stressor matrix

This is what makes a review in this toolkit different from a best-practice
checklist, and it is the step to run first when a stressor analysis exists.

A design review that only lists defects tells you about this design. A review
that asks **why the analysis did not already catch each defect** tells you about
your analysis — and that compounds, because the analysis gets used again on the
next system.

#### Classify every finding

For each finding, read `docs/stressor-analysis/` and
`docs/journey/stressor-iteration-history.md`, then place it in one of four
classes. State the class next to the finding in the report.

**A — The matrix caught this; the residual is missing.**
The vulnerability is in the matrix, a residual was identified, and the design
does not contain it. This is not a review finding at all — it is an
implementation gap. Route it to `/restack-adr` (was the residual deliberately
rejected, and if so where is that decision?) rather than treating it as a new
discovery.

**B — The matrix caught this; the residual is present but does not work.**
The design contains the residual and the weakness is still there. The mechanism
was misdiagnosed. This is the most valuable class: it means the *reasoning* in
`/restack-stressor residues` was wrong, not just the implementation. Route back
to residual identification, not to a patch.

**C — The matrix should have caught this and did not.**
The actor is on a walked path, the stressor is one that generation should have
produced, and neither appears. Ask which: a **missing actor** (never made it
into a column), a **missing path** (usually an error or async path nobody
walked), or a **missing stressor class** (almost always organisational,
regulatory, or human — the categories teams skip).

Record which gap, because that is a correction to how the next analysis runs.

**D — Genuinely outside the analysis.**
The design changed after the last iteration, a new dependency arrived, or the
environment moved. Legitimate. Feed it back as a new stressor and note that the
matrix is stale.

#### What the distribution tells you

The mix matters more than any single finding.

| Mostly | Means |
|---|---|
| **A** | The analysis is sound; delivery is not following it. An organisational problem, not an architectural one. |
| **B** | Residuals are being chosen without diagnosing the mechanism — pattern-matching to a familiar fix. |
| **C** | The path map is incomplete. Go back to `/restack-discover`, not forward to fixes. |
| **D** | The matrix is simply stale. Re-run the loop. |

**A review that is mostly class C is a discovery finding wearing a design
review's clothes.** Say so plainly. Fixing the individual findings leaves the
cause in place, and the same review will produce a fresh set of class C
findings next quarter.

#### When there is no stressor analysis

Say so, and say what it costs: without it you are reviewing against general
principle rather than against this system's actual vulnerabilities, so the
review will find what is conventionally wrong and miss what is specifically
dangerous here.

Then run the review anyway — a review is still worth having — but recommend
`/restack-stressor` before the next one, and treat any critical finding as
provisional until it can be checked against a matrix.

Do not silently downgrade to a checklist review. The whole argument of
[ADR-006](../../../docs/adr/ADR-006-exclude-risk-assessor-skill.md) is that
enumerated checks produce false confidence; a review that quietly becomes one
inherits exactly that problem.
