// The pane, on both surfaces: tabs, the lists, and the one button, which
// fills the prompt and never submits or overwrites a draft.

import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import { FIXTURES, MATRIX_FIXTURES } from './fixtures.ts'

const SURFACES = ['terminal', 'desktop'] as const
const ROOT = '/work'

// The tree's text in document order, with a Button's `label` and a Markdown
// element's `text`, which are props rather than children.
const textOf = (node: unknown): string => {
  if (typeof node === 'string') return node
  if (Array.isArray(node)) return node.map(textOf).join('')
  if (node === null || typeof node !== 'object') return ''
  const el = node as { children?: unknown; props?: { text?: unknown; label?: unknown } }
  const own = [el.props?.label, el.props?.text].filter((v): v is string => typeof v === 'string').join(' ')

  return own + ('children' in el ? textOf(el.children) : '')
}

// Every `color` in the tree, with whether that element is dimmed.
const colorsOf = (node: unknown, out: Array<[string, boolean]> = []): Array<[string, boolean]> => {
  if (Array.isArray(node)) node.forEach(n => colorsOf(n, out))
  else if (node !== null && typeof node === 'object') {
    const el = node as { children?: unknown; props?: { color?: unknown; dimColor?: unknown } }
    if (typeof el.props?.color === 'string') out.push([el.props.color, el.props.dimColor === true])
    colorsOf(el.children, out)
  }

  return out
}

// headroom's traffic-light keys: a verdict, which ADR-030 rules out.
const VERDICT_COLORS = ['success', 'warning', 'error']

type Seen = { filled: string[]; toasts: string[]; opened: string[]; closed: string[] }

// The engine, for a project at /work holding the named journey fixture in
// docs/journey/ and `analysis` in docs/stressor-analysis/, drawn on `surface`.
const stub = (
  on: On,
  surface: string,
  fixture: string | null | Record<string, string>,
  draft = '',
  analysis: Record<string, string> = {},
): Seen => {
  const seen: Seen = { filled: [], toasts: [], opened: [], closed: [] }
  mock.store(on)
  mock.clock(on, { now: Date.parse('2026-04-20T12:00:00Z') })
  const dirs: Record<string, Readonly<Record<string, string>>> = {
    journey: fixture === null ? {} : typeof fixture === 'string' ? FIXTURES[fixture] : fixture,
    'stressor-analysis': analysis,
  }
  // The engine hands a stub the path resolved and absolute, so match its end.
  const where = (path: string) => path.replace(/\\/g, '/').match(/\/work\/docs\/(journey|stressor-analysis)(?:\/([^/]+))?$/)
  const fileAt = (path: string): string | undefined => {
    const m = where(path)

    return m && m[2] !== undefined ? dirs[m[1]][m[2]] : undefined
  }
  on('session.root', () => ({ value: ROOT }))
  on('session.cwd', () => ({ value: ROOT }))
  on('session.surfaces', () => ({ value: [surface] }))
  on('fs.exists', ($, e) => ({ value: fileAt(e.path) !== undefined }))
  on('fs.stat', ($, e) => {
    const text = fileAt(e.path)

    return text !== undefined ? { value: { kind: 'file', size: text.length, mtimeMs: 1, isLink: false } } : { deny: 'missing' }
  })
  on('fs.read', ($, e) => ({ value: fileAt(e.path) ?? '' }))
  on('fs.list', ($, e) => {
    const m = where(e.path)
    if (!m || m[2] !== undefined || Object.keys(dirs[m[1]]).length === 0) return { deny: 'missing' }

    return {
      value: Object.entries(dirs[m[1]]).map(([name, text]) => ({ name, kind: 'file', size: text.length, mtimeMs: 1, isLink: false })),
    }
  })
  on('ui.open', ($, e) => {
    seen.opened.push(e.id)
    return { value: { isPlaced: true } }
  })
  on('ui.close', ($, e) => {
    seen.closed.push(e.id)
    return { value: undefined }
  })
  on('ui.toast', ($, e) => {
    seen.toasts.push(e.text)
    return { value: undefined }
  })
  on('prompt.read', () => ({ value: { text: draft, cursor: draft.length } }))
  on('prompt.fill', ($, e) => {
    seen.filled.push(e.text)
    return { isFilled: true, text: e.text, cursor: e.text.length }
  })

  return seen
}

