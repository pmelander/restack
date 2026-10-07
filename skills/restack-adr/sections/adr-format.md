### ADR format

```markdown
# ADR-NNN: [Title — the decision, in active voice]

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-NNN
**Date:** YYYY-MM-DD
**Deciders:** [who actually decided, not who was informed]
**Reversibility:** Reversible | Costly to reverse | One-way door
**Addresses residuals:** [residual ids from the stressor analysis, or "none — not residual-driven"]
**Stressors addressed:** [the stressors this decision's residual clears, with their tags]
**Technical story:** [optional ticket reference]
**Review date:** [when to run /restack-adr review — default 6 months]
**Challenged by removal:** [only once challenged: YYYY-MM-DD, kept (D<n>): what would come back, by lens — `docs/stressor-analysis/ablation-<date>-<slug>.md`]
**Assumptions:** [settles A-<n>, ...; rests on A-<n>, ... | none]

## Context

[The forces at play. What made this decision necessary now? What constraints —
technical, organisational, regulatory — bound the option set? If this came out
of a stressor analysis, state which actor was vulnerable and to what.]

## Decision

We will [decision, active voice].

### Derived details

| Detail | Derived from | Overturnable |
|---|---|---|
| [an implementation detail the brief never decided] | [aspiration, constraint or ADR-NNN] | yes / no |

## Consequences

### Positive
### Negative
### Neutral

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| [HLD / LLD / deployment guide / runbook / config manifest / test strategy] | [the section and the claim] | updated / bannered / ticketed [ref] |

## Alternatives considered

### [Alternative]
- **Pros:**
- **Cons:**
- **Why rejected:**

## References
```

### The fields that are not standard ADR

The first three fields exist because this toolkit produces decisions from
stressor analysis, and a decision that loses its link to the analysis loses the
reason it was made. The last three exist because decisions change, and each
change leaves gaps in documents the ADR never touched.

**Reversibility.** Ask: if this turns out wrong in six months, what does undoing
it cost? *Reversible* — a config change, a swapped library behind an interface.
*Costly to reverse* — a schema migration, a vendor commitment with a notice
period. *One-way door* — a published contract partners depend on, a data model
other systems now read, anything that becomes an actor other paths route
through.

This is not decoration. **A one-way door gets an ADR whether or not anyone
asked for one**, and it justifies spending longer on alternatives. A reversible
decision documented at the same length is waste, and treating the two alike is
how ADR practice dies of ceremony.

**Addresses residuals / Stressors addressed.** When a decision implements a
residual, record which one and which stressors it clears. This is the trail
that makes `/restack-journey review` able to detect "residuals implemented
without documentation", lets an auditor connect a control to the harm it
addresses, and tells the next architect why a queue exists that looks
unnecessary from the code alone.

Write `none — not residual-driven` when the decision came from somewhere else.
An empty field is ambiguous; an explicit "none" is information.

**Review date.** A decision with no review date is never revisited, and
unrevisited decisions are how architectures rot while everyone follows them.

**Challenged by removal.** Added by `update` after `/restack-stressor ablate`
removed the decision's residual on paper and the architect kept it (ADR-028 in
the ReStack repository). One entry per challenge, newest last, separated by
`;`: the date, the gate's `D<n>`, what would come back if it went (cells and
the lens they land on, the aspiration's column named when it is hit), and the
report. **The field is absent until the decision is challenged**, so its
absence says something. The stressors listed at proposal time say why a
residual was added; this field says why it is still there, tested against the
design as it now stands. That is the line an inheritor needs before deleting
something that looks unnecessary.

**Assumptions.** Mandatory, on `create` and on every `update` (ADR-031 in the
ReStack repository). `settles` lists the register rows this decision answers;
`rests on` lists the open rows it depends on. Write `none` when it touches no
row: as with residuals, an explicit "none" is information and an empty field
is not. Find the candidates with `journey.py assume touching` (*Journey
Files*); the architect confirms each, and each settled row's status is
written with `assume status`. A decision whose open `rests on` rows are never
settled is a decision resting on beliefs, and the register's summary counts
those rows as load-bearing.

