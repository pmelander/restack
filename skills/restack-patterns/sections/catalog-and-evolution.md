### Catalog structure

```
docs/patterns/
  README.md                    index, organised BY PROBLEM
  architectural/
  decision/
  technology/
  context/
  anti-patterns/
  deprecated/                  kept, with why they were retired
```

**The index is organised by problem, not by solution name.** People arrive with
a problem. A catalog browsable only by someone who already knows the answer is
a catalog for people who do not need it.

```markdown
## I need to...
- ...survive a third party being unavailable    -> queue-and-async-settlement
- ...keep two datastores consistent             -> transactional-outbox
- ...roll out a change a stakeholder fears      -> shadow-then-phased-rollout
- ...scale reads without touching writes        -> cache-aside-with-replicas
```

Keep `deprecated/` rather than deleting. A retired pattern with its reason is
what stops it being rediscovered enthusiastically in two years.

Each entry carries: maturity (**Experimental / Proven / Deprecated**), the
instances that justify it, last-reviewed date, and effectiveness data.

---

### Tracking effectiveness

A catalog nobody measures becomes a set of assertions with institutional
authority, which is worse than nothing.

For each pattern, track:

- **Adoption** — where it has been used since being catalogued.
- **Outcome** — did it work? Where it did not, why? The context boundary is
  usually what needs correcting.
- **Cost to introduce** — the estimate people most want and least often have.
- **Impact removed**, where it came from a residual — the matrix has the
  before/after numbers.
- **Abandonments** — where it was tried and backed out. The most informative
  data point in the catalog and the one nobody records, because backing out
  feels like a failure rather than a finding.

Where a pattern has been used three or more times since cataloguing, the
outcomes are stronger evidence than the original three instances. Update the
write-up from them.

A pattern that has been in the catalog for a year with no adoption is telling
you something: either it is unfindable, it is not a real pattern, or the
problem stopped occurring. Investigate rather than leaving it.

---

### Evolving the catalog

Patterns are not permanent. The context that made one correct changes, and a
catalog that only grows becomes a liability — new joiners cannot tell live
guidance from archaeology.

Run this quarterly, or when the environment shifts.

**Promote.** Experimental → Proven when the outcome data supports it. Say what
evidence justified the promotion.

**Amend.** Most updates are to the **context boundary** — a limit discovered by
someone applying it where it did not fit. That failure is valuable; record it
as a boundary correction rather than a failure of the pattern.

**Deprecate** when the context that made it right has gone: the constraint
lifted, the platform changed, a better approach arrived. Move it to
`deprecated/` with the reason and the replacement. **Never delete** — the
reasoning is what stops the rediscovery.

**Split** when a pattern is being applied to two genuinely different problems.
The forced generality is what makes its context boundary vague.

**Merge** when two entries turn out to be the same mechanism.

#### Review questions

For each pattern, once a quarter:

- Has it been used since the last review? Successfully?
- Does the context boundary still hold, or has someone found a new limit?
- Is the trade-off list still honest, or has the cost changed?
- Would you still recommend this to a team starting today?
- If it is Deprecated, is the replacement actually named?

#### The failure to guard against

A pattern library becomes **policy by accident**. It is written as "this worked
three times", it gets read as "this is how we do things", and eventually it is
enforced in review as though it were a standard.

Guard against it in the writing: keep the context boundary prominent, keep the
trade-offs honest, keep the instance links visible so a reader can judge
whether their situation matches. A pattern is evidence, not an instruction —
and the moment it is enforced without regard to context, it has become one of
the anti-patterns in the same catalog.
