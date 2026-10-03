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

### 3. ~~Journey state as tooling rather than prose~~ — done

The journey-state contract is currently instructions the model follows, and
over a long session that degrades. It is the last open follow-up from
[ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md).

A small helper writing state atomically would make persistence structural
instead of behavioural — modest work, and the reliability gain lands on exactly
the long-running engagements the toolkit exists for. The same argument that
justified `setup` over `cp -R`: a step that matters should not depend on
remembering to take it.

**The reading half shipped in 2.9.0** as `/restack-trace`
([ADR-021](docs/adr/ADR-021-trace-checks-as-a-worklist.md)): a read-only
script that finds where the journey files and the documents drift, and hands
the reviewer a worklist. **The writing half shipped in 2.11.0** as
`journey.py` in `/restack-journey`
([ADR-023](docs/adr/ADR-023-journey-files-written-by-a-helper.md)): every tier
2 and 3 skill writes the decisions log, the register and the journey history
through it, a brief takes its `D<n>` when it is issued, and a non-canonical
file is refused rather than guessed at. `migrate` converts the old shapes.

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

2.8.0 covers the first half: commands chain without pause between questions
([ADR-020](docs/adr/ADR-020-follow-up-commands-run-without-pause.md)). Gates
are still answered where they arise, never auto-resolved, so a single approval
gate at the end remains open.

### 6. ~~Update awareness~~ — done

Shipped in 2.5.0. `/restack-journey start` and `where`, and
`/restack-discover paths`, print one line at most once a day when `origin/main`
has a newer `VERSION`, with a snooze. The check never upgrades anything and
never runs inside a gate. It is off with `/restack-upgrade off` or
`RESTACK_UPDATE_CHECK=off`. See
[ADR-016](docs/adr/ADR-016-update-awareness.md) and
[INSTALL.md](INSTALL.md#update-check-and-opt-out).

The open question was settled: a symlinked install reports, with different
wording. On `main` it names `git pull --ff-only`. On a branch it only reports
the gap. It never points at `/restack-upgrade`'s copy path.

What is still unknown: whether once a day is the right cadence, or whether
architects snooze it every time. If the snooze is the normal response, the
notice is noise and the cadence should drop to weekly.

### 7. ~~Next step as a button~~ — built and withdrawn

Shipped in 2.5.0 and withdrawn in 2.5.2 the same day. In the desktop app's Code
tab a button fills the message box rather than sending, text starting with `/`
never arrives, and a button often needed several clicks before its command
appeared at all. Those are host behaviours ReStack can neither test nor fix,
and a button less reliable than the text line above it adds nothing.

The open question was settled and the reasoning still stands for any future
attempt: **carry the command, never its arguments,** and resolve the target
when the command runs. See
[ADR-017](docs/adr/ADR-017-next-step-as-a-button.md) for what was established,
what was not, and what would justify trying again.

What came back in 2.6.0 is smaller: the `Next:` line, with the command in a
fenced `text` block the host gives a Copy button. Arguments are included,
because a copied command is pasted and sent by the architect, not on their
behalf ([ADR-018](docs/adr/ADR-018-next-command-as-a-copy-block.md)).

In 2.8.0 the command runs instead, through the `Skill` tool, and the block is
the fallback ([ADR-020](docs/adr/ADR-020-follow-up-commands-run-without-pause.md)).

### 8. ~~Cross-model second opinion~~ — done

Shipped in 2.2.0 as an outside opinion in three places, behind a data gate that
defaults to anonymised. See
[ADR-013](docs/adr/ADR-013-outside-opinion.md).

What is still unknown: how often Codex is actually present. Most runs will get
the same-family fallback, whose agreement is weak evidence. If it turns out
nobody has Codex installed, the honest question is whether the fallback alone
justifies the step.

### 9. Restyle an existing project

Projects written under an older style keep it. The reference engagement has
61 ADRs and a full document set written while the pack still closed with
reflection prompts and spoke of capability transfer
([ADR-022](docs/adr/ADR-022-working-toolkit-not-training-pack.md)), and earlier
formats besides (several register tables, footnote amendments).

Wanted: a mode that rewrites the **wording and shape** of existing documents
to the current style, **ADRs included, as long as nothing material changes**.
That conflicts on purpose with `/restack-adr`'s rule "never quietly rewrite a
decision", so the mode needs a guard that proves it changed only wording:

- the material content is compared before and after: IDs, statuses, dates,
  decision points, alternatives, figures, Knock-on rows, cited stressors and
  residuals. Any difference stops the rewrite for that document;
- every restyled document gets an editorial note (date, "wording only", what
  was reshaped), so the history stays honest;
- a change that *would* be material goes to `/restack-adr update` as a
  decision, never through restyle.

trace already parses most of the material content, which makes it the
natural home for the before-and-after comparison. Write the user story when
the work reaches it.

**The journey files are done** (2.11.0, `journey.py migrate`): structure only,
with a material check that refuses to write if any word, ID or status would be
lost, and everything that needs judgement left to the architect. What remains
is the descriptive documents and the ADRs, where restyling means rewording,
and "no word lost" is no longer the right guard.

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

**A training pack.** ReStack is a working toolkit: it does the method and the
bookkeeping, and the architect makes the calls. Skills are not designed to
teach, or measured by how rarely they are needed
([ADR-022](docs/adr/ADR-022-working-toolkit-not-training-pack.md)).

Any new skill has to pass one test: **does it produce something the engagement
uses, to a bar someone can check, while leaving the decisions with the
architect?** A skill that reduces the method to a checklist will be turned down
however useful it looks.

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
3. **A skill idea that fits the theory** — with what it produces and the bar
   that output must meet.

See [Contributing](CONTRIBUTING.md).
