// The pane, on both surfaces: tabs, the lists, and the one button, which
// fills the prompt and never submits or overwrites a draft.

import { expect, mock, test } from 'claude-code/testing'
import type { On } from 'claude-code'

import { FIXTURES } from './fixtures.ts'

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

type Seen = { filled: string[]; toasts: string[]; opened: string[]; closed: string[] }

// The engine, for a project at /work holding the named fixture, drawn on `surface`.
const stub = (on: On, surface: string, fixture: string | null, draft = ''): Seen => {
  const seen: Seen = { filled: [], toasts: [], opened: [], closed: [] }
  mock.store(on)
  const files: Readonly<Record<string, string>> = fixture === null ? {} : FIXTURES[fixture]
  const nameOf = (path: string) => path.replace(/\\/g, '/').match(/\/work\/docs\/journey\/([^/]+)$/)?.[1]
  const has = (path: string) => {
    const name = nameOf(path)

    return name !== undefined && name in files
  }
  on('session.root', () => ({ value: ROOT }))
  on('session.cwd', () => ({ value: ROOT }))
  on('session.surfaces', () => ({ value: [surface] }))
  on('fs.exists', ($, e) => ({ value: has(e.path) }))
  on('fs.stat', ($, e) =>
    has(e.path)
      ? { value: { kind: 'file', size: files[nameOf(e.path)!].length, mtimeMs: 1, isLink: false } }
      : { deny: 'missing' },
  )
  on('fs.read', ($, e) => ({ value: files[nameOf(e.path) ?? ''] ?? '' }))
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

test('where nothing draws a pane, /restack-view prints the line and opens nothing', async ($, on) => {
  const seen = stub(on, 'vscode', 'band')
  const answer = await $.command.run({ command: 'restack-view', args: '' })
  expect(answer.text).toContain('next /restack-stressor analyze')
  expect(seen.opened).toEqual([])
})
