# ReStack — Roadmap

Where the toolkit is, what is next, and what has deliberately been ruled out.

---

## Where it is now

**v2.0.0 — all fifteen skills generated, September 2026.**

Every skill is rendered from a template with a shared behavioural preamble, so
cross-cutting behaviour — decision briefs, evidence rules, stop gates, the
journey-state contract — is defined once rather than fourteen times.

Installation is a `setup` script rather than a manual copy: it reports what
changed, removes skills deleted upstream, and records where it installed from
so `/restack-upgrade` can pull and reinstall in one command. `INSTALL.md`
carries agent-followable instructions, so pointing a Claude session at the
repository is a supported way in.

CI checks on every push that no generated file has drifted from its source,
that the skills tree is valid, and that **every install path a skill tells
Claude to use actually resolves** — the check that would have caught the
`/restack-excel` helper bug three refactors earlier.

| | |
|---|---|
| Skills | 15 (14 architecture + `/restack-upgrade`) |
| Sections (on-demand depth) | 42 across 13 skills |
| Preamble tiers | 3 at tier 3 (residuality core), 10 at tier 2, 2 at tier 1 |
| Compliance packs | 1 (GDPR) |
| ADRs | 13 |

The decisions behind this shape:
[ADR-001](docs/adr/ADR-001-incorporate-residuality-theory.md) (Residuality
Theory as the foundation),
[ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md) (generated
skills, tiered preamble, on-demand sections),
[ADR-009](docs/adr/ADR-009-prefix-skill-names.md) (prefixed names),
[ADR-010](docs/adr/ADR-010-skills-are-self-contained.md) (skills ship their own
runtime dependencies) and
[ADR-011](docs/adr/ADR-011-setup-script-and-upgrade-skill.md) (setup script and
upgrade skill).

---

## Next

### 1. Field validation — the only thing that really matters

**These skills have not been run end to end on a live engagement in v2 form.**
Fourteen skills were rewritten against their own internal logic and against
each other; that is not the same as working.

What would tell us most, in order:

- Which gate did you want to skip, and why? A gate people route around is
  either badly placed or badly argued.
- Where did a skill produce something you could not use?
- Did the compounding actually show up — did one residual clear stressors it
  was not designed for?
- Did `docs/journey/` survive a real gap, handoff, or interruption?

Open an issue with what happened. Negative reports are more useful than
positive ones.

### 2. Compliance packs

GDPR ships as a worked example. Wanted: **HIPAA, PCI DSS, ISO 27001, SOC 2**,
and anything sector-specific.

The bar is the part that takes the work: each stressor must be a **concrete
scenario you could walk against an actor**, not a restated control. "Implement
access controls" is a control. "A support engineer with standing production
access queries a customer record out of curiosity, six months before anyone
reviews the audit log" is a stressor. See
`skills/restack-stressor/compliance-packs/README.md`.

### 3. Journey state as tooling rather than prose

The journey-state contract is currently instructions the model follows, and
over a long session that degrades. It is the last open follow-up from
[ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md).

A small helper writing state atomically would make persistence structural
instead of behavioural — modest work, and the reliability gain lands on exactly
the long-running engagements the toolkit exists for. The same argument that
justified `setup` over `cp -R`: a step that matters should not depend on
remembering to take it.

### 4. A worked end-to-end example

`examples/` has fragments — an ADR, an HLD, a banking stressor analysis. What
is missing is one engagement followed from `/restack-journey start` through
three stressor iterations to a design review, with the journey state at each
step.

That is the fastest way for someone to understand what the toolkit produces,
and it doubles as a regression test for the skills' coherence.

### 5. An unattended mode

Run the full sequence — discover, walk, generate, analyse, residues — with
intermediate decisions auto-resolved by stated principles, surfacing everything
genuinely contestable at a **single** approval gate at the end.

The design question worth getting right is which decisions may never be
auto-resolved. Terrain classification and the confidence gate probably qualify:
both are judgements about what you do not know, and a model auto-answering them
is precisely the false confidence this toolkit exists to avoid.

### 6. Update awareness

Today an install only learns it is stale when someone remembers to run
`/restack-upgrade`. The skills should notice for themselves, at the right
moments and no others.

The shape worth building:

- **When:** at session-opening commands only (`/restack-journey start` and
  `where`, `/restack-discover paths`), and at most once a day, using a timestamp
  in `~/.restack/`. Never inside a stop gate or while a brief is open, because
  an upgrade notice there competes with the decision.
