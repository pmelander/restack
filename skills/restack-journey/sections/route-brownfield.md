### Brownfield / oilfield route

An existing system is there. You cannot walk paths you have not found, and the
paths that exist are rarely the paths that were designed. Discovery is not
preamble to the real work — in this terrain it *is* a substantial part of the
work, and the confidence gate at step 7 exists to stop you skipping it.

```
1.  /restack-journey start             establish aspiration, classify terrain
2.  /restack-discover paths            map what is actually there
3.  /restack-discover actor            investigate critical or opaque actors
4.  /restack-discover intentions       trace key intentions end to end
5.  /restack-discover gaps             prioritise the unknowns
6.  /restack-discover organisation     map resistance as stressors
7.  /restack-discover confidence       explicit go / no-go
      |
      +-- CONFIDENCE GATE: not ready --> back to 2
      |
8.  /restack-stressor walk             walk the discovered paths
9.  /restack-stressor generate         include the organisational stressors from 6
10. /restack-stressor analyze          build the matrix on real paths
11. /restack-stressor residues         identify residuals
      |
      +-- ITERATE GATE: /restack-journey iterate --> loop to 8, or proceed
      |
12. /restack-adr create                document each residual as a decision
13. /restack-tech-stack evaluate       evaluate any new technology the residuals require
14. /restack-solution-doc hld          document the target state
15. /restack-design-review complete    validate the design
16. /restack-solution-doc deployment   operational readiness
```

**Expected iterations: 3-5.** More than greenfield, because each iteration
tends to surface actors discovery missed. That is the loop working, not the
loop failing.

**Oilfield vs brownfield.** Same route, different attitude. An oilfield is a
brownfield that is still actively producing value and cannot be stopped — every
residual must be introducible without an outage, which constrains which
residuals are admissible. Note it in the journey state; it changes step 11's
option set, not the sequence.

**Two failure modes specific to this terrain:**

*Design-first, discovery-skipped.* An HLD exists, written from documentation and
conversation, and the design review found "critical issues". Those issues are
usually symptoms — the design rests on beliefs about the system that were never
verified. The corrective action is to go back to step 2, not to patch the
findings.

*Discovery that never converges.* Every `/restack-discover paths` run finds more actors
and the boundary keeps moving. This means the system boundary was never agreed.
Stop discovering and settle the boundary as an explicit decision brief: what is
in scope for this aspiration, and what is a neighbouring system we treat as a
single opaque actor with a known contract.

**Organisational stressors are first-class here.** An EA board that takes six
weeks to approve a vendor is a stressor on every path whose residual requires
that vendor. Put it in the matrix as a column-hitting stressor. Teams routinely
discover their highest-impact stressor is a process, not a technology.
