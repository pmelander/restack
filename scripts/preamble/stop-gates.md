## Stop Gates

A **stop gate** is a point in a workflow where you halt and wait for the
architect. It is not a recommendation and not a checkpoint you narrate past.
When you reach one you emit the decision brief, then stop — no further phases,
no artifact generation, no "meanwhile I have also drafted".

The three gates that recur across this toolkit:

| Gate | Where | Question it settles |
|---|---|---|
| **Confidence gate** | end of discovery, before any walk | Do we know the system well enough to stress it? |
| **Iterate gate** | end of each stressor iteration | Is impact low enough to proceed, or do we loop? |
| **Approach gate** | wherever two or more viable designs exist | Which path forward, and is it a one-way door? |

Individual commands declare additional gates inline as `**STOP.**`.

Three rules:

1. **A clear answer is still a gate.** "The recommendation is obvious" is a
   reason to make the recommendation strong, not a reason to skip the brief.
   Writing the conclusion in prose and continuing is the exact failure this
   mechanism exists to prevent.
2. **Passing a gate is recorded.** Log the decision and its rationale to
   `docs/journey/decisions-log.md` before continuing. A gate that leaves no
   trace did not happen.
3. **A gate reached with Low confidence routes backwards**, not forwards. The
   correct output is `NEEDS_DISCOVERY` and a specific `/restack-discover` command.
