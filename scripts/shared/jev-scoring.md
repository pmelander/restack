### Scoring matrix cells with Jev

A decision model — TypeSafe's Jev, reached over the System One API — answering
one yes/no question per cell: *does this stressor affect this actor?* It returns
a calibrated probability rather than a word, which is the only reason it is
worth wiring in at all.

**This is optional, informational, and never a gate.** Nothing waits on it,
nothing fails without it, and a run with no API key scores exactly as it always
has, with no note and no degraded-mode banner. An architect who has never heard
of Jev should not be able to tell from the output that this section exists.

#### Why cells, and only cells

The matrix is the one place in this toolkit where the work is genuinely
mechanical and genuinely large. Twelve actors against thirty stressors is 360
judgements, each one narrow, each one the same shape, and the model scoring them
is the same model that generated the stressors and will read the result. That is
three roles for one judgement, and the middle one is the least defensible.

It is also where a wrong answer is cheapest to catch. A miscounted cell moves a
column total by one and shows up in the margins; a bad terrain classification
poisons everything downstream and shows up months later.

**What Jev does not touch:** stressor generation, residual identification, the
four reading-the-matrix checks, and every gate. Those are judgements about what
you do not know about your own system, and the reasoning in
`scripts/shared/second-opinion.md` about where an outside voice helps applies
here unchanged — more so, because Jev is a decision model with no capacity to
explain itself. It hands back a number. A number is the right output for a cell
and the wrong output for everything else.

---

### Probe first

```bash
[ -n "${TYPESAFE_API_KEY:-}" ] && command -v python3 >/dev/null 2>&1 \
  && echo "JEV_AVAILABLE" || echo "JEV_NOT_AVAILABLE"
```

`JEV_NOT_AVAILABLE` ends this section. Score the matrix as the
matrix-construction section describes and say nothing about it — an optional
enhancement that announces its own absence is a nag, and the architect did not
ask for one.

---

### Before anything is sent: decide what leaves

**Read the "Before anything is sent" step in `scripts/shared/second-opinion.md`
and apply it unchanged.** Same three options, same defaults, same rule that an
architect who cannot answer the classification question has answered `C`. What
you are about to send is the same document — a path map of a real system and its
failure modes — and it does not become less sensitive for going to a scoring
model rather than a chat model.

Two deltas, and only two:

**The provider is TypeSafe AI, and the endpoint is `api.typesafe.ai`.** Say so
by name. Their published position is that Jev is not trained on customer
requests or responses; that is their policy, not a guarantee you can offer on
their behalf, and it does not change what leaving your control means.

**Under option A, anonymisation is mandatory rather than merely consistent.**
The second-opinion default sends an anonymised path map. Here, actor names do
not just appear in the state — every question is keyed by an actor id *and names
that actor in its own instructions*, because TypeSafe do not use the question id
in inference, only to key the answer back to you. So the actor set travels twice
in every request: once in the state, once across the question map, and a third
time inside the instruction text. A request with an anonymised path map and real
actor ids is not anonymised. Anonymise the state, the ids and the instructions
together, from one mapping, or do not send.

Keep the mapping in the conversation, never in a file that goes with the
request. Map the probabilities back before anything is written to the matrix.

---

### One request per stressor

Jev ingests the `state` once and evaluates every question against it in
parallel, so the natural unit is **one request per stressor row**, carrying one
`noul` per actor. A 30×12 matrix is 30 requests, not 360.

Do not invert this. One request per actor carrying one question per stressor
would send the same path map thirty times and ask each question against a state
that describes the whole system rather than the stressor in play.

**State: the walked path map(s), trimmed to the actors on those paths.** Not the
design docs, not the ADRs, not the full journey state. Trimming is not only an
egress courtesy — TypeSafe document context rot as a known failure mode of
`jev-1.13`, where accuracy falls as the state grows with material unrelated to
the decision. Everything in the state that is not an actor on a walked path, or
the intention flowing along it, is costing you accuracy on every cell in the
row.

Include the stressor statement itself in the state, in full, as the architect
wrote it. A stressor paraphrased down to a label is the flat-matrix failure
arriving one request early.

**Questions: one `noul` per actor, keyed by a stable actor id.** The id is how
the answer finds its way back to a cell, and nothing more — TypeSafe state
plainly that the key is not used in inference. **So the actor must be named in
the instruction text, or every question in the request is identical** and the
probabilities come back describing the path rather than the actor.

The instructions carry the matrix section's own definition of "affects", word
for word, because `jev-1.13` reads instructions literally and answers the
question you wrote rather than the one you meant:

> Under this stressor, does `Order Service` fail, degrade materially, lose
> correctness, or propagate the damage onward?

and the criteria carry the other half of that definition, the half that is easy
to lose:

```json
"criteria": {
  "true": "The actor fails, degrades materially, loses correctness, or propagates the damage onward.",
  "false": "The actor is unaffected, or notices the stressor and handles it correctly."
}
```

