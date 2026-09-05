### Organisational resistance as stressors

Organisational forces belong on the **stressor list**, not the path map. The
path map describes how the system works; stressors describe the forces acting
on it. An architecture board that takes two quarters to approve a vendor
constrains the design exactly as hard as a database that cannot take the write
load — and it is far more likely to be the thing that actually stops delivery.

Teams that run this step routinely find their highest-impact stressor is a
process, not a technology.

#### 1. Map who is connected to this change

Go wider than the project's stakeholder list. Include:

- whoever **owns** each system on the paths you discovered — including the ones
  who did not ask for this work and get no benefit from it
- whoever can **veto**: architecture board, security, change advisory, legal,
  procurement, a regulator's relationship owner
- whoever **operates** it at 3am, who inherits every residual you add
- whoever **pays**, and on what budget cycle

The owner of an adjacent system who gains nothing and absorbs the risk is the
most commonly missed and most consequential.

#### 2. For each, establish three things

- **Primary concern** — cost, risk, compliance, territory, reputation,
  workload. Say which; "resistant" is not a concern.
- **Current position** — supportive, neutral, resistant, blocking.
- **The mechanism of their resistance** — a governance gate, a budget cycle, a
  headcount limit, decision paralysis, or a fear with a specific object.

The mechanism is what you can design against. "The EA board is difficult" is
gossip. "The EA board meets monthly and requires a security review completed
two weeks prior, so any new vendor costs six weeks minimum" is a stressor with
a shape.

#### 3. Translate each into a stressor

A stressor is a concrete scenario that can be walked against each actor. Apply
the same standard as technical stressors — a category cannot be walked.

| Resistance observed | Weak (a category) | Stressor (walkable) |
|---|---|---|
| EA vendor approval | "governance risk" | "The chosen queueing vendor is rejected at the architecture board; only the approved list is available, adding 6 weeks" |
| No budget | "funding constraint" | "Implementation must land with zero new licence spend this financial year" |
| Legacy team resists | "team resistance" | "The team owning the core ledger declines to expose a new endpoint; integration must work against the existing batch interface only" |
| Key person dependency | "key person risk" | "The one engineer who understands the settlement job leaves before cutover" |
| Change freeze | "release risk" | "A production change freeze runs from 1 November to 15 January; nothing ships in that window" |
| Regulator relationship | "compliance risk" | "The regulator requests evidence of the new control within 30 days of go-live" |

Tag each `organisational` so it stays visible in the matrix. At iteration three
it is easy to notice the analysis has drifted toward comfortable technical
stressors, and the tag is how you catch it.

#### 4. Hand off to the matrix

These go into `/restack-stressor generate` alongside technical stressors and get scored
against the same actors. That scoring is often surprising: a governance
stressor frequently hits more actors than any single technical one, because it
constrains every actor a residual might introduce.

#### Resistance is a stressor, not a fixed constraint

This is the part that changes outcomes. Treating resistance as immovable turns
it into a boundary on the design. Treating it as a stressor means asking the
normal next question — **what residual addresses it?** — and organisational
stressors have architectural residuals:

- **Phased rollout path** — gives a nervous system owner a visible off-ramp,
  and turns one irreversible decision into several reversible ones.
- **Shadow-mode path** — the new path runs alongside the old, writing nowhere,
  until the evidence exists. Converts an argument about risk into an
  observation.
- **Approved-list-compatible actor** — a residual built from what governance
  has already cleared, at some technical cost, is often better than a superior
  residual that arrives two quarters later.
- **Contract-and-version boundary** — lets a resistant team's system stay
  untouched behind a stable interface, so cooperation is needed once, not
  continuously.
- **Human-in-the-loop actor** — where a regulator or a nervous owner needs
  judgement in the path, making it explicit is more honest, and more
  defensible, than automating around it.

Understanding *why* someone resists tells you which residual to reach for. That
is not politics as a separate activity — it is architecture, and it changes the
path map.

#### Output

An organisational stressor list, each entry tagged `organisational`, with its
source stakeholder, the resistance mechanism, and the veto point if one exists.
Ready to inject into `/restack-stressor generate`.