- **How:** read `repo` from `~/.restack/install.json` and compare the local
  `VERSION` against `origin/main:VERSION`. Being offline or having no git
  checkout is silent, never an error.
- **What it does:** one line, "ReStack v2.4.0 available (installed v2.3.0):
  `/restack-upgrade`", plus a snooze. It never upgrades itself. A skill set that
  changes under an in-flight journey breaks the journey's audit trail.
- **Opt-out:** a setting in `~/.restack/` turns it off, for environments where
  an outbound fetch from a skill is not acceptable.

gstack's update check is the reference for the throttle and snooze. Open
question: should a symlinked development install report "local behind remote"?
It cannot be upgraded by copy, so the notice would need different wording.

### 7. ~~Next step as a button~~ — done

Shipped as a tier-1 preamble fragment, `next-step.md`, so all sixteen skills
end the same way. A `Next:` line names the full command, and where the host has
a widget tool with `sendPrompt()`, a button sits below it. The skill degrades
silently to the line alone, renders one to three buttons, and never renders one
for a gate.

The open question is settled: **a button carries the command, never its
arguments.** The `Next:` line keeps the arguments. A command that arrives bare
resolves its target from the journey state at click time, so a stale button
cannot send a stale target, and no text from a file reaches `sendPrompt()`. See
[ADR-017](docs/adr/ADR-017-next-step-as-a-button.md).

What is still unknown: whether the one line a bare command spends naming its
target is friction people notice, or the confirmation they wanted anyway.

### 8. ~~Cross-model second opinion~~ — done

Shipped in 2.2.0 as an outside opinion in three places, behind a data gate that
defaults to anonymised. See
[ADR-013](docs/adr/ADR-013-outside-opinion.md).

What is still unknown: how often Codex is actually present. Most runs will get
the same-family fallback, whose agreement is weak evidence. If it turns out
nobody has Codex installed, the honest question is whether the fallback alone
justifies the step.

---

## Deliberately not doing

These are positions, not gaps, and each has an ADR arguing it.

**A risk assessor.** Risk registers train architects to think in enumerated
threats, which is the habit this toolkit exists to break. Stressor analysis
covers risk and reaches further —
[ADR-006](docs/adr/ADR-006-exclude-risk-assessor-skill.md).

**A compliance checker.** Compliance enters as stressor packs so that residuals
address the underlying harm structurally, rather than satisfying a control on
paper — [ADR-007](docs/adr/ADR-007-compliance-via-stressor-packs.md).

**A severity scale on the matrix.** Binary scoring is not a simplification.
Severity estimates look like measurements, let uncomfortable stressors be
argued down, and make the matrix too expensive to rebuild each iteration —
and a matrix that stops being rebuilt is worse than none.

**Telemetry, analytics, or usage tracking.** This is a fourteen-skill toolkit,
not a platform. That machinery would cost more in ceremony than it returns.

Any new skill has to pass one test: **does it build thinking the architect
carries forward, or does it create dependency?** A skill that trains people to
work from checklists will be turned down however useful it looks.

---

## Version history

| Version | What changed |
|---|---|
| **2.0.0** | Sep 2026 — all skills generated from templates; shared tiered preamble; decision briefs with confidence and reversibility; three stop gates; on-demand sections; every skill wired to the residuality core; renamed to ReStack; all skills prefixed; `setup` + `/restack-upgrade` + agent-followable install; CI |
| 1.x | May 2026 — 14 skills as hand-maintained files. Residuality Theory adopted ([ADR-001](docs/adr/ADR-001-incorporate-residuality-theory.md)); Phase 2 redesigned around capability building ([ADR-002](docs/adr/ADR-002-redesign-phase-2-for-capability-building.md)); stressor analysis added ([ADR-003](docs/adr/ADR-003-add-stressor-analysis-skill.md)); risk assessor excluded ([ADR-006](docs/adr/ADR-006-exclude-risk-assessor-skill.md)); compliance moved to stressor packs ([ADR-007](docs/adr/ADR-007-compliance-via-stressor-packs.md)) |

---

## Contributing to the roadmap

Open an issue. The most valuable contributions, in order:

1. **What happened when you used it.** Especially where it got in the way.
2. **A compliance pack**, meeting the scenario bar above.
3. **A skill idea that fits the theory** — with an argument for why it builds
   capability rather than dependency.

See [Contributing](CONTRIBUTING.md).