That `false` clause is the whole of "handling it *is* the residual working".
Leave it out and every actor with a working timeout scores as affected, which
inverts the meaning of the matrix and would do it invisibly.

---

### Thresholds, and the band in the middle

| Probability | Cell |
|---|---|
| `p >= 0.8` | `1` |
| `p <= 0.2` | `0` |
| `0.2 < p < 0.8` | escalates to the model, which scores it as it always has |

The escalated cells are scored by reading the path map and the stressor, exactly
as the matrix-construction section describes, and they may come back `1` with a
`?` like any other cell.

**Jev never produces a `?`, and never clears one.** A `?` means *this
architecture has not been understood well enough to say* — it is a claim about
the state of the analysis, and it carries a discovery step that would settle it.
A probability near 0.5 is a different statement: the model is confident the
answer is genuinely balanced. Treating one as the other would convert an
architect's registered ignorance into a model's calibrated hedge, and the
assumptions register would quietly stop filling up.

Where a cell already carries a `?` from a previous iteration, Jev does not get a
vote on it. Only discovery clears a `?`.

**The thresholds are tuned to `jev-1.13.0`, which is why the script pins that
version rather than the `jev-latest` alias.** TypeSafe's own guidance is to pin
a version once thresholds are tuned against it, and their jaggedness notes are
blunt about why: a threshold tuned on a `noul` does not transfer, and separate
questions are not held to arithmetic identities — the same question and its
negation, asked as two nouls, were observed summing to 1.19. Do not build
anything on top of these numbers that assumes they compose.

---

### When a request fails

**Any HTTP error, and any row that comes back malformed, falls back to model
scoring for that row and is recorded as having done so.** Non-blocking, every
one of them, on the same rule as the outside opinion: note it in one line and
continue.

A row is malformed when the response is missing an answer for an actor, carries
an answer with no `noul` field, or carries a `noul` outside `0..1`. Do not
partially accept it — a row scored half by Jev and half by the model, with no
record of which half, is worse than a row the model scored alone, because the
provenance line will claim something that is not true.

`429` and `529` are the two worth one retry with a short backoff, because they
say "later" rather than "no". `401` means the key is wrong; stop trying, do not
print the key, and fall back for the whole matrix. `422` means the request was
malformed — that is a defect in the script, not a transient, so report it and
fall back rather than retrying.

---

### What stays with the model, unconditionally

The four checks in the "Reading the matrix" part of
`skills/restack-stressor/sections/matrix-construction.md` — concentration,
clusters, flatness, suspicious zeros — are read off the finished matrix by the
model, whatever produced the cells. They are interpretation, not scoring, and
naming the mechanism behind a cluster is the step the whole method exists to
reach.

**Suspicious zeros get a second look regardless of source.** A column summing to
zero is either a genuinely trivial actor or an actor nobody understood, and that
check does not get easier because a confident model produced the zeros. If
anything it gets harder: Jev has never seen this system, cannot ask, and will
return `0.03` for an actor whose real behaviour is nowhere in the state you
sent. A confident zero from a model that could not have known is exactly the
zero worth doubting.

---

### Provenance

Every row records what scored it — `jev`, `model`, or `mixed` — in the matrix
file, per the output format in the matrix-construction section. Raw
probabilities go to `docs/stressor-analysis/matrix-<date>.jev.json` beside the
matrix, so the thresholds can be re-examined later against cells that are
already scored, and so `/restack-arch-learning` has something to check the ADR's
prediction against.

**The audit trail records the request count and the egress choice. Nothing
else.** Not the state, not the questions, not the probabilities — those live in
the `.jev.json`, which is a working artifact the architect can delete. The
API key never enters the journey state, a prompt file, the matrix, or the
`.jev.json`, and is read only from `TYPESAFE_API_KEY`.

---

### Running it

The script ships with this skill. Resolve it once per session, installed path
first:

```bash
JEV="$HOME/.claude/skills/restack-stressor/scripts/jev_score.py"
[ -f "$JEV" ] || JEV="skills/restack-stressor/scripts/jev_score.py"
```

It takes one JSON document on stdin or by `--in`, and writes per-cell
probabilities as JSON. Input carries the trimmed path map, the stressor list and
the actor list; `jev_score.py --help` is the authority on the exact shape.

**Assemble the input as a file, never on the command line.** Path maps carry
free text the architect wrote, and interpolating that into a shell command is
the same injection waiting to happen that the outside-opinion section warns
about.

The script refuses a request that would exceed the model's context budget rather
than truncating it — `jev-1.13` allows 64k tokens for the state plus all
questions together, and 32k for the state plus the longest single question.
A truncated path map scores cells against a system that is missing its last
three actors, and it does it silently. If the script refuses, the honest answers
are to split the actor set across two requests or to trim the state further;
both are better than a number that came from half a map.
