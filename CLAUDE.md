# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ReStack** is a collection of Claude Code skills built on **Residuality Theory**, designed to build antifragile systems thinking and Solution Architect capabilities that compound over time.

## Architecture

### Project Structure

```
.
├── .github/workflows/skills.yml        # CI: generator drift + skills-tree validation
├── scripts/
│   ├── gen_skills.py                   # renders SKILL.md from SKILL.md.tmpl
│   ├── check_skills.py                 # validates frontmatter, banners, sections
│   └── preamble/                       # shared behaviour, composed by tier
│       ├── manifest.json               # tier -> fragment composition
│       ├── voice.md                    # tier 1
│       ├── completion-status.md        # tier 1
│       ├── decision-brief.md           # tier 2
│       ├── evidence.md                 # tier 2
│       ├── completeness.md             # tier 2
│       ├── confusion-protocol.md       # tier 2
│       ├── glossary.md                 # tier 3
│       ├── stop-gates.md               # tier 3
│       └── journey-state.md            # tier 3
├── skills/                                     # Claude Code layout: skills/<name>/SKILL.md
│   ├── restack-journey/                        # generated, tier 3
│   │   ├── SKILL.md.tmpl                       #   source of truth
│   │   ├── SKILL.md                            #   generated - do not edit
│   │   └── sections/                           #   route maps + terrain classification
│   ├── restack-discover/                       # generated, tier 3
│   │   ├── SKILL.md.tmpl
│   │   ├── SKILL.md
│   │   └── sections/                           #   confidence model, actor/intention protocols
│   ├── restack-stressor/                       # generated, tier 3
│   │   ├── SKILL.md.tmpl
│   │   ├── SKILL.md
│   │   ├── sections/                           #   walk, generation, matrix, residuals, workshop
│   │   └── compliance-packs/                   #   regulatory stressor packs
│   ├── restack-adr/                            # legacy
│   ├── restack-solution-doc/                   # legacy
│   ├── restack-tech-stack/                     # legacy
│   ├── restack-design-review/                  # legacy
│   ├── restack-cloud/                          # legacy
│   ├── restack-capacity/                       # legacy
│   ├── restack-arch-learning/                  # legacy
│   ├── restack-capability-assessor/            # legacy
│   ├── restack-patterns/                       # legacy
│   ├── restack-evolve/                         # legacy
│   └── restack-excel/                          # legacy
├── helpers/read_spreadsheet.py         # Python helper for Excel reading
├── templates/                          # Document templates
├── examples/                           # Example outputs
├── requirements.txt                    # Python dependencies (openpyxl)
└── docs/
    ├── journey/                        # Journey state for an engagement
    ├── adr/                            # ADR-001 .. ADR-009
    └── ...                             # Generated documentation location
```

### Skill Development Pattern

**`SKILL.md` is a build artifact — never edit it directly.** The source is
`skills/<name>/SKILL.md.tmpl`; run `python scripts/gen_skills.py` to render.
Hand edits to a generated file are lost at the next build. See
[ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md).

Converted so far: `/restack-journey`, `/restack-discover`, `/restack-stressor` — the residuality core.
The other eleven are still hand-maintained `SKILL.md` files and follow the
legacy structure below until they are converted. `scripts/check_skills.py`
reports which is which.

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
| 1 | utilities with no architectural judgement (`/restack-excel`) | voice, completion status |
| 2 | skills that shape architectural decisions | decision briefs, evidence rules, completeness, confusion protocol |
| 3 | the residuality core (`/restack-journey`, `/restack-stressor`, `/restack-discover`) | vocabulary, stop gates, journey state contract |

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
python scripts/check_skills.py          # CI: frontmatter, banners, orphaned sections
```

Both run in CI on every push and pull request (`.github/workflows/skills.yml`).
`check_skills.py` covers what the generator cannot: a skill with no
`description` is undiscoverable, a generated file with its banner removed has
been hand-edited, and a section file missing from `manifest.json` will never be
read by anything.

### Key Design Principle

Skills are **capability transfer tools**, not dependency-creating tools. Every skill should build thinking that architects carry forward independently. The measure of success is how rarely the skill needs to be invoked because the thinking has been internalised.

## Development Commands

### Testing Skills

```bash
# View skill content
cat skills/restack-adr/SKILL.md

