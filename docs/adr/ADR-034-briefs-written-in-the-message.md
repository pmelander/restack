# ADR-034: Briefs Are Written in the Message and Asked in the Call

**Status:** Proposed

**Date:** 2026-10-22

**Deciders:** ReStack maintainers

**Technical Story:** architect report, 2026-10-22: "when an agent returns a
question to me it only uses half the width of the chat output. It makes long
questions hard to read."

**Implementation Status:** implemented

**Implemented Date:** 2026-10-22

**Implemented By:** ReStack maintainers

**Review Date:** 2027-04-22

## Context

`decision-brief.md` said a brief is issued via `AskUserQuestion` "never as
prose in the chat", and `questions.md` said the same of every question. So the
whole brief went into the call's `question` field: title, aspiration,
position, ELI10, the cost of choosing wrong, recommendation, confidence,
reversibility, every option's ✅ and ❌, and the Net line.

The Claude desktop app draws an `AskUserQuestion` call as a card about half the
width of the chat, and drops the question's line breaks. A brief is built from
lines (one field per line, a list per option), so it arrived as one dense
paragraph. On the reference engagement a brief about where a panel sits ran to
several hundred words in that card, with the ✅ and ❌ of three options run
together. The terminal draws the same call full width, so the format had only
been read there.

The card's width and layout belong to the host. No skill or tool argument sets
them. What a skill decides is what goes into the call.

The old rule existed to stop a brief from becoming a recommendation buried in
prose that the work then carries on past. That failure is about the answer, not
where the text is drawn: the protection is that the call is made and the work
stops until it is answered.

## Decision

### 1. A brief has two parts, issued in one turn

- **The brief, in the message**, as markdown, immediately before the call:
  a `### D<N> — <title>` heading, the fields as lists and paragraphs with blank
  lines between them, each option as a bold label with its ✅ and ❌ as a list,
  then the Net line. The chat draws it full width.
- **The question, in the call:** `header` is `D<N>`, `question` is the title
  line alone, and each option has its label (recommended first, marked
  `(Recommended)`) and a one-line `description` of what it buys and what it
  costs, under 150 characters.

The content rules do not change: aspiration, ELI10, the cost of choosing wrong,
a recommendation, confidence, reversibility, two ✅ and one ❌ per option, the
Net line.

### 2. Every question keeps its context out of the call

`questions.md`: the `question` is one sentence and each option's description
one line. What the architect needs to answer (what was found, why it matters)
goes in the message above the call.

### 3. The answer still comes only through the call

A brief written in the message with no call after it is the
conclusion-in-prose failure, and the self-check now says so. An interrupted
call re-issues both parts unchanged. Where `AskUserQuestion` is unavailable,
the brief already in the message gains its lettered options and "reply with a
letter", and the work stops.

## Consequences

### Positive

- Briefs are drawn full width with real lists in the desktop app, and read
  the same in the terminal.
- The card shows exactly what is being chosen between, so the choice reads at
  a glance with the reasoning just above it.
- The brief stays in the transcript as written, where it can be quoted and
  scrolled back to. Before, it existed only inside a card.

### Negative

- The brief and the card are two pieces of text that must agree. An option's
  label in the card that differs from the brief's is a new way to be wrong;
  the self-check asks for the brief's labels, word for word.
- In the terminal the brief is now read twice over: once in the message, then
  the options again in the prompt.

### Neutral

- No script, file or fixture changes. `decision open` and `decision answer`
  record the same entries.
- If the host later draws the card full width, the split still reads well, so
  nothing needs reverting.

## Knock-on changes

All done in the same step.

| Document | What this decision requires there | Done |
|---|---|---|
| `scripts/preamble/decision-brief.md` | the two parts, the markdown format, the self-check, interruption and fallback | done 2026-10-22, carried by every tier 2 and 3 skill |
| `scripts/preamble/questions.md` | the call short, the context in the message | done 2026-10-22, carried by every skill |
| [ADR-020](ADR-020-follow-up-commands-run-without-pause.md) | decision 5: every question is still a choice in the call; its context moves to the message | marked 2026-10-22 |
| CLAUDE.md, CHANGELOG.md | the behaviour and the ADR | done 2026-10-22 |

## Alternatives considered

### Shorten the brief to fit the card

- **Pros:** one piece of text; nothing to keep in step.
- **Cons:** the brief's fields are what make it a brief. Cutting ELI10, the
  cost of being wrong or the ✅ and ❌ to fit a card removes what the architect
  decides on.
- **Why rejected:** the content was right; it was in the wrong place.

### Put each option's ✅ and ❌ in the option's `preview`

- **Pros:** the comparison sits next to each option inside the dialog.
- **Cons:** previews are drawn differently by each host, and only while an
  option has focus. The comparison between options is what the architect
  reads, and a preview shows one option at a time.
- **Why rejected:** a full-width brief shows every option at once, everywhere.

### Wait for the host to widen the card

- **Pros:** no change here.
- **Cons:** the host's layout is not ours to plan around, and long briefs are
  unreadable until then.
- **Why rejected:** the split reads well whatever the host does.

## References

- [ADR-008](ADR-008-generated-skills-with-tiered-preamble.md): briefs and stop
  gates as shared preamble
- [ADR-020](ADR-020-follow-up-commands-run-without-pause.md): only questions
  pause a chain, and every question is a choice
