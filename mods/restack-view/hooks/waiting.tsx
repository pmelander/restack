// The waiting bars (ADR-030, view 2): open asks by recipient and age, and the
// register by status. Drawing only: the figures come from journey.ts, and
// nothing here is a judgement. A glyph's density is an age, a colour is
// whether an ask was sent or which status a row has. No red for "late", no
// green for "done".

import type { Elements, RenderSurface } from 'claude-code'

import type { AskBar } from './journey.ts'

type Els = Pick<Elements[RenderSurface], 'Box' | 'Text'>

// 0–6 days, 7–29, 30 and more.
const AGE_GLYPH = ['░', '▒', '█'] as const
const SENT_COLOR = 'suggestion'
const LABEL_WIDTH = 20
// Block glyphs measure about 1.15 cells wide in the Desktop's proportional
// font; drawing a little under the column count keeps a bar on one line, as
// headroom measured.
const DESKTOP_SLACK = 0.85

// A muted categorical palette, one colour per status, none of them a verdict.
const STATUS_COLOR: Record<string, string> = {
  Open: '#5b8def',
  'Partly resolved': '#9b7fe0',
  'Resolved by design (test pending)': '#3fa7a0',
  Resolved: '#8a8f98',
  Withdrawn: '#5f6368',
  Superseded: '#a08c5a',
}
const OTHER_COLOR = '#777777'

const room = (columns: number, surface: RenderSurface, used: number): number =>
  Math.max(4, Math.floor((columns - used) * (surface === 'desktop' ? DESKTOP_SLACK : 1)))

const countsOf = (bar: AskBar): string =>
  [
    bar.never > 0 ? `${bar.never} never asked` : undefined,
    bar.sent > 0 ? `${bar.sent} sent` : undefined,
    bar.oldest === undefined ? undefined : `oldest ${bar.oldest} d`,
  ]
    .filter(Boolean)
    .join(' · ')

const COUNTS_WIDTH = 34

// One row per recipient: the name, one glyph per ask (oldest first), the counts.
export function drawAskBars(els: Els, bars: AskBar[], surface: RenderSurface, columns: number) {
  const { Box, Text } = els
  const fits = room(columns, surface, LABEL_WIDTH + COUNTS_WIDTH + 2)

  return (
    <Box key="ask-bars" flexDirection="column">
      {bars.map((bar, i) => {
        const shown = bar.cells.length > fits ? bar.cells.slice(0, fits - 1) : bar.cells
        const more = bar.cells.length - shown.length

        return (
          <Box key={`ask-bar-${i}`} flexDirection="row" columnGap={1}>
            <Box width={LABEL_WIDTH} flexShrink={0}>
              <Text wrap="truncate">{bar.recipient}</Text>
            </Box>
            <Box flexGrow={1} overflow="hidden">
              <Text wrap="truncate">
                {shown.map(cell =>
                  cell.isSent ? <Text color={SENT_COLOR}>{AGE_GLYPH[cell.bucket]}</Text> : AGE_GLYPH[cell.bucket],
                )}
                {more > 0 ? <Text dimColor>{` +${more}`}</Text> : null}
              </Text>
            </Box>
            <Box width={COUNTS_WIDTH} flexShrink={0}>
              <Text dimColor wrap="truncate">
                {countsOf(bar)}
              </Text>
            </Box>
          </Box>
        )
      })}
      <Text dimColor wrap="truncate">
        {'░ 0–6 d  ▒ 7–29 d  █ 30+ d · '}
        <Text color={SENT_COLOR}>sent</Text>
        {' in colour, never asked plain'}
      </Text>
      <Text> </Text>
    </Box>
  )
}

// Split `width` cells across counts by share, largest remainder first, keeping
// at least one cell for every status that has a row (headroom's allocation).
function allocate(counts: number[], width: number): number[] {
  const sum = counts.reduce((a, b) => a + b, 0)
  if (sum <= 0 || width <= 0) return counts.map(() => 0)
  const exact = counts.map(n => (n / sum) * width)
  const cells = exact.map(Math.floor)
  let left = width - cells.reduce((a, b) => a + b, 0)
  for (const { i } of exact.map((x, i) => ({ i, r: x - Math.floor(x) })).sort((a, b) => b.r - a.r)) {
    if (left <= 0) break
    cells[i] += 1
    left -= 1
  }
  counts.forEach((n, i) => {
    if (n <= 0 || cells[i] > 0) return
    const donor = cells.indexOf(Math.max(...cells))
    if (cells[donor] > 1) {
      cells[donor] -= 1
      cells[i] = 1
    }
  })

  return cells
}

// The whole register as one stacked bar, then each status with its count.
export function drawStatusBar(els: Els, statuses: Array<[string, number]>, surface: RenderSurface, columns: number) {
  const { Box, Text } = els
  const total = statuses.reduce((a, [, n]) => a + n, 0)
  if (total === 0) return null
  const cells = allocate(
    statuses.map(([, n]) => n),
    room(columns, surface, 2),
  )

  return (
    <Box key="status-bar" flexDirection="column">
      <Text wrap="truncate">
        {statuses.map(([status], i) =>
          cells[i] > 0 ? <Text color={STATUS_COLOR[status] ?? OTHER_COLOR}>{'█'.repeat(cells[i])}</Text> : null,
        )}
      </Text>
      <Box flexDirection="row" flexWrap="wrap" columnGap={2}>
        {statuses.map(([status, n]) => (
          <Text key={`status-${status}`}>
            <Text color={STATUS_COLOR[status] ?? OTHER_COLOR}>●</Text>
            <Text dimColor>{` ${status} ${n}`}</Text>
          </Text>
        ))}
      </Box>
      <Text dimColor>{`${total} rows in the register`}</Text>
      <Text> </Text>
    </Box>
  )
}
