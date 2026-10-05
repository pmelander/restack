# Changelog

All notable changes to ReStack. Versions follow the skill set as a whole;
individual skills carry their own `version:` in frontmatter.

## [Unreleased]

A read-only journey view as a Claude Code mod
([ADR-029](docs/adr/ADR-029-a-journey-view-as-a-mod.md)): the band, installed
on request with `./setup --mods`.

### Added

- **`setup --mods` / `--no-mods`** (`-Mods` / `-NoMods`): installs the mods
  beside the skills, where Claude Code loads each as `<name>@skills-dir`. The
  choice is recorded in `install.json` (`"mods"`), so a plain re-run and
  `/restack-upgrade` keep it. A broken mod, a mod named like a skill, and the
  two flags together are refused. The `.claude-plugin/types/` Claude Code
  writes on a development load is never installed or compared.

- **`mods/restack-view`**, ReStack's first TypeScript. It draws one line above
  the prompt: terrain, phase, confidence, the next command, and the counts of
  open asks, assumptions and decisions. It is read from the canonical journey
  files and never written back. `/restack-view` prints the line;
  `/restack-view band [on|off]` hides or shows it. It shares the band with
  other mods and survives `/clear`.
- **`scripts/check_mods.py`**: a mod's calls and hooks, as
  `claude plugin validate` reports them, held to the view's allowlist.
- **A `mods` CI job**: installs the Claude Code CLI, runs the check and
  `claude plugin test`.
- **`tests/fixtures/journey/band/`**: a full canonical journey, pinned
  canonical by `journey.py check`, rendered into the mod's tests by
  `gen_skills.py`.

### Changed

- **The band reads a lived-in journey**, not only the template: a terrain
  sentence shows its terms (`Greenfield/Brownfield`), other fields their first
  clause, and the next move comes from the newest Current Position subsection
  only. Found on the first live run.
- **`local_copies.py`** no longer counts an installed mod as a skill, so a
  project's own folder sharing the mod's short name is never reported.
- **`/restack-upgrade`** 2.0.1: the install check skips a mod (no `SKILL.md`),
  and says upgrades keep the mods choice.

### Decided

- ADR-029: mods are views; ADR-010 is amended to allow TypeScript for them;
  packaging ReStack as a marketplace plugin is parked.

## [2.16.0] — 2026-10-05

Adopted residuals can be challenged by removal
([ADR-028](docs/adr/ADR-028-residuals-challenged-by-removal.md)). The loop
only ever added: on the reference engagement, like-for-like impact fell
195 → 133 while the total rose to 244, and every gate offered ways to keep
and extend. The architect spotted a hub in the generated system overview,
a storage account the matrix split into five columns that together held 35
cells on 24 rows, more than any single actor. A paper pilot then showed how
far a by-hand count goes wrong: 35 cells looked saved and 6 actually went.

### Added

- **`/restack-stressor ablate [target]`** (stressor 2.4.0), with the method
  in the new section `ablation.md`:
  - with no target, it finds candidates: substrate groups the architect
    declares, the topology of the HLD's diagram source, and how deep
    residuals defend residuals;
  - with one, it scores scenarios over the target and what was built on it.
    Each needs a named substitute, checked against the decisions that
    rejected it; rows classified vanish / inherit / morph, confirmed by the
    architect; circular credit added. The net is a range, by lens and on the
    aspiration's column;
  - it ends in an approach gate, and never edits a matrix or an ADR.
- **`matrix.py rollup`**: columns summed by declared substrate, each group
  ranked by distinct rows against the most-hit actor outside it, and the
  rows that cross a group.
- **`matrix.py ablate`**: a removal scored from the architect's row classes.
  The re-open set is the cells only the removed residuals cleared; overlap,
  circular credit, retired actors and existing 1s are named, not counted.
  Exit 1 while anything is missing.
- **The ablation report template**, `templates/ablation-report-template.md`,
  vendored into the stressor skill.
- **A `Challenged by removal` field** in the ADR format (adr 2.2.0): absent
  until a challenge, one dated entry per kept outcome. `update` records it
  without an amendment.
- 11 test cases for `rollup` and `ablate`, against a third iteration of the
  synthetic engagement.

