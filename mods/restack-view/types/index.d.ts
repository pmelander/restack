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

declare module 'claude-code' {
  interface PluginState {
    'restack-view': { view: View | null; isBandOn: boolean }
  }
}
