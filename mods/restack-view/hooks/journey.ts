// Reads the three journey files in the canonical shape journey.py writes
// (ADR-023), and nothing else. Pure functions over text: no `$`, so the tests
// run them straight against the fixtures journey.py is tested against.
//
// The rules mirror journey.py's: a change to the canonical shape there that
// does not reach here fails tests/journey.test.ts (ADR-029, decision point 4).

import type { Journey, View } from '../types'

export type Files = { state?: string; register?: string; log?: string }

// The register's seven columns, as journey.py's COLUMNS.
const COLUMNS = ['ID', 'Assumption', 'Source', 'Validates it', 'Depends on it', 'Status', 'Status date']
const A_ROW = /^\s*\|\s*\**\s*A-(\d+)\s*\**\s*\|/
const STATUS_LINE = /^\s*-\s*A-(\d+)\s*·\s*([^·]+?)\s*·\s*(\d{4}-\d{2}-\d{2}|—)\s*·?\s*(.*)$/
const UPDATE_HEADING = /^#+\s*updates?\b/i
const D_HEADING = /^## D(\d+) · (\d{4}-\d{2}-\d{2}) · (.*)$/
const LEGACY_D_HEADING = /^## (\d{4}-\d{2}-\d{2}):\s*D(\d+)\b/
const ASK_PREFIX = /^Ask ([^:|*`]{1,40}?):\s*(.*)$/s
// The two statuses journey.py counts as still open (ASK_OPEN).
const OPEN = ['open', 'partly resolved']

const lines = (text: string): string[] => text.replace(/\r\n?/g, '\n').split('\n')

// journey.py's strip_md: emphasis, code ticks and edge underscores.
const stripMd = (text: string): string => text.replace(/\*+|`|(?<!\w)_+|_+(?!\w)/g, '').trim()

const splitRow = (line: string): string[] => {
  let body = line.trim()
  if (body.startsWith('|')) body = body.slice(1)
  if (body.endsWith('|') && !body.endsWith('\\|')) body = body.slice(0, -1)

  return body.split(/(?<!\\)\|/).map(c => c.trim())
}

// journey.py's is_separator.
const isSeparator = (line: string): boolean => {
  const cells = splitRow(line).filter(c => c !== '')

  return line.trim().startsWith('|') && cells.every(c => /^:?-{2,}:?$/.test(c))
}

// A bold field, `**Name:** value`, also as a list item and with a qualifier
// in the label, as a long journey writes them: `- **Next move (D1 = A):** ...`,
// `**Current Phase (2026-10-03, end of session):** ...`. The first match in
// `text` wins. A template placeholder (`[...]`) is no value.
const field = (text: string, ...names: string[]): string | undefined => {
  const label = names.map(n => n.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')
  const m = text.match(new RegExp(`^(?:\\s*-\\s+)?\\*\\*(?:${label})(?: \\([^)]*\\))?:\\*\\*\\s*(.+?)\\s*$`, 'mi'))
  const value = m?.[1]

  return value === undefined || value === '' || value.startsWith('[') ? undefined : value
}

// The header: everything above the first `##` heading, so a `Previous phase
// line` further down is never read as the phase.
const header = (text: string): string => {
  const all = lines(text)
  const end = all.findIndex(l => l.startsWith('## '))

  return (end < 0 ? all : all.slice(0, end)).join('\n')
}

// The current position: the `## Current Position` section, and of its dated
// `###` subsections only the first, the newest, because each supersedes the
// ones below it. Never a superseded position.
const currentPosition = (text: string): string => {
  const all = lines(text)
  const start = all.findIndex(l => /^##\s+current position\b/i.test(l))
  if (start < 0) return ''
  const rest = all.slice(start + 1)
  const end = rest.findIndex(l => l.startsWith('## '))
  const section = end < 0 ? rest : rest.slice(0, end)
  const subs = section.map((l, i) => (l.startsWith('### ') ? i : -1)).filter(i => i >= 0)
  if (subs.length === 0) return section.join('\n')
  const newestEnd = subs[1] ?? section.length

  return [...section.slice(0, subs[0]), ...section.slice(subs[0], newestEnd)].join('\n')
}

// A free-text field cut to its first clause, so one long sentence cannot take
// the whole band.
const MAX_FIELD = 32
const compact = (value: string | undefined): string | undefined => {
  if (value === undefined) return undefined
  const clause = value.split(/\. |: |; | — | – |, | \(/)[0].replace(/[.\s]+$/, '').trim()
  if (clause === '') return undefined

  return clause.length > MAX_FIELD ? clause.slice(0, MAX_FIELD - 1) + '…' : clause
}

// The template's terrain terms, in the order the field names them:
// "Greenfield service, but its quote-time half is brownfield" is
// `Greenfield/Brownfield`. A field with none of them is cut to its first clause.
const TERRAINS = ['Greenfield', 'Brownfield', 'Minefield', 'Ongoing Evolution']
const terrainOf = (value: string | undefined): string | undefined => {
  if (value === undefined) return undefined
  const found: string[] = []
  for (const m of value.matchAll(/\b(greenfield|brownfield|minefield|ongoing evolution)\b/gi)) {
    const term = TERRAINS.find(t => t.toLowerCase() === m[1].toLowerCase())
    if (term !== undefined && !found.includes(term)) found.push(term)
  }

  return found.length > 0 ? found.join('/') : compact(value)
}

// The first ReStack command in a line: a code span if there is one, else the
// bare command and its first argument.
const command = (text: string | undefined): string | undefined => {
  if (text === undefined) return undefined
  const span = text.match(/`(\/restack-[^`]+)`/)
  if (span) return span[1].trim()
  const bare = text.match(/\/restack-[a-z-]+(?:\s+[a-z][\w-]*)?/)

  return bare?.[0]
}

const confidenceOf = (text: string | undefined): string | undefined =>
  text?.match(/^(High|Medium|Low)\b/i)?.[1]

// journey.py's state_shape: the history is the last section, and a list.
export function stateProblem(text: string): string | undefined {
  const all = lines(text)
  const start = all.findIndex(l => /^##\s+journey history\b/i.test(l))
  if (start < 0) return 'no `## Journey History` section'
  const rest = all.slice(start + 1)
  if (rest.some(l => l.startsWith('## '))) return '`## Journey History` is not the last section'
  if (rest.some(l => l.trim().startsWith('|'))) return 'the journey history is a table'

  return undefined
}

type Register = { open: number; asks: number }

// journey.py's register_shape, then the rows: exactly one table, with the
// canonical columns, no `Update` headings, and only status lines after it.
export function readRegister(text: string): Register | string {
  const all = lines(text)
  const tables: Array<[number, number]> = []
  let orphans = 0
  let updates = 0
  let i = 0
  while (i < all.length) {
    const line = all[i]
    if (UPDATE_HEADING.test(line)) updates += 1
    if (line.trim().startsWith('|') && !isSeparator(line)) {
      const start = i
      while (i < all.length && all[i].trim().startsWith('|')) i += 1
      const header = splitRow(all[start]).map(c => stripMd(c).toLowerCase())
      if (header[0] === 'id') tables.push([start, i])
      else if (A_ROW.test(all[start])) orphans += i - start
      continue
    }
    i += 1
  }
  if (tables.length !== 1) return `${tables.length} register tables; the canonical register has exactly one`
  const [start, end] = tables[0]
  if (splitRow(all[start]).map(stripMd).join('|') !== COLUMNS.join('|')) {
    return "the register table's columns are not the canonical seven"
  }
  if (orphans > 0) return `${orphans} row(s) outside any table`
  if (updates > 0) return `${updates} 'Update' heading(s)`
  for (const line of all.slice(end)) {
    const t = line.trim()
    if (t && t !== '## Status lines' && !STATUS_LINE.test(line)) return 'a line after the table is not a status line'
  }

  let open = 0
  let asks = 0
  for (const line of all.slice(start, end)) {
    if (!A_ROW.test(line)) continue
    const cells = splitRow(line)
    const status = stripMd(cells[5] ?? '').toLowerCase()
    if (!OPEN.includes(status)) continue
    open += 1
    if (ASK_PREFIX.test((cells[3] ?? '').trim())) asks += 1
  }

  return { open, asks }
}

// journey.py's log_shape, then the decisions whose answer is still `(open)`,
// as `decision open` writes them.
export function readLog(text: string): number | string {
  const all = lines(text)
  const legacy = all.findIndex(l => LEGACY_D_HEADING.test(l))
  if (legacy >= 0) return `line ${legacy + 1} is a decision heading in the old shape`

  let open = 0
  let inDecision = false
  for (const line of all) {
    if (line.startsWith('## ')) {
      inDecision = D_HEADING.test(line)
      continue
    }
    if (inDecision && /^- \*\*Answer:\*\*\s*\(open\)\s*$/.test(line)) open += 1
  }

  return open
}

// The view of one journey. The first file not in the canonical shape wins:
// the band names it rather than guessing at what it says.
export function readJourney(files: Files): View | null {
  if (files.state === undefined) return null
  const stateProblemText = stateProblem(files.state)
  if (stateProblemText !== undefined) return { kind: 'not-canonical', file: 'journey-state.md' }

  const register = files.register === undefined ? undefined : readRegister(files.register)
  if (typeof register === 'string') return { kind: 'not-canonical', file: 'assumptions-register.md' }
  const decisions = files.log === undefined ? undefined : readLog(files.log)
  if (typeof decisions === 'string') return { kind: 'not-canonical', file: 'decisions-log.md' }

  const head = header(files.state)
  const position = currentPosition(files.state)
  const journey: Journey = {
    kind: 'journey',
    terrain: terrainOf(field(head, 'Terrain Type')),
    phase: compact(field(head, 'Current Phase')),
    confidence: confidenceOf(field(position, 'Confidence level')),
    next: command(field(position, "What's next", 'Next move')),
    asks: register?.asks,
    open: register?.open,
    decisions,
  }

  return journey
}

const plural = (n: number, one: string, many: string): string => `${n} ${n === 1 ? one : many}`

// The band's line, as pieces so the drawing can colour them. The same text
// answers `/restack-view` where nothing draws.
export function bandParts(view: View): { lead: string; next?: string; tail: string } {
  if (view.kind === 'not-canonical') {
    return { lead: `${view.file} is not canonical`, next: '/restack-journey migrate', tail: '' }
  }
  const lead = [view.terrain, view.phase, view.confidence].filter(Boolean).join(' · ')
  const counts = [
    view.asks === undefined ? undefined : plural(view.asks, 'ask', 'asks'),
    view.open === undefined ? undefined : `${view.open} open`,
    view.decisions === undefined ? undefined : plural(view.decisions, 'decision', 'decisions'),
  ].filter(Boolean)

  return { lead, next: view.next, tail: counts.join(' · ') }
}

export function bandText(view: View): string {
  const { lead, next, tail } = bandParts(view)
  if (view.kind === 'not-canonical') return `${lead}: ${next}`

  return [lead, next === undefined ? undefined : `next ${next}`, tail].filter(Boolean).join(' · ')
}
