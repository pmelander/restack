# Grounding, not absurdity

The active ingredient in a stressor is **unrelatedness to the system**.
`/restack-stressor` reaches for it through an `absurd` category, and that
category gets read too literally - fire-breathing lizards, the moon, everyone's
clocks running backwards. Those work in a workshop as icebreakers and they have
a defect the method does not acknowledge: **they are dismissible**.

A mundane, entirely unrelated real-world event is not.

> A regional authority imposes a moderate water-abstraction restriction across
> four municipalities.

That is a harder stressor against a booking platform than any lizard, because
nobody in the room can argue it will not happen. The argument stops being about
whether to take the stressor seriously and starts being about what the system
does when it arrives - which is the only conversation worth having.

## Two dials, not one

| | |
|---|---|
| **plausibility** | how far outside the expected the event sits: `mundane`, `stretched`, `absurd` |
| **grounding** | how much of the system the renderer saw: `uncoupled`, `adjacent`, `aimed` |

These are independent, and conflating them is the mistake. An `uncoupled` draw
is not a silly one - it is one the renderer produced without ever seeing the
system. That is what breaks the architect's frame, and a system-aware prompt
destroys it silently by re-importing the prior the sampler exists to escape.

Keep `absurd` in the taxonomy. It is a real register and occasionally the only
thing that gets a room to reason about total loss with no warning. Just stop
asking it to carry the work that `uncoupled` does.

## Both tracks, every batch

Aimed stressors use what the team knows and find the cracks in known structure.
Uncoupled ones find the cracks nobody was looking for. A batch needs both, and
the ratio is not a judgement call to make batch by batch - it is what
`--balance grounding,plausibility` fixes by construction. Left probabilistic, a
batch of thirty can plausibly come back with two uncoupled specs, and the track
that does the distinctive work is the one that goes missing.

## Zero rows are the finding, not the waste

Uncoupled draws miss more often. Most of them will produce a matrix row that
scores against no actor at all.

**Do not triage them before the matrix.** Deciding in advance which random
events are worth walking is exactly where the architect's prior re-enters, and
it re-enters wearing the clothes of efficiency. Sample more on that track, walk
them all, and let a full-zero row stand: it is a real statement about how
tightly this system is coupled to the world, and it is information the team
does not otherwise have.

The same applies to `validate.py`. It checks four things and relevance is
deliberately not one of them.

## The mechanism belongs to the walk

`/restack-stressor` is right that an absurd stressor needs translating to its
mechanism - "fire-breathing lizards melt the inventory datacentre" is
functionally sudden total physical loss of one component with no warning.

But that translation belongs **in the walk, at each actor**, not in the
generator's output. Pre-supplying it hands the team the answer and re-anchors
them on a mechanism somebody else chose; the same statement walked against six
actors may resolve to six different mechanisms, and the interesting ones are
the mechanisms nobody predicted.

So the generator emits the statement and nothing else. No impact, no affected
component, no "which would mean".
