# The journey view: `restack-view`

A ReStack engagement runs for weeks, and everything it knows is on disk in
`docs/journey/`. That record is complete but hard to read: the phase, the next
command and the open asks are spread over three files and several sections, and
a 100-row impact matrix cannot be read as a markdown table.

`restack-view` puts that record on screen. It is a Claude Code mod with two
parts:

- **The band**: one line above the prompt that says where the journey stands,
  updated after every turn.
- **The pane**: `/restack-view` opens five tabs that draw what the text hides:
  the rhythm of the work, who the open asks wait on, what rests on a belief,
  and the impact matrix as a heatmap.

```text
restack Brownfield · Stressor Analysis · Medium · next /restack-stressor analyze · 2 asks · 3 open · 1 decision
```

It is a **view**. It reads the journey files and never writes them, never
decides and never submits a prompt. No skill depends on it, and everything it
shows has a command that gives the same answer where it is not loaded
([ADR-029](adr/ADR-029-a-journey-view-as-a-mod.md),
[ADR-030](adr/ADR-030-journey-view-visuals.md)).

---

## Why it exists

"What were we doing, and what's open?" is the first question of almost every
session. Without the view, the answer costs a turn: `/restack-journey where`
reads the files into context and answers in the transcript, where it scrolls
away. With the view, the answer is on screen before you type, and stays there.

The pane exists because ReStack's output is right but hard to see. On the
engagement the view was built against (anonymised; seven stressor iterations
in), the matrix was 115 stressors by 29 actors, the assumptions register was
121 KB and the decisions log was 1,300 lines. Three things the method depends
on could only be found by reading numbers:

- **Where vulnerability concentrates.** The most-hit actors, the clusters of
  stressors that share a mechanism, and one actor with an empty column
  because its path had never been walked.
- **What the work was waiting on.** No ask to another team had been sent, and
  that was the critical path. The register held every date needed to see it.
- **What a belief was carrying.** One open assumption was cited by several
  ADRs and a residual. Finding what moves if it is wrong meant opening four
  files.

The pane draws each of these, so you can see them instead of reading for
them.

---

## Install

```bash
./setup --mods          # Windows: .\setup.ps1 -Mods
```

It installs beside the skills, as `~/.claude/skills/restack-view`, and loads
in every new session. In a session that is already open, run
`/reload-plugins`. The choice is remembered, so `/restack-upgrade` keeps the
view current; `./setup --no-mods` removes it. It needs Claude Code 2.1.287 or
later.

If you installed ReStack by asking Claude Code to do it, ask it to add the
mods. [INSTALL.md](../INSTALL.md) has the details.

---

## The band

```text
restack Brownfield · Stressor Analysis · Medium · next /restack-stressor analyze · 2 asks · 3 open · 1 decision
```

| Part | From |
|---|---|
| `Brownfield · Stressor Analysis · Medium` | terrain, phase and confidence in the header of `journey-state.md` |
| `next /restack-stressor analyze` | the next move recorded in *Current Position* |
| `2 asks` | open asks to people outside the design, from the assumptions register |
| `3 open` | open assumptions in the register |
| `1 decision` | open decisions in the decisions log |

It refreshes when a turn ends, so it follows the work without you asking.

**A stale position says so.** When the recorded next move has already run, or
a decision was answered after the position was written, the band does not
offer a move that is finished. It tells you to bring the position up to date
first ([ADR-032](adr/ADR-032-a-stale-position-says-so.md)):

```text
restack Greenfield · Documentation/Review · position stale since 2026-04-20 · next /restack-journey where · 1 decision
```

**A journey file in an older shape** shows only
`<file> is not canonical: /restack-journey migrate`. The view reads the
canonical shape that `journey.py` writes, and does not guess at the rest.

`/restack-view band off` hides the line and `/restack-view band on` brings it
back. The choice is kept between sessions. The band is shared: what other mods
draw above the prompt stays, under this line.

---

## The pane

`/restack-view` opens it. The tabs are `1` to `5`, and Esc closes the pane.
Each tab lists up to 60 items and then says how many are left and which
command or file has the full list.

The sketches below are in monochrome. The pane draws them in your theme's
colours, so they work in light and dark.

### 1 · Position

```text
    ____      _____ __             __
   / __ \___ / ___// /_____ ______/ /__
  / /_/ / _ \\__ \/ __/ __ `/ ___/ //_/
 / _, _/  __/__/ / /_/ /_/ / /__/ ,<
/_/ |_|\___/____/\__/\__,_/\___/_/|_|

