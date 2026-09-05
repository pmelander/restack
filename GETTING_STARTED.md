# Getting Started with ReStack

Welcome! This guide will get you up and running in under 5 minutes.

---

## Step 1: Install

**Linux/Mac:**
```bash
git clone git@github.com:pmelander/restack.git restack
cd restack
cp -R skills/* ~/.claude/skills/
pip install -r requirements.txt
```

**Windows:**
```powershell
git clone git@github.com:pmelander/restack.git restack
cd restack
Copy-Item -Recurse -Path "skills\*" -Destination "$env:USERPROFILE\.claude\skills\"
pip install -r requirements.txt
```

> **Note:** Excel reading requires Python and openpyxl. If `/restack-excel` commands fail, run: `pip install -r requirements.txt`

---

## Step 2: Verify

Open Claude Code and type `/` — you should see:

**Orchestration & Discovery:**
`/restack-journey` `/restack-discover`

**Stressor Analysis:**
`/restack-stressor`

**Design & Documentation:**
`/restack-adr` `/restack-solution-doc` `/restack-tech-stack` `/restack-design-review`

**Cloud & Infrastructure:**
`/restack-cloud` `/restack-capacity`

**Organisational Capabilities:**
`/restack-arch-learning` `/restack-capability-assessor` `/restack-patterns` `/restack-evolve`

**Utilities:**
`/restack-excel`

✅ If you see these, installation was successful.

---

## Step 3: Start Your Journey

The first thing to do with any new engagement isn't to open a specific skill — it's to understand where you are and what the terrain demands.

```
/restack-journey start
```

Tell Claude about the system you're working on — what you're trying to achieve, what exists today, and any constraints. It will assess the terrain and map your recommended skill sequence from there.

**New to Residuality Theory?** Read the [Introduction to Residuality Theory](RESIDUALITY.md) first — it explains the philosophy behind the toolkit and the vocabulary all the skills share.

---

## The Three Terrains

The journey looks different depending on what you're walking into:

### Greenfield — blank canvas
You have an aspiration and nothing yet exists. You design the paths, then walk and stress them.

```
/restack-journey start
→ /restack-tech-stack → /restack-adr → /restack-solution-doc hld
→ /restack-stressor walk → /restack-stressor generate → /restack-stressor analyze → /restack-stressor residues
→ [iterate until impact sufficiently low]
→ /restack-adr → /restack-design-review → /restack-solution-doc deployment
```

### Brownfield — existing system
Something is already there. You need to discover it before you can change it.

```
/restack-journey start
→ /restack-discover paths → /restack-discover actor → /restack-discover organisation → /restack-discover confidence
→ /restack-stressor walk → /restack-stressor generate → /restack-stressor analyze → /restack-stressor residues
→ [iterate until impact sufficiently low]
→ /restack-adr → /restack-design-review → /restack-solution-doc
```

### Minefield — high fragility, high complexity
An existing system with fragile dependencies, unclear paths, and organisational resistance. Discover extensively before touching anything.

```
/restack-journey start
→ /restack-discover paths → /restack-discover actor → /restack-discover intentions → /restack-discover gaps
→ /restack-discover organisation → /restack-discover confidence
→ [if not confident — keep discovering]
→ /restack-stressor walk → /restack-stressor generate → /restack-stressor analyze → /restack-stressor residues
→ [iterate more cycles than brownfield]
→ /restack-adr → /restack-design-review → /restack-solution-doc
```

---

## The Stressor Iteration Loop

At the heart of every journey is a loop, not a straight line:

```
walk paths → generate stressors → build matrix → find residuals
     ↑                                                  ↓
  re-walk ←← implement residuals ←← impact low enough? ←←
```

You keep iterating until the system's vulnerability is **sufficiently low** — not zero, but low enough given the aspiration and the cost of further improvement. Use `/restack-journey iterate` to make that judgment explicitly rather than by instinct.

---

## Mid-Journey? Start Here

Already mid-project and not sure which skill to reach for next?

```
/restack-journey where
```

Describe what you've done so far. Claude will tell you where you are, what's been skipped, and what comes next.

---

## The Skills at a Glance

