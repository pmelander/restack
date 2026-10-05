# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ReStack** is a collection of Claude Code skills built on **Residuality Theory**, designed to build antifragile systems thinking and Solution Architect capabilities that compound over time.

## Architecture

### Project Structure

```
.
├── setup / setup.ps1                   # install the skills into ~/.claude/skills
├── VERSION  CHANGELOG.md  INSTALL.md
├── .github/workflows/skills.yml        # CI: generator drift, skills-tree validation, tests
├── tests/                              # unittest, stdlib only - shipped scripts' behaviour
├── scripts/
│   ├── gen_skills.py                   # renders SKILL.md from SKILL.md.tmpl
│   ├── check_skills.py                 # validates frontmatter, banners, sections
│   ├── shared/                         # method shared by several skills, vendored into each
│   │   ├── second-opinion.md           #   outside opinion (stressor, design-review)
│   │   ├── update-check.md             #   update notice at session open (journey, discover)
│   │   └── trace.md                    #   document-drift worklist (design-review, journey, adr, solution-doc, trace)
│   └── preamble/                       # shared behaviour, composed by tier
│       ├── manifest.json               # tier -> fragment composition
│       ├── voice.md                    # tier 1
│       ├── paths-and-shell.md          # tier 1
│       ├── questions.md                # tier 1
│       ├── completion-status.md        # tier 1
│       ├── next-command.md             # tier 1
│       ├── decision-brief.md           # tier 2
│       ├── evidence.md                 # tier 2
│       ├── completeness.md             # tier 2
│       ├── confusion-protocol.md       # tier 2
│       ├── journey-files.md            # tier 2: write the journey files with journey.py
│       ├── glossary.md                 # tier 3
│       ├── stop-gates.md               # tier 3
│       └── journey-state.md            # tier 3
├── skills/                                     # Claude Code layout: skills/<name>/SKILL.md
│   ├── restack-journey/                        # generated, tier 3
│   │   ├── SKILL.md.tmpl                       #   source of truth
│   │   ├── SKILL.md                            #   generated - do not edit
│   │   ├── scripts/journey.py                  #   writes + migrates the journey files, run by every tier 2-3 skill
│   │   └── sections/                           #   route maps + terrain classification
│   ├── restack-discover/                       # generated, tier 3
│   │   ├── SKILL.md.tmpl
│   │   ├── SKILL.md
│   │   └── sections/                           #   confidence model, actor/intention protocols
│   ├── restack-stressor/                       # generated, tier 3
│   │   ├── SKILL.md.tmpl
│   │   ├── SKILL.md
│   │   ├── sections/                           #   walk, generation, matrix, residuals, workshop
│   │   ├── scripts/matrix.py                   #   matrix arithmetic: totals, compare, residual claims
│   │   └── compliance-packs/                   #   regulatory stressor packs
│   ├── restack-events/                         # generated, tier 2
│   │   ├── SKILL.md.tmpl
│   │   ├── SKILL.md
│   │   ├── scripts/                            #   sampler + validator, ship with the skill
│   │   ├── reference/                          #   taxonomy weights, register guidance
│   │   └── sections/                           #   grounding, render protocol, handoff
│   ├── restack-adr/                            # generated, tier 2
│   ├── restack-solution-doc/                   # generated, tier 2
│   ├── restack-tech-stack/                     # generated, tier 2
│   ├── restack-design-review/                  # generated, tier 2
│   ├── restack-cloud/                          # generated, tier 2
│   ├── restack-capacity/                       # generated, tier 2
│   ├── restack-arch-learning/                  # generated, tier 2
│   ├── restack-capability-assessor/            # generated, tier 2
│   ├── restack-patterns/                       # generated, tier 2
│   ├── restack-evolve/                         # generated, tier 2
│   ├── restack-excel/                          # generated, tier 1
│   │   └── read_spreadsheet.py                #   runtime helper, ships with the skill
│   ├── restack-trace/                          # generated, tier 1
│   │   └── scripts/trace.py                    #   document drift, run by review, journey, adr, solution-doc
│   └── restack-upgrade/                        # generated, tier 1
│       ├── scripts/update_check.py             #   update check, run by journey + discover
│       └── scripts/local_copies.py             #   old ReStack copies in a project or profile (retire-local)
├── templates/                          # Document templates, vendored into the skills that write them
├── examples/                           # Example outputs
├── requirements.txt                    # Python dependencies (openpyxl)
└── docs/
    ├── journey/                        # Journey state for an engagement
    ├── adr/                            # ADR-001 .. ADR-028
    └── ...                             # Generated documentation location
```

