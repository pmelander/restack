### Architecture retrospective protocol

Different from a sprint retrospective. The subject is the *decisions* and the
*architecture*, over months, not the last two weeks of delivery. It needs a
longer lookback because architectural consequences arrive slowly.

#### Before the session

**Do the outcome analysis first.** Walk in with the predictions and the events
already assembled. A retrospective that opens by asking "so what happened?"
gets whatever the room remembers, which is reconstructed and flattering.

Prepare, and circulate beforehand:

- the decisions in scope, with what each predicted
- what actually happened, with dates
- the four-case comparison, already drafted
- the specific questions you want the room to resolve

Circulating in advance is what stops the session being spent on recall.

#### Who is in the room

The people who made the decisions, the people who operate the result, and the
people who had to work around it. That third group is routinely absent and is
usually the one holding the useful information — the workaround is evidence a
design did not fit.

#### Running it

**1. Establish the facts before the interpretations.** Present what was
predicted and what happened. Corrections are welcome; explanations are not, yet.
Separating these two phases is most of the facilitation.

**2. Take the misses one at a time.** For each unpredicted event, ask the room
to diagnose the mechanism — missing actor, missing path, missing stressor class.
Push past "we didn't think of it" to *why the process did not surface it*. That
is the difference between a retrospective and a confession.

**3. Ask what people knew but did not say.** Almost always somebody had a
concern they did not raise, or raised once and dropped. Ask directly: what did
you suspect that you did not push on, and what stopped you?

The answer is usually structural — no forum, no time, seniority, or a decision
that already felt settled. That is a fixable process finding and it is invisible
in any artefact.

**4. Check the residuals that worked.** Name the stressors that occurred and
caused no harm. Teams rarely notice these, and this is where the method earns
its keep visibly.

**5. Separate reasoning from outcome, out loud.** State that a bad outcome from
sound reasoning is not a failure, and mean it. Without that framing people
defend rather than examine, and the session yields nothing.

#### Facilitation notes

- **Blameless, and structurally so.** Ask what the process failed to surface,
  not who missed it. The moment it becomes personal, the information stops.
- **Protect the person who was wrong.** The most valuable contributor in the
  room is whoever made the call that did not work out. If they get punished for
  it, nobody volunteers next time and you lose the input permanently.
- **Watch for the seniority effect.** If the lead speaks first the room
  converges on their account. Have them go last.
- **Do not resolve everything.** A disagreement about why something failed,
  recorded honestly, is more useful than a consensus nobody believes.

#### Output

Not a list of feelings. Three things:

1. **Corrections to the method** — for each miss, what changes about how the
   next analysis runs. These are the compounding output.
2. **Actions with owners** — a specific residual to add, a path to walk, an ADR
   to write, a stressor class to add to the generation prompt.
3. **What to keep** — the practices that demonstrably worked, named, so they
   survive the next reorganisation.

Write to `docs/learning/retrospective-<date>.md`, and feed the corrections into
the places they act: new stressor classes into `/restack-stressor generate`,
missing actors into `/restack-discover paths`, recurring decisions into
`/restack-patterns extract`, capability gaps into
`/restack-capability-assessor`.

#### The test of whether it worked

A retrospective that produced no change to how the team works was a debrief.
Six months later, check: did the miss types actually change? If the same
category is still being missed, the retrospective identified it and the
correction never landed — and that is itself the finding for the next session.
