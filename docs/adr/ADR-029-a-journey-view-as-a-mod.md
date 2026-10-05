# ADR-029: The Journey Gets a Read-Only View as a Claude Code Mod, Installed by `setup`; Packaging ReStack as a Plugin Is Parked

**Status:** Proposed. Amends [ADR-010](ADR-010-skills-are-self-contained.md)
on languages.

**Date:** 2026-10-05

**Deciders:** ReStack maintainers

**Technical Story:** Maintainer question, 2026-10-05: does ReStack have a use
for Claude Code [plugins](https://code.claude.com/docs/en/plugins/overview)
and [mods](https://code.claude.com/docs/en/plugins/mods/overview)? The
maintainer then decided to park the plugin install, focus on mods, open
ADR-010's Python rule to TypeScript, and keep mods to usability only.

**Implementation Status:** not started

**Review Date:** 2027-04-05

## Context

### What the architect cannot see

A ReStack engagement runs for weeks, and its state is on disk in
`docs/journey/` ([ADR-023](ADR-023-journey-files-written-by-a-helper.md)).
There are two ways to see it today:

- **Ask Claude.** `/restack-journey where` costs a turn, puts the journey
  files into context, and answers in the transcript, where it scrolls away.
- **Open the files.** `journey-state.md`, `assumptions-register.md` and
  `decisions-log.md` are the record, not a dashboard. The current phase,
  the next command and the open asks are in three files and several
  sections.

So between commands the architect works without knowing where the journey
stands. "What were we doing, and what's open?" is the first question of
almost every session. It costs a turn every time it is asked.

### What a mod is

A mod is a plugin with a JavaScript or TypeScript *hooks module*. Claude
Code loads `.ts` directly, with no Node.js, bundler or build step. The
module runs inside Claude Code and can:

- draw a **band** above the prompt and a **pane** with tabs, buttons and
  text, in the terminal and the Desktop Code tab
- register a **command** that runs the mod's own code with no Claude turn,
  even while Claude is working (`immediate: true`)
- put text in the prompt box as a draft (`$.prompt.fill`) without
  submitting it
- read files (`$.fs.read`), and react to turns ending (`turn.complete`)

It reaches anything outside itself only through the mods API (`$`).
`claude plugin validate` lists every API call a module makes, so what a mod
can do is visible without running it. `claude plugin test` runs a mod's
tests with no session, sign-in or network.

A mod does not draw in the VS Code chat panel, `claude -p` or cloud
sessions. The maintainer does not need those for this, so it is not a
constraint.

### A mod is a plugin, and the plugin install is parked

There are three ways to load a mod:

| Way | Persistent | Needs a marketplace |
|---|---|---|
| `claude plugin install <mod>@<marketplace>` | yes | yes |
| `claude --plugin-dir <dir>` | one session | no |
| `CLAUDE_CODE_PLUGIN_DIRS` in `env` in `~/.claude/settings.json` | yes, terminal and Desktop | no |

The third way loads a directory the same way `--plugin-dir` does, in every
session. The docs give it for "apps you can't pass a flag to", which covers
the Desktop app. It needs no marketplace and no change to how the skills
install.

Packaging all of ReStack as a marketplace plugin was analysed and is
**parked** (decision point 8). It would rename every command
(`/restack-journey` would become `/restack:journey`), break the 32 files
that hard-code `$HOME/.claude/skills/...`, and tie installation to
marketplace policy. A view that is optional does not justify any of that.

### What an organisation can turn off

Under a Team or Enterprise plan, Claude Code loads a built-in guard,
`sec-default`, ahead of every mod a user installs. By default it protects
managed settings and deny rules, and allows everything else. An
organisation can stop a user's mod from loading with:

- `allowManagedModsOnly`
- `disableSideloadFlags`, which rejects `--plugin-dir`. It is expected to
  stop `CLAUDE_CODE_PLUGIN_DIRS` too; the docs do not say.
- `disableAllHooks`

A policy mod can also refuse a mod whose calls include something it blocks.
The docs' own example policy refuses any mod that calls `$.process.run`.

In every one of these cases the mod does not load. Under this decision,
nothing else changes.

## Decision

1. **ADR-010 is amended: a mod is written in TypeScript.** The rules that
   keep a Python helper runnable without an install apply to the mod too,
   translated:
   - **No packages.** A mod imports only its own files and `claude-code`,
     the one bare import Claude Code allows. No `package.json`, no
     `node_modules`, no build step.
   - **It ships in its own directory, `mods/restack-view/`,** and works
     when that directory is the only thing installed. It never sits under
     `skills/`.
   - **Everything a skill runs stays Python and standard library.** A
     skill never calls the mod, and the mod never replaces a helper.
2. **A mod is a view, never a dependency.**
   - No skill, section or preamble fragment names the mod. Every fact it
     shows has a command that gives the same answer: `/restack-journey
     where`, `/restack-journey asks`, `/restack-trace`.
   - A mod that fails to load, or is turned off by policy, changes nothing
     but what is on screen.
   - **It never writes, decides or submits.** The `calls:` line of
     `claude plugin validate` is the contract, and CI fails on any call
     outside this list: `$.fs.read`, `$.fs.stat`, `$.fs.exists`, `$.ui.*`,
     `$.command.register`, `$.prompt.fill`, `$.store.get`, `$.store.set`,
     `$.session.cwd`. It makes no `$.fs.write`, `$.process.*`, `$.http.*`,
     `$.model.*`, `$.prompt.submit` or `$.session.send` calls, and has no
     `tool.call`, `tool.check` or `prompt.submit` hooks.
   - **The mod's own store holds only its preferences**, such as the band
     being hidden. Nothing about the engagement is stored there.
3. **The first mod is `restack-view`, a journey view.**
   - **The band**, one line above the prompt, on by default and shown only
     when the working directory has `docs/journey/journey-state.md`.
     `/restack-view band off` hides it, and the mod remembers that choice
     (O1). It shows terrain, phase,
     confidence, the next command from *Current Position*, and the counts
     of open asks, open assumptions and open decisions. For example:
     `Brownfield · Stressor Analysis · Medium · next: /restack-stressor
     analyze · 9 asks · 14 open · 2 decisions`.
   - **A `/restack-view` command** opens a pane, with `immediate: true` so
     it works mid-turn. It has four tabs: *Position* (Current Position and
     Next Session Prep), *Asks* (open asks by recipient), *Assumptions*
     (open rows) and *Decisions* (open decisions).
   - **One button, "Put the next command in the prompt",** fills the prompt
     box with the next command. The architect reads it and presses Enter.
     The mod never submits.
   - **It reads again when a turn ends** and when the pane opens, comparing
     file modification times. It never polls on a timer.
4. **The mod reads the canonical files itself.** It parses the shape
   `journey.py` writes ([ADR-023](ADR-023-journey-files-written-by-a-helper.md)):
   the bold header fields, the *Current Position* block, the register's
   table and its `## Status lines`, and the decisions log. It does not run
   `journey.py`, so it needs no `$.process` call, which keeps it out of the
   most common policy refusal and keeps the calls a reviewer approves small.
   - **The parser is pinned to the journey fixtures.** The mod's tests read
     `tests/fixtures/journey/`, which `tests/test_journey.py` already runs
     `journey.py` against. A change to the canonical shape that does not
     reach the mod fails a test.
   - **What it cannot read, it does not guess.** A legacy file or an
     unknown shape shows `journey files are not canonical: /restack-journey
     migrate`, and nothing else.
5. **`setup` installs the mod only on request.**
   - `setup --mods` (`.\setup.ps1 -Mods`) copies `mods/restack-view/` to
     `~/.restack/mods/restack-view/`. It then adds that absolute path to
     `env.CLAUDE_CODE_PLUGIN_DIRS` in `~/.claude/settings.json`, keeping
     every other entry and every other setting, and backs the file up
     first. `--dry-run` shows the settings change before anything is
     written.
   - **Once registered, every later `setup` refreshes the copy**, so the mod
     updates with the skills and `/restack-upgrade` needs no change.
     `setup --no-mods` removes the entry and the copy.
   - **The settings edit is done by a standard-library Python helper**,
     `scripts/settings_env.py`, which both setup scripts call. Windows
     PowerShell 5.1 is not trusted to rewrite JSON. Without Python, setup
     prints the line to add by hand and does not edit the file.
   - **This is the only write outside `restack-*`.** It touches one key,
     only entries under `~/.restack/mods/`, only on request, and the tests
     cover it. ADR-011's safety property is extended, not broken (see the
     accounting).
6. **Mods are tested in CI.** The workflow installs the Claude Code CLI, then
   runs:
   - `claude plugin validate --strict --json mods/restack-view`, with a
     check of its `calls:` against decision point 2's list
   - `claude plugin test mods/restack-view`

   The mod's README names the oldest Claude Code version it is tested with.
   That is v2.1.289 at the time of writing, because the event and element
   names it relies on are from that version's reference.
7. **Further mods follow the same rules, and are decided one at a time.**
   Candidates already seen: a trace worklist pane, and the journey-file
   guard. The trace pane would need `$.process.run` or a second parser, so
   it gets its own decision. The guard is enforcement, not usability, so it
   is not a mod under this ADR. If it is built, it is a plain settings hook
   running Python.
8. **Packaging ReStack as a marketplace plugin is parked.** The analysis is
   kept here so it does not have to be redone:
   - Plugin skills are namespaced, `/<plugin>:<skill>`. That is a rename of
     every command, the `Skill` handoffs in `next-command.md`, and its chain
     rule keyed to `/restack-*`.
   - `${CLAUDE_PLUGIN_ROOT}` replaces fixed paths, but only inside a plugin.
     `<base>/../restack-<owner>/scripts/...` would work in both layouts.
   - Auto-update is off by default for third-party marketplaces.
   - Organisations can allowlist marketplaces, and may block a public one.
   - What it would replace: `setup`, `install.json`, the remote half of the
     update check, most of `/restack-upgrade`. What it would add: per-project
     pinning through `enabledPlugins`.

   **Revisit when** a team asks to pin a ReStack version per project, or
   Claude Code offers unnamespaced or aliased plugin skills, or the copy
   install fails in a way a plugin would not.

### Decisions settled by the maintainer, 2026-10-05

| # | Question | Options | Answer |
|---|---|---|---|
| O1 | **Is the band on by default?** | (a) On whenever a journey is present, with `/restack-view band off` remembered in the mod's store. (b) Off until `/restack-view band on`. | **(a).** The band is the point: the state is visible without asking. One line is cheap, and turning it off is one command. |
| O2 | **Does `setup` install the mod by default?** | (a) Only with `--mods`. (b) By default, with `--no-mods` to skip it. | **(a), for now.** It is the first write to `~/.claude/settings.json`, and the first TypeScript. Revisit making it the default after a release of field use. |
| O3 | **Parse in TypeScript, or ask `journey.py`?** | (a) The mod parses the canonical files (decision point 4). (b) Add `journey.py status --json` and have the mod run it with `$.process.run`. | **(a).** One source of truth for the *shape*, pinned by shared fixtures. (b) has one parser, but adds `$.process.run`, which is the call reviewers refuse first. |
| O4 | **Command name** | `/restack-view`, `/rv`, or `/restack` | **`/restack-view`.** It does not collide with a skill and stays in the `restack-` namespace that ADR-009 reserved. |

### Decision-point accounting

| Source | Decision point | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| ADR-010 | A skill works when its directory is the only thing installed | holds, and applies to the mod | A runtime path that was never installed | The mod ships in `mods/restack-view/` and is loaded from its own copy |
| CLAUDE.md, from ADR-010 | Standard library only | holds for Python; **amended**: mods are TypeScript with no packages | A script people skip because it needs an install | Claude Code loads `.ts` itself. Only `claude-code` may be imported. |
| CLAUDE.md, from ADR-010 | Reference scripts by their installed path | holds; the mod is registered by absolute path | A path that resolves only from a checkout | `setup --mods` writes the installed path; the test checks it |
| CLAUDE.md, from ADR-010 | Test what the script does | holds; `claude plugin test` in CI | A check that proves a path exists, not that it works | Same, for the mod |
| ADR-011 | `setup` touches only `restack-*` | **extended**: plus one settings key, its `~/.restack/mods/` entries, on request | `setup` damaging another suite | The edit keeps every other entry and setting, backs up first, shows in `--dry-run`, and is tested |
| ADR-011 | Installation by reference, with consent | holds | Changing every session on an implied instruction | `--mods` is explicit; without it nothing is registered |
| ADR-019 | The install is a copy in the profile | holds | Work in progress leaking into sessions | The mod is a copy in `~/.restack/mods/`. The maintainer tests with `claude --plugin-dir mods/restack-view`. |
| ADR-023 | The journey files are written only by `journey.py` | holds, reinforced | A write that changes a status on the architect's behalf | The mod cannot write: no `$.fs.write` (decision point 2), checked in CI |
| ADR-022 | The architect owns the decisions | holds | A tool making a call the architect answers for | The mod never submits; the button fills the prompt and stops |

## Consequences

### Positive

- The journey's position, next command and open items are on screen all
  session, without a turn and without context spent reading the files.
- A mod that does not load costs nothing. The method, the skills and their
  output are unchanged whether the view is there or not.
- The mod's reach is small and checkable. A security reviewer reads one
  `calls:` line, and CI holds it there.
- The mod is the first non-Python code, so the rules for the next one are
  set before it is written.

### Negative

- **A second parser of the journey files.** The shared fixtures catch
  drift in the shape, but a field `journey.py` adds is invisible to the mod
  until the mod is taught it. Mitigation: the canonical shape changes in
  one PR with the mod's parser, and the fixture test fails if it does not.
- **A second language and test runner.** CI needs the Claude Code CLI.
  The mods API is new, and its events and methods can change between
  Claude Code releases. The tested-version line in the README is the
  warning, and a failing CI run is the alarm.
- **`setup` now edits `~/.claude/settings.json`.** It is opt-in and
  narrow, but it is the first write outside the skills directory, and a
  bug there affects every session.
- **It may not load where ReStack is used most.** An organisation with
  `allowManagedModsOnly` or `disableSideloadFlags` sees nothing. The
  answer there is the organisation's mod channel: a managed directory
  marketplace, which needs the parked packaging work or the mod's own
  marketplace entry.
- **The band reads the files after every turn.** The reads are small and
  check modification times first. The cost is not zero, but it is local
  and quick.

### Neutral

- No skill changes. No command is renamed.
- `/restack-upgrade` needs no change. It runs the clone's `setup`, which
  refreshes the mod when it is registered.
- VS Code chat, `claude -p` and cloud sessions get the skills and no view,
  which is what they have today.

## Knock-on changes

To do in the change that implements this.

| Document | What this decision invalidates | Change |
|---|---|---|
| `mods/restack-view/` | does not exist | new: `.claude-plugin/plugin.json`, `hooks/hooks.json`, `hooks/register.ts`, `tests/*.test.ts`, README |
| `scripts/settings_env.py` | does not exist | new, standard library: add and remove one `CLAUDE_CODE_PLUGIN_DIRS` entry, with a backup |
| `setup`, `setup.ps1` | skills only | `--mods` / `--no-mods` (`-Mods` / `-NoMods`); refresh a registered copy; dry-run output |
| `tests/test_setup.py` | | `--mods`, `--no-mods`, an existing `CLAUDE_CODE_PLUGIN_DIRS` kept, other settings kept, backup written, scratch `HOME` only |
| `.github/workflows/skills.yml` | Python checks only | install the Claude Code CLI; `claude plugin validate` with the calls allowlist; `claude plugin test` |
| `scripts/check_skills.py` | | a mod under `skills/` fails; a `package.json` in `mods/` fails |
| ADR-010 | "standard library only" as the whole language rule | amended-by banner |
| ADR-011 | the safety property's scope | amended-by banner |
| CLAUDE.md | structure, the scripts rules, build commands | `mods/` in the tree; the mod rules beside the script rules; `claude plugin test` |
| INSTALL.md, README.md, QUICKREF.md, GETTING_STARTED.md, CHANGELOG.md | | the view, `setup --mods`, `/restack-view`, what turns it off |

## Alternatives considered

### Package ReStack as a plugin, with the view inside it

- **Pros:** one install; the mod and the skills arrive and update together
  through `/plugin`.
- **Cons:** every command renamed, every fixed path changed, and
  installation tied to marketplace policy, to ship a view that is optional.
- **Why rejected:** parked, with the conditions to revisit it (decision
  point 8).

### Ship the mod through a ReStack marketplace on its own

- **Pros:** uses the official install and update path; the skills stay as
  they are.
- **Cons:** two install mechanisms for one toolkit. A plugin cached by
  version needs a version bump and `claude plugin update` to change, so
  `setup` and `/restack-upgrade` would have to drive Claude Code's plugin
  CLI as well.
- **Why rejected:** `CLAUDE_CODE_PLUGIN_DIRS` loads the copy `setup` already
  maintains, with no second update path. Revisit if sideloading proves
  blocked where ReStack is used, since a marketplace entry is also the
  route into an organisation's managed directory.

### A status line script instead of a mod

- **Pros:** works today with a shell command, no TypeScript.
- **Cons:** the status line is the user's, often already taken by another
  tool, and it is one line with no pane, no tabs and no button. ReStack
  would be overwriting a personal setting.
- **Why rejected:** a mod adds its own band and pane beside whatever the
  user has.

### Run `journey.py` from the mod

- **Pros:** one parser.
- **Cons:** `$.process.run` on every refresh, and the call most policies
  refuse.
- **Why rejected (provisionally, O3):** the shared fixtures give one source
  of truth for the shape without the process call.

### Have the button submit the next command

- **Pros:** one key instead of two.
- **Cons:** a click would start a command chain the architect has not
  read. Chains stop at gates, but the choice to start one is the
  architect's.
- **Why rejected:** filling the prompt costs one Enter and keeps the
  architect the one who runs it.

## References

- [ADR-009](ADR-009-prefix-skill-names.md): the `restack-` prefix
- [ADR-010](ADR-010-skills-are-self-contained.md): skills ship what they run
- [ADR-011](ADR-011-setup-script-and-upgrade-skill.md): setup, its safety
  property, installation by consent
- [ADR-019](ADR-019-copy-only-install.md): the copy-only install
- [ADR-022](ADR-022-working-toolkit-not-training-pack.md): the architect owns
  the decisions
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): the journey files
  and their canonical shape
- Claude Code docs: [mods overview](https://code.claude.com/docs/en/plugins/mods/overview),
  [create](https://code.claude.com/docs/en/plugins/mods/create),
  [interface](https://code.claude.com/docs/en/plugins/mods/interface),
  [API](https://code.claude.com/docs/en/plugins/mods/api),
  [test](https://code.claude.com/docs/en/plugins/mods/test),
  [reference](https://code.claude.com/docs/en/plugins/mods/reference),
  [admin](https://code.claude.com/docs/en/plugins/mods/admin),
  [plugins](https://code.claude.com/docs/en/plugins/overview)
