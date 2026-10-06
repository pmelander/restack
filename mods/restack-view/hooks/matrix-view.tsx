// The Matrix tab's drawing (ADR-030, view 1): a Raster in the terminal, an Svg
// on the Desktop, the staleness stamp in the title. Data from matrix.ts; the
// callbacks come from the hook, so nothing here touches `$`.

import type { Elements, RenderSurface } from 'claude-code'

import type { MatrixState } from '../types'
import { claimedCells, COLOR, fileLabel, order, rasterCells, SVG_LIMIT, svgSource } from './matrix.ts'

type Els = Pick<Elements[RenderSurface], 'Box' | 'Text' | 'Button' | 'Select' | 'Raster' | 'Svg'>

export type MatrixPicks = {
  residual: string
  isSortedByTotal: boolean
  onFile: (name: string) => void
  onResidual: (pick: string) => void
  onSort: () => void
}

const LABEL_WIDTH = 8
const hex = (c: number): string => `#${c.toString(16).padStart(6, '0')}`

const NONE_YET =
  'No impact matrix scored yet. /restack-stressor analyze writes one to docs/stressor-analysis/, and it is drawn here.'

export function drawMatrix(els: Els, state: MatrixState | null, picks: MatrixPicks, surface: RenderSurface, columns: number) {
  const { Box, Text, Button, Select, Raster, Svg } = els
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

  const stamp =
    grid.baseline === undefined
      ? { text: ' · no scoring baseline', isStale: grid.stale.length > 0 }
      : grid.stale.length > 0
        ? { text: ` · scored at D${grid.baseline} · stale: D${grid.stale.join(', D')} changed the actor set`, isStale: true }
        : grid.marked.length > 0
          ? { text: ` · scored at D${grid.baseline}, marked scored pre-D${grid.marked.join(', pre-D')}`, isStale: false }
          : { text: ` · scored at D${grid.baseline}`, isStale: false }
  const title = (
    <Text wrap="wrap">
      <Text bold>{file ? fileLabel(file) : grid.file}</Text>
      {` · ${grid.rows.length} × ${grid.actors.length} · ${grid.total} cells`}
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
  )

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
  const controls = (
    <Box flexDirection="row" columnGap={2} flexWrap="wrap">
      {fileSelect}
      {residualSelect}
      <Button
        key="matrix-sort"
        label={picks.isSortedByTotal ? 'File order' : 'Sort by total'}
        hotkey="s"
        plain
        onPress={() => picks.onSort()}
      />
    </Box>
  )

  const legend = (
    <Text wrap="wrap">
      <Text color={hex(COLOR.hit)}>■</Text>
      <Text dimColor> hit  </Text>
      <Text color={hex(COLOR.unknown)}>■</Text>
      <Text dimColor> unknown (counts as 1)  </Text>
      {grid.claims.length > 0 ? <Text color={hex(COLOR.claimed)}>■</Text> : null}
      {grid.claims.length > 0 ? <Text dimColor>{` claimed by ${grid.residualsFile}  `}</Text> : null}
      <Text dimColor>lens </Text>
      {Object.entries(COLOR.lens).map(([lens, c]) => (
        <Text key={`lens-${lens}`}>
          <Text color={hex(c)}>▌</Text>
          <Text dimColor>{`${lens} `}</Text>
        </Text>
      ))}
    </Text>
  )

  if (surface === 'desktop') {
    let source = svgSource(grid, rows, cols, claimed)
    if (source.length > SVG_LIMIT) source = svgSource(grid, rows, cols, claimed, false)
    const drawing =
      source.length > SVG_LIMIT ? (
        <Text dimColor>Too many marked cells to draw here; the terminal draws it whole.</Text>
      ) : (
        <Svg source={source} alt={`Impact matrix ${grid.file}: ${grid.rows.length} stressors by ${grid.actors.length} actors`} isInteractive />
      )

    return (
      <Box flexDirection="column">
        {title}
        {controls}
        <Text> </Text>
        {drawing}
        {legend}
      </Box>
    )
  }

  // Terminal: each actor column as wide as its code needs, down to one cell.
  const longest = Math.max(...grid.actors.map(a => a.length))
  const fixed = LABEL_WIDTH + 2 + 8
  const fits = (w: number) => fixed + cols.length * w <= columns
  const cw = [Math.min(4, longest + 1), 3, 2, 1].find(fits) ?? 1
  const raster = rasterCells(grid, rows, cols, claimed, cw)
  const lines = raster.rows
  const pad = (s: string, n: number) => (s.length > n ? s.slice(0, n) : s.padEnd(n))
  const header = ' '.repeat(LABEL_WIDTH + 2) + cols.map(c => pad(grid.actors[c], cw)).join('')
  const footer = ' '.repeat(LABEL_WIDTH + 2) + cols.map(c => pad(String(grid.colTotals[c]), cw)).join('')
  const labels = Array.from({ length: lines }, (_, i) => pad(grid.rows[rows[i * 2]].id, LABEL_WIDTH)).join('\n')
  const totals = Array.from({ length: lines }, (_, i) => {
    const bottom = rows[i * 2 + 1]

    return `${grid.rows[rows[i * 2]].total}${bottom === undefined ? '' : ` ${grid.rows[bottom].total}`}`
  }).join('\n')

  return (
    <Box flexDirection="column">
      {title}
      {controls}
      <Text> </Text>
      {cw >= Math.min(longest, 2) ? (
        <Text dimColor wrap="truncate">
          {header}
        </Text>
      ) : (
        <Text dimColor wrap="wrap">{`Columns, left to right: ${cols.map(c => grid.actors[c]).join(' ')}`}</Text>
      )}
      <Box flexDirection="row">
        <Box width={LABEL_WIDTH} flexShrink={0}>
          <Text dimColor>{labels}</Text>
        </Box>
        <Raster key="matrix-grid" columns={raster.columns} rows={raster.rows} cells={raster.cells} />
        <Box marginLeft={1}>
          <Text dimColor>{totals}</Text>
        </Box>
      </Box>
      <Text wrap="truncate">{footer}</Text>
      <Text dimColor>{'Two stressors per line: the upper half of each cell is the first, the lower half the second.'}</Text>
      {legend}
    </Box>
  )
}
