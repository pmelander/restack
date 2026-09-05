# ADR-009: Prefix Every Skill Name with `restack-`

**Status:** Accepted

**Date:** 2026-09-05

**Deciders:** ReStack maintainers

**Technical Story:** Name collision with other Claude Code skill suites

**Implementation Status:** implemented

**Implemented Date:** 2026-09-05

**Implemented By:** ReStack maintainers

**Review Date:** 2027-03-05

## Context

Claude Code resolves a skill by its directory name: `~/.claude/skills/<name>/SKILL.md`
becomes the command `/<name>`. The namespace is flat and global, and exactly one
directory can own a name.

Our documented install was `cp -R skills/* ~/.claude/skills/`, which took the
name `design-review` — and gstack, a widely used skill suite, ships a
`design-review` too. On a machine with both installed, the copy overwrote
gstack's skill. No warning, no error; the user simply has one fewer skill than
they think, and the one that answers `/design-review` is not the one they
expect.

`design-review` was the only collision against gstack specifically, but it is
not a special case. `review`, `patterns`, `evolve`, `discover` and `health` are
all names a reasonable suite would claim, and the collision surface grows with
every suite a user installs. Shipping a public toolkit that can silently delete
part of someone else's is not acceptable regardless of how many names collide
today.

Three options were considered:

1. **Rename only the colliding skill.** Cheapest, and wrong for the same reason
   patching one symptom is usually wrong — it fixes today's collision and
   leaves the mechanism in place.
2. **A router skill** — one `/restack` command dispatching to sub-skills. One
   name claimed, which is minimal and tidy. But it costs a level of indirection
   on every invocation, obscures the skills from `/` autocomplete (the main way
   people discover what a suite can do), and the router file becomes a
   bottleneck every skill change has to touch.
3. **Prefix every skill.** Verbose, and it changes every command name in the
   documentation.

## Decision

**Prefix every skill directory with `restack-`.** `skills/design-review/`
becomes `skills/restack-design-review/`, invoked as `/restack-design-review`.

The prefix is applied to the **directory name in the repository**, not at
install time. The folder name and the command are therefore always the same
string. This matters more than it first appears:

- `cp -R skills/* ~/.claude/skills/` needs no renaming logic and stays a
  one-liner.
- The symlink development method keeps working — symlinking
  `skills/restack-adr` yields `/restack-adr`, so a developer's local commands
  match the documentation.
- There is no second naming scheme to hold in your head, and no way for the
  installed name and the documented name to drift apart.

Typing cost is real — `/restack-capability-assessor` is not short — but `/re`
plus autocomplete reaches any of them, and grouping the whole suite under one
prefix in the `/` menu is a discovery benefit that partly repays the verbosity.

## Consequences

**Positive**

- ReStack can no longer overwrite another suite's skill, today or as either
  suite grows.
- The suite is visible as a group: typing `/restack` lists all fourteen.
- Folder name, command name, and documentation agree by construction.

**Negative**

- Every command in every document changed — 1,076 command references and 99
  path references across 59 files. Applied mechanically with two narrow rules
  (a `skills/<name>` path rule and a `/<name>` token rule with lookarounds), so
  that document paths like `docs/adr/`, `docs/journey/` and
  `docs/stressor-analysis/` were not rewritten. Twelve edge cases were tested
  before applying.
- Existing users with an unprefixed install have orphaned duplicates. The
  installation guide carries a migration note, deliberately printing each
  skill's header rather than deleting anything, since an unprefixed
  `design-review` may belong to a suite the user still wants.
- Commands are longer to type.

**Neutral**

- The `name:` field in converted skills' frontmatter now carries the prefix
  too, so it matches the directory. `check_skills.py` would surface a mismatch
  if one were introduced.

## Alternatives revisited

If the prefix proves genuinely irritating in daily use, the router option
remains available and is not blocked by this decision — a `/restack` router
could be added later alongside the prefixed skills, giving both entry points.
The reverse migration (router first, prefixes later) would be harder, because
users would already have muscle memory for a dispatch syntax.
