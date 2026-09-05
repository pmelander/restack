### The six dimensions

**1. Decision-making quality** — making sound, well-reasoned architectural
decisions. Evidence: ADR quality, whether alternatives are real, depth of
trade-off analysis, whether outcomes are reviewed. Growth is from gut-feel to
evidence-based.

**2. Documentation clarity** — communicating architecture so others can act on
it. Evidence: whether documents answer a newcomer's questions, whether they are
current, whether anyone reads them. Growth is from sparse and stale to living.

**3. Technology evaluation** — choosing technology against context rather than
reputation. Evidence: evaluation rigour, awareness of bias, whether the boring
option is ever chosen. Growth is from hype-driven to context-aware.

**4. Design quality** — producing robust, evolvable architectures. Evidence:
review findings, incident patterns, how the system handles the unexpected.
Growth is from reactive patching to deliberate design.

**5. Evolutionary thinking** — designing for change. Evidence: fitness
functions, reversible decisions, whether changes ship incrementally, brittleness
trend. Growth is from rigid to continuously adaptable.

**6. Learning culture** — improving from experience systematically. Evidence:
retrospective quality, pattern library health, whether outcomes are tracked,
whether the same mistakes recur. Growth is from repeating mistakes to
compounding.

**Residuality capability is measured across dimensions 4, 5 and 6**, not as a
separate line. A team that walks paths, generates stressors honestly, diagnoses
mechanisms and re-walks is showing design quality, evolutionary thinking and
learning culture simultaneously.

---

### The five maturity levels

| Level | Characteristic | The team says | Its risk |
|---|---|---|---|
| **1 Ad-hoc** | inconsistent, reactive, individual-dependent | "we figure it out as we go" | high variance, repeated mistakes, knowledge walks out |
| **2 Aware** | gaps recognised, practices emerging | "we know we should do this better" | inconsistent, abandoned under pressure |
| **3 Defined** | documented, consistent, team-wide | "this is how we do things here" | process rigidity, context-blindness |
| **4 Managed** | measured, data-informed improvement | "we measure and optimise" | optimising the metric rather than the outcome |
| **5 Optimising** | continuous innovation, teaching others | "we're always getting better" | complexity, over-engineering |

**Level 3 is the right target for most teams on most dimensions.** Say this
plainly and often. Presenting 5 as the goal turns assessment into a ranking
exercise, makes everyone below it feel deficient, and produces roadmaps nobody
follows.

Levels 4 and 5 require sustained investment and are appropriate only for the
dimensions that are genuinely core to what this team does. A team at Level 3
across the board with one dimension at 4 is in excellent shape.

**Progress is the goal, not the level.** A team moving 1→2 has done more real
work than one moving 4→5.

---

### Rating with evidence

**Every rating needs an artefact behind it.** A rating from a conversation is a
rating of how the team talks about itself, which is uncorrelated with practice
and usually flattering.

| Dimension | Look at |
|---|---|
| Decision-making | actual ADRs — are alternatives real? are outcomes reviewed? |
| Documentation | actual documents — could a newcomer act on them? are they current? |
| Technology evaluation | evaluations and their retros — was the boring option ever chosen? |
| Design quality | review findings and incidents — do the same causes recur? |
| Evolutionary thinking | fitness functions, flags, deploy frequency, brittleness scores |
| Learning culture | retrospectives, pattern catalog, ADR review completion rate |

**Rate the practice, not the knowledge.** A team that can describe stressor
analysis fluently and has never completed a second iteration is not at Level 3
in evolutionary thinking. What people know and what they do under deadline are
different measurements, and only the second one matters.

**Rate the team, not its strongest member.** One person doing excellent work is
a Level 1 signal — individual-dependent — however good the artefacts look. Ask
who else could have produced this, and what happens if they leave.

**Rate consistency, not the best example.** Look at the median artefact and the
worst recent one, not the one you were shown.

#### Splitting a rating

Where evidence genuinely conflicts — strong ADRs, no outcome reviews — do not
average. Report the split: "Decision-making: 3 on decision quality, 1 on
outcome tracking." The split is more actionable than a middle number, and the
middle number is what makes assessments feel wrong to the people being assessed.