### Changed

- **The iterate gate checks whether the design should shrink** (journey
  2.5.0, step 9). Four triggers add "challenge first" to the brief: the total
  rose while like-for-like fell; residuals three generations deep; a declared
  substrate outranks the most-hit actor; the design is about to become the
  target. The row "residuals adding complexity faster than they remove
  impact" now leans **Challenge, then proceed**, not **Proceed**.
- A `residues` gate brief on a residual that defends an earlier one also
  offers removing the defended residual.
- `matrix.py`'s claim parser can keep claims on actor codes a matrix no
  longer has, so a challenge can name them.

## [2.15.0] — 2026-10-04

The architect answers the asks first; only what they defer goes into the
pack ([ADR-027](docs/adr/ADR-027-asks-triaged-with-the-architect-first.md)).
On the first real `asks` run, the architect settled 33 of 43 routed asks in
one sitting. Three decisions and one structural finding came out of the
answers, and a pack-first flow would have surfaced them weeks later.

### Added

- **Triage in `/restack-journey asks`** (journey 2.4.0). Every routed ask is
  put to the architect, one choice question each, with `Defer to
  <recipient>` always the last option. Answers go to the register as they
  come, at Medium confidence. An answer that contradicts a logged decision or
  an ADR becomes a brief in the same run. `--no-triage` skips it for one
  recipient the architect names.
- **`journey.py assume unasked A-n... --why "..."`** cancels a send recorded
  in error. It writes a status line that repeats the status, and `asks`
  counts the row as asked one time fewer, or never. It refuses a row with no
  send to cancel.
- 5 test cases for `unasked`, including sync and trace.

### Changed

- The pack holds only deferred asks, and its summary shows answered and
  deferred counts per recipient. With nothing deferred, no pack is written.
- A send is recorded only after "has any of these sections been sent?",
  asked on its own. "Which sections are going out" no longer records
  anything.
- Routing proposes the architect first for a row whose owner is unclear,
  when the design boundary names the architect's team.
- `assume sync` ignores `unasked` lines as it does `asked` lines.
- The register template, `journey-files.md` and `journey-state.md` document
  the `unasked` line.

## [2.14.0] — 2026-10-03

Asks to people outside the design are routed in the assumptions register and
written out as a send-ready pack
([ADR-026](docs/adr/ADR-026-asks-routed-in-the-register.md)). On the
reference engagement, seven recipients were waiting on asks at the end of
review, and one hand-written document covered three of them. The rest were
spread across a register of about 150 rows.

### Added

- **`/restack-journey asks [recipient]`** (journey 2.3.0) writes
  `docs/journey/asks-<date>.md`, with one section per recipient. Each section
  stands alone and has no method vocabulary outside its `Ref:` line. It
  stops to ask which sections went out, and records only those. It never
  sends anything. The method is in the new section `asks-pack.md`.
- **`journey.py`**:
  - `assume add --ask <recipient>`: writes `Ask <recipient>:` at the start of
    `Validates it`.
  - `assume route A-n <recipient>`: sets or renames the recipient, and
    changes nothing else in the row.
  - `assume asked A-n... --to <recipient>`: records a send as a status line
    that repeats the row's status. It cannot change a status, and records
    nothing if any row is wrong.
  - `asks [recipient]`: read-only. The open asks by recipient, with
    last-asked dates, unrouted rows that read like asks, and recipient names
    that may be the same.
- 21 test cases against `tests/fixtures/journey/asks/`.

### Changed

- `assume sync` ignores `asked` lines, so a row's date stays the date its
  status last changed.
- Handoff asks are registered with `--ask` when they are made:
  `journey-state.md` and `journey-files.md` (preamble),
  `/restack-discover` 2.2.1, `/restack-stressor` 2.3.1, and
  `/restack-journey start`. `/restack-journey where` names asks never sent
  that hold up the next gate.
- The register template documents the prefix and the `asked` status line.

## [2.13.0] — 2026-10-03

The impact matrix's arithmetic is done by a script; scoring stays with the
architect ([ADR-025](docs/adr/ADR-025-matrix-arithmetic-by-script.md)). On the
reference engagement the model checked 67 claimed cells with one-off scripts
that vanished with the session.

