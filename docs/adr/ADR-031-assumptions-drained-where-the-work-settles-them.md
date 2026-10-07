# ADR-031: Assumptions Are Drained Where the Work Settles Them, by Kind, With the Register's Load Visible

**Status:** Proposed

**Date:** 2026-10-07

**Deciders:** ReStack maintainers

**Technical Story:** one brownfield journey's assumptions register,
2026-09-30 to 2026-10-07. Feedback from that engagement, anonymised.

**Implementation Status:** implemented

**Implemented Date:** 2026-10-07

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-07

## Context

The workflow has a well-worn path for **adding** an assumption and none that
**closes** one. On the reference engagement the register reached 172 rows in a
week, and 100 were not closed: 79 Open, 12 Partly resolved and 9 Resolved by
design (test pending). Nobody could say which of the 100 were live exposure and
which had been answered days before. A register in that state no longer says
what the design rests on, and that was its job.

What the engagement showed:

- **Rows go stale where they were written.** 50 of the 100 were last touched on
  the day the iteration that created them ran. Four iterations, about twenty
  decisions and about twenty ADRs or amendments followed, and none of those
  rows changed.
- **Rows defer to a step, and the step passes without closing them.** Five rows
  said "decide in iteration 6 residues". Iterations 6 and 7 both ran. All five
  were still Open.
- **Decisions and ADRs settle rows without saying so.** An ADR designed the
  path a row asked for, and the row stayed Open. A decision split a shared
  record into single-writer records. Two sibling rows were marked Superseded
  that day, and two others about the same record were not. An ablation cut a
  pipeline whose rows are still Open.
- **Every skill says "add"; closing is reactive.** The `journey-files.md`
  preamble fragment carries `assume add` into all fourteen tier 2 and 3
  skills. `assume status` is one table row: "something settles or changes an
  assumption". No step in `decision answer`, `/restack-adr`, the iterate gate,
  `ablate` or `/restack-design-review` asks which rows the work just settled.
  `decision answer` already refuses to run without `--actors`, so every
  decision says whether it changed the actor set. Nothing makes it say whether
  it settled an assumption.
