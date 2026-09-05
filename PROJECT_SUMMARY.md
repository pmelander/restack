# ReStack — Project Summary

A one-page orientation for anyone deciding whether to adopt, extend, or
contribute to this toolkit. For what it does and why, read the
[README](README.md); for how the toolkit itself is built, read
[CLAUDE.md](CLAUDE.md).

---

## What it is

Fifteen Claude Code skills implementing
[Residuality Theory](RESIDUALITY.md) as a working architectural practice —
walking paths, stress-testing them against scenarios including deliberately
absurd ones, and identifying the discrete architectural changes (residuals)
that reduce whole classes of exposure at once.

**Status:** v2.0.0, September 2026. All fifteen skills generated from
templates with a shared behavioural preamble. CI enforces that generated files
match their source. Not yet run end to end on a live engagement in this form.

---

## The premise

Skills are **capability transfer tools, not dependency-creating tools**. Every
skill states what thinking it builds and what success looks like when it is no
longer needed. The measure is how rarely the toolkit gets invoked because the
thinking has been internalised.

That premise is enforced in review: a proposed skill that would train
architects to work from checklists or registers is turned down, however useful
it looks.

---

## How it is built

| | |
|---|---|
| **Source of truth** | `skills/<name>/SKILL.md.tmpl` — `SKILL.md` is a build artifact |
| **Generator** | `python scripts/gen_skills.py`, standard library only |
| **Shared behaviour** | `scripts/preamble/`, composed by declared tier (1 utility, 2 decision-shaping, 3 residuality core) |
| **On-demand depth** | `skills/<name>/sections/` — 42 sections, read when their situation applies rather than loaded every run |
| **Validation** | `gen_skills.py --check` (drift) and `check_skills.py` (frontmatter, banners, orphaned sections), both in CI |
| **Document formats** | `templates/` is canonical; skills carry method, not format |

This structure exists so cross-cutting behaviour — how a decision is put to the
architect, what counts as evidence, when a workflow must stop — is defined once
rather than fourteen times, and so a skill can carry deep method without paying
for it on every invocation.

---

## Behaviour that distinguishes it

- **Decision briefs.** Judgement calls become structured briefs rating
  **confidence** (is this built on verified beliefs, and what would raise it)
  and **reversibility** (reversible / costly / one-way door) — the axes
  architecture decisions actually turn on.
- **Stop gates.** Three points halt rather than drift past: the confidence gate
  (do we understand this system well enough to stress it?), the iterate gate
  (is impact low enough?), and approach gates.
- **Evidence rules.** Documentation rates *low*; inference from a component's
  name is not evidence. Unverified claims are registered as assumptions.
- **File-based state.** `docs/journey/` carries position, iteration history,
  decisions and assumptions, so an engagement survives weeks and handoffs.
- **`NEEDS_DISCOVERY`** is a first-class outcome — the toolkit's own route is
  the remedy when it does not know enough.

---

## Decisions on record

Eleven ADRs. Four matter most to anyone evaluating the approach:

| ADR | Decision |
|---|---|
| [001](docs/adr/ADR-001-incorporate-residuality-theory.md) | Residuality Theory as the foundation |
| [006](docs/adr/ADR-006-exclude-risk-assessor-skill.md) | **No risk assessor** — registers train enumerated-threat thinking; stressor analysis covers risk and reaches further |
| [007](docs/adr/ADR-007-compliance-via-stressor-packs.md) | **No compliance checker** — compliance enters as stressor packs so residuals address the harm structurally |
| [008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md) | Generated skills, tiered preamble, on-demand sections |

Also: [002](docs/adr/ADR-002-redesign-phase-2-for-capability-building.md)
capability-building redesign, [003](docs/adr/ADR-003-add-stressor-analysis-skill.md)
stressor analysis, [004](docs/adr/ADR-004-add-excel-reading-utility.md) Excel
utility, [005](docs/adr/ADR-005-add-architecture-learning-analyzer.md) learning
analyzer, [009](docs/adr/ADR-009-prefix-skill-names.md) prefixed skill names, and
[010](docs/adr/ADR-010-skills-are-self-contained.md) skills ship their own
runtime dependencies, and
[011](docs/adr/ADR-011-setup-script-and-upgrade-skill.md) setup script and
upgrade skill.

ADR-006 and ADR-007 are the ones worth reading first — they show the philosophy
actively deciding what *not* to build, which is the clearest statement of what
this toolkit is for.

---

## Layout

```
skills/restack-*/          15 skills: SKILL.md.tmpl (source) + SKILL.md + sections/
setup, setup.ps1           installer; /restack-upgrade re-runs it
scripts/                   generator, validator, preamble fragments
templates/                 canonical document formats
docs/adr/                  11 ADRs
docs/                      installation, usage
examples/                  example outputs
```

---

## Contributing

Highest value first:

1. **Reports from real use** — especially where a gate got in the way.
2. **Compliance packs** — HIPAA, PCI DSS, ISO 27001, SOC 2. GDPR ships as a
   worked example. Each stressor must be a walkable scenario, not a restated
   control.
3. **Skills that fit the theory**, with an argument for why they build
   capability rather than dependency.

`SKILL.md` files are generated — edit the `.tmpl` and run the generator; CI
rejects drift. See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[Roadmap](ROADMAP.md).
