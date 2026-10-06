// Reads the three journey files in the canonical shape journey.py writes
// (ADR-023), and nothing else. Pure functions over text: no `$`, so the tests
// run them straight against the fixtures journey.py is tested against.
//
// The rules mirror journey.py's: a change to the canonical shape there that
// does not reach here fails tests/journey.test.ts (ADR-029, decision point 4).

import type { Ask, Decision, Detail, Journey, OpenRow, Tab, View } from '../types'

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

// One register row's cells, as journey.py's split_row gives them.
type Cells = string[]
type Table = { rows: Cells[]; statusLines: string[] }

// journey.py's register_shape, then the rows: exactly one table, with the
// canonical columns, no `Update` headings, and only status lines after it.
function registerTable(text: string): Table | string {
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

  return {
    rows: all.slice(start, end).filter(l => A_ROW.test(l)).map(splitRow),
    statusLines: all.slice(end).filter(l => STATUS_LINE.test(l)),
  }
}

const isOpen = (cells: Cells): boolean => OPEN.includes(stripMd(cells[5] ?? '').toLowerCase())

// journey.py's split_ask: `Ask BI: row counts` is an ask of BI for row counts.
const askOf = (cells: Cells): { recipient: string; need: string } | undefined => {
  const m = (cells[3] ?? '').trim().match(ASK_PREFIX)

  return m ? { recipient: m[1].trim(), need: m[2].trim() } : undefined
}

export function readRegister(text: string): Register | string {
  const table = registerTable(text)
  if (typeof table === 'string') return table
  const open = table.rows.filter(isOpen)

  return { open: open.length, asks: open.filter(c => askOf(c) !== undefined).length }
}

// journey.py's sends: each row's sends, oldest first; `unasked` cancels the last.
const sendsOf = (statusLines: string[]): Map<string, Array<[string, string]>> => {
  const sends = new Map<string, Array<[string, string]>>()
  for (const line of statusLines) {
    const m = line.match(STATUS_LINE)
    if (!m) continue
    const id = `A-${Number(m[1])}`
    const list = sends.get(id) ?? []
    if (m[4].startsWith('asked ')) list.push([m[3], m[4].slice('asked '.length).trim()])
    else if (m[4].startsWith('unasked ')) list.pop()
    sends.set(id, list)
  }

  return sends
}

const rowId = (cells: Cells): string => stripMd(cells[0] ?? '')

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

// --- the pane ----------------------------------------------------------------

// The decisions whose answer is still `(open)`, with their heading and gate.
function openDecisions(text: string): Decision[] {
  const found: Decision[] = []
  let current: Decision | undefined
  let isOpenAnswer = false
  const close = () => {
    if (current !== undefined && isOpenAnswer) found.push(current)
  }
  for (const line of lines(text)) {
    if (line.startsWith('## ')) {
      close()
      const m = line.match(D_HEADING)
      current = m ? { id: `D${m[1]}`, date: m[2], question: m[3].trim() } : undefined
      isOpenAnswer = false
      continue
    }
    if (current === undefined) continue
    const gate = line.match(/^- \*\*Gate:\*\*\s*(.+?)\s*$/)
    if (gate) current.gate = gate[1]
    if (/^- \*\*Answer:\*\*\s*\(open\)\s*$/.test(line)) isOpenAnswer = true
  }
  close()

  return found
}

// The header fields, as written: the first line of each `**Label:** value`
// above the first `##`.
const headerFields = (text: string): Array<[string, string]> =>
  lines(header(text))
    .map(l => l.match(/^\*\*([^*:]+?)(?: \([^)]*\))?:\*\*\s*(.+?)\s*$/))
    .filter((m): m is RegExpMatchArray => m !== null && !/^previous|^earlier/i.test(m[1]))
    .map(m => [m[1], m[2]])

// What the pane lists. Null for no journey or one not in the canonical shape:
// the pane then shows what the band shows.
export function readDetail(files: Files): Detail | null {
  const view = readJourney(files)
  if (view === null || view.kind !== 'journey' || files.state === undefined) return null
  const table = files.register === undefined ? undefined : registerTable(files.register)
  const all = table === undefined || typeof table === 'string' ? [] : table.rows
  const statusLines = table === undefined || typeof table === 'string' ? [] : table.statusLines
  const sends = sendsOf(statusLines)
  const registered = registeredOf(statusLines)

  const asks: Ask[] = []
  const open: OpenRow[] = []
  for (const cells of all.filter(isOpen)) {
    const id = rowId(cells)
    const status = stripMd(cells[5] ?? '')
    open.push({ id, status, assumption: cells[1] ?? '', validates: cells[3] ?? '' })
    const ask = askOf(cells)
    if (ask === undefined) continue
    const last = sends.get(id)?.at(-1)
    asks.push({
      id,
      status,
      ...ask,
      sent: last === undefined ? 'never asked' : `asked ${last[1]} ${last[0]}`,
      // Without a status line, the row's own status date is when it was registered.
      registered: registered.get(id) ?? dateOf(cells[6]),
      sentOn: last?.[0],
    })
  }

  return {
    header: headerFields(files.state),
    // Without the `---` rule that closes the section in the file.
    position: currentPosition(files.state).replace(/(\s*\n\s*-{3,}\s*)+$/, '').trim(),
    asks,
    open,
    decisions: files.log === undefined ? [] : openDecisions(files.log),
    statuses: statusCounts(all),
  }
}

const dateOf = (cell: string | undefined): string | undefined => cell?.match(/\d{4}-\d{2}-\d{2}/)?.[0]

