### Ongoing evolution route and cadence

The system is live. The journey does not end — it changes shape. Stressors
evolve because the environment does, residuals that were sound need
revalidating, and the team's capability moves. A live system with no cadence
quietly returns to fragility while everyone believes the architecture work is
"done".

### Triggered work — driven by change, not the calendar

| Trigger | Run | Because |
|---|---|---|
| A significant change ships | `/restack-discover paths` | the path map may no longer be true |
| Paths changed | `/restack-stressor walk` on affected paths only | re-walk what moved, not everything |
| An incident occurred | `/restack-stressor generate`, then `/restack-arch-learning analyze` | an incident is a stressor that found you first |
| A new integration or dependency | `/restack-discover actor` | a new actor is a new column in the matrix |
| A regulation or contract changes | `/restack-stressor compliance <pack>` | new stressor class, same loop |
| A residual is implemented | `/restack-journey iterate` | confirm impact actually fell |

**An incident is the highest-value input this loop ever gets.** It is a real
stressor, with a real path, and a known outcome. Feed it back as a stressor and
check whether the matrix predicted it. If it did not, the gap is in the path map
or the stressor generation — and that is the most useful thing you will learn
all quarter.

### Periodic work — driven by the calendar

| Cadence | Run | Watching for |
|---|---|---|
| Monthly | `/restack-evolve health` | fitness function drift |
| Quarterly | `/restack-stressor generate` | new stressor classes in the environment |
| Quarterly | `/restack-design-review complete` | architectural drift from the documented target |
| Quarterly | `/restack-arch-learning analyze` | which past decisions actually played out well |
| Quarterly | `/restack-patterns evolve` | promote what worked into the pattern library |
| Every 6 months | `/restack-capability-assessor assess` | team growth against the architecture's demands |
| Continuously | `/restack-adr create` | every significant decision, as it is made |

### Setting the cadence

Cadence is a function of two things, and you must ask about both before
recommending one:

1. **Environment volatility.** How often does something outside the system
   change in a way that matters — regulation, traffic profile, partner APIs,
   competitive pressure? Fast-moving environments need quarterly stressor
   generation; a stable internal system may need it annually.
2. **Team capability maturity.** A team that has internalised path-and-stressor
   thinking needs less formal cadence, because they do it continuously. A team
   new to it needs the calendar until the habit forms.

The output is `docs/journey/cadence-schedule.md`, and it must name an **owner**
per activity. A cadence with no named owner is a document, not a rhythm.

### The residuality goal for this route

You are trying to make this route unnecessary as a *process* while keeping it
alive as a *habit*. When the team re-walks a path because a change shipped —
without anyone consulting a schedule — the cadence has done its job and can be
retired to a lighter check.
