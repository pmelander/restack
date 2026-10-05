### Challenge by removal (ablation)

Every iteration adds residuals, and every residual is an actor with stressors
of its own. Over a long engagement the design accretes, and nothing in the
analysis ever takes a residual out again. An ablation asks the other question:
**if this residual, and what was built on it, went, what would come back, and
what would go with it?**

The answer is a **report and a decision brief**, never a verdict. A residual
that survives the challenge comes out of it with a tested justification. One
that fails it becomes an option at a gate. Keep, cut and substitute are the
architect's (ADR-028).

#### Five ways an ablation goes wrong

These come from the first one done by hand. Each step below exists to stop one.

1. **Deleting instead of substituting.** The removed actors carried
   intentions, and the intentions still need a carrier. A cut with no named
   substitute can't be scored.
2. **Counting columns.** Most cells on a residual's columns describe what the
   system *means*, not what it is built on, and they survive the cut. On the
   reference engagement 29 of 35 did. Classify every row.
3. **Counting overlapping credit.** A cell two residuals claim doesn't come back
   when one of them goes. The re-open set is the unique contribution only.
4. **Counting circular credit.** A residual credited with clearing a stressor
   that exists only because of its own subtree. Remove the subtree and the
   stressor vanishes: it doesn't re-open.
5. **Reading the total without the lens.** A small net that moves exposure
   onto the aspiration's own column is worse than a large one that doesn't.

#### Step 0: find a candidate (when no target was named)

The matrix ranks actors. It doesn't show **what actors share**, and a hub
split across several columns stays below every single actor. Look three ways.

1. **Shared substrate.** From the deployment and security documents, list
   what columns share: one storage account, one identity, one pipeline agent,
   one region, one process. Propose groups, each with the line that
   evidences it, and ask the architect to confirm them. **The grouping is
   theirs**; a substrate nobody declares stays hidden. Write the confirmed
   groups to `docs/stressor-analysis/groups-<date>.md`, one
   `- <name>: <COL>, <COL>` line each, and run
   `python "$MX" rollup <matrix> --groups <file>`. A group that outranks the
   most-hit actor outside it is a candidate. Its crossing rows are the
   common-mode stressors the columns hide.
2. **Topology.** Read the HLD's diagram *source* (mermaid or similar), not
   the rendered image. A rendered overview can leave edges out: the reference
   engagement's left out three of its hub's. Count, per node, with a subgraph
   counted as one node:
   - edges in and out;
   - distinct writers (actors with an edge *into* a store).

   Show the top nodes as a worklist. Three or more writers to one store is
   worth a look.
3. **Generation depth.** For each residual, follow what it created (the
   residuals file's `**Creates:**` lines, the ADR's created actors) to the
   residuals whose cells sit on those actors. Draw the tree:
   **G0 → G1 → G2 → …**. A residual that exists to defend another residual is
   a third generation, and the place to look first.

Show the candidates with the numbers behind each. The architect picks the
target with one choice question. Picking what to examine is not a gate and
takes no D-number.

#### Step 1: the baseline

Name the matrix the ablation runs on and its scoring baseline. From
`docs/journey/decisions-log.md`, list every decision since that baseline whose
entry says it changed the actor set. If there is any, the matrix is stale:
say so on the report's first line. Ask the architect whether to re-score first
or run on the stale matrix with the qualifier. Either is legitimate; quoting a
stale net without saying so is not.

#### Step 2: the removal set and the scenarios

The target is rarely one column.

1. Map the target residual to its columns (the actors it created).
2. Find what depends on it:
   - residuals whose cells sit on those columns;
   - residuals whose ADR amends or builds on the target's;
   - every citation of the target's ADR and residual ID: `python "$TR" refs <ID>`.
3. Draw the subtree with its generations.
4. **Name two or three scenarios.** The whole subtree; the target's carrier
   kept and the branch on top of it cut; one generation alone. The useful cut
   on the reference engagement sat two generations below the one the
   architect asked about.

Confirm the scenarios with the architect before scoring them.

#### Step 3: intentions and substitutes

For each scenario:

1. **List the intentions the removed actors carry.** Use the path maps: what
   enters and leaves each one. Then list the jobs nobody designed them for:
   other ADRs that rely on them for something incidental, like a time source,
   an audit history, or an off-ramp when another store is down. Search the
   ADRs for the actor's name to find them.
