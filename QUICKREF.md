# ReStack — Quick Reference

Every command, in journey order. Type `/restack` in Claude Code to see them all.

```bash
git clone https://github.com/pmelander/restack.git ~/restack
cd ~/restack && ./setup                # Windows: .\setup.ps1
```

`./setup --dry-run` shows what would change · `--symlink` for development ·
`/restack-upgrade` to update later. See [INSTALL.md](INSTALL.md).

---

## The shape of an engagement

```
/restack-journey start           classify terrain, map the route
        ↓
/restack-discover ...            brownfield & minefield only
        ↓
   ═══ CONFIDENCE GATE ═══       do we know this system well enough to stress it?
        ↓
/restack-stressor walk           ┐
/restack-stressor generate       │
/restack-stressor analyze        │  the loop
/restack-stressor residues       │
        ↓                        │
   ═══ ITERATE GATE ═══          ┘  is impact low enough, or do we loop?
        ↓
/restack-adr create              document each residual as a decision
/restack-solution-doc hld        capture the design
/restack-design-review complete  validate it
        ↓
/restack-journey cadence         the rhythm once it is live
```

### The three gates

The workflow **stops** at each of these and waits for you. They are not
recommendations you can read past.

| Gate | Where | Settles |
|---|---|---|
| **Confidence** | `/restack-discover confidence` | do we understand the system well enough to stress it? |
| **Iterate** | `/restack-journey iterate` | is impact low enough to proceed, or do we loop? |
| **Approach** | wherever two viable designs exist | which way, and is it a one-way door? |

A gate reached with **low confidence on an irreversible decision** routes
backwards to discovery, not forwards to a choice.

---

## Orchestration

```bash
/restack-journey start           # classify terrain, map the route, name the first move
/restack-journey where           # mid-journey: where am I, what was skipped, what next
/restack-journey iterate         # THE ITERATE GATE — loop or proceed
/restack-journey review          # health check against the seven journey failures
/restack-journey cadence         # ongoing rhythm for a live system
```

State lives in `docs/journey/` — position, iteration history, decisions,
assumptions. Read at the start of every command, written at the end.

## Discovery — brownfield and minefield

```bash
/restack-discover paths          # map what is actually there; settle the boundary
/restack-discover actor <name>   # what an actor really does, vs what docs claim
/restack-discover intentions     # trace one intention until it resolves or dies
/restack-discover gaps           # prioritise unknowns: impact × likelihood × cost to close
/restack-discover organisation   # map resistance, translate it into stressors
/restack-discover confidence     # THE CONFIDENCE GATE — ready to walk?
```

Confidence thresholds rise with terrain. In brownfield an unknown becomes a
registered assumption; in a **minefield an unknown on a critical path blocks**.

## Stressor analysis

```bash
/restack-stressor walk [path] ["stressor"]   # traverse a path, actor by actor
/restack-stressor generate [count]           # 20-30 across 7 categories, incl. absurd
/restack-stressor analyze                    # build the impact matrix
/restack-stressor vulnerabilities            # concentration, clusters, flatness, zeros
/restack-stressor residues                   # residuals by mechanism, ranked by leverage
/restack-stressor iterate                    # re-walk, per-actor before/after
/restack-stressor workshop                   # facilitate with a group
/restack-stressor compliance <pack>          # inject a regulatory stressor pack
/restack-stressor import <file> [sheet]      # import an existing matrix
```

Scoring is **binary** — 1 if the stressor reaches the actor, 0 if not. Not a
simplification: severity scales let uncomfortable stressors get argued down, and
what you want is breadth of exposure, not depth of any one failure.

`/restack-stressor compliance list` shows available packs. GDPR ships as a
worked example.

## Decide and record

```bash
/restack-adr create <title>      # with reversibility + the residual it implements
/restack-adr list                # flags ADRs past their review date
/restack-adr update <number>     # supersede rather than rewrite
/restack-adr review <number>     # outcome review: predicted vs happened
/restack-adr search <term>       # searches alternatives too — finds what you rejected
/restack-adr template

/restack-tech-stack recommend                    # a stack, seven dimensions each
/restack-tech-stack evaluate <tech>              # incl. "what would make this wrong?"
/restack-tech-stack compare <a> vs <b>           # weighted before scoring
/restack-tech-stack migrate from <old> to <new>  # starts from "probably don't"
/restack-tech-stack report
/restack-tech-stack retro <tech>                 # how did that choice play out?

/restack-solution-doc hld                # actors, paths, and what each residual defends against
/restack-solution-doc lld [component]    # only where an LLD is warranted
/restack-solution-doc deployment         # incl. what CANNOT be rolled back
/restack-solution-doc runbook            # incl. what NOT to do at 3am
/restack-solution-doc complete
/restack-solution-doc update <type>
/restack-solution-doc review <type>

/restack-design-review architecture      # boundaries, coupling, state, blast radius
/restack-design-review data              # ownership, dual writes, consistency, recovery
/restack-design-review api               # contract, evolution, error semantics
/restack-design-review security          # threat model first, not a control list
/restack-design-review performance       # shape, not speed
/restack-design-review consistency       # do the documents still agree with each other?
/restack-design-review complete          # all five, then consistency
/restack-design-review self-check        # you review; it only pushes on assumptions
```

