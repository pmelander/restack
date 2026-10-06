# ADR-030: The Journey View Draws What the Text Hides: the Matrix, the Waiting, What Rests on a Belief, and the Rhythm

**Status:** Accepted

**Date:** 2026-10-06

**Deciders:** ReStack maintainers

**Technical Story:** Maintainer, 2026-10-06: "The output of restack is
extremely text heavy. Think about what kind of visualization might be useful
for the architect, that can be added to the view panel." Grounded in the
reference engagement at iteration 7: a 115 × 29 impact matrix, a 121 KB
assumptions register, a 1,300-line decisions log. Anonymised: this
repository is public.

**Implementation Status:** in progress. Built: the waiting bars (O1: first)
and the Matrix tab. The Matrix tab was checked against `matrix.py` on the
reference engagement's five real matrices, up to 152 × 30: rows, actors,
totals, unknowns, accept or reject, and every residual claim agree. Not yet
built: the lookup and the rhythm. The pane also gained a banner, an 80s fade
of the ReStack logo, which the maintainer asked for "just because we can".

**Accepted:** 2026-10-06, by the maintainer

**Review Date:** 2027-04-06

## Context

[ADR-029](ADR-029-a-journey-view-as-a-mod.md) gave the journey a read-only
view: a band above the prompt and a pane with Position, Asks, Assumptions and
Decisions tabs, all text. Its decision point 7 says further views are decided
one at a time. This is that decision for four of them.

ReStack's output is right and hard to see. On the reference engagement:

- **The impact matrix is 115 rows by 29 columns** (iteration 6). As a
  markdown table it cannot be read. Yet its shape is the method: where
  vulnerability concentrates, which rows cluster, which columns are
  suspiciously empty. The iteration's notes name all three: the most-hit
  actors, nine clusters holding most of the cells, and one actor whose
  column was empty because its path had not been walked. Each was found by
  reading numbers, not by seeing them.
- **The critical path was waiting.** The journey's own assessment found
  that no ask to another team had been sent, and called that the critical
  path. The register held every date needed to see it. Nothing drew it.
- **Beliefs carry weight nobody can see.** One open assumption, about who
  owns a neighbouring system, was cited by several ADRs and a residual.
  Finding what moves if it is wrong meant opening four files.
- **Seven iterations against an expected two or three.** The journey history
  records every command with its date, so the loop count, the parked
  stretches and where the effort went are all on disk, in 200 list lines.

