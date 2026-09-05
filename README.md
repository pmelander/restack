# ReStack

**Architecture skills for Claude Code, built on Residuality Theory.**

Fifteen skills — fourteen that walk you through designing systems which
survive things nobody predicted, and one that keeps them up to date. They build
the thinking so that eventually you do it without them.

> Formerly *Residual Architecture Skill Set*. Renamed to ReStack in September 2026; the history is unchanged.

---

## The problem this addresses

Risk registers enumerate the threats you already imagined. Compliance
checklists codify harms that happened to somebody else. Both produce confidence
proportional to how much you wrote down, rather than to how exposed you
actually are.

The failures that hurt are the ones nobody listed.

ReStack takes the opposite approach, from
[Barry O'Reilly's Residuality Theory](RESIDUALITY.md): stress a design against
scenarios so varied that some of them are absurd, find which components keep
getting hit, and change the architecture so whole *classes* of surprise stop
mattering. You are not defending against a list. You are making the system
structurally harder to hurt.

---

## What that looks like

You walk a path through the system, actor by actor, and watch what an intention
does as it propagates:

```
/restack-stressor walk checkout

  Browser → API Gateway → Auth → Order Service → Inventory DB
          → Payment Gateway → Notification Queue → Email Service

  Under "payment provider goes offline":
    Order Service blocks at the Payment Gateway hop — no timeout configured
    Intention dies at hop 5; the customer sees a spinner, then a 502
```

Then you generate stressors — deliberately including ones that sound
unserious — and score which actors each one reaches:

```
                           | API GW | Auth | Order | Inventory | Payment | Notify |
---------------------------|--------|------|-------|-----------|---------|--------|
Payment provider down      |   0    |  0   |   1   |     0     |    1    |   1    | = 3
Region-wide AZ failure     |   1    |  1   |   1   |     1     |    1    |   1    | = 6
Auth token clock skew      |   1    |  1   |   1   |     0     |    0    |   0    | = 3
Black Friday 40x spike     |   1    |  0   |   1   |     1     |    1    |   1    | = 5
Regulator audit mid-outage |   0    |  0   |   1   |     0     |    1    |   0    | = 2
Fire-breathing lizards     |   0    |  0   |   0   |     1     |    0    |   0    | = 1
---------------------------|--------|------|-------|-----------|---------|--------|
Vulnerability              |   3    |  2   |   5   |     3     |    4    |   3    | Total: 20
```

Order Service is carrying the most exposure. Four of the stressors hitting it
share one mechanism — nothing on that path degrades when a downstream
dependency slows. So you add **one** residual, a payment-intent queue with an
async settlement path, and re-walk:

```
Actor          | Iter 1 | Iter 2 | Delta | Residual applied
---------------|--------|--------|-------|------------------------------
Order Service  |   5    |   2    |  -3   | async payment queue + timeout
Payment GW     |   4    |   2    |  -2   | async payment queue
Total          |  20    |  13    |  -7   | 1 residual, 2 actors changed
```

One change, seven points, against stressors that had nothing to do with each
other. That compounding is the whole argument — and it is why the lizards stay
in. An absurd stressor is a mechanism in a costume, and teams will reason
seriously about "sudden total loss of a facility with no warning" when it
arrives as a lizard, then wave the identical scenario away as unrealistic when
it arrives as a datacentre fire.

---

## What makes these skills behave differently

**They stop and make you decide.** Every point where judgement is genuinely
yours becomes a structured brief — not a recommendation buried in prose. It
carries the aspiration the decision serves, plain-English stakes, a
recommendation, and two ratings that matter more than a confidence score:

```
D3 — Iterate the stressor loop, or proceed to design?
Aspiration: originate a mortgage in under a day with no rekeying
Confidence: Medium — impact numbers assume the queue residual is implemented,
            and it is currently proposed only
Reversibility: Reversible — proceeding does not close off another iteration
```

`Confidence: Low` on a **one-way door** routes you back to discovery instead of
forward to a choice.

**They refuse to proceed on beliefs.** A claim about how an existing system
behaves needs a source. Code, logs, a live probe, or a person who operates it —
documentation rates *low* and inference from a component's name is not evidence
at all. Anything unverified gets registered as an assumption with what would
settle it.

