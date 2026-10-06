// The waiting bars (ADR-030, view 2): open asks by recipient and age, and the
// register by status. Drawing only: the figures come from journey.ts.
//
// Drawn the way headroom draws its meters: lower half blocks that tile with a
// gap between rows, theme colours that follow light and dark, and the empty
// track as the same block dimmed. Colour is vivid and never a verdict: age
// runs cool to warm, teal to orange, with no red for late and no green for
// done (ADR-030).

import type { Elements, RenderSurface } from 'claude-code'

import type { AgeBucket, AskBar } from './journey.ts'

type Els = Pick<Elements[RenderSurface], 'Box' | 'Text'>

// A lower half block: seamless in any font, level with lowercase text, and
// its upper half is the gap between bars (headroom).
const BAR = '▄'
const TRACK_COLOR = 'inactive'

// Theme keys, so the colours follow the theme. 0–6 days, 7–29, 30 and more.
const AGE_COLOR: Record<AgeBucket, string> = { 0: 'planMode', 1: 'autoAccept', 2: 'claude' }
const AGE_LABEL: Record<AgeBucket, string> = { 0: '0–6 d', 1: '7–29 d', 2: '30+ d' }
// Oldest on the left, where the eye starts.
const AGE_ORDER: AgeBucket[] = [2, 1, 0]

const STATUS_COLOR: Record<string, string> = {
  Open: 'claude',
  'Partly resolved': 'autoAccept',
  'Resolved by design (test pending)': 'planMode',
  Resolved: 'ide',
  Withdrawn: 'inactive',
  Superseded: 'promptBorder',
}
const OTHER_COLOR = 'promptBorder'

const LABEL_WIDTH = 20
const COUNTS_WIDTH = 34
// Block glyphs measure about 1.15 cells wide in the Desktop's proportional
// font; drawing a little under the column count keeps a bar on one line
// (headroom's measurement).
const DESKTOP_SLACK = 0.85

const room = (columns: number, surface: RenderSurface, used: number): number =>
  Math.max(8, Math.floor((columns - used) * (surface === 'desktop' ? DESKTOP_SLACK : 1)))

// Split `width` cells across counts by share, largest remainder first, keeping
// at least one cell for every non-zero count (headroom's allocation).
export function allocate(counts: number[], width: number): number[] {
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

// One run of a bar: `cells` blocks in a colour, or the dimmed empty track.
const run = ({ Text }: Els, key: string, cells: number, color: string, isTrack = false) =>
  cells > 0 ? (
    <Text key={key} color={color} dimColor={isTrack}>
      {BAR.repeat(cells)}
    </Text>
  ) : null

const countsOf = (bar: AskBar): string =>
  [
    String(bar.cells.length),
    bar.never > 0 ? `never asked ${bar.never}` : undefined,
    bar.sent > 0 ? `sent ${bar.sent}` : undefined,
    bar.oldest === undefined ? undefined : `${bar.oldest} d`,
  ]
    .filter(Boolean)
    .join(' · ')

// One meter per recipient. Its filled length is its share of the busiest
// recipient's asks, split by age, oldest first; the rest is the empty track.
export function drawAskBars(els: Els, bars: AskBar[], surface: RenderSurface, columns: number) {
  const { Box, Text } = els
  const track = room(columns, surface, LABEL_WIDTH + COUNTS_WIDTH + 2)
  const most = Math.max(1, ...bars.map(b => b.cells.length))

  return (
    <Box key="ask-bars" flexDirection="column">
      {bars.map((bar, i) => {
        const filled = Math.max(1, Math.round((bar.cells.length / most) * track))
        const byAge = AGE_ORDER.map(b => bar.cells.filter(c => c.bucket === b).length)
        const parts = allocate(byAge, filled)

        return (
          <Box key={`ask-bar-${i}`} flexDirection="row" columnGap={1}>
            <Box width={LABEL_WIDTH} flexShrink={0}>
              <Text wrap="truncate">{bar.recipient}</Text>
            </Box>
            <Box flexGrow={1} height={1} overflow="hidden">
              <Text wrap="truncate">
                {AGE_ORDER.map((b, j) => run(els, `age-${b}`, parts[j], AGE_COLOR[b]))}
                {run(els, 'track', track - filled, TRACK_COLOR, true)}
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
      <Text wrap="truncate">
        {[0, 1, 2].map(b => (
          <Text key={`legend-${b}`}>
            <Text color={AGE_COLOR[b as AgeBucket]}>{BAR}</Text>
            <Text dimColor>{` ${AGE_LABEL[b as AgeBucket]}  `}</Text>
          </Text>
        ))}
        <Text dimColor>since the last send, or since registered when never asked</Text>
      </Text>
      <Text> </Text>
    </Box>
  )
}

// The whole register as one stacked meter, then each status with its count.
export function drawStatusBar(els: Els, statuses: Array<[string, number]>, surface: RenderSurface, columns: number) {
  const { Box, Text } = els
  const total = statuses.reduce((a, [, n]) => a + n, 0)
  if (total === 0) return null
  const parts = allocate(
    statuses.map(([, n]) => n),
    room(columns, surface, 2),
  )

  return (
    <Box key="status-bar" flexDirection="column">
      <Box height={1} overflow="hidden">
        <Text wrap="truncate">
          {statuses.map(([status], i) => run(els, `status-${i}`, parts[i], STATUS_COLOR[status] ?? OTHER_COLOR))}
        </Text>
      </Box>
      <Box flexDirection="row" flexWrap="wrap" columnGap={2}>
        {statuses.map(([status, n]) => (
          <Text key={`status-${status}`}>
            <Text color={STATUS_COLOR[status] ?? OTHER_COLOR}>●</Text>
            <Text>{` ${status} `}</Text>
            <Text bold>{String(n)}</Text>
          </Text>
        ))}
      </Box>
      <Text dimColor>{`${total} rows in the register`}</Text>
      <Text> </Text>
    </Box>
  )
}