What a mod can draw (Claude Code 2.1.289, the
[mods reference](https://code.claude.com/docs/en/plugins/mods/reference)):

| Element | Terminal | Desktop | Limit |
|---|---|---|---|
| `Text` with colours, block glyphs | ✓ | ✓ | 10,000 characters per string |
| `Raster`, a grid of coloured cells | ✓ | | 512 × 256 cells |
| `Svg` | | ✓ | 131,072 characters |
| `Select`, `Input` | ✓ | ✓ | |

`headroom`, the maintainer's own mod, shows block glyphs in `Text` drawing
clean bars on both surfaces, with a measured width allowance for the
Desktop's proportional font.

Three facts about the data shape this decision:

1. **Matrix scoring is binary.** A cell is `1`, `0`/`·`, or unknown (`?`,
   `1?`), and unknown counts as 1, because unknown exposure is exposure
   ([ADR-025](ADR-025-matrix-arithmetic-by-script.md)). Anything above 1 is a
   scoring error, not a severity. A heatmap of severities would misrepresent
   the method.
2. **Matrices go stale.** A matrix declares `Scoring baseline: D<n>`. A later
   decision logged with `Changes the actor set: yes` makes it stale unless it
   is marked `scored pre-D<m>`. `trace.py`'s BASE check enforces this. The
   reference engagement's latest matrix carries exactly such a mark.
3. **Every figure already has a script.** `matrix.py` computes the totals and
   the residual claims, `journey.py` the asks and statuses, `trace.py` the
   staleness. A view whose numbers differ from theirs is a second source of
   truth.

## Decision

The pane gains four views, on the same rules as ADR-029: read-only, optional,
no skill depends on them, and every number matches the script that owns it.

### 1. The matrix heatmap: a new **Matrix** tab

- **Flipped, and drawn as text** (maintainer, 2026-10-06). One lane per
  actor, one character per stressor: `■` for a mark, `·` for empty. The
  lanes run across, and only as many stressors as the pane can draw are
  shown, paged with `p` and `n`. A lane of dots with a 0 total is a
  suspicious zero, visible as one.
- **The terminal draws the lanes as `Text`,** which is monospace there.
  **The Desktop draws the same window as an `Svg`** of shapes on an exact
  grid: squares for marks, dots for empty, labels in a monospace face. The
  Desktop's `Text` is proportional and has no font option, so as text the
  lanes drifted apart and nothing lined up (maintainer, 2026-10-06). The
  `Svg` is not interactive, so it is drawn without a frame. Both read one
  `flippedWindow`, so the surfaces cannot disagree about the data.
- **One mark per cell, three states:** hit (`1`), unknown (`?`, `1?`), empty.
  No severity scale, because there is none. A lens strip runs above the
  lanes, one colour per stressor, and a ruler names every tenth stressor.
- **Margins:** each lane ends with its actor's total over the whole matrix,
  counted as `matrix.py totals` counts it, with its unknowns and its claimed
  cells beside it.
- **Residual overlay:** cells a residual claims to clear are drawn in a
  second, dimmer colour, read from the residuals file of the same iteration
  with `matrix.py claims`' rules. A `Select` picks one residual to highlight
  alone.
- **The staleness stamp is in the title, not a footnote:**
  `iteration <n> · <rows> × <columns> · scored at D<b> · stale: D<m> changed the actor set`.
  The BASE rule is mirrored from `trace.py`. A stale matrix still draws, and
  says so where the eye lands first.
- **Which matrix:** the newest `docs/stressor-analysis/matrix-<date>[-iter<n>].md`
  by date, then iteration. A `Select` lists the others. Its residuals are
  the file with the same suffix, if there is one.
- **Order:** the file's own row and column order by default. A button
  re-sorts both by total, as a reading aid. The order never implies a
  ranking the matrix does not hold.
- **Withdrawn: the grid as an image.** The first version drew stressors as
  rows: a `Raster` in the terminal, two stressors per line, and an `Svg` on
  the Desktop. On the reference engagement's 152 × 30 matrix the Desktop
  scaled the image to fit the pane, about 1,060 pixels tall shrunk to 220.
  The labels went past reading, and the interactive frame drew a white
  box. Flipping the axes puts the long dimension across, where paging
  handles it, and the short one down, where every actor gets a readable
  label.
- **A matrix `matrix.py` would reject** (a cell above 1, a total that does
  not add up) draws nothing but the problem and the command:
  `matrix-<date>-iter<n>.md: 3 cells scored above 1: python matrix.py totals`.

### 2. Waiting: bars at the top of the **Asks** and **Assumptions** tabs

- **Asks, one bar per recipient:** each open ask placed in one bucket.
  `never asked` is measured from the row's registration, and `asked` from
  its last send. The buckets are 0–6, 7–29 and 30+ days, and the number of
  asks is beside each bar. Sends are read as `journey.py asks` reads them,
  with `unasked` cancelling the last.
- **Assumptions, one stacked bar** of the register's statuses: Open, Partly
  resolved, Resolved by design (test pending), Resolved, Withdrawn and
  Superseded, with counts.
- **Drawn as headroom draws its meters:** lower half blocks (`▄`) in
  `Text`, theme colour keys that follow light and dark, and the empty track
  as the same block dimmed. The same on both surfaces, with headroom's
  Desktop width allowance. Each recipient's meter fills in proportion to the
  busiest recipient's asks, split by age with the oldest on the left. Sent
  and never asked are counted beside it.
- **Colour is vivid and never a judgement** (maintainer, 2026-10-06, after
  the first version read as too muted). Age runs cool to warm: `planMode`
  teal for 0–6 days, `autoAccept` purple for 7–29, `claude` orange for 30+.
  Statuses take the same family: Open orange, Partly resolved purple, by
  design teal, Resolved `ide` blue, the rest grey. The traffic-light keys
  (`success`, `warning`, `error`) are never used. A test fails if one
  appears, so there is no red for "late", no green for "done", and no
  "at risk".

### 3. What rests on a belief: a lookup on the **Assumptions** tab

- **An `Input` takes an ID** (`A-12`) and shows the row, then each ID its
  *Depends on it* cell names, grouped by kind and resolved where a canonical
  source holds it:
  - an ADR, to its title, from `docs/adr/`
  - a residual, to its heading in the newest residuals file
  - a decision, to its heading in the decisions log
  - a stressor, to its row in the newest matrix, with its hits
  - another assumption, to its row
- **What is not found is shown as written and marked `not found`.** It is
  never guessed at.
- **The reverse:** other open rows whose *Depends on it* names this ID, so a
  belief that other beliefs stand on shows them.
- **Text in a tree** (`├─`, `└─`), the same on both surfaces.

### 4. The rhythm: a strip at the top of the **Position** tab

- **One column per day** of the journey history, from its first entry to
  today, or one per week when the span is wider than the pane.
- **Each entry is marked by its command's family:** discover, stressor and
  events, decisions (ADR and the journey's gates), documentation and trace,
  and review. Entries that record a decision (`D<n>`) carry a gate mark.
- **Days with no entry stay empty.** Long stretches of them are the parked
  periods, shown, not named.
- **The counts the history holds, as numbers beside the strip:**
  iterations (`/restack-journey iterate` entries), gates, entries. No
  expected range and no verdict. The route's expectation belongs in
  `/restack-journey review`.
- **Block glyphs in `Text`**, both surfaces.

### Reading the files

- **Three more parsers mirror three scripts:** the matrix grid and the
  claims from `matrix.py`, the BASE rule from `trace.py`, and the history
  lines from `journey.py`. Each is pinned the way the journey reader is
  (ADR-029, decision point 4). `gen_skills.py` renders `tests/fixtures/matrix/`
  and the BASE cases of `tests/fixtures/trace/` into the mod's fixtures, and
  the mod's tests assert the scripts' own figures on them.
- **One new call, `$.fs.list`,** to find the matrices, residual files and
  ADRs. It reads; the allowlist in `scripts/check_mods.py` gains it, and
  nothing else.
- **All reading happens in the refresh, after each turn, guarded by
  modification times.** Drawing reads state only. A 115 × 29 matrix parses
  in well under the 10-second hook limit.

### Not built: an iteration trend chart

Totals across iterations look like the obvious chart. They are not
comparable: the actor and stressor sets change between iterations, and only
like-for-like on the same rows and columns means anything. That figure needs
`matrix.py compare`'s rules over two named files, and the history records it
in prose. A line of raw totals that rises reads as "the design is
getting worse" when it means "more was stressed". That is the misreading the
method exists to prevent. **Revisit** if `matrix.py compare` writes its
like-for-like figures to a canonical place the mod can read without guessing.

### Decisions settled by the maintainer, 2026-10-06

| # | Question | Options | Answer |
|---|---|---|---|
| O1 | **Build order** | (a) Waiting, then the matrix, then the lookup, then the rhythm. (b) The matrix first. | **(a).** Waiting reuses the register parser already built, and ships in a slice. The matrix brings two new parsers, two renderers and the BASE rule; it is the most valuable and the largest. |
| O2 | **The Matrix tab with no matrix** | (a) Hidden until `docs/stressor-analysis/` has one. (b) Shown, saying none is scored yet. | **(b).** A tab that appears later is a tab nobody finds. One line saying where the matrix will come from costs nothing. |
| O3 | **Unknown cells** | (a) Their own colour. (b) The hit colour, marked with a dot. | **(a).** On the reference engagement each unknown cell is registered as an assumption. They deserve to be seen as a different kind of thing, while counting as hits in every total. |
| O4 | **The rhythm's families** | (a) Five, as above. (b) One per skill, 17 colours. | **(a).** Seventeen colours cannot be told apart in a terminal, and the question the strip answers is where the effort went, not which command ran. |

## Consequences

### Positive

- The matrix's shape, the waiting and the weight on a belief become visible
  without a turn, and without reading 121 KB.
- A stale matrix says so where it is drawn. Today the stamp is a line in a
  history file.
- No new language, no new kind of call beyond `$.fs.list`, and no change to
  any skill.

### Negative

- **Three more mirrored parsers.** The view now mirrors parts of
  `journey.py`, `matrix.py` and `trace.py`. The fixtures catch drift in
  what they cover. A layout `matrix.py` learns later, and the fixtures do
  not hold, is invisible to the view until it is taught. Mitigation: a
  matrix the view cannot read draws the problem and the command, never a
  partial grid.
- **A wide matrix is read a page at a time.** The flipped lanes show only
  the stressors the pane can draw. On the reference engagement that is about
  80 of 152 at a time in a full-width terminal, fewer when docked. Sorting
  by total brings the most-hit stressors into the first page.
- **The pane grows.** Five tabs and three controls. Every view must stay
  quiet when its data is absent, or the pane becomes the dashboard nobody
  reads.

### Neutral

- Nothing changes for VS Code chat, `claude -p` or cloud sessions, which
  draw no pane.
- The band is unchanged.

## Knock-on changes

| Document | Change |
|---|---|
| `mods/restack-view/hooks/` | `matrix.ts`, `history.ts`, `refs.ts` (pure); the Matrix tab; the bars, lookup and strip; `$.fs.list` in the refresh |
| `mods/restack-view/types/index.d.ts` | the matrix, waiting, lookup and rhythm state |
| `mods/restack-view/tests/` | each view on both surfaces; figures equal to `matrix.py`, `journey.py asks` and `trace.py` BASE on the fixtures |
| `scripts/gen_skills.py` | renders `tests/fixtures/matrix/` and the BASE cases of `tests/fixtures/trace/` into the mod's fixtures |
| `scripts/check_mods.py`, ADR-029 | `$.fs.list` added to the allowlist |
| `mods/restack-view/README.md`, QUICKREF.md, CHANGELOG.md | the new tab and views |

## Alternatives considered

### A health score or a traffic light per journey

- **Pros:** one glance.
- **Cons:** a verdict computed by a view. The method's judgements belong to
  the architect and to `/restack-journey review`, which shows its reasoning.
- **Why rejected:** ADR-021's rule, that output is a worklist and never a
  verdict, applies to pictures too.

### A JSON snapshot written by the Python scripts for the mod to draw

- **Pros:** one parser per format; the view draws exactly what the scripts
  compute.
- **Cons:** a second file to keep in step with the journey files, written
  by every command that touches them, or a `$.process.run` per refresh. ADR-029
  rejected that call because policy mods refuse it first.
- **Why rejected:** for now. Revisit if a third mirrored parser drifts in
  practice despite the fixtures.

### Charts as images rendered by Python

- **Pros:** any chart a plotting library can draw.
- **Cons:** a dependency (ADR-010), a process call, and an `Image` element
  that exists only in the terminal.
- **Why rejected:** block glyphs and text cover these four views without any
  of that. The one image the pane does draw is the banner's `Svg` on the
  Desktop, where text has no monospace font to hold the art.

### The matrix as a severity heatmap

- **Why rejected:** scoring is binary (Context, fact 1). A colour scale
  would invent a dimension the matrix does not have.

## References

- [ADR-021](ADR-021-trace-checks-as-a-worklist.md): a worklist, never a verdict
- [ADR-023](ADR-023-journey-files-written-by-a-helper.md): the canonical journey files
- [ADR-025](ADR-025-matrix-arithmetic-by-script.md): matrix arithmetic by script; binary scoring
- [ADR-026](ADR-026-asks-routed-in-the-register.md),
  [ADR-027](ADR-027-asks-triaged-with-the-architect-first.md): asks and sends
- [ADR-029](ADR-029-a-journey-view-as-a-mod.md): the view, its contract, its install
- Claude Code docs: [mods interface](https://code.claude.com/docs/en/plugins/mods/interface),
  [reference](https://code.claude.com/docs/en/plugins/mods/reference)
