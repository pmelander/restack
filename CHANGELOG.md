# Changelog

All notable changes to ReStack. Versions follow the skill set as a whole;
individual skills carry their own `version:` in frontmatter.

## [2.5.0] — 2026-10-02

Update awareness ([ROADMAP](ROADMAP.md) item 6). An install now hears that it
is stale without anyone remembering to ask. 2.4.0 fixed defects that failed
silently in every install, and an install that never upgrades keeps them, with
nothing to say so ([ADR-016](docs/adr/ADR-016-update-awareness.md)).

### Added

- **A one-line update notice at session open.** `/restack-journey start` and
  `where`, and `/restack-discover paths`, run a check at most once a day and
  print `ReStack v{new} available (installed v{old}): /restack-upgrade`, with a
  snooze offer on the same line. Up to date, offline, no checkout, no
  `install.json` and no Python all print nothing. The check never runs while a
  decision brief is open or inside a stop gate, and it never upgrades anything:
  a skill set that changes under an in-flight journey breaks its audit trail.
  The instructions live once, in a shared section (`update-check.md`).
- **`/restack-upgrade snooze [days]`, `off` and `on`.** A snooze holds one
  version for seven days by default, and a newer release breaks through it.
  `off` writes `{"update_check": false}` to `~/.restack/config.json`.
  `RESTACK_UPDATE_CHECK=off` in the environment also turns it off and wins over
  the file, for machines where an outbound fetch from a skill is not
  acceptable. A `config.json` that cannot be read counts as off.
  `/restack-upgrade check` now shows the setting, the last check and any
  snooze, including a check that failed.
- **`skills/restack-upgrade/scripts/update_check.py`**, standard library only.
  The only network call is `git fetch origin main` in the recorded checkout,
  capped at five seconds, with credential prompts and windows suppressed.
- **`tests/test_update_check.py`**, 34 cases, run in CI. They cover every silent
  path, the throttle, the snooze, both opt-outs, both symlink wordings, Git Bash
  paths, a BOM in `install.json`, a transport that never answers, and the
  section's `sh`, `bash` and PowerShell snippets exactly as written.

### Fixed

- **`/restack-upgrade` could replace a symlinked install with copies.** Step 4
  ran plain `./setup`. On a symlinked install it now runs a `--symlink`
  dry run and asks the architect to re-link from a shell that can create
  symlinks, if a skill was added or removed. Step 3 stops when the checkout is
  not on `main`. `docs/INSTALLATION.md` said "`./setup` after a pull" for
  symlink installs, and now says `./setup --symlink`.

### Decided

- **Symlinked development installs report, with different wording**, the open
  question from the roadmap. On `main` the notice names
  `git -C "<repo>" pull --ff-only`. On a branch it only reports the gap. It
  never points at the copy upgrade
  ([ADR-016](docs/adr/ADR-016-update-awareness.md)).

### Changed

- `/restack-journey` 2.2.0, `/restack-discover` 2.2.0, `/restack-upgrade` 1.3.0.

## [2.4.0] — 2026-10-02

Twenty improvements from one long brownfield journey: discovery, three stressor
iterations, ADRs, HLD/LLD/runbook, a consistency review and an ADR amendment
batch. Ordered by the damage each gap did.

### Fixed

- **Shared sections and templates were never installed.** `setup` installs
  `skills/restack-*/` only, so `second-opinion.md` (indexed by
  `/restack-stressor` and `/restack-design-review`) and nine `templates/*.md`
  references existed only in a checkout. The outside opinion silently never
  ran for a copy install. Both are now vendored into each consuming skill by
  `gen_skills.py` ([ADR-015](docs/adr/ADR-015-vendored-sections-and-base-relative-paths.md)).
- **Section paths resolved against the wrong root.** Every section path is now
  written `<base>/sections/<file>`, against the skill's base directory as Claude
  Code prints it. `check_skills.py` fails on any repo-only path, which is the
  class that CI passed for months because it ran from the repository root.
- **Copy installs missed section-only edits.** `setup` compared only `SKILL.md`.
  It now compares the whole skill directory, and both setup scripts verify
  after installing that every indexed section exists. `/restack-upgrade check`
  runs the same verification against the live install.

