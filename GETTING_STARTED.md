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

> **Note:** Excel reading requires Python and openpyxl. If `/excel` commands fail, run: `pip install -r requirements.txt`

---

## Step 2: Verify

Open Claude Code and type `/` — you should see:

**Orchestration & Discovery:**
`/journey` `/discover`

**Stressor Analysis:**
`/stressor`

**Design & Documentation:**
`/adr` `/solution-doc` `/tech-stack` `/design-review`

**Cloud & Infrastructure:**
`/cloud` `/capacity`

**Organisational Capabilities:**
`/arch-learning` `/capability-assessor` `/patterns` `/evolve`

**Utilities:**
`/excel`

✅ If you see these, installation was successful.

---

## Step 3: Start Your Journey

The first thing to do with any new engagement isn't to open a specific skill — it's to understand where you are and what the terrain demands.

```
/journey start
```

Tell Claude about the system you're working on — what you're trying to achieve, what exists today, and any constraints. It will assess the terrain and map your recommended skill sequence from there.

**New to Residuality Theory?** Read the [Introduction to Residuality Theory](RESIDUALITY.md) first — it explains the philosophy behind the toolkit and the vocabulary all the skills share.

---

## The Three Terrains

The journey looks different depending on what you're walking into:

### Greenfield — blank canvas
You have an aspiration and nothing yet exists. You design the paths, then walk and stress them.

```
/journey start
→ /tech-stack → /adr → /solution-doc hld
→ /stressor walk → /stressor generate → /stressor analyze → /stressor residues
→ [iterate until impact sufficiently low]
→ /adr → /design-review → /solution-doc deployment
```

### Brownfield — existing system
Something is already there. You need to discover it before you can change it.

```
/journey start
→ /discover paths → /discover actor → /discover organisation → /discover confidence
→ /stressor walk → /stressor generate → /stressor analyze → /stressor residues
→ [iterate until impact sufficiently low]
→ /adr → /design-review → /solution-doc
```

### Minefield — high fragility, high complexity
An existing system with fragile dependencies, unclear paths, and organisational resistance. Discover extensively before touching anything.

```
/journey start
→ /discover paths → /discover actor → /discover intentions → /discover gaps
→ /discover organisation → /discover confidence
→ [if not confident — keep discovering]
→ /stressor walk → /stressor generate → /stressor analyze → /stressor residues
→ [iterate more cycles than brownfield]
→ /adr → /design-review → /solution-doc
```

---

## The Stressor Iteration Loop

At the heart of every journey is a loop, not a straight line:

```
walk paths → generate stressors → build matrix → find residuals
     ↑                                                  ↓
  re-walk ←← implement residuals ←← impact low enough? ←←
```

You keep iterating until the system's vulnerability is **sufficiently low** — not zero, but low enough given the aspiration and the cost of further improvement. Use `/journey iterate` to make that judgment explicitly rather than by instinct.

---

## Mid-Journey? Start Here

Already mid-project and not sure which skill to reach for next?

```
/journey where
```

Describe what you've done so far. Claude will tell you where you are, what's been skipped, and what comes next.

---

## The Skills at a Glance

### The Journey Orchestrator
| Skill | When to use |
|-------|------------|
| `/journey start` | Beginning any new engagement |
| `/journey where` | Mid-project, unsure what's next |
| `/journey iterate` | After stressor analysis — proceed or loop? |
| `/journey review` | Health check — what's been missed? |
| `/journey cadence` | Establishing rhythm for a live system |

### Discovery (Brownfield / Minefield)
| Skill | When to use |
|-------|------------|
| `/discover paths` | Map what's actually in an existing system |
| `/discover actor` | Confirm what an actor actually does |
| `/discover intentions` | Trace how a signal propagates |
| `/discover gaps` | Prioritise what's still unknown |
| `/discover organisation` | Map resistance patterns as stressors |
| `/discover confidence` | Are you ready to walk? |

### Stressor Analysis (every journey)
| Skill | When to use |
|-------|------------|
| `/stressor walk` | Traverse a path — the foundational step |
| `/stressor generate` | Generate stressors, including absurd ones 🐉 |
| `/stressor analyze` | Build the impact matrix |
| `/stressor vulnerabilities` | Find the most exposed actors |
| `/stressor residues` | Identify residuals to reduce impact |
| `/stressor iterate` | Re-walk after implementing residuals |
| `/stressor compliance <pack>` | Inject compliance stressors |

### Design & Documentation
| Skill | When to use |
|-------|------------|
| `/adr create` | Document every significant decision |
| `/solution-doc hld` | High-Level Design |
| `/solution-doc complete` | Full documentation set |
| `/design-review complete` | Validate before building |
| `/tech-stack recommend` | Technology selection |
| `/cloud design` | Cloud-native architecture |
| `/capacity estimate` | Resource sizing |

### Organisational Capabilities (ongoing)
| Skill | Cadence |
|-------|---------|
| `/arch-learning analyze` | Quarterly |
| `/capability-assessor assess` | Every 6 months |
| `/patterns evolve` | Quarterly |
| `/evolve health` | Monthly |

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
- [ ] Start your first journey (`/journey start`)
- [ ] Walk your first path (`/stressor walk`)
- [ ] Generate stressors — include at least one absurd one 🐉
- [ ] Create your first ADR (`/adr create`)
- [ ] Star the repository ⭐

---

**Welcome to the Architect's Journey. Let's build antifragile systems together.** 🐉
