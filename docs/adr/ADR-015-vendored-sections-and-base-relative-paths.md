# ADR-015: Vendor Shared Sections Into Each Skill, and Write Every Section Path Against `<base>`

**Status:** Accepted

**Date:** 2026-10-02

**Deciders:** ReStack maintainers

**Technical Story:** Field feedback from a full brownfield journey, items 12 and 13

**Implementation Status:** implemented

**Implemented Date:** 2026-10-02

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-02

## Context

Two defects reached a real engagement and were invisible from this repository.

**The outside opinion never ran from an install.** `/restack-stressor` and
`/restack-design-review` told Claude to read `scripts/shared/second-opinion.md`.
`setup` installs `skills/restack-*/` and nothing else
([ADR-011](ADR-011-setup-script-and-upgrade-skill.md)), so that file did not
exist in any copy install. The step did not fail. It was skipped, and nothing
said so. ADR-013 introduced shared sections and noted that the index "renders
the real path". The real path was a path into the checkout.

**Section paths resolved against the wrong root.** The section index said
`skills/restack-design-review/sections/...`. Installed, the file is at
`~/.claude/skills/restack-design-review/sections/...`. The agent had to search
for it, and a Glob from the architect's project returned nothing.

The same class covered nine references to `templates/*.md`, including the
journey-state template `/restack-journey start` creates the journey from.

CI passed throughout. `check_skills.py` verified that every path resolved, but
it resolved them from the repository root, which is the one place they all
work. The check was sound. Its assumption about *where* a path is read from was
not.

## Decision

1. **Every path a skill names to its own files is written `<base>/...`.**
   `<base>` is the skill's base directory, which Claude Code prints when the
   skill loads. The rule is stated once, in a new tier-1 preamble fragment
   (`paths-and-shell.md`), with `~/.claude/skills/<name>` as the fallback.
2. **Shared sections and canonical templates are vendored.** `gen_skills.py`
   writes a generated copy, with a banner, into each consuming skill's
   `sections/`. The source stays single (`scripts/shared/`, `templates/`), and
   the installed skill is self-contained, which is what
   [ADR-010](ADR-010-skills-are-self-contained.md) already required of scripts.
   A manifest entry declares `"shared": true` or `"source": "templates/<file>"`.
3. **`check_skills.py` fails on repo-only paths.** That means any
   `skills/<name>/sections/`, `scripts/shared/`, `templates/` or bare
   `sections/` reference in a skill. It also resolves `<base>/` against the
   skill's own directory, and requires every vendored copy to exist and carry
   its banner. `gen_skills.py --check` catches a vendored copy that has drifted
   from its source.
4. **The install verifies itself.** `setup` and `setup.ps1` check, after
   installing, that every `<base>/sections/` path named in an installed
   `SKILL.md` exists, and they exit non-zero if one does not.
   `/restack-upgrade check` runs the same check against the live install. The
   copy-install change test now compares the whole directory, not just
   `SKILL.md`, so a section edited on its own reaches the install.

## Consequences

### Positive

- Every section a skill names is installed with it, and three independent
  checks would catch a regression: CI, `setup`, and `/restack-upgrade check`.
- The defect class is closed rather than the instance. A future shared section
  or template cannot be referenced in the way that broke this time.
- `templates/` became reachable from an install. That made it possible to give
  the journey files one canonical shape that any agent can append to.

### Negative

- Vendored copies are duplicated text in the repository, for example
  `second-opinion.md` twice. They are generated and bannered, and `--check`
  catches drift, but a contributor can still edit the copy by mistake. The
  banner and `check_skills.py` are the defence.
- `<base>` depends on the harness printing the base directory. Where it does
  not, the fallback is the default install location, which is wrong for a
  `--target` install. That is acceptable: `--target` is rare, and the failure
  is a Read error, not a silent skip.

### Neutral

- Relative Markdown links to ADRs from sections (`../../../docs/adr/...`) are
  citations for human readers on GitHub, not instructions to Claude. They are
  left as they are.

## Alternatives considered

### Make `setup` install `scripts/shared/` and `templates/` too
- **Pros:** No duplication in the repository.
- **Cons:** It recreates a second install root that every skill must locate. It
  breaks ADR-010's self-containment for anyone who copies one skill by hand.
  It also does nothing for the wrong-root problem.
- **Why rejected:** It moves the dependency instead of removing it.

### Inline shared sections into `SKILL.md` with `{{SECTION:<id>}}`
- **Pros:** No extra files, and nothing to locate.
- **Cons:** The method is loaded on every invocation, which is exactly what
  on-demand sections exist to avoid ([ADR-008](ADR-008-generated-skills-with-tiered-preamble.md)).
- **Why rejected:** It pays the context cost on every run to fix an install bug.

## References

- [ADR-010](ADR-010-skills-are-self-contained.md): skills ship their own runtime dependencies
- [ADR-011](ADR-011-setup-script-and-upgrade-skill.md): setup script and upgrade skill
- [ADR-013](ADR-013-outside-opinion.md): the first shared section
