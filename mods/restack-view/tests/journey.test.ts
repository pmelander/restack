// The parser against the journeys journey.py is tested against. The expected
// counts are journey.py's own: rows whose status is in ASK_OPEN, asks among
// them by split_ask, and decisions whose answer is `(open)`.

import { expect, test } from 'claude-code/testing'

import {
  BUDGET,
  askBars,
  bandText,
  bucketOf,
  daysSince,
  budget,
  readDetail,
  readJourney,
  readLog,
  readRegister,
  stateProblem,
  sectionsOf,
} from '../hooks/journey.ts'
import { FIXTURES } from './fixtures.ts'

const filesOf = (name: string) => ({
  state: FIXTURES[name]['journey-state.md'],
  register: FIXTURES[name]['assumptions-register.md'],
  log: FIXTURES[name]['decisions-log.md'],
})

test('a full journey: header fields, next command, and the three counts', () => {
  expect(readJourney(filesOf('band'))).toEqual({
    kind: 'journey',
    terrain: 'Brownfield',
    phase: 'Stressor Analysis',
    confidence: 'Medium',
    next: '/restack-stressor analyze',
    asks: 2,
    open: 3,
    decisions: 1,
  })
})

test('the band line reads in order, with plurals', () => {
  const view = readJourney(filesOf('band'))
  expect(view).toBeDefined()
  expect(bandText(view!)).toBe(
    'Brownfield · Stressor Analysis · Medium · next /restack-stressor analyze · 2 asks · 3 open · 1 decision',
  )
})

test('counts match journey.py on the asks journey', () => {
  expect(readRegister(FIXTURES.asks['assumptions-register.md'])).toEqual({ open: 5, asks: 3 })
  expect(readLog(FIXTURES.asks['decisions-log.md'])).toBe(0)
})

test('a canonical journey without the header fields shows only the counts', () => {
  const view = readJourney(filesOf('canonical'))
  expect(view).toMatchObject({ kind: 'journey', asks: 0, open: 2, decisions: 0 })
  expect(bandText(view!)).toBe('0 asks · 2 open · 0 decisions')
})

test('a legacy journey is named, never guessed at', () => {
  expect(stateProblem(FIXTURES.legacy['journey-state.md'])).toBeDefined()
  expect(typeof readRegister(FIXTURES.legacy['assumptions-register.md'])).toBe('string')
  expect(typeof readLog(FIXTURES.legacy['decisions-log.md'])).toBe('string')
  const view = readJourney(filesOf('legacy'))
  expect(view).toEqual({ kind: 'not-canonical', file: 'journey-state.md' })
  expect(bandText(view!)).toBe('journey-state.md is not canonical: /restack-journey migrate')
})

test('a missing register or log leaves its count out', () => {
  const view = readJourney({ state: FIXTURES.band['journey-state.md'] })
  expect(view).toMatchObject({ kind: 'journey', terrain: 'Brownfield' })
  expect(bandText(view!)).toBe('Brownfield · Stressor Analysis · Medium · next /restack-stressor analyze')
})

test('no journey-state.md is no journey', () => {
  expect(readJourney({ register: FIXTURES.band['assumptions-register.md'] })).toBe(null)
})

test('a template placeholder is no value', () => {
  const state = FIXTURES.band['journey-state.md'].replace('**Terrain Type:** Brownfield', '**Terrain Type:** [Greenfield | Brownfield]')
  expect(readJourney({ state })).toMatchObject({ terrain: undefined, phase: 'Stressor Analysis' })
})

// The shape a long engagement leaves, from a field report of the first live
// run: the terrain a sentence, the phase label qualified, the position dated.
test('a lived-in journey: terms, first clauses, and only the newest position', () => {
  const view = readJourney(filesOf('lived'))
  expect(view).toMatchObject({
    kind: 'journey',
    terrain: 'Greenfield/Brownfield',
    phase: 'Documentation/Review',
    next: '/restack-design-review complete',
  })
  // The superseded subsection's `What's next` and `Confidence level` are not read.
  expect(view).toMatchObject({ confidence: undefined })
  expect(bandText(view!)).toBe(
    'Greenfield/Brownfield · Documentation/Review · next /restack-design-review complete · 2 asks · 3 open · 1 decision',
  )
})

