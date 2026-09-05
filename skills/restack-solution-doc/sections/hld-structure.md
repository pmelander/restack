### High-level design structure

The HLD's job is to let someone who was not in the room understand what the
system does, how change flows through it, and why it is shaped this way. Write
it in the toolkit's vocabulary — actors, intentions, paths, residuals — because
that is the vocabulary the analysis produced and translating it into generic
box-and-line language loses the reasoning.

```markdown
# High-Level Design — <system>

**Status:** Draft | Agreed | Superseded
**Date:**    **Authors:**
**Aspiration:** [one sentence — what this system is for]
**Terrain:** Greenfield | Brownfield | Oilfield | Minefield
**Based on:** [path maps, stressor matrix iteration N, ADRs NNN-NNN]

## 1. Aspiration and scope
## 2. Context — what this system sits between
## 3. Actors
## 4. Paths
## 5. Residuals and what they defend against
## 6. Data
## 7. Cross-cutting concerns
## 8. Decisions and open questions
## 9. What this design does not do
```

#### 1. Aspiration and scope

The aspiration verbatim from the journey state — not a restatement. Then the
boundary: what is inside this system, and what is a neighbouring system treated
as an opaque actor with a contract. The boundary is the single most useful line
in the document and the one most often left implicit.

#### 2. Context

What this system sits between. Who sends intentions in, where they go out.
Keep it to one diagram and a paragraph; the detail belongs in Paths.

#### 3. Actors

A table, not prose. For each: name, responsibility in one line, stateful or
stateless, and who owns it. State ownership explicitly — an actor with no owner
is an operational problem the design is quietly creating.

Mark which actors are **new**, which are **existing**, and which are
**residuals** introduced by the stressor analysis. That third category is the
one a reader will otherwise mistake for over-engineering.

#### 4. Paths

The heart of the document. For each significant path: the triggering intention,
the actors in sequence, where the intention resolves, and the failure behaviour.

Include the paths people skip — the error path, the retry path, the async
settlement path, the path taken during partial outage. A HLD documenting only
happy paths describes a system that does not exist.

For each path, state the **consistency and latency expectations**. A path
described without them is a path nobody can operate or test against.

#### 5. Residuals and what they defend against

This section is what makes the document worth keeping.

For each residual in the design: what it is, which stressors it clears, and
which ADR records the decision. Without this, every residual looks like
unnecessary complexity to whoever inherits the system — and the first thing a
new team does with unexplained complexity is remove it.

```markdown
| Residual | Shape | Clears | ADR |
|---|---|---|---|
| Payment-intent queue | new actor + async settlement path | provider outage, load spike, AZ loss, audit-during-outage | ADR-014 |
```

Also state what each residual **created**: the new actors and paths it
introduced, which are themselves walkable and stressable.

#### 6. Data

What data exists, which actor owns each piece, what consistency guarantee each
path needs, and how the schema evolves. Ownership is the field that prevents
the most expensive class of future defect.

#### 7. Cross-cutting concerns

Security posture and trust boundaries, observability (specifically: how you
would know a path is failing), and the operational shape — deploy, rollback,
scale. One or two paragraphs each; depth belongs in the LLD and the runbook.

#### 8. Decisions and open questions

Link the ADRs rather than restating them. Then list the open questions
explicitly, with owners — the assumptions register is the source.

#### 9. What this design does not do

An explicit non-goals list. It prevents the most common misreading of any HLD,
which is that everything unmentioned is either included or forgotten. It also
records scope decisions that were real choices, so nobody relitigates them by
accident.

---

### Writing it

**Ask before writing, one question at a time.** What is the aspiration, who
uses it, what already exists, what must not break. If a stressor analysis
exists, most of this is already recorded — read `docs/journey/journey-state.md`,
`docs/discovery/` and `docs/stressor-analysis/` first and confirm rather than
re-ask. Re-asking questions the journey already answered is how architects stop
trusting the tooling.

**The evidence rules apply.** In brownfield terrain, an HLD statement about how
an existing actor behaves is a claim needing a source. Mark unverified ones as
assumptions inline rather than letting the document's confident tone launder
them into facts — that laundering is precisely how a design review later finds
"critical issues" that were beliefs all along.

**Length is not the goal.** A ten-page HLD that nobody reads is worse than three
pages that everybody does. Cut anything a reader could get from the code.
