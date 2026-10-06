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
| `/restack-view` | opens the pane; where nothing draws a pane, prints the line instead |
| `/restack-view band [on\|off]` | shows or hides the line; remembered between sessions; no argument toggles |

## The pane

Four tabs, `1` to `4`. Esc closes it.

| Tab | Shows | Whole list in |
|---|---|---|
| Position | the header fields and the newest Current Position subsection | `/restack-journey where` |
| Asks | a waiting bar per recipient, then open asks by recipient: status, last send, what is needed | `/restack-journey asks` |
| Assumptions | the register by status as one bar, then open rows: status, the belief, what would settle it | `assumptions-register.md` |
| Decisions | open decisions: date, question, gate | `decisions-log.md` |

**The waiting bars** ([ADR-030](../../docs/adr/ADR-030-journey-view-visuals.md)):
one glyph per open ask, oldest first. Its density is its age, counted from the
last send, or from registration when it was never sent: `░` 0–6 days, `▒`
7–29, `█` 30 and more. Colour means it was sent; plain means never asked. The
status bar shows every row of the register by status. Neither is a verdict:
there is no red for late and no green for done.

**Put the next command in the prompt** (`n`, on Position) puts the next move in
the prompt box and closes the pane. You read it and press Enter: the mod never
submits. With a draft already typed, it keeps your draft and shows the command
in a toast instead. Each tab stays under Claude Code's 10,000-character element
limit and ends with how many rows are left and where the rest is.

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
