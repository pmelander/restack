# ADR-022: ReStack Is a Working Toolkit, Not a Training Pack

**Status:** Accepted

**Date:** 2026-10-03

**Deciders:** ReStack maintainers

**Technical Story:** architect, 2026-10-03: "This was never the intention. This
is not a training pack. It might be an unintended consequence, but we should
not build the pack around that premise."

**Implementation Status:** implemented

**Implemented Date:** 2026-10-03

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-03

## Context

[ADR-001](ADR-001-incorporate-residuality-theory.md) adopted Residuality Theory,
and with it a second idea that the theory does not require: that the toolkit's
job is to build capability in the architect, measured by how rarely the skills
are needed once the thinking is internalised.
[ADR-002](ADR-002-redesign-phase-2-for-capability-building.md) made that the
organising principle of Phase 2. By 2.9.1 it was structural:

- every skill template carried **Capability being built** and **Residuality
  goal** sections, and closed with **Reflection prompts**;
- the voice fragment required "capability transfer over answer delivery" and a
  reflection prompt at the end of every session, "not optional";
  [ADR-020](ADR-020-follow-up-commands-run-without-pause.md) held them to the
  end of a chain;
- CLAUDE.md called skills "capability transfer tools" judged by how rarely
  they are invoked, and the ROADMAP's test for a new skill was "does it build
  thinking the architect carries forward, or does it create dependency?";
- behaviour followed: `/restack-design-review self-check` refused to review
  ("this command exists to transfer the capability"), and `/restack-adr` asked
  its questions one at a time because "the questions are the capability
  transfer"; the README promised "eventually you do it without them".

That was never the intention. The architect uses ReStack as a working toolkit
on live engagements. The reference brownfield engagement ran 61 ADRs, seven
stressor iterations and a full document set through it, and nothing about that
work was improved by a closing question or a skill designed around its own
obsolescence. The premise also justified behaviour on the wrong grounds: a
review that withholds findings, or a rule followed because it teaches rather
than because it produces a better record.

One thing that sat under the premise is right, for a different reason: the
architect owns the decisions. Gates, decision briefs and "never auto-resolve"
exist because the architect answers for the design. That stays.

## Decision

1. **ReStack is a working toolkit.** It does residuality-based architecture
   work rigorously: discovery, stressor analysis, decisions, documentation,
   and keeping a long engagement consistent. The skills run the method and
   keep the record; the architect makes the calls. A skill is measured by the
   quality and traceability of what it produces.
2. **Every skill states what it produces and when it is done.** The
   **Capability being built** and **Residuality goal** sections are replaced
   by **What it produces** (the artifacts, and where) and **Done when** (a
   checkable bar). Content in the old sections that described a good output
   moved into them.
3. **Reflection prompts are removed**: from the voice fragment, from the chain
   rules in `next-command.md`, from the fifteen skills that had them, and from
   two command steps that closed with one. A prompt that carried method moved
   into the skill's **Done when** as a check on the output (for example "the
   Negative consequences are not empty", "the most likely reason the matrix
   is wrong is stated").
4. **Decision ownership stays, justified as accountability.** The voice rule
   becomes "The architect owns the judgement": do the analysis in full, put
   the frame and the tradeoff in front of the architect, never quietly make
   their call. Gates, briefs and stop rules are unchanged.
5. **`/restack-design-review self-check` becomes an author's review.** The
   architect reviews against the criteria, the skill challenges their answers,
   then adds what it saw as findings marked as its own. One finding list.
6. **Behaviour with a teaching rationale is kept only where it has another
   one.** `/restack-adr` still asks one question at a time, because each answer
   changes the next question and a batch gets answered as a form.
7. **Skills whose subject is a team's learning or capability keep it.**
   `/restack-arch-learning`, `/restack-capability-assessor` and
   `/restack-patterns` analyse how a team decides and what it can do. That is
   work the toolkit does, not a premise about the toolkit.
8. **Existing project documents are not rewritten by this change.** Projects
   written under the old style keep their text. A restyle mode that rewrites
   wording without changing material content is on the ROADMAP.

### Decision-point accounting

