### From assessment to development

Most capability roadmaps fail the same way: they are a list of dimensions with
target levels and dates, nobody's actual week changes, and the next assessment
finds the same ratings.

The difference between a roadmap that works and one that does not is whether
development is attached to **work the team is already doing**.

#### Prioritising gaps

Do not work on the lowest rating. Work on the gap that is costing the most
*now*, which is a different question.

Score each gap on three things:

1. **Consequence** — what is this costing? Point at incidents, rework, delays,
   decisions being relitigated. A Level 1 rating on a dimension that is not
   biting is not urgent.
2. **Leverage** — does improving this improve others? Learning culture is the
   highest-leverage dimension: a team that reviews outcomes improves
   decision-making and design quality without being worked on directly.
3. **Readiness** — does the team have the appetite and the slack? A correct
   priority the team cannot act on is not a priority.

**Pick one, occasionally two.** A roadmap addressing five dimensions addresses
none. The others usually improve as a side effect of the one that gets
attention.

#### Design development into real work

The rule: **development happens on live work, or it does not happen.**

Training sessions, book clubs and workshops produce knowledge, and knowledge is
not what the assessment measured. The assessment measured practice under
deadline. Only practice changes practice.

| Instead of | Do this |
|---|---|
| A workshop on ADRs | The next three real decisions get ADRs, reviewed together |
| A talk on stressor analysis | One live path walked and stressed, as a group |
| Reading about fitness functions | One fitness function written for an existing residual |
| A course on documentation | One existing document tested on an actual newcomer |
| A session on evaluation | The next technology choice evaluated across all seven dimensions |

Each is real work that had to happen anyway, done with attention. The cost is
slower delivery on that item, and that cost should be stated so it can be
agreed rather than resented.

#### Deliberate practice

Where a specific skill needs building, design the exercise so it has a
**feedback loop** — the missing ingredient in most attempts.

- **Prediction exercises.** Before an incident review, everyone writes what
  they think the cause was. Compare. Fast, uncomfortable, and the most
  effective calibration exercise available.
- **Retrospective ADR writing.** Take a decision made without one and write it
  now. The gaps in the reasoning are visible immediately and safely, because
  the decision is already made.
- **Pre-mortem.** Before a design commits, each person writes how it failed a
  year from now. Feeds directly into stressor generation.
- **Review swaps.** Two people review each other's designs against the same
  criteria, then compare what each found. What one missed is the specific
  learning.
- **Walk someone else's path.** An architect walks a path in a system they do
  not own. Reveals which of their assumptions were about *systems* and which
  were about *this* system.

#### The roadmap

Three phases over roughly six months, each with a named practice, the real work
it attaches to, an owner, and an observable outcome.

The observable outcome is the part that is usually missing and matters most:
not "improve documentation" but "a newcomer can deploy the service from the
runbook without asking anyone". Something you could check.

**Commitments must come from the team, in their words, at the end of the
session.** A roadmap written for a team is a document; one they wrote is a
plan. If they will not commit to it, that is the real finding and it usually
means the priority is wrong or there is no slack — both worth knowing now.

#### Tracking

Re-assess in three to six months. Less than three and there is nothing to see;
more than six and the assessment has stopped being an input.

Track **practice, not sentiment**: are outcome reviews happening, is the second
stressor iteration being run, are ADRs being written for one-way doors. Count
them.

When a rating has not moved, the useful question is not "why did you not
improve" but **"what got in the way?"** — the answer is usually structural
(no slack, a reorganisation, the priority was wrong) and that is a finding about
the environment rather than the team.
