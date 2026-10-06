// restack-view: where the ReStack journey stands, on one line above the prompt,
// and in a pane with the open asks, assumptions and decisions.
//
// A view and nothing more (ADR-029). It reads docs/journey/ and never writes
// it, never submits, and no skill depends on it: `/restack-journey where`
// gives the same answer wherever this mod is not loaded.

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { MatrixFile, MatrixState } from '../types'
import { drawBanner } from './banner.tsx'
import { askBars, bandParts, bandText, readDetail, readJourney, registerRows, TABS, tabText } from './journey.ts'
import type { Files } from './journey.ts'
import {
  adrFiles,
  assumptionNumber,
  decisionTitles,
  lookup,
  lookupLines,
  parseRefs,
  residualTitles,
  titleOf,
} from './refs.ts'
import { actorSetChanges, matrixFiles, readClaims, readMatrix, residualsFor, staleness } from './matrix.ts'
import { drawMatrix } from './matrix-view.tsx'
import { drawAskBars, drawStatusBar } from './waiting.tsx'

const view = atom({ plugin: 'restack-view', key: 'view' } as const, null)
const detail = atom({ plugin: 'restack-view', key: 'detail' } as const, null)
const isBandOn = atom({ plugin: 'restack-view', key: 'isBandOn' } as const, true)
const tab = atom({ plugin: 'restack-view', key: 'tab' } as const, 'position')
const matrix = atom({ plugin: 'restack-view', key: 'matrix' } as const, null)
const matrixPick = atom({ plugin: 'restack-view', key: 'matrixPick' } as const, null)
const residualPick = atom({ plugin: 'restack-view', key: 'residualPick' } as const, '*')
const isSortedByTotal = atom({ plugin: 'restack-view', key: 'isSortedByTotal' } as const, false)
const matrixOffset = atom({ plugin: 'restack-view', key: 'matrixOffset' } as const, 0)
const lookupResult = atom({ plugin: 'restack-view', key: 'lookup' } as const, null)

const PANE = 'restack-view'
// The surfaces that draw a pane. Anywhere else, `/restack-view` prints the line.
const DRAWS = ['terminal', 'desktop']

// The band's on/off choice, kept between sessions. The mod's store holds its
// own preferences only, never anything about the engagement.
const BAND_KEY = 'isBandOn'

const FILES = {
  state: 'journey-state.md',
  register: 'assumptions-register.md',
  log: 'decisions-log.md',
} as const

const USAGE_TEXT = 'Usage: /restack-view [band [on|off]]'
const FILLED = 'The next command is in the prompt: read it, then press Enter.'
const NO_JOURNEY = 'No ReStack journey here: no docs/journey/journey-state.md under this project.'

const join = (base: string, ...parts: string[]): string => {
  const sep = base.includes('\\') && !base.includes('/') ? '\\' : '/'

  return [base.replace(/[\\/]+$/, ''), ...parts].join(sep)
}

// The journey's directory: under the project root, else under the working
// directory, as the skills write it.
async function journeyDir($: EngineInterface): Promise<string | undefined> {
  const bases = [await $.session.root(), await $.session.cwd()]
  for (const base of new Set(bases)) {
    const dir = join(base, 'docs', 'journey')
    if (await $.fs.exists(join(dir, FILES.state))) return dir
  }

  return undefined
}

// Refreshes run one after another, never two at once and never dropped, so a
// command that awaits one sees every read started before it.
let pending: Promise<void> = Promise.resolve()
// What the last read saw: the directory and each file's modification time.
// The files are read again only when this changes.
let lastSeen = ''

async function refresh($: EngineInterface): Promise<void> {
  const previous = pending
  let done = () => {}
  pending = new Promise<void>(resolve => {
    done = resolve
  })
  try {
    await previous
    await readOnce($)
  } finally {
    done()
  }
}

