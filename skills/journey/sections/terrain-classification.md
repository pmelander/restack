### Terrain classification protocol

Terrain is not a label you assign from the project's job title. "Greenfield"
projects that integrate with two existing systems are brownfield on those
paths. A modernisation with an unmapped 15-year-old core and an EA board that
must approve every vendor is not brownfield — it is minefield, and treating it
as brownfield is how the journey fails in month three.

Classify from evidence, one question at a time. Do not batch these.

**1. Aspiration.** What should this system achieve? Push until the answer is a
capability, not a technology. "Move to Azure" is not an aspiration; "originate a
mortgage in under a day without a human rekeying anything" is. Record the
aspiration verbatim — every later decision brief is measured against it.

**2. What exists today.** Nothing / a system you understand / a system you have
been told about. The third case is the common one and the dangerous one. Ask:
*who has actually read this code in the last year?* If the answer is nobody, the
knowledge is documentation-grade, which the evidence rules rate Low.

**3. Blast radius of being wrong.** What happens if a change to this system
misbehaves in production? Inconvenience, lost revenue, regulatory exposure, or
physical/financial harm to a person. This is the strongest single signal for
minefield.

**4. Organisational resistance.** Who can stop this, and what do they need?
Architecture boards, vendor approval, change advisory, a team that owns a
component and did not ask for this work. **Organisational constraints are
stressors** — they belong in the matrix, not in a risks slide. If more than one
gate exists, weight toward minefield.

**5. Team capability against the target.** Does the team have production
experience with what the design will likely require? A capability gap is a
stressor on every path that depends on the new technology.

### The classification

| Signal | Greenfield | Brownfield / Oilfield | Minefield |
|---|---|---|---|
| Existing system | none | present, partly understood | present, poorly understood |
| Knowledge source | design intent | code + people available | documentation + folklore |
| Blast radius | contained | real but recoverable | severe or irreversible |
| Organisational gates | few | some | many, with veto power |
| Expected discovery effort | none | days | weeks, and it will find more |

Mixed signals are normal and mean **classify per path, not per project**. A
greenfield service that writes to a legacy ledger is greenfield on its own paths
and minefield on the ledger path. Say so explicitly and let the route follow the
riskiest path in scope.

### Gate

Terrain determines everything downstream — how much discovery is mandatory,
how many iterations to expect, whether a walk can begin at all. It is an
**approach gate**. Issue the decision brief with your classification as the
recommendation, the evidence behind it, and the cost of being wrong in each
direction (over-classifying burns weeks on discovery nobody needed;
under-classifying puts a design on top of a system you do not understand).

**STOP.** Do not map the route, recommend a first move, or write journey state
until the architect confirms the terrain.