Position   Asks   Assumptions   Decisions   Matrix
────────────────────────────────────────────────────────────────────────────

RHYTHM

  ▄▄▄█▄▄ ▄▄▄▄█▄▄▄          ▄▄█▄▄▄▄▄█▄▄▄▄█▄    ▄▄▄▄█▄▄ ▄
  2026-03-01                                         2026-04-20
  48 entries · 3 iterations · 9 gates · 51 days, one cell a day · █ a gate
  ■ discover  ■ stressor and events  ■ decisions  ■ documentation and trace  ■ review  ■ other

NEXT MOVE

  [n] Put the next command in the prompt   /restack-stressor analyze

  Current Position of 2026-04-20: nothing in the history since

JOURNEY

  Terrain Type     Brownfield
  Current Phase    Stressor Analysis
  ...

WHERE WE ARE

  ...the newest Current Position subsection, as journey-state.md writes it
```

**The rhythm** is the journey history as a strip: one cell a day from the
first entry to today, or one a week when the days do not fit. Each cell has
the colour of the commands run that day: discovery, stressor work,
decisions, documentation, review, or other. `█` marks a day with a gate.
Empty days are drawn as a dimmed track, blank in the sketch, so the weeks the
journey was parked show up as gaps with no label needed. Under the strip are
the history's own counts. There is no "expected" number of iterations: that
judgement belongs to `/restack-journey review`.

**The next move** has one button. `n` puts the next command in the prompt and
leaves the pane open. Esc moves you to the prompt, where you read the command
and press Enter yourself: the view never submits. If you have already typed
something, your draft is kept and the command appears in a toast instead.
Under the button is how old the position is, and whether anything has happened
since.

### 2 · Asks

```text
WAITING · 5

  Courier app team    ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄   3 · never asked 2 · sent 1 · 34 d
  Locker vendor       ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄            2 · sent 2 · 9 d
  ■ 0–6 d  ■ 7–29 d  ■ 30+ d  since the last send, or since registered when never asked

COURIER APP TEAM · 3

  A-1   Open · never asked
        how long a courier's reservation is held before it lapses
  ...
```

One meter per recipient. Its length is its share of the busiest recipient's
open asks, and it is coloured by age, oldest on the left: teal for 0–6 days,
purple for 7–29, orange for 30 and more. Age counts from the last time the
ask was sent, or from when it was registered if it was never sent. The counts
beside the meter say which. Below the meters, the open asks are listed by
recipient, with their status, last send and what is needed.

This is where an unsent ask on the critical path becomes visible.
`/restack-journey asks` turns the open asks into one send-ready section per
recipient.

### 3 · Assumptions

```text
THE REGISTER · 31

  ▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
  ■ Open 12  ■ Partly resolved 4  ■ Resolved by design (test pending) 3  ■ Resolved 10  ■ Withdrawn 2
  31 rows in the register

WHAT RESTS ON A BELIEF

  Assumption  12                                              [look up]

  A-12 · Open · The locker controller queues commands while offline
  settles it: a bench test of the controller with the network pulled

  ├─ ADRs
  │  ├─ ADR-0004 · Locker controller owns the offline queue (ADR-004-offline-queue.md)
  │  └─ ADR-0009 · not found
  │
  ├─ Residuals
  │  └─ R2 · Depot battery backup (residuals-iter1.md)
  │
  ├─ Stressors
  │  └─ S-5 · hits RS, LC, CA (matrix-iter3.md)
  │
  └─ Open rows that rest on it
     └─ A-14, A-19

OPEN ASSUMPTIONS · 12
  ...
```

**The register bar** shows every row by status, so you can see at a glance
whether the register is being closed or only growing
([ADR-031](adr/ADR-031-assumptions-drained-where-the-work-settles-them.md)).

**What rests on a belief** is a lookup. Type an assumption's number (`12`,
`A-12` and `A-012` all work) and press Enter. It shows the row, then every ID
in its *Depends on it* cell, resolved where a file holds it: an ADR to its
title, a residual to its heading, a decision to its heading, a stressor to its
hits in the newest matrix, another assumption to its row. An ID no file holds
is marked `not found`. Names that are not IDs are listed as written. Last
come the open rows that rest on this one. This answers the question *what
moves if this belief is wrong?* without opening four files. Nothing is read
until you press Enter.

### 4 · Decisions

The open decisions, each with its date, its question and the gate it belongs
to. The whole log is in `decisions-log.md`.

### 5 · Matrix

```text
IMPACT MATRIX

  iteration 3 · 2026-04-18 · 40 stressors × 6 actors · 60 cells (1 unknown) · scored at D7
  Matrix: iteration 3 · 2026-04-18     Residual claims: All residuals
  S-1 … S-40 (1–40 of 40 stressors)   Sort by total

  lens ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
       S-1       S-11      S-21      S-31
  RS   ■■·■·■■·■■■■■·■■···■·■·■■■■·■··■·■■■·■■·   25 6 claimed
  LC   ·■··■····■·■··■·■····■········■····■··■·   10 (1?)
  CA   ■■■·■···■··········■■·····■········■····    9
  NS   ··■·■■···■■·■·■··■···■····■■····■··■·■··   14
  PG   ···················■■···················    2
  DC   ········································    0

  ■ hit  ■ unknown (counts as 1)  ■ claimed by residuals-iter3.md  · empty   lens ■O ■V ■C ■P ■X