const PANE = {
  plugin: 'restack-view',
  component: 'Pane',
  requestId: 'restack-view',
  viewport: { columns: 120, rows: 40 },
  props: {
    title: 'ReStack journey',
    isFocused: true,
    bodyColumns: 80,
    placement: 'inline',
    scroll: { offset: 0, bodyRows: 30 },
    view: {},
  },
} as const

for (const surface of SURFACES) {
  test(`/restack-view opens the pane, which shows the position first, on ${surface}`, async ($, on) => {
    const seen = stub(on, surface, 'band')
    const answer = await $.command.run({ command: 'restack-view', args: '' })
    expect(answer.text).toBeUndefined()
    expect(seen.opened).toEqual(['restack-view'])

    const ui = await $.ui.mount({ ...PANE, surface })
    const tree = textOf(await ui.drawn())
    expect(tree).toContain('Position')
    expect(tree).toContain('Decisions')
    expect(tree).toContain("**What's next:**")
    expect(tree).toContain('/restack-stressor analyze')
  })

  test(`the tabs switch between the lists, on ${surface}`, async ($, on) => {
    stub(on, surface, 'band')
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })

    await ui.press({ key: 'tab-asks' })
    expect(textOf(await ui.drawn())).toContain('### Depot operations (1)')
    await ui.press({ key: 'tab-assumptions' })
    expect(textOf(await ui.drawn())).toContain('Reservation lookups stay under 50 ms')
    await ui.press({ key: 'tab-decisions' })
    expect(textOf(await ui.drawn())).toContain('**D3**')
    expect(await ui.find({ key: 'fill-next' })).toBeUndefined()
  })

  test(`the button fills an empty prompt, closes the pane, and submits nothing, on ${surface}`, async ($, on) => {
    const seen = stub(on, surface, 'band')
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })

    await ui.press({ key: 'fill-next' })
    expect(seen.filled).toEqual(['/restack-stressor analyze'])
    expect(seen.closed).toEqual(['restack-view'])
  })

  test(`the button never writes over a draft, on ${surface}`, async ($, on) => {
    const seen = stub(on, surface, 'band', 'half a thought')
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })

    await ui.press({ key: 'fill-next' })
    expect(seen.filled).toEqual([])
    expect(seen.closed).toEqual([])
    expect(seen.toasts).toEqual(['Your draft is kept. Next: /restack-stressor analyze'])
  })

  test(`a legacy journey shows what the band shows, and no button, on ${surface}`, async ($, on) => {
    stub(on, surface, 'legacy')
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })
    expect(textOf(await ui.drawn())).toContain('journey-state.md is not canonical: /restack-journey migrate')
    expect(await ui.find({ key: 'fill-next' })).toBeUndefined()
  })
}

