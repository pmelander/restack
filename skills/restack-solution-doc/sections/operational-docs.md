### Deployment guide

Written for someone deploying this system who was not involved in building it —
including you, in eight months, at an unsociable hour.

```markdown
# Deployment Guide — <system>

## 1. Prerequisites          [access, accounts, tooling, with who grants each]
## 2. Environments           [what differs between them, and why]
## 3. Configuration          [every setting, its default, its safe range, where secrets come from]
## 4. Deploy procedure       [numbered, executable, no implied knowledge]
## 5. Verification           [how you know it worked - specific checks, not "confirm it's up"]
## 6. Rollback               [the procedure, and what is NOT reversible]
## 7. First-deploy notes     [migrations, seed data, one-time steps]
```

Three parts carry most of the value:

**Verification must be specific.** "Check the service is healthy" is not a
check. "GET /health returns 200 and `db: connected`; submit a test order and
confirm it reaches the settlement queue within 30s" is. A vague verification
step means every deploy is verified differently and nobody knows what "worked"
means.

**Rollback must name what cannot be rolled back.** Applied schema migrations,
messages already consumed, notifications already sent, partner calls already
made. The honest list is what an operator needs at the moment they are deciding
whether to roll back or fix forward, and discovering the list mid-incident is
the worst time.

**Prerequisites must name who grants access.** Half of all out-of-hours deploy
delays are waiting for a permission nobody knew was needed.

If the system has a **phased-rollout or shadow-mode residual**, document the
phases here as distinct procedures — that residual only works if the operator
knows how to run it, and it is usually the one residual that exists specifically
for a nervous stakeholder.

---

### Replacing an operational document

When a new deployment guide or runbook replaces an old one, **archive the old
one in the same step**: move it to `archive/<name>-v<n>-<YYYY-MM-DD>.md` next
to the current one, with a banner at the top naming its replacement and the
decision that superseded it. Never leave a stale guide beside a new one. An
operator searching under time pressure opens whichever one they find first.

---

### Operations runbook

Written for whoever is holding the pager. Optimise ruthlessly for someone under
stress at 3am who did not build this.

```markdown
# Runbook — <system>

## 1. What this system does      [three sentences, the paths that matter]
## 2. Health and where to look   [dashboards, logs, key metrics with normal ranges]
## 3. Common alerts              [one entry per alert: meaning, checks, actions, escalation]
## 4. Common tasks               [restart, drain, replay, scale, flush]
## 5. Failure modes              [from the LLDs and the stressor matrix]
## 6. Operational levers         [what to change to reduce blast radius, and its effect]
## 7. Escalation                 [who, when, and what to have ready]
```

#### Writing it for 3am

- **Actions before explanation.** What to do first, then why. Someone paged
  needs the command, not the design rationale.
- **Every metric gets a normal range.** A dashboard without normal values
  cannot be read by someone seeing it for the first time.
- **One entry per alert, and every alert has one.** An alert with no runbook
  entry is an alert that will be acknowledged and ignored, which is worse than
  no alert.
- **Every alert the runbook names is defined in an ADR or LLD.** If it is not,
  register it as a design gap in the assumptions register, and say so in the
  entry. An alert that exists only in the runbook has no owner and no
  guarantee it was ever built. One field runbook named seven such alerts.
- **Every lever is written end to end:** who may pull it, what it does to the
  system, and **the signal that confirms it took effect**. Then add what to do
  when the signal does not come. If a diagnosis step depends on a lever ("flip
  it; if the host recovers, the feature was the cause"), check that the ADR,
  the LLD and the runbook describe the lever the same way. If they differ, one
  reading turns that step into a false negative.
- **Say what NOT to do.** "Do not restart the settlement worker mid-batch — it
  is not idempotent before the commit point." This is the highest-value content
  in any runbook and it is almost never written down.

#### Populate failure modes from the analysis

Section 5 should not be invented. The stressor matrix already lists what can go
wrong and the residuals already say what should absorb it. For each significant
stressor: what an operator would observe, which residual is supposed to handle
it, and what to do if the residual is not working.

That last part matters. A residual failing is not covered by the residual, and
it is exactly the situation the matrix does not describe.

#### The test

Give the runbook to someone who has never operated this system and ask them to
work through a failure scenario. Every question they ask is a gap. This is the
only reliable way to find the implied knowledge the author could not see, and
it takes twenty minutes.
