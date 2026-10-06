// The journey's rhythm (ADR-030, view 4): the history read as journey.py
// writes it, and as an older history left it, laid out by day or by week.

import { expect, test } from 'claude-code/testing'

import { familyOf, historyEntries, rhythm } from '../hooks/rhythm.ts'
import type { Entry } from '../hooks/rhythm.ts'
import { FIXTURES } from './fixtures.ts'

test('a command belongs to the family of its skill, prefixed or not', () => {
  expect(familyOf('/restack-stressor walk courier-fill')).toBe('stressor')
  expect(familyOf('/stressor residues')).toBe('stressor')
  expect(familyOf('/restack-events')).toBe('stressor')
  expect(familyOf('/journey where')).toBe('decisions')
  expect(familyOf('/restack-adr update 0044')).toBe('decisions')
  expect(familyOf('/restack-solution-doc update hld')).toBe('documentation')
  expect(familyOf('/restack-design-review consistency')).toBe('review')
  expect(familyOf('/restack-discover confidence')).toBe('discover')
  // No ReStack command, or a skill outside the five: other.
  expect(familyOf('repo setup (D43)')).toBe('other')
  expect(familyOf('/restack-upgrade')).toBe('other')
})

test('the history as journey.py writes it: dates, families, gates and iterations', () => {
  expect(historyEntries(FIXTURES.band['journey-state.md'])).toEqual([
    { date: '2026-03-01', command: '/restack-journey start', family: 'decisions', isGate: true, isIterate: false },
    { date: '2026-03-20', command: '/restack-journey iterate', family: 'decisions', isGate: true, isIterate: true },
    { date: '2026-04-18', command: '/restack-journey iterate', family: 'decisions', isGate: true, isIterate: true },
  ])
})

test('a gate mentioned mid-line counts, and free text is kept as other', () => {
  const state = [
    '## Journey History',
    '',
    '- 2026-09-30 · `/restack-discover confidence` (D2 = A) · walk P1 now',
    '- 2026-10-01 · repo setup (D43) · scaffold only',
    '- 2026-10-02 · `/restack-trace` · 4 findings',
  ].join('\n')
  expect(historyEntries(state).map(e => [e.family, e.isGate])).toEqual([
    ['discover', true],
    ['other', true],
    ['documentation', false],
  ])
})

test('a history kept as a table, as a legacy journey has it, gives no strip', () => {
  expect(historyEntries(FIXTURES.legacy['journey-state.md'])).toEqual([])
  expect(rhythm([], '2026-04-20', 80)).toBe(null)
})

test('one cell a day from the first entry to today, the empty days empty', () => {
  const r = rhythm(historyEntries(FIXTURES.band['journey-state.md']), '2026-04-20', 100)!
  expect([r.start, r.end, r.bucket, r.cells.length]).toEqual(['2026-03-01', '2026-04-20', 1, 51])
  expect(r.counts).toEqual({ entries: 3, iterations: 2, gates: 3, days: 51 })
  expect(r.cells[0]).toEqual({ family: 'decisions', isGate: true, count: 1 })
  expect(r.cells[19]).toEqual({ family: 'decisions', isGate: true, count: 1 })
  expect(r.cells[1]).toEqual({ family: undefined, isGate: false, count: 0 })
  expect(r.cells.filter(c => c.count > 0).length).toBe(3)
})

test('more days than the pane holds: a cell a week, then several weeks', () => {
  const entries = historyEntries(FIXTURES.band['journey-state.md'])
  const weekly = rhythm(entries, '2026-04-20', 20)!
  expect([weekly.bucket, weekly.cells.length]).toEqual([7, 8])
  const long: Entry[] = [
    { date: '2025-01-01', command: '/restack-journey start', family: 'decisions', isGate: true, isIterate: false },
  ]
  const multi = rhythm(long, '2026-02-04', 20)!
  expect(multi.counts.days).toBe(400)
  expect([multi.bucket, multi.cells.length]).toEqual([21, 20])
})

test("a cell takes the family most of its entries share; a tie goes to the latest", () => {
  const e = (date: string, command: string): Entry => ({
    date,
    command,
    family: familyOf(command),
    isGate: false,
    isIterate: false,
  })
  const tie = rhythm([e('2026-04-01', '/restack-stressor walk'), e('2026-04-01', '/restack-adr create')], '2026-04-01', 10)!
  expect(tie.cells[0]).toMatchObject({ family: 'decisions', count: 2 })
  const most = rhythm(
    [e('2026-04-01', '/restack-stressor walk'), e('2026-04-01', '/restack-stressor analyze'), e('2026-04-01', '/restack-adr create')],
    '2026-04-01',
    10,
  )!
  expect(most.cells[0]).toMatchObject({ family: 'stressor', count: 3 })
})