2. **List candidate carriers for those intentions,** and check each against
   the record. An earlier decision may already have rejected it (look in
   the ADRs' "Alternatives considered" and the decisions log). If so, cite
   the decision and say what has changed since, or strike the candidate. A
   substitute that survives only because nobody checked is the commonest
   way an ablation flatters a cut.
3. **`none` is a real answer:** the intention is dropped. Say so in the brief,
   and test it against the aspiration. "Losing it is acceptable" may already
   be on record.
4. **One substitute per run.** The script moves the cells onto one column. If
   the intentions need different carriers, run once per carrier. Otherwise
   pick the one that carries most, and name the others' stressors as new rows
   (Step 6).

Ask the architect to confirm the substitute for each scenario.

#### Step 4: classify the rows

Run `python "$MX" ablate <matrix> --remove <COLS>` without `--classify`. It
lists every row that touches the removed columns, in the classify file's
format. Propose a class for each, **with a mechanism-level reason**:

| Class | Meaning | Reason it must state |
|---|---|---|
| `vanish` | The stressor exists only because of the removed set. The whole row goes | Which removed actor the scenario depends on, and why nothing else can produce it |
| `inherit` | The stressor is about what the intention means. It lands on the substitute unchanged | Why the substitute faces the same scenario |
| `morph` | The mechanism is carrier-specific, with an analogue on the substitute | What the analogue is. The row is re-scored on the substitute |

Then **add the circular rows**: rows the removed residuals are credited with
clearing (their cells may be 0 now) whose stressor exists only because of the
removed set. Class them `vanish`. A missing route into a store the subtree
locked down is the reference engagement's case.

`vanish` is the classification that favours a cut. **Every `vanish` needs
its mechanism.** "Goes with it" is not a reason.

Show the proposed classes as one table, and ask the architect to confirm or
change them. Ask per row only for the ones they want to change. Write the
confirmed file to `docs/stressor-analysis/ablation-<date>-<slug>-<scenario>.classes.md`,
one `S-<n>: <class> — <reason>` line each.

#### Step 5: the arithmetic

```bash
python "$MX" ablate <matrix> --remove <COLS> --residuals <R,R> \
  --claims docs/stressor-analysis/residuals-*.md \
  --classify <classes file> --substitute <ACTOR|none> --aspiration <COL>
```

- **`--claims`** takes every residuals file in the engagement, so a cell
  claimed by a residual that stays is found and not counted as re-opening.
- **`--aspiration`** is the column for the aspiration's first axis: what
  must not be disturbed. Ask if the journey state doesn't make it obvious.
- **Exit 1** means the ablation is incomplete. The output says what is
  missing. Do not report a net from an incomplete run.

#### Step 6: what the substitute brings

The script counts what moves and what comes back. It can't count the
stressors the substitute brings with it. Name them with the generation
method: the substitute's own failure modes on these intentions; its coupling
to everything else that already uses it (a shared substrate again); and
lever rows if it carries a stop.

Give each a lens and the columns it would hit, and estimate the cells **as
a range**. Mark them "named, not walked". The net in the report is then a
range: the script's net plus the new rows' range. A single figure needs the
rows walked first (`walk`, then re-score).

#### Step 7: what the matrix can't hold

List what the cut removes or adds outside the cells:
- accepted risks that close or open;
- identities, pipelines and agents that go or arrive;
- policies a later decision weakened that the cut would restore;
- how many documents would change: count the hits from `refs`.

**Note whether anything is implemented.** A cut that costs documents only
will never be cheaper than now.

#### Step 8: the report and the brief

Write `docs/stressor-analysis/ablation-<date>-<slug>.md`:

1. **The question**, how it came up, and the baseline line from Step 1.
2. **What the target carries**: columns, cells, the incidental jobs.
3. **The subtree**, with generations.
4. **Per scenario:**
   - the substitute, and the record it was checked against;
   - the classified rows: vanished, inherited and morphed counts, with the
     rows named;
   - the re-open set, and what was claimed but didn't re-open, with the
     reason for each;
   - the new rows, named;
   - the net as a range, by lens and on the aspiration's column;
   - what the matrix can't hold.
5. **What the ablation found about the analysis**: overlap, circular credit,
   a hub the columns hid. These hold whatever the architect decides.
6. **Open for the architect.**

Then the **approach gate**. Get the number with
`journey.py decision open "<question>" --gate approach`, and issue the brief
with these options:
- **keep**, recording the challenge;
- **cut**, one option per scenario worth cutting;
- **substitute**;
- **re-score first**, when the baseline is stale.

**STOP.** When the architect answers, record it with `decision answer`. That
and the brief's own entry are the only journey writes an ablation makes. It
never edits the matrix or an ADR.

After the answer:
- **Kept:** hand off to `/restack-adr update <ADR>` to add the dated line
  `Challenged by removal on <date>: kept because <cells, lens>`. That line is
  the tested justification an inheritor needs.
- **Cut:** hand off to `/restack-adr`, to supersede with the knock-on changes,
  and then to `analyze` for a re-score: the actor set changed.

#### Output

```
docs/stressor-analysis/
  groups-<date>.md                                  declared substrates (Step 0)
  ablation-<date>-<slug>-<scenario>.classes.md      confirmed row classes (Step 4)
  ablation-<date>-<slug>.md                         the report (Step 8)
```
