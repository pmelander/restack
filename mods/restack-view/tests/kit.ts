// What the tests share: /restack-view run the way a person runs it, and an
// index read that fails the test, naming the index, when the item is not there.

import type { Engine } from 'claude-code/testing'

// A person typing /restack-view in the composer; the engine stamps `origin`
// and `presentation` on a real run, so a test states them.
export const runView = ($: Engine, args = '') =>
  $.command.run({
    command: 'restack-view',
    args,
    origin: { kind: 'composer' },
    presentation: { isFullscreen: false, columns: 120 },
  })

// `xs[i]`, where a missing item is the failure the test is there to catch.
export function at<T>(xs: readonly T[], i: number): T {
  const x = xs[i]
  if (x === undefined) throw new Error(`no item ${i}: the list has ${xs.length}`)

  return x
}