### Added — supersession discipline

- **Decision-point accounting** (`/restack-adr update`). Before an amend,
  supersede or deprecate, every decision point of the old ADR is marked *holds
  / replaced / withdrawn*. Each withdrawn point answers "what failure did this
  prevent, and what prevents it now?" An answer of "nothing" is a STOP and a
  brief. In the field batch, three supersessions each removed a protection
  nobody had written down.
- **Knock-on changes**, a mandatory ADR field: every descriptive document the
  decision invalidates, updated, bannered or ticketed in the same step.
  Repeated in `/restack-stressor residues` and checked at the iterate gate and
  in `/restack-journey review`. In the field, 84% of consistency findings came
  from one pivot whose ADRs touched none of the four pre-pivot documents.
- **Amendments go at the top, as a banner**, with contradicted passages struck
  inline (`/restack-adr`, `/restack-solution-doc update`). Consistency check 7
  reports footnote amendments and stale amendments as their own class (`AM-n`).
- **Class S, lost on supersession**, in the design-review matrix cross-check,
  separate from C (missed by the analysis).

### Added — analysis gaps

- **Unwalked human operators block the route to documentation.** The iterate
  gate cannot pass while an on-call, approver or break-glass holder is
  unwalked, unless the architect explicitly accepts it. `/restack-stressor walk`
  gains a lever template: *actor pulls lever → system effect → confirming
  signal*.
- **Lever stressors are mandatory.** For every safety lever, generation must
  cover pulled-with-no-effect and effect-but-unconfirmable, plus the wrong-actor
  question.
- **Stale matrices are marked.** A decision that adds or removes an actor after
  scoring marks the matrix `scored pre-D<n>`, and the HLD copies that qualifier
  next to any impact figure.
- **Platform IaC as a standard discovery probe**, including shared modules,
  plus an *inherited platform defaults* anti-pattern. A hosted actor's profile
  carries a sourced *Hosting, network and identity* block.
- **Implementation status and design boundary** are asked up front, persisted
  in `journey-state.md`, and read by every tier-3 skill before probing.

### Added — protocol and format

- Brief numbers continue the journey's decisions log instead of restarting at
  `D1` in every command.
- A rejected or interrupted brief is not an answer. It is re-issued unchanged
  on resumption, and no decision is logged without a recorded answer.
- **Derived details** in ADRs (*detail · derived from · overturnable*). A
  one-way-door or Low-confidence detail becomes a brief, and
  `/restack-journey review` lists the unconfirmed ones.
- Canonical journey files: one assumptions-register schema with a fixed status
  vocabulary and appended status lines; a decisions-log template; journey
  history as an append-only list at the end of the file.
- A tier-1 *Paths and shell* fragment: the `<base>` rule, plus Windows-safe
  scripting (scratch files, not heredocs; `PYTHONIOENCODING=utf-8`).
- Traceability promises in ADRs name their artifacts, location and retention.
  Runbook alerts must be defined in an ADR or LLD. Replaced operational
  documents are archived with a banner in the same step.

## [Unreleased]

### Added

- [ADR-014](docs/adr/ADR-014-jev-for-cell-scoring.md) — scoring impact-matrix
  cells with a decision model, **built and withdrawn the same day**. Nothing in
  the skills changed; the ADR is the deliverable.

  The idea was sound enough to build: the matrix is the one genuinely mechanical
  judgement in the method, and it is made by the same model that generates the
  stressors and reads the result. A calibrated probability per cell, with an
  uncertain middle band handed back to the architect, addresses that directly.

  It failed the prediction written into the ADR before the run. Agreement in the
  confident band passed at 94.6%, but 70.6% of cells landed in the escalation
  band against a 20% target — and the two criteria move against each other, so
  no threshold pair satisfies both. Splitting the compound question, which the
  vendor's own documentation prescribes, made separation worse.

  Kept as a record because the reasoning survives the result, and because a
  prediction that is allowed to end a feature is only worth writing if it is
  honoured when it does.

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