### The Journey Orchestrator
| Skill | When to use |
|-------|------------|
| `/restack-journey start` | Beginning any new engagement |
| `/restack-journey where` | Mid-project, unsure what's next |
| `/restack-journey iterate` | After stressor analysis — proceed or loop? |
| `/restack-journey review` | Health check — what's been missed? |
| `/restack-journey cadence` | Establishing rhythm for a live system |

### Discovery (Brownfield / Minefield)
| Skill | When to use |
|-------|------------|
| `/restack-discover paths` | Map what's actually in an existing system |
| `/restack-discover actor` | Confirm what an actor actually does |
| `/restack-discover intentions` | Trace how a signal propagates |
| `/restack-discover gaps` | Prioritise what's still unknown |
| `/restack-discover organisation` | Map resistance patterns as stressors |
| `/restack-discover confidence` | Are you ready to walk? |

### Stressor Analysis (every journey)
| Skill | When to use |
|-------|------------|
| `/restack-stressor walk` | Traverse a path — the foundational step |
| `/restack-stressor generate` | Generate stressors, including absurd ones 🐉 |
| `/restack-stressor analyze` | Build the impact matrix |
| `/restack-stressor vulnerabilities` | Find the most exposed actors |
| `/restack-stressor residues` | Identify residuals to reduce impact |
| `/restack-stressor iterate` | Re-walk after implementing residuals |
| `/restack-stressor compliance <pack>` | Inject compliance stressors |

### Design & Documentation
| Skill | When to use |
|-------|------------|
| `/restack-adr create` | Document every significant decision |
| `/restack-solution-doc hld` | High-Level Design |
| `/restack-solution-doc complete` | Full documentation set |
| `/restack-design-review complete` | Validate before building |
| `/restack-tech-stack recommend` | Technology selection |
| `/restack-cloud design` | Cloud-native architecture |
| `/restack-capacity estimate` | Resource sizing |

### Organisational Capabilities (ongoing)
| Skill | Cadence |
|-------|---------|
| `/restack-arch-learning analyze` | Quarterly |
| `/restack-capability-assessor assess` | Every 6 months |
| `/restack-patterns evolve` | Quarterly |
| `/restack-evolve health` | Monthly |

---

## Understanding the Philosophy

This toolkit is built on **Residuality Theory** — the practice of designing systems that don't just survive unexpected stress, but become stronger because of it.

Key principles:
- **Walk paths, don't just list components** — understanding how intentions flow through actors reveals what diagrams hide
- **Unknown unknowns matter most** — stressors include the absurd because real surprises are never on the list
- **Compliance as a byproduct** — regulatory requirements emerge as residuals of antifragile design
- **Capability transfer** — the measure of success is how little you need the toolkit because the thinking is internalised

→ [Read the full introduction to Residuality Theory](RESIDUALITY.md)

---

## Where Files Are Saved

```
docs/
  adr/                    # Architecture Decision Records
  architecture/           # HLD.md, LLD-*.md
  deployment/             # Deployment guides
  operations/             # Runbooks
  reviews/                # Design review reports
  technology/             # Tech stack reports
  stressor-analysis/      # Stressor matrices, residual recommendations
  cloud/                  # Cloud architecture docs and IaC
  capacity/               # Capacity estimates and forecasts
```

---

## Getting Help

- 📖 [Residuality Theory](RESIDUALITY.md) — the philosophy behind the toolkit
- 🔍 [Quick Reference](QUICKREF.md) — every command at a glance
- 📚 [Usage Guide](docs/USAGE.md) — detailed examples for every skill
- 🗺️ [Roadmap](ROADMAP.md) — what's built and what's next
- 🤝 [Contributing](CONTRIBUTING.md) — how to add compliance packs and skills

---

## First Steps Checklist

- [ ] Install and verify (`/` in Claude Code shows the skills)
- [ ] Read [Introduction to Residuality Theory](RESIDUALITY.md)
- [ ] Start your first journey (`/restack-journey start`)
- [ ] Walk your first path (`/restack-stressor walk`)
- [ ] Generate stressors — include at least one absurd one 🐉
- [ ] Create your first ADR (`/restack-adr create`)
- [ ] Star the repository ⭐

---

**Welcome to the Architect's Journey. Let's build antifragile systems together.** 🐉
