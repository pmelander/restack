### Cloud migration — the six R's

| Strategy | Effort | Cloud benefit | When |
|---|---|---|---|
| **Rehost** (lift and shift) | Low | Low | legacy apps, tight deadline, datacentre exit |
| **Replatform** (lift, tinker, shift) | Medium | Medium | some benefit for manageable effort |
| **Repurchase** (move to SaaS) | Low–Medium | High | commodity function — CRM, HR, email |
| **Refactor** (re-architect) | High | High | strategic apps that need cloud-native capability |
| **Retire** | None | n/a | redundant or unused — check usage before assuming |
| **Retain** | None | None | compliance, latency, or integration constraint |

Choose per workload, not per programme. A portfolio migrating under one
strategy is a programme that has not looked at its workloads.

**Retire is the most under-used and highest-return option.** Before costing any
migration, ask what actually calls this system. Teams routinely migrate
workloads nobody uses because nobody checked, and the check is cheap.

**Retain is a legitimate answer**, and stating it explicitly is better than
leaving a system in scope that will never move.

#### What the six R's do not tell you

They classify effort, not risk. The residuality question runs alongside:
**which residuals does this workload currently rely on, and do they survive the
move?**

An on-premise system usually carries undocumented residuals — a reconciliation
batch, an operator who intervenes, a reliable small network, a shared filesystem
that made an ordering assumption safe. Rehosting preserves the code and drops
those, and the vulnerability they covered returns in a less familiar
environment.

Run `/restack-discover` on anything being migrated with more than trivial
effort, and walk the migration paths with `/restack-stressor walk`. A migration
is a period of elevated fragility and is exactly what the analysis is for.

Design the move as paths, not phases — strangler, shadow, reversible cutover —
per `/restack-tech-stack`'s migration analysis, and define the abort condition
before starting.

---

### Disaster recovery tiers

| Strategy | RTO | RPO | Cost | Complexity |
|---|---|---|---|---|
| Backup and restore | Hours | Hours | $ | Low |
| Pilot light | 10–30 min | Minutes | $$ | Medium |
| Warm standby | Minutes | Seconds | $$$ | High |
| Active/active | Near-zero | Near-zero | $$$$ | Very high |

#### Choose the tier from stressors, not from the menu

The tier is a consequence of two numbers and one question, in this order:

1. **What is the actual RTO and RPO requirement?** Not the aspirational one.
   Ask what it costs the business per hour of outage and per hour of lost data,
   and get a number or a range. "As low as possible" is not a requirement and
   will buy an active/active architecture nobody can operate.
2. **Which disaster?** DR tiers describe recovery speed, not scope. Region loss,
   data corruption, ransomware, accidental deletion and a bad deploy are
   different stressors with different recovery paths — and **replication
   defends against none of the last four**. Corruption replicates. This is the
   most common serious gap in cloud DR designs: a warm standby that faithfully
   reproduces the corrupted data in seconds.
3. **What is the organisational reality?** Who declares a disaster, and are
   they reachable at 03:00 on a Sunday? A ten-minute RTO with a two-hour
   decision latency is a two-hour RTO. That decision path is an actor; put it
   on the path map.

#### Requirements for any tier

- **Backups that have been restored.** An untested backup is a belief. Record
  when a restore was last performed and how long it took — the second number is
  the one nobody has.
- **Backups outside the blast radius.** A different account or subscription,
  with separate credentials, and immutable where the threat model includes
  ransomware. A backup an attacker can delete with the credential they already
  have is not a backup.
- **A documented, exercised runbook.** Who declares, who executes, in what
  order, and how you verify recovery succeeded.
- **A stated data-loss window** that the business has actually agreed to,
  rather than one implied by the technology chosen.
- **A failback plan.** Teams design the failover and discover at the worst
  moment that returning is undefined.

Rate each of these Validated or Assumed, and say which. A DR design where every
line is Assumed is a plan, not a capability.
