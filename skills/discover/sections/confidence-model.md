### Confidence model

Rate every path and every actor. An unrated path map invites everyone to
assume it is all equally solid, which it never is.

#### Path confidence

| Level | Meaning | Basis |
|---|---|---|
| **Validated** | Confirmed by direct observation | watched it happen in production or staging; traces, logs |
| **Inferred** | Strongly supported, not directly observed | consistent log patterns, code analysis, two corroborating accounts |
| **Documented** | Documentation says so, nothing verified it | docs exist and look current |
| **Assumed** | Expectation or a single source | "that's how we think it works" |
| **Unknown** | No basis | a gap, not a path |

#### Actor intent confidence

| Level | Meaning |
|---|---|
| **Confirmed** | Behaviour observed directly, edge cases probed |
| **Documented** | Documented, and the documentation appears current |
| **Tribal** | One or two people know; nothing written down |
| **Guessed** | Inferred from the name, the context, or an adjacent system |

**Documented is not a passing grade on its own.** The evidence rules put
documentation at Low confidence for a reason: it describes the system as
designed or as last written up, not as it runs. A path that is Documented
end-to-end and Validated nowhere is a hypothesis with a diagram.

### Prioritising gaps

For each gap, score three things and rank on the combination:

1. **Impact if wrong** — does the design change if this assumption fails?
   A gap that cannot change any decision is not worth closing.
2. **Likelihood of being wrong** — how reliable is the source? Tribal knowledge
   about a system that has been refactored since is likely wrong.
3. **Cost to close** — reading a config is minutes; getting time with the one
   person who knows may be weeks.

Work **high impact + likely wrong + cheap to close** first. That ordering is
the whole discipline: it is what stops discovery becoming an open-ended
archaeology project.

Give every gap a named owner and a specific closing action — "read the retry
policy in `orders/config/resilience.yaml`", not "investigate Order Service".

### The confidence gate

This is a stop gate. It settles one question: **do we know this system well
enough to stress it?**

Thresholds depend on terrain, and the difference is the point:

| | Brownfield / oilfield | Minefield |
|---|---|---|
| Actors on critical paths | at least **Documented** | at least **Confirmed** |
| Intentions on critical paths | at least **Inferred** | at least **Validated** |
| Open gaps on critical paths | accepted as registered assumptions | **block** — must be closed |
| Organisational stressors | listed | listed, with veto points named |
| Team agreement | the confidence view is shared, not one person's | same, plus the owning team concurs |

In brownfield, an unknown becomes a registered assumption and the journey
continues. In a minefield an unknown on a critical path stops the journey. The
assumptions register is for peripheral unknowns only.

#### Running the gate

1. Rate every path and actor. Show the ratings — a summary sentence hides the
   one Assumed actor sitting on the critical path.
2. Identify the lowest-confidence elements **on the paths that matter**.
   Low confidence on a peripheral path is not a blocker; say so explicitly so
   it does not get treated as one.
3. State honestly what you know, what you think you know, and what you do not
   know. The third list is the valuable one and the one that gets quietly
   dropped.
4. Form a recommendation: **ready to walk** / **needs more discovery** /
   **needs investigation before anything**.
5. Issue the decision brief. `Confidence:` on the brief is your own rating of
   the recommendation, and it is usually Medium at best — say what would raise
   it. **STOP.**
6. Log the gate and its rationale to `docs/journey/decisions-log.md`.

**Not ready routes backwards to a specific command**, never to "do more
discovery": unknown actor behaviour → `/discover actor <name>`; unclear
propagation → `/discover intentions`; a moving system boundary →
`/discover paths`; unmapped resistance → `/discover organisation`.

#### The failure this gate exists to prevent

A team proceeds to stressor analysis over a Documented-grade path map, builds a
careful matrix, designs residuals, writes the HLD — and the design review then
finds "critical issues" that are really the original unverified beliefs
surfacing three months late, at design-review prices. The matrix was rigorous;
it was just rigorous about the wrong system.

If the honest answer is that the map is not trusted, the correct output is
`NEEDS_DISCOVERY`, naming the specific unknown — not a confident-looking
summary that lets everyone move on.
