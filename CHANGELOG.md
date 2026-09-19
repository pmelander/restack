# Changelog

All notable changes to ReStack. Versions follow the skill set as a whole;
individual skills carry their own `version:` in frontmatter.

## [2.4.0] — 2026-09-19

### Added

- **Optional cell scoring with Jev**, TypeSafe's decision model, in
  `/restack-stressor analyze` and `/restack-stressor residues`. The matrix is
  the one genuinely mechanical judgement in the method — a few hundred narrow,
  identical, binary calls — and it is currently made by the same model that
  generated the stressors and will read the result. Three roles, one instrument,
  and the middle one is the least defensible. One request per stressor carrying
  one yes/no question per actor; a 30×12 matrix is 30 requests, not 360.
  [ADR-014](docs/adr/ADR-014-jev-for-cell-scoring.md).
- **A band in the middle, which is the point.** `p >= 0.8` scores 1, `p <= 0.2`
  scores 0, and everything between comes back to the model to score as it always
  has. A decision model's value here is not that it is right more often, it is
  that it reports which cells it is unsure about — and those are exactly the
  cells that deserve a human-shaped judgement. The obvious design, a threshold
  at 0.5 and nobody in the loop, would have produced a matrix with no `?` cells
  and an empty assumptions register.
- **Jev never produces a `?` and never clears one.** A `?` records that the
  architecture is not understood well enough to answer, and carries the
  discovery step that would settle it. A probability near 0.5 is a different
  claim entirely. Collapsing the two would convert registered ignorance into a
  calibrated hedge, and `/restack-discover` would stop being told what to go and
  look at.
- `skills/restack-stressor/scripts/jev_score.py` — standard library only, key
  read from `TYPESAFE_API_KEY` and nowhere else, never printed. It refuses a
  request over the model's context budget instead of truncating it: a truncated
  path map scores cells against a system missing its last three actors and says
  nothing about it. Both of Jev's limits are checked — 64k for state plus all
  questions, 32k for state plus the longest single question — because a wide
  actor set trips the first long before any question approaches the second.
- **A per-row provenance line in the matrix** (`jev` / `model` / `mixed`), and
  the raw probabilities beside it in
  `docs/stressor-analysis/matrix-<date>.jev.json`. Two scoring paths means two
  ways a matrix can be wrong, and without the column nobody could tell which.
  It is also what lets `/restack-arch-learning` check ADR-014's prediction
  without re-scoring anything.

### Changed

- The model version is **pinned to `jev-1.13.0`** rather than the `jev-latest`
  alias, because the 0.8/0.2 bands are thresholds tuned against that version's
  calibration. An alias moves when a release ships; scoring would change with
  nothing in this repository changing, and the ADR's validation would quietly
  stop describing the model in use.
- Anonymisation is **mandatory** rather than recommended when sending under
  option A of the existing data gate. The actor set travels three times in every
  request — in the state, across the question map as ids, and inside each
  question's instruction text, because TypeSafe do not use the question id in
  inference. A request with an anonymised path map and real actor ids is not
  anonymised.

### Notes

- Optional, informational, never a gate, and **silent when absent**. No
  `TYPESAFE_API_KEY`, no scoring, and no mention of it — an architect who has
  never heard of Jev cannot tell from the output that any of this exists. Every
  HTTP error and every malformed row falls back to model scoring for that row
  and is recorded as having done so.
- The four "reading the matrix" checks stay with the model unconditionally.
  Scoring a cell and interpreting a column are different jobs, and only the
  second produces residuals. Suspicious zeros get a second look regardless of
  source — a confident zero from a model that has never seen the system is
  exactly the zero worth doubting.
- Executable code does not go in `scripts/shared/`. `setup` installs
  `skills/restack-*/` and nothing else, so a script there would only ever run
  from a checkout. The protocol is shared; the script it calls ships with the
  skill, per [ADR-010](docs/adr/ADR-010-skills-are-self-contained.md).

## [2.3.0] — 2026-09-17

### Added

- **`/restack-events`** — batches of event statements for use as stressors, with
  the distribution fixed by a seeded combinatorial sampler instead of by the
  model. Asked directly for "random events" an LLM collapses onto a narrow mode
  — the same few regions, the same institutional actors, the same register — and
  no amount of instruction fixes it, because the instruction is processed by the
  thing with the prior. `sample.py` draws the spec, one isolated subagent renders
  each one, `validate.py` checks the result. Standard library only; no API key,
  no network.
- **`grounding` as a first-class dimension** (`uncoupled`, `adjacent`, `aimed`),
  stratified with `plausibility` so every batch carries both blind draws and
  aimed ones by construction. This is what `/restack-stressor`'s `absurd`
  category was reaching for and kept missing: the active ingredient is
  unrelatedness to the system, not silliness. Fire-breathing lizards get waved
  away in the room; a mundane, entirely unrelated real-world event cannot be.
- **A leakage check on the blind tracks.** An `uncoupled` statement naming the
  system's sector or components means context reached a prompt that should not
  have had it — the batch's most valuable rows quietly converted into ordinary
  ones, with nothing else downstream to reveal it. Blocking, not advisory.
  Uncoupled renders run with no Read, Grep or Glob for the same reason: a
  subagent that can reach the filesystem may go and find the design docs itself.

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
