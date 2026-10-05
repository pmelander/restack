// The parser against the journeys journey.py is tested against. The expected
// counts are journey.py's own: rows whose status is in ASK_OPEN, asks among
// them by split_ask, and decisions whose answer is `(open)`.

import { expect, test } from 'claude-code/testing'

import { bandText, readJourney, readLog, readRegister, stateProblem } from '../hooks/journey.ts'
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

test('CRLF files read the same as LF', () => {
  const crlf = (s: string) => s.replace(/\n/g, '\r\n')
  const files = filesOf('band')
  expect(readJourney({ state: crlf(files.state), register: crlf(files.register), log: crlf(files.log) })).toEqual(
    readJourney(files),
  )
})