test('a terrain with no template term is cut to its first clause', () => {
  const state = FIXTURES.band['journey-state.md'].replace(
    '**Terrain Type:** Brownfield',
    '**Terrain Type:** A replatform of the depot estate, with a vendor-run controller fleet underneath',
  )
  expect(readJourney({ state })).toMatchObject({ terrain: 'A replatform of the depot estate' })
})

test('a long first clause is capped', () => {
  const state = FIXTURES.band['journey-state.md'].replace(
    '**Current Phase:** Stressor Analysis',
    '**Current Phase:** Stressor analysis of the offline unlock path across every depot',
  )
  const phase = (readJourney({ state }) as { phase?: string }).phase ?? ''
  expect(phase.length).toBe(32)
  expect(phase.endsWith('…')).toBe(true)
})

test('a phase line further down is never read as the phase', () => {
  const state = FIXTURES.lived['journey-state.md'].replace(/^\*\*Current Phase.*$/m, '')
  expect(readJourney({ state })).toMatchObject({ phase: undefined })
})

test('CRLF files read the same as LF', () => {
  const crlf = (s: string) => s.replace(/\n/g, '\r\n')
  const files = filesOf('band')
  expect(readJourney({ state: crlf(files.state), register: crlf(files.register), log: crlf(files.log) })).toEqual(
    readJourney(files),
  )
})

// --- the pane's lists ---------------------------------------------------------

test('the pane lists what the band counts', () => {
  const detail = readDetail(filesOf('band'))
  expect(detail).toBeDefined()
  expect(detail!.asks.map(a => [a.id, a.recipient, a.sent])).toEqual([
    ['A-1', 'Depot operations', 'never asked'],
    ['A-2', 'Locker vendor', 'never asked'],
  ])
  expect(detail!.open.map(r => r.id)).toEqual(['A-1', 'A-2', 'A-3'])
  expect(detail!.decisions).toEqual([
    { id: 'D3', date: '2026-04-18', question: 'Offline unlock: local codes or a cached allow-list?', gate: 'brief' },
  ])
  expect(detail!.header.map(([label]) => label)).toContain('Terrain Type')
})

test('a send is the last one recorded, and unasked cancels it, as journey.py reads them', () => {
  const sent = Object.fromEntries(readDetail(filesOf('asks'))!.asks.map(a => [a.id, a.sent]))
  expect(sent).toEqual({
    'A-1': 'never asked',
    'A-2': 'asked Locker vendor 2026-04-02',
    'A-3': 'asked Locker vendor team 2026-04-15',
  })
  const register =
    FIXTURES.asks['assumptions-register.md'] + '- A-2 · Open · 2026-04-03 · unasked Locker vendor: recorded in error\n'
  const again = readDetail({ ...filesOf('asks'), register })!
  expect(again.asks.find(a => a.id === 'A-2')!.sent).toBe('never asked')
})

test('the position tab is the newest subsection, never a superseded one', () => {
  const where = sectionsOf(readDetail(filesOf('lived'))!, 'position').find(s => s.key === 'where')!
  expect(where.markdown).toContain('**Next move:** `/restack-design-review complete`')
  expect(where.markdown).not.toContain('(superseded)')
  expect(where.markdown).not.toContain('Previous phase line')
  expect(where.markdown!.trimEnd().endsWith('---')).toBe(false)
})

test('the header fields are a two-column list, the history line excluded', () => {
  const journey = sectionsOf(readDetail(filesOf('band'))!, 'position').find(s => s.key === 'journey')!
  expect(journey.fields).toContainEqual(['Terrain Type', 'Brownfield'])
  expect(journey.fields!.map(([label]) => label)).not.toContain('Previous phase line')
})

test('each tab is headed sections of items, and says when there is nothing', () => {
  const detail = readDetail(filesOf('band'))!
  const asks = sectionsOf(detail, 'asks')
  expect(asks.map(s => [s.title, s.count])).toEqual([
    ['Depot operations', 1],
    ['Locker vendor', 1],
  ])
  expect(asks[1].items).toEqual([{ id: 'A-2', meta: 'Partly resolved · never asked', lines: ['the UPS hold-up time'] }])
  const open = sectionsOf(detail, 'assumptions')[0]
  expect([open.title, open.count]).toEqual(['Open assumptions', 3])
  expect(open.items!.find(i => i.id === 'A-3')).toEqual({
    id: 'A-3',
    meta: 'Open',
    lines: ['Reservation lookups stay under 50 ms', '*settles it:* a load test against the staging API'],
  })
  expect(sectionsOf(detail, 'decisions')[0].items).toEqual([
    { id: 'D3', meta: '2026-04-18 · gate: brief', lines: ['Offline unlock: local codes or a cached allow-list?'] },
  ])
  const none = readDetail(filesOf('canonical'))!
  expect(sectionsOf(none, 'asks')).toEqual([{ key: 'asks', title: 'Open asks', count: 0, empty: 'No open asks.' }])
  expect(sectionsOf(none, 'decisions')[0].empty).toBe('No open decisions.')
  expect(sectionsOf(none, 'matrix')).toEqual([])
})