### Added

- **`matrix.py`** in `/restack-stressor` (standard library, no network):
  - `totals`: row, column and grand totals checked, or filled with `--write`
    (which changes no score and refuses a non-binary matrix); cells that are
    not 0, 1 or `?`; the unknown cells; and the four reading checks as
    numbers: concentration, identical-actor-set clusters, flatness, zero
    columns.
  - `compare`: the per-actor before/after table, the total against the shared
    stressor set (split into actors in both, removed and added) and against
    the expanded set, cells cleared, cells newly 1, and cells that left with a
    removed actor.
  - `claims`: each residual's `**Clears N cells:**` list checked: 1 before,
    0 after (or its actor removed), the stated count, overlaps, the distinct
    total, and cells cleared that no residual claims.
- `tests/test_matrix.py` (14 cases) against `tests/fixtures/matrix/`.

### Changed

- `/restack-stressor` `analyze`, `vulnerabilities`, `residues` and `iterate`
  use it; `residual-identification.md` fixes the checkable cell-list format
  the field already used.
- **trace 1.0.3: a bare `?` counts as 1**, as the method says (unknown
  exposure is exposure). It counted 0 before.

### Notes

- Run read-only on the reference engagement's iterations 6 → 7: 195 → 133 on
  the shared stressor set, 244 on the expanded one; 66 cells cleared on shared
  actors plus one claimed cell whose actor was removed, which are exactly the
  67 the residuals claimed, with none cleared unclaimed.

## [2.12.0] — 2026-10-03

Old ReStack skill copies in a project or the profile are reported, and
retired by moving them aside
([ADR-024](docs/adr/ADR-024-retire-old-skill-copies.md)). The reference
engagement still carried 14 pre-prefix copies in `.claude/skills/`, loading
beside the installed `restack-*` skills: a run under 2.11 closed with the
reflection prompts 2.10 removed.

### Added

- **`local_copies.py`** in `/restack-upgrade`: finds old copies by name
  **and** content (the installed skill's title, or the residuality
  vocabulary), in `.claude/skills/` and `.claude/commands/` only. A project's
  own skill that shares a name is left alone. `--profile` does the same for
  `~/.claude/skills`, never counting the `restack-*` install.
- **A session-open line** through the update check, for the project and for
  the profile, each at most once a day, local (no install record or network
  needed), under the existing opt-out. `/restack-upgrade check` lists them.
- **`/restack-upgrade retire-local [--profile]`**: list, dry run, a brief,
  then a move to `.claude/skills-retired-<date>/` with a README on how to undo.
  Nothing is deleted.
- `tests/test_local_copies.py` (14 cases).

### Changed

- `tests/test_update_check.py` runs `check` with a scratch `HOME`,
  `USERPROFILE` and working directory, since the check now reads both
  `.claude` folders.
- `docs/INSTALLATION.md`: upgrading from an unprefixed install points at
  `retire-local --profile`.

## [2.11.1] — 2026-10-03

Fixes from the first real migration: the reference engagement's journey
files, migrated and then worked through 43 judgement items with the
architect. Three steps had to be done by hand or went wrong; each now has a
command or a guard, and tests.

### Fixed

- **Git Bash rewrote `--command "/restack-journey ..."` into a Windows path**
  (`C:/Program Files/Git/restack-journey ...`). The snippet in
  `journey-files.md` now turns MSYS argument conversion off and translates the
  script's own path with `cygpath`, which the first attempt at the fix broke
  (a test caught it). `history add` also repairs a rewritten command, and
  accepts one without its slash.

### Added

- **`assume sync A-<n> | --all`**: a row takes the status and date of its
  last status line, with no new line. Aligning a row to a status already on
  record used to need `assume status` and a fresh `--why`, and in the field run
  that invited a reason the record did not contain.
- **`decision note D<n> --actors ...`**: records whether an answered decision
  changed the actor set when it never said, marked `(recorded <date>; not
  stated when decided)`. Refuses if the entry already says, or is still open.
  Eighteen field decisions needed this, and the lines were appended by hand.
