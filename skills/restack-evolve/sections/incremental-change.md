### Incremental change

The goal is a sequence of small, safe, individually valuable steps rather than
one large change that is correct only when complete. Big-bang changes fail for
a structural reason: they cannot be validated until the end, so every
assumption made at the start is tested simultaneously at the point of maximum
commitment.

#### The patterns

**Strangler fig.** New intentions route to the new implementation while
existing ones continue on the old; the old shrinks until it can be removed.
Requires a routing seam — usually the hardest part, and worth building first
even though it delivers nothing visible.

**Branch by abstraction.** Introduce an abstraction over the current
implementation, add the new one behind it, switch, remove the old. Keeps the
system working throughout and keeps the change on the main line rather than in
a long-lived branch that diverges.

**Shadow mode.** The new path receives real traffic and writes nowhere.
Compares behaviour under real load before any commitment. The highest-value and
most-skipped step, because it feels like work that produces nothing — while
being the only step that converts an argument about risk into an observation.

**Feature flags.** Decouple deploy from release, and make the change reversible
without a deploy. Flags are debt: give each one an owner and a removal date, or
the codebase accumulates permanent conditionals nobody dares delete.

**Expand and contract** (for schema and contract change). Add the new field or
endpoint; migrate consumers; remove the old. Three deploys instead of one
coordinated deploy, and each is individually safe.

**Parallel run.** Both implementations process everything, outputs compared,
discrepancies investigated before cutover. Expensive, and correct where being
wrong is unacceptable — settlement, billing, regulated calculations.

#### Designing the sequence

1. **Name the end state and the first step separately.** The first step should
   be valuable and safe on its own. If the only valuable state is the end
   state, the plan is a big bang wearing increments.
2. **Build the seam first.** Routing, abstraction, or flag. It delivers nothing
   visible and makes everything after it reversible.
3. **Order by risk retired per step.** Do the step that resolves the biggest
   unknown early, while abandoning is still cheap.
4. **Make each step reversible**, and state how. "Revert the deploy" stops
   being true the moment a migration runs — so say exactly where reversibility
   ends.
5. **Define the abort condition** before starting, while honesty is still
   cheap. Migrations without one run to completion regardless of evidence,
   because by the time it is going badly, too much has been spent to stop.
6. **Plan the cleanup as a step, not an intention.** The old path, the flag,
   the parallel run — each needs an owner and a date. Uncompleted migrations
   are the most common source of accidental brittleness: two implementations,
   both live, neither fully trusted.

#### Where increments genuinely do not work

Say so rather than forcing the frame. Some changes are atomic — a cryptographic
migration, a regulatory cutover with a fixed date, a change where running both
systems is itself the risk. For those, the incremental work goes into
**rehearsal**: test the cutover repeatedly in a lower environment, and make
failure recoverable rather than making the change gradual.

#### Coaching this

When walking an architect through a change, the useful questions are:

- What is the smallest step that is valuable on its own?
- Where is the seam, and does it exist yet?
- What would you learn from step one that could change steps two and three?
- After step one ships, what can you no longer undo?
- What would tell you to stop, and who decides?
- Who removes the old path, and when?

The last question is the one that never gets asked, and its absence is why
systems accumulate half-finished migrations.