**They gate.** Three points where the workflow halts rather than drifting past:
*have we discovered enough to stress this?* (the threshold rises in dangerous
terrain), *is impact low enough to stop iterating?*, and *which approach, and is
it reversible?*

**They remember.** Journey state lives on disk in `docs/journey/`, so an
engagement survives weeks, breaks, and handoffs — with an audit trail of what
was decided and why.

**They compound.** Residuals that recur across engagements become patterns.
Decisions carry predictions, which makes them falsifiable, which is what lets
the next analysis be better than the last.

---

## Start here

```
/restack-journey start
```

Describe the system, what you are trying to achieve, and what already exists.
It classifies the terrain and maps the route from there — because the route
genuinely differs:

| Terrain | You are | First move |
|---|---|---|
| **Greenfield** | designing paths that do not exist yet | design, then stress before building |
| **Brownfield** | changing a system you partly understand | discover before you touch anything |
| **Minefield** | changing a fragile system with real blast radius | discover extensively; gaps block, they do not become assumptions |

At the centre of every route is a loop, not a line:

```
walk paths → generate stressors → build matrix → find residuals
     ↑                                                  ↓
  re-walk ←← implement residuals ←← impact low enough? ←←
```

You iterate until vulnerability is low enough — not zero, but low enough given
the aspiration and what further reduction would cost. That judgement stays
yours; the toolkit's job is to make you make it deliberately, with the matrix
in front of you, rather than by drifting onward.

→ **[Getting Started](GETTING_STARTED.md)** · **[All commands](QUICKREF.md)** · **[The theory](RESIDUALITY.md)**

---

## The skills

Fourteen for the work, organised by where you are rather than by what they
are called — plus `/restack-upgrade`.

**Orchestration**

| | |
|---|---|
| [`/restack-journey`](skills/restack-journey/SKILL.md) | classify terrain, map the route, run the iterate gate, keep state |

**Understand what is there** — brownfield and minefield

| | |
|---|---|
| [`/restack-discover`](skills/restack-discover/SKILL.md) | map paths and actors, trace intentions, rate confidence honestly, own the confidence gate |

**Find what will break**

| | |
|---|---|
| [`/restack-stressor`](skills/restack-stressor/SKILL.md) | walk paths, generate stressors, build the matrix, identify residuals by mechanism |

**Decide and record**

| | |
|---|---|
| [`/restack-adr`](skills/restack-adr/SKILL.md) | decisions with reversibility and the residual they implement |
| [`/restack-tech-stack`](skills/restack-tech-stack/SKILL.md) | technology against seven dimensions, including which residuals it must express |
| [`/restack-solution-doc`](skills/restack-solution-doc/SKILL.md) | HLD, LLD, deployment, runbook — in actors, intentions and paths |
| [`/restack-design-review`](skills/restack-design-review/SKILL.md) | review that also asks why the matrix did not catch each finding |

**Build it**

| | |
|---|---|
| [`/restack-cloud`](skills/restack-cloud/SKILL.md) | cloud design, IaC, Well-Architected, migration, DR — primitives treated as residuals |
| [`/restack-capacity`](skills/restack-capacity/SKILL.md) | sizing with the arithmetic shown, bottlenecks as stressors, load tests that validate residuals |

**Get better at it** — the compounding layer

| | |
|---|---|
| [`/restack-arch-learning`](skills/restack-arch-learning/SKILL.md) | compare what you predicted against what happened; correct the method |
| [`/restack-patterns`](skills/restack-patterns/SKILL.md) | recurring residuals become patterns; recurring failures become anti-patterns |
| [`/restack-evolve`](skills/restack-evolve/SKILL.md) | brittleness, incremental change, fitness functions that stop residuals eroding |
| [`/restack-capability-assessor`](skills/restack-capability-assessor/SKILL.md) | team capability rated on practice under deadline, not on knowledge |

**Utility and maintenance**

| | |
|---|---|
| [`/restack-excel`](skills/restack-excel/SKILL.md) | spreadsheets into the markdown workflow |
| [`/restack-upgrade`](skills/restack-upgrade/SKILL.md) | pull, reinstall, show what changed — also repairs a broken install |

