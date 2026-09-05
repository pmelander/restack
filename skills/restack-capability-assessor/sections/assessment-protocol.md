### Running an honest assessment

The failure mode is not inaccuracy. It is an assessment everyone agrees with
and nobody acts on, because it was pitched to be comfortable.

#### Before anything: establish what it is for

Ask directly, and get a real answer:

- **Development** — the team wants to get better. Honesty is safe and the
  assessment can be blunt.
- **Reporting upward** — someone else will read it. The team will manage its
  answers accordingly, and you must say so out loud rather than pretending
  otherwise.
- **Comparison between teams** — the most distorting purpose, and it needs
  handling explicitly (see below).

If the stated purpose is development but the output goes to a manager who makes
staffing decisions, the assessment will be optimistic and you will not be told
why. Name the tension at the start. An assessment run under an unstated purpose
is data about what the team thinks is safe to say.

#### Gather evidence first, then talk

**Read the artefacts before interviewing.** The ADRs, the documents, the review
findings, the retrospectives, the pattern catalog, the journey state, the
fitness functions. Form provisional ratings with the evidence noted.

This ordering matters for the same reason it does in a retrospective:
conversation first anchors you on the team's self-image, and the artefacts then
get read as confirmation.

Then interview to explain what you found — not to establish it. "Your ADRs
consistently list two alternatives and one is always a strawman; tell me what
happens when a decision gets made" is a question that produces information.
"How would you rate your decision-making?" produces a number.

#### Ask about behaviour under pressure

The single most useful line of questioning. Practices that hold on a calm week
and dissolve at a deadline are Level 2, whatever the documentation says.

- When did you last skip the ADR? What was happening?
- When did you last ship without a review?
- What is the first practice to go when a date is at risk?

The answers are almost always honest, because the question does not sound like
a test — and they place the team more accurately than any artefact.

#### Involve the team in rating, but do not let them set it

Self-assessment alongside yours is valuable for the **gaps between the two**,
which are the interesting output:

- **Team rates higher than evidence** — usually a practice they believe is
  established that only one person performs, or knowledge mistaken for
  practice.
- **Team rates lower than evidence** — often a team that is doing well and
  comparing itself to an idealised standard. Worth correcting; it demoralises.
- **Wide spread within the team** — the practice is inconsistent, which is
  itself the finding, and more useful than any single number.

Present your rating with its evidence, hear the disagreement, and change your
mind where they show you something you missed. Do not adjust to reduce
discomfort — an assessment that has been negotiated is a negotiation, not an
assessment.

#### Write it up

Use `templates/capability-assessment-template.md`, the canonical format.

Three rules for the writing:

**Lead with what is strong**, specifically and with evidence. Not
encouragement — a team needs to know which practices to protect when they start
changing things.

**Name the single most consequential gap** rather than listing six. Six gaps
produce no action; one produces movement, and the others usually improve
alongside it.

**Never rank individuals.** This assesses a team's practices. The moment it
reads as a judgement of people, every future assessment is managed and the
instrument is destroyed permanently.

---

### Comparing teams

Legitimate for finding where practice already exists that could spread. Corrosive
when it becomes a league table — and it becomes one by default unless prevented.

**Compare practices, never scores.** "Team A reviews ADR outcomes quarterly;
Team B does not" is actionable. "Team A: 3.4, Team B: 2.8" is a ranking that
teaches teams to manage their assessments.

**Account for context.** A team on a greenfield internal tool and one on a
regulated minefield system face different demands. The second may be at Level 2
on documentation and be entirely correct to be, given where its effort is
going.

**Use it to route knowledge, not to rank.** The output should be "Team A's
retrospective practice is the strongest here — Team B should sit in on one",
not an ordering.

If the comparison is going to be used for ranking regardless, say so plainly
and let the requester decide whether to proceed knowing that future assessments
will be managed and the data will degrade.
