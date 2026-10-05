# ADR-029: ReStack Ships as a Claude Code Plugin From Its Own Marketplace; Mods Are Not Adopted Yet

**Status:** Proposed

**Date:** 2026-10-05

**Deciders:** ReStack maintainers

**Technical Story:** Maintainer question, 2026-10-05: Claude Code now has
plugins and mods ([plugins overview](https://code.claude.com/docs/en/plugins/overview),
[mods overview](https://code.claude.com/docs/en/plugins/mods/overview)). Does
ReStack have a use for them?

**Implementation Status:** not started. Proposed against `main` at 2.16.0,
after [ADR-028](ADR-028-residuals-challenged-by-removal.md) landed.

**Review Date:** 2027-04-05

## Context

ReStack installs and updates itself with code it owns:

- `setup` / `setup.ps1` copy `skills/restack-*/` into `~/.claude/skills`,
  remove skills deleted upstream, refuse a broken tree and write
  `~/.restack/install.json` ([ADR-011](ADR-011-setup-script-and-upgrade-skill.md),
  [ADR-019](ADR-019-copy-only-install.md)).
- `update_check.py` fetches `main` into `~/.restack/upstream.git` once a day
  and prints a notice ([ADR-016](ADR-016-update-awareness.md)).
- `/restack-upgrade` clones the latest release into a temporary directory and
  runs its `setup` ([ADR-019](ADR-019-copy-only-install.md)).
- `local_copies.py` finds old ReStack copies a project or profile still
  carries ([ADR-024](ADR-024-retire-old-skill-copies.md)).

That is two installers kept in step, a cache, a state file and a test suite
(`tests/test_setup.py`, `tests/test_update_check.py`). It all exists because
Claude Code had no package format. Now it has one.

**A plugin** is a directory with `.claude-plugin/plugin.json` and components:
skills, agents, hooks, MCP servers. **A marketplace** is a repository with
`.claude-plugin/marketplace.json` listing plugins. Users add it once, then
install with `/plugin install <plugin>@<marketplace>` or
`claude plugin install`. Claude Code then owns what we built ourselves:

| Ours today | Claude Code's plugin system |
|---|---|
| `setup` copies skills, removes ones deleted upstream | install and update replace the plugin as a unit, in a per-version cache |
| `install.json` records version and source | `claude plugin list` shows version, scope and status |
| `update_check.py` + `upstream.git` | marketplace refresh at session start; auto-update per marketplace |
| `/restack-upgrade` | `/plugin` → **Update now**, `claude plugin update restack@restack` |
| nothing | **project scope**: an engagement repo commits `enabledPlugins` in `.claude/settings.json`, so the whole team gets ReStack |
| nothing | version pinning: `/plugin marketplace add pmelander/restack#v3.0.0` |

Project scope deals with the problem behind ADR-024 at its source. Projects
carried their own stale copies because nothing let a project say "this
engagement uses ReStack" without copying it in.

Four facts about plugins shape this decision:

1. **Plugin skills are namespaced.** A skill runs as `/<plugin>:<skill>`. The
   last segment is the directory name, or the frontmatter `name` if set. With
   no renames, `/restack-journey` becomes `/restack:restack-journey`.
2. **The install path is not fixed.** Each version is cached in its own
   directory. Skills reach bundled files through `${CLAUDE_PLUGIN_ROOT}`,
   which is substituted in skill content, but only in a plugin. Every
   `$HOME/.claude/skills/restack-*/...` reference breaks under a plugin
   install. At 2.16.0 that is 8 source files (5 templates,
   `journey-files.md`, `trace.md`, `update-check.md`) rendering into 32
   generated and vendored files.
3. **Auto-update is off by default for third-party marketplaces.** Each user
   turns it on once, in `/plugin` → **Marketplaces**.
4. **Organisations can restrict marketplaces** through managed settings:
   allowlist, block, force-install. A public GitHub marketplace may be
   blocked where ReStack is used. The same plugin can be listed in an
   organisation's own marketplace or its claude.ai plugin library, which
   then syncs it to members.

**Mods** are plugins with a JavaScript or TypeScript hooks module. A mod runs
inside Claude Code and can draw a pane or a band above the prompt, add a
command that runs without a Claude turn, and hold, rewrite or answer a tool
call. It is not sandboxed and runs as the user. It draws only in the terminal
and the Desktop Code tab, not in the VS Code chat panel, `claude -p` or cloud
sessions. `disableAllHooks`, `--safe-mode` and an organisation's
`allowManagedModsOnly` turn it off, while the rest of the plugin keeps
loading.

## Decision

1. **ReStack ships as one plugin, `restack`, from a marketplace in this
   repository.** `.claude-plugin/marketplace.json` and
   `.claude-plugin/plugin.json` live at the repository root. The plugin root
   is the repository root, so `skills/restack-*/` is found where it already
   is. The install is
   `claude plugin marketplace add pmelander/restack` and then
   `claude plugin install restack@restack`. Releases are the existing
   `vX.Y.Z` tags, so a team can pin one.
2. **Script references are layout-neutral, and this is the first change
   made.** Every helper is reached from the skill's own base directory,
   `<base>/../restack-<owner>/scripts/<file>.py`, as sections already are
   ([ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md)). The
   skills sit side by side in both layouts, so the path resolves in the copy
   install and in the plugin cache alike. `check_skills.py` learns the form
   and resolves it against `skills/`. This changes nothing users see, and it
   ships in 2.x, before any of the rest.
3. **`plugin.json`'s `version` is `VERSION`.** `gen_skills.py` writes it, and
   `--check` fails on drift, as it does for `SKILL.md`.
4. **Project scope is documented as the way to use ReStack on an
   engagement.** INSTALL.md shows the `enabledPlugins` entry and how to pin
   a release. `local_copies.py` and `retire-local` stay. A project can still
   carry old copies, and Claude Code still loads them beside the plugin.
5. **The update notice is retired, and the local-copies line stays.**
   INSTALL.md tells users to turn on auto-update for the `restack`
   marketplace. The remote fetch, the `upstream.git` cache, the throttle and
   the "update available" line are removed from `update_check.py`. The
   session-open check keeps its one local, offline job from ADR-024: reporting
   old copies in the project and the profile, once a day, under the same
   opt-out in `~/.restack/config.json`.
6. **The copy install is migrated by moving, never deleting.** The last 2.x
   release adds `/restack-upgrade migrate-plugin`. It lists the copy install,
   shows a dry run and **stops on a brief**. On yes, it moves
   `~/.claude/skills/restack-*` to `~/.claude/skills-retired-<date>/`, the
   same way `retire-local` does (ADR-024), and prints the two install
   commands. It does not run them. Installing a plugin changes every future
   session, so the user runs those commands (ADR-011, "installation by
   reference, with consent").
7. **Mods are not adopted in this decision.** Nothing in the method may
   depend on a mod. A mod draws in only two places and can be switched off
   by settings that leave the rest of the plugin running. Two candidates are
   recorded for later decisions, in this order:
   - **A guard on the journey files.** Hold a hand `Edit`/`Write` to
     `docs/journey/*.md` and point it at `journey.py`. That turns the
     ADR-023 contract from a request into a rule. It is a **plain plugin
     hook running a standard-library Python script**, not a mod, so ADR-010
     holds unchanged.
   - **A journey band and a `where` that needs no Claude turn.** Show
     position, the current gate, open asks and the last matrix total, read
     from `docs/journey/`. This one needs a mod. It must fall back to the
     existing `/restack-journey where` wherever nothing draws, and it is
     spiked only after decision points 1 to 6 have shipped.

### Decisions still open

These are the maintainer's calls. Each one changes what is built.

| # | Question | Options | Recommendation |
|---|---|---|---|
| O1 | **Command names** | (a) `/restack:journey`: frontmatter `name` drops the prefix, and the namespace takes over ADR-009's job. (b) `/restack:restack-journey`: no rename. | **(a).** The namespace prevents the collision ADR-009 guarded against, and (b) is the name typed every day. But (a) means one `SKILL.md` cannot serve both installs: in a copy install, `name: journey` would be `/journey` again, the exact ADR-009 collision. So (a) needs O2 settled first. |
| O2 | **Does `setup` stay?** | (a) Retire `setup` and the copy install in 3.0. (b) Keep both installs, with `gen_skills.py` rendering a copy-install variant. (c) Keep `setup` for one minor release, migration only. | **(a)**, with an organisation-mirror path in INSTALL.md for marketplaces that are blocked (Context, fact 4). (b) doubles the build forever for a case a mirror covers. Before deciding, check at least one restricted organisation's managed plugin policy. |
| O3 | **`claude plugin validate` in CI** | (a) Install the Claude Code CLI in the workflow and validate on every push. (b) Validate locally before a release, recorded in the release checklist. | **(b)** until the CLI is cheap to install in CI. `check_skills.py` already covers what we write. `validate` covers what Claude Code reads. |

### Decision-point accounting

ADR-011 and ADR-019 are superseded on the points below. ADR-016 is
superseded, and ADR-024 holds.

| Source | Decision point | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| ADR-009 | Every skill is named `restack-*` | depends on O1 | Overwriting another suite's skill in a flat namespace | Plugin namespace `restack:` (O1a), or the prefix stays (O1b) |
| ADR-011 | `setup` owns installation | replaced | Lossy `cp -R` installs | Claude Code installs the plugin as a unit |
| ADR-011 | Remove skills deleted upstream | replaced | A removed command lingering | An update replaces the plugin directory as a whole |
| ADR-011 | Refuse a broken tree | replaced | A skill with no `SKILL.md`, silently ignored | `check_skills.py` in CI, and `claude plugin validate` (O3) |
| ADR-011 | Only `restack-*` is ever touched | moot | `setup` deleting another suite | ReStack writes nothing into the skills directory. Claude Code owns the plugin cache. `migrate-plugin` touches `restack-*` only. |
| ADR-011 | Installation by reference, with consent | holds | An agent installing skills on an implied instruction | `migrate-plugin` prints the commands and never runs them |
| ADR-016 | Daily update notice | withdrawn | Running stale skills unaware | Marketplace auto-update, turned on per INSTALL.md. **Accepted gap:** a user who leaves it off gets no notice. |
| ADR-016 | Silence offline, opt-out, once a day | holds, for the local-copies line | An optional notice erroring or nagging at session open | Same, and the check no longer touches the network |
| ADR-019 | Install is a copy in the profile | replaced by the plugin cache | Work in progress leaking into sessions; symlink privileges | A plugin install is a copy too. The maintainer tests with `claude --plugin-dir .` per session, which is explicit, like `./setup` was. |
| ADR-019 | Install independent of any checkout | holds | Deleting the clone breaking the install | The plugin cache is independent of any clone |
| ADR-019 | Upgrade from a temporary clone | replaced | Upgrades touching a checkout | Claude Code fetches the marketplace itself |
| ADR-024 | Report and retire old copies by moving | holds | A stale copy answering in place of the install | Unchanged. Project scope also removes the reason copies were made. |

## Consequences

### Positive

- About 550 lines of installer in two shells (`setup`, `setup.ps1`), the remote half of
  `update_check.py`, a cache, a state file and most of two test suites go.
  They were maintained to do what Claude Code now does.
- An engagement repository can declare ReStack and pin its version, so a
  team works from one version and a project stops needing its own copy.
- Install, update and disable go through the same `/plugin` UI and
  organisational controls as every other plugin, including managed
  allowlists and the claude.ai organisation library.
- Decision point 2 ships on its own and fixes a latent fragility: helpers
  stop depending on where the profile lives, which also covers the
  `CLAUDE_CONFIG_DIR` gap ADR-019 accepted.

### Negative

- **Breaking change.** If O1 is (a), every command is renamed, the
  `Skill` handoffs in `next-command.md` change, and every document,
  trigger and example that names a command is touched. It is a 3.0.
- **`next-command.md`'s chain rule is keyed to the prefix.** "A chain never
  runs anything outside `/restack-*`" has to be re-keyed to the `restack:`
  namespace in the same change, or chains stop running ReStack commands.
- **Auto-update is opt-in for us.** Third-party marketplaces default to off,
  so some users will run old versions with no notice (accounting, ADR-016).
- **Running both installs at once loads duplicates** until the copy install
  is migrated. Decision point 6 exists for this, but a user who installs the
  plugin without running it gets the ADR-024 failure in the profile.
- **Dependence on Claude Code's plugin system.** A change to its namespace
  rules, cache layout or marketplace format is now our breakage, outside our
  tests.

### Neutral

- Skills, sections, preamble tiers and `gen_skills.py` are unchanged in
  shape. Plugin skills are `SKILL.md` files under `skills/<name>/`, as ours
  already are.
- Context cost does not change: each skill's description is in context
  either way.
- Cloud sessions load neither a copy install nor a locally installed
  plugin. Neither is a regression.
- `~/.restack/` stays for configuration. Nothing moves to
  `${CLAUDE_PLUGIN_DATA}`, because ReStack keeps no state a version needs to
  carry forward.

## Knock-on changes

To do in the change that implements this, after ADR-028 lands. The command
renames assume O1 (a).

| Document | What this decision invalidates | Change |
|---|---|---|
| `.claude-plugin/marketplace.json`, `.claude-plugin/plugin.json` | do not exist | new; `version` written by `gen_skills.py` |
| `scripts/preamble/journey-files.md`, `scripts/shared/trace.md`, `scripts/shared/update-check.md`, 5 templates | `$HOME/.claude/skills/...` helper paths | `<base>/../restack-<owner>/...` (decision point 2, ships first) |
| `scripts/check_skills.py` | `INSTALLED_PREFIXES` only | resolve the base-relative form; with O1 (a), check frontmatter `name` |
| `scripts/preamble/next-command.md` | `/restack-*` command form and chain rule | `/restack:<skill>`; rule re-keyed to the namespace |
| every `SKILL.md.tmpl` | `name: restack-<x>`, triggers | with O1 (a): `name: <x>` |
| `skills/restack-upgrade/` | upgrade from a clone, remote update check | `migrate-plugin`; `check` and `retire-local` stay; the remote fetch goes |
| `scripts/shared/update-check.md`, `skills/restack-journey/`, `skills/restack-discover/` | session-open update notice | the update line goes; the local-copies line stays |
| `setup`, `setup.ps1`, `tests/test_setup.py`, `tests/test_update_check.py` | the copy install | per O2 |
| ADR-009, ADR-011, ADR-016, ADR-019 | as accounted above | superseded-by banners |
| INSTALL.md, README.md, QUICKREF.md, GETTING_STARTED.md, CLAUDE.md, CHANGELOG.md | install, upgrade and command names | rewritten; project-scope and organisation-mirror sections in INSTALL.md |

## Alternatives considered

### Stay with `setup` and the copy install

- **Pros:** no breaking change; everything we own stays tested and
  understood.
- **Cons:** we keep maintaining an installer, an updater and a cache that
  duplicate the platform's, and there is still no way for a project to
  declare ReStack.
- **Why rejected:** ADR-011 built `setup` because no package format
  existed. That reason is gone.

### Ship both a plugin and the copy install, indefinitely

- **Pros:** works wherever marketplaces are blocked, without a mirror.
- **Cons:** two renderings of every skill if commands are renamed (O1),
  two install paths to test, and duplicate skills for anyone who has both.
- **Why rejected (provisionally, pending O2):** an organisation that blocks
  third-party marketplaces can list the same plugin in its own. That costs
  one mirror, not a second build forever.

### One plugin per skill

- **Pros:** users install only what they use.
- **Cons:** the skills call each other's helpers (`journey.py` from every
  tier 2 and 3 skill, `trace.py` from four, `matrix.py` from
  `/restack-journey` since ADR-028) and hand off through
  `next-command.md`. Split them and every dependency becomes a declared
  cross-plugin dependency.
- **Why rejected:** ReStack is one method. ADR-022 calls it a working
  toolkit, and it installs as one unit.

### Build the journey band as a mod now

- **Pros:** "where am I" without a turn, visible all session.
- **Cons:** JavaScript and a new test stack, before the packaging it rides
  on exists. Users in VS Code and `claude -p` would not see it.
- **Why rejected:** sequenced after packaging (decision point 7), not ruled
  out.

## References

- [ADR-009](ADR-009-prefix-skill-names.md): the `restack-` prefix
- [ADR-010](ADR-010-skills-are-self-contained.md): skills ship what they run;
  standard library only
- [ADR-011](ADR-011-setup-script-and-upgrade-skill.md): setup and the upgrade
  skill
- [ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md):
  base-relative paths
- [ADR-016](ADR-016-update-awareness.md): the update notice
- [ADR-019](ADR-019-copy-only-install.md): the copy-only install
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): the journey files
  are written by a helper
- [ADR-024](ADR-024-retire-old-skill-copies.md): retiring old copies by moving
- Claude Code docs: [plugins](https://code.claude.com/docs/en/plugins/overview),
  [install and update](https://code.claude.com/docs/en/plugins/install),
  [components and path variables](https://code.claude.com/docs/en/plugins/components),
  [mods](https://code.claude.com/docs/en/plugins/mods/overview)
