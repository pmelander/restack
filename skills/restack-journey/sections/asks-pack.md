### Asks pack: what the design needs from people outside it

An asks pack turns the register's open asks into text a recipient can act on.
Each ask closes an assumption that only someone outside the design can settle
(ADR-026 in the ReStack repository). The register remains the record. The pack
is that record, written for the people who have to answer.

**The reader is not the architect.** A recipient outside the design does not
know what a stressor, a residual, an actor, a gate or `D29` is, and should not
have to. They know their own system, and they need four things: the question,
why it matters to them, what is held up while it stays open, and what we
already know.

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
3. **Ask what else is going out.** Documents, updated handoffs and decision
   packs that close no assumption go in the pack's *Also going out* list. If
   one of them is really a question, it is an unregistered ask: register it
   with `assume add --ask` first, then pack it.
4. **Read what each ask holds up.** Use the row's `Depends on it` cell, then
   `journey-state.md` for the current phase and the gate it is heading for.
   "Holds up" is a gate, a decision, an iteration or a document, named in the
   recipient's terms.

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

| Recipient | Questions | Assumptions closed | First time asked | Asked before |
|---|---|---|---|---|
| <recipient> | <n> | <n> | <n> | <n, with the oldest date> |

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

1. **STOP.** Give the pack's path and the summary table, then ask which
   sections are going out now (a multi-select choice). Writing the pack
   records nothing. The skill never sends anything.
2. **Record only what the architect says went:** one
   `assume asked <IDs> --to "<recipient>"` per section sent. A section held
   back records nothing, and appears again in the next pack.
3. `history add --command "/restack-journey asks" --outcome "<n> asks for <m>
   recipients; sent: <recipients>"`.

### Done when

- Every routed open ask in the `asks` output is in exactly one section, or is
  named in the reply as held back by the architect.
- No ID in the pack belongs to a row that is no longer Open or Partly
  resolved.
- Every section reads on its own, and the method's vocabulary appears only on
  `Ref:` lines.
- No deadline appears that the architect did not give, and no ask is recorded
  as sent that the architect did not confirm.
