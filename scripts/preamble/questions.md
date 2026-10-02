## Questions

Every question to the architect is a choice, asked with `AskUserQuestion` as a
tool call, never as prose in the chat. That covers decision briefs and the
one-line confirms alike ("is anything implemented, or is this design-only?").

- **Offer the plausible answers as options,** two to four, the one you would
  pick first and labelled `(Recommended)`. The host adds a free-text "Other",
  so never add one yourself.
- **A confirm is a choice too:** the reading you found, as the recommended
  option, against the readings you ruled out.
- **An open answer still gets options.** For a number, a name or a URL, offer
  what you found on disk or a sensible default; "Other" takes the rest. Ask in
  prose only when nothing can be enumerated, and then ask one question and stop.
- **One question at a time.** The question is where the thinking happens. A
  batch gets skimmed.
- An architectural judgement is a decision brief, not a bare question: this
  section sets the shape, *Decision Briefs* sets the content, where a skill
  has them.

If `AskUserQuestion` is unavailable, write the same question with lettered
options, add "reply with a letter", and stop.
