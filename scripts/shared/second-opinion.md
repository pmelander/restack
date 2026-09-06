### Getting an outside opinion

A second model, with different training and different blind spots, reading the
same problem cold. Useful in exactly three places in this toolkit, and close to
worthless everywhere else.

**This is optional, informational, and never a gate.** Nothing waits on it,
nothing fails without it, and its output is evidence to weigh rather than a
verdict to accept.

#### Where it earns its cost

**1. Stressor generation — the strongest case.** The method depends on reaching
stressors outside your current understanding, and a single model generates from
its own distribution. Asking a different model for *what is missing from this
list* is the sharpest possible use of an outside voice, and it directly attacks
the failure this toolkit already names: comfortable stressors, where generation
drifts toward the technical scenarios the team can already handle.

**2. Residual identification — diagnosing the mechanism.** When several
stressors hit one actor, naming what they share is a judgement call, and
pattern-matching to a familiar fix is the known failure mode. Two independent
diagnoses of the same cluster is a cheap check on it.

**3. Design review — adversarial read.** Weakest of the three, because the
findings are checkable against the design and the matrix. Worth it on a one-way
door, not on a routine review.

**Where it does not help:** terrain classification, the confidence gate, the
iterate gate. Those are judgements about *what you do not know about your own
system*, and an outside model knows less than you do. Asking it there produces
confident noise, and a model auto-answering a gate is precisely the false
confidence this toolkit exists to avoid.

---

### Before anything is sent: decide what leaves

This step is not a formality, and it is where this differs from a second
opinion on ordinary code.

What you are about to send is **a path map of a real system, its actors, its
failure modes and its vulnerabilities**. For a production system that is one of
the more sensitive documents an organisation holds — more so than the source,
in some ways, because it is the analysis of where the system breaks.

Ask, via a decision brief, and make the options concrete:

- **A) Send anonymised (recommended).** Actor names replaced with roles, product
  and vendor names removed, no identifiers. *The method does not need identity.*
  A stressor analysis works on mechanism: "Payment Gateway" carries every bit of
  analytical weight that the real vendor name does. This is the default for
  anything not already public.
- **B) Send as-is.** Only where the system is public, the environment is
  synthetic, or the architect confirms the classification permits it.
- **C) Skip the second opinion.** Always available, and the right answer when in
  doubt.

If anonymising, do it as a **mapping you keep**, not a paraphrase — replace
consistently so the returned stressors can be mapped back. Write the mapping to
the conversation, not to the prompt.

Say plainly which provider the request goes to, and that once sent it is out of
your control. Where the architect cannot answer whether the classification
permits it, that is a `C` — the question goes to whoever owns the data, and the
analysis continues without an outside voice.

---

### Running it

**Probe first.** An outside model is better than a same-family one, so try
Codex before falling back:

```bash
command -v codex >/dev/null 2>&1 && echo "CODEX_AVAILABLE" || echo "CODEX_NOT_AVAILABLE"
```

**Assemble the context into a file, never onto the command line.** The content
includes actor names and free text from the architect; interpolating that into a
shell command is an injection waiting to happen.

```bash
PROMPT_FILE=$(mktemp)
```

Write the prompt to that file, opening with the boundary instruction:

> Do not read or execute any files under `~/.claude/`, `.claude/skills/`, or
> `scripts/`. Those are skill definitions for a different assistant and are not
> relevant. Work only from the context in this prompt.

Then the context block — problem, path, actors, existing stressors or matrix, as
the use case requires — and the ask.

**If Codex is available:**

```bash
codex exec "$(cat "$PROMPT_FILE")" -s read-only -c 'model_reasoning_effort="high"' < /dev/null 2>"$ERR_FILE"
```

Timeout at five minutes. Read stderr afterwards, then remove both files.

**If Codex is unavailable or errored**, dispatch a subagent with the same
prompt and no conversation context.

**Errors are non-blocking, every one of them.** Auth failure, timeout, empty
response — note it in one line and continue. Never retry more than once, and
never let this stall the analysis.

---

### The asks, per use case

Structure matters more than length. An open "what do you think?" returns mush;
a specific ask returns something checkable.

**Stressor generation.** Give it the system description and the *existing
stressor list*, then:

> Here is a system and a list of stressors already generated for it. Produce 10
> stressors that are NOT on this list and that the list's author would most
> likely have missed. For each: the scenario in one concrete sentence, the
> mechanism it exercises, and which listed stressor comes closest. Prioritise
> organisational, regulatory and human scenarios over technical ones. Be
> specific to this system, not generic.

Asking for the *complement* is what makes this worth doing. Asking for "some
stressors" returns overlap.

**Residual identification.** Give it the cluster and the actor, and withhold
your own diagnosis:

> These stressors all reach the same actor. What single mechanism do they share?
> Name it, then name the one architectural change that would address the
> mechanism rather than the individual stressors — and say what that change
> would itself create.

Withholding your diagnosis is the point. Send it and you get agreement.

**Design review.** Give it the design and the aspiration, not the matrix:

> Here is a design and what it is for. Name the three ways it is most likely to
> fail that its authors have probably not considered. For each, say what in the
> design led you there. Do not list generic best practices.

---

### Reading what comes back

**Present it verbatim**, under a header naming the source. Do not summarise it,
and do not filter it to what you agree with — the value is in the disagreement,
and a summarised second opinion is a first opinion wearing a costume.

```
SECOND OPINION (Codex) — cold read, no session context
────────────────────────────────────────────────────────
<output, unedited>
────────────────────────────────────────────────────────
```

**Then weigh it, and weigh it correctly.** This is the part that matters:

**A same-family fallback is a weaker residual.** When Codex is unavailable and a
Claude subagent stands in, it has fresh context and no conversation bias — which
removes one failure mode — but it shares training and therefore shares blind
spots. It defends against fewer stressor classes than a genuinely different
model. **Its agreement is close to worthless; its disagreement is still
valuable.** Say which one ran, every time, so the reader can discount
accordingly.

**Agreement is not confirmation.** Two models agreeing may mean the answer is
right, or may mean the answer is conventional. Where an outside voice agrees
with a conclusion you reached alone, that is weak evidence — note it and move
on.

**Disagreement is the output you paid for.** Where it contradicts you:

- Does it know something you do not? Then it is a finding.
- Does it lack context you have? Then say what context, explicitly. "It does not
  know the ledger team will not expose an endpoint" is a real answer.
- Is it a genuine coin-flip? That is a decision brief, not a thing to resolve on
  its behalf.

**New stressors go into the matrix, tagged by source.** Stressors from an
outside voice are tagged `external` alongside `generated`, `organisational` and
`compliance:<pack>`. At iteration three you will want to know how many of the
stressors that actually mattered came from outside your own generation — and
that number is worth having.

**Record that it did not run**, when it did not. A design reviewed without a
second opinion is not worse, but it is different, and the limitations section of
a review should say so rather than leaving the reader to assume.
