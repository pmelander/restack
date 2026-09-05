### Workshop facilitation

Stressor analysis works better with a group than with an architect alone, for
one reason: the group knows things the architect does not, and most of it is the
kind of knowledge that never reaches a document. The operator who knows the
batch job silently retries. The support lead who knows customers use the export
feature as a backup. The workshop exists to get that into the matrix.

Your role is facilitator. You hold the method and the vocabulary; the room holds
the system knowledge.

#### Before

- The path map must exist. A workshop that starts by arguing about what the
  system is will spend its whole session there. If paths have not been walked,
  run `/stressor walk` first — even roughly.
- Get the right room: someone who operates it, someone who built it, someone
  who supports it, someone who can say no to a change. The last one is the most
  often missing and the most important for organisational stressors.
- Teach the vocabulary in five minutes: actor, intention, path, stressor,
  residual. Precision here saves an hour of ambiguity later.

#### Running it

**1. Walk one path together, out loud.** Do not present a finished walk — walk
it live and let people interrupt. The interruptions are the value: "it doesn't
actually go there any more", "that times out after 30 seconds, not 5". Expect
the path map to change during this step, in a way it never does in a review.

**2. Generate stressors divergently, then converge.** Silent individual
generation first — five minutes, everyone writes their own — then share. Doing
it as an open group discussion first anchors everyone on whoever speaks first
and halves the diversity of the output.

Push for all seven categories. When the room stalls, it has almost always
exhausted the technical ones and needs an explicit prompt for organisational,
social, and regulatory. Introduce the absurd category deliberately: it gives
permission to say the thing that sounds unserious, which is frequently the thing
someone has been quietly worried about for a year.

**3. Score the matrix as a group, and time-box each cell.** Long arguments about
one cell are a signal, not a problem — when the room cannot agree whether a
stressor reaches an actor, nobody knows what that actor does under stress. Score
it 1, mark it `?`, and capture it as a discovery task. That disagreement is
often the most valuable output of the day.

**4. Find clusters together.** Ask the room, not yourself: "what do these four
stressors have in common at this actor?" The mechanism is usually named faster
by the person who operates the thing than by anyone analysing it.

**5. Propose residuals, and let the room attack them.** Specifically ask: what
does this residual break? Who has to approve it? What happens to it at 3am when
it fails? The people who will operate the residual are in the room; use them.

#### Facilitation notes

- **Protect the absurd stressors.** The moment someone says "that's not
  realistic" and the room laughs it off, the method's main advantage is gone.
  Restate it as a mechanism and keep it: "the lizards are a datacentre lost with
  no warning — do we survive that?"
- **Watch for the senior voice anchoring the room.** If the architect or the
  lead scores first, everyone else scores to agree. Have them score last.
- **Do not let it become a risk workshop.** The tell is the room drifting to
  likelihood and mitigation owners. Redirect: we are not ranking probability, we
  are finding which actors are exposed to the most independent things.
- **Capture disagreement rather than resolving it.** A resolved disagreement
  based on nobody's actual knowledge is worse than a recorded open question.

#### After

- Write the matrix up the same day, with `?` cells preserved.
- Turn every `?` into a named discovery task with an owner.
- Send the residual list back to the room before it becomes ADRs — the people
  who will operate them will find the problems.
- Record who was in the room. Six months on, the matrix's credibility depends on
  it, and so does knowing whose knowledge is missing.
