### Writing findings

A finding that cannot be acted on is noise, and a review full of noise trains
people to skim reviews.

#### Every finding needs four things

1. **Where** — the actor, the path, the hop. "The design has a coupling
   problem" is not a finding; "Order Service reads the Inventory table directly,
   so an inventory schema change breaks checkout" is.
2. **What breaks** — the concrete failure, with the conditions that trigger it.
3. **Evidence** — what you read, observed, or traced. The evidence rules apply
   in full: a finding inferred from a component's name is a question, not a
   finding, and should be written as one.
4. **What to do** — a specific change, or an explicit "needs investigation" with
   the investigation named.

#### Severity

Rate by consequence, not by how much it offends you.

| | Meaning |
|---|---|
| **Critical** | Will cause data loss, a breach, or an outage of a path serving the aspiration. Fix before build. |
| **Major** | Will cause real pain at expected load or during expected change. Fix before it becomes load-bearing. |
| **Minor** | Costs effort or elegance but not correctness. Fix when convenient. |
| **Question** | You do not have enough evidence to call it. Say what would settle it. |

**Use Question honestly and often.** A reviewer who converts every uncertainty
into a Major finding gets tuned out, and the tuning-out is permanent. The
Question class is what keeps the Critical class credible.

Severity is not a vote on how interesting the problem is. A dull dual-write is
Critical; an inelegant module boundary is Minor.

#### Say what is right, too

Name two or three things the design gets right, specifically — not as
encouragement, but because a review that lists only defects gives the reader no
way to tell which parts to preserve when they start changing things. "The
outbox on the settlement path is correct and should not be removed while
refactoring" is useful information.

---

### The review report

Write to `docs/reviews/design-review-<scope>-<date>.md`.

```markdown
# Design review — <scope>
**Date:** YYYY-MM-DD   **Reviewer:**
**Design reviewed:** [document or code, with commit or version]
**Stressor analysis:** [iteration N, dated] | none — see limitations

## Verdict
[Ready to build / Ready with conditions / Not ready — one line, then the reason]

## Matrix cross-check
[Finding distribution across classes A/B/C/D and what that distribution means.
See matrix-crosscheck.md. This section comes before the findings because it
often changes what the findings mean.]

## Findings
### Critical
### Major
### Minor
### Questions

## What this design gets right

## Limitations of this review
[What you could not assess and why — no access, no data, no analysis to check
against. Reviews get quoted later as though they were exhaustive; this section
is what stops that.]

## Recommended sequence
[Ordered by what unblocks the most, not by severity alone.]
```

#### The verdict must be a real judgement

"Ready with conditions" requires naming the conditions and who closes them.
A review that ends without a verdict transfers the decision back to the person
who asked for the review, which is the one thing they were trying to avoid.

#### Ordering recommendations

Order by what unblocks the most downstream work, not strictly by severity.
A Major finding that invalidates three Minor ones goes first. A Critical finding
whose fix depends on a discovery task goes after that task.

Where several findings share a cause, say so and give the cause once. Five
findings that are all the same missing residual is one recommendation, not five
— and presenting it as five overstates the work and hides the shape of it.

#### The failure this report format guards against

A review that lists twenty findings with no verdict, no ordering, and no
limitations is a document that makes the reviewer safe and the reader stuck.
The point is a decision the team can act on, not a demonstration of scrutiny.
