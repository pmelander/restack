# Getting Started with ReStack

Install in two minutes, then walk through a first engagement end to end.

---

## Install

**Linux / macOS**
```bash
git clone git@github.com:pmelander/restack.git restack
cd restack
cp -R skills/* ~/.claude/skills/
pip install -r requirements.txt
```

**Windows**
```powershell
git clone git@github.com:pmelander/restack.git restack
cd restack
Copy-Item -Recurse -Path "skills\*" -Destination "$env:USERPROFILE\.claude\skills\"
pip install -r requirements.txt
```

Python and `openpyxl` are needed only by `/restack-excel`. Everything else works
without them.

**Verify:** open Claude Code and type `/restack`. You should see fourteen
skills. If you see none, check they landed in `~/.claude/skills/restack-*/`,
each containing a `SKILL.md`.

Prefer symlinks while developing, or upgrading from an unprefixed install? See
[Installation](docs/INSTALLATION.md).

**Before your first engagement**, read
[Introduction to Residuality Theory](RESIDUALITY.md). It is short, and every
skill uses its vocabulary precisely — *aspiration*, *actor*, *intention*,
*path*, *stressor*, *residual*. Without it the skills will feel like they are
using ordinary words strangely, because they are.

---

## Your first engagement

### 1. Start the journey

```
/restack-journey start
```

Describe the system, what you want it to achieve, and what already exists. You
will be asked five things, **one at a time**: the aspiration, what exists
today, the blast radius of being wrong, who can block this, and whether the
team has done this before.

They are not a form. The answers classify the terrain, and terrain decides
everything downstream — how much discovery is mandatory, how many iterations to
expect, whether you can start designing at all.

**Expect to be stopped here.** The terrain classification comes back as a
decision brief and waits for you to confirm it. Over-classifying costs weeks of
discovery nobody needed; under-classifying puts a design on top of a system
nobody understands.

### 2. Follow the route for your terrain

| Terrain | What it means | Route |
|---|---|---|
| **Greenfield** | blank canvas, you design the paths | design → walk → stress → build what survives |
| **Brownfield** | existing system, partial knowledge | discover → confidence gate → walk → stress |
| **Oilfield** | brownfield that cannot be stopped | same route; residuals must land without an outage |
| **Minefield** | fragile, political, severe blast radius | discover extensively; gaps block rather than becoming assumptions |

Mixed terrain is normal and means **classify per path**. A greenfield service
that writes to a legacy ledger is greenfield on its own paths and minefield on
the ledger path.

### 3. Discover, if you are not on a blank canvas

```
/restack-discover paths          # what is actually there
/restack-discover actor <name>   # what an opaque or critical actor really does
/restack-discover organisation   # who can block this, translated into stressors
/restack-discover confidence     # the gate: ready to stress this?
```

Two things surprise people here.

**Documentation rates *low* as evidence.** A claim about how an existing actor
behaves needs code, logs, a probe, or a person who operates it. Anything else
gets registered as an assumption with what would settle it. This feels
pedantic until a design review three months later finds "critical issues" that
were unexamined beliefs from week one.

**Organisational resistance is a stressor, not a constraint.** An architecture
board that takes six weeks to approve a vendor constrains the design as hard as
a database that cannot take the write load — so it goes in the matrix and gets
a residual, like anything else. Teams routinely find their highest-impact
stressor is a process.

### 4. Walk, stress, and find the residuals

```
/restack-stressor walk checkout       # traverse the path, actor by actor
/restack-stressor generate            # 20-30 stressors across seven categories
/restack-stressor analyze             # build the impact matrix
/restack-stressor vulnerabilities     # where is it concentrated? what clusters?
/restack-stressor residues            # what change removes the most?
```

Walk the error path as well as the happy path — they are different paths, and
only one of them was designed on purpose.

**Include the absurd stressors.** At least one per generation, deliberately.
Plausible stressors come from what you already fear, and what you already fear
you have partly designed for. "Fire-breathing lizards melt the inventory
datacentre" is *sudden total loss of a facility with no warning* — a scenario
teams will reason about seriously in a costume and dismiss as unrealistic in a
suit.