- `journey-files.md`: **a `--why` comes from the record**, never a plausible
  reason; if the record holds none, ask.
- `tests/test_journey.py`: 44 cases (was 35), including the snippet run in
  Git Bash with a slash command.

## [2.11.0] — 2026-10-03

The journey files are written by a helper, and old shapes migrate without
material change ([ADR-023](docs/adr/ADR-023-journey-files-written-by-a-helper.md)).
This is the writing half of ROADMAP item 3; trace (2.9.0) was the reading half.

### Added

- **`journey.py`** in `/restack-journey` (standard library, no network):
  `assume add | status`, `decision next | open | answer`, `history add`,
  `check` and `migrate`. It takes the next `A-<n>` and `D<n>`, puts each row
  and entry in its canonical place, keeps a register row and its status lines
  in step, writes atomically, and keeps a file's line endings.
- **A brief takes its number when it is issued.** `decision open` writes the
  entry with `Answer: (open)`; `decision answer` fills it once, and refuses to
  answer twice. An open entry is the record of an interrupted brief.
- **`migrate`** converts old-shape journey files: register rows from every
  table into one, notes kept verbatim above it; date-first decision headings;
  a history table into list lines at the end. Structure only, never a status,
  a decision or a date. It refuses to write if any word, row or decision
  reference would be lost, reports what needs judgement, is a dry run unless
  `--write`, and backs up outside git.
- **`/restack-journey migrate`**: dry run, report, a brief, then the write and
  the judgement items one at a time.
- **`journey-files.md`**, a tier-2 preamble fragment, so every skill that
  writes decisions or assumptions uses the helper.
- `tests/test_journey.py` (35 cases) against `tests/fixtures/journey/`, a
  synthetic canonical journey and a legacy one.
- **Branding** in `assets/`: lockups for light and dark backgrounds, mark,
  icon, avatar and favicon. The README opens with the lockup, switching on
  the reader's colour scheme.

### Changed

- `decision-brief.md`: numbers come from `decision open`. `journey-state.md`:
  a refused file is appended by hand and offered `migrate`.
- Decisions-log template: open entries and unnumbered event entries are part
  of the contract.
- **trace 1.0.2** reads a migrated register: notes in its "Earlier notes"
  section count as later than the rows, so the status-drift heuristic keeps
  working. Both scripts now write UTF-8 to stderr as well as stdout; a
  refusal quoting `·` failed on a cp1252 console.

### Notes

- Run read-only on a copy of the 2.4.0 reference engagement's journey files:
  123 rows from 18 tables and 12 stray groups, 18 decision headings and 151
  history rows converted, every word kept. trace's structural `REG` items
  disappeared; the content items (A-40, A-88, the falsified-but-Open rows)
  remained for the architect.

## [2.10.0] — 2026-10-03

ReStack is a working toolkit, not a training pack
([ADR-022](docs/adr/ADR-022-working-toolkit-not-training-pack.md)). The
skills run the method and keep the record; the architect makes the calls. The
premise that the pack builds capability in its users, measured by how rarely
it is needed, was never the intention and is withdrawn.

### Changed

- **Every skill states what it produces and when it is done.** "Capability
  being built" and "Residuality goal" are replaced in fifteen skills by **What
  it produces** (the artifacts, and where) and **Done when** (a checkable bar).
- **No reflection prompts.** Removed from the voice fragment, from the chain
  rules, from fifteen skills, and from two command steps. Prompts that carried
  method became Done-when checks on the output.
- **The voice rule is "The architect owns the judgement"**, justified by
  accountability rather than teaching. Gates, decision briefs and stop rules
  are unchanged.
- **`/restack-design-review self-check` is an author's review**: the architect
  reviews, the skill challenges their answers and then adds its own findings,
  marked as its own.
- `/restack-adr` still asks one question at a time, now because each answer
  changes the next question. Its descriptions and `/restack-tech-stack`'s no
  longer promise to build habits or thinking.
- CLAUDE.md (template structure, design principle, skill-development rules),
  README, ROADMAP (the new-skill test, and "a training pack" under
  Deliberately not doing), RESIDUALITY.md, QUICKREF and PROJECT_SUMMARY.