### Skill Development Pattern

**`SKILL.md` is a build artifact — never edit it directly.** The source is
`skills/<name>/SKILL.md.tmpl`; run `python scripts/gen_skills.py` to render.
Hand edits to a generated file are lost at the next build. See
[ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md).

**All seventeen skills are generated.** Tiers: `/restack-journey`,
`/restack-discover` and `/restack-stressor` at 3 (the residuality core);
`/restack-excel`, `/restack-trace` and `/restack-upgrade` at 1 (utilities); the
other eleven at 2.
`scripts/check_skills.py` reports the current state.

Each skill template follows this structure:
1. **Frontmatter** — `name`, `version`, `preamble-tier`, `model`, multi-line
   `description` (including when to invoke proactively), `allowed-tools`,
   `triggers`
2. **`{{PREAMBLE}}`** — shared behaviour composed by tier (see below)
3. **Role Definition** — clear statement of the skill's purpose
4. **What it produces** — the artifacts the skill writes, and where
5. **Done when** — the quality bar those artifacts must meet before the skill
   reports done; checkable, not aspirational
6. **Core Concept** — the key idea and compound effect
7. **`{{SECTION_INDEX}}`** — the on-demand sections and when to read each
8. **Commands** — numbered, executable steps; not bullet summaries. Each names
   the section to read and the gates where it must **STOP**
9. **`{{SECTION_SELF_CHECK}}`** — catches sections run from memory

### Preamble tiers

Declared per skill as `preamble-tier: N`. Each tier includes the ones below it.
Fragments live in `scripts/preamble/`, composed per `manifest.json`.

| Tier | For | Adds |
|---|---|---|
| 1 | utilities with no architectural judgement (`/restack-excel`) | voice, paths and shell, questions, completion status, next command |
| 2 | skills that shape architectural decisions | decision briefs, evidence rules, completeness, confusion protocol |
| 3 | the residuality core (`/restack-journey`, `/restack-stressor`, `/restack-discover`) | vocabulary, stop gates, journey state contract |

Change a cross-cutting behaviour once, in the fragment, then regenerate.

`next-command.md` is how a command hands off: a `Next:` line, then the
command runs through the `Skill` tool in the same turn. A chain of commands
pauses only at questions: a decision brief or gate, the confusion protocol,
something only a person can supply, or two genuinely close next moves
([ADR-020](docs/adr/ADR-020-follow-up-commands-run-without-pause.md)). Where
`Skill` is unavailable, the command is handed over in a fenced block tagged
`text`, never a shell tag
([ADR-018](docs/adr/ADR-018-next-command-as-a-copy-block.md)). A skill that
names its next move should use it rather than invent its own format, and every
skill lists `Skill` in `allowed-tools`. `questions.md` makes every question a
choice through `AskUserQuestion`, confirms included. Rendering
the move as a `show_widget` button was built and withdrawn in 2.5.2 because
clicks were unreliable. Read
[ADR-017](docs/adr/ADR-017-next-step-as-a-button.md) before trying that again.

### Sections (on-demand depth)

Content that applies to some runs and not others goes in
`skills/<name>/sections/<id>.md`, registered in `sections/manifest.json` with a
human-readable `trigger`. The manifest is a passive registry — the skeleton's
prose decides when a section is read. This is what lets a skill carry deep
method without paying for it on every invocation.

**Every section path is written `<base>/sections/<file>.md`**, where `<base>` is
the skill's base directory as Claude Code prints it at load. Never write
`skills/<name>/sections/...`, `scripts/shared/...` or `templates/...` in a
skill: those resolve from this checkout and nowhere else, and
`check_skills.py` fails on them
([ADR-015](docs/adr/ADR-015-vendored-sections-and-base-relative-paths.md)).

**Shared sections.** Method used by several skills lives once in
`scripts/shared/` and is registered with `"shared": true` in each consuming
manifest. `gen_skills.py` **vendors** a generated copy into each consuming
skill's `sections/`, because `setup` installs `skills/restack-*/` and nothing
else. In use: `scripts/shared/second-opinion.md`
([ADR-013](docs/adr/ADR-013-outside-opinion.md)) and
`scripts/shared/update-check.md`
([ADR-016](docs/adr/ADR-016-update-awareness.md)). Prefer a shared section over
duplicating method into two skills; prefer an owned section when only one skill
needs it. Edit the source, never the vendored copy; its banner says so.

