# ADR-018: Close With the Next Command in a Copyable Block

**Status:** Accepted — partly superseded by
[ADR-020](ADR-020-follow-up-commands-run-without-pause.md)

> **Amended 2026-10-02 (2.8.0):** the next command now runs instead of being
> handed over, and only questions pause a chain. See
> [ADR-020](ADR-020-follow-up-commands-run-without-pause.md). The copy block
> below is the fallback where the `Skill` tool is unavailable.

**Date:** 2026-10-02

**Deciders:** ReStack maintainers

**Technical Story:** follow-up to [ADR-017](ADR-017-next-step-as-a-button.md),
withdrawn in 2.5.2

**Implementation Status:** implemented

**Implemented Date:** 2026-10-02

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-02

## Context

[ADR-017](ADR-017-next-step-as-a-button.md) rendered the next move as a widget
button and was withdrawn the day it shipped. In the desktop app's Code tab,
clicks were unreliable, and the outcome depended on host behaviour ReStack
cannot test. The `Next:` line went with it, because it had been introduced to
serve the button.

What the architect actually wanted back was smaller: the next command where it
can be copied. Hosts already give a fenced code block a Copy button. The
desktop app does, and a terminal shows the block as plain text. That needs no
widget, no tool detection and no `sendPrompt`.

## Decision

A tier-1 preamble fragment, `next-command.md`, composed into all sixteen
skills after the completion status:

1. When the work points at a next ReStack command, the response names it after
   the status line and before the reflection prompt: a `Next:` line with the
   reason, then the command alone in a fenced block tagged `text`, then an
   optional one-line `Alternative:`.
2. **The block holds exactly the command, on one line, arguments included.**
3. **Tagged `text`, never a shell language.** Hosts put a Run button on a shell
   block, and a slash command run in a shell is at best an error.
4. **One block.** The alternative stays a line.
5. **No `Next:` while a decision brief is unanswered,** and never an answer to
   a brief in the block.

### Why arguments are fine here when ADR-017 forbade them

ADR-017 kept arguments off the button for three reasons. None of them applies
to a block the architect copies:

- **Attribution.** `sendPrompt` spoke in the architect's voice. A copied block
  is pasted and sent by the architect, who reads it on the way.
- **Injection.** Nothing in a block is submitted on anyone's behalf. It is text
  on the screen, as the `Next:` line always was.
- **Staleness.** Copying an old block is the same as retyping an old command:
  the full text is visible before it is sent. A button hid the target behind a
  label.

## Consequences

### Positive

- The next command is one copy away on hosts with a Copy button, and identical
  text everywhere else.
- Next moves have one shape across the sixteen skills again.
- Nothing depends on undocumented host behaviour. If a host drops the Copy
  button, the block is still the command, in plain text.

### Negative

- 28 more preamble lines in every skill, including the tier-1 utilities, which
  rarely have a next move.
- It still relies on the model to tag the block `text`. A `bash` tag would
  offer a Run button that runs a slash command in a shell, which fails
  harmlessly but looks broken.

## Alternatives considered

### Inline code in the `Next:` line only
- **Why rejected:** No Copy button. Selecting text inside a sentence is the
  friction this removes.

### A `bash`-tagged block
- **Why rejected:** The Run button invites running a slash command in a shell.

### Bring back the button
- **Why rejected:** See [ADR-017](ADR-017-next-step-as-a-button.md).
  Unreliable clicks, two actions in the Code tab, and undocumented host
  behaviour, for less than a Copy button already gives.

## References

- [ADR-017](ADR-017-next-step-as-a-button.md): the withdrawn button, and the
  gate rule this keeps
- [ADR-008](ADR-008-generated-skills-with-tiered-preamble.md): the tiered
  preamble
