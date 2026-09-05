## Claims About the System Need Evidence

In brownfield and minefield terrain the documentation is wrong, the diagram is
three refactors stale, and the person who knew is gone. Treat every statement
about how the existing system behaves as a **material claim**.

A claim about an actor's behaviour, an integration's contract, a path's shape,
or a failure mode is admissible only with a source:

| Source | Confidence |
|---|---|
| Code read, config read, schema inspected | High |
| Log, trace, or metric observed | High |
| Live probe run against the system | High |
| A person who operates it, asked directly | Medium |
| Documentation, diagram, wiki, prior HLD | **Low — verify before relying on it** |
| Inference from naming, convention, or familiarity | **Not evidence** |

When a cheap probe would settle the question, run it before asking the
architect and before declaring anything blocked.

Anything you carry forward without a source is an **assumption**, not a fact.
Say so in the moment (`ASSUMPTION: ...`), and register it in
`docs/journey/assumptions-register.md` with what would validate it. An
unregistered assumption is how a design review ends up finding "critical
issues" that were really just unexamined beliefs from Phase 1.
