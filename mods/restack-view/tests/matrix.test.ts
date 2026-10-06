// The Matrix tab's reading, against the matrices matrix.py is tested against.
// Every expected figure here is matrix.py's own (tests/test_matrix.py, and
// parse_claims run on the same files), or trace.py's BASE rule.

import { expect, test } from 'claude-code/testing'

import type { MatrixGrid } from '../types'
import {
  actorSetChanges,
  claimedCells,
  desktopWindow,
  COLOR,
  EMPTY,
  flippedWindow,
  laneSvg,
  HIT,
  matrixFiles,
  order,
  readClaims,
  readMatrix,
  SVG_LIMIT,
  runs,
  staleness,
  UNKNOWN,
} from '../hooks/matrix.ts'
import { FIXTURES, MATRIX_FIXTURES } from './fixtures.ts'

const gridOf = (name: string, residuals?: string): MatrixGrid => {
  const { grid, problems } = readMatrix(MATRIX_FIXTURES[name])
  expect(problems).toEqual([])
  const claims = residuals === undefined ? [] : readClaims(MATRIX_FIXTURES[residuals], grid!.actors)

  return { ...grid!, file: name, claims, residualsFile: residuals, stale: [], marked: [] }
}

test('iteration 1: 5 stressors × 4 actors, total 11, 2 unknown cells counted as 1', () => {
  const g = gridOf('matrix-iter1.md')
  expect(g.actors).toEqual(['CA', 'RS', 'LC', 'NS'])
  expect(g.rows.map(r => r.id)).toEqual(['S-1', 'S-2', 'S-3', 'S-4', 'S-5'])
  expect(g.rows.map(r => r.lens)).toEqual(['O', 'C', 'O', 'C', 'X'])
  expect(g.total).toBe(11)
  expect(g.unknown).toBe(2)
  expect(g.colTotals).toEqual([2, 4, 3, 2])
  // S-5: CA 1, RS 1, LC 1?, NS ?
  expect(g.rows[4].cells).toEqual([HIT, HIT, UNKNOWN, UNKNOWN])
  expect(g.rows[4].total).toBe(4)
  expect(g.rows[2].cells).toEqual([EMPTY, EMPTY, EMPTY, HIT])
})

test('iteration 3: 12 × 8, total 23, a zero row kept', () => {
  const g = gridOf('matrix-iter3.md')
  expect([g.rows.length, g.actors.length, g.total]).toEqual([12, 8, 23])
  expect(g.colTotals).toEqual([4, 2, 3, 3, 3, 3, 3, 2])
  expect(g.rows.find(r => r.id === 'S-12')!.total).toBe(0)
})

test('a severity scale is a problem, and nothing is drawn', () => {
  const { problems } = readMatrix(MATRIX_FIXTURES['broken.md'])
  expect(problems).toContain('1 × Locker = 2: scoring is 0 or 1')
  expect(problems).toContain('2 cells sum to 1, the row says 2')
  expect(problems).toContain('no totals row')
})

test('margins never filled in are a problem', () => {
  const { problems } = readMatrix(MATRIX_FIXTURES['unfinished.md'])
  expect(problems).toContain('1 has no row total (cells sum to 2)')
  expect(problems).toContain('no totals row')
})

test('a file with no matrix says so', () => {
  expect(readMatrix('# Notes\n\nNo table here.\n').problems[0]).toMatch(/^no impact matrix found/)
})

test('claims as parse_claims reads them, outside the cluster included', () => {
  const one = readClaims(MATRIX_FIXTURES['residuals-iter1.md'], ['CA', 'RS', 'LC', 'NS'])
  expect(one).toEqual([
    { id: 'R1', title: 'Event-sourced reservations', cells: [['S-1', 'RS'], ['S-2', 'RS'], ['S-4', 'RS']] },
    { id: 'R2', title: 'Depot battery backup', cells: [['S-5', 'LC'], ['S-5', 'NS'], ['S-3', 'CA'], ['S-1', 'RS']] },
  ])
  // OC and BG are not actors of iteration 2: their claims are dropped, as matrix.py drops them.
  const two = readClaims(MATRIX_FIXTURES['residuals-iter2.md'], ['CA', 'RS', 'LC', 'PR'])
  expect(two.map(c => [c.id, c.cells])).toEqual([
    ['R4', [['S-4', 'RS'], ['S-13', 'CA']]],
    ['R5', [['S-1', 'RS'], ['S-4', 'RS']]],
  ])
})

