### Assessing brittleness

Brittleness is how hard the architecture makes change. It is distinct from
vulnerability — the stressor matrix measures what breaks the system *now*;
brittleness measures what will make it expensive to *fix*.

The two interact, and that interaction is the reason this assessment matters: a
brittle architecture cannot absorb residuals cheaply, so a matrix full of known
vulnerabilities stays unaddressed because every fix is a project. **Brittleness
is what stops the stressor loop converging.**

#### Measure with the change, not the opinion

Do not ask whether the architecture is flexible; everyone says yes. Take
concrete changes and trace them.

1. **Name three to five changes the system is plausibly going to be asked for
   in the next year.** Real ones, from the roadmap or the stakeholders — not
   hypotheticals chosen to make a point.
2. **Trace each through the path map.** Which actors change, which contracts
   change, which teams must coordinate, what data must migrate, what must be
   deployed together.
3. **Score each on four axes:**

| Axis | Question |
|---|---|
| **Blast radius** | how many actors must change together? |
| **Coordination** | how many teams must agree, and how many release cycles? |
| **Reversibility** | can it be rolled back after it ships? |
| **Confidence** | would you deploy it on a Friday? |

The last one is not a joke. It is a fast proxy for how well the team
understands the blast radius, and the honest answer is informative.

A change touching one actor, one team, reversible, deployable Friday, is cheap.
One requiring four teams and a coordinated deploy is not — and if that describes
the *typical* change, the architecture is brittle regardless of how clean it
looks in a diagram.

#### The usual sources

- **Undeclared coupling** — shared tables, filename conventions, ordering
  assumptions. Change propagates by surprise because the dependency was never
  declared.
- **Deployment coupling** — components that must ship together. All the cost of
  distribution, none of the independence.
- **Data model rigidity** — a schema every consumer reads directly, so no field
  can change without coordination.
- **Missing seams.** Nowhere to substitute an implementation, so every change is
  surgery on the original.
- **Knowledge concentration.** One person understands it. This is brittleness
  even when the code is clean, and it is the most common form.
- **Absent tests around the change surface.** No safety net means every change
  is slow because it is scary, and slow-because-scary is indistinguishable from
  brittle in practice.
- **Irreversible decisions accumulating** — each one-way door narrows the space
  of cheap future change.

#### Report it as cost, not as a grade

A brittleness score is an abstraction nobody acts on. What moves people is:
"adding a new payment provider touches six actors across three teams and cannot
be rolled back after the schema migration — roughly a quarter."

Then rank remediation by **which brittleness blocks the residuals the matrix
already wants**. That is the ordering that matters: fixing brittleness in an
area with no known vulnerabilities is tidying, while fixing the coupling that
prevents an already-identified residual unblocks real risk reduction.

#### Feed it back

Brittleness findings belong in the matrix. "Change requires coordinating three
teams" is an organisational stressor — it makes every residual slower to
introduce, which raises effective impact across the board.

Where a needed residual is blocked by brittleness, that is a decision brief:
fix the brittleness first, apply a weaker residual now, or accept the
vulnerability with an ADR recording the trade.
