### Evaluation dimensions

Score every candidate across all seven. Teams reliably evaluate the first
dimension well and the rest not at all, and the ones they skip are where the
regret comes from.

**1. Fit for the actual requirement.** Not "is it good" but "does it do the
specific thing this system needs". Name the requirement first, then check.
Reversing that order is how a shortlist gets assembled from reputation.

**2. Fit for the residuals.** The one this toolkit adds, and the one most often
decisive. The stressor analysis said this design needs a queue with ordering
guarantees, or an outbox, or per-tenant isolation. Which candidates express
those cheaply, and which require you to build the residual yourself? A
technology that makes a required residual awkward is a bad fit however good it
looks in isolation.

**3. Team capability.** Does the team have production experience with this —
not tutorial experience, production? A capability gap is a stressor on every
path depending on the technology, and it belongs in the matrix, not in a
footnote. "We'll learn it" is a real option, but it is a schedule and risk
decision that should be made deliberately.

**4. Operational cost.** Who runs it at 3am, how is it upgraded, how does it
fail, and what does it look like when it is unhealthy? Managed versus
self-hosted is usually a larger decision than the technology choice itself, and
it is frequently made by accident.

**5. Organisational constraint.** Is it on the approved list? Does it need
procurement, a security review, an architecture board slot? Governance is a
stressor with a shape — six weeks of approval is a real cost that belongs in
the comparison, not a footnote appended after the decision. See
`/restack-discover organisation`.

**6. Total cost over the horizon.** Licence, infrastructure, and the
operational and training cost, at expected scale, over the period the decision
has to survive. Free technologies with expensive operations are common and the
cost lands on a different budget, which is why it goes unnoticed until it does
not.

**7. Exit cost.** If this turns out wrong in two years, what does leaving cost?
This is the reversibility rating and it should be stated explicitly for every
candidate. A slightly worse technology with a cheap exit often beats a better
one with lock-in, particularly under uncertainty — and uncertainty is the normal
condition.

#### Producing the comparison

A matrix with the dimensions as rows and candidates as columns. Score, and show
the reasoning — an unexplained score is an opinion in a table.

**Weight the dimensions before scoring**, and say so. Weighting afterwards is
how a decision already made gets dressed as an analysis, and everyone can tell.

Always include the **do-nothing option**: keep what you have, or use what is
already in the stack. It frequently wins, and a comparison that omits it has
assumed its own conclusion.

#### Bias checks

Ask these out loud. They are uncomfortable, which is why they work.

- **Why are you drawn to this?** Hype, genuine fit, or the fact that it is
  interesting to learn? All three are real forces; only one is a reason.
- **Would you choose it if nobody would ever know you had?** Résumé-driven
  development is real and rarely admitted.
- **What is the boring option**, and what specifically does it fail to do?
  If the boring option cannot be dismissed on a concrete requirement, it wins.
- **Who benefits from you choosing this?** Vendor content, conference talks and
  benchmark posts are marketing with citations.
- **Is this solving a problem you have, or one you have read about?**

#### The output is a recommendation, not a survey

State a recommendation with the reason mapped to the stated requirement, say
what would change your mind, and rate confidence. A comparison matrix handed
over without a recommendation pushes the decision back to whoever asked, which
is what they were trying to avoid.

Where the top two are genuinely close, that is a decision brief, not a coin
toss made on the architect's behalf.
