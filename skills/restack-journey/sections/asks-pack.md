### Asks pack: what the design needs from people outside it

An asks pack turns the register's open asks into text a recipient can act on.
Each ask closes an assumption that only someone outside the design can settle
(ADR-026 in the ReStack repository). The register remains the record. The pack
is that record, written for the people who have to answer.

**The architect reads the asks first.** The `Ask` prefix says someone
outside the design *can* settle a row. It does not say the architect can't.
On the engagement behind ADR-027, the architect settled 33 of 43 routed
asks in one sitting, and three decisions and one structural finding came out
of the answers. A pack sent first would have sent 36 questions to eight
teams and surfaced those weeks later. So every routed ask goes to the
architect before it goes into a pack, and only the deferred ones are packed.

**The pack's reader is not the architect.** A recipient outside the design
does not know what a stressor, a residual, an actor, a gate or `D29` is, and
should not have to. They know their own system, and they need four things:
the question, why it matters to them, what is held up while it stays open,
and what we already know.

### Before writing

1. **Run `journey.py asks`** (see *Journey Files*). It lists the open asks by
   recipient, with when each was last asked. It also lists open rows whose
   check reads like an ask but has no recipient, and recipient names that may
   be the same recipient. If the helper is unavailable, build the same list by
   hand: rows that are Open or Partly resolved, whose `Validates it` starts
   with `Ask`.
2. **Settle the routing in one confirm.** Put the unrouted rows and the
   look-alike names in one table. For each, propose a recipient or "settled
   inside the design", give one line of reasoning, and confirm with one
   choice: accept as proposed, or adjust. Then run `assume route` once per
   confirmed row. Never route a row the architect has not confirmed. Who is
   asked is their call, and a wrong recipient costs a round trip.
   **When the owner is unclear** and `Design boundary:` in `journey-state.md`
   names the architect's own team, propose **the architect first** for that
   row, not the neighbouring team. The row stays unrouted and goes into
   triage with the rest, and its defer option names the team you would
   otherwise have routed it to. Route it only if the architect defers it.
3. **Read what each ask holds up.** Use the row's `Depends on it` cell, then
   `journey-state.md` for the current phase and the gate it is heading for.
   "Holds up" is a gate, a decision, an iteration or a document. Triage needs
   it in the architect's terms, and the pack needs it in the recipient's.
4. **Triage with the architect** (next part), unless they skipped it for a
   named recipient.
5. **Ask what else is going out.** Documents, updated handoffs and decision
   packs that close no assumption go in the pack's *Also going out* list. If
   one of them is really a question, it is an unregistered ask: register it
   with `assume add --ask` first, then triage and pack it.

### Triage: the architect first

Walk every routed ask in the `asks` output, plus the rows marked "the
architect first" in routing, recipient by recipient. Each ask gets **one
choice question**, one at a time, per *Questions*:

- **The question is in the architect's terms.** IDs, the belief, what it
  holds up, and "asked <recipient> on <date>" if it was sent before. Rows
  that one answer would settle together share a question, which names every
  ID.
- **Two or three plausible answers**, drawn from the register row, its
  source and the evidence on disk. Never offer an answer the evidence does
  not support just to fill the list. With no evidence either way, offer the
  belief as recorded and its negation.
- **`Defer to <recipient>` is always the last option.** Never drop it, even
  when an answer looks certain.

Write each answer as it comes, before the next question. An interrupted
triage then loses nothing: the next `asks` run no longer lists a settled row.

| The architect's answer | Write |
|---|---|
| settles the row | `assume status A-<n> "Resolved" --why "Architect, <date>: <the answer>. Medium: asked directly."` |
| settles part of it | `assume status A-<n> "Partly resolved" --why "..."`; the remainder stays routed, and the pack asks only for that |
| makes the ask moot | `assume status A-<n> "Withdrawn" --why "Architect, <date>: ..."` |
| contradicts a logged decision, or withdraws an ADR's point | **STOP the triage.** Issue the brief now: `decision open`, the brief, `decision answer` (with `--supersedes D<m>` when it reverses one). The row's status follows the decision. Then resume |
| shows the row is routed wrong | confirm the new recipient, `assume route`, and ask again with the new defer option |
| `Defer to <recipient>` | nothing. The row stays routed and goes in the pack |

- **An architect's answer is Medium, not High.** In the evidence table it
  is "a person who operates it, asked directly". The `--why` says so. When
  they cite a document or a measurement, the confidence is that source's,
  and the `--why` names it.
- **A one-way door keeps its check.** If a wrong answer would be expensive
  to reverse, write the check that would catch it into the `--why`
  ("confirm in the shadow run"). If the design goes ahead before that check
  runs, register the check itself with `assume add`, so it is tracked.
- **An answer can expose what no ask covered**, such as a fact about traffic
  or ownership that changes what the design reaches. Register it with
  `assume add` (no `--ask`) or raise a brief. Name it in the reply. Never
  leave it in the conversation.
