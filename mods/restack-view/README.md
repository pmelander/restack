# restack-view

Where the ReStack journey stands, on one line above the prompt
([ADR-029](../../docs/adr/ADR-029-a-journey-view-as-a-mod.md)):

```text
restack Brownfield · Stressor Analysis · Medium · next /restack-stressor analyze · 2 asks · 3 open · 1 decision
```

Terrain, phase and confidence from `journey-state.md`, the next command from
its *Current Position*, then open asks and open assumptions from the register
and open decisions from the log. A journey not in the canonical shape shows
`<file> is not canonical: /restack-journey migrate` and nothing else.

It is a **view**. It reads `docs/journey/` and never writes it, never submits
a prompt, and no skill depends on it: `/restack-journey where` gives the same
answer wherever this mod is not loaded. `scripts/check_mods.py` holds its
calls to that.

## Install

```bash
./setup --mods          # Windows: .\setup.ps1 -Mods
```

It installs beside the skills, as `~/.claude/skills/restack-view`, and loads as
`restack-view@skills-dir` in new sessions (`/reload-plugins` in an open one).
The choice is remembered, so `/restack-upgrade` keeps it current.
`./setup --no-mods` removes it.

## Commands

| Command | Does |
|---|---|
| `/restack-view` | prints the line, for places that draw nothing |
| `/restack-view band [on\|off]` | shows or hides the line; remembered between sessions; no argument toggles |

## Where it draws

The terminal and the Desktop Code tab. Not the VS Code chat panel, `claude -p`
or cloud sessions. It shares the band: what other band mods draw stays, under
this line.

## Develop

```bash
claude --plugin-dir mods/restack-view          # load it for one session, hot-reloaded
claude plugin validate mods/restack-view       # what it hooks and calls
claude plugin test mods/restack-view           # the tests, no session needed
python scripts/check_mods.py                   # the view's contract (ADR-029)
```

`tests/fixtures.ts` is generated from `tests/fixtures/journey/` by
`python scripts/gen_skills.py`. Never edit it.

Tested with Claude Code 2.1.289. Mods need 2.1.287 or later.