test("the staleness stamp is trace.py's BASE rule", () => {
  expect(actorSetChanges(FIXTURES.band['decisions-log.md'])).toEqual([2])
  // Scored at D2; D5 changed the actor set since; not marked.
  expect(staleness(MATRIX_FIXTURES['matrix-iter1.md'], [2, 5])).toEqual({ baseline: 2, stale: [5], marked: [] })
  // Scored at D5, marked `scored pre-D6`: D6 is accounted for.
  expect(staleness(MATRIX_FIXTURES['matrix-iter3.md'], [6])).toEqual({ baseline: 5, stale: [], marked: [6] })
  expect(staleness('| no | baseline |', [3])).toEqual({ stale: [], marked: [] })
})

test('the newest matrix first: by date, then iteration; other files ignored', () => {
  const files = matrixFiles([
    'matrix-2026-10-01.md',
    'residuals-2026-10-02-iter6.md',
    'matrix-2026-10-01-iter4.md',
    'matrix-2026-10-02-iter7.md',
    'matrix-notes.md',
    'matrix-2026-10-02-iter6.md',
  ])
  expect(files.map(f => f.name)).toEqual([
    'matrix-2026-10-02-iter7.md',
    'matrix-2026-10-02-iter6.md',
    'matrix-2026-10-01-iter4.md',
    'matrix-2026-10-01.md',
  ])
  expect(files[0]).toEqual({ name: 'matrix-2026-10-02-iter7.md', date: '2026-10-02', iter: 7 })
})

test('sorting by total reorders rows and columns, and changes no cell', () => {
  const g = gridOf('matrix-iter1.md')
  expect(order(g, false)).toEqual({ rows: [0, 1, 2, 3, 4], cols: [0, 1, 2, 3] })
  const sorted = order(g, true)
  expect(sorted.rows[0]).toBe(4)
  expect(sorted.cols).toEqual([1, 2, 0, 3])
})

test('flipped: one lane per actor, one mark per stressor, totals over the whole matrix', () => {
  const g = gridOf('matrix-iter1.md')
  const { rows, cols } = order(g, false)
  const w = flippedWindow(g, rows, cols, claimedCells(g, '-'), 0, 100)
  expect([w.start, w.end, w.count]).toEqual([0, 5, 5])
  expect(w.ids).toEqual(['S-1', 'S-2', 'S-3', 'S-4', 'S-5'])
  expect(w.lens).toEqual([COLOR.lens.O, COLOR.lens.C, COLOR.lens.O, COLOR.lens.C, COLOR.lens.X])
  expect(w.lanes.map(l => l.actor)).toEqual(['CA', 'RS', 'LC', 'NS'])
  expect(w.lanes[0].marks).toEqual(['hit', 'empty', 'empty', 'empty', 'hit'])
  expect(w.lanes[3].marks).toEqual(['empty', 'empty', 'hit', 'empty', 'unknown'])
  expect(w.lanes.map(l => [l.total, l.unknown])).toEqual([[2, 0], [4, 0], [3, 1], [2, 1]])
  expect(w.ruler).toBe('S-1')
})

test('claimed cells are marked as claimed, and counted per actor', () => {
  const g = gridOf('matrix-iter1.md', 'residuals-iter1.md')
  const { rows, cols } = order(g, false)
  // RS: S-1, S-2 and S-4 are claimed (R1, and R2 for S-1); S-5 is not.
  const all = flippedWindow(g, rows, cols, claimedCells(g, '*'), 0, 100).lanes[1]
  expect(all.marks).toEqual(['claimed', 'claimed', 'empty', 'claimed', 'hit'])
  expect(all.claimed).toBe(3)
  // R2 alone claims only S-1 × RS in that lane.
  expect(flippedWindow(g, rows, cols, claimedCells(g, 'R2'), 0, 100).lanes[1].marks).toEqual([
    'claimed', 'hit', 'empty', 'hit', 'hit',
  ])
  expect(flippedWindow(g, rows, cols, claimedCells(g, '-'), 0, 100).lanes[1].claimed).toBe(0)
})

test('the window is as wide as the pane draws, and paging is clamped', () => {
  const g = gridOf('matrix-iter3.md')
  const { rows, cols } = order(g, false)
  const at = (offset: number, width: number) => {
    const w = flippedWindow(g, rows, cols, new Set(), offset, width)

    return [w.start, w.end, w.lanes[0].marks.length]
  }
  expect(at(0, 5)).toEqual([0, 5, 5])
  expect(at(5, 5)).toEqual([5, 10, 5])
  // Past the end, the window keeps its width and ends at the last stressor.
  expect(at(10, 5)).toEqual([7, 12, 5])
  expect(at(99, 5)).toEqual([7, 12, 5])
  expect(at(0, 500)).toEqual([0, 12, 12])
})