**Canonical templates** a skill writes against (`templates/*.md`) are vendored
the same way, with `"source": "templates/<file>"` in the manifest.

**A shared section is prose, read by Claude. Executable code never goes in
`scripts/shared/`** — `setup` installs `skills/restack-*/` and nothing else, so
a script there would run only from a checkout and never from an install. Shared
*method* belongs in `scripts/shared/`; the script that method calls belongs in
the skill, per [ADR-010](docs/adr/ADR-010-skills-are-self-contained.md).

### Build commands

```bash
python scripts/gen_skills.py            # regenerate everything with a template
python scripts/gen_skills.py journey    # one skill
python scripts/gen_skills.py --check    # CI: fail on drift between .tmpl and SKILL.md
python scripts/check_skills.py          # CI: frontmatter, banners, sections, install paths
python -m unittest discover -s tests    # CI: behaviour of the scripts skills ship
```

All three run in CI on every push and pull request (`.github/workflows/skills.yml`).
`check_skills.py` covers what the generator cannot: a skill with no
`description` is undiscoverable, a generated file with its banner removed has
been hand-edited, a section file missing from `manifest.json` will never be
read by anything, and **an install path a skill tells Claude to use must
actually resolve** — `/restack-excel` invoked a helper by a path that was never
installed and survived three refactors because nothing checked
([ADR-010](docs/adr/ADR-010-skills-are-self-contained.md)).

Paths written into the *user's* project (`docs/...`), placeholders and runtime
state are deliberately not checked; the rule is conservative because a
validator that cries wolf gets muted, and a muted check is a failed control.

### Key Design Principle

ReStack is a **working toolkit** for residuality-based architecture, not a
training pack ([ADR-022](docs/adr/ADR-022-working-toolkit-not-training-pack.md)).
The skills do the method and the bookkeeping in full: discovery, stressor
analysis, decisions, documentation, and keeping a long engagement consistent.
**The architect owns the decisions.** Gates, decision briefs and "never
auto-resolve" exist because the architect answers for the design, not to
teach them. A skill is measured by the quality and traceability of what it
produces, not by how rarely it is needed.

## Development Commands

### Testing Skills

```bash
# View a generated skill
cat skills/restack-adr/SKILL.md

# Install your edits: regenerate, then copy into ~/.claude/skills
python scripts/gen_skills.py && ./setup

# See what an install would change, without writing
./setup --dry-run
```

The install is always a copy in the user profile
([ADR-019](docs/adr/ADR-019-copy-only-install.md)). There is no symlinked
development mode: sessions load what was last installed, not the working tree,
so another session's half-finished edits never leak into yours. Re-run
`./setup` after every regenerate you want to try.

**Agents: never run `./setup` against the real profile to test it.** The tests
in `tests/` point `HOME` and `USERPROFILE` at a scratch directory, and so
should anything else that exercises the installers.

Do not hand-roll the install with `cp -R` or `ln -s`: `setup` also removes
skills deleted upstream, refuses a broken tree, and records where it installed
from so `/restack-upgrade` can find it ([ADR-011](docs/adr/ADR-011-setup-script-and-upgrade-skill.md)).

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

### Skills that ship executable scripts

`/restack-excel`, `/restack-events`, `/restack-journey`, `/restack-stressor`,
`/restack-trace` and `/restack-upgrade` ship Python alongside their SKILL.md.
Two rules follow from [ADR-010](docs/adr/ADR-010-skills-are-self-contained.md):

1. **Standard library only.** A skill runs from whatever project the architect
   is in, not from this checkout, and a script that needs its own install is a
   script people skip. `/restack-excel` needs openpyxl for `.xlsx` and says so
   when it is missing; nothing else may add a dependency.
2. **Reference scripts by their installed path.** Resolve once per session to
   `$HOME/.claude/skills/<name>/...` with the repo path as fallback, as both
   skills do. `check_skills.py` verifies these resolve — a bare relative path
   only works when the working directory happens to be this repository, which
   is the bug that ADR exists to stop.
