### Discovery anti-patterns

Read these at the start of a session, and again at the point discovery starts
feeling finished — that feeling is itself one of the signals below.

**Trusting the docs.** Documentation describes the system as designed, or as
last written up. Logs, traces, code, config and direct observation beat it every
time. The evidence rules rate documentation Low for this reason; a path map
that is Documented end-to-end and Validated nowhere is a hypothesis with a
diagram.

**Interviewing one person.** Every actor accumulates tribal knowledge and each
person holds one slice. Cross-reference every significant claim against a second
source. Where two sources disagree, do not reconcile them into a tidy
description — the disagreement usually marks exactly where the system changed
and somebody's mental model did not.

**Stopping at the happy path.** The happy path is the best documented and the
least revealing. The error path, the timeout path, the partial-failure path and
the manual-intervention path are where the undocumented actors live, because
nobody designed them deliberately.

**Assuming symmetry.** A sending to B does not mean B only receives from A.
Polling, batch jobs, side channels, admin tools and manual interventions are
invisible until you go looking for them specifically.

**Designing while discovering.** The moment you start designing you stop
discovering, because you begin looking for evidence that confirms the design.
The tell is catching yourself pleased that a finding fits the plan. Finish
discovery first; note residual opportunities without developing them.

**Treating resistance as fixed.** Organisational resistance is a stressor, not a
boundary. Understanding *why* someone resists tells you which residual might
address it — a phased rollout, a shadow path, an approved-list-compatible
choice.

**Discovering forever.** The mirror image, and it looks like diligence.
Discovery that keeps finding new actors and never converges usually means the
**system boundary was never agreed**, not that the system is unusually complex.
The fix is not more discovery — it is settling the boundary as an explicit
decision: what is in scope for this aspiration, and what is a neighbouring
system we treat as one opaque actor with a known contract.

**Confidence by fatigue.** Declaring the map good because the team is tired of
discovery. The confidence gate exists to make that visible; the honest output
is `NEEDS_DISCOVERY` with a named unknown, not a summary written to let everyone
move on.

**Losing the surprises.** The findings that contradicted expectations are the
highest-value output of any session, and they are the first thing to evaporate
when the summary gets written. Record each one explicitly, along with what the
team believed beforehand — that pair is what makes the next system's
assumptions better.