| # | Decision point | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| 1 | ADR-001: incorporate Residuality Theory | holds | design for enumerated risks only | unchanged |
| 2 | ADR-001: shift from tool-centric to a capability-building system | withdrawn | output produced without the reasoning behind it | **What it produces** requires the reasoning in the artifact (ADR context and alternatives, residuals with the stressors they clear, Done-when checks) |
| 3 | ADR-001: reflection prompts in every skill | withdrawn | a run ending without anyone examining it | the **Done when** checks, which examine the output rather than ask the architect to |
| 4 | ADR-001: outcome tracking | holds | decisions never revisited | unchanged (`/restack-adr review`, `/restack-arch-learning`) |
| 5 | ADR-002: the four organisational skills | holds | no way to learn from history, assess a team, extract patterns, keep residuals true | unchanged |
| 6 | ADR-002: build capability *in* users rather than do analysis *for* them | withdrawn | architects deferring judgement to the tool | decision 4: the architect owns every call, and the skills stop at it |
| 7 | ADR-005: reflection prompts at each stage of arch-learning | withdrawn | lessons stated without being examined | **Done when**: every miss has a cause and the cheapest point it could have been caught |
| 8 | ADR-020 point 4: reflection prompts close the chain | withdrawn | the chain ending on mechanics | the chain ends at its status line and `Next:`; nothing to hold |

## Consequences

### Positive

- Every skill now has a checkable bar for its own output, which the old
  sections never gave. "Done when" can be reviewed; "the capability has
  transferred" could not.
- Commands end when the work ends. No closing question to answer or skip.
- Behaviour is justified by the quality of the result or by accountability,
  both of which an architect can argue with on the merits.

### Negative

- Some reflection prompts did surface real gaps ("which stressor did the room
  want to argue down?"). Those that carried method were moved into Done when;
  any that were missed are lost until a field run shows the gap.
- ADR-001 and ADR-002 now carry amendments that withdraw part of what they
  decided. The history reads less cleanly than a single founding premise did.
- Projects written in the old style (reflection sections in journey notes,
  "capability" language in documents) are inconsistent with the pack until
  they are restyled.

### Neutral

- Historical documents in `docs/` (phase summaries, integration and
  measurement write-ups) are records of what was believed then. They carry a
  banner saying so and are not rewritten. ADR-003, ADR-004, ADR-012, ADR-017
  and ADR-018 use the old vocabulary as history or as a category label and
  specify nothing current; they are left as they are. (`trace terms` on the
  old terms lists them; each was checked.)

## Knock-on changes

| Document | What this decision invalidates | Done in the same step |
|---|---|---|
| `scripts/preamble/voice.md`, `next-command.md` | the capability-transfer and reflection rules | updated |
| 16 skill templates (all but `/restack-upgrade`), 4 section files | Capability/Residuality-goal sections, reflection prompts, self-check, teaching rationales | updated, regenerated |
| CLAUDE.md, README.md, ROADMAP.md, RESIDUALITY.md, QUICKREF.md, PROJECT_SUMMARY.md | the premise, the template structure, the new-skill test | updated |
| ADR-001, ADR-002, ADR-005, ADR-020 | the withdrawn points in the table above | bannered and marked inline |
| `docs/PHASE1_REFACTOR_SUMMARY.md`, `PHASE2_REDESIGN.md`, `RESIDUALITY_INTEGRATION_COMPLETE.md`, `RESIDUALITY_MEASUREMENT_FRAMEWORK.md` | the premise, as current guidance | bannered as historical record |

## Alternatives considered

### Keep reflection prompts, optional

- **Pros:** keeps the prompts that surfaced real gaps.
- **Cons:** an optional closing question is still a question at the end of
  every command, and still frames the run as an exercise.
- **Why rejected:** the useful ones are checks on the output, and belong in
  Done when, where they are applied rather than asked.

### Delete the sections without replacing them

- **Pros:** smallest change.
- **Cons:** loses the quality bar some of them carried, and leaves skills with
  no statement of what done looks like.
- **Why rejected:** "What it produces" and "Done when" are what a working
  toolkit owes its user.

### Supersede ADR-001 and ADR-002 outright

- **Pros:** one clean replacement.
- **Cons:** both contain decisions that hold (adopting the theory, the four
  organisational skills), and superseding them would retire those too.
- **Why rejected:** the withdrawn points are accounted for above and the ADRs
  are amended, which is what `/restack-adr update` prescribes when a decision
  stands with parts withdrawn.

## References

- [ADR-001](ADR-001-incorporate-residuality-theory.md),
  [ADR-002](ADR-002-redesign-phase-2-for-capability-building.md),
  [ADR-005](ADR-005-add-architecture-learning-analyzer.md),
  [ADR-020](ADR-020-follow-up-commands-run-without-pause.md): amended