### Two things deliberately absent

There is no risk assessor and no compliance checker, and that is a position
rather than a gap.

Risk registers train architects to think in enumerated threats, which is the
habit this toolkit exists to break — stressor analysis covers risk and reaches
further ([ADR-006](docs/adr/ADR-006-exclude-risk-assessor-skill.md)).
Compliance enters as **stressor packs**
(`/restack-stressor compliance gdpr`), so a regulation's requirements arrive as
scenarios to walk, and the residuals that emerge address the underlying harm
structurally rather than satisfying a control on paper
([ADR-007](docs/adr/ADR-007-compliance-via-stressor-packs.md)).

---

## Install

```bash
git clone https://github.com/pmelander/restack.git ~/restack
cd ~/restack && ./setup          # Windows: .\setup.ps1
```

Open Claude Code and type `/restack`. Later, `/restack-upgrade` pulls and
reinstalls in one step.

`setup` reports what it installed, updated and removed, and — unlike a plain
copy — removes ReStack skills that no longer exist upstream. `--dry-run` shows
what it would do; `--symlink` makes repository edits live. Python and
`openpyxl` are optional and affect only `/restack-excel`.

**Installing with an agent?** Point Claude Code at
[INSTALL.md](INSTALL.md) — "install ReStack from
https://github.com/pmelander/restack" — and it has step-by-step instructions to
follow, including confirming with you before it writes anything.

Every skill is prefixed so ReStack coexists with other skill suites — an
unprefixed `design-review` or `patterns` silently overwrites whatever was
installed there first. See
[Installation](docs/INSTALLATION.md#why-every-skill-is-prefixed) for the
symlink method, upgrading from an unprefixed install, and troubleshooting.

---

## Status

All fourteen architecture skills are at **v2.0.0**, generated from templates
with a shared behavioural preamble. CI checks on every push that no generated file has
drifted from its source and that the skills tree is valid.

**These skills are the deliverable; they have not yet been run end to end on a
live engagement in this form.** If you use them in anger, the most useful thing
you could report back is which gate you wanted to skip, and why.

See the [Roadmap](ROADMAP.md) for what is next, and the
[ADRs](docs/adr/) for the decisions behind the design — including the ones
about what deliberately does *not* exist.

---

## Contributing

`SKILL.md` files are **generated**. Edit `skills/<name>/SKILL.md.tmpl` and run
`python scripts/gen_skills.py`; CI rejects drift.

Most wanted:

- **Compliance packs** — HIPAA, PCI DSS, ISO 27001, SOC 2. GDPR exists as a
  worked example. Each stressor must be a concrete scenario you could walk, not
  a restated control.
- **Real-world reports** — where a gate helped, and where it got in the way.
- **Skills that fit the theory.** A skill that trains architects to work from
  checklists or registers will be turned down, however useful it looks.

See [Contributing](CONTRIBUTING.md).

---

## Documentation

| | |
|---|---|
| [RESIDUALITY.md](RESIDUALITY.md) | the theory, and the vocabulary every skill uses |
| [GETTING_STARTED.md](GETTING_STARTED.md) | first engagement, start to finish |
| [QUICKREF.md](QUICKREF.md) | every command, and the gates |
| [docs/USAGE.md](docs/USAGE.md) | worked examples per skill |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | install, upgrade, troubleshoot |
| [INSTALL.md](INSTALL.md) | install methods, and instructions an agent can follow |
| [CHANGELOG.md](CHANGELOG.md) | what changed, by version |
| [CLAUDE.md](CLAUDE.md) | architecture of the toolkit itself |
| [docs/adr/](docs/adr/) | decisions made while building it |

---

## Acknowledgements

The skill-authoring mechanics — generated skills, the tiered preamble,
on-demand sections, and structured decision briefs — were adapted from
[Garry Tan's gstack](https://github.com/garrytan/gstack). The residuality
method, and everything the skills actually do, is our own.
[ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md) records
what was taken, what was changed, and what was deliberately left behind.

Residuality Theory is the work of **Barry O'Reilly**. See
[RESIDUALITY.md](RESIDUALITY.md).

---

MIT licensed. Built for Solution Architects using Claude Code.