Every design review triages findings first — *system* findings classify against
the matrix as **A** matrix caught it, residual missing · **B** residual present
but not working · **C** matrix should have caught it · **D** genuinely new;
*artifact* findings (documents disagreeing with each other) are reported
separately. Mostly **C** is a discovery problem wearing a review's clothes;
mostly artifact means the analysis is sound and the docs are not keeping up.

## Build it

```bash
/restack-cloud design <architecture>     # primitives named as the residuals they are
/restack-cloud iac <provider>            # terraform | cloudformation | bicep | cdk
/restack-cloud review                    # six pillars, then what they cannot reach
/restack-cloud cost <analysis>           # checks the matrix before removing anything
/restack-cloud migrate <to-cloud>        # six R's; Retire checked first
/restack-cloud dr                        # tier derived from stressors, not picked

/restack-capacity estimate               # arithmetic shown, assumptions inline
/restack-capacity scale <strategy>       # horizontal|vertical|auto|database|cache|cdn
/restack-capacity bottleneck             # ceilings, not utilisation; names the second one
/restack-capacity load-test              # validates residuals, not just throughput
/restack-capacity forecast               # a trigger and a lead time, not a line
/restack-capacity right-size             # separates over-provisioning from headroom
```

## Get better at it

```bash
/restack-arch-learning analyze           # predicted vs happened; diagnose each miss
/restack-arch-learning outcomes          # which decisions have no recorded outcome
/restack-arch-learning retrospective     # facilitated, evidence circulated first
/restack-arch-learning lessons           # routed to where they act, not to a document
/restack-arch-learning patterns          # candidates for extraction
/restack-arch-learning trends            # miss types, estimate bias, iteration counts

/restack-patterns extract                # three independent instances or it is not one
/restack-patterns catalog                # indexed BY PROBLEM
/restack-patterns suggest <scenario>     # checks the context boundary against your case
/restack-patterns effectiveness          # incl. abandonments — the strongest signal
/restack-patterns anti-patterns          # incl. why people keep choosing it
/restack-patterns evolve                 # promote, amend, deprecate — never delete

/restack-evolve assess                   # change cost measured with real changes
/restack-evolve fitness-functions        # automated checks that residuals still hold
/restack-evolve brittleness              # what stops the stressor loop converging
/restack-evolve increment                # seam first; cleanup is a step, not an intention
/restack-evolve health                   # a muted fitness function is a failed control
/restack-evolve coach                    # asks; does not answer

/restack-capability-assessor assess      # practice under deadline, not knowledge
/restack-capability-assessor gaps        # what it costs now, not the lowest score
/restack-capability-assessor roadmap     # attached to live work or it will not happen
/restack-capability-assessor track       # "what got in the way?", not "why didn't you"
/restack-capability-assessor exercises   # deliberate practice with a feedback loop
/restack-capability-assessor compare     # practices, never scores
```

## Utility and maintenance

```bash
/restack-upgrade                         # pull, reinstall, show what changed
                                         #   also repairs a broken install

/restack-excel read <file> [sheet]       # to a markdown table
/restack-excel preview <file> [rows]     # check the shape first
/restack-excel sheets <file>
/restack-excel convert <file> [sheet]    # write to a file instead of the chat
```

---

## Vocabulary

Used precisely by every skill. Full definitions in [RESIDUALITY.md](RESIDUALITY.md).

| | |
|---|---|
| **Aspiration** | what the system should achieve — every decision is measured against it |
| **Intention** | a signal defining what happens next; connects actors |
| **Actor** | anything that acts on an intention — service, module, queue, person |
| **Path** | a sequence of actors connected by intentions. Paths never fork; a fork is a new path |
| **Stressor** | a fact or force outside your current understanding |
| **Residual** | a discrete change — new actor, intention, or path — that persists after the stressor |
| **Walk** | traversing a path to see what each actor does as an intention propagates |
| **Terrain** | greenfield / brownfield / oilfield / minefield — sets thresholds and route |

---

## Where things are written

```
docs/journey/          journey-state, iteration history, decisions log, assumptions
docs/discovery/        path maps, actor profiles
docs/stressor-analysis/ stressor sets, matrices, residuals
docs/adr/              decisions
docs/architecture/     HLD, LLDs, evolvability assessments
docs/deployment/       deployment guide
docs/operations/       runbook
docs/reviews/          design review reports
docs/patterns/         pattern catalog, indexed by problem
docs/learning/         outcome analyses, retrospectives
```

---

## Everyday recipes

| I want to... | Run |
|---|---|
| Start anything | `/restack-journey start` |
| Pick up someone else's engagement | `/restack-journey where` |
| Understand a system before changing it | `/restack-discover paths` → `actor` → `confidence` |
| Find out what will break it | `/restack-stressor walk` → `generate` → `analyze` |
| Decide whether to keep iterating | `/restack-journey iterate` |
| Record a decision properly | `/restack-adr create` |
| Check a design before building | `/restack-design-review complete` |
| Work out how big it needs to be | `/restack-capacity estimate` |
| Know why every change is expensive | `/restack-evolve brittleness` |
| Find out if we are getting better | `/restack-arch-learning trends` |
| Handle a regulation | `/restack-stressor compliance <pack>` |
