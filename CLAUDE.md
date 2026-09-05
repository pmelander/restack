# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ReStack** is a collection of Claude Code skills built on **Residuality Theory**, designed to build antifragile systems thinking and Solution Architect capabilities that compound over time.

## Architecture

### Project Structure

```
.
├── skills/                             # Claude Code layout: skills/<name>/SKILL.md
│   ├── adr/
│   │   └── SKILL.md                    # /adr
│   ├── solution-doc/
│   │   └── SKILL.md                    # /solution-doc
│   ├── tech-stack/
│   │   └── SKILL.md                    # /tech-stack
│   ├── design-review/
│   │   └── SKILL.md                    # /design-review
│   ├── stressor/
│   │   ├── SKILL.md                    # /stressor
│   │   └── compliance-packs/           # Regulatory stressor packs
│   │       ├── README.md
│   │       └── gdpr.md
│   ├── excel/
│   │   └── SKILL.md                    # /excel
│   ├── arch-learning/
│   │   └── SKILL.md                    # /arch-learning
│   ├── capability-assessor/
│   │   └── SKILL.md                    # /capability-assessor
│   ├── patterns/
│   │   └── SKILL.md                    # /patterns
│   ├── evolve/
│   │   └── SKILL.md                    # /evolve
│   ├── cloud/
│   │   └── SKILL.md                    # /cloud
│   ├── capacity/
│   │   └── SKILL.md                    # /capacity
│   ├── discover/
│   │   └── SKILL.md                    # /discover
│   └── journey/
│       └── SKILL.md                    # /journey
├── helpers/
│   └── read_spreadsheet.py             # Python helper for Excel reading
├── templates/                          # Document templates
│   ├── journey-state-template.md
│   ├── adr-template.md
│   ├── hld-template.md
│   ├── tech-comparison-template.md
│   ├── stressor-analysis-template.md
│   ├── capability-assessment-template.md
│   ├── pattern-template.md
│   ├── anti-pattern-template.md
│   └── fitness-function-template.md
├── examples/                           # Example outputs
├── requirements.txt                    # Python dependencies (openpyxl)
└── docs/
    ├── journey/                        # Journey state tracking (REQUIRED)
    │   ├── journey-state.md            # Current position, iteration log, artifacts
    │   ├── stressor-iteration-history.md   # Detailed stressor iteration log
    │   ├── decisions-log.md            # Lightweight decision log
    │   ├── assumptions-register.md     # Assumptions and validation status
    │   └── cadence-schedule.md         # Ongoing rhythm and triggers
    ├── adr/                            # ADRs documenting toolkit decisions
    │   ├── ADR-001-incorporate-residuality-theory.md
    │   ├── ADR-002-redesign-phase-2-for-capability-building.md
    │   ├── ADR-003-add-stressor-analysis-skill.md
    │   ├── ADR-004-add-excel-reading-utility.md
    │   ├── ADR-005-add-architecture-learning-analyzer.md
    │   ├── ADR-006-exclude-risk-assessor-skill.md
    │   └── ADR-007-compliance-via-stressor-packs.md
    └── ...                             # Generated documentation location
```

### Skill Development Pattern

**`SKILL.md` is a build artifact — never edit it directly.** The source is
`skills/<name>/SKILL.md.tmpl`; run `python scripts/gen_skills.py` to render.
Hand edits to a generated file are lost at the next build. See
[ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md).

Converted so far: `/journey`, `/stressor`. The other twelve are still
hand-maintained `SKILL.md` files and follow the legacy structure below until
they are converted.

Each skill template follows this structure:
1. **Frontmatter** — `name`, `version`, `preamble-tier`, `model`, multi-line
   `description` (including when to invoke proactively), `allowed-tools`,
   `triggers`
2. **`{{PREAMBLE}}`** — shared behaviour composed by tier (see below)
3. **Role Definition** — clear statement of the skill's purpose
4. **Capability Being Built** — what thinking the skill transfers to the architect
5. **Residuality Goal** — what success looks like when the capability is internalised
6. **Core Concept** — the key idea and compound effect
7. **`{{SECTION_INDEX}}`** — the on-demand sections and when to read each
8. **Commands** — numbered, executable steps; not bullet summaries. Each names
   the section to read and the gates where it must **STOP**
9. **`{{SECTION_SELF_CHECK}}`** — catches sections run from memory
10. **Reflection Prompts** — questions that build the capability

