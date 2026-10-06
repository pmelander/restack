// The journey's rhythm (ADR-030, view 4): the history as a strip of days,
// each marked by the family of the commands run that day, gates marked, the
// empty days left empty. Pure functions over text: the counts it shows are
// the history's own, and it says nothing about what they ought to be.

export type Family = 'discover' | 'stressor' | 'decisions' | 'documentation' | 'review' | 'other'

export type Entry = { date: string; command: string; family: Family; isGate: boolean; isIterate: boolean }

// Five families (ADR-030, O4), by the skill a command names; `other` for a
// line with no ReStack command, or a skill outside them.
const FAMILY: Record<string, Family> = {
  discover: 'discover',
  stressor: 'stressor',
  events: 'stressor',
  adr: 'decisions',
  journey: 'decisions',
  'tech-stack': 'decisions',
  cloud: 'decisions',
  capacity: 'decisions',
  'solution-doc': 'documentation',
  trace: 'documentation',
  excel: 'documentation',
  'design-review': 'review',
  'arch-learning': 'review',
  'capability-assessor': 'review',
  patterns: 'review',
  evolve: 'review',
}

export const FAMILIES: ReadonlyArray<[Family, string]> = [
  ['discover', 'discover'],
  ['stressor', 'stressor and events'],
  ['decisions', 'decisions'],
  ['documentation', 'documentation and trace'],
  ['review', 'review'],
  ['other', 'other'],
]

// The skill a command names, with or without the `restack-` prefix an old
// history leaves out: `/stressor walk x` and `/restack-stressor walk x` alike.
export function familyOf(command: string): Family {
  const m = command.match(/\/(?:restack-)?([a-z][a-z-]*)/)

  return m ? (FAMILY[m[1]] ?? 'other') : 'other'
}

const HISTORY_LINE = /^\s*-\s*(\d{4}-\d{2}-\d{2})\s*·\s*(.*)$/

// The `## Journey History` lines, in the shape journey.py writes them:
// `- <date> · <command> · <outcome>[ · D<n>]`. A gate is any `D<n>` on the
// line, since a long history also writes them mid-line, `(D2 = A)`.
export function historyEntries(state: string): Entry[] {
  const lines = state.replace(/\r\n?/g, '\n').split('\n')
  const start = lines.findIndex(l => /^##\s+journey history\b/i.test(l))
  if (start < 0) return []
  const out: Entry[] = []
  for (const line of lines.slice(start + 1)) {
    if (line.startsWith('## ')) break
    const m = line.match(HISTORY_LINE)
    if (!m) continue
    const command = m[2].split('·')[0].replace(/`/g, '').trim()
    out.push({
      date: m[1],
      command,
      family: familyOf(command),
      isGate: /\bD\d+\b/.test(m[2]),
      isIterate: /\/(?:restack-)?journey iterate\b/.test(command),
    })
  }

  return out.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0))
}

export type Cell = { family?: Family; isGate: boolean; count: number }

export type Rhythm = {
  start: string
  end: string
  // Days per cell: 1, or whole weeks when the days do not fit.
  bucket: number
  cells: Cell[]
  counts: { entries: number; iterations: number; gates: number; days: number }
}

const DAY_MS = 86_400_000
const dayIndex = (date: string): number => Math.floor(Date.parse(`${date}T00:00:00Z`) / DAY_MS)
const isoOf = (index: number): string => new Date(index * DAY_MS).toISOString().slice(0, 10)

// The strip from the first entry to `today`, one cell per day, or per week
// (then per several weeks) when the days are more than `width`. A cell takes
// the family most of its entries share, the latest of them on a tie.
export function rhythm(entries: Entry[], today: string, width: number): Rhythm | null {
  if (entries.length === 0) return null
  const first = dayIndex(entries[0].date)
  const last = Math.max(dayIndex(today), dayIndex(entries[entries.length - 1].date))
  const days = last - first + 1
  const room = Math.max(1, width)
  const bucket = days <= room ? 1 : 7 * Math.ceil(days / room / 7)
  const cells: Array<Cell & { tally: Map<Family, number> }> = Array.from({ length: Math.ceil(days / bucket) }, () => ({
    isGate: false,
    count: 0,
    tally: new Map(),
  }))
  for (const e of entries) {
    const cell = cells[Math.floor((dayIndex(e.date) - first) / bucket)]
    cell.count += 1
    cell.isGate ||= e.isGate
    cell.tally.set(e.family, (cell.tally.get(e.family) ?? 0) + 1)
    // Ties go to the latest entry's family: ascending dates, so this one.
    const best = Math.max(...cell.tally.values())
    if ((cell.tally.get(e.family) ?? 0) === best) cell.family = e.family
  }

  return {
    start: isoOf(first),
    end: isoOf(last),
    bucket,
    cells: cells.map(({ family, isGate, count }) => ({ family, isGate, count })),
    counts: {
      entries: entries.length,
      iterations: entries.filter(e => e.isIterate).length,
      gates: entries.filter(e => e.isGate).length,
      days,
    },
  }
}
