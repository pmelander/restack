## Residuality Vocabulary

Use these words precisely. Sloppy vocabulary is how stressor analysis decays
into risk-register thinking.

**Aspiration** — the overarching goal a stakeholder communicates to the
architect. It reflects strategic intent and is broken down into underlying
motives and actionable purposes.

**Intention** — a signal that defines what should happen next. Intentions
connect actors and guide the flow of change through the system.

**Actor** — any user, application, module, or system component that acts upon
an intention to change. An actor may update its internal state and/or propagate
the intention onward. Actors can be stateful or stateless.

**Path** — a sequence of actors connected by intentions. A path always starts
and ends with a single actor. Paths never fork — when forking occurs, a new
path is created. Each path ends when the intention is fully resolved.

**Stressor** — any fact or external influence on a system that is outside our
current understanding. Stressors identify fault lines, reveal weak spots, and
highlight slow reactions in the architecture.

**Residual (residue)** — a specific addition, removal, or modification
introduced to the system in response to a stressor. It is localised, discrete,
and persists after the stressor has been addressed. A residual may be a new
actor, a new intention, or a new path.

**Walk** — traversing a path to analyse the state and behaviour of each actor
as the intention propagates. Walks are iterative, performed again as stressors
and residuals evolve.

**Terrain** — the character of the environment being changed. *Greenfield*:
blank canvas, paths are designed. *Brownfield / oilfield*: existing system,
partial knowledge. *Minefield*: existing system, high fragility, political
complexity, change carries hidden risk.
