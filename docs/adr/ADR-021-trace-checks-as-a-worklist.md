# ADR-021: Mechanical Document Checks as a Script That Produces a Worklist, Owned by a Utility Skill

**Status:** Accepted

**Date:** 2026-10-02

**Deciders:** ReStack maintainers

**Technical Story:** field feedback from a full brownfield journey (2.4.0 items
1–3, 6, 11, 17, 21); [ROADMAP](../../ROADMAP.md) item 3, "Journey state as
tooling rather than prose", the reading half

**Implementation Status:** implemented

**Implemented Date:** 2026-10-02

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-02

## Context

2.4.0 turned a long field engagement's feedback into rules: a mandatory
Knock-on field, banners instead of footnote amendments, a canonical
assumptions register, a `scored pre-D<n>` qualifier, alerts defined outside the
runbook. Each rule has an acceptance check, and most of those checks are
mechanical. Does this ID exist? Did this file change after that date? Does
this row's status match its last status line? Do these cells add up?

Today the model runs them by reading. On the reference engagement that is 61
ADRs, a 139-row register, 34 logged decisions, five matrices and 26
descriptive documents, about 230,000 words, re-read on every review. A model
reading that much from memory misses rows, and the misses are silent. A
read-only probe of the same tree, written in an afternoon, found what the
reviews had not:

- 17 register rows whose table status contradicted a later update in the same
  file (five of them falsified assumptions still marked Open);
- 59 register rows that scripted appends had landed outside any table, where a
  renderer shows them as plain text;
- six Knock-on rows recorded as "pending" or "TBD", against a rule that says
  the same step;
- 13 ADRs with an amendment after the body and no banner at the top;
- six PDFs older than the Markdown they were exported from, one of them a
  deployment guide.

All of these are the bookkeeping half of checks that need judgement. The
judgement half (has the ADR's substance reached the HLD, is this actor in the
component view, is this alert really undefined or just named differently) is
not mechanical, and a script that pretended otherwise would teach architects
to stop reading.

Two constraints shape where such a script can live. Executable code never goes
in `scripts/shared/`, because `setup` installs `skills/restack-*/` and nothing
else ([ADR-010](ADR-010-skills-are-self-contained.md)). And four skills need
it: design-review's consistency pass, journey review, and the update commands
of `/restack-adr` and `/restack-solution-doc`.

## Decision

1. **A script does the mechanical checks; the model does the reading.**
   `trace.py` reads a project's `docs/` and reports ten classes of item: `REF`
   (IDs with no definition), `REG` (register drift), `KO` (Knock-on unfinished),
   `AM` (footnote amendments), `SUP` (superseded ADRs still cited), `BASE`
   (matrices scored before an actor-set change), `MX` (matrix arithmetic and
   non-binary cells), `ALERT` (runbook-only alerts), `PH` (placeholders) and
   `PDF` (stale exports). Two commands serve the update steps: `terms` lists
   passages that still use a replaced mechanism's terms unmarked, and `refs`
   lists every citation of an ID.
2. **The output is a worklist, never a verdict.** Every item is a place to
   look. The consuming skill opens the document, confirms the item, and
   reports it in its own format with its own severity. trace assigns no
   severity, because severity comes from who acts on a stale document, which a
   script cannot know. The report ends by saying so, and the shared section
   says that silence is not consistency.
3. **A new tier-1 utility skill, `/restack-trace`, owns the script**
   (`skills/restack-trace/scripts/trace.py`). It is the architect's direct
   entry point and the install location the consumers resolve. Tier 1 because
   it makes no architectural judgement, like `/restack-excel` and
   `/restack-upgrade`.
4. **Consumers reach it through one shared section**, `scripts/shared/trace.md`,
   vendored into design-review, journey, adr, solution-doc and trace itself
   ([ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md)). It holds
   the locating snippet, the code-to-check map and the reading rules once. The
   dependency is optional by construction, as with the update check
   ([ADR-016](ADR-016-update-awareness.md)): a missing script or Python is
   reported in one line and the checks are done by hand.