for (const surface of SURFACES) {
  test(`the Asks tab opens with one waiting bar per recipient, on ${surface}`, async ($, on) => {
    stub(on, surface, 'asks')
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })
    await ui.press({ key: 'tab-asks' })
    const tree = textOf(await ui.drawn())
    expect(tree).toContain('Depot operations')
    expect(tree).toContain('1 · never asked 1 · 41 d')
    expect(tree).toContain('1 · sent 1 · 18 d')
    expect(tree).toContain('7–29 d')
    expect(tree.indexOf('41 d')).toBeLessThan(tree.indexOf('### Depot operations'))

    // One colour per age bucket (41, 18 and 5 days), and no verdicts.
    const colors = colorsOf(await ui.drawn())
    for (const key of ['claude', 'autoAccept', 'planMode']) expect(colors.map(([c]) => c)).toContain(key)
    for (const key of VERDICT_COLORS) expect(colors.map(([c]) => c)).not.toContain(key)
  })

  test(`a recipient with fewer asks draws a shorter meter on the dimmed track, on ${surface}`, async ($, on) => {
    // A second ask for Depot operations: its meter is full, the others half.
    const row = '| A-8 | Depots hold spare lockers | survey | Ask Depot operations: the spare count | R1 | Open | 2026-04-12 |'
    const register = FIXTURES.asks['assumptions-register.md']
      .replace('\n\n## Status lines', `\n${row}\n\n## Status lines`)
      .concat('- A-8 · Open · 2026-04-12 · registered\n')
    stub(on, surface, { ...FIXTURES.asks, 'assumptions-register.md': register })
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })
    await ui.press({ key: 'tab-asks' })
    expect(textOf(await ui.drawn())).toContain('2 · never asked 2 · 41 d')
    expect(colorsOf(await ui.drawn())).toContainEqual(['inactive', true])
  })

  test(`the Assumptions tab opens with the register by status, on ${surface}`, async ($, on) => {
    stub(on, surface, 'asks')
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })
    await ui.press({ key: 'tab-assumptions' })
    const tree = textOf(await ui.drawn())
    expect(tree).toContain(' Open 4')
    expect(tree).toContain(' Resolved by design (test pending) 1')
    expect(tree).toContain('7 rows in the register')
    const colors = colorsOf(await ui.drawn()).map(([c]) => c)
    for (const key of ['claude', 'autoAccept', 'planMode', 'ide']) expect(colors).toContain(key)
    for (const key of VERDICT_COLORS) expect(colors).not.toContain(key)
  })

  test(`no bars on the Position and Decisions tabs, on ${surface}`, async ($, on) => {
    stub(on, surface, 'asks')
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface })
    expect(textOf(await ui.drawn())).not.toContain('rows in the register')
    await ui.press({ key: 'tab-decisions' })
    expect(textOf(await ui.drawn())).not.toContain('never asked ·')
  })
}

// --- the banner ------------------------------------------------------------------

for (const surface of SURFACES) {
  test(`the banner tops the pane, and leaves a narrow pane alone, on ${surface}`, async ($, on) => {
    stub(on, surface, 'band')
    await $.command.run({ command: 'restack-view', args: '' })
    const wide = await $.ui.mount({ ...PANE, surface })
    if (surface === 'terminal') {
      expect(textOf(await wide.drawn())).toContain('/_/ |_|')
    } else {
      const svg = await wide.find({ type: 'Svg' })
      expect((svg as { props: { source: string } }).props.source).toContain('linearGradient')
    }
    await wide.unmount()

    const narrow = await $.ui.mount({ ...PANE, surface, props: { ...PANE.props, bodyColumns: 30 } })
    expect(textOf(await narrow.drawn())).not.toContain('/_/ |_|')
    expect(await narrow.find({ type: 'Svg' })).toBeUndefined()
  })
}

// --- the Matrix tab (ADR-030, view 1) -------------------------------------------

// The fixture journey's log, plus a later decision that changed the actor set.
const LOG_WITH_D5 =
  FIXTURES.band['decisions-log.md'] +
  '\n## D5 · 2026-04-19 · Add the event cluster\n\n- **Gate:** brief\n- **Answer:** yes\n- **Rationale:** —\n- **Changes the actor set:** yes\n- **Supersedes:** —\n'
const ANALYSIS = {
  'matrix-2026-04-10-iter1.md': MATRIX_FIXTURES['matrix-iter1.md'],
  'residuals-2026-04-10-iter1.md': MATRIX_FIXTURES['residuals-iter1.md'],
  'matrix-2026-04-01.md': MATRIX_FIXTURES['broken.md'],
  'stressors-2026-04-01.md': '# Stressors\n',
}