// Each row's first status line: when journey.py registered it.
const registeredOf = (statusLines: string[]): Map<string, string> => {
  const first = new Map<string, string>()
  for (const line of statusLines) {
    const m = line.match(STATUS_LINE)
    if (!m || m[3] === '—') continue
    const id = `A-${Number(m[1])}`
    if (!first.has(id)) first.set(id, m[3])
  }

  return first
}

// The register's vocabulary, in journey.py's order, with every `Superseded by
// D<n>` counted as one status. A status outside it is counted under its own name.
const VOCABULARY = ['Open', 'Partly resolved', 'Resolved by design (test pending)', 'Resolved', 'Withdrawn', 'Superseded']
const statusCounts = (rows: Cells[]): Array<[string, number]> => {
  const counts = new Map<string, number>(VOCABULARY.map(v => [v, 0]))
  for (const cells of rows) {
    const raw = stripMd(cells[5] ?? '')
    const known = /^superseded by d\d+$/i.test(raw) ? 'Superseded' : VOCABULARY.find(v => v.toLowerCase() === raw.toLowerCase())
    const key = known ?? raw
    counts.set(key, (counts.get(key) ?? 0) + 1)
  }

  return [...counts.entries()].filter(([, n]) => n > 0)
}

// --- waiting (ADR-030, view 2) ---------------------------------------------

const DAY_MS = 86_400_000

// Whole days from a YYYY-MM-DD date to `nowMs`; never negative.
export function daysSince(date: string | undefined, nowMs: number): number | undefined {
  const at = date === undefined ? NaN : Date.parse(`${date}T00:00:00Z`)

  return Number.isNaN(at) ? undefined : Math.max(0, Math.floor((nowMs - at) / DAY_MS))
}

// 0: 0–6 days, 1: 7–29, 2: 30 and more. Unknown age counts as the oldest.
export type AgeBucket = 0 | 1 | 2
export const bucketOf = (days: number | undefined): AgeBucket =>
  days === undefined || days >= 30 ? 2 : days >= 7 ? 1 : 0

export type AskCell = { id: string; isSent: boolean; days?: number; bucket: AgeBucket }
export type AskBar = { recipient: string; cells: AskCell[]; never: number; sent: number; oldest?: number }

// One bar per recipient, in the register's order: each open ask aged from its
// last send, or from its registration when it was never sent. Oldest first.
export function askBars(detail: Detail, nowMs: number): AskBar[] {
  const bars = new Map<string, AskBar>()
  for (const ask of detail.asks) {
    const key = ask.recipient.toLowerCase()
    const bar = bars.get(key) ?? { recipient: ask.recipient, cells: [], never: 0, sent: 0 }
    const isSent = ask.sentOn !== undefined
    const days = daysSince(isSent ? ask.sentOn : ask.registered, nowMs)
    bar.cells.push({ id: ask.id, isSent, days, bucket: bucketOf(days) })
    if (isSent) bar.sent += 1
    else bar.never += 1
    bars.set(key, bar)
  }
  for (const bar of bars.values()) {
    bar.cells.sort((a, b) => (b.days ?? Infinity) - (a.days ?? Infinity))
    const known = bar.cells.map(c => c.days).filter((d): d is number => d !== undefined)
    bar.oldest = known.length > 0 ? Math.max(...known) : undefined
  }

  return [...bars.values()]
}

// One element's text stays under Claude Code's 10,000-character limit: items
// are added while they fit, then one line says how many are left and where
// the rest is.
export const BUDGET = 9_000
export function budget(items: string[], rest: string, max = BUDGET): string {
  const kept: string[] = []
  let size = 0
  for (const item of items) {
    if (size + item.length + 1 > max - 200) break
    kept.push(item)
    size += item.length + 1
  }
  const left = items.length - kept.length

  return left === 0 ? kept.join('\n') : [...kept, '', `… ${left} more: ${rest}`].join('\n')
}

export const TABS: ReadonlyArray<[Tab, string]> = [
  ['position', 'Position'],
  ['asks', 'Asks'],
  ['assumptions', 'Assumptions'],
  ['decisions', 'Decisions'],
]

// A tab's body as markdown. Every list names the command that gives it whole.
export function tabText(detail: Detail, tab: Tab): string {
  if (tab === 'position') {
    const fields = detail.header.map(([label, value]) => `- **${label}:** ${value}`)
    const position = detail.position === '' ? ['No Current Position section.'] : detail.position.split('\n')

    return budget([...fields, '', ...position], '/restack-journey where')
  }
  if (tab === 'asks') {
    if (detail.asks.length === 0) return 'No open asks.'
    const groups = new Map<string, Ask[]>()
    for (const ask of detail.asks) {
      const key = ask.recipient.toLowerCase()
      groups.set(key, [...(groups.get(key) ?? []), ask])
    }
    const items: string[] = []
    for (const group of groups.values()) {
      items.push(`### ${group[0].recipient} (${group.length})`)
      for (const ask of group) items.push(`- **${ask.id}** · ${ask.status} · ${ask.sent} — ${ask.need}`)
    }

    return budget(items, '/restack-journey asks')
  }
  if (tab === 'assumptions') {
    if (detail.open.length === 0) return 'No open assumptions.'

    return budget(
      detail.open.map(r => `- **${r.id}** · ${r.status} — ${r.assumption} *Settles it:* ${r.validates}`),
      'docs/journey/assumptions-register.md',
    )
  }
  if (detail.decisions.length === 0) return 'No open decisions.'

  return budget(
    detail.decisions.map(d => `- **${d.id}** · ${d.date} · ${d.question}${d.gate ? ` · gate: ${d.gate}` : ''}`),
    'docs/journey/decisions-log.md',
  )
}
