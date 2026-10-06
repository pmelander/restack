// What rests on a belief (ADR-030, view 3): reading "Depends on it" cells in
// the shapes a long engagement writes them, and resolving each ID only where
// a canonical source holds it. The cells here are invented, in those shapes.

import { expect, test } from 'claude-code/testing'

import type { MatrixGrid } from '../types'
import { registerRows } from '../hooks/journey.ts'
import { readMatrix } from '../hooks/matrix.ts'
import {
  adrFiles,
  decisionTitles,
  lookup,
  lookupLines,
  parseRefs,
  residualTitles,
  titleOf,
} from '../hooks/refs.ts'
import { FIXTURES, MATRIX_FIXTURES } from './fixtures.ts'

test('an ADR clause owns its bare numbers, ranges and slashes', () => {
  expect(parseRefs('ADR-0005, 0025, 0026–0031, 0032, 0040; LLD-03; LLD-09')).toMatchObject({
    adrs: [5, 25, 26, 27, 28, 29, 30, 31, 32, 40],
    other: ['LLD-03', 'LLD-09'],
  })
  expect(parseRefs('Whole offline half: LLD-02, LLD-08; ADR-0002/0003')).toMatchObject({
    adrs: [2, 3],
    other: ['Whole offline half: LLD-02', 'LLD-08'],
  })
})

test('other kinds are recognised, and anything else is kept as written', () => {
  expect(parseRefs('DECISION-01 Q4; ADR-0004 guardrails; LLD-03')).toEqual({
    adrs: [4],
    residuals: [],
    decisions: [],
    stressors: [],
    assumptions: [],
    other: ['DECISION-01 Q4', 'guardrails', 'LLD-03'],
  })
  expect(parseRefs('R6-A, R13, D8, A-09, S-12')).toMatchObject({
    residuals: ['R6-A', 'R13'],
    decisions: [8],
    assumptions: [9],
    stressors: ['S-12'],
    other: [],
  })
})

test('ADR files by number, titles without their prefix', () => {
  expect([...adrFiles(['ADR-0047-fleet-guard.md', 'ADR-12.md', 'README.md']).entries()]).toEqual([
    [47, 'ADR-0047-fleet-guard.md'],
    [12, 'ADR-12.md'],
  ])
  expect(titleOf('# ADR-0047: Fleet-action guard\n\nBody.\n')).toBe('Fleet-action guard')
  expect(titleOf('No heading\n')).toBeUndefined()
})

test('decision and residual headings', () => {
  expect(decisionTitles(FIXTURES.band['decisions-log.md']).get(3)).toBe(
    'Offline unlock: local codes or a cached allow-list? (2026-04-18)',
  )
  expect(residualTitles(MATRIX_FIXTURES['residuals-iter1.md']).get('R2')).toBe('Depot battery backup')
})

const rowsOf = (text: string) => {
  const rows = registerRows(text)
  if (typeof rows === 'string') throw new Error(rows)

  return rows
}

const iter3 = (): MatrixGrid => ({
  ...readMatrix(MATRIX_FIXTURES['matrix-iter3.md']).grid!,
  file: 'matrix-iter3.md',
  claims: [],
  stale: [],
  marked: [],
})

test('a row resolved: found where a source holds it, not found where none does', () => {
  const rows = rowsOf(FIXTURES.asks['assumptions-register.md'])
  // A-2 rests on ADR-0004 and S-12.
  const result = lookup('A-2', rows, {
    adrs: new Map([[4, { file: 'ADR-0004-controller.md', title: 'Controller reporting interval' }]]),
    residuals: new Map(),
    decisions: new Map(),
    grid: iter3(),
  })
  expect(result).toMatchObject({ kind: 'found', id: 'A-2', status: 'Open' })
  const lines = lookupLines(result).map(l => l.text)
  expect(lines[0]).toBe('A-2 · Open · Locker controllers report door state within a second')
  expect(lines).toContain('│  └─ ADR-0004 · Controller reporting interval (ADR-0004-controller.md)')
  expect(lines).toContain('   └─ S-12 · no hits (matrix-iter3.md)')

  // Without the ADR and the matrix, both are said to be not found.
  const bare = lookupLines(lookup('A-2', rows, { adrs: new Map(), residuals: new Map(), decisions: new Map() }))
  expect(bare.filter(l => l.tone === 'missing').map(l => l.text.trim())).toEqual([
    '│  └─ ADR-0004 · not found',
    '└─ S-12 · not found',
  ])
})

test('a residual resolved from its residuals file', () => {
  const rows = rowsOf(FIXTURES.asks['assumptions-register.md'])
  const residuals = new Map(
    [...residualTitles(MATRIX_FIXTURES['residuals-iter1.md']).entries()].map(([r, title]) => [
      r,
      { file: 'residuals-iter1.md', title },
    ]),
  )
  const lines = lookupLines(lookup('A-3', rows, { adrs: new Map(), residuals, decisions: new Map() })).map(l => l.text)
  expect(lines).toContain('   └─ R2 · Depot battery backup (residuals-iter1.md)')
})

test('A-09 is A-9; an unknown ID and a non-ID are said so', () => {
  const rows = rowsOf(FIXTURES.asks['assumptions-register.md'])
  const none = { adrs: new Map(), residuals: new Map(), decisions: new Map() }
  expect(lookup('A-02', rows, none)).toMatchObject({ kind: 'found', id: 'A-2' })
  expect(lookup('a-99', rows, none)).toEqual({ kind: 'error', message: 'A-99 is not in the register.' })
  expect(lookup('ADR-0004', rows, none)).toEqual({ kind: 'error', message: "Type an assumption's ID, such as A-12." })
})

test('the open rows that rest on a belief are named', () => {
  const register = FIXTURES.band['assumptions-register.md'].replace(
    '| A-3 | Reservation lookups stay under 50 ms | inference | a load test against the staging API | ADR-0003 |',
    '| A-3 | Reservation lookups stay under 50 ms | inference | a load test against the staging API | ADR-0003, A-1 |',
  )
  const result = lookup('A-1', rowsOf(register), { adrs: new Map(), residuals: new Map(), decisions: new Map() })
  expect(result).toMatchObject({ kind: 'found', restsOnIt: ['A-3'] })
  expect(lookupLines(result).map(l => l.text)).toContain('└─ Open rows that rest on it')
})