3. **Test what the script does, in `tests/`.** `check_skills.py` proves a
   path resolves, not that the script behaves. `tests/test_update_check.py`
   runs every silent path, the throttle, snooze and opt-out, and the shared
   section's shell snippets as written, against a scratch `~/.restack`
   (`RESTACK_STATE_DIR`) and a local bare repository. Never test against the
   real `~/.restack` or the live skills directory. `tests/test_trace.py` runs
   every check against `tests/fixtures/trace/`, a synthetic engagement with a
   planted defect and a clean neighbour per check. `tests/test_journey.py`
   runs every write and the migration against `tests/fixtures/journey/`, a
   canonical journey, a legacy one and one with asks, and checks that
   migration loses no word and that recording a sent ask changes no status.
   `tests/test_matrix.py` runs the matrix arithmetic against
   `tests/fixtures/matrix/`, two iterations and their residuals with the
   numbers known. `tests/test_local_copies.py` builds scratch projects with old copies
   and look-alikes. **Anything that runs `update_check.py check` points
   `HOME`, `USERPROFILE` and the working directory at scratch**: the check
   also reads the project's and the profile's `.claude` folders. **Fixtures
   are invented, never taken from a real engagement**: this repository is
   public.

Three scripts are called by other skills, and every dependency is optional
by construction. `journey.py` is run by every tier 2 and 3 skill through the
`journey-files.md` preamble fragment; if it is missing, the snippet says so
and the files are written by hand in their canonical shape
([ADR-023](docs/adr/ADR-023-journey-files-written-by-a-helper.md)). **It
writes only canonical files, and `migrate` changes structure only**: a change
to it must never let a write or a migration alter a status, a decision or a
date on the architect's behalf. Recording a sent ask repeats the row's
status rather than taking one, for the same reason
([ADR-026](docs/adr/ADR-026-asks-routed-in-the-register.md)); cancelling a send recorded in error
likewise repeats the status
([ADR-027](docs/adr/ADR-027-asks-triaged-with-the-architect-first.md)). `update_check.py` is run by `/restack-journey` and
`/restack-discover` through `update-check.md`; if it is missing, the snippet
prints nothing, which is the same as "up to date"
([ADR-016](docs/adr/ADR-016-update-awareness.md)). `trace.py` is run by
design-review, journey, adr and solution-doc through `trace.md`; if it is
missing, the skill says so and does the checks by hand
([ADR-021](docs/adr/ADR-021-trace-checks-as-a-worklist.md)). **trace's output
is a worklist, not a verdict**: a check added to it must point at something a
reader confirms, never rate it.

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
/restack-journey asks [who]      # Architect answers first; send-ready asks for the rest

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

/restack-trace [docs]                    # document drift: a worklist to confirm
/restack-trace only <codes> [docs]       # some checks: REF REG KO AM SUP BASE MX ALERT PH PDF
/restack-trace terms <term>...           # unmarked uses of a replaced mechanism's terms
/restack-trace refs <ID>                 # every citation of ADR-12, D7 or A-31

/restack-upgrade                         # pull, reinstall, show what changed
/restack-upgrade check                   # verify the install + update-check status
/restack-upgrade snooze [days]           # hide the daily update notice
/restack-upgrade off | on                # the update-check opt-out (~/.restack/config.json)
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

1. **Output first** — every command produces something the engagement uses: an
   artifact, a decision, a finding, a gate passed
2. **A checkable bar** — "Done when" states what the output must meet, in terms
   someone could verify
3. **Decisions stay with the architect** — the skill frames the call and stops;
   it never makes a call the architect answers for
4. **Consistent method** — new skills must align with Residuality Theory. A
   skill that reduces the method to a checklist or a risk register is the wrong
   shape, because a checklist covers only what its author already feared

## Installation

```bash
./setup                 # copy into ~/.claude/skills; the only install method
./setup --dry-run       # what would change, without writing
pip install -r requirements.txt   # optional; /restack-excel only
```

Windows: `.\setup.ps1` with `-DryRun` / `-Quiet`.
Update later with `/restack-upgrade`, which installs the latest release from a
temporary clone and never touches a checkout.

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
| Document Trace | `/restack-trace` | Utility |
| Upgrade | `/restack-upgrade` | Utility |

## Contributing

When adding new skills:
1. Follow existing skill patterns — especially the What it produces and Done when sections
2. Create an ADR in `docs/adr/` for any significant design decision (including decisions *not* to build something)
3. Update all documentation files: README.md, QUICKREF.md, GETTING_STARTED.md, CLAUDE.md
4. Test thoroughly before committing
