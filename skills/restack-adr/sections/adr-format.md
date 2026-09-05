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

## Context

[The forces at play. What made this decision necessary now? What constraints —
technical, organisational, regulatory — bound the option set? If this came out
of a stressor analysis, state which actor was vulnerable and to what.]

## Decision

We will [decision, active voice].

## Consequences

### Positive
### Negative
### Neutral

## Alternatives considered

### [Alternative]
- **Pros:**
- **Cons:**
- **Why rejected:**

## References
```

### The fields that are not standard ADR

Three fields exist because this toolkit produces decisions from stressor
analysis, and a decision that loses its link to the analysis loses the reason
it was made.

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