- **Never settle a row on your own reading of an answer.** If an "Other"
  answer is ambiguous between settling, partly settling and deferring, ask
  which.

**Skipping triage** is the architect's call, for one named recipient:
`/restack-journey asks <recipient> --no-triage`. Offer it when the architect
says up front that the recipient's asks must go to that team, such as a
legal decision or figures only that team holds. Never skip triage for the
whole pack, and never on your own judgement.

If triage leaves nothing deferred and nothing is going out, write no pack.
Say so, with the counts.

### Writing each section

- **One section per recipient**, readable without the rest of the pack: no
  "see above", and no term defined in another section.
- **A question per answer, not per row.** When one answer settles several
  assumptions, ask it once and list every ID it closes.
- **Ask for the answer in the form that settles the check.** Name the unit,
  the period and the form: "the hold-up time in seconds, from the UPS
  datasheet" settles a check; "can you tell us about the UPS?" starts a
  thread. Where a yes or a no settles it, say so.
- **Why it matters, in their terms.** Describe the effect on their system,
  their users or their team, not the residual it protects. Leave out the
  method's vocabulary entirely.
- **What it holds up.** Name the gate, decision or document. A deadline goes
  in only if the architect gave one. Never invent a date to create urgency.
- **What we already know.** Give the source by name. Link a document only
  when the recipient can open it. Quote only what the question needs. Do not
  paste register rows, matrix rows or long stretches of design documents, and
  leave out anything the architect has marked confidential or internal.
- **Asked before.** If `asks` shows a previous send, say so plainly, with the
  date: "We first asked this on 2026-04-02." Do not apologise or escalate.
- **The reference line keeps the IDs** (`Ref: A-12, A-14`), so an answer can
  be matched back to the register. It is the only place an ID appears.

### Format

Write `docs/journey/asks-<YYYY-MM-DD>.md`. Never overwrite an earlier pack: a
second pack on the same day takes a `-2` suffix. Earlier packs are the record
of what was asked, of whom, and when.

```markdown
# Asks: <engagement or design name>

<YYYY-MM-DD> · from <the architect, or the design team> · built from the
assumptions register on that date. Each section below stands alone and can be
forwarded by itself.

Answered by the architect: <n> · deferred: <m> · <w> withdrawn, if any.

| Recipient | Answered by the architect | Deferred | Questions | First time asked | Asked before |
|---|---|---|---|---|---|
| <recipient> | <n, or "not triaged"> | <n> | <n> | <n> | <n, with the oldest date> |

---

## <Recipient>

<Two or three sentences in their terms: what is being designed, and why it
touches their system or team.>

### 1. <the question, answerable as asked>

- **Why it matters:** <the effect on them, or on the design, without the
  method's vocabulary>
- **What it holds up:** <gate, decision or document; a date only if the
  architect gave one>
- **What we have so far:** <source by name; a link only if they can open it>
- **Asked before:** <date> *(omit the line when this is the first time)*
- **Ref:** A-<n>, A-<m>

---

## Also going out

| What | To | Why |
|---|---|---|
| <document or pack> | <recipient> | <what it changes for them> |
```

### After writing

1. **STOP.** Give the pack's path and the summary table. Writing the pack
   records nothing. The skill never sends anything.
2. **Ask whether anything has been sent, as its own question:** "Has any of
   these sections been sent?", a multi-select of the sections plus
   `None sent yet`. Nothing else counts as a send. "Which sections are going
   out", "these are ready" and "send them" are plans, not sends. Neither is
   the architect reading or approving the pack.
3. **Record only what the architect says went:** one
   `assume asked <IDs> --to "<recipient>"` per section sent, with `--date`
   when it went on another day. A section not yet sent records nothing, and
   appears again in the next pack. When the architect later says a section
   went, record it then.
4. `history add --command "/restack-journey asks" --outcome "<n> answered by
   the architect, <m> deferred to <k> recipients; sent: <recipients, or none
   yet>" [--decision D<n>]`, naming any brief triage raised.

**A send recorded in error** is cancelled with
`assume unasked A-<n> [A-<m> ...] --why "<what the architect said>"`. It
writes a status line that repeats the status and cancels the row's last
send, so `asks` counts it as asked one time fewer, or never. Never correct a
send with `assume status`: the send would still count.

### Done when

- Every routed open ask in the `asks` output was put to the architect, one
  question each with `Defer to <recipient>` as an option, before the pack
  was written, unless the architect skipped triage for that recipient.
- Every answer is in the register as a status line that cites the architect
  and the date, at Medium.
- An answer that contradicts a logged decision or an ADR produced a
  numbered brief in the same run.
- The pack holds only deferred asks. Every one is in exactly one section, or
  is named in the reply as held back by the architect. The summary shows
  answered and deferred counts.
- No ID in the pack belongs to a row that is no longer Open or Partly
  resolved.
- Every section reads on its own, and the method's vocabulary appears only on
  `Ref:` lines.
- No deadline appears that the architect did not give, and no ask is recorded
  as sent unless the architect confirmed it went, in a question that asked
  exactly that.
