// The Matrix tab's drawing (ADR-030, view 1), flipped and as text: one lane
// per actor, one character per stressor, as many stressors as the pane draws,
// paged with `p` and `n`. Text in the terminal; on the Desktop, whose text is
// proportional, the same lanes as shapes in an Svg (laneSvg). Data from matrix.ts;
// the callbacks come from the hook, so nothing here touches `$`.

import type { Elements, RenderSurface } from 'claude-code'

import type { MatrixState } from '../types'
import { claimedCells, COLOR, desktopWindow, fileLabel, flippedWindow, order, runs } from './matrix.ts'
import type { Mark } from './matrix.ts'

type Els = Pick<Elements[RenderSurface], 'Box' | 'Text' | 'Button' | 'Select' | 'Svg'>

export type MatrixPicks = {
  residual: string
  isSortedByTotal: boolean
  offset: number
  onFile: (name: string) => void
  onResidual: (pick: string) => void
  onSort: () => void
  onPage: (offset: number) => void
}

const GLYPH: Record<Mark, string> = { hit: '■', unknown: '■', claimed: '■', empty: '·' }
const MARK_COLOR: Record<Mark, string | undefined> = {
  hit: COLOR.hit,
  unknown: COLOR.unknown,
  claimed: COLOR.claimed,
  empty: undefined,
}
const TOTAL_WIDTH = 5

const NONE_YET =
  'No impact matrix scored yet. /restack-stressor analyze writes one to docs/stressor-analysis/, and it is drawn here.'