test('a long list stops at sixty items and says where the rest is', () => {
  const detail = readDetail(filesOf('band'))!
  const many = { ...detail, open: Array.from({ length: 75 }, (_, i) => ({ id: `A-${i + 1}`, status: 'Open', assumption: 'x', validates: 'y' })) }
  const open = sectionsOf(many, 'assumptions')[0]
  expect(open.items!.length).toBe(60)
  expect(open.count).toBe(75)
  expect(open.more).toBe('… 15 more: docs/journey/assumptions-register.md')
})

test('a tab stays under the element limit and says where the rest is', () => {
  const rows = Array.from({ length: 400 }, (_, i) => `- **A-${i + 1}** · Open — ${'x'.repeat(60)}`)
  const text = budget(rows, '/restack-journey asks')
  expect(text.length).toBeLessThan(BUDGET)
  expect(text).toMatch(/… \d+ more: \/restack-journey asks$/)
  expect(budget(['one', 'two'], 'elsewhere')).toBe('one\ntwo')
})

// --- waiting (ADR-030, view 2) ---------------------------------------------

const NOW = Date.parse('2026-04-20T12:00:00Z')

test('each open ask is aged from its last send, or from registration when never sent', () => {
  const bars = askBars(readDetail(filesOf('asks'))!, NOW)
  expect(bars.map(b => [b.recipient, b.cells.map(c => [c.id, c.isSent, c.days, c.bucket])])).toEqual([
    ['Depot operations', [['A-1', false, 41, 2]]],
    ['Locker vendor', [['A-2', true, 18, 1]]],
    ['Locker vendor team', [['A-3', true, 5, 0]]],
  ])
  expect(bars[0]).toMatchObject({ never: 1, sent: 0, oldest: 41 })
})

test('a cancelled send ages the ask from its registration again', () => {
  const register =
    FIXTURES.asks['assumptions-register.md'] + '- A-2 · Open · 2026-04-03 · unasked Locker vendor: recorded in error\n'
  const bar = askBars(readDetail({ ...filesOf('asks'), register })!, NOW).find(b => b.recipient === 'Locker vendor')!
  expect(bar.cells).toEqual([{ id: 'A-2', isSent: false, days: 31, bucket: 2 }])
})

test('without status lines, the status date is the registration', () => {
  const register = FIXTURES.band['assumptions-register.md'].split('## Status lines')[0]
  const bar = askBars(readDetail({ ...filesOf('band'), register })!, NOW).find(b => b.recipient === 'Depot operations')!
  expect(bar.cells[0]).toMatchObject({ id: 'A-1', isSent: false, days: 41 })
})

test('the age buckets are 0-6, 7-29 and 30 days and more; unknown is the oldest', () => {
  expect([6, 7, 29, 30, undefined].map(bucketOf)).toEqual([0, 1, 1, 2, 2])
  expect(daysSince('2026-04-20', NOW)).toBe(0)
  expect(daysSince('2026-04-21', NOW)).toBe(0)
  expect(daysSince('not a date', NOW)).toBeUndefined()
})

test('the register by status, in the vocabulary order, every row counted', () => {
  expect(readDetail(filesOf('asks'))!.statuses).toEqual([
    ['Open', 4],
    ['Partly resolved', 1],
    ['Resolved by design (test pending)', 1],
    ['Resolved', 1],
  ])
  const register = FIXTURES.band['assumptions-register.md'].replace('| Resolved | 2026-04-01 |', '| Superseded by D2 | 2026-04-01 |')
  expect(readDetail({ ...filesOf('band'), register })!.statuses).toContainEqual(['Superseded', 1])
})
