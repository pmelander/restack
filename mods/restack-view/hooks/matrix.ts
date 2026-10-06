// The impact matrix for the Matrix tab (ADR-030, view 1). Pure functions over
// text, mirroring the scripts that own each figure:
//
// - the table, the cells and the totals: matrix.py's Matrix, score and totals
// - the residual claims: matrix.py's parse_claims
// - the staleness stamp: trace.py's BASE check over the decisions log
//
// The matrix is never scored here, and a matrix matrix.py would reject is
// never drawn: the view shows the problem and the command instead.

import type { Claim, MatrixFile, MatrixGrid } from '../types'

// --- matrix.py ----------------------------------------------------------------

const LABEL_HEADERS = new Set([
  '#', 'id', 'stressor', 'lens', 'class', 'category', 'type', 'description',
  'source', 'tags', 'notes', 'stressor description', 'tag',
])
const TOTAL_HEADER = /^(σ|Σ|sum|total|impact|= ?)$/i
const MARGIN_ROW = /^(total|σ|Σ|vulnerab|actor vulnerab)/i
const STRESSOR_ID = /\bS-\d+[a-z]?\b/
const SEPARATOR = /^\|?[\s:|-]+\|?$/

const stripMd = (text: string): string => text.replace(/\*+|`|(?<!\w)_+|_+(?!\w)/g, '').trim()

// matrix.py's split_row: no escaped pipes in a matrix.
const splitRow = (line: string): string[] => {
  let body = line.trim()
  if (body.startsWith('|')) body = body.slice(1)
  if (body.endsWith('|')) body = body.slice(0, -1)

  return body.split('|').map(c => c.trim())
}

// [value, unknown] for a cell, or null when it is not a score.
export function score(cell: string): [number, boolean] | null {
  const text = stripMd(cell)
  if (['', '·', '.', '-', '–', '0'].includes(text)) return [0, false]
  if (text === '?') return [1, true]
  const m = text.match(/^(\d+)(\?)?$/)

  return m ? [Number(m[1]), m[2] !== undefined] : null
}

// The tables of a file: runs of lines starting with `|`, separators dropped.
function tables(lines: string[]): string[][] {
  const out: string[][] = []
  let block: string[] = []
  for (const line of lines) {
    if (line.trim().startsWith('|')) {
      if (!SEPARATOR.test(line.trim())) block.push(line)
    } else if (block.length > 0) {
      out.push(block)
      block = []
    }
  }
  if (block.length > 0) out.push(block)

  return out
}

// A cell as the grid holds it: 0 empty, 1 hit, 2 unknown (counted as 1).
export const EMPTY = 0
export const HIT = 1
export const UNKNOWN = 2

// The first table with a total column and binary-looking actor columns, as
// matrix.py finds it; its problems as `matrix.py totals` reports them. A
// non-empty `problems` means the view draws nothing but the first of them.
export function readMatrix(text: string): { grid?: Omit<MatrixGrid, 'file' | 'claims' | 'residualsFile' | 'baseline' | 'stale' | 'marked'>; problems: string[] } {
  const lines = text.replace(/^﻿/, '').replace(/\r\n?/g, '\n').split('\n')
  for (const block of tables(lines)) {
    const header = splitRow(block[0]).map(stripMd)
    const totalCols = header.map((h, k) => (TOTAL_HEADER.test(h) ? k : -1)).filter(k => k >= 0)
    if (totalCols.length === 0) continue
    const totalCol = totalCols[totalCols.length - 1]
    const body = block.slice(1).map(splitRow).filter(c => c.length === header.length)
    const data = body.filter(c => !MARGIN_ROW.test(stripMd(c[0])))
    const margins = body.filter(c => MARGIN_ROW.test(stripMd(c[0])))
    const cols: number[] = []
    for (let k = 0; k < totalCol; k++) {
      if (LABEL_HEADERS.has(header[k].toLowerCase()) || data.length === 0) continue
      if (data.filter(c => score(c[k]) !== null).length / data.length >= 0.8) cols.push(k)
    }
    if (cols.length === 0) continue

    const labelCols = Array.from({ length: totalCol }, (_, k) => k).filter(k => !cols.includes(k))
    const lensCol = header.findIndex(h => h.toLowerCase() === 'lens')
    const key = (c: string[]): string => {
      for (const k of labelCols) {
        const m = stripMd(c[k]).match(STRESSOR_ID)
        if (m) return m[0]
      }

      return labelCols.length > 0 ? stripMd(c[labelCols[0]]) : stripMd(c[0])
    }

    const problems: string[] = []
    const colTotals = cols.map(() => 0)
    let unknown = 0
    const rows = data.map(c => {
      const id = key(c)
      let got = 0
      const cells = cols.map((k, j) => {
        const v = score(c[k])
        if (v === null) {
          problems.push(`${id} × ${header[k]} = '${stripMd(c[k])}' is not a score`)
          return EMPTY
        }
        const [value, isUnknown] = v
        if (value > 1) problems.push(`${id} × ${header[k]} = ${value}: scoring is 0 or 1`)
        if (isUnknown) unknown += 1
        got += value
        colTotals[j] += value

        return value === 0 ? EMPTY : isUnknown ? UNKNOWN : HIT
      })
      const stated = stripMd(c[totalCol]).match(/\d+/)
      if (stated === null) problems.push(`${id} has no row total (cells sum to ${got})`)
      else if (Number(stated[0]) !== got) problems.push(`${id} cells sum to ${got}, the row says ${stated[0]}`)

      return { id, lens: lensCol >= 0 ? stripMd(c[lensCol]) || undefined : undefined, cells, total: got }
    })
    const total = colTotals.reduce((a, b) => a + b, 0)
    for (const c of margins) {
      cols.forEach((k, j) => {
        const stated = stripMd(c[k]).match(/\d+/)
        if (stated && Number(stated[0]) !== colTotals[j]) {
          problems.push(`column ${header[k]} sums to ${colTotals[j]}, the totals row says ${stated[0]}`)
        }
      })
      const stated = stripMd(c[totalCol]).match(/\d+/)
      if (stated && Number(stated[0]) !== total) problems.push(`the matrix sums to ${total}, the totals row says ${stated[0]}`)
    }
    if (margins.length === 0) problems.push('no totals row')

    return { grid: { actors: cols.map(k => header[k]), rows, colTotals, total, unknown }, problems }
  }

  return { problems: ['no impact matrix found (a table with actor columns and a Σ / Total column)'] }
}

const RESIDUAL_HEADING = /^#{2,4}\s+(R-?[\w.]+)\b(.*)$/
const CLAIM_LINE = /(S-\d+[a-z]?)\s*(?::\s*|\(\s*)([A-Za-z][\w/]*(?:\s*,\s*[A-Za-z][\w/]*)*)/g

// matrix.py's parse_claims: the cells each residual claims to clear, inside
// its cluster or outside it, on the actors this matrix has.
export function readClaims(text: string, actors: string[]): Claim[] {
  const known = new Set(actors)
  const out: Array<Claim & { stated?: number }> = []
  let current: (Claim & { stated?: number }) | undefined
  let inClears = false
  for (const line of text.replace(/^﻿/, '').replace(/\r\n?/g, '\n').split('\n')) {
    const h = line.match(RESIDUAL_HEADING)
    if (h) {
      const title = stripMd(h[2]).replace(/^[:—–\- ]+/, '').trim()
      current = { id: h[1], title: title.length > 60 ? title.slice(0, 60) + '…' : title, cells: [] }
      out.push(current)
      inClears = false
      continue
    }
    if (current === undefined) continue
    const m = line.match(/\*\*Clears (\d+) cells?/i)
    if (m) {
      current.stated = Number(m[1])
      inClears = true
      continue
    }
    if (inClears && line.startsWith('**') && !/outside/i.test(line)) inClears = false
    const t = line.trim()
    if (!inClears || !(t.startsWith('-') || t.startsWith('*'))) {
      if (inClears && t !== '' && !(t.startsWith('-') || t.startsWith('*'))) inClears = false
      continue
    }
    for (const [, s, cols] of line.matchAll(CLAIM_LINE)) {
      for (const col of cols.split(',').map(c => c.trim())) {
        if (known.has(col)) current.cells.push([s, col])
      }
    }
  }

  return out.filter(c => c.stated !== undefined || c.cells.length > 0).map(({ id, title, cells }) => ({ id, title, cells }))
}

// --- trace.py's BASE check -----------------------------------------------------

// The decisions logged with `Changes the actor set: yes`, by number.
export function actorSetChanges(log: string): number[] {
  const changes: number[] = []
  let current: number | undefined
  for (const line of log.replace(/\r\n?/g, '\n').split('\n')) {
    if (line.startsWith('## ')) {
      const m = line.match(/\bD(\d{1,3})\b/)
      current = m ? Number(m[1]) : undefined
      continue
    }
    const m = line.match(/\*\*Changes the actor set:?\*\*:?\s*(\w+)/i)
    if (m && current !== undefined && m[1].toLowerCase() === 'yes' && !changes.includes(current)) changes.push(current)
  }

  return changes.sort((a, b) => a - b)
}

// The baseline a matrix declares, the actor-set changes since that it is not
// marked `scored pre-D<n>` for, and the marks it carries.
export function staleness(matrix: string, changes: number[]): { baseline?: number; stale: number[]; marked: number[] } {
  const m = matrix.match(/scoring baseline:?\**\s*:?\s*\**\s*D(\d+)/i)
  const marked = [...matrix.matchAll(/scored pre-D(\d+)/gi)].map(x => Number(x[1]))
  if (!m) return { stale: [], marked }
  const baseline = Number(m[1])

  return { baseline, stale: changes.filter(n => n > baseline && !marked.includes(n)), marked }
}

// --- which matrix ------------------------------------------------------------

const MATRIX_NAME = /^matrix-(\d{4}-\d{2}-\d{2})(?:-iter(\d+))?(.*)\.md$/

// The matrices in docs/stressor-analysis/, newest first: by date, then by
// iteration, `matrix-<date>.md` before `matrix-<date>-iter<n>.md`.
export function matrixFiles(names: string[]): MatrixFile[] {
  return names
    .map(name => ({ name, m: name.match(MATRIX_NAME) }))
    .filter((x): x is { name: string; m: RegExpMatchArray } => x.m !== null)
    .map(({ name, m }) => ({ name, date: m[1], iter: m[2] === undefined ? undefined : Number(m[2]) }))
    .sort((a, b) => (a.date === b.date ? (b.iter ?? -1) - (a.iter ?? -1) : a.date < b.date ? 1 : -1))
}

// A matrix's residuals: the file with the same suffix, if there is one.
export const residualsFor = (matrix: string): string => matrix.replace(/^matrix-/, 'residuals-')

export const fileLabel = (f: MatrixFile): string => (f.iter === undefined ? f.date : `iteration ${f.iter} · ${f.date}`)

// --- drawing, as data ---------------------------------------------------------

// The order to draw: the file's own, or by total as a reading aid (rows and
// columns both, ties kept in file order). The order never changes a cell.
export function order(grid: MatrixGrid, byTotal: boolean): { rows: number[]; cols: number[] } {
  const rows = grid.rows.map((_, i) => i)
  const cols = grid.actors.map((_, j) => j)
  if (!byTotal) return { rows, cols }

  return {
    rows: rows.sort((a, b) => grid.rows[b].total - grid.rows[a].total || a - b),
    cols: cols.sort((a, b) => grid.colTotals[b] - grid.colTotals[a] || a - b),
  }
}

// The claimed cells to dim: every residual's, one residual's, or none.
export function claimedCells(grid: MatrixGrid, pick: string): Set<string> {
  const set = new Set<string>()
  for (const claim of grid.claims) {
    if (pick !== '*' && pick !== claim.id) continue
    for (const [s, a] of claim.cells) set.add(`${s}|${a}`)
  }

  return set
}

// 24-bit colours: a Raster takes 0x00RRGGBB, and an Svg the same as hex. Fixed
// rather than theme keys because a Raster has no theme. Cells are vivid, lens
// bands muted; none of them is a verdict (ADR-030).
export const COLOR = {
  hit: 0xff8a5c,
  unknown: 0xc78cff,
  claimed: 0x7a4636,
  lens: { O: 0x4a7fbf, V: 0x7f6fbf, C: 0x3f8f86, P: 0x9f8a4f, X: 0x777777 } as Record<string, number>,
  lensOther: 0x5a5a5a,
  none: 0x01000000,
}

const cellColor = (grid: MatrixGrid, r: number, c: number, claimed: Set<string>): number | undefined => {
  const row = grid.rows[r]
  const v = row.cells[c]
  if (v === EMPTY) return undefined
  if (claimed.has(`${row.id}|${grid.actors[c]}`)) return COLOR.claimed

  return v === UNKNOWN ? COLOR.unknown : COLOR.hit
}

const lensColor = (lens: string | undefined): number =>
  lens === undefined ? COLOR.lensOther : (COLOR.lens[lens.toUpperCase()] ?? COLOR.lensOther)

// Two stressor rows per terminal row, as half blocks: the top row is the
// foreground of `▀`, the bottom row its background. One lens column, a gap,
// then each actor column `width` cells wide: its first cell drawn, the rest a
// gap, so columns read apart.
export function rasterCells(grid: MatrixGrid, rows: number[], cols: number[], claimed: Set<string>, width: number) {
  const columns = 2 + cols.length * width
  const lines = Math.ceil(rows.length / 2)
  const words: number[] = []
  for (let line = 0; line < lines; line++) {
    const top = rows[line * 2]
    const bottom = rows[line * 2 + 1]
    const pair = (a: number | undefined, b: number | undefined) => {
      if (a === undefined && b === undefined) words.push(0x20, COLOR.none, COLOR.none)
      else if (a === undefined) words.push(0x2584, b!, COLOR.none)
      else words.push(0x2580, a, b ?? COLOR.none)
    }
    pair(lensColor(grid.rows[top].lens), bottom === undefined ? undefined : lensColor(grid.rows[bottom].lens))
    pair(undefined, undefined)
    for (const c of cols) {
      pair(cellColor(grid, top, c, claimed), bottom === undefined ? undefined : cellColor(grid, bottom, c, claimed))
      for (let k = 1; k < width; k++) pair(undefined, undefined)
    }
  }

  return { columns, rows: lines, cells: new Uint8Array(Uint32Array.from(words).buffer).toBase64() }
}

const hex = (c: number): string => `#${c.toString(16).padStart(6, '0')}`
const esc = (s: string): string => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

export const SVG_LIMIT = 131_072

// The Desktop's drawing: only the marked cells, each with a tooltip, a lens
// band, rotated actor codes above, column totals below, every fifth row named.
export function svgSource(grid: MatrixGrid, rows: number[], cols: number[], claimed: Set<string>, withTitles = true): string {
  const cw = 12
  const ch = 7
  const left = 56
  const top = 46
  const width = left + 10 + cols.length * cw + 8
  const height = top + rows.length * ch + 24
  const parts: string[] = [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" font-family="ui-monospace, monospace" font-size="9">`,
  ]
  cols.forEach((c, j) => {
    const x = left + 10 + j * cw + cw / 2
    parts.push(`<text transform="translate(${x},${top - 4}) rotate(-60)" fill="#8a8f98">${esc(grid.actors[c])}</text>`)
    parts.push(`<text x="${x}" y="${top + rows.length * ch + 14}" text-anchor="middle" fill="#8a8f98">${grid.colTotals[c]}</text>`)
  })
  rows.forEach((r, i) => {
    const y = top + i * ch
    const row = grid.rows[r]
    parts.push(`<rect x="${left}" y="${y}" width="6" height="${ch - 1}" fill="${hex(lensColor(row.lens))}"/>`)
    if (i % 5 === 0) parts.push(`<text x="${left - 4}" y="${y + ch}" text-anchor="end" fill="#8a8f98">${esc(row.id)}</text>`)
    cols.forEach((c, j) => {
      const color = cellColor(grid, r, c, claimed)
      if (color === undefined) return
      const rect = `x="${left + 10 + j * cw + 1}" y="${y}" width="${cw - 2}" height="${ch - 1}" fill="${hex(color)}"`
      parts.push(withTitles ? `<rect ${rect}><title>${esc(`${row.id} × ${grid.actors[c]}`)}</title></rect>` : `<rect ${rect}/>`)
    })
  })
  parts.push('</svg>')

  return parts.join('')
}