async function readOnce($: EngineInterface): Promise<void> {
  try {
    const dir = await journeyDir($)
    if (dir === undefined) {
      lastSeen = ''
      await update($, view, () => null)
      await update($, detail, () => null)
      await update($, matrix, () => null)
      return
    }
    const names = Object.entries(FILES)
    const times = await Promise.all(
      names.map(([, name]) => $.fs.stat(join(dir, name)).then(s => s.mtimeMs, () => -1)),
    )
    // The matrices sit beside the journey, in docs/stressor-analysis/. Listed
    // every time; the one shown is read again only when it or its residuals change.
    const stressorDir = join(dir.replace(/[\\/]journey$/, ''), 'stressor-analysis')
    const entries = await $.fs.list(stressorDir).catch(() => [])
    const mtimeOf = (name: string): number => entries.find(x => x.name === name)?.mtimeMs ?? -1
    const matrices = matrixFiles(entries.filter(x => x.kind === 'file').map(x => x.name))
    const pick = await read($, matrixPick)
    const shown = matrices.find(f => f.name === pick) ?? matrices[0]
    const seen = [
      dir,
      ...times,
      matrices.map(f => f.name).join(','),
      shown?.name ?? '',
      shown === undefined ? -1 : mtimeOf(shown.name),
      shown === undefined ? -1 : mtimeOf(residualsFor(shown.name)),
    ].join('|')
    if (seen === lastSeen) return

    const files: Files = {}
    for (const [i, [key, name]] of names.entries()) {
      if (times[i] >= 0) files[key as keyof Files] = await $.fs.read(join(dir, name))
    }
    const next = readJourney(files)
    const nextDetail = readDetail(files)
    const nextMatrix =
      shown === undefined
        ? { files: matrices }
        : await matrixState($, stressorDir, matrices, shown, files.log ?? '', mtimeOf(residualsFor(shown.name)) >= 0)
    await update($, view, () => next)
    await update($, detail, () => nextDetail)
    await update($, matrix, () => nextMatrix)
    lastSeen = seen
  } catch {
    // A file moved mid-read, or the session is not bound yet: keep the last view.
  }
}

// The shown matrix, its residuals' claims and its staleness; or the first
// problem matrix.py would report, and no grid.
async function matrixState(
  $: EngineInterface,
  dir: string,
  files: MatrixFile[],
  shown: MatrixFile,
  log: string,
  hasResiduals: boolean,
): Promise<MatrixState> {
  const text = await $.fs.read(join(dir, shown.name))
  const { grid, problems } = readMatrix(text)
  if (grid === undefined || problems.length > 0) return { files, file: shown.name, problem: problems[0] }
  const residualsFile = residualsFor(shown.name)
  const claims = hasResiduals ? readClaims(await $.fs.read(join(dir, residualsFile)), grid.actors) : []

  return {
    files,
    file: shown.name,
    grid: {
      ...grid,
      file: shown.name,
      claims,
      residualsFile: hasResiduals ? residualsFile : undefined,
      ...staleness(text, actorSetChanges(log)),
    },
  }
}

// The Assumptions tab's lookup: what rests on one assumption (ADR-030, view 3).
// Read on Enter, not on every refresh, and only what the row cites: the ADRs
// it names, the residual files newest first until every residual it names is
// found, the decisions log if it names a decision, and the matrix the Matrix
// tab shows for its stressors.
async function runLookup($: EngineInterface, input: string): Promise<void> {
  const dir = await journeyDir($)
  if (dir === undefined) {
    await update($, lookupResult, () => ({ kind: 'error' as const, message: NO_JOURNEY }))
    return
  }
  const docs = dir.replace(/[\\/]journey$/, '')
  const rows = registerRows(await $.fs.read(join(dir, FILES.register)).catch(() => ''))
  if (typeof rows === 'string') {
    const message = 'assumptions-register.md is not canonical: /restack-journey migrate'
    await update($, lookupResult, () => ({ kind: 'error' as const, message }))
    return
  }
  const n = assumptionNumber(input)
  const row = n === undefined ? undefined : rows.find(r => assumptionNumber(r.id) === n)
  const refs = parseRefs(row?.depends ?? '')

  const adrs = new Map<number, { file: string; title?: string }>()
  if (refs.adrs.length > 0) {
    const listed = await $.fs.list(join(docs, 'adr')).catch(() => [])
    const files = adrFiles(listed.filter(x => x.kind === 'file').map(x => x.name))
    for (const a of refs.adrs) {
      const file = files.get(a)
      if (file === undefined) continue
      adrs.set(a, { file, title: titleOf(await $.fs.read(join(docs, 'adr', file)).catch(() => '')) })
    }
  }

  const residuals = new Map<string, { file: string; title: string }>()
  if (refs.residuals.length > 0) {
    const listed = await $.fs.list(join(docs, 'stressor-analysis')).catch(() => [])
    const names = matrixFiles(listed.map(x => x.name.replace(/^residuals-/, 'matrix-')))
      .map(f => f.name.replace(/^matrix-/, 'residuals-'))
      .filter(name => listed.some(x => x.name === name))
    for (const name of names) {
      if (refs.residuals.every(r => residuals.has(r))) break
      const titles = residualTitles(await $.fs.read(join(docs, 'stressor-analysis', name)).catch(() => ''))
      for (const r of refs.residuals) {
        const title = titles.get(r)
        if (!residuals.has(r) && title !== undefined) residuals.set(r, { file: name, title })
      }
    }
  }

  const decisions = refs.decisions.length > 0 ? decisionTitles(await $.fs.read(join(dir, FILES.log)).catch(() => '')) : new Map<number, string>()
  const grid = (await read($, matrix))?.grid
  const result = lookup(input, rows, { adrs, residuals, decisions, grid })
  await update($, lookupResult, () => result)
}

