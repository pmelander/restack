// What rests on a belief (ADR-030, view 3): an assumption's row, every ID its
// "Depends on it" cell names, each resolved where a canonical source holds it,
// and the other open rows that rest on it. Pure functions over text.
//
// What is not found is said to be not found. Nothing is guessed: a name the
// reader does not know as an ID is shown as written, under "also named".

import type { Lookup, LookupItem, MatrixGrid } from '../types'
import type { RegisterRow } from './journey.ts'

export type Refs = {
  adrs: number[]
  residuals: string[]
  decisions: number[]
  stressors: string[]
  assumptions: number[]
  // Everything else, as written: LLD-03, "golden vectors".
  other: string[]
}

const ADR = /\bADR-?(\d+)/gi
const RESIDUAL = /\bR-?(\d+(?:-[A-Z])?)\b/g
const DECISION = /\bD(\d{1,3})\b/g
const STRESSOR = /\bS-(\d+[a-z]?)\b/g
const ASSUMPTION = /\bA-(\d+)\b/g
// Bare numbers, and ranges, that continue an ADR list: `0025, 0026–0031`, `0002/0003`.
const BARE = /\b(\d{3,4})(?:\s*[–-]\s*(\d{3,4}))?\b/g

const uniq = <T>(xs: T[]): T[] => [...new Set(xs)]

