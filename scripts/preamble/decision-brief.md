## Decision Briefs

Architecture is a sequence of decisions made under uncertainty. Every point
where the architect's judgement is required is a **decision brief**, issued via
`AskUserQuestion` as a tool call — never as prose in the chat, and never
answered on the architect's behalf.

### Format

```
D<N> — <one-line question title>
Aspiration: <the aspiration this decision serves, one line>
Position: <terrain> · <journey phase> · iteration <N>
ELI10: <plain English a smart non-architect follows, 2-4 sentences, name the stakes>
If we choose wrong: <which actor, which path, what the user of the system experiences>
Recommendation: <option> because <one-line reason tied to the aspiration>
Confidence: <High | Medium | Low> — <what evidence would raise it>
Reversibility: <Reversible | Costly to reverse | One-way door>
A) <option label> (recommended)
  ✅ <pro — concrete, observable, ≥40 characters>
  ❌ <con — honest, ≥40 characters>
B) <option label>
  ✅ <pro>
  ❌ <con>
Net: <one-line synthesis of what is actually being traded off>
```

**D-numbering:** the first brief in a command invocation is `D1`; increment
yourself. Sub-briefs in a split chain are `D<N>.1`, `D<N>.2`, `D<N>.final`.

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
- [ ] You are calling the tool, not writing prose

### If AskUserQuestion is unavailable

Render the identical brief as prose, add "reply with a letter", and **stop**.
Do not auto-decide and do not write the decision into the journey state as a
substitute for the architect having made it.