- ADR-001, ADR-002, ADR-005 and ADR-020 are amended with banners and inline
  marks; ADR-022 accounts for each withdrawn point. The May 2026 phase and
  integration write-ups are bannered as historical record.

### Added

- ROADMAP item 9: restyle an existing project to the current style, ADRs
  included, with a guard that proves nothing material changed.

## [2.9.1] — 2026-10-03

The first field run of `/restack-trace`, on the 2.4.0 reference engagement,
confirmed most of the items it opened and named four kinds of noise: three
false-positive classes and one miss. All are fixed in `trace.py`, each with a
fixture case and a decoy that must still be reported. `tests/test_trace.py`
goes from 35 to 41 cases.

### Fixed

- **A TBD handed to a registered assumption is a tracked gap.** A Knock-on
  outcome "struck; … TBD (A-n)" was read as pending (`KO`), and every
  "TBD (A-n)" counted as a placeholder (`PH`). Both now skip a TBD, TODO or
  pending that names an assumption in the register. One that names an
  unregistered assumption is still reported.
- **Banners in other words cover their amendments.** Blockquote banners headed
  "UPDATED", "Current state", "Revised" or "Changed" were not recognised, so
  the amendments they covered were reported as footnotes (`AM`). A
  `**Updated:** <date>` metadata line is still not a banner.
- **A renamed export is paired with its source.** `HLD-high-level-design.pdf`
  was never compared with `HLD.md` (`PDF`). A PDF whose name starts with one
  Markdown file's name plus `-` is now paired with it, marked `[heuristic]`.

The shared section's `PH` and `PDF` rows say so.

### Added

- **The report header names the trace version** (`trace 1.0.1: docs ...`),
  read from the skill's frontmatter. The second field run dropped from 65 to
  56 items over unchanged documents, and the agent had to compare file times
  to establish that the script, not the documents, had changed. The shared
  section now says to compare runs only at the same version.

## [2.9.0] — 2026-10-02

A script finds where the documents drift, and hands the reviewer a worklist
([ADR-021](docs/adr/ADR-021-trace-checks-as-a-worklist.md)). 2.4.0 wrote the
field feedback down as rules, and most of their acceptance checks are
mechanical: does this ID exist, did this file change after that date, do these
cells add up. Until now the model ran them by re-reading every document.

### Added

- **`/restack-trace`**, a tier-1 utility skill, and `scripts/trace.py`
  (standard library, read-only, no network). `scan` reports ten classes:
  - `REF`: an ADR, decision or assumption cited with no definition;
  - `REG`: register drift (a row a later status line or update contradicts,
    statuses outside the vocabulary, several tables, rows outside any table);
  - `KO`: Knock-on rows recorded as pending, documents "updated" that have not
    changed since the ADR's date, "bannered" with no banner, names that
    resolve to nothing, and ADRs missing the field after it became routine;
  - `AM`: amendments after the body that no banner at the top covers;
  - `SUP`: descriptive documents citing a superseded ADR unmarked;
  - `BASE`: matrices scored before a decision that changed the actor set, and
    documents quoting them without `scored pre-D<n>`;
  - `MX`: row and column totals that do not match their cells, and cells
    scored above 1;
  - `ALERT`, `PH`, `PDF`: runbook-only alerts, placeholders, stale exports.

  `terms` lists passages that still use a replaced mechanism's terms unmarked.
  `refs` lists every citation of an ID, marked or unmarked.
- **`scripts/shared/trace.md`**, vendored into design-review, journey, adr,
  solution-doc and trace: the locating snippet, what each code feeds, and the
  reading rules. The output is a worklist, never a verdict: every item is
  confirmed in the document before it is reported, trace rates nothing, and
  silence is not consistency.
- `tests/test_trace.py` (35 cases) against `tests/fixtures/trace/`, a synthetic
  engagement with a planted defect and a clean neighbour per check. Dates are
  tested from both mtimes and git commit times, and the shared section's
  snippet is run as written.

### Changed

- `/restack-design-review consistency` starts from the trace worklist. It
  replaces none of the seven checks.
