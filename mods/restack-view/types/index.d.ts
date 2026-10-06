// What the band shows, read from the journey files (ADR-029). Nothing here is
// written back: the mod is a view, and journey.py is the only writer (ADR-023).

export type Journey = {
  kind: 'journey'
  terrain?: string
  phase?: string
  confidence?: string
  // The next ReStack command from Current Position, e.g. `/restack-stressor analyze`.
  next?: string
  // Undefined when the file is missing, so the band leaves the count out.
  asks?: number
  open?: number
  decisions?: number
}

export type NotCanonical = {
  kind: 'not-canonical'
  // The journey file that is not in the shape journey.py writes.
  file: string
}

export type View = Journey | NotCanonical

// What the pane lists, read from the same files at the same time as the View.

export type Ask = {
  id: string
  recipient: string
  need: string
  status: string
  // `never asked`, or the last recorded send: `asked <whom> <date>`.
  sent: string
  // The row's first status line: when it was registered (YYYY-MM-DD).
  registered?: string
  // The last recorded send, after any `unasked` (YYYY-MM-DD).
  sentOn?: string
}

export type OpenRow = {
  id: string
  status: string
  assumption: string
  validates: string
}

export type Decision = {
  id: string
  date: string
  question: string
  gate?: string
}

export type Detail = {
  // The header fields as written, first line only, label then value.
  header: Array<[string, string]>
  // The newest Current Position subsection, as markdown.
  position: string
  asks: Ask[]
  open: OpenRow[]
  decisions: Decision[]
  // Every row of the register by status, in the vocabulary's order.
  statuses: Array<[string, number]>
}

export type Tab = 'position' | 'asks' | 'assumptions' | 'decisions'

declare module 'claude-code' {
  interface PluginState {
    'restack-view': { view: View | null; detail: Detail | null; isBandOn: boolean; tab: Tab }
  }
}
