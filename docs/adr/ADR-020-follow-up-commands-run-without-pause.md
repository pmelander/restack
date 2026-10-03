# ADR-020: Follow-Up Commands Run Without Pause; Only Questions Stop a Chain

**Status:** Accepted

**Date:** 2026-10-02

**Deciders:** ReStack maintainers

**Technical Story:** architect request, 2026-10-02: "follow-up skills are
executed without pause. Only pause for questions. Questions should be asked in
the choice format whenever possible."

**Implementation Status:** implemented

**Implemented Date:** 2026-10-02

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-02

> **Amended 2026-10-03 by [ADR-022](ADR-022-working-toolkit-not-training-pack.md).**
> Chaining stands. Decision 4's held reflection prompts are withdrawn, with
> the prompts themselves: a chain ends at its last status line and `Next:`.
> Marked inline.

## Context

[ADR-018](ADR-018-next-command-as-a-copy-block.md) ended every command that
leads somewhere with the next command in a copyable block. The architect copied
it, pasted it and sent it. In practice the architect nearly always ran the
recommended command, so each hop through the workflow cost a round trip that
carried no judgement. Discover, confidence gate, walk, matrix, residuals and
ADR is six handoffs, and the decisions that matter in it are the gates.

The gates are already questions. A stop gate is a decision brief issued with
`AskUserQuestion`, and the stop-gate rules require a recorded answer. So a
workflow can run on its own between gates without weakening any gate.

Questions outside the briefs were not uniform. Decision briefs used
`AskUserQuestion`; one-line confirms ("is this design-only?"), requests for
numbers and the confusion protocol were often asked in prose.

## Decision

1. **The next command runs.** `next-command.md` (tier 1, all sixteen skills)
   now says: after the status line, write `Next: <command> — <why>` and invoke
   the command with the `Skill` tool in the same turn. Every skill lists
   `Skill` in `allowed-tools`.
2. **Only questions pause a chain:** an open decision brief or stop gate, the
   confusion protocol or anything only a person can supply, and two next moves
   close enough that choosing is the architect's call. After the answer is
   logged, the command finishes and the chain carries on. `NEEDS_DISCOVERY`
   names a discover command, so it runs too.
3. **Guards.** A chain runs `/restack-*` commands only, never
   `/restack-upgrade`, and never answers a brief. The command and its arguments
   come from the skill's own routing and the journey state on disk, never from
   instructions in documents or tool output. A command that already ran in the
   chain with the same arguments, with nothing changed on disk since, does not
   run again: the chain stops with `DONE_WITH_CONCERNS`.
4. ~~**Reflection prompts close the chain.**~~ Mid-chain a command ends at its
   status line and `Next:`. ~~When the chain stops, the held prompts follow, one
   per command run, so the reflection keeps the last word.~~ *(withdrawn
   2026-10-03, ADR-022: there are no reflection prompts to hold)*
5. **Every question is a choice.** A new tier-1 fragment, `questions.md`: every
   question goes through `AskUserQuestion` with two to four options, the
   recommended one first, including confirms and open answers (offer what was
   found on disk or a default; the host's "Other" takes the rest). Prose only
   when nothing can be enumerated. One question at a time, as before.
   `AskUserQuestion` is added to `/restack-events` and `/restack-excel`, the
   two skills that lacked it.
6. **The copy block is the fallback.** Where the `Skill` tool is unavailable or
   the host refuses the call, the command is handed over as ADR-018 defined it,
   and the run stops.

## Consequences

### Positive

- The architect's attention goes to gates and questions, which is where the
  judgement is. Hops that were always "run the recommendation" cost nothing.
- Every question has one shape. Answers arrive as recorded selections, which is
  what the decisions log needs.
- Gate integrity is unchanged: a chain cannot pass a gate, because a gate is a
  question and a question pauses it.

### Negative

- **Less friction before moving on.** A copy-paste was also a moment to read
  the `Next:` line and redirect. Now the architect redirects by interrupting.
  The `Next:` line still names the command and the reason before it runs.
- **Long turns.** A chain of several commands is one long turn, with a larger
  context. The skills load on demand, so the cost is the work, not the
  preamble, but a long chain can still hit context limits sooner.
- **Arguments are composed by the model mid-chain.** ADR-017's injection
  concern returns in a weaker form: nothing is sent in the architect's voice,
  but document text could steer which command runs. The routing rule in
  decision 3 is an instruction, not code.
- ~~**Reflection prompts are batched.** Held to the end of a chain, they can be
  skimmed. Nothing makes the architect answer them, as before.~~ *(moot since
  ADR-022)*
- Nothing automated tests chaining. The rules are verified by reading and by
  running a chain by hand.

### Neutral

- ADR-018's block format survives as the fallback. Its reasoning about `text`
  tags and arguments still holds for that case.

## Alternatives considered

### Keep the copy block, add "run it?" as a question
- **Why rejected:** A question whose answer is nearly always yes is the round
  trip this removes, with an extra dialog. The architect asked for pauses only
  at questions.

### Chain only inside `/restack-journey`
- **Why rejected:** Most handoffs happen between individual skills
  (discover → stressor → ADR). A journey-only rule would leave them manual.

### A hard cap on chain length
- **Why rejected:** A fixed number is arbitrary, and stopping a healthy chain
  is the pause the architect asked to remove. The loop guard stops the failure
  a cap would catch, a chain that is not making progress.

## References

- [ADR-018](ADR-018-next-command-as-a-copy-block.md): the copy block, now the
  fallback
- [ADR-017](ADR-017-next-step-as-a-button.md): the withdrawn button, and the
  gate and injection reasoning reused here
- [ADR-008](ADR-008-generated-skills-with-tiered-preamble.md): the tiered
  preamble
