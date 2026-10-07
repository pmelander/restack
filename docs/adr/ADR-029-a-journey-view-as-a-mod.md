# ADR-029: The Journey Gets a Read-Only View as a Claude Code Mod, Installed by `setup`; Packaging ReStack as a Plugin Is Parked

**Status:** Accepted. Amends [ADR-010](ADR-010-skills-are-self-contained.md)
on languages.

**Date:** 2026-10-05

**Deciders:** ReStack maintainers

**Technical Story:** Maintainer question, 2026-10-05: does ReStack have a use
for Claude Code [plugins](https://code.claude.com/docs/en/plugins/overview)
and [mods](https://code.claude.com/docs/en/plugins/mods/overview)? The
maintainer then decided to park the plugin install, focus on mods, open
ADR-010's Python rule to TypeScript, and keep mods to usability only.

**Implementation Status:** implemented on `feature/restack-mods-adr`: the
band and `/restack-view band [on|off]`, the pane and its button,
`scripts/check_mods.py` and the CI job, `setup --mods` / `--no-mods` in both
installers, and `local_copies.py` skipping an installed mod. Open: a session
started in a subdirectory of the project does not find its journey (decision
point 3), and the CI job has not yet run.

**Accepted:** 2026-10-05, by the maintainer

**Review Date:** 2027-04-05

> **Amended 2026-10-07 by [ADR-032](ADR-032-a-stale-position-says-so.md).**
> The band's next command is the one Current Position records, unless the
> position is stale (its move has run, or a decision was answered after it).
> Then the band reads `position stale since <date> · next /restack-journey
> where`, and the pane's button fills `where`. `journey.py check` gives the
> same answer.

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

There are four ways to load a mod:

| Way | Id | Persistent | Needs |
|---|---|---|---|
| `claude plugin install <mod>@<marketplace>` | `<name>@<marketplace>` | yes | a marketplace |
| `claude --plugin-dir <dir>` | `<name>@inline` | one session | a flag |
| `CLAUDE_CODE_PLUGIN_DIRS` in `env` in `~/.claude/settings.json` | `<name>@inline` | yes | a settings edit |
| a plugin directory saved under `~/.claude/skills/` | `<name>@skills-dir` | yes | nothing else |

The fourth way is the one ReStack already uses for its skills. A directory
under `~/.claude/skills/` that has `.claude-plugin/plugin.json` loads as a
plugin, in place, in every session, in the terminal and the Desktop app. It
is on unless its manifest sets `defaultEnabled: false` or a settings file
sets `"<name>@skills-dir": false`. It needs no marketplace, no settings edit
and no change to how the skills install.

### A working example: `headroom`

The maintainer's own `headroom` mod is installed exactly this way, in
`~/.claude/skills/headroom/`. It is not part of ReStack. It draws the context
window, rate limits and cost above the prompt, and it has the shape a band
mod should have:

- **TSX.** The module is `hooks/register.tsx`. Elements come from
  `$.ui.resolve(e)` and are written as JSX, typed with `Register` and
  `EngineInterface` from `claude-code`.
- **Typed state.** `types/index.d.ts`, named by `types` in the manifest,
  declares the data shapes and the `PluginState` atoms. `tsconfig.json`
  extends the declarations Claude Code generates into
  `.claude-plugin/types/`, which is git-ignored.
- **Refresh outside the render.** `refresh()` builds a snapshot and writes
  it to a `$.state` atom, behind a re-entrancy guard. The `ui.render` hook
  only reads it, so a write redraws without `$.ui.invalidate`. Refresh runs
  on `session.measure`, which fires after each turn. A few `$.clock.after`
  retries cover a session whose first data is not ready yet.
- **A toggle that persists.** `/headroom [on|off]` toggles with no argument,
  prints usage on a bad one, and keeps the choice in `$.store`, restored at
  `session.start`.
- **A band that steps aside.** It returns `next(e)` while a survey is up,
  when it is off, and when it has nothing to show. It drops rows in
  priority order to fit `e.props.maxRows`. It draws a padded monospace line
  in the terminal and fixed `Box` columns on the Desktop's proportional
  font.
- **Tests per surface.** The same tests run for `terminal` and `desktop`,
  with `mock.store`, `mock.clock` at a fixed time, the data call stubbed,
  and the drawn tree read as text. One test checks what is dropped when only
  one row fits.

It also shows two gaps a second band mod must not repeat:

- **It replaces the band rather than sharing it.** A tree returned from
  `AbovePrompt` replaces what the mods after it draw. To share the band, a
  mod puts `await next(e)` among its own children. With two band mods
  installed and neither composing, only one shows, depending on load order.
- **It loses its state after `/clear`.** `/clear`, `/resume` and `/branch`
  reset every `$.state` value, and `session.start` does not fire again. The
  stored "off" is forgotten until the next session. The fix the docs give
  is a `classic.SessionStart` hook filtered on `source: clear | resume |
  fork` that reloads from `$.store`.

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
- a marketplace allowlist that does not include `skills-dir`, which stops
  plugins saved under `~/.claude/skills/` from loading
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
     when that directory is the only thing installed. In this repository it
     never sits under `skills/`, which is for `SKILL.md` skills. Installed,
     it sits beside them.
   - **It follows `headroom`'s shape:** a `.tsx` hooks module, a
     `types/index.d.ts` named in the manifest, a `tsconfig.json` extending
     the generated declarations, and `.claude-plugin/types/` git-ignored.
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
     outside this list: `$.fs.read`, `$.fs.stat`, `$.fs.exists`,
     `$.fs.ancestors`, `$.fs.list` (added by ADR-030), `$.ui.*`, `$.command.register`, `$.prompt.read`,
     `$.prompt.fill`, `$.store.get`, `$.store.set`, `$.session.root`,
     `$.session.cwd`, `$.session.surfaces`, `$.clock.after`, `$.clock.now`, and its own `$.state`
     atoms. It makes no `$.fs.write`, `$.process.*`, `$.http.*`,
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
     it works mid-turn. Where no surface draws a pane (`$.session.surfaces()`
     has no `terminal` or `desktop`: a `-p` run, the VS Code chat panel), it
     prints the band's line instead. A `-p` run reports every pane as
     placed, so `isPlaced` cannot tell. It has four tabs: *Position* (Current Position and
     Next Session Prep), *Asks* (open asks by recipient), *Assumptions*
     (open rows) and *Decisions* (open decisions).
   - **One button, "Put the next command in the prompt",** fills the prompt
     box with the next command and leaves the pane open (amended: closing
     it lost the view the architect was reading). The pane is opened again
     without `closeOnEscape`, so Esc hands the keys to the prompt and the
     pane stays. The architect reads it and presses Enter. The mod never
     submits. **It never overwrites a draft:** it reads the prompt first
     (`$.prompt.read`), and if anything is typed there it shows a toast with
     the command instead.
   - **The button lives in the pane, not the band.** A digit hotkey on a
     band button fires when that digit is typed alone into an empty prompt,
     so the band carries text only.
   - **It finds the journey from the project root.** It looks for
     `docs/journey/` under `$.session.root`, then under `$.session.cwd`.
     The types define the root as where the session started, or where `/cd`
     took it, so **a session started in a subdirectory of the project does
     not find its journey yet.** Walking up with `$.fs.ancestors` is to be
     checked in the pane slice: it is declared for instruction files, and
     whether it takes `docs/journey/journey-state.md` is not documented.
   - **The pane shows rows, not files.** A `Text` or `Markdown` element
     holds at most 10,000 characters. Each tab lists its rows up to that
     budget, then ends with `… N more: /restack-journey asks` (or `where`).
   - **It reads again after each turn** (`session.measure`) and when the
     pane opens, comparing file modification times first. The snapshot goes
     into a `$.state` atom, and the render only reads it. It never polls;
     the only timers are `headroom`'s few warm-up retries at session start.
   - **It shares the band.** Its tree includes `await next(e)`, so a band
     mod such as `headroom` still draws. It steps aside while a survey is up,
     and returns `next(e)` alone when it is off or there is no journey.
   - **It survives `/clear`.** A `classic.SessionStart` hook on `clear`,
     `resume` and `fork` reloads the band preference and the snapshot.
4. **The mod reads the canonical files itself.** It parses the shape
   `journey.py` writes ([ADR-023](ADR-023-journey-files-written-by-a-helper.md)):
   the bold header fields, the *Current Position* block, the register's
   table and its `## Status lines`, and the decisions log. It does not run
   `journey.py`, so it needs no `$.process` call, which keeps it out of the
   most common policy refusal and keeps the calls a reviewer approves small.
   - **The parser is pinned to the journey fixtures.** A mod test cannot
     read files itself: a stub answers `$.fs.read`, as `headroom`'s test
     stubs its data call. So `gen_skills.py` renders
     `tests/fixtures/journey/` into `mods/restack-view/tests/fixtures.ts`,
     and `--check` fails on drift. These are the same files
     `tests/test_journey.py` runs `journey.py` against. A change to the
     canonical shape that does not reach the mod fails a test.
   - **What it cannot read, it does not guess.** A legacy file or an
     unknown shape shows `journey files are not canonical: /restack-journey
     migrate`, and nothing else.
   - **The header fields are free text, and the band says so briefly.**
     `journey.py` fixes the files' structure, not what a field says, and a
     long engagement writes sentences. The first live run showed a terrain
     sentence filling the whole band. So the terrain shows the template's
     terms in the order the field names them (`Greenfield/Brownfield`), and
     any other field shows its first clause, capped at 32 characters. The
     header is read above the first `##` only, so a `Previous phase line`
     is never the phase. A label may carry a qualifier
     (`**Current Phase (2026-10-03):**`). The next move and the confidence
     come from the newest Current Position subsection only, and the next
     move is read from `What's next` or `Next move`. The `lived` fixture
     holds all of this, including a superseded subsection whose
     `What's next` must not be read.
5. **`setup` installs the mod only on request, as a skills-directory
   plugin.**
   - `setup --mods` (`.\setup.ps1 -Mods`) copies `mods/restack-view/` to
     `~/.claude/skills/restack-view/`, where it loads as
     `restack-view@skills-dir`. That is the directory and prefix `setup`
     already owns, so nothing outside `restack-*` is written, and no
     settings file is touched.
   - **Once installed, every later `setup` refreshes the copy**, so the mod
     updates with the skills and `/restack-upgrade` needs no change.
     `setup --no-mods` removes it.
   - **`setup` must know it is a mod, not a skill.** Its "refuse a broken
     tree" check expects `SKILL.md`, and its "removed upstream" loop deletes
     any `restack-*` folder missing from `skills/`. Both learn that a
     `restack-*` folder holding `.claude-plugin/plugin.json` and present in
     `mods/` is a mod. `local_copies.py` learns the same, so ADR-024 never
     reports it as an old copy.
   - **Developing it does not touch the install.** The maintainer runs
     `claude --plugin-dir mods/restack-view`, whose `@inline` copy takes
     precedence over the installed `@skills-dir` one for that session.
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

### The mods API this relies on

Checked against the [mods reference](https://code.claude.com/docs/en/plugins/mods/reference),
which documents v2.1.289. Mods themselves need v2.1.287. When the docs and
the declarations Claude Code generates for the installed version disagree,
the declarations win, and this table is corrected.

| Kind | Used | For |
|---|---|---|
| Events | `session.start` | register `/restack-view`, restore the band preference, first read |
| | `session.measure` | re-read after each turn |
| | `classic.SessionStart` `{ source: clear \| resume \| fork }` | reload after `/clear`, `/resume`, `/branch` |
| | `command.run` `{ command: 'restack-view' }` | open the pane; `band on \| off` |
| | `ui.render` `{ component: 'AbovePrompt' }`, `{ component: 'Pane' }` | the band and the pane |
| Render-site props | `hasSurvey`, `maxRows`, `bodyColumns` (band); `requestId`, `bodyColumns`, `placement`, `scroll` (pane) | stepping aside, fitting the space |
| Elements | `Box`, `Text`, `Button`, `Markdown` | all available in the terminal and on the Desktop |
| Methods | the allowlist in decision point 2 | |
| Command option | `immediate: true` | `/restack-view` works mid-turn |
| Limits | 10 s per hook; 10,000 characters per `Text` or `Markdown`; 4 MiB per `$.fs.read`; redraws throttled to 10 a second | the reads are bounded, the pane is budgeted, refresh is per turn |

### Decisions settled by the maintainer, 2026-10-05

| # | Question | Options | Answer |
|---|---|---|---|
| O1 | **Is the band on by default?** | (a) On whenever a journey is present, with `/restack-view band off` remembered in the mod's store. (b) Off until `/restack-view band on`. | **(a).** The band is the point: the state is visible without asking. One line is cheap, and turning it off is one command. |
| O2 | **Does `setup` install the mod by default?** | (a) Only with `--mods`. (b) By default, with `--no-mods` to skip it. | **(a), for now.** It is ReStack's first TypeScript, and the first code that runs inside Claude Code. Revisit making it the default after a release of field use. |
| O3 | **Parse in TypeScript, or ask `journey.py`?** | (a) The mod parses the canonical files (decision point 4). (b) Add `journey.py status --json` and have the mod run it with `$.process.run`. | **(a).** One source of truth for the *shape*, pinned by shared fixtures. (b) has one parser, but adds `$.process.run`, which is the call reviewers refuse first. |
| O4 | **Command name** | `/restack-view`, `/rv`, or `/restack` | **`/restack-view`.** It does not collide with a skill and stays in the `restack-` namespace that ADR-009 reserved. |

### Decision-point accounting

| Source | Decision point | Now | What failure did it prevent? | What prevents it now? |
|---|---|---|---|---|
| ADR-010 | A skill works when its directory is the only thing installed | holds, and applies to the mod | A runtime path that was never installed | The mod ships in `mods/restack-view/` and is loaded from its own copy |
| CLAUDE.md, from ADR-010 | Standard library only | holds for Python; **amended**: mods are TypeScript with no packages | A script people skip because it needs an install | Claude Code loads `.ts` itself. Only `claude-code` may be imported. |
| CLAUDE.md, from ADR-010 | Reference scripts by their installed path | holds; the mod references nothing outside itself | A path that resolves only from a checkout | Claude Code finds the mod in `~/.claude/skills/`. Its module imports only its own files. |
| CLAUDE.md, from ADR-010 | Test what the script does | holds; `claude plugin test` in CI | A check that proves a path exists, not that it works | Same, for the mod |
| ADR-011 | `setup` touches only `restack-*` | holds | `setup` damaging another suite | The mod installs as `~/.claude/skills/restack-view/`, inside the prefix. No settings file is written. |
| ADR-011 | Refuse a broken tree; remove skills deleted upstream | holds, taught about mods | Installing a skill Claude Code ignores; a command lingering | A `restack-*` folder from `mods/` with a manifest is a mod, not a broken skill, and is removed only by `--no-mods` or when it leaves `mods/` |
| ADR-011 | Installation by reference, with consent | holds | Changing every session on an implied instruction | `--mods` is explicit; without it nothing is copied |
| ADR-019 | The install is a copy in the profile | holds | Work in progress leaking into sessions | The mod is a copy in `~/.claude/skills/`. The maintainer tests with `claude --plugin-dir mods/restack-view`. |
| ADR-024 | Report and retire old ReStack copies | holds | A stale copy answering in place of the install | `local_copies.py` recognises the installed mod, so it is never reported as an old copy |
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
- **`setup` has a second kind of thing to manage.** Its tree check, its
  "removed upstream" loop and `local_copies.py` all treat a `restack-*`
  folder as a skill today. A mistake there could delete the mod, or report
  it as stale.
- **It may not load where ReStack is used most.** An organisation with
  `allowManagedModsOnly`, or a marketplace allowlist without `skills-dir`,
  sees nothing. The answer there is the organisation's mod channel: a
  managed directory marketplace, which needs the parked packaging work or
  the mod's own marketplace entry.
- **The band reads the files after every turn.** The reads are small and
  check modification times first. The cost is not zero, but it is local
  and quick.

### Neutral

- No skill changes. No command is renamed.
- `/restack-upgrade` needs no change. It runs the clone's `setup`, which
  refreshes the mod when it is installed.
- VS Code chat, `claude -p` and cloud sessions get the skills and no view,
  which is what they have today.

## Knock-on changes

To do in the change that implements this.

| Document | What this decision invalidates | Change |
|---|---|---|
| `mods/restack-view/` | does not exist | new: `.claude-plugin/plugin.json`, `hooks/hooks.json`, `hooks/register.tsx`, `types/index.d.ts`, `tsconfig.json`, `tests/*.test.ts`, `.gitignore` for `.claude-plugin/types/`, README |
| `scripts/gen_skills.py` | renders skills only | renders `tests/fixtures/journey/` into `mods/restack-view/tests/fixtures.ts`; `--check` covers it |
| `setup`, `setup.ps1` | skills only | `--mods` / `--no-mods` (`-Mods` / `-NoMods`); refresh an installed mod; the tree check and the "removed upstream" loop recognise a mod; dry-run output |
| `skills/restack-upgrade/scripts/local_copies.py` | every `restack-*` folder is a skill | the installed mod is not an old copy |
| `tests/test_setup.py`, `tests/test_local_copies.py` | | `--mods`, `--no-mods`, a plain `setup` keeping and refreshing an installed mod, a mod never reported as an old copy, scratch `HOME` only |
| `.github/workflows/skills.yml` | Python checks only | install the Claude Code CLI; `claude plugin validate` with the calls allowlist; `claude plugin test` |
| `scripts/check_skills.py` | | a mod under `skills/` fails; a `package.json` in `mods/` fails |
| ADR-010 | "standard library only" as the whole language rule | amended-by banner |
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
- **Why rejected:** a skills-directory plugin loads the copy `setup` already
  maintains, with no second update path. Revisit if `skills-dir` proves
  blocked where ReStack is used, since a marketplace entry is also the
  route into an organisation's managed directory.

### Register the mod in `CLAUDE_CODE_PLUGIN_DIRS`

- **Pros:** the mod can live anywhere, such as `~/.restack/mods/`, away
  from the skills.
- **Cons:** `setup` would edit `~/.claude/settings.json`, merging into a
  value the user may already set, for the first time outside `restack-*`.
  That needs a JSON helper, because Windows PowerShell 5.1 cannot be
  trusted to rewrite the file, plus a backup and its own tests.
- **Why rejected:** `~/.claude/skills/` already loads plugins, and `setup`
  already owns `restack-*` there. This ADR's first draft took this route
  before `headroom` showed the simpler one.

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
- **Why rejected (O3):** the shared fixtures give one source
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