export function drawMatrix(els: Els, state: MatrixState | null, picks: MatrixPicks, surface: RenderSurface, columns: number) {
  const { Box, Text, Button, Select, Svg } = els
  if (state === null || state.files.length === 0) return <Text dimColor>{NONE_YET}</Text>

  const fileSelect =
    state.files.length > 1 ? (
      <Select
        key="matrix-file"
        label="Matrix"
        value={state.file}
        options={state.files.map(f => ({ value: f.name, label: `${fileLabel(f)} (${f.name})` }))}
        onSelect={value => picks.onFile(value)}
      />
    ) : null

  if (state.problem !== undefined || state.grid === undefined) {
    return (
      <Box flexDirection="column">
        {fileSelect}
        <Text>
          <Text bold>{state.file}</Text>
          {`: ${state.problem ?? 'not read'}. Not drawn: run matrix.py totals on it (/restack-stressor analyze).`}
        </Text>
      </Box>
    )
  }

  const grid = state.grid
  const file = state.files.find(f => f.name === grid.file)
  const { rows, cols } = order(grid, picks.isSortedByTotal)
  const claimed = claimedCells(grid, picks.residual)

  // The lane's width: what is left of the pane after the actor code and the total.
  const label = Math.max(4, ...grid.actors.map(a => a.length)) + 1
  const room = columns - label - TOTAL_WIDTH - 1
  // The Desktop's drawing must stay under the Svg limit, so its window may be narrower.
  const desktop = surface === 'desktop' ? desktopWindow(grid, rows, cols, claimed, picks.offset, Math.max(10, room)) : null
  const win = desktop?.win ?? flippedWindow(grid, rows, cols, claimed, picks.offset, Math.max(10, room))

  const stamp =
    grid.baseline === undefined
      ? { text: ' · no scoring baseline', isStale: grid.stale.length > 0 }
      : grid.stale.length > 0
        ? { text: ` · scored at D${grid.baseline} · stale: D${grid.stale.join(', D')} changed the actor set`, isStale: true }
        : grid.marked.length > 0
          ? { text: ` · scored at D${grid.baseline}, marked scored pre-D${grid.marked.join(', pre-D')}`, isStale: false }
          : { text: ` · scored at D${grid.baseline}`, isStale: false }

  const residualSelect =
    grid.claims.length > 0 ? (
      <Select
        key="matrix-residual"
        label="Residual claims"
        value={picks.residual}
        options={[
          { value: '*', label: 'All residuals' },
          { value: '-', label: 'None' },
          ...grid.claims.map(c => ({ value: c.id, label: `${c.id} ${c.title}`.slice(0, 48) })),
        ]}
        onSelect={value => picks.onResidual(value)}
      />
    ) : null

  const isPaged = win.count > win.end - win.start
  const pager = (
    <Box flexDirection="row" columnGap={2} flexWrap="wrap">
      {isPaged && win.start > 0 ? (
        <Button key="matrix-prev" label="◀ previous" hotkey="p" plain onPress={() => picks.onPage(Math.max(0, win.start - (win.end - win.start)))} />
      ) : null}
      <Text dimColor>{`${win.ids[0]} … ${win.ids[win.ids.length - 1]} (${win.start + 1}–${win.end} of ${win.count} stressors)`}</Text>
      {isPaged && win.end < win.count ? (
        <Button key="matrix-next" label="next ▶" hotkey="n" plain onPress={() => picks.onPage(win.end)} />
      ) : null}
      <Button
        key="matrix-sort"
        label={picks.isSortedByTotal ? 'File order' : 'Sort by total'}
        hotkey="s"
        plain
        onPress={() => picks.onSort()}
      />
    </Box>
  )

  const pad = (s: string, n: number) => (s.length >= n ? s.slice(0, n) : s.padEnd(n))

  return (
    <Box flexDirection="column">
      <Text wrap="wrap">
        <Text bold>{file ? fileLabel(file) : grid.file}</Text>
        {` · ${grid.rows.length} stressors × ${grid.actors.length} actors · ${grid.total} cells`}
        {grid.unknown > 0 ? ` (${grid.unknown} unknown)` : ''}
        {/* Stale is a fact about the file, said where the eye lands first. */}
        {stamp.isStale ? (
          <Text bold color="claude">
            {stamp.text}
          </Text>
        ) : (
          <Text dimColor>{stamp.text}</Text>
        )}
      </Text>
      <Box flexDirection="row" columnGap={2} flexWrap="wrap">
        {fileSelect}
        {residualSelect}
      </Box>
      {pager}
      <Text> </Text>
      {surface === 'desktop' && desktop === null ? (
        <Text dimColor>Too many marks to draw here, even ten stressors at a time; the terminal draws them as text.</Text>
      ) : surface === 'desktop' && desktop !== null ? (
        <Svg source={desktop.svg} alt={`Impact matrix ${grid.file}, ${win.ids[0]} to ${win.ids[win.ids.length - 1]}, one lane per actor`} />
      ) : (
        <Box flexDirection="column">
          <Text wrap="truncate">
            <Text dimColor>{pad('lens', label)}</Text>
            {runs(win.lens).map(([color, n], i) => (
              <Text key={`lens-${i}`} color={color}>
                {'▄'.repeat(n)}
              </Text>
            ))}
          </Text>
          <Text dimColor wrap="truncate">
            {' '.repeat(label) + win.ruler}
          </Text>
          {win.lanes.map(lane => (
            <Text key={`lane-${lane.actor}`} wrap="truncate">
              <Text bold={lane.total > 0} dimColor={lane.total === 0}>
                {pad(lane.actor, label)}
              </Text>
              {runs(lane.marks).map(([mark, n], i) =>
                MARK_COLOR[mark] === undefined ? (
                  <Text key={`m-${i}`} dimColor>
                    {GLYPH[mark].repeat(n)}
                  </Text>
                ) : (
                  <Text key={`m-${i}`} color={MARK_COLOR[mark]}>
                    {GLYPH[mark].repeat(n)}
                  </Text>
                ),
              )}
              <Text bold={lane.total > 0} dimColor={lane.total === 0}>
                {` ${String(lane.total).padStart(TOTAL_WIDTH - 1)}`}
              </Text>
              {lane.unknown > 0 ? <Text color={COLOR.unknown}>{` (${lane.unknown}?)`}</Text> : null}
              {lane.claimed > 0 ? <Text color={COLOR.claimed}>{` ${lane.claimed} claimed`}</Text> : null}
            </Text>
          ))}
        </Box>
      )}
      <Text> </Text>
      <Text wrap="wrap">
        <Text color={COLOR.hit}>■</Text>
        <Text dimColor> hit  </Text>
        <Text color={COLOR.unknown}>■</Text>
        <Text dimColor> unknown (counts as 1)  </Text>
        {grid.claims.length > 0 ? <Text color={COLOR.claimed}>■</Text> : null}
        {grid.claims.length > 0 ? <Text dimColor>{` claimed by ${grid.residualsFile}  `}</Text> : null}
        <Text dimColor>· empty   lens </Text>
        {Object.entries(COLOR.lens).map(([lens, c]) => (
          <Text key={`lens-key-${lens}`}>
            <Text color={c}>■</Text>
            <Text dimColor>{`${lens} `}</Text>
          </Text>
        ))}
      </Text>
    </Box>
  )
}