### Preamble tiers

Declared per skill as `preamble-tier: N`. Each tier includes the ones below it.
Fragments live in `scripts/preamble/`, composed per `manifest.json`.

| Tier | For | Adds |
|---|---|---|
| 1 | utilities with no architectural judgement (`/excel`) | voice, completion status |
| 2 | skills that shape architectural decisions | decision briefs, evidence rules, completeness, confusion protocol |
| 3 | the residuality core (`/journey`, `/stressor`, `/discover`) | vocabulary, stop gates, journey state contract |

Change a cross-cutting behaviour once, in the fragment, then regenerate.

### Sections (on-demand depth)

Content that applies to some runs and not others goes in
`skills/<name>/sections/<id>.md`, registered in `sections/manifest.json` with a
human-readable `trigger`. The manifest is a passive registry — the skeleton's
prose decides when a section is read. This is what lets a skill carry deep
method without paying for it on every invocation.

### Build commands

```bash
python scripts/gen_skills.py            # regenerate everything with a template
python scripts/gen_skills.py journey    # one skill
python scripts/gen_skills.py --check    # CI: fail on drift between .tmpl and SKILL.md
```

### Key Design Principle

Skills are **capability transfer tools**, not dependency-creating tools. Every skill should build thinking that architects carry forward independently. The measure of success is how rarely the skill needs to be invoked because the thinking has been internalised.

## Development Commands

### Testing Skills

```bash
# View skill content
cat skills/adr/SKILL.md

# Symlink for development (changes reflected immediately)
ln -s "$(pwd)/skills/adr" ~/.claude/skills/adr

# Copy all for stable use
cp -R skills/* ~/.claude/skills/
```

### Adding New Skills

1. Create `skills/<skill-name>/SKILL.md.tmpl`
2. Declare frontmatter: `name`, `version`, `preamble-tier`, `model`,
   `description`, `allowed-tools`, `triggers`
3. Resolve `{{PREAMBLE}}` at the top of the body
4. Put situational depth in `sections/`, registered in `sections/manifest.json`
5. Follow the Skill Development Pattern above
6. Run `python scripts/gen_skills.py <skill-name>` and commit both the template
   and the generated `SKILL.md`
7. Document any significant design decisions as an ADR in `docs/adr/`
8. Update `README.md`, `QUICKREF.md`, `GETTING_STARTED.md`, and `CLAUDE.md`

### Adding Compliance Packs

1. Create `skills/stressor/compliance-packs/<framework>.md`
2. Follow the pack structure defined in `skills/stressor/SKILL.md`
3. Each stressor must be a concrete scenario (not a control statement)
4. Include regulation reference and explanation of the real harm
5. List common residuals that emerge from the analysis

### Git Workflow

```bash
git checkout -b feature/new-skill-name
git commit -m "feat: add skill-name skill"
git push origin feature/new-skill-name
```

## Skill Usage

### Journey & Discovery (start here)

```bash
/journey start           # Begin any engagement — assess terrain, map the route
/journey where           # Mid-project: where am I, what comes next?
/journey iterate         # Iterate stressor loop or proceed?
/journey review          # Journey health check
/journey cadence         # Establish an ongoing rhythm

/discover paths                  # Map paths through an existing system
/discover actor <name>           # Investigate what an actor actually does
/discover intentions             # Trace how an intention propagates
/discover gaps                   # Identify and prioritise confidence gaps
/discover organisation           # Map organisational resistance as stressors
/discover confidence             # Assess readiness to proceed to stressor analysis
```

### Individual Capabilities

```bash
/adr create <title>              # Architecture Decision Records
/solution-doc hld                # Solution Documentation
/tech-stack recommend            # Technology Stack Advisor
/design-review complete          # Design Review
/stressor walk [path-name]       # Walk a path, evaluating each actor in sequence
/stressor analyze                # Stressor Analysis — build impact matrix
/stressor compliance <pack>      # Inject compliance stressor pack
```

### Organisational Capabilities

```bash
/arch-learning analyze           # Architecture Learning Analyzer
/capability-assessor assess      # Team Capability Assessor
/patterns extract                # Pattern Extractor
/evolve assess                   # Evolutionary Architecture Coach
```

### Specialised Tools