- **One table, five kinds of item, no type.** The register holds unverified
  beliefs about existing systems, open design questions (decisions waiting for
  a brief), external asks, build-time test obligations ("measure in
  non-production") and post-launch observations ("count during shadow"). Each
  drains at a different stage. Only asks have a marker
  ([ADR-026](ADR-026-asks-routed-in-the-register.md)), and only asks drain.
- **The status record reads as split.** By contract the row's Status cell is
  the current state and the status lines are its history
  ([ADR-023](ADR-023-journey-files-written-by-a-helper.md)). The register
  never said so to its reader. With 241 status lines, several per row, the
  architect reconciled the two by hand.
- **Nothing shows the load.** `/restack-journey where` and `iterate` do not
  report how many rows are open, how old they are, or which open rows rest
  under an adopted ADR. `/restack-trace` checks that the register is
  consistent, not that it is current.

Recovering the live set took a separate triage: three parallel agents over the
full document set. Every new session pays that reading cost again.

## Decision

The rule from [ADR-023](ADR-023-journey-files-written-by-a-helper.md) holds
throughout: **`journey.py` never changes a status on the architect's behalf.**
Everything below either lists candidates, records a claim the architect made,
or writes a status the architect chose.

### 1. Every row has a kind, written as a prefix

The kind goes at the start of the `Validates it` cell, as an ask's recipient
already does. The seven columns stay as they are.

| Kind | Prefix | What it is | Where it drains |
|---|---|---|---|
| belief | none | an unverified claim about what exists | evidence: a discovery note, a code read, a test. `Resolved`, `Partly resolved` or `Withdrawn` |
| ask | `Ask <recipient>:` | only someone outside the design can settle it | the asks pack ([ADR-026](ADR-026-asks-routed-in-the-register.md), [ADR-027](ADR-027-asks-triaged-with-the-architect-first.md)) |
| decide | `Decide:` | an open design question | a decision brief. Ends `Superseded by D<n>` |
| test | `Test:` | a check the build has to run | the design answers it (`Resolved by design (test pending)`), and the build carries it |
| observe | `Observe:` | something only the running system can show | the design answers it, and operation carries it as a fitness function or a cadence item |

`assume add --kind decide|test|observe` writes the prefix, and
`assume kind A-<n> <kind>` sets it on an existing row after the architect
confirms it. Like `assume route`, it changes the start of that one cell and
nothing else. The prefix slot holds one kind, so `route` replaces a kind
prefix and `kind` replaces an ask's.

**A row the design has answered is carried, not exposure.** Whatever its
kind, a row `Resolved by design (test pending)` is an obligation handed to the
build or to operation. The register's summary counts carried rows apart from
open ones, so a design-only engagement doesn't report obligations it was never
going to discharge as live risk. No new status: `Resolved by design (test
pending)` already says it. A `Test:` or `Observe:` row still Open is exposure:
the design hasn't answered it yet.

### 2. Decisions say what they did to the register

`decision answer` takes a required `--assumptions`, alongside the `--actors`
it already requires:

- `none`; or
- clauses separated by `;`, each a verb and its IDs:
  `settles A-3, A-7; changes A-9; raises A-12`.
  - **settles**: it answers the row. The row's status should move.
  - **changes**: it alters what the row says or rests on. Re-read it.
  - **raises**: rows registered because of this decision.

Every ID must have a row. The answer writes `- **Assumptions:** <clauses>` into
the entry. It **does not change any status**: the architect chooses
`Resolved`, `Partly resolved` or `Superseded by D<n>` for each settled row, and
`assume status` writes it. `decision open` adds an `Assumptions: —` line to
new entries, and `decision note D<n> --assumptions ...` completes an answered
entry that never said, marked as recorded later, as `--actors` already can.

### 3. The events that settle rows are obliged to look for them

`journey.py assume touching <ref>...` lists the not-closed rows whose
Assumption, `Validates it` or `Depends on it` cell names any of the references:
an ID (`D12`, `ADR-0031`, `R-4`, `S-17`, `A-9`; zero padding and continued
ADR lists such as `ADR-0005, 0025` count) or a phrase (`iteration 6`, an
actor's name). Matching is textual. It is a worklist to confirm, never a
verdict ([ADR-021](ADR-021-trace-checks-as-a-worklist.md)).

Five events run it on what they just touched and put the candidates to the
architect before they finish:

| Event | Looks for rows naming |
|---|---|
| a decision brief answered | what the brief was about: the ADRs, residuals, actors and rows it names. Their answer fills `--assumptions` |
| an ADR created, amended or superseded | the ADR, what it supersedes, the residuals and actors it creates or removes. The ADR's `Assumptions:` header line records what it settles and what it rests on |
| the iterate gate | `iteration <n>` for this iteration, and the residuals the iteration changed |
| an ablation's answer | the removed residual and actors |
| a design review finding | the documents and actors the finding is about |

### 4. The register's load is visible where the route is decided

`journey.py register` prints a read-only summary:

- rows by status, then the not-closed rows by kind, with **exposure** (open
  beliefs, asks, decisions and undesigned obligations) apart from
  **carried** (obligations the design has answered);
- the exposure by age since its status date, in the mod's buckets (0–6,
  7–29, 30+ days), and how many were never touched after registration;
- how many of the exposure rows are **load-bearing**: their `Depends on it`
  names an ADR, decision or residual. The rest are incidental;
- four worklists, each a candidate to confirm:
  1. **said settled, still open**: a decision's `Assumptions:` says it settles
     the row, and the row is not closed;
  2. **deferred to a step that has passed**: the row names `iteration <n>`
     and iteration *n* is in the history, or names a decision that has been
     answered;
  3. **resting on something superseded**: `Depends on it` names a decision a
     later one supersedes, or an ADR whose status is Superseded or
     Deprecated;
  4. **decisions waiting for a brief**: open `Decide:` rows.

`/restack-journey where` and `iterate` print it. The iterate gate adds a step:
the rows this iteration should have settled go into the brief, and so does a
non-empty "said settled, still open" list.

### 5. The row is the current state

The register template and its preamble say so in one line: the row is the
current state, and the status lines are its history. `assume show A-<n>...`
prints a row's cells and its own status lines, and nothing else.

### 6. A register that has already accumulated is triaged with the architect

`/restack-journey settle [load-bearing | stale | kind <kind> | A-<n>...]` works
like the asks triage ([ADR-027](ADR-027-asks-triaged-with-the-architect-first.md)),
which settled 33 of 43 asks in its first run. It takes the candidates from
`register`'s worklists (or the scope given), load-bearing and oldest first. For
each it reads the evidence the worklist cites and asks one choice question,
with statuses drawn from that evidence and **Still open** always last. Each
answer is written with `assume status`, its `--why` pointing at the evidence.
Nothing is written that the architect has not chosen.

## Consequences

### Positive

- The register drains at the steps that settle it, while the evidence is in
  front of the architect, instead of in a triage weeks later.
- "What does the design rest on" has a one-command answer: the exposure count,
  its age and the load-bearing rows.
- Test and observe obligations stop inflating the open count once the design
  answers them, without leaving the register.
- A decision that settles rows says so in the log, so a missed status change is
  findable by script rather than by memory.

### Negative

- One more required field on every decision, and a confirm step on every ADR,
  ablation and iterate gate. Most will be `none`. The field is the point: a
  `none` that should have been something is visible in review, an absent field
  is not.
- `touching` is textual. It misses a row that describes the thing without
  naming it, and it lists rows that mention it in passing. The architect
  confirms every candidate, and `settle` is the backstop.
- Kinds are set by whoever registers the row, and can be wrong. `assume kind`
  corrects them, after the architect confirms.

### Neutral

- The status vocabulary and the seven columns don't change. A register written
  before this decision is still canonical. Its rows read as beliefs until a
  kind is set.
- `/restack-trace` gets no new check. Staleness is journey state, not document
  drift. `trace` REG still checks that the register is consistent.

## Knock-on changes

All done in 2.18.0.

| Document | What this decision requires there | Done in the same step |
|---|---|---|
| `skills/restack-journey/scripts/journey.py` | `--kind`, `assume kind`, `assume show`, `assume touching`, `register`, `--assumptions` on `decision answer` and `decision note` | done 2026-10-07; `decision open` writes the field, and an entry opened before it gets the line on answer |
| `tests/test_journey.py`, `tests/fixtures/journey/` | an invented register with every kind, a stale deferral, a superseded dependency and a decision that settles a row | done 2026-10-07: the `drain` journey, one planted case per worklist, and tests that no new command changes a status |
| `scripts/preamble/journey-files.md`, `journey-state.md` | the new commands; closing is an obligation; the row is current | done 2026-10-07: *Close what the work settles* and *The row is the current state*, carried by every tier 2 and 3 skill |
| `templates/assumptions-register-template.md`, `decisions-log-template.md`, `adr-template.md` | kinds; the row is current; the `Assumptions` field and header line | done 2026-10-07, and `skills/restack-adr/sections/adr-format.md` |
| `skills/restack-journey/SKILL.md.tmpl` | `where` and `iterate` print `register`; the iterate step; `settle`; review's twelfth failure | done 2026-10-07: `/restack-journey` 2.6.0, iterate step 10 |
| `skills/restack-adr/SKILL.md.tmpl` | `create` and `update` look for touched rows and fill the header line | done 2026-10-07: `/restack-adr` 2.3.0 |
| `skills/restack-stressor/sections/ablation.md` | after the answer, the rows naming the removed set | done 2026-10-07: `/restack-stressor` 2.5.0, Step 8 |
| `skills/restack-design-review/SKILL.md.tmpl` | a finding that settles or refutes a row goes to the register | done 2026-10-07: `/restack-design-review` 2.4.0, step 9 |
| CLAUDE.md, README.md, QUICKREF.md, GETTING_STARTED.md, CHANGELOG.md, VERSION | the command and the ADR | done 2026-10-07: 2.18.0 |

## Alternatives considered

### A `Kind` column

- **Pros:** explicit, sortable, and visible in a rendered table.
- **Cons:** every existing register stops being canonical and has to be
  migrated. `journey.py`, `trace.py`, the restack-view mod and all their
  fixtures change shape for a field the `Validates it` prefix already carries
  for asks.
- **Why rejected:** the prefix works, it has a precedent, and an existing
  register keeps working unchanged.

### An optional `--assumptions`

- **Pros:** no friction on the many decisions that touch no row.
- **Cons:** the engagement's failure is that the step was available and never
  taken. An optional field is that same step.
- **Why rejected:** `--actors` is required for the same reason, and it works.

### Let `decision answer --assumptions "settles A-3"` set the status

- **Pros:** one command instead of two, and nothing can drift between them.
- **Cons:** "settles" doesn't say whether the row is Resolved, Partly resolved
  or Superseded by the decision. Choosing one for the architect is the move
  [ADR-023](ADR-023-journey-files-written-by-a-helper.md) forbids.
- **Why rejected:** the claim is recorded, the status is chosen, and
  `register` lists any gap between the two.

### A "handed over" status or send line for test obligations

- **Pros:** a test row could leave the register once a backlog item exists.
- **Cons:** it adds machinery for a destination the toolkit doesn't own and
  can't check, and the reference engagement was design-only.
- **Why rejected for now:** counting carried rows apart from exposure solves
  the reading problem. Revisit if an engagement hands a backlog over.

### A trace check for stale rows

- **Pros:** `/restack-trace` already runs at review and after ADR batches.
- **Cons:** "this row is probably settled" is a judgement about journey state,
  not drift between documents. And `where` and `iterate` are where the load
  needs to be seen.
- **Why rejected:** the summary belongs to the helper that owns the register.

## References

- [ADR-021](ADR-021-trace-checks-as-a-worklist.md): a script's output is a
  worklist, not a verdict
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): the journey files are
  written by a helper that never changes a status for the architect
- [ADR-026](ADR-026-asks-routed-in-the-register.md): the `Ask <recipient>:`
  prefix this decision generalises
- [ADR-027](ADR-027-asks-triaged-with-the-architect-first.md): triage with the
  architect first, the model for `settle`
- [ADR-028](ADR-028-residuals-challenged-by-removal.md): ablation, one of the
  events that settles rows
