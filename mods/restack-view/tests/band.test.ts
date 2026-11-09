// The band and /restack-view, on both surfaces, with the journey files
// answered from the fixtures in place of the disk.

import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import { FIXTURES } from './fixtures.ts'

const SURFACES = ['terminal', 'desktop'] as const
const ROOT = '/work'
const OTHERS = 'drawn by another mod'
const LINE = 'Brownfield · Stressor Analysis · Medium · next /restack-stressor analyze · 2 asks · 3 open · 1 decision'

// The tree's text in document order.
const textOf = (node: unknown): string =>
  typeof node === 'string'
    ? node
    : Array.isArray(node)
      ? node.map(textOf).join('')
      : node && typeof node === 'object' && 'children' in node
        ? textOf((node as { children: unknown }).children)
        : ''

// What the band's button asked of the engine, and the panes it holds open.
type Panes = { opened: string[]; closed: string[]; up: Set<string> }

// Stands in for the engine: a project at /work holding the named fixture, or
// no journey at all; an in-memory store; and another band mod beneath this one.
const stub = (on: On, fixture: string | null, stored: Record<string, unknown> = {}): Panes => {
  const panes: Panes = { opened: [], closed: [], up: new Set() }
  mock.store(on, stored)
  const files = fixture === null ? {} : FIXTURES[fixture]
  // The engine hands a stub the path resolved and absolute, so match its end.
  const nameOf = (path: string) => {
    const m = path.replace(/\\/g, '/').match(/\/work\/docs\/journey\/([^/]+)$/)

    return m?.[1]
  }
  on('session.root', () => ({ value: ROOT }))
  on('session.cwd', () => ({ value: ROOT }))
  // Nothing draws a pane here, so /restack-view prints the line: the pane has its own tests.
  on('session.surfaces', () => ({ value: [] }))
  on('fs.exists', ($, e) => ({ value: nameOf(e.path) in files }))
  on('fs.stat', ($, e) => {
    const name = nameOf(e.path)

    return name !== undefined && name in files
      ? { value: { kind: 'file', size: files[name].length, mtimeMs: 1, isLink: false } }
      : { deny: 'missing' }
  })
  on('fs.read', ($, e) => ({ value: files[nameOf(e.path) ?? ''] ?? '' }))
  on('command.register', () => ({ value: undefined }))
  on('session.start', () => ({ cwd: ROOT }))
  on('classic.SessionStart', () => ({}))
  on('ui.render', () => ({ type: 'Text', props: {}, children: [OTHERS] }))
  on('ui.open', ($, e) => {
    panes.opened.push(e.id)
    panes.up.add(e.id)
    return { value: { isPlaced: true } }
  })
  on('ui.close', ($, e) => {
    panes.closed.push(e.id)
    panes.up.delete(e.id)
    return { value: undefined }
  })
  on('ui.panes', () => ({
    value: [...panes.up].map(id => ({ id, title: id, isShown: true, isFocused: false, isPlaced: true })),
  }))

  return panes
}

const mountBand = ($: Parameters<Parameters<typeof test>[1]>[0], surface: (typeof SURFACES)[number]) =>
  $.ui.mount({
    plugin: 'restack-view',
    surface,
    component: 'AbovePrompt',
    props: { hasSurvey: false, isWorking: false, maxRows: 4, bodyColumns: 120 },
    viewport: { columns: 120, rows: 30 },
  })