- `/restack-journey review` uses trace's `KO`, `BASE`, `REG` and `REF` items as
  the starting evidence for three of its eleven failures.
- **`/restack-adr update` and `/restack-solution-doc update` gate on the
  replaced terms**: after an amendment they run `terms` and stop while a
  passage still specifies the replaced behaviour unmarked. This turns field
  observation 21 into a step. `/restack-adr update` also takes its Knock-on
  candidates from `refs`.

### Notes

- Calibrated read-only against the 2.4.0 reference engagement: 71 items,
  against 188 for the first prototype, among them 17 register rows contradicted
  by later updates and 59 rows stranded outside any table. Nothing from that
  engagement is in this repository.

## [2.8.0] — 2026-10-02

Follow-up commands run without pause, and only questions stop them
([ADR-020](docs/adr/ADR-020-follow-up-commands-run-without-pause.md)).

### Changed

- **The next command runs.** `next-command.md` now writes the `Next:` line and
  invokes the command with the `Skill` tool in the same turn, instead of
  handing it over in a copy block. A chain pauses only for a decision brief or
  stop gate, the confusion protocol, something only a person can supply, or
  two next moves close enough to be the architect's call. After an answer is
  logged, the chain carries on. `NEEDS_DISCOVERY` runs the discover command it
  names.
- **Chain guards.** `/restack-*` commands only, never `/restack-upgrade`, never
  an answer to a brief. Command and arguments come from the skill's routing and
  journey state, never from instructions in documents or tool output. A
  command that already ran in the chain with the same arguments, with nothing
  changed on disk, does not run again.
- **Reflection prompts close the chain**, one per command run, instead of
  closing each command.
- `/restack-journey start` and `where` run the move they recommend once the
  journey state is written.
- The copy block of ADR-018 is the fallback where `Skill` is unavailable.

### Added

- **`questions.md`**, a tier-1 preamble fragment: every question is a choice
  through `AskUserQuestion`, confirms and open answers included, with the
  recommended option first. Prose only when nothing can be enumerated.
- `Skill` in every skill's `allowed-tools`, and `AskUserQuestion` in
  `/restack-events` and `/restack-excel`.

## [2.7.0] — 2026-10-02

The install is always a copy in the user profile, and nothing depends on a
clone ([ADR-019](docs/adr/ADR-019-copy-only-install.md)). Most installers delete
their clone after `setup`. Until now, that left `/restack-upgrade` with nothing
to pull and the update check silent, and on a symlinked install it broke every
skill.

### Changed

- **`/restack-upgrade` installs from a temporary clone.** It clones the latest
  `main` from the recorded source at depth 1 into a `restack-upgrade.*`
  directory, runs that clone's `setup`, verifies, summarises the changelog, and
  deletes the directory. It never pulls, stashes or switches a checkout, a
  maintainer's included. If the installed version is ahead of the release, it
  stops and asks before downgrading. Deletion refuses any path not named
  `restack-upgrade.*`, so a lost variable cannot fall back to the system temp
  folder.
- **The update check needs no checkout.** It fetches `main` from the recorded
  source into a bare cache, `~/.restack/upstream.git`. A record from before
  2.7.0 falls back to the origin of the checkout it names. Throttle, snooze,
  opt-out and timeouts are unchanged.
- **`setup` records `source`**: the checkout's origin, or the project URL for a
  download.
- **Developing ReStack** is `python scripts/gen_skills.py && ./setup`. Sessions
  load what was last installed, so another session's work in progress no
  longer leaks into them.
- INSTALL.md and the installation guide: clone anywhere, run setup, delete the
  clone if you like. Agents install from a `restack-install.*` temporary clone
  and delete it afterwards.

### Removed

- **`setup --symlink`, `--target` and `CLAUDE_SKILLS_DIR`** (and `-Symlink` and
  `-Target` in `setup.ps1`). The two options are refused with a message, and
  the variable is ignored with a note. `--copy` is still accepted and does
  nothing. Tests that need a scratch install point `HOME` and `USERPROFILE` at
  one.
- The symlink-specific update notice, which told a symlinked install to
  `git pull`.

### Fixed