const openMatrix = async ($: Parameters<Parameters<typeof test>[1]>[0], surface: (typeof SURFACES)[number]) => {
  await $.command.run({ command: 'restack-view', args: '' })
  const ui = await $.ui.mount({ ...PANE, surface })
  await ui.press({ key: 'tab-matrix' })

  return ui
}

for (const surface of SURFACES) {
  test(`with no matrix yet, the tab says where one comes from, on ${surface}`, async ($, on) => {
    stub(on, surface, 'band')
    const ui = await openMatrix($, surface)
    expect(textOf(await ui.drawn())).toContain('No impact matrix scored yet. /restack-stressor analyze')
  })

  test(`the newest matrix is drawn, stale where the eye lands, on ${surface}`, async ($, on) => {
    stub(on, surface, { ...FIXTURES.band, 'decisions-log.md': LOG_WITH_D5 }, '', ANALYSIS)
    const ui = await openMatrix($, surface)
    const tree = textOf(await ui.drawn())
    expect(tree).toContain('iteration 1 · 2026-04-10 · 5 stressors × 4 actors · 11 cells (2 unknown)')
    expect(tree).toContain(' · scored at D2 · stale: D5 changed the actor set')
    expect(colorsOf(await ui.drawn())).toContainEqual(['claude', false])
    expect(tree).toContain('claimed by residuals-2026-04-10-iter1.md')
    // The same text on both surfaces: one lane per actor, the window named.
    expect(tree).toContain('S-1 … S-5 (1–5 of 5 stressors)')
    expect(tree).toContain('RS')
    expect(tree).toContain('3 claimed')
    expect(await ui.find({ type: 'Raster' })).toBeUndefined()
  })

  test(`the Select shows an older matrix, and a rejected one only as its problem, on ${surface}`, async ($, on) => {
    stub(on, surface, 'band', '', ANALYSIS)
    const ui = await openMatrix($, surface)
    await ui.select({ key: 'matrix-file', value: 'matrix-2026-04-01.md' })
    const tree = textOf(await ui.drawn())
    expect(tree).toContain('matrix-2026-04-01.md: 1 × Locker = 2: scoring is 0 or 1. Not drawn')
    expect(await ui.find({ type: 'Raster' })).toBeUndefined()
  })

  test(`a matrix wider than the pane pages, on ${surface}`, async ($, on) => {
    stub(on, surface, 'band', '', { 'matrix-2026-04-12-iter3.md': MATRIX_FIXTURES['matrix-iter3.md'] })
    await $.command.run({ command: 'restack-view', args: '' })
    const ui = await $.ui.mount({ ...PANE, surface, props: { ...PANE.props, bodyColumns: 20 } })
    await ui.press({ key: 'tab-matrix' })
    expect(textOf(await ui.drawn())).toContain('S-1 … S-10 (1–10 of 12 stressors)')
    expect(await ui.find({ key: 'matrix-prev' })).toBeUndefined()
    await ui.press({ key: 'matrix-next' })
    expect(textOf(await ui.drawn())).toContain('S-3 … S-12 (3–12 of 12 stressors)')
    await ui.press({ key: 'matrix-prev' })
    expect(textOf(await ui.drawn())).toContain('(1–10 of 12 stressors)')
  })

  test(`sorting by total is a toggle, on ${surface}`, async ($, on) => {
    stub(on, surface, 'band', '', ANALYSIS)
    const ui = await openMatrix($, surface)
    expect(textOf(await ui.drawn())).toContain('Sort by total')
    await ui.press({ key: 'matrix-sort' })
    expect(textOf(await ui.drawn())).toContain('File order')
  })
}

test('where nothing draws a pane, /restack-view prints the line and opens nothing', async ($, on) => {
  const seen = stub(on, 'vscode', 'band')
  const answer = await $.command.run({ command: 'restack-view', args: '' })
  expect(answer.text).toContain('next /restack-stressor analyze')
  expect(seen.opened).toEqual([])
})