Then look for **clusters**: several stressors hitting the same actors are one
weakness wearing different clothes. Design the residual against the shared
mechanism, not against each stressor. That is what produces the compounding —
one queue clearing four unrelated rows.

### 5. Decide whether to loop

```
/restack-journey iterate
```

The most consequential command in the toolkit. It reports impact, the delta
since last iteration, and — importantly — whether the residuals you are
counting are **implemented** or merely **proposed**. Impact reduction from
unimplemented residuals is a forecast, not a result.

Then it stops and asks. "Sufficiently low" is your judgement, and the toolkit's
job is to make you make it with the matrix in front of you rather than by
drifting onward.

Expect **2–3 iterations** in greenfield, **3–5** in brownfield, **5+** in a
minefield. If impact is flat despite implemented residuals, the path map is
usually incomplete — go back to discovery rather than adding more residuals.

### 6. Record, document, review

```
/restack-adr create Add payment-intent queue    # what it defends against, and can we undo it
/restack-solution-doc hld                       # the design, with residuals explained
/restack-design-review complete                 # validate before building
```

Write an ADR for **every implemented residual**. Without one, the queue you
added looks like unnecessary complexity to whoever inherits the system — and
the first thing anyone does with unexplained complexity is remove it.

---

## What to expect from these skills

**They stop.** Three gates halt the workflow and wait for you: the confidence
gate, the iterate gate, and any approach gate where two designs are both
viable. This is deliberate. If you find yourself wanting to skip one, that is
worth noticing — and worth telling us about.

**They ask one question at a time.** Never a batch. The questions are where the
thinking happens.

**They say when they do not know.** `NEEDS_DISCOVERY` is a normal outcome, not
a failure. Producing a confident-looking matrix over a path map nobody believes
is the failure.

**They are opinionated.** Binary scoring, no severity scale. No risk register.
Compliance as stressors rather than controls. Each of those is argued in an
[ADR](docs/adr/) — disagree with the reasoning, not just the behaviour.

---

## Once it is live

An engagement does not end; it changes shape.

```
/restack-journey cadence
```

Sets the rhythm and, crucially, an **owner** per activity. Triggered work — a
significant change ships, an incident happens, a new integration appears —
matters more than the calendar. An incident is the highest-value input this
loop ever gets: a real stressor with a real path and a known outcome. Feed it
back and check whether the matrix predicted it.

Roughly: `/restack-evolve health` monthly, `/restack-stressor generate` and
`/restack-arch-learning analyze` quarterly, `/restack-capability-assessor`
every six months, `/restack-adr` continuously.

---

## Where files are written

```
docs/journey/            state, iteration history, decisions log, assumptions
docs/discovery/          path maps, actor profiles
docs/stressor-analysis/  stressor sets, matrices, residuals
docs/adr/                decisions
docs/architecture/       HLD, LLDs, evolvability assessments
docs/deployment/         deployment guide
docs/operations/         runbook
docs/reviews/            design review reports
docs/patterns/           pattern catalog, indexed by problem
docs/learning/           outcome analyses, retrospectives
```

`docs/journey/` is the one that matters most. It is why an engagement survives
a three-week gap, a handoff, or an audit.

---

## Checklist

- [ ] Installed; `/restack` shows fourteen skills
- [ ] Read [Residuality Theory](RESIDUALITY.md) — the vocabulary is load-bearing
- [ ] `/restack-journey start` and confirmed the terrain
- [ ] Walked one path, including its error path
- [ ] Generated stressors with at least one genuinely absurd one
- [ ] Built a matrix and found a cluster
- [ ] Added one residual and re-walked to see the compounding
- [ ] Written an ADR for it

---

## Help

| | |
|---|---|
| [RESIDUALITY.md](RESIDUALITY.md) | the theory and the vocabulary |
| [QUICKREF.md](QUICKREF.md) | every command, and the gates |
| [docs/USAGE.md](docs/USAGE.md) | worked examples per skill |
| [docs/INSTALLATION.md](docs/INSTALLATION.md) | symlinks, upgrades, troubleshooting |
| [ROADMAP.md](ROADMAP.md) | what is next |
| [CONTRIBUTING.md](CONTRIBUTING.md) | compliance packs and new skills |