# Symlink for development (changes reflected immediately)
ln -s "$(pwd)/skills/restack-adr" ~/.claude/skills/restack-adr

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

1. Create `skills/restack-stressor/compliance-packs/<framework>.md`
2. Follow the pack structure defined in `skills/restack-stressor/SKILL.md`
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
/restack-journey start           # Begin any engagement — assess terrain, map the route
/restack-journey where           # Mid-project: where am I, what comes next?
/restack-journey iterate         # Iterate stressor loop or proceed?
/restack-journey review          # Journey health check
/restack-journey cadence         # Establish an ongoing rhythm

/restack-discover paths                  # Map paths through an existing system
/restack-discover actor <name>           # Investigate what an actor actually does
/restack-discover intentions             # Trace how an intention propagates
/restack-discover gaps                   # Identify and prioritise confidence gaps
/restack-discover organisation           # Map organisational resistance as stressors
/restack-discover confidence             # Assess readiness to proceed to stressor analysis
```

### Individual Capabilities

```bash
/restack-adr create <title>              # Architecture Decision Records
/restack-solution-doc hld                # Solution Documentation
/restack-tech-stack recommend            # Technology Stack Advisor
/restack-design-review complete          # Design Review
/restack-stressor walk [path-name]       # Walk a path, evaluating each actor in sequence
/restack-stressor analyze                # Stressor Analysis — build impact matrix
/restack-stressor compliance <pack>      # Inject compliance stressor pack
```

### Organisational Capabilities

```bash
/restack-arch-learning analyze           # Architecture Learning Analyzer
/restack-capability-assessor assess      # Team Capability Assessor
/restack-patterns extract                # Pattern Extractor
/restack-evolve assess                   # Evolutionary Architecture Coach
```

### Specialised Tools

```bash
/restack-cloud design <architecture>     # Cloud Architect
/restack-cloud iac <provider>
/restack-cloud review
/restack-cloud cost
/restack-cloud migrate <to-cloud>
/restack-cloud dr

/restack-capacity estimate               # Capacity Planner
/restack-capacity scale <strategy>
/restack-capacity bottleneck
/restack-capacity load-test
/restack-capacity forecast
/restack-capacity right-size

/restack-excel read <file> [sheet]       # Excel/CSV Reader
```

## Journey Memory Management

The journey-state contract — which files exist, when they are read, when they
are written, and why conversation memory is not sufficient — is defined once,
in `scripts/preamble/journey-state.md`, and composed into every tier-3 skill.

Read that fragment rather than restating it here. It is the authority; this
file used to carry a second, differently-worded copy, which is exactly the
duplication [ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md)
was written to remove.

State lives in `docs/journey/`: `journey-state.md` (position, terrain,
aspiration, artifacts), `stressor-iteration-history.md` (per-iteration
matrices), `decisions-log.md` (every gate passed, with rationale), and
`assumptions-register.md` (unverified beliefs and what would settle them).

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
| Architect's Journey | `/restack-journey` | Orchestration |
| Environment Discovery | `/restack-discover` | Discovery |
| Architecture Decision Records | `/restack-adr` | Individual |
| Solution Documentation | `/restack-solution-doc` | Individual |
| Technology Stack Advisor | `/restack-tech-stack` | Individual |
| Design Review | `/restack-design-review` | Individual |
| Stressor Analysis | `/restack-stressor` | Individual |
| Architecture Learning Analyzer | `/restack-arch-learning` | Organisational |
| Team Capability Assessor | `/restack-capability-assessor` | Organisational |
| Pattern Extractor | `/restack-patterns` | Organisational |
| Evolutionary Coach | `/restack-evolve` | Organisational |
| Cloud Architect | `/restack-cloud` | Specialised |
| Capacity Planner | `/restack-capacity` | Specialised |
| Excel Reader | `/restack-excel` | Utility |

## Contributing

When adding new skills:
1. Follow existing skill patterns — especially the Capability Being Built and Residuality Goal sections
2. Create an ADR in `docs/adr/` for any significant design decision (including decisions *not* to build something)
3. Update all documentation files: README.md, QUICKREF.md, GETTING_STARTED.md, CLAUDE.md
4. Test thoroughly before committing
