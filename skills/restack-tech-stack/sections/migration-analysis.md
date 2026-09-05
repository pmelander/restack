### Migration analysis

Most proposed migrations should not happen. Start from that position and make
the case overcome it, because the costs of migrating are concrete and arrive
early while the benefits are estimated and arrive late.

#### 1. Establish what problem this actually solves

Ask, and do not accept an abstraction: which specific pain, experienced by
whom, how often, at what cost? Acceptable answers name an incident, a recurring
delay, a cost line, or a capability that is genuinely blocked.

Unacceptable answers, all common:

- "It is end of life" — when? What actually breaks on that date? Frequently
  nothing, for years.
- "It does not scale" — at what load? Have you measured, or is this folklore?
- "It is legacy" — this describes its age, not a problem.
- "Everyone is moving to X" — that is not a requirement.

**If there is no concrete pain, stop here.** That is the finding, and it is a
good one. Say it plainly.

#### 2. Check whether the pain is actually about the technology

This is the step that saves the most wasted quarters. Very often the pain is a
design problem wearing the technology's name: the database is not slow, the
query pattern is; the framework is not the bottleneck, the synchronous chain
around it is.

Migrating relocates that problem into an unfamiliar system, where you get to
rediscover it with less expertise.

Check the stressor matrix. If the vulnerability sits on a path rather than in
the component, a residual is cheaper than a migration and usually faster.

#### 3. Cost the migration honestly

Teams estimate the build and forget everything around it:

- **Dual running.** Both systems live at once, for longer than planned, with
  both operational costs and the synchronisation between them.
- **Data migration**, including the historical data nobody remembers until
  someone needs a report from three years ago.
- **Every integration.** Each consumer of the old system needs work, and each
  belongs to someone with their own priorities. This is where migrations
  actually stall — not on technology, on other teams' roadmaps.
- **Capability ramp.** The team is slower for months. Real, rarely costed.
- **Opportunity cost.** What is not being built during this.
- **The long tail.** The last 5% takes as long as the first 80%, because it is
  the undocumented edge cases the original system quietly handles.

Multiply the honest estimate. Then ask what the same effort would buy if spent
directly on the pain from step 1.

#### 4. Design the migration as paths, not phases

If it proceeds, this is where the toolkit's vocabulary earns its keep. A
migration is a change to paths, and it should be walked like any other.

- **Strangler path** — new intentions route to the new system while old ones
  continue on the old. The two coexist by design, not by accident.
- **Shadow path** — the new system receives real traffic and writes nowhere,
  so you compare behaviour under real load before committing. This is the
  highest-value migration residual and the most often skipped.
- **Reversible cutover** — can you route back after switching? If not, you have
  a one-way door and it needs an ADR and a much higher confidence bar.
- **Data ownership during transition** — which system is authoritative, when?
  Dual-write periods are a partial-failure defect unless designed with an
  outbox or equivalent.

Then walk the migration paths and stress them. A migration is a period of
elevated fragility; running it through `/restack-stressor walk` is exactly the
kind of thing the analysis exists for, and it routinely surfaces the rollback
nobody had planned.

#### 5. Define the abort condition in advance

What would tell you to stop, and who decides? Migrations without a stated abort
condition run to completion regardless of evidence, because by the time it is
going badly, too much has been spent to admit it. Write the condition down
before starting, while it is still cheap to be honest.

#### Output

A recommendation — **migrate / do not migrate / fix in place** — with the
honest cost, the alternative use of that effort, the migration path design if
proceeding, and the abort condition. Record it as an ADR: a rejected migration
is exactly the kind of decision that gets proposed again in eighteen months,
and the record is what stops it being re-argued from scratch.