test('the ruler names every tenth stressor where it fits', () => {
  const g = gridOf('matrix-iter3.md')
  const { rows, cols } = order(g, false)
  // S-11 at column 10 needs four columns; twelve hold it only from 14.
  expect(flippedWindow(g, rows, cols, new Set(), 0, 12).ruler).toBe('S-1')
  const wide = gridOf('matrix-iter3.md')
  const extra = { ...wide, rows: [...wide.rows, ...wide.rows.map(r => ({ ...r, id: r.id + 'b' }))] }
  const order2 = order(extra, false)
  expect(flippedWindow(extra, order2.rows, order2.cols, new Set(), 0, 24).ruler).toBe('S-1       S-11      S-9b')
})

test('runs group equal neighbours', () => {
  expect(runs(['a', 'a', 'b', 'a'])).toEqual([['a', 2], ['b', 1], ['a', 1]])
  expect(runs([])).toEqual([])
})


test('on the Desktop the lanes are shapes on an exact grid, labelled in monospace', () => {
  const g = gridOf('matrix-iter1.md', 'residuals-iter1.md')
  const { rows, cols } = order(g, false)
  const svg = laneSvg(flippedWindow(g, rows, cols, claimedCells(g, '*'), 0, 100))
  // Lens runs O, C, O, C, X (5), and one square per mark: CA 2, RS 4, LC 3, NS 2.
  expect(svg.match(/<rect /g)!.length).toBe(5 + 11)
  // Every empty cell at once: one dotted line per lane.
  expect(svg.match(/<line /g)!.length).toBe(4)
  expect(svg).toContain('stroke-dasharray="2 6"')
  expect(svg).toContain('font-family="ui-monospace, Menlo, Consolas, monospace"')
  expect(svg).toContain('>RS</text>')
  expect(svg).toContain('3 claimed')
  expect(svg).toContain('(1?)')
  expect(svg).toContain(`fill="${COLOR.claimed}"`)
  expect(svg).not.toContain('<use')
  expect(svg).not.toContain('currentColor')
})

// A grid the size of a real engagement's: 152 stressors by 30 actors, with a
// mark in roughly one cell in `every`.
const bigGrid = (every: number) => {
  const actors = Array.from({ length: 30 }, (_, j) => `A${j}`)
  const rows = Array.from({ length: 152 }, (_, i) => ({
    id: `S-${i + 1}`,
    lens: 'OVCPX'[i % 5],
    cells: actors.map((_, j) => ((i * 7 + j * 13) % every === 0 ? 1 : 0)),
    total: 0,
  }))
  rows.forEach(r => (r.total = r.cells.reduce((a, b) => a + b, 0)))
  const colTotals = actors.map((_, j) => rows.reduce((a, r) => a + r.cells[j], 0))

  return {
    file: 'big.md',
    actors,
    rows,
    colTotals,
    total: colTotals.reduce((a, b) => a + b, 0),
    unknown: 0,
    claims: [],
    stale: [],
    marked: [],
  } as MatrixGrid
}

test('a real-sized matrix draws a full page under the Svg limit', () => {
  // About one cell in 19 marked, as on the reference engagement (244 of 4,560).
  const g = bigGrid(19)
  const { rows, cols } = order(g, false)
  const fit = desktopWindow(g, rows, cols, new Set(), 0, 125)
  expect(fit).not.toBeNull()
  expect(fit!.win.end - fit!.win.start).toBe(125)
  expect(fit!.svg.length).toBeLessThan(SVG_LIMIT)
})

test('a matrix too dense for one page narrows its window until it fits', () => {
  // Every cell marked: 4,560 squares would pass the limit at full width.
  const g = bigGrid(1)
  const { rows, cols } = order(g, false)
  expect(laneSvg(flippedWindow(g, rows, cols, new Set(), 0, 152)).length).toBeGreaterThan(SVG_LIMIT)
  const fit = desktopWindow(g, rows, cols, new Set(), 0, 152)
  expect(fit).not.toBeNull()
  expect(fit!.svg.length).toBeLessThanOrEqual(SVG_LIMIT)
  expect(fit!.win.end - fit!.win.start).toBeLessThan(152)
})
