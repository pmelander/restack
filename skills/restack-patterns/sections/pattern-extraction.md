### What qualifies as a pattern

The bar matters more than the format. A catalog of things somebody thought
sounded good is worse than no catalog, because it carries institutional
authority it has not earned.

**Three instances, independently chosen.** The same solution reached three
times, by people who were not simply copying the previous instance. Two is a
coincidence; copying is not evidence.

**A recurring problem, not a recurring shape.** The pattern is the
problem–solution pair. "We use queues" is not a pattern. "When a path depends
on a third party whose availability we do not control, we insert a queue and
fork an async settlement path" is.

**Known trade-offs.** If nobody can say what the solution costs, it has not
been used long enough to be a pattern. Every pattern write-up needs the case
against it.

**A stated context boundary.** Where does it stop applying? A pattern without
limits gets applied everywhere, and a pattern applied everywhere becomes an
anti-pattern. This is the field that most often distinguishes a real pattern
from an enthusiasm.

Reject the candidate if any of the four is missing, and say which. A rejected
candidate with a reason is more useful than an accepted one without evidence.

### Residuals are the richest source

The stressor loop produces residuals: discrete changes that answer a specific
mechanism. A residual that has worked across three engagements, against
different stressors, in different systems, is a pattern with unusually good
evidence behind it — you know what it defends against and you have the matrices
showing impact before and after.

When extracting from residuals, carry the provenance across:

- the **mechanism** it addresses, not just the stressor that prompted it
- which stressor classes it has cleared in practice
- what it **created** — the new actors and paths, which are the trade-off
- the terrain it was used in; a minefield residual may be over-engineering in
  greenfield

Check `docs/journey/stressor-iteration-history.md` for the impact numbers. A
pattern that can say "removed 5 to 7 matrix points across three systems" is in
a different class from one asserting a benefit.

### Types worth distinguishing

**Architectural** — recurring system design solutions. Saga for distributed
consistency, cache-aside with read replicas, queue-worker-DLQ.

**Decision** — how this organisation tends to decide. "We prioritise
operational simplicity over feature breadth in datastores." Valuable because it
is invisible to newcomers and shapes every evaluation.

**Technology** — stack choices that work here. Worth recording with *why they
work here*, since that is the part that does not transfer.

**Context** — patterns about the organisation itself. "Any vendor decision
needs six weeks for architecture board, so vendor-dependent residuals are
planned a quarter ahead." These are the ones nobody writes down and everybody
learns painfully.

### Extraction protocol

1. **Find the candidates.** From residuals in the iteration history, from
   `/restack-arch-learning patterns`, from ADRs that reached the same
   conclusion repeatedly.
2. **Verify the three instances.** Name them, with links. If you cannot name
   three, stop — say what you have and what would complete it.
3. **Find the problem underneath.** What was actually common? Frequently the
   three instances differ in the surface solution and share a mechanism; the
   mechanism is the pattern.
4. **Establish the context boundary.** Ask each instance's participants when
   they would *not* do this. Where they cannot answer, that is a limit nobody
   has found yet — say so rather than inventing one.
5. **Collect the trade-offs**, including the instance where it worked least
   well. A pattern with no recorded downside has not been examined.
6. **Write it up** using `templates/pattern-template.md`. That file is the
   canonical format — do not restate it here or invent a variant.
7. **Record effectiveness data** from the instances: what it cost, what it
   removed, how long it took to introduce.

### Writing it so it gets used

The catalog fails by being unusable more often than by being wrong.

- **Lead with the problem.** People arrive with a problem, not a solution name.
  A catalog indexed by solution name is browsable only by someone who already
  knows the answer.
- **Name the pattern after the problem it solves** where possible, or use the
  industry name if one is established — inventing local names for known
  patterns costs you every newcomer.
- **Include the "do not use when" prominently**, not as a footnote. It is the
  part that prevents the most damage.
- **Link the instances.** A reader's first question is "where have we actually
  done this?", and the answer is what converts a document into a decision.