- **Removing a link could delete through it.** `setup`'s "removed upstream" loop
  ran `rm -rf` on a trailing-slash glob. A test confirmed that Git Bash deleted
  the contents of a junction's target that way. Links are now removed as links
  (`rm -f`; `Directory.Delete(path, $false)` in `setup.ps1`), and a symlinked
  install from before 2.7.0 is converted to copies with its checkout untouched.
  Both cases are covered by tests on both installers.
- The uninstall instructions used `rm -rf ~/.claude/skills/restack-*/`, which
  has the same trailing-slash hazard on a symlinked install.
- `docs/INSTALLATION.md` had `$HOME\restack` mangled into `$HOME` plus a line
  reading `estack`, and an uninstall section that removed only four skills.

## [2.6.0] — 2026-10-02

### Added

- **The next command in a copyable block**
  ([ADR-018](docs/adr/ADR-018-next-command-as-a-copy-block.md)). A tier-1
  preamble fragment, `next-command.md`, composed into all sixteen skills. A
  command that leads somewhere names it after the status line: `Next:` with one
  line on why, then the command alone in a fenced block tagged `text`, which the
  desktop app gives a Copy button. An `Alternative:` line follows when the
  skill weighed one. There is no block while a decision brief is unanswered,
  and never an answer to a brief inside it.
- The block carries the full command, arguments included. ADR-017 kept
  arguments off its button because `sendPrompt` spoke for the architect. A
  copied block is pasted and sent by the architect, so that reasoning does not
  apply. It is tagged `text` because a shell tag gets a Run button, and a slash
  command does not belong in a shell.

This brings back the `Next:` line that 2.5.2 withdrew with the button, without
the button. ADR-017 carries an amendment banner pointing here.

## [2.5.3] — 2026-10-02

### Fixed

- **`setup` wrote invalid JSON for a path with a backslash or double quote.**
  It interpolated `version`, `repo`, `skills_dir` and `method` raw into
  `~/.restack/install.json`, so `CLAUDE_SKILLS_DIR='C:\Users\me\skills'` under
  Git Bash recorded `"C:\Users\..."`, an invalid `\U` escape. The update check
  (ADR-016) then read no record at all and stayed silent; the sed one-liners
  in `/restack-upgrade` still worked, which hid it. Every value now goes
  through a `json_str` helper that escapes `\` and `"`, which is what
  `setup.ps1` already got from `ConvertTo-Json`. A record written wrongly
  before this release is rewritten by the next `./setup` with no `--target`:
  `/restack-upgrade` runs it for a copy install, and a symlinked one needs
  `./setup --symlink` from a shell that can create symlinks. Until then
  `/restack-upgrade check` reports the record as `cannot be read`, and the
  update notice cannot announce this release to that install.

### Added

- `tests/test_setup.py`: an eighth case, for both installers, that sets
  `CLAUDE_SKILLS_DIR` to a backslash path on Windows and checks the record
  parses and names that directory. Elsewhere the directory name carries a `\`
  and a `"`, so CI on Linux covers the escaping too.

## [2.5.2] — 2026-10-02

### Removed

- **Next step as a button, withdrawn the day it shipped**
  ([ADR-017](docs/adr/ADR-017-next-step-as-a-button.md)). In the desktop app's
  Code tab, a button often needed several clicks before its command appeared in
  the message box. Even then it only filled the box, and the architect still
  pressed send. The cause sits in the host, where ReStack can neither test nor
  fix it, and a button less reliable than the text line above it adds nothing.
- **The `Next:` / `Alternative:` line format and the bare-command rule went
  with it.** Both existed to support the button. The tier-1 preamble is back to
  voice, paths and shell, and completion status, and the generated skills match
  2.4.0 apart from the changes 2.5.0 and 2.5.1 made to them. Skills name their
  next move as they did before.

Kept: ADR-017, marked withdrawn. It records what the click test established
(the box is filled rather than sent, a leading `/` is dropped, clicks are
unreliable), what it did not (why), and what any second attempt would need. The
update check's rule that `/restack-upgrade` is never the session's next move is
reworded so it no longer names the removed format.

## [2.5.1] — 2026-10-02

### Fixed

