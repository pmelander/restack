### Extracting anti-patterns

An anti-pattern is a solution that keeps being chosen and keeps failing. The
second half is what makes it worth documenting — a bad idea nobody has is not a
risk.

#### The bar

**Three instances of the same failure**, as with patterns. One painful project
is a story, not an anti-pattern.

**A reason people keep choosing it.** This is the essential field and the one
usually missing. Anti-patterns persist because they look right at the moment of
decision — they are locally reasonable, cheap up front, familiar, or the option
that avoids a difficult conversation. An anti-pattern write-up that does not
explain the attraction will not prevent anything, because it does not address
the reasoning that produces it.

**Observable symptoms.** How would you know you are in one *now*, before the
consequences arrive? This is the field that gives the document its practical
value.

**A correct alternative.** Naming a failure without a way out just tells people
they are stuck. If there is no better option in some contexts, say that
explicitly — that is genuinely useful and rarely said.

#### Sources

- **Class B findings from design review** — a residual that was implemented and
  did not work. The mechanism was misdiagnosed, and if that misdiagnosis
  recurs, it is an anti-pattern.
- **Recurring miss types from `/restack-arch-learning`** — a way of thinking
  that keeps failing.
- **Superseded ADRs** — decisions repeatedly reversed after the same discovery.
- **Incidents with a common shape.**

The design-review class B route is the most productive, because those failures
come with the reasoning that produced them already written down.

#### Write it up

Use `templates/anti-pattern-template.md` — the canonical format.

Three things to get right in the writing:

**Describe the trap, not the people.** "Teams under deadline pressure choose
the shared database because it removes a coordination conversation" explains
the mechanism. "Teams take shortcuts" blames, and a document that blames does
not get read by the people who need it.

**Give it the symptoms early.** Someone consulting this is usually already
partway in, and wants to know whether their situation matches.

**Include the migration cost.** How expensive is it to get out, once in? That
number is the whole argument for avoiding it up front, and it is the one thing
that changes behaviour at decision time.

#### Anti-patterns specific to this method

Worth watching for in your own practice, because the toolkit has failure modes
of its own:

- **Residual inflation** — a residual per high cell instead of one per
  mechanism, producing defensive machinery nobody understands.
- **Matrix theatre** — an impeccable matrix built over a path map the team does
  not believe, because building the matrix felt like progress.
- **Comfortable stressors** — generation drifting toward technical stressors
  the team can already handle, so impact falls while exposure does not.
- **Residuals as forecasts** — reporting impact reduction from residuals that
  were proposed and never implemented.
- **Confidence by fatigue** — passing the confidence gate because discovery is
  tiring, not because the map is trusted.

Each of these makes the analysis *look* better while the system gets no safer,
which is the most expensive kind of failure this method can have.
