# Changelog

All notable changes to ReStack. Versions follow the skill set as a whole;
individual skills carry their own `version:` in frontmatter.

## [2.0.0] — 2026-09-05

The rewrite. Every skill regenerated from templates with shared behaviour, and
every skill wired into the residuality core.

### Added

- **Generated skills.** `skills/<name>/SKILL.md` is now built from
  `SKILL.md.tmpl` by `python scripts/gen_skills.py`. CI rejects drift.
- **Tiered shared preamble** (`scripts/preamble/`) — voice, decision briefs,
  evidence rules, completeness, confusion protocol, vocabulary, stop gates and
  the journey-state contract, composed by declared tier instead of restated per
  skill.
- **Decision briefs.** Judgement calls are structured `AskUserQuestion` briefs
  rating **confidence** and **reversibility**, and naming the aspiration served.
- **Three stop gates** — confidence (`/restack-discover confidence`), iterate
  (`/restack-journey iterate`), and approach gates wherever two designs are
  viable. They halt rather than drift past.
- **On-demand sections** — 42 across 13 skills, read when their situation
  applies rather than loaded on every invocation.
- **Evidence rules.** Documentation rates low; inference from a component's
  name is not evidence. Unverified claims become registered assumptions.
- **`NEEDS_DISCOVERY`** as a first-class completion status.
- **Matrix cross-check** in `/restack-design-review` — every finding classified
  by whether the stressor analysis should have caught it.
- **Residual traceability** in `/restack-adr` — which residual a decision
  implements and which stressors it clears, plus an explicit reversibility field.
- **Brittleness** in `/restack-evolve`, and fitness functions reframed as
  automated residual validation.
- **`setup` / `setup.ps1` and `/restack-upgrade`** — installation that reports
  what changed and removes skills deleted upstream; upgrade by `git pull`.
- CI (`.github/workflows/skills.yml`), `scripts/check_skills.py`, `VERSION`,
  this changelog.

### Changed

- **All skills prefixed `restack-`** ([ADR-009](docs/adr/ADR-009-prefix-skill-names.md)).
  An unprefixed install silently overwrote another suite's skill of the same
  name — `design-review` collided with gstack's.
- Renamed from *Residual Architecture Skill Set* to **ReStack**.
- Every skill moved to `model: opus` except `/restack-excel`.
- `templates/` is now canonical for document formats; skills carry method, not
  format. Removes the duplicate, thinner copies skills had embedded.
- Docs reorganised by journey position rather than by build phase.

### Fixed

- **`/restack-excel` was broken for every user outside the repository.** Its
  helper was invoked by a path relative to the working directory but was never
  installed. Now ships inside the skill
  ([ADR-010](docs/adr/ADR-010-skills-are-self-contained.md)).
- Four broken relative links, three of them long-standing.
- `/restack-stressor` listed the GDPR compliance pack as planned when it had
  shipped.

### Removed

- `STATUS.txt` — a Phase 1 completion snapshot describing four skills.
- `helpers/` — its one file moved into `/restack-excel`.

## [1.x] — 2026-05

Fourteen hand-maintained skills. Residuality Theory adopted
([ADR-001](docs/adr/ADR-001-incorporate-residuality-theory.md)); organisational
skills redesigned around capability building
([ADR-002](docs/adr/ADR-002-redesign-phase-2-for-capability-building.md));
stressor analysis added
([ADR-003](docs/adr/ADR-003-add-stressor-analysis-skill.md)); Excel utility
([ADR-004](docs/adr/ADR-004-add-excel-reading-utility.md)) and learning analyzer
([ADR-005](docs/adr/ADR-005-add-architecture-learning-analyzer.md)) added; risk
assessor deliberately excluded
([ADR-006](docs/adr/ADR-006-exclude-risk-assessor-skill.md)); compliance moved
to stressor packs
([ADR-007](docs/adr/ADR-007-compliance-via-stressor-packs.md)).