```bash
/cloud design <architecture>     # Cloud Architect
/cloud iac <provider>
/cloud review
/cloud cost
/cloud migrate <to-cloud>
/cloud dr

/capacity estimate               # Capacity Planner
/capacity scale <strategy>
/capacity bottleneck
/capacity load-test
/capacity forecast
/capacity right-size

/excel read <file> [sheet]       # Excel/CSV Reader
```

## Journey Memory Management

**CRITICAL REQUIREMENT:** Journey progress MUST be persisted to file at every significant step.

### Journey State Files

When executing `/journey` commands, you MUST maintain these files in `docs/journey/`:

1. **`journey-state.md`** — current position, aspiration, terrain type, iteration log, artifacts, gaps
   - Update after EVERY `/journey` command
   - Update after executing skills within the journey (discover, stressor, adr, etc.)
   - This is the single source of truth for journey progress

2. **`stressor-iteration-history.md`** — detailed log of each stressor iteration with impact matrices
   - Update after every `/stressor analyze` and `/journey iterate`

3. **`decisions-log.md`** — lightweight log of decision points (supplement to formal ADRs)
   - Update whenever a significant decision is made

4. **`assumptions-register.md`** — assumptions being carried forward with validation status
   - Update when assumptions are identified or validated

### When to Update

**ALWAYS update journey state when:**
- Starting a journey (`/journey start`)
- Checking position (`/journey where`)
- Making iteration decisions (`/journey iterate`)
- Reviewing journey health (`/journey review`)
- Establishing cadence (`/journey cadence`)
- Completing discovery commands
- Completing stressor analysis iterations
- Creating ADRs
- Generating solution documentation
- Completing design reviews

**Before executing a journey command:** Read `docs/journey/journey-state.md` to understand context.

**After executing a journey command:** Update `docs/journey/journey-state.md` with outcomes.

### Rationale

Built-in memory in Claude Code is insufficient for long-running architectural journeys that may:
- Span weeks or months
- Resume after breaks
- Involve multiple architects
- Require audit trails
- Need iteration history for learning

File-based persistence ensures journey continuity, enables handoffs, and creates an audit trail of architectural thinking.

---

## Key Principles

### Residuality Theory Foundation

1. **Design for unknown unknowns** — not just known risks
2. **Antifragility over robustness** — systems that benefit from stress
3. **Residuals over mitigations** — architectural improvements that protect against classes of stressors
4. **Compliance as byproduct** — regulatory requirements addressed structurally, not procedurally
5. **Risk assessment replaced** — stressor analysis covers risk and more

### For Skill Development

1. **Capability first** — every command should build a thinking skill, not just produce output
2. **Clear residuality goal** — state what success looks like when the skill is no longer needed
3. **Reflection prompts** — include questions that deepen the thinking
4. **Consistent philosophy** — new skills must align with Residuality Theory; if a skill would train architects to think in checklists or registers, reconsider the approach

## Installation

```bash
# Copy method (stable use)
cp -R skills/* ~/.claude/skills/
pip install -r requirements.txt

# Symlink method (development — changes reflected immediately)
ln -s /path/to/repo/skills/* ~/.claude/skills/
```

## Skills

| Skill | Command | Category |
|-------|---------|----------|
| Architect's Journey | `/journey` | Orchestration |
| Environment Discovery | `/discover` | Discovery |
| Architecture Decision Records | `/adr` | Individual |
| Solution Documentation | `/solution-doc` | Individual |
| Technology Stack Advisor | `/tech-stack` | Individual |
| Design Review | `/design-review` | Individual |
| Stressor Analysis | `/stressor` | Individual |
| Architecture Learning Analyzer | `/arch-learning` | Organisational |
| Team Capability Assessor | `/capability-assessor` | Organisational |
| Pattern Extractor | `/patterns` | Organisational |
| Evolutionary Coach | `/evolve` | Organisational |
| Cloud Architect | `/cloud` | Specialised |
| Capacity Planner | `/capacity` | Specialised |
| Excel Reader | `/excel` | Utility |

## Contributing

When adding new skills:
1. Follow existing skill patterns — especially the Capability Being Built and Residuality Goal sections
2. Create an ADR in `docs/adr/` for any significant design decision (including decisions *not* to build something)
3. Update all documentation files: README.md, QUICKREF.md, GETTING_STARTED.md, CLAUDE.md
4. Test thoroughly before committing
