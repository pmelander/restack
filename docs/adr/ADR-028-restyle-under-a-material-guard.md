# ADR-028: Old-Style Documents Are Restyled by a Dedicated Skill, Under a Material Guard

**Status:** Accepted

**Date:** 2026-10-04

**Deciders:** ReStack maintainers

**Technical Story:** [ROADMAP](../../ROADMAP.md) item 9, "Restyle an existing
project", the half [ADR-023](ADR-023-journey-files-written-by-a-helper.md) left
open: ADRs and descriptive documents

**Implementation Status:** implemented

**Implemented Date:** 2026-10-04

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-04

## Context

[ADR-022](ADR-022-working-toolkit-not-training-pack.md) withdrew the
capability-building premise and, in its point 8, left existing project
documents alone: "Projects written under the old style keep their text." The
reference brownfield engagement has 61 ADRs and a full document set in that
style: reflection sections, capability-transfer framing, metadata as sections,
older heading names. Read next to anything written since, the set is
inconsistent, and the framing reads as if the project were an exercise.

[ADR-023](ADR-023-journey-files-written-by-a-helper.md) restructured the
journey files with the guard "every word of the old file survives". That guard
is wrong here, because restyling means rewording. And `/restack-adr` forbids
exactly this kind of edit: "never quietly rewrite a decision". A restyle that
turns "must" into "should", 72 hours into 48, or loses a rejected alternative
in the tidy-up records a decision nobody made, and it reads as though it always
said so.

So restyle needs a different guard: one that lets the words change and holds
what a reader acts on fixed.

## Decision

1. **A new utility skill, `/restack-restyle`** (tier 1, the 18th skill),
   owns restyling for ADRs and descriptive documents: `survey`, restyle named
   documents, and `check` (the guard alone). The architect chose one skill
   over restyle commands inside `/restack-adr` and `/restack-solution-doc`.
2. **`restyle.py` is the guard**, shipped in the skill (standard library, no
   network), with three commands: `survey`, `compare OLD NEW`,
   `apply OLD NEW`. It is not optional: without Python or the script,
   restyle writes nothing. Unlike trace, there is no by-hand fallback, because
   the comparison is what makes the rewrite safe.
3. **What is compared exactly, and refuses the write on any difference:**
   metadata fields and values, IDs, dates, figures, code (fenced and inline),
   link targets, table rows, the alternatives considered, struck passages and
   blockquote banners, earlier editorial notes, and any section that
   disappeared together with the words only it used.
4. **What is listed for the architect, and holds the write until
   `--confirmed`:** a changed title, a change in the count of a normative word
   (must, shall, should, may, never, always, only, not, no, ...) with the OLD
   and NEW sentences, names and acronyms lost or added, long words lost, an ID
   cited a different number of times, a section renamed or merged, and a body
   that shrank by more than 30%. The architect chose listing over refusing for
   normative words: contractions and harmless rephrasing would trip a
   refusal constantly, and a guard that cries wolf gets bypassed.
5. **Gaps are never filled.** A missing Reversibility, Review date or
   Knock-on changes is reported for `/restack-adr update`. Adding one, even as
   "not recorded", is refused: the field would claim something about the
   decision.
6. **Sections go only when the architect names them** (`--drop "<heading>"`),
   and the editorial note names every one. A section gone without `--drop` is
   refused when its own words are gone.
7. **`apply` writes the editorial note**, not the draft: one line under
   `## Editorial notes` at the end of the document, with the date, "restyled,
   wording only", what was reshaped, what was dropped, and the script version.
   A draft that writes its own note is refused. Outside a clean git work tree
   `apply` keeps a backup.
8. **Scratch lives in `.restyle/` folders** next to each document: drafts and
   backups. trace and survey ignore dot folders, so a backup can never be read
   as a second ADR with the same number.
9. **Out of scope:** the journey files (`journey.py migrate`), records
   (`journey/`, `reviews/`, `discovery/`, `stressor-analysis/`, `archive/`),
   and retired ADRs unless named.

## Consequences

### Positive

- An old-style project can be brought to the current style document by
  document, with a written proof per document that nothing a reader acts on
  moved, and a note that says so.
- The boundary between restyle and decision is mechanical: a refusal that the
  document genuinely needs is, by definition, an `/restack-adr update`.
- Survey doubles as an inventory of gaps and footnote amendments across an old
  ADR set, each routed to the skill that owns it.

### Negative

- **The guard compares tokens, not meaning.** A reworded sentence that keeps
  every ID, figure and normative word can still say something different
  ("retries are capped" → "retries are limited" passes). The confirm items and
  the architect's reading of the diff are the rest of the control, and the
  skill says so rather than implying exit 0 means "same meaning".
- Tables are compared cell by cell, so a badly worded table cannot be
  restyled at all, and a Knock-on list written as bullets cannot become a
  table. Both stay as they are.
- Confirm items are frequent: almost every real restyle loses some words. On
  61 ADRs that is many questions. They are asked per document, but a tired
  architect can still accept them unread.
- One more skill, and ADR wording rules now live in `/restack-adr` and in
  restyle's house-style section.

### Neutral

- Field names are compared case-insensitively but not by synonym:
  "Decision makers" → "Deciders" is refused. If the reference engagement shows
  that renaming is common, an alias table is a small change.
- The note sits at the end of the document, where trace's amendment check
  does not read it as an amendment.

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| ROADMAP.md item 9 | restyle of ADRs and descriptive documents as future work | updated: done |
| CLAUDE.md, README.md, QUICKREF.md, GETTING_STARTED.md, PROJECT_SUMMARY.md | seventeen skills; the list of skills that ship scripts | updated |
| ADR-022 point 8 | "a restyle mode … is on the ROADMAP" | none: the point stands as history, and this ADR is its follow-up |

## Alternatives considered

### Restyle commands inside `/restack-adr` and `/restack-solution-doc`

- **Pros:** the skill that owns a document is the one that changes it, as
  trace's rule says; no new skill.
- **Cons:** the guard and its method would be shared across two skills, and
  restyle would sit beside the command that says "never quietly rewrite".
- **Why rejected:** the architect chose one skill. Restyle is a bulk pass over
  a whole set, rarely run, with its own guard; it reads more clearly as its
  own tool than as a sixth command in two places.

### The comparison in `trace.py`

- **Pros:** trace already parses most of the material content (ROADMAP item 9
  said so).
- **Cons:** trace is read-only by contract, and its dependency is optional by
  construction. A guard that may be missing is not a guard.
- **Why rejected:** the guard must be present whenever a write happens, so it
  ships with the skill that writes.

### Refuse on normative-word changes too

- **Pros:** the strictest guard; nothing that might flip meaning is written
  without a rerun.
- **Cons:** "isn't" → "is not", or "only after" → "not before", would refuse
  constantly.
- **Why rejected:** the architect chose to have them listed with both
  sentences; a refusal that fires on harmless rewording gets bypassed.

### Insert missing fields as "not recorded"

- **Pros:** every ADR has the current template's shape.
- **Cons:** the value claims something about the decision, and the shape
  hides that the field was never filled.
- **Why rejected:** a gap is reported to the owning skill instead.

## References

- [ADR-021](ADR-021-trace-checks-as-a-worklist.md): trace, read-only and optional
- [ADR-022](ADR-022-working-toolkit-not-training-pack.md): the style being restyled away
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): the journey files' migration, structure only
- `skills/restack-restyle/scripts/restyle.py`, `tests/test_restyle.py`