```

The newest impact matrix in `docs/stressor-analysis/`, turned on its side: one
lane per actor, one character per stressor. Turned this way, a matrix of
any length fits the pane, and its shape is visible:

- **A busy lane** is where vulnerability concentrates. In the sketch, RS is
  hit by 25 of 40 stressors.
- **Marks in the same columns across lanes** are stressors that share a
  mechanism: the clusters a residual can clear together.
- **An empty lane** is suspicious. DC has no hits: either it is genuinely
  safe, or its path was never walked.

A mark is orange for a hit and violet for an unknown, which counts as 1.
Scoring is binary, so there is no severity scale. The strip above the lanes
colours each stressor by its lens, where the matrix has a Lens column. Each
lane ends with the actor's total across the whole matrix, its unknowns, and
the cells residuals claim to clear. Claimed cells are dimmed, and the
*Residual claims* menu shows the claims of all residuals, of none, or of one,
so you can see what a single residual is meant to remove.

| Key | Does |
|---|---|
| `p` / `n` | page through the stressors, when there are more than fit; a ruler names every tenth |
| `s` | sort stressors and actors by total, as a reading aid; press again for file order |

The title line says when the matrix is **stale**: it was scored before a
decision that changed the actor set, and was not marked `scored pre-D<n>`.
This is the same rule `/restack-trace` applies. The numbers are the ones
`matrix.py` computes. A matrix `matrix.py` would reject is not drawn: the tab
names the problem instead. When there is more than one matrix, the *Matrix*
menu picks an earlier iteration.

---

## What it does not do

**It never writes or submits.** The only thing it puts anywhere is the next
command, in the prompt box, for you to send. `scripts/check_mods.py` checks
every call the mod makes against an allowlist in CI, and fails it for any
hook on tool calls or prompts and any access to the environment.

**It gives no verdict.** There is no health score, no traffic light, no red
for late and no green for done. Colour means age, status, command family or
lens, never good or bad. Whether three iterations is too many, or an ask is
late, is a judgement for you and `/restack-journey review`, not for a
colour.

**Nothing depends on it.** Every view has a command that answers the same
question:

| In the view | Without it |
|---|---|
| the band, the Position tab | `/restack-journey where` |
| the Asks tab | `/restack-journey asks` |
| the Assumptions tab | `assumptions-register.md`, `/restack-journey settle` |
| the Decisions tab | `decisions-log.md` |
| the Matrix tab | `docs/stressor-analysis/`, `matrix.py totals` |
| a stale position | `journey.py check` |

---

## Where it draws

In the terminal and in the Desktop app's Code tab. On the Desktop, where text
is proportional, the matrix and the banner are drawn as images so the columns
line up.

It does not draw in the VS Code chat panel, in `claude -p` or in cloud
sessions. The skills work the same there; use the commands in the table above.

---

## Commands

| Command | Does |
|---|---|
| `/restack-view` | opens the pane; where no pane can be drawn, prints the band's line instead |
| `/restack-view band` | toggles the band |
| `/restack-view band on` / `off` | shows or hides the band; remembered between sessions |

`/restack-view` runs without a Claude turn, so it works while Claude is busy
and costs nothing.

---

## Further reading

- [ADR-029](adr/ADR-029-a-journey-view-as-a-mod.md): why the view is a mod,
  and why it stays read-only
- [ADR-030](adr/ADR-030-journey-view-visuals.md): the four visuals, and the
  ones deliberately not built
- [ADR-032](adr/ADR-032-a-stale-position-says-so.md): the stale position
- [mods/restack-view/README.md](../mods/restack-view/README.md): developing
  the mod and running its tests
