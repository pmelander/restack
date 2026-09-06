### Artifact consistency

A design that has been through several stressor iterations is described by many
documents — ADRs, an HLD, LLDs, a deployment guide, a runbook, a configuration
manifest. They drift. An ADR supersedes an earlier one's assumption and the
earlier one is never updated; an iteration adds two actors and the HLD keeps the
old container view; a deployment guide describes a topology a later decision
replaced.

This is not pedantry about documents. **A stale artifact is a defect waiting to
be implemented**, because somebody will follow it. On one real engagement the
*critical* finding of a design review was a deployment guide and an ADR
disagreeing about where a UI is hosted — an engineer following the guide would
have provisioned a resource the design had explicitly rejected, and broken the
ingress posture doing it.

Drift grows with document count, so it barely exists early and dominates later.
Run this pass on any design with more than a handful of ADRs.

#### What is authoritative

Establish the order before you start, because every finding here is "these two
disagree" and you need to know which one is wrong:

1. **ADRs** — decisions are the source of truth. A design document contradicting
   an accepted ADR is the design document being wrong.
2. **HLD and LLDs** — describe the system the decisions produced.
3. **Deployment, runbook, configuration manifest** — describe how it is operated.

The exception, and it matters: when a design document is right and the ADR is
stale, the finding is that **a decision was made without being recorded**. That
is worse than drift, because the reasoning is gone. Route it to
`/restack-adr create` or `/restack-adr update`, not to a documentation fix.

#### The six checks

**1. ADR against ADR.** Does a later decision invalidate an earlier one's
assumptions without the earlier being amended or superseded? Look for
supersession chains, amendments, and ADRs about the same actor or path. A
recorded invariant that a later ADR quietly changed is the most dangerous case,
because it reads as current.

**2. ADR against design docs.** Does every accepted decision appear in the HLD
and the relevant LLD? Take the ADRs since the last review and grep the design
documents for each decision's substance — not its number, which will match
whether or not the content followed.

**3. Actors against the design.** Every actor on a walked path and every column
in the matrix should appear in the HLD's component view. New actors introduced
by an iteration are the usual miss: they were added to the analysis and never to
the picture.

**4. Residuals against their records.** Every implemented residual should have an
ADR and appear in the HLD's residual table with what it defends against. A
residual with no record looks like unnecessary complexity to whoever inherits
it, and gets removed.

**5. Placeholders and empty evidence.** TBDs, empty measurement tables,
"provisional" values that have outlived their provisionality. An empty table
presented in a document with the authority of a filled one is worse than an
acknowledged gap — it reads as measured.

**6. Operational documents against the current design.** Does the runbook
describe actors that still exist, and does the deployment guide describe the
topology that was actually decided? These drift furthest because they are
written once, late, and rarely revisited.

#### Severity comes from who acts on it

Rate by **what happens if someone follows the stale document**, not by how far
apart the two documents are.

| | |
|---|---|
| **Critical** | An engineer or operator would take a wrong action — wrong topology provisioned, wrong procedure run in an incident |
| **Major** | A reader forms a materially wrong model of the system and would design against it |
| **Minor** | Cosmetic or historical drift nobody would act on |

A deployment guide is executed by someone under time pressure, so it earns
critical readily. A background section in an HLD almost never does.

#### Reporting

Report artifact findings **separately from system findings**, and say which
document is wrong rather than only that two disagree. Every finding needs the
authoritative source, the stale one, and the action someone would wrongly take.

```
AC-1  DEPLOYMENT.md §2.2 contradicts ADR-0041 on UI hosting
      Authoritative: ADR-0041 (SPA bundled into the BFF container)
      Stale:         DEPLOYMENT.md §2.2 (Azure Static Web Apps)
      Wrong action:  engineer provisions a separate resource, adds CORS,
                     and may expose a public endpoint the design excludes
      Severity:      Critical - the deployment guide is executed as written
      Fix:           rewrite §2.2 to the bundled topology
```

#### The pattern behind the findings

Once you have several, look at *when* they were introduced. Drift clusters
around iterations: a stressor iteration changes the design, the ADRs get
written, and the descriptive documents lag. If most findings date from one
iteration, the gap is a missing step in that loop rather than carelessness — and
the fix is to update the HLD as part of implementing a residual, not to review
harder afterwards.
