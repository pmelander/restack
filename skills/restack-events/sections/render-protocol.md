# Render briefs

One subagent per spec. The brief below is the subagent's entire prompt: the
spec, the rules, nothing else. Which variant you send is decided by the spec's
`grounding` value, and that decision is the one thing in this skill that must
not be improvised.

## Rules common to all three

Put these in every brief, verbatim in substance:

- Write **one to three sentences**. No preamble, no explanation, no caveats.
- Render the spec's dimensions as a concrete event. Do not name the dimensions
  in the output, and do not restate the spec.
- **Never name a real person.** Institutions, authorities, bodies and generic
  groups only. A fabricated claim attributed to a named real person is
  defamatory content whatever label travels with it, and labels do not travel
  with text once it leaves the pipeline.
- **Do not supply the mechanism.** No "which would mean", no "this could
  affect", no impact assessment. The statement is the event and stops there.
- `magnitude`, `onset` and `reversibility` show up as details of what happened,
  never as adjectives lifted from the spec.
- Return **only** a JSON object:
  `{"spec_id": "<id>", "statement": "<text>", "grounding": "<grounding>"}`

For a spec carrying a `second` object, write both events in the same statement
as things that happened together. Do not explain how they relate — whether they
are connected is what the walk is for.

## uncoupled - the brief carries the spec and nothing else

> You are writing one event statement from a specification. You will be given
> no information about any system, and you must not ask for any or go looking
> for any. Write the event as though reporting on the world.

**The subagent runs with no tools.** Not Read, not Grep, not Glob, not Bash. A
subagent that can reach the filesystem may go and find the project's design
docs on its own initiative, and the blind draw has quietly stopped being blind
with nothing downstream to say so. This is the one property the HTTP version of
this pipeline got for free.

## adjacent - one sentence of sector, no more

> The reader of this statement works in <sector>. Write an event that could
> plausibly appear in that sector's news, drawn from the specification below.

`<sector>` is a single clause: "regional passenger aviation", "retail
banking in the Nordics". Not the system, not its components, not its
customers, not its vendors. If you find yourself writing a second sentence of
context, the spec belongs on the `aimed` track instead.

**Also runs with no tools**, for the same reason.

## aimed - the only brief that sees the system

> The system under analysis is described below. Write an event that would
> stress it, drawn from the specification.
>
> <the system's aspiration, actors, paths, and existing residuals>

This is the only track allowed read-only tools, and the only one that should
ever see the actor and path map. Include existing residuals deliberately:
restack's own guidance is that after iteration two you start generating
stressors your residuals already handle, so name them and ask for something
they do not cover.

## Why the split is enforced rather than suggested

The two tracks find different things. Aimed stressors use what the team knows
and find the cracks in known structure. Uncoupled ones find the cracks nobody
was looking for, and they only work while nobody has told the renderer what the
system is. One sentence of system context turns a blind draw into an aimed one,
and the batch still looks fine.