5. **One gate, not a scan, enforces anything.** After an amendment,
   `/restack-adr update` and `/restack-solution-doc update` run `terms` with the
   replaced mechanism's terms and **STOP** while an unmarked passage still
   specifies the replaced behaviour. This makes field observation 21 ("refuse to
   finish while an unmarked contradicting passage remains") a step rather than
   a promise. `scan` never stops anything.
6. **Conservative by design.** Patterns the toolkit's formats define are
   reported plainly. Inferred ones (legacy register updates, alert names,
   document names in a Knock-on cell) are marked `[heuristic]`. Noisy classes
   are aggregated into one item. A project that adopted the Knock-on field late
   is checked only from the ADR where it became routine (80% of ADRs from there
   on carry it). Retired ADRs, history directories and `archive/` are excluded
   where citing old decisions is their purpose. On the reference engagement
   this took the first prototype from 188 items to 71, every one worth opening.
7. **Read-only, standard library, no network.** trace never writes to the
   project. Dates come from git commit times in a work tree, with mtimes for
   uncommitted files, and from mtimes otherwise. The report says which, because
   a fresh copy resets every mtime.
8. **Fixtures are synthetic.** `tests/fixtures/trace/` is an invented
   engagement with one planted defect per check and a clean neighbour beside
   each, and `tests/test_trace.py` asserts both. Nothing from a real engagement
   enters this repository: the reference engagement contains a client's
   internal system names, people and work items, and fixtures are committed in
   public.

## Consequences

### Positive

- The acceptance checks 2.4.0 wrote down become runnable, for the items a
  script can see.
- Reviews start from a list instead of a re-read. The reading goes to checks
  2–4, which are about meaning and were the ones getting squeezed.
- Footnote amendments get caught at the step that creates them, not at the
  next review.
- `MX` keeps scoring binary at the source. A cell scored 2 is reported, which
  enforces the severity-scale position in the ROADMAP without arguing it again.

### Negative

- A seventeenth skill to maintain, and a parser that has to follow the
  templates. A template change that moves a field (`**Status:**`, `## Knock-on
  changes`, the register's status lines) can silently blind a check. The
  fixture tests catch it only if the fixture is updated with the template.
- A worklist invites being treated as the review. The shared section's rules
  and the closing line push against that, but cannot prevent it.
- mtimes outside git make the date-based items weak on a copied tree. The
  report says so; it cannot fix it.

### Neutral

- Legacy formats are tolerated rather than migrated. trace reports the shape
  problem (`REG`: several tables, rows outside any table, "Update" headings)
  and leaves migration to the architect.
- `S-` and `R-` identifiers are not traced yet. Their definition formats vary
  more than ADRs, decisions and assumptions, and a check on them would be
  mostly heuristic.

## Alternatives considered

### Keep the checks as prose

- **Pros:** no code; nothing to keep in step with the templates.
- **Cons:** the field evidence is that it does not work past a few dozen
  documents. Every item above survived prose rules and at least one review.
- **Why rejected:** a step that matters should not depend on remembering to
  take it, the argument that justified `setup` over `cp -R`.

### Put the script in `/restack-design-review`

- **Pros:** no new skill; consistency is that skill's job.
- **Cons:** journey, adr and solution-doc would depend on design-review's
  install path. The architect would have no direct command for a check they
  want between reviews.
- **Why rejected:** the owner should be the skill whose whole job is the
  script, as `/restack-upgrade` owns `update_check.py`.

### Let trace fail CI-style and block

- **Pros:** drift could not accumulate.
- **Cons:** most items need a person to decide whether they are drift at all.
  A gate on a heuristic either blocks good work or gets muted.
- **Why rejected:** only `terms` gates, because its question ("does this
  passage still use the replaced term unmarked?") has an answer the architect
  can act on immediately.

## References

- [ADR-010](ADR-010-skills-are-self-contained.md): skills ship their own scripts
- [ADR-012](ADR-012-artifact-consistency-as-a-review-dimension.md): artifact consistency as a review dimension
- [ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md): vendored shared sections
- [ADR-016](ADR-016-update-awareness.md): an optional cross-skill script dependency
- `scripts/shared/trace.md`, `skills/restack-trace/`, `tests/test_trace.py`
