### The current style, and what a restyle may touch

ReStack is a working toolkit, not a training pack (ADR-022 in the ReStack
repository). Documents written while it framed itself as capability building
carry that framing. A restyle removes the framing and reshapes the document to
the current templates. It changes nothing a reader acts on.

#### What an older style left

| Old style | Current style | How |
|---|---|---|
| A *Reflection prompts*, *Capability being built*, *Residuality goal* or *Learning objectives* section | none | dropped, only when the architect names it (`--drop`) |
| Sentences addressed to the reader as a learner ("as you work through this you are building the capability to...", "by the end you will internalise...") | none, or a plain statement of the fact inside them | removed or reduced to the fact |
| Metadata as sections (`## Status` / `Accepted`) or as a bullet list | `**Status:** Accepted` lines above the body, in the template's order | reshaped; values unchanged |
| Heading names from an older template ("Options considered", "Pros and Cons of the Options") | the current template's ("Alternatives considered") | renamed; the alternatives under it unchanged |
| Long run-on paragraphs, passive voice, hedging | short paragraphs, active voice, concrete nouns: the actor, the path, the intention | reworded |
| Sections in an older order | the template's order | moved, whole |

The current ADR shape is the format in `/restack-adr`; the descriptive
documents' shapes are in `/restack-solution-doc`. Use them for order and
headings, never as a list of fields to fill.

#### Never, in a restyle

- **Add a field or a section with content.** A missing Reversibility, Review
  date or Knock-on changes is a gap. Report it for `/restack-adr update`.
  Filling it is a decision about the system.
- **Change a value.** Status, dates, deciders, figures, IDs, units. Keep
  numbers as digits, exactly as written.
- **Touch a table, a code block, a link target, a struck passage or a
  banner.** They are compared exactly. A table that reads badly stays as it
  is.
- **Change a normative word's force.** "must" stays "must", "never" stays
  "never", "should" is not upgraded to "must". A negation is never dropped
  to make a sentence read better.
- **Rename an alternative, or drop one.**
- **Move an amendment into the body or strike a passage.** An amendment
  written as a footnote is a finding for the owning skill's `update`, which
  accounts for it.
- **Resolve a TBD, or update a document to match what was built.** Both are
  decisions.
- **Restyle a record.** Journey files, reviews, discovery notes, stressor
  analyses, archives and retired ADRs are history.

#### When the style and the substance cannot be separated

Some old-style passages carry a fact inside the framing ("This builds the
team's capability to notice that the queue is the only thing protecting S-4").
Keep the fact, drop the framing ("The queue is the only thing protecting
S-4"), and expect a CONFIRM item for the words that went. If the fact itself
is out of date, that is not restyle's to fix: note it for the owning skill.
