## Decision Briefs

Architecture is a sequence of decisions made under uncertainty. Every point
where the architect's judgement is required is a **decision brief**, answered
through `AskUserQuestion` as a tool call, and never answered on the architect's
behalf.

A brief has two parts, issued together in one turn:

1. **The brief, in the message**, as markdown, immediately before the call. The
   chat draws it full width, with real lists.
2. **The question, in the call.** Hosts draw an `AskUserQuestion` call as a
   narrow card and drop its line breaks, so a brief put inside one reads as a
   single dense paragraph. The call carries only:
   - `header`: `D<N>`;
   - `question`: the title line, `D<N> — <one-line question title>`, and
     nothing else;
   - per option, `label`: the option's label, the recommended one first with
     `(Recommended)`; `description`: one line on what it buys and what it
     costs, under 150 characters.

Then stop. Writing the brief is not asking it: a brief left in the message
with no call after it is the conclusion-in-prose failure the stop gates exist
to prevent.

### Format

The brief in the message:

```markdown
### D<N> — <one-line question title>

- **Aspiration:** <the aspiration this decision serves, one line>
- **Position:** <terrain> · <journey phase> · iteration <N>

**ELI10:** <plain English a smart non-architect follows, 2-4 sentences, name the stakes>

**If we choose wrong:** <which actor, which path, what the user of the system experiences>

- **Recommendation:** <option> because <one-line reason tied to the aspiration>
- **Confidence:** <High | Medium | Low> — <what evidence would raise it>
- **Reversibility:** <Reversible | Costly to reverse | One-way door>

**A) <option label>** (recommended)
- ✅ <pro — concrete, observable, ≥40 characters>
- ✅ <pro>
- ❌ <con — honest, ≥40 characters>

**B) <option label>**
- ✅ <pro>
- ✅ <pro>
- ❌ <con>

**Net:** <one-line synthesis of what is actually being traded off>
```

Keep the blank lines: without them markdown joins the fields into one
paragraph, which is the problem this layout solves.

**D-numbering:** numbers are unique within a journey, and a brief takes its
number when it is issued, not when it is answered. Get it from
`journey.py decision open` (see *Journey Files*), which writes the open entry
to `docs/journey/decisions-log.md`; without the helper, the next brief is one
past the highest `D<N>` in the log, or `D1`. Sub-briefs in a split chain are
`D<N>.1`, `D<N>.2`, `D<N>.final`, recorded in the parent's entry. A brief that
was never answered keeps its number; do not reuse it.

**Aspiration line.** Every architectural decision either serves the stated
aspiration or it is scope creep. If you cannot name the aspiration the decision
serves, that is itself the finding — surface it instead of the question.

**Confidence** is the residuality-native honesty valve. `Low` means the option
set rests on beliefs about the system that have not been verified. Say what
would raise it ("read the Order Service retry config", "ask the DBA whether
replication is synchronous"). A `Low`-confidence brief on a **One-way door** is
a signal to stop and run `/restack-discover` instead of deciding.

**Reversibility** governs how hard the architect should think. Reversible
decisions should be made fast and revisited cheaply. One-way doors — data model
shape, integration contracts, vendor lock-in, anything that becomes an actor
other paths depend on — deserve a slower brief and an ADR regardless of outcome.

**Recommendation is always present**, including when you have no preference:
`Recommendation: <default> — this is a taste call, no strong preference either
way`. The `(recommended)` label stays on the default option.

**Pros and cons:** minimum two ✅ and one ❌ per option, each at least 40
characters, each concrete and observable. For a genuine hard stop (destructive
or one-way confirmation), `✅ No cons — this is a hard-stop choice` is the only
permitted escape.

### Five or more options

`AskUserQuestion` caps at four options per call. Never drop, merge, or silently
defer an option to fit. Either batch into coherent groups of ≤4, or split into
a sequential chain — one brief per option, each with buckets
**A) Include · B) Defer · C) Cut · D) Hold** (Hold stops the chain for
discussion), closed by a `D<N>.final` brief validating the assembled set.
The architect's option set is sacred.

### Self-check before emitting

- [ ] The brief is in the message, as markdown, before the call
- [ ] `D<N>` header present
- [ ] Aspiration line names a real aspiration, not the task
- [ ] ELI10 present, plain English, names the stakes
- [ ] "If we choose wrong" names a specific actor or path
- [ ] Recommendation present with a reason tied to the aspiration
- [ ] Confidence rated, with the evidence that would raise it
- [ ] Reversibility rated
- [ ] Every option has ≥2 ✅ and ≥1 ❌, each ≥40 characters
- [ ] `(recommended)` on exactly one option
- [ ] Net line closes the tradeoff
- [ ] The call follows the brief: `question` is the title line alone, each
      option's `label` the brief's label word for word, its `description` one
      line, nothing else from the brief in it

### If a brief is interrupted or rejected

A rejected, interrupted or cancelled `AskUserQuestion` call (a host restart, a
dismissed dialog) is **not an answer**. It is not "no", and it is not consent to
the recommendation. Do not proceed on the recommendation and do not log a
decision. On resumption, say that `D<N>` is unanswered and re-issue it
unchanged, the brief and the call. If the architect answers in chat instead, that is the answer: record
it in their words. **No decision is logged without a recorded answer.**

### If AskUserQuestion is unavailable

The brief is already in the message. End it with the options' letters and
labels, add "reply with a letter", and **stop**.
Do not auto-decide and do not write the decision into the journey state as a
substitute for the architect having made it.
