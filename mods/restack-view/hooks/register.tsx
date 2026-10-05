// restack-view: where the ReStack journey stands, on one line above the prompt.
//
// A view and nothing more (ADR-029). It reads docs/journey/ and never writes
// it, never submits, and no skill depends on it: `/restack-journey where`
// gives the same answer wherever this mod is not loaded.

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import { bandParts, bandText, readJourney } from './journey.ts'
import type { Files } from './journey.ts'

const view = atom({ plugin: 'restack-view', key: 'view' } as const, null)
const isBandOn = atom({ plugin: 'restack-view', key: 'isBandOn' } as const, true)

// The band's on/off choice, kept between sessions. The mod's store holds its
// own preferences only, never anything about the engagement.
const BAND_KEY = 'isBandOn'

const FILES = {
  state: 'journey-state.md',
  register: 'assumptions-register.md',
  log: 'decisions-log.md',
} as const

const USAGE_TEXT = 'Usage: /restack-view [band [on|off]]'
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
      return
    }
    const names = Object.entries(FILES)
    const times = await Promise.all(
      names.map(([, name]) => $.fs.stat(join(dir, name)).then(s => s.mtimeMs, () => -1)),
    )
    const seen = dir + '|' + times.join('|')
    if (seen === lastSeen) return

    const files: Files = {}
    for (const [i, [key, name]] of names.entries()) {
      if (times[i] >= 0) files[key as keyof Files] = await $.fs.read(join(dir, name))
    }
    const next = readJourney(files)
    await update($, view, () => next)
    lastSeen = seen
  } catch {
    // A file moved mid-read, or the session is not bound yet: keep the last view.
  }
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
      description: 'ReStack journey view: where the journey stands. band [on|off] shows or hides the line above the prompt',
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

      return { text: current === null ? NO_JOURNEY : bandText(current) }
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
}
