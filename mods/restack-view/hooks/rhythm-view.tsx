// The rhythm strip's drawing (ADR-030, view 4), at the top of the Position tab.
// Block glyphs of one width only, so the strip lines up in the Desktop's
// proportional font as headroom's bars do: `▄` a day with entries, `█` a day
// with a gate, the dimmed track an empty day. Counts as numbers, no verdict.

import type { Elements, RenderSurface } from 'claude-code'

import { FAMILIES } from './rhythm.ts'
import type { Family, Rhythm } from './rhythm.ts'

type Els = Pick<Elements[RenderSurface], 'Box' | 'Text'>

export const FAMILY_COLOR: Record<Family, string> = {
  discover: '#4a90d9',
  stressor: '#ff8a5c',
  decisions: '#af87ff',
  documentation: '#3fa7a0',
  review: '#e0b050',
  other: '#8a8f98',
}
// No label of its own: the section's heading names it.
const LABEL = ''
// Block glyphs measure about 1.15 cells wide in the Desktop's proportional
// font (headroom's measurement).
const DESKTOP_SLACK = 0.85

// The cells the strip may use on this surface, after its label.
export const stripWidth = (columns: number, surface: RenderSurface): number =>
  Math.max(10, Math.floor((columns - LABEL.length - 1) * (surface === 'desktop' ? DESKTOP_SLACK : 1)))

const plural = (n: number, one: string, many: string): string => `${n} ${n === 1 ? one : many}`

export function drawRhythm(els: Els, r: Rhythm | null, surface: RenderSurface) {
  const { Box, Text } = els
  if (r === null) return null
  const width = r.cells.length
  const unit = r.bucket === 1 ? 'a day' : r.bucket === 7 ? 'a week' : `${r.bucket / 7} weeks`
  const axis =
    width >= r.start.length + r.end.length + 2
      ? r.start + ' '.repeat(width - r.start.length - r.end.length) + r.end
      : `${r.start} → ${r.end}`

  return (
    <Box key="rhythm" flexDirection="column">
      <Text wrap="truncate">
        <Text dimColor>{LABEL}</Text>
        {r.cells.map((cell, i) =>
          cell.family === undefined ? (
            <Text key={`day-${i}`} color="inactive" dimColor>
              ▄
            </Text>
          ) : (
            <Text key={`day-${i}`} color={FAMILY_COLOR[cell.family]}>
              {cell.isGate ? '█' : '▄'}
            </Text>
          ),
        )}
      </Text>
      <Text dimColor wrap="truncate">
        {' '.repeat(LABEL.length) + axis}
      </Text>
      <Text wrap="wrap">
        <Text dimColor>{' '.repeat(LABEL.length)}</Text>
        <Text bold>{plural(r.counts.entries, 'entry', 'entries')}</Text>
        <Text dimColor> · </Text>
        <Text bold>{plural(r.counts.iterations, 'iteration', 'iterations')}</Text>
        <Text dimColor> · </Text>
        <Text bold>{plural(r.counts.gates, 'gate', 'gates')}</Text>
        <Text dimColor>{` · ${plural(r.counts.days, 'day', 'days')}, one cell ${unit} · █ a gate`}</Text>
      </Text>
      <Text wrap="wrap">
        <Text dimColor>{' '.repeat(LABEL.length)}</Text>
        {FAMILIES.map(([family, label]) => (
          <Text key={`family-${family}`}>
            <Text color={FAMILY_COLOR[family]}>▄</Text>
            <Text dimColor>{` ${label}  `}</Text>
          </Text>
        ))}
      </Text>
    </Box>
  )
}
