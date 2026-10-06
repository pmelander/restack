// The pane's layout: headed sections, items in a fixed column, a blank line
// between everything (maintainer, 2026-10-06: the pane read too compact,
// especially with a lot of text). One place, so every tab spaces alike.

import type { Elements, RenderSurface } from 'claude-code'

type Els = Pick<Elements[RenderSurface], 'Box' | 'Text' | 'Markdown'>

const ACCENT = 'claude'
const INDENT = 2

// `OPEN ASSUMPTIONS · 3`: bold, in the accent, the count when there is one.
export function heading(els: Els, title: string, count?: number) {
  const { Text } = els

  return (
    <Text bold color={ACCENT} wrap="truncate">
      {title.toUpperCase()}
      {count === undefined ? '' : ` · ${count}`}
    </Text>
  )
}

// A headed block: the heading, a blank line, the content indented under it,
// and a blank line after.
export function section(els: Els, key: string, title: string, count: number | undefined, children: unknown) {
  const { Box } = els

  return (
    <Box key={key} flexDirection="column" marginBottom={1}>
      {heading(els, title, count)}
      <Box flexDirection="column" marginTop={1} paddingLeft={INDENT}>
        {children}
      </Box>
    </Box>
  )
}

// Every legend's colour key, on every tab: a full square, as the matrix marks
// a hit (maintainer, 2026-10-06).
export const KEY = '■'

// A dim rule across the pane, under the tabs.
export const rule = (els: Els, width: number) => (
  <els.Text key="rule" dimColor wrap="truncate">
    {'─'.repeat(Math.max(10, width))}
  </els.Text>
)

export type Item = {
  id: string
  // The status line beside the id: status, dates, gate.
  meta: string
  // The text under it, each line its own paragraph; markdown, as the files write it.
  lines: string[]
}

// Items in a column: the id in a fixed bold column, the status line and the
// text wrapping beside it, a blank line between items.
export function items(els: Els, key: string, list: Item[], more?: string) {
  const { Box, Text, Markdown } = els
  const idWidth = Math.max(4, ...list.map(i => i.id.length)) + 2

  return (
    <Box key={key} flexDirection="column" rowGap={1}>
      {list.map((item, i) => (
        <Box key={`${key}-${i}`} flexDirection="row">
          <Box width={idWidth} flexShrink={0}>
            <Text bold>{item.id}</Text>
          </Box>
          <Box flexDirection="column" flexGrow={1} flexShrink={1}>
            <Text dimColor wrap="wrap">
              {item.meta}
            </Text>
            {item.lines.map((line, j) => (
              <Markdown key={`${key}-${i}-${j}`} text={line} />
            ))}
          </Box>
        </Box>
      ))}
      {more === undefined ? null : <Text dimColor>{more}</Text>}
    </Box>
  )
}

// Label and value pairs in two columns, the values wrapping in theirs.
export function fields(els: Els, key: string, pairs: Array<[string, string]>) {
  const { Box, Text, Markdown } = els
  const labelWidth = Math.min(24, Math.max(...pairs.map(([label]) => label.length)) + 2)

  return (
    <Box key={key} flexDirection="column" rowGap={1}>
      {pairs.map(([label, value], i) => (
        <Box key={`${key}-${i}`} flexDirection="row">
          <Box width={labelWidth} flexShrink={0}>
            <Text dimColor wrap="truncate">
              {label}
            </Text>
          </Box>
          <Box flexGrow={1} flexShrink={1}>
            <Markdown key={`${key}-v-${i}`} text={value} />
          </Box>
        </Box>
      ))}
    </Box>
  )
}
