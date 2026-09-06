# Changelog

All notable changes to ReStack. Versions follow the skill set as a whole;
individual skills carry their own `version:` in frontmatter.

## [2.2.2] — 2026-09-06

### Added

- **Attestation vs input echo** in the actor-investigation protocol. A manifest
  field that looks like an upstream attestation may be a value you supplied and
  got back — in which case it records what you asked for, not what they did, and
  cannot detect their drift. Found by running `/restack-discover actor` against
  a real external boundary, where a `extract_spec_version` field read exactly
  like the control for a semantic-drift stressor and turned out to be an
  idempotency key sourced from the consumer's own config.

## [2.2.1] — 2026-09-06

### Added

- `setup` and `setup.ps1` report whether the Codex CLI is present, and say what
  its absence costs — the outside opinion falls back to a same-family subagent
  that shares blind spots. README, INSTALL.md and the installation guide
  document both optional extras.

### Removed

- The "formerly Residual Architecture Skill Set" note from the README. The
  rename is recorded in the changelog and the git history; the front page does
  not need it.

### Added

- **An outside opinion**, in the three places it earns its cost: stressor
  generation (asking a different model for the *complement* of your list —
  the strongest use, and a direct attack on the comfortable-stressors failure),
  residual identification (two independent diagnoses of a cluster, ours
  withheld), and design review on a one-way door. Probes for Codex, falls back
  to a fresh subagent, every error non-blocking.
  [ADR-013](docs/adr/ADR-013-outside-opinion.md).
- **A data gate before anything is sent.** What ReStack would send is a path map
  of a real system and a ranked account of where it is weakest — categorically
  more sensitive than a design summary. Anonymised is the recommended default,
  because the method works on mechanism and needs no identity, so the safer
  option costs no accuracy.
- **Shared sections** — `"shared": true` in a manifest resolves content from
  `scripts/shared/`, so method used by several skills lives once and is still
  read on demand.
- Stressors from an outside model are tagged `external`.

### Corrected after the first live run

Tested against codex-cli 0.153.4 on a real engagement, which corrected three
things the guidance had wrong or missing:

- **Failure detection.** `codex exec` writes its banner *and a copy of the
  answer* to stderr on success, so "stderr is non-empty" is a broken failure
  test that would fail every successful run. Gate on exit status; use stderr
  only to classify which failure occurred. Real unauthenticated text is
  `401 Unauthorized` / `Missing bearer or basic authentication`, and it takes
  ~10s to surface because the client retries 5× over WebSocket then 5× over
  HTTPS.
- **The absurd-stressor instruction does not survive a terse structured prompt**
  — the model optimises for the format directive and drops it. Ask separately,
  or keep generating those yourself.
- **Verify every "nothing covers this" claim.** The outside model cannot see
  your ADRs. On the first run, 6 of 10 claims survived checking; the rest were
  adjacent to existing decisions.

### Changed

- Refused at terrain classification, the confidence gate and the iterate gate:
  those are judgements about what you do not know about your own system, where
  an outside model knows strictly less than you do.
- `/restack-stressor` and `/restack-design-review` to v2.2.0.
- `check_skills.py` validates shared sections and counts them in the per-skill
  section totals.

## [2.1.1] — 2026-09-06

### Fixed

- **`setup --symlink` silently installed by copy on Windows and claimed
  otherwise.** Git Bash without symlink support copies when `ln -s` is used —
  exit status 0, and you get a directory. setup then printed "edits in the repo
  are live", which was false. Both scripts now probe symlink capability up
  front, degrade to copy with a warning naming the fix, verify each link, and
  report the method actually used. `setup.ps1` had the same defect in a
  different form: `New-Item -ItemType SymbolicLink` throws without Developer
  Mode, which would have aborted the install partway through.
- `/restack-upgrade`'s repair table now covers the degraded-symlink case.

## [2.1.0] — 2026-09-06

First changes driven by field evidence rather than by reasoning about the
toolkit. A real engagement built with v1 — 42 ADRs, 9 LLDs, 2 stressor
iterations, 5 design reviews — was used to test v2's mechanisms against
something they had never seen. See
[ADR-012](docs/adr/ADR-012-artifact-consistency-as-a-review-dimension.md).

### Added

- **Artifact consistency as a review dimension** —
  `/restack-design-review consistency`, plus a section covering six checks: ADR
  against ADR, ADR against design docs, actors against the HLD, residuals
  against their records, placeholders and empty evidence, and operational
  documents against the current design. `complete` runs it last.

### Changed

- **The matrix cross-check now triages before it classifies.** Findings split
  into *system* findings, which classify A/B/C/D, and *artifact* findings,
  which do not and are reported separately. The reference engagement had 32
  review findings and 4 citations of any stressor or residual id; its
  *critical* finding was a deployment guide contradicting an ADR — which the
  four-class scheme could not express.
- Review reports separate system findings from artifact findings, and note the
  ratio: mostly-artifact means the analysis is sound and the documents are not
  keeping up.
- `/restack-solution-doc review` hands drift checking to
  `/restack-design-review consistency` — a document reviewed against itself
  cannot reveal drift, because drift is a property of the set.
- `/restack-design-review` and `/restack-solution-doc` to v2.1.0.

### Validated

- The residual-traceability fields v2 added to `/restack-adr` were worth it: of
  42 v1 ADRs, 5 mention a residual id and none record reversibility.

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
  this changelog. `check_skills.py` verifies that **every install path a skill
  tells Claude to use actually resolves** — the check that would have caught
  the `/restack-excel` helper bug three refactors earlier.

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