for (const surface of SURFACES) {
  test(`draws the journey line above the prompt, and keeps the other mods' band, on ${surface}`, async ($, on) => {
    stub(on, 'band')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const answer = await $.command.run({ command: 'restack-view', args: '' })
    expect(answer.text).toBe(LINE)

    const tree = textOf(await (await mountBand($, surface)).drawn())
    expect(tree).toContain('restack ' + LINE)
    expect(tree).toContain(OTHERS)
    expect(tree.indexOf('restack ')).toBeLessThan(tree.indexOf(OTHERS))
  })

  test(`band off hides the line and is remembered, on ${surface}`, async ($, on) => {
    stub(on, 'band')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const off = await $.command.run({ command: 'restack-view', args: 'band off' })
    expect(off.text).toBe('Journey band off.')

    const tree = textOf(await (await mountBand($, surface)).drawn())
    expect(tree).not.toContain('restack ')
    expect(tree).toContain(OTHERS)
  })

  test(`a stored off survives /clear, on ${surface}`, async ($, on) => {
    stub(on, 'band', { isBandOn: false })
    await $.classic.SessionStart({ source: 'clear' })
    await $.command.run({ command: 'restack-view', args: '' })

    const tree = textOf(await (await mountBand($, surface)).drawn())
    expect(tree).not.toContain('restack ')
  })

  test(`a legacy journey says so and names the fix, on ${surface}`, async ($, on) => {
    stub(on, 'legacy')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    await $.command.run({ command: 'restack-view', args: '' })

    const tree = textOf(await (await mountBand($, surface)).drawn())
    expect(tree).toContain('journey-state.md is not canonical: /restack-journey migrate')
  })

  test(`a stale position says so and offers where, on ${surface}`, async ($, on) => {
    stub(on, 'stale')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const answer = await $.command.run({ command: 'restack-view', args: '' })
    expect(answer.text).toBe(
      'Greenfield · Documentation/Review · position stale since 2026-04-20 · next /restack-journey where · 1 decision',
    )

    const tree = textOf(await (await mountBand($, surface)).drawn())
    expect(tree).toContain('restack ' + answer.text)
  })

  test(`a recorded wait says who, with no command, on ${surface}`, async ($, on) => {
    stub(on, 'waiting')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const answer = await $.command.run({ command: 'restack-view', args: '' })
    expect(answer.text).toBe('Greenfield · Documentation/Review · waiting on depot operations and the locker vendor · 1 decision')

    const tree = textOf(await (await mountBand($, surface)).drawn())
    expect(tree).toContain('restack ' + answer.text)
  })

  test(`the band's button opens the view and closes it again, on ${surface}`, async ($, on) => {
    const panes = stub(on, 'band')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const band = await mountBand($, surface)
    expect((await band.find({ key: 'toggle-view' }))?.props.label).toBe('Open view')

    await band.press({ key: 'toggle-view' })
    expect(panes.opened).toEqual(['restack-view'])
    expect((await band.find({ key: 'toggle-view' }))?.props.label).toBe('Close view')

    await band.press({ key: 'toggle-view' })
    expect(panes.closed).toEqual(['restack-view'])
    expect((await band.find({ key: 'toggle-view' }))?.props.label).toBe('Open view')
  })

  test(`a pane already gone is opened again, not closed, on ${surface}`, async ($, on) => {
    const panes = stub(on, 'band')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const band = await mountBand($, surface)
    await band.press({ key: 'toggle-view' })
    // Gone from the engine's record, as after its mark or Esc.
    panes.up.delete('restack-view')
    await band.press({ key: 'toggle-view' })
    expect(panes.opened).toEqual(['restack-view', 'restack-view'])
    expect(panes.closed).toEqual([])
  })

  test(`a pane still up after a reload starts the button at close, on ${surface}`, async ($, on) => {
    const panes = stub(on, 'band')
    panes.up.add('restack-view')
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const band = await mountBand($, surface)
    expect((await band.find({ key: 'toggle-view' }))?.props.label).toBe('Close view')
  })

  test(`no journey, no line, on ${surface}`, async ($, on) => {
    stub(on, null)
    await $.session.start({ surface, isInteractive: true, cwd: ROOT })
    const answer = await $.command.run({ command: 'restack-view', args: '' })
    expect(answer.text).toContain('No ReStack journey here')

    const tree = textOf(await (await mountBand($, surface)).drawn())
    expect(tree).toBe(OTHERS)
  })
}

test('a bad argument prints the usage', async ($, on) => {
  stub(on, 'band')
  const answer = await $.command.run({ command: 'restack-view', args: 'pane please' })
  expect(answer.text).toBe('Usage: /restack-view [band [on|off]]')
})

test('band with no on or off toggles', async ($, on) => {
  stub(on, 'band')
  expect((await $.command.run({ command: 'restack-view', args: 'band' })).text).toBe('Journey band off.')
  expect((await $.command.run({ command: 'restack-view', args: 'band' })).text).toBe('Journey band on.')
})