// The IDs a "Depends on it" cell names, clause by clause (`;`). In a clause that
// names an ADR, every bare three- or four-digit number is one of its ADRs.
export function parseRefs(cell: string): Refs {
  const refs: Refs = { adrs: [], residuals: [], decisions: [], stressors: [], assumptions: [], other: [] }
  for (const clause of cell.replace(/\*+|`/g, '').split(';')) {
    let rest = clause
    const adrs = [...clause.matchAll(ADR)].map(m => Number(m[1]))
    if (adrs.length > 0) {
      refs.adrs.push(...adrs)
      rest = rest.replace(ADR, ' ')
      for (const m of rest.matchAll(BARE)) {
        const from = Number(m[1])
        const to = m[2] === undefined ? from : Number(m[2])
        for (let n = from; n <= to && n - from < 100; n++) refs.adrs.push(n)
      }
      rest = rest.replace(BARE, ' ')
    }
    for (const [re, into, map] of [
      [RESIDUAL, refs.residuals, (s: string) => `R${s}`],
      [STRESSOR, refs.stressors, (s: string) => `S-${s}`],
    ] as const) {
      for (const m of rest.matchAll(re)) into.push(map(m[1]))
      rest = rest.replace(re, ' ')
    }
    for (const m of rest.matchAll(DECISION)) refs.decisions.push(Number(m[1]))
    rest = rest.replace(DECISION, ' ')
    for (const m of rest.matchAll(ASSUMPTION)) refs.assumptions.push(Number(m[1]))
    rest = rest.replace(ASSUMPTION, ' ')
    for (const piece of rest.split(/[,/]/)) {
      const t = piece.replace(/[()]/g, ' ').replace(/\s+/g, ' ').trim()
      if (t !== '' && /[A-Za-z0-9]/.test(t)) refs.other.push(t)
    }
  }

  return {
    adrs: uniq(refs.adrs),
    residuals: uniq(refs.residuals),
    decisions: uniq(refs.decisions),
    stressors: uniq(refs.stressors),
    assumptions: uniq(refs.assumptions),
    other: uniq(refs.other),
  }
}

// A-09 and A-9 are one assumption, as journey.py has it. So is a bare 9: the
// register holds nothing but A- IDs, so the prefix adds nothing when typed.
export const assumptionNumber = (id: string): number | undefined => {
  const m = id.trim().match(/^(?:A-?)?(\d+)$/i)

  return m ? Number(m[1]) : undefined
}

// ADR files by number: `ADR-0047-title.md` and `ADR-47.md` alike.
export function adrFiles(names: string[]): Map<number, string> {
  const out = new Map<number, string>()
  for (const name of names) {
    const m = name.match(/^ADR-?(\d+)\b.*\.md$/i)
    if (m && !out.has(Number(m[1]))) out.set(Number(m[1]), name)
  }

  return out
}

// A document's title: its first `# ` heading, without an `ADR-0047:` prefix.
export const titleOf = (text: string): string | undefined =>
  text
    .split(/\r?\n/)
    .find(l => l.startsWith('# '))
    ?.slice(2)
    .replace(/^ADR-?\d+\s*[:—–-]\s*/i, '')
    .trim()

// Every decision's heading in the canonical log: `## D<n> · <date> · <title>`.
export function decisionTitles(log: string): Map<number, string> {
  const out = new Map<number, string>()
  for (const line of log.split(/\r?\n/)) {
    const m = line.match(/^## D(\d+) · (\d{4}-\d{2}-\d{2}) · (.*)$/)
    if (m) out.set(Number(m[1]), `${m[3].trim()} (${m[2]})`)
  }

  return out
}

// Residual headings, `## R13: Fleet-action guard`, as matrix.py finds them.
export function residualTitles(text: string): Map<string, string> {
  const out = new Map<string, string>()
  for (const line of text.split(/\r?\n/)) {
    const m = line.match(/^#{2,4}\s+(R-?[\w.-]+?)\b\s*[:—–-]?\s*(.*)$/)
    if (m) out.set(m[1].replace(/^R-/, 'R'), m[2].replace(/\*+/g, '').trim())
  }

  return out
}

export type Sources = {
  adrs: Map<number, { file: string; title?: string }>
  residuals: Map<string, { file: string; title: string }>
  decisions: Map<number, string>
  grid?: MatrixGrid
}

const pad4 = (n: number): string => String(n).padStart(4, '0')

// The lookup itself. `rows` is every row of the register.
export function lookup(input: string, rows: RegisterRow[], sources: Sources): Lookup {
  const n = assumptionNumber(input)
  if (n === undefined) return { kind: 'error', message: `Type an assumption's ID, such as 12 or A-12.` }
  const row = rows.find(r => assumptionNumber(r.id) === n)
  if (row === undefined) return { kind: 'error', message: `A-${n} is not in the register.` }
  const refs = parseRefs(row.depends)

  const item = (id: string, title: string | undefined, where?: string): LookupItem =>
    title === undefined ? { id, isFound: false } : { id, isFound: true, title, where }

  const adrs = refs.adrs.map(a => {
    const hit = sources.adrs.get(a)

    return hit === undefined ? item(`ADR-${pad4(a)}`, undefined) : item(`ADR-${pad4(a)}`, hit.title ?? hit.file, hit.file)
  })
  const residuals = refs.residuals.map(r => {
    const hit = sources.residuals.get(r)

    return item(r, hit?.title, hit?.file)
  })
  const decisions = refs.decisions.map(d => item(`D${d}`, sources.decisions.get(d)))
  const stressors = refs.stressors.map(s => {
    const grid = sources.grid
    const found = grid?.rows.find(r => r.id === s)
    if (grid === undefined || found === undefined) return item(s, undefined)
    const hits = grid.actors.filter((_, j) => found.cells[j] !== 0)

    return item(s, hits.length === 0 ? 'no hits' : `hits ${hits.join(', ')}`, grid.file)
  })
  const assumptions = refs.assumptions.map(a => {
    const other = rows.find(r => assumptionNumber(r.id) === a)

    return item(`A-${a}`, other === undefined ? undefined : `${other.status} · ${other.assumption}`)
  })
  // The reverse: open rows whose own cell names this one.
  const restsOnIt = rows
    .filter(r => assumptionNumber(r.id) !== n && /^(open|partly resolved)$/i.test(r.status))
    .filter(r => parseRefs(r.depends).assumptions.includes(n))
    .map(r => r.id)

  return {
    kind: 'found',
    id: row.id,
    status: row.status,
    assumption: row.assumption,
    validates: row.validates,
    groups: [
      { label: 'ADRs', items: adrs },
      { label: 'Residuals', items: residuals },
      { label: 'Decisions', items: decisions },
      { label: 'Stressors', items: stressors },
      { label: 'Assumptions', items: assumptions },
    ].filter(g => g.items.length > 0),
    other: refs.other,
    restsOnIt,
  }
}

// The lookup as tree lines, the same on both surfaces.
export function lookupLines(result: Lookup): Array<{ text: string; tone: 'head' | 'found' | 'missing' | 'plain' }> {
  if (result.kind === 'error') return [{ text: result.message, tone: 'plain' }]
  const out: Array<{ text: string; tone: 'head' | 'found' | 'missing' | 'plain' }> = [
    { text: `${result.id} · ${result.status} · ${result.assumption}`, tone: 'head' },
    { text: `settles it: ${result.validates}`, tone: 'plain' },
    { text: '', tone: 'plain' },
  ]
  const branches: Array<{ label: string; lines: Array<{ text: string; tone: 'found' | 'missing' | 'plain' }> }> = [
    ...result.groups.map(g => ({
      label: g.label,
      lines: g.items.map(i =>
        i.isFound
          ? { text: `${i.id} · ${i.title}${i.where && i.where !== i.title ? ` (${i.where})` : ''}`, tone: 'found' as const }
          : { text: `${i.id} · not found`, tone: 'missing' as const },
      ),
    })),
    ...(result.other.length > 0 ? [{ label: 'Also named, as written', lines: result.other.map(o => ({ text: o, tone: 'plain' as const })) }] : []),
    ...(result.restsOnIt.length > 0
      ? [{ label: 'Open rows that rest on it', lines: [{ text: result.restsOnIt.join(', '), tone: 'plain' as const }] }]
      : []),
  ]
  if (branches.length === 0) out.push({ text: '└─ its Depends on it cell names nothing', tone: 'plain' })
  branches.forEach((b, i) => {
    const last = i === branches.length - 1
    // A spacer between branches, so a long one does not run into the next.
    if (i > 0) out.push({ text: '│', tone: 'plain' })
    out.push({ text: `${last ? '└─' : '├─'} ${b.label}`, tone: 'plain' })
    b.lines.forEach((l, j) => {
      out.push({ text: `${last ? '   ' : '│  '}${j === b.lines.length - 1 ? '└─' : '├─'} ${l.text}`, tone: l.tone })
    })
  })

  return out
}