**Knock-on changes.** Mandatory, on `create` and on every `update`. List every
descriptive document the decision invalidates (HLD, LLD, deployment guide,
runbook, configuration manifest, test strategy) and what happened to each **in
the same step**: updated, bannered as stale, or ticketed with a reference.
"None" is a valid answer only after you have looked: grep `docs/` for the
mechanism the decision changes. ADRs are read when someone asks why; the
deployment guide is read by whoever deploys, and a guide written before a
pivot will be followed to the letter. In one field session, 84% of a
consistency review's findings dated from a single pivot whose ADR touched none
of the four operational documents written before it.

**Derived details.** Writing an ADR precisely surfaces details the brief never
decided: tear down only on an explicit OFF and not on staleness, jitter the
re-enable, break-glass may only move towards *less* of the feature. Record each
one as *detail · derived from · overturnable*, so the architect can see what
was decided on their behalf and overturn it. **A derived detail that is a
one-way door, or that you hold at Low confidence, is not a derived detail. It
is a decision brief: issue it and STOP.** `/restack-journey review` lists the
overturnable rows still awaiting the architect's confirmation.

**Traceability claims.** Any promise of replay, audit or reconstruction ("we
can replay against the exact bytes", "every change is traceable") names its
mechanism: which artifacts, where they live, and **how long they are kept**.
Then check the retention against the promise. An inherited retention rule that
deletes the bytes after five days defeats a replay promise silently, and
nothing fails until the day someone needs the replay.

### Writing the sections well

**Context is the field that decays first and matters most.** In two years the
decision will be obvious and the reason will be gone. Write down what was
uncertain, what you were afraid of, and what you did not know — the things that
feel too obvious to record are exactly the ones that will not survive.

**Alternatives must be real.** Two or three, each one somebody could have
chosen. A strawman alternative is worse than none: it makes the decision look
examined when it was not, and it misleads the person who later wonders whether
the obvious option was considered.

**Negative consequences must be honest.** An ADR with an empty Negative section
is a sales document. Every decision costs something; if you cannot name the
cost, you have not finished thinking. This section is what the person
inheriting the system will search for first.

### Numbering and naming

`docs/adr/ADR-NNN-title-in-kebab-case.md`, zero-padded to three digits.

Take the next number by scanning existing files, not by counting them — a
deleted or reserved number makes a count wrong, and two ADRs sharing a number
is a mess to unpick. If the next number is already taken (a colleague's
unmerged branch), take the one after it and say so rather than renumbering
someone else's work.

### Superseding

Never edit a decision away. Set the old ADR's status to
`Superseded by ADR-NNN`, leave its content intact, and have the new ADR's
Context explain what changed — a new stressor, a failed assumption, an
environment that moved. The pair together is the useful artifact: it shows the
thinking evolving, which is the thing a single up-to-date document can never
show.

### Decision-point accounting (before any amend, supersede or deprecate)

An old ADR usually protects against more than its title says, and the extra
protection was never written down as its purpose. Retire it whole and you
retire that too. So before choosing a mechanism, account for it point by point,
and write the table into the new ADR, or into the dated note when deprecating:

| # | Decision point in ADR-NNN | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| 1 | [one decision, as the old ADR states it] | holds / replaced by ADR-x / withdrawn | [the failure, concretely] | [ADR, mechanism or test] |

1. List the old ADR's decision points one by one. Read the body, not only the
   Decision heading: constraints stated in Context or Consequences are decision
   points too.
2. Mark each one *holds*, *replaced by ADR-x* or *withdrawn*.
3. **For every withdrawn row, answer: what failure did this prevent, and what
   prevents it now?** Read the point against the *current* contracts, not
   against the old ADR's own framing.

If the answer for any row is "nothing", **STOP**. Issue a decision brief, with
options to keep that point, replace it, or accept the gap and register it,
before superseding. Three supersessions in one field batch each removed a
protection nobody had recorded: an alert for "applying against the business's
off", a response field that now contradicted a byte-identical contract, and a
gate before a customer-affecting mode a neighbour depended on. All three were
visible only point by point.

### Amendments that contradict the body

An amendment that changes behaviour the body still specifies goes **at the top,
as a banner**, not at the end. Then strike or mark each contradicted passage
inline (`~~old~~ — superseded by amendment YYYY-MM-DD, see banner`). A developer
reads the body. Amendment by footnote leaves the old specification looking
current.

Before writing an amendment, grep later ADRs for the mechanism it describes. An
amendment that describes a mechanism a later ADR already superseded is stale on
arrival.
