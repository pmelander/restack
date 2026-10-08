# restack-view

What the view shows and how to use it, tab by tab, is in
[The journey view](../../docs/VIEW.md). This page is the mod's reference:
what it reads, its commands and keys, and how to develop it.

Where the ReStack journey stands, on one line above the prompt
([ADR-029](../../docs/adr/ADR-029-a-journey-view-as-a-mod.md)):

```text
restack Brownfield · Stressor Analysis · Medium · next /restack-stressor analyze · 2 asks · 3 open · 1 decision
```

Terrain, phase and confidence from `journey-state.md`, the next command from
its *Current Position*, then open asks and open assumptions from the register
and open decisions from the log. A journey not in the canonical shape shows
`<file> is not canonical: /restack-journey migrate` and nothing else.

A **stale position**, one whose next move has already run or that a decision
was answered after, says so instead of offering a finished move
([ADR-032](../../docs/adr/ADR-032-a-stale-position-says-so.md)):

```text
restack Greenfield · Documentation/Review · position stale since 2026-04-20 · next /restack-journey where · 1 decision
```

A position whose next move is a **wait** says who it waits on and offers no
command, since nothing runs until an answer arrives
([ADR-033](../../docs/adr/ADR-033-a-wait-is-a-next-move.md)). The Position tab
keeps the command the wait names behind its button, for when one does:

```text
restack Greenfield · Documentation/Review · waiting on depot operations and the locker vendor · 1 decision
```

The Position tab adds a line under the next move: the position's date, the
history and decisions since, and whether its move ran. `journey.py check`
prints the same line.

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

Five tabs, `1` to `5`, under the ReStack banner in an 80s fade. Esc closes it.

| Tab | Shows | Whole list in |
|---|---|---|
| Position | the rhythm strip, then the header fields and the newest Current Position subsection | `/restack-journey where` |
| Asks | a waiting bar per recipient, then open asks by recipient: status, last send, what is needed | `/restack-journey asks` |
| Assumptions | the register by status as one bar, a lookup of what rests on a belief, then open rows: status, the belief, what would settle it | `assumptions-register.md` |
| Decisions | open decisions: date, question, gate | `decisions-log.md` |
| Matrix | the newest impact matrix as a heatmap, with residual claims and its staleness | `docs/stressor-analysis/` |

**The Matrix tab** ([ADR-030](../../docs/adr/ADR-030-journey-view-visuals.md))
draws the newest `docs/stressor-analysis/matrix-<date>[-iter<n>].md` as
`matrix.py` reads it, flipped: one lane per actor, one character per stressor.
`■` is a mark, orange for a hit and violet for an unknown, which counts as 1;
`·` is empty. There is no severity scale, because scoring is binary. As many
stressors are shown as the pane can draw: `p` and `n` page through, and a
ruler above names every tenth. A lens strip runs above the lanes. Each lane
ends with its actor's total over the whole matrix, its unknowns, and its
claimed cells. Cells the same iteration's residuals claim are dimmed, and the
Select shows all residuals, none, or one. The title says when the matrix is
stale: scored before a decision that changed the actor set, and not marked
`scored pre-D<n>`, as `trace.py` decides it. `s` sorts stressors and actors
by total, as a reading aid. A matrix `matrix.py` would reject is not drawn:
the tab names the problem instead.

**The rhythm** (Position tab): the journey history as a strip, one cell a
day from its first entry to today, or a week when the days do not fit. A cell
takes the colour of its commands' family: discover, stressor and events,
decisions, documentation and trace, review, or other. `█` marks a day with a
gate. Empty days stay empty, so the parked stretches show without a label.
Under it are the history's own counts: entries, iterations and gates. There
is no expected range: that belongs to `/restack-journey review`.

**What rests on a belief** (Assumptions tab): type an assumption's ID, such
as `A-12`, and press Enter. The row is shown, then every ID its *Depends on
it* cell names, resolved where a source holds it: an ADR to its title from
`docs/adr/`, a residual to its heading, a decision to its heading, a
stressor to its hits in the matrix the Matrix tab shows, another assumption
to its row. What no source holds is marked `not found`. Names that are not
IDs, such as `LLD-03`, are listed as written. Last come the open rows that
rest on this one. Nothing is read until you press Enter.

**The waiting bars** ([ADR-030](../../docs/adr/ADR-030-journey-view-visuals.md)):
a meter per recipient, filled in proportion to the busiest recipient's open
asks and coloured by age, oldest on the left: teal 0–6 days, purple 7–29,
orange 30 and more. Age counts from the last send, or from registration when
an ask was never sent; the counts beside each meter say which. The status
meter shows every row of the register by status. Both use theme colours, so
they follow light and dark, and neither is a verdict: there is no red for
late and no green for done.

**Put the next command in the prompt** (`n`, on Position) puts the next move in
the prompt box and leaves the pane open. Esc takes you to the prompt, the pane
staying up; you read the command and press Enter: the mod never submits. With a draft already typed, it keeps your draft and shows the command
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
