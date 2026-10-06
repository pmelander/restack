// The Matrix tab's reading, against the matrices matrix.py is tested against.
// Every expected figure here is matrix.py's own (tests/test_matrix.py, and
// parse_claims run on the same files), or trace.py's BASE rule.

import { expect, test } from 'claude-code/testing'

import type { MatrixGrid } from '../types'
import {
  actorSetChanges,
  claimedCells,
  COLOR,
  EMPTY,
  HIT,
  matrixFiles,
  order,
  rasterCells,
  readClaims,
  readMatrix,
  staleness,
  svgSource,
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

test('the raster packs two stressors per line as half blocks, claimed cells dimmed', () => {
  const g = gridOf('matrix-iter1.md', 'residuals-iter1.md')
  const { rows, cols } = order(g, false)
  const r = rasterCells(g, rows, cols, claimedCells(g, '-'), 1)
  expect([r.columns, r.rows]).toEqual([6, 3])
  const words = new Uint32Array(Uint8Array.fromBase64(r.cells).buffer)
  const at = (line: number, column: number) => Array.from(words.slice((line * 6 + column) * 3, (line * 6 + column) * 3 + 3))
  // Line 0 is S-1 over S-2. CA: hit over empty. RS: hit over hit.
  expect(at(0, 2)).toEqual([0x2580, COLOR.hit, COLOR.none])
  expect(at(0, 3)).toEqual([0x2580, COLOR.hit, COLOR.hit])
  // LC: empty over hit draws the lower half only.
  expect(at(0, 4)).toEqual([0x2584, COLOR.hit, COLOR.none])
  // Line 2 is S-5 alone: LC unknown.
  expect(at(2, 4)).toEqual([0x2580, COLOR.unknown, COLOR.none])
  // The lens band: O over C.
  expect(at(0, 0)).toEqual([0x2580, COLOR.lens.O, COLOR.lens.C])

  const all = rasterCells(g, rows, cols, claimedCells(g, '*'), 1)
  const claimed = new Uint32Array(Uint8Array.fromBase64(all.cells).buffer)
  // S-1 × RS is claimed by R1 and R2: dimmed.
  expect(claimed[(0 * 6 + 3) * 3 + 1]).toBe(COLOR.claimed)
  const r1 = new Set([...claimedCells(g, 'R1')])
  expect(r1.has('S-5|LC')).toBe(false)
})

test('the Desktop drawing marks only the scored cells, each with its name', () => {
  const g = gridOf('matrix-iter3.md')
  const { rows, cols } = order(g, false)
  const svg = svgSource(g, rows, cols, claimedCells(g, '-'))
  // 23 hits, plus 12 lens bands.
  expect(svg.match(/<rect /g)!.length).toBe(23 + 12)
  expect(svg).toContain('<title>S-8 × EB</title>')
  expect(svg).not.toContain('currentColor')
})