// The Matrix tab's Select: show another matrix from its first stressor, then read it.
async function pickMatrix($: EngineInterface, name: string): Promise<void> {
  await update($, matrixPick, () => name)
  await update($, matrixOffset, () => 0)
  await refresh($)
}

// The pane's one button. It never submits, and never writes over a draft:
// with anything typed, the command goes in a toast instead.
async function fillNext($: EngineInterface, command: string): Promise<void> {
  const box = await $.prompt.read()
  if (box.text.trim() !== '') {
    $.ui.toast(`Your draft is kept. Next: ${command}`)
    return
  }
  const filled = await $.prompt.fill({ text: command })
  if (!filled.isFilled) {
    $.ui.toast(`Next: ${command}`)
    return
  }
  // Back to the prompt, where the command waits for the architect's Enter.
  await $.ui.close({ id: PANE })
  $.ui.toast(FILLED)
}

async function loadBand($: EngineInterface): Promise<void> {
  const stored = await $.store.get(BAND_KEY)
  if (typeof stored === 'boolean') await update($, isBandOn, () => stored)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await loadBand($)
    const ran = await next(e)
    void refresh($)
    // Registered last: a name refused here would skip the rest of this hook.
    await $.command.register({
      name: 'restack-view',
      description: 'ReStack journey view: open the pane of open asks, assumptions and decisions. band [on|off] shows or hides the line above the prompt',
      argumentHint: '[band [on|off]]',
      immediate: true,
    })

    return ran
  })

  // /clear, /resume and /branch reset $.state and do not fire session.start.
  on('classic.SessionStart', { source: ['clear', 'resume', 'fork'] }, async ($, e, next) => {
    await loadBand($)
    lastSeen = ''
    void refresh($)

    return next(e)
  })

  // After each turn: the turn may have written the journey files.
  on('session.measure', async ($, e, next) => {
    void refresh($)

    return next(e)
  })

  on('command.run', { command: 'restack-view' }, async ($, e) => {
    const args = e.args.trim().toLowerCase().split(/\s+/).filter(Boolean)
    if (args.length === 0) {
      lastSeen = ''
      await refresh($)
      const current = await read($, view)
      const surfaces = await $.session.surfaces()
      if (!surfaces.some(s => DRAWS.includes(s))) {
        return { text: current === null ? NO_JOURNEY : bandText(current) }
      }
      await $.ui.open({ id: PANE, title: 'ReStack journey', focus: true, closeOnEscape: true })

      return {}
    }
    if (args[0] !== 'band' || args.length > 2 || (args[1] !== undefined && args[1] !== 'on' && args[1] !== 'off')) {
      return { text: USAGE_TEXT }
    }
    const isOn = args[1] === undefined ? !(await read($, isBandOn)) : args[1] === 'on'
    await update($, isBandOn, () => isOn)
    await $.store.set(BAND_KEY, isOn)

    return { text: `Journey band ${isOn ? 'on' : 'off'}.` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    if (e.props.hasSurvey || !(await read($, isBandOn))) return next(e)
    const current = await read($, view)
    if (current === null) return next(e)

    const { Box, Text } = $.ui.resolve(e)
    const { lead, next: command, tail } = bandParts(current)
    const isWarning = current.kind === 'not-canonical'
    const mine = (
      <Text key="restack-view" wrap="truncate">
        <Text dimColor>restack </Text>
        <Text color={isWarning ? 'warning' : undefined}>{lead}</Text>
        {command !== undefined && <Text dimColor>{isWarning ? ': ' : lead ? ' · next ' : 'next '}</Text>}
        {command !== undefined && <Text color="suggestion">{command}</Text>}
        {tail !== '' && <Text dimColor> · {tail}</Text>}
      </Text>
    )
    // Share the band: what the mods after this one draw stays, under this line.
    const theirs = await next(e)

    return (
      <Box flexDirection="column">
        {mine}
        {theirs}
      </Box>
    )
  })

  on('ui.render', { component: 'Pane' }, async ($, e, next) => {
    if (e.requestId !== PANE) return next(e)
    const { Box, Text, Button, Markdown, Select, Svg, Input } = $.ui.resolve(e)
    const current = await read($, view)
    const lists = await read($, detail)
    const open = await read($, tab)
    const banner = drawBanner({ Box, Text, Svg }, e.surface, e.props.bodyColumns)

    if (current === null) {
      return (
        <Box flexDirection="column">
          {banner}
          <Text dimColor>{NO_JOURNEY}</Text>
        </Box>
      )
    }
    if (current.kind === 'not-canonical' || lists === null) {
      return (
        <Box flexDirection="column">
          {banner}
          <Text color="warning">{bandText(current)}</Text>
        </Box>
      )
    }
    const command = current.next
    const els = { Box, Text }
    const width = e.props.bodyColumns
    // Ages are counted to now, not to the last read: a day passes without a file changing.
    const bars = open === 'asks' && lists.asks.length > 0 ? askBars(lists, await $.clock.now()) : []
    const found = open === 'assumptions' ? await read($, lookupResult) : null
    const lookupView =
      found === null ? null : (
        <Box flexDirection="column">
          {lookupLines(found).map((line, i) =>
            line.tone === 'head' ? (
              <Text key={`lookup-${i}`} bold wrap="wrap">
                {line.text}
              </Text>
            ) : line.tone === 'missing' ? (
              <Text key={`lookup-${i}`} italic dimColor wrap="wrap">
                {line.text}
              </Text>
            ) : line.tone === 'found' ? (
              <Text key={`lookup-${i}`} wrap="wrap">
                {line.text}
              </Text>
            ) : (
              <Text key={`lookup-${i}`} dimColor wrap="wrap">
                {line.text}
              </Text>
            ),
          )}
        </Box>
      )
    const matrixPicks = {
      residual: await read($, residualPick),
      isSortedByTotal: await read($, isSortedByTotal),
      offset: await read($, matrixOffset),
      onFile: (name: string) => {
        void pickMatrix($, name)
      },
      onResidual: (value: string) => {
        void update($, residualPick, () => value)
      },
      onSort: () => {
        void update($, isSortedByTotal, value => !value)
        void update($, matrixOffset, () => 0)
      },
      onPage: (offset: number) => {
        void update($, matrixOffset, () => offset)
      },
    }

    return (
      <Box flexDirection="column">
        {banner}
        <Box flexDirection="row" columnGap={3}>
          {TABS.map(([name, label], i) => (
            <Button
              key={`tab-${name}`}
              label={label}
              hotkey={String(i + 1)}
              plain
              dimColor={open !== name}
              onPress={() => update($, tab, () => name)}
            />
          ))}
        </Box>
        <Text> </Text>
        {open === 'position' && command !== undefined && (
          <Box flexDirection="row" columnGap={1}>
            <Button key="fill-next" label="Put the next command in the prompt" hotkey="n" onPress={() => fillNext($, command)} />
            <Text dimColor>{command}</Text>
          </Box>
        )}
        {bars.length > 0 && drawAskBars(els, bars, e.surface, width)}
        {open === 'assumptions' && drawStatusBar(els, lists.statuses, e.surface, width)}
        {open === 'assumptions' && (
          <Box flexDirection="column">
            <Input
              key="lookup"
              label="What rests on"
              placeholder="an assumption, such as A-12, then Enter"
              value=""
              submitLabel="look up"
              onSubmit={value => {
                void runLookup($, value)
              }}
            />
            {lookupView}
            <Text> </Text>
          </Box>
        )}
        {open === 'matrix' ? (
          drawMatrix({ Box, Text, Button, Select, Svg }, await read($, matrix), matrixPicks, e.surface, width)
        ) : (
          <Markdown key={`body-${open}`} text={tabText(lists, open)} />
        )}
      </Box>
    )
  })
}
