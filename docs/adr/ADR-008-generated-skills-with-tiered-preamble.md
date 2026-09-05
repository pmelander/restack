# ADR-008: Generate SKILL.md from Templates with a Tiered Shared Preamble

**Status:** Accepted

**Date:** 2026-09-05

**Deciders:** ReStack maintainers

**Technical Story:** Adopting proven skill-authoring patterns from gstack

**Implementation Status:** partially implemented — `/journey` and `/stressor` converted; twelve skills remain

**Implemented Date:** 2026-09-05

**Implemented By:** ReStack team

**Review Date:** 2027-03-05

## Context

Fourteen skills, each a hand-maintained `SKILL.md`, produced three problems that
were getting worse as the toolkit grew.

**Cross-cutting behaviour was duplicated or absent.** The journey-state
persistence contract was written twice, in `CLAUDE.md` and in
`skills/journey/SKILL.md`, in different words. The Residuality vocabulary
existed only in `skills/stressor/SKILL.md`, so every other skill either
restated it loosely or assumed it. There was no shared statement of how to ask
the architect a question, what counts as evidence about an existing system, or
how to close a command — so those behaviours were inconsistent where they
existed at all, and mostly they did not.

**Instruction depth varied without reason.** `/stressor walk` was specified as
six executable steps. `/stressor analyze`, `vulnerabilities`, `residues` and
`iterate` were four or five summary bullets each — enough to describe the
command, not enough to execute it. The model narrates a bulleted description
and executes a numbered protocol, and the difference showed in output quality
on exactly the commands that carry the method.

**Every skill loaded whole, every time.** The largest skills run to 900 lines.
Content that applies to one run in four — the greenfield route when the terrain
is minefield, workshop facilitation when there is no workshop — was paid for on
every invocation. That capped how deep any single skill could afford to go,
which is the opposite of what this toolkit is for.

We evaluated gstack (Garry Tan's skill suite) as a reference implementation.
Its skills are generated from templates, compose shared behaviour by declared
tier, split situational depth into on-demand sections, and gate architect
decisions behind a structured brief format. Those mechanics are independent of
gstack's subject matter and transfer cleanly.

## Decision

**`skills/<name>/SKILL.md` becomes a build artifact.** The source of truth is
`skills/<name>/SKILL.md.tmpl`, and `python scripts/gen_skills.py` renders it.
Generated files carry an `AUTO-GENERATED` banner. `--check` verifies the tree is
current and exits non-zero on drift, so CI can enforce it.

**Shared behaviour lives in `scripts/preamble/` and is composed by tier**, each
skill declaring `preamble-tier: N` in its frontmatter:

| Tier | For | Adds |
|---|---|---|
| 1 | utilities with no architectural judgement | voice, completion status |
| 2 | skills that shape architectural decisions | decision briefs, evidence rules, completeness, confusion protocol |
| 3 | the residuality core — journey and stressor loop | vocabulary, stop gates, journey state contract |

**Situational depth moves to `skills/<name>/sections/`**, registered in a
passive `manifest.json` and surfaced by a generated section index that tells the
model to read a section when its situation applies. The manifest is a registry
only — the skeleton's prose decides when to read, so there is no second place
that encodes control flow.

**Architect decisions are issued as structured decision briefs** via
`AskUserQuestion`, and the points where a workflow must halt are named **stop
gates** rather than described as recommendations.

### What we adapted rather than copied

gstack's decision brief scores each option for *completeness* — appropriate for
implementation choices. Ours scores **confidence** (is the option set built on
verified beliefs about the system, and what would raise it) and
**reversibility** (reversible / costly / one-way door), and carries an
**aspiration** line so a decision that serves no stated aspiration is visible as
scope creep. Those are the axes architecture decisions actually turn on, and
`Confidence: Low` on a one-way door routes to `/discover` instead of to a
choice.

gstack's completion statuses end with `NEEDS_CONTEXT`. Ours is
`NEEDS_DISCOVERY`, naming the specific unknown and the `/discover` command that
closes it — which makes the toolkit's own route the remedy.

### What we deliberately did not take

Telemetry and analytics, cross-machine memory sync, browser automation, model
overlays, host-session branching, and version-bump ceremony. Those solve
problems of a large distributed skill platform with a user base. This is a
fourteen-skill toolkit; that machinery would cost more in ceremony than it
returns in behaviour, and ceremony crowding out substance is the specific
failure mode of this port.

## Consequences

**Positive**

- Cross-cutting behaviour is changed once. Amending the decision-brief format
  updates every skill at the next generate.
- Depth is now affordable. `/stressor` carries a full matrix-construction and
  residual-leverage method in sections, at no cost on runs that do not need them.
- Weak commands were forced into the open. Converting `/stressor` required
  writing the analyze/vulnerabilities/residues method that was previously
  implied — the conversion was the audit.
- Drift is detectable. `--check` in CI catches a hand-edited `SKILL.md`, and
  caught one stale fact during this work: `SKILL.md` listed the GDPR pack as
  planned while `compliance-packs/README.md` and a 176-line `gdpr.md` said
  otherwise.

**Negative**

- Two-step authoring. Contributors edit a template and run a generator; a
  hand-edit to `SKILL.md` is silently lost at the next build. Mitigated by the
  banner, the `--check` mode, and documentation in `CONTRIBUTING.md`.
- Python is now required to develop the toolkit, not just to use `/excel`. The
  generator is standard-library-only to keep that cost at zero installs.
- Mixed state until the remaining twelve skills are converted: some skills have
  the shared preamble and some do not.

**Neutral**

- Generated files stay committed. They are what Claude Code loads, and a
  contributor must be able to read the assembled skill without running a build.

## Follow-ups

1. Convert the remaining twelve skills, tiering each: `/discover` at tier 3;
   `/adr`, `/solution-doc`, `/tech-stack`, `/design-review`, `/cloud`,
   `/capacity`, `/arch-learning`, `/capability-assessor`, `/patterns`,
   `/evolve` at tier 2; `/excel` at tier 1.
2. Add `python scripts/gen_skills.py --check` to CI.
3. Resolve the `/design-review` name collision with gstack — installing this
   toolkit's skills flat into `~/.claude/skills/` currently overwrites gstack's
   skill of the same name.
4. Consider replacing prose-instructed journey-state writes with a small helper
   binary, so persistence does not depend on the model remembering to do it.
