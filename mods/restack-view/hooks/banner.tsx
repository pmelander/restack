// The ReStack banner at the top of the pane, in an 80s sunset fade, because a
// mod can. Decoration only: it carries no data, so ADR-030's no-verdict rule
// has nothing to say about its colours.

import type { Elements, RenderSurface } from 'claude-code'

type Els = Pick<Elements[RenderSurface], 'Box' | 'Text' | 'Svg'>

// figlet's "slant", as the maintainer pasted it, first line re-indented.
export const ART = [
  '    ____      _____ __             __  ',
  '   / __ \\___ / ___// /_____ ______/ /__',
  '  / /_/ / _ \\\\__ \\/ __/ __ `/ ___/ //_/',
  ' / _, _/  __/__/ / /_/ /_/ / /__/ ,<   ',
  '/_/ |_|\\___/____/\\__/\\__,_/\\___/_/|_|  ',
]
const WIDTH = Math.max(...ART.map(l => l.length))

// Gold, orange, hot pink, magenta, violet: a synthwave sunset.
const STOPS = [0xffd319, 0xff901f, 0xff2975, 0xf222ff, 0x8c1eff]

// The fade at `t` from 0 to 1, between the two nearest stops.
export function fade(t: number): string {
  const x = Math.min(1, Math.max(0, t)) * (STOPS.length - 1)
  const i = Math.min(STOPS.length - 2, Math.floor(x))
  const f = x - i
  const mix = (shift: number) =>
    Math.round(((STOPS[i] >> shift) & 0xff) * (1 - f) + ((STOPS[i + 1] >> shift) & 0xff) * f)

  return `#${[16, 8, 0].map(s => mix(s).toString(16).padStart(2, '0')).join('')}`
}

// Diagonal: mostly across, a little down, as a chrome logo catches the light.
const at = (row: number, col: number): number => (col / (WIDTH - 1)) * 0.7 + (row / (ART.length - 1)) * 0.3

const esc = (s: string): string => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

// The Desktop's text is proportional, so the banner is an Svg there: monospace
// text filled with the same fade as a gradient.
export function bannerSvg(): string {
  const cw = 7.8
  const lh = 13
  const w = Math.ceil(WIDTH * cw) + 4
  const h = ART.length * lh + 6
  const stops = STOPS.map((_, i) => `<stop offset="${i / (STOPS.length - 1)}" stop-color="${fade(i / (STOPS.length - 1))}"/>`)
  const lines = ART.map((l, i) => `<text x="2" y="${(i + 1) * lh}" xml:space="preserve">${esc(l)}</text>`)

  return [
    `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}">`,
    `<defs><linearGradient id="sunset" x1="0" y1="0" x2="1" y2="0.45">${stops.join('')}</linearGradient></defs>`,
    `<g font-family="ui-monospace, Menlo, Consolas, monospace" font-size="13" font-weight="700" fill="url(#sunset)">`,
    ...lines,
    '</g></svg>',
  ].join('')
}

// Narrower than the art, it is left out: a banner that wraps is worse than none.
export function drawBanner(els: Els, surface: RenderSurface, columns: number) {
  if (columns < WIDTH + 2) return null
  const { Box, Text, Svg } = els
  if (surface === 'desktop') {
    return (
      <Box key="banner" flexDirection="column">
        <Svg source={bannerSvg()} alt="ReStack" />
      </Box>
    )
  }

  return (
    <Box key="banner" flexDirection="column">
      {ART.map((line, row) => (
        <Text key={`banner-${row}`} bold>
          {[...line].map((ch, col) => (ch === ' ' ? ' ' : <Text color={fade(at(row, col))}>{ch}</Text>))}
        </Text>
      ))}
    </Box>
  )
}