- **`setup --target` overwrote the record of the real install.** Both `setup`
  and `setup.ps1` wrote `~/.restack/install.json` on every run, so installing
  into a scratch directory replaced the record of the install Claude Code
  loads. `/restack-upgrade` then read the scratch `skills_dir` and `method`,
  and step 4b verified the scratch tree. Now only an install into the default
  skills directory is recorded: `$CLAUDE_SKILLS_DIR`, else `~/.claude/skills`,
  however `--target` spells it. A skipped record prints a `Note:` that names
  `CLAUDE_SKILLS_DIR` as the way to make a non-default install permanent.
  ADR-016's guard in the update check stays, for records written before
  this release ([ADR-011](docs/adr/ADR-011-setup-script-and-upgrade-skill.md),
  Notes).
- **`./setup --dry-run` exited 1** whenever `--symlink` was not given, because
  its last command was `[ -n "$x" ] && printf`. `setup.ps1 -DryRun` exited 0.
- **The tests could run in WSL.** On Windows, `bash` on PATH is often the WSL
  launcher, which ignores the scratch `HOME`, so `test_update_check.py` would
  have run its snippet against the WSL user's real home. `tests/shells.py`
  refuses launchers and finds Git for Windows' own `sh` and `bash`.

### Added

- **`tests/test_setup.py`**: the same seven cases against both installers,
  with `HOME` and `USERPROFILE` in a scratch directory. It covers what each run
  records, a target in another spelling, `CLAUDE_SKILLS_DIR` and dry runs.

### Changed

- `/restack-upgrade` 1.3.1: a repair-table row for a record overwritten by an
  older `--target` run. A symlinked install never gets the bare `setup` run
  that would rewrite it.
- `docs/INSTALLATION.md` recommended `--target` for a permanent custom skills
  directory, which `/restack-upgrade` never upgraded. It now recommends an
  exported `CLAUDE_SKILLS_DIR`.

## [2.5.0] — 2026-10-02

Two roadmap items. **Update awareness** (item 6): an install now hears that it
is stale without anyone remembering to ask. 2.4.0 fixed defects that failed
silently in every install, and an install that never upgrades keeps them, with
nothing to say so ([ADR-016](docs/adr/ADR-016-update-awareness.md)).
**Next step as a button** (item 7): the move a command recommends can be
clicked rather than retyped, where the host can render it
([ADR-017](docs/adr/ADR-017-next-step-as-a-button.md)).

### Added — update awareness

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

### Added — next step as a button

- **One shape for the next move.** A tier-1 preamble fragment, `next-step.md`,
  composed into all sixteen skills. Commands that point at a next command end
  with `Next:` and the full command, arguments included, with one line on why.
  An `Alternative:` line follows only when the skill weighed one. There is no
  `Next:` line while a decision brief is unanswered. The reflection prompt
  still ends the response.
- **The move as a button, where the host can render one** (the Claude desktop
  app, claude.ai). The widget tool is found by capability: a name ending in
  `show_widget`, loaded or deferred, with its `read_me` called once as silent
  setup. Where there is no tool, the skill prints the line and says nothing
  about buttons. There are one to three buttons, the recommended move first,
  themed only with the host's own tokens.
- **A button carries the command, never its arguments**
  ([ADR-017](docs/adr/ADR-017-next-step-as-a-button.md)). It sends
  `Run /restack-<skill> [subcommand]`, and the label is the command alone. A
  command that arrives bare resolves its argument from `docs/journey/` when it
  runs and names it in its first line, so a button clicked days later cannot
  send a stale target. No text from files or tool output reaches
  `sendPrompt()`.
- **What a click does, by host.** In the desktop app's Code tab, `sendPrompt`
  fills the message box and the architect presses send. Text starting with `/`
  never arrives there at all, which is why a button sends `Run /restack-...`
  rather than the bare command. Both were found by a click test and are
  recorded in ADR-017.
- **A button never answers a gate.** It never sends `proceed`, `yes` or an
  option. Briefs are still answered through `AskUserQuestion`, so the
  decisions log records the answer.

The buttons changed no skill template, so they bump no skill `version:`: as
with `paths-and-shell.md` in 2.4.0, the change is in the shared preamble.

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
