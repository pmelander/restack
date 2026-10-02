# ADR-017: Render the Next Step as a Button That Carries the Command, Never Its Arguments

**Status:** Rejected — built, shipped in 2.5.0, withdrawn in 2.5.2 the same day

**Date:** 2026-10-02

**Deciders:** ReStack maintainers

**Technical Story:** [ROADMAP](../../ROADMAP.md) item 7, "Next step as a button"

**Implementation Status:** withdrawn

**Implemented Date:** 2026-10-02 (withdrawn 2026-10-02)

**Implemented By:** ReStack maintainers

**Review Date:** none — the decision is closed, not pending

## Context

> **This decision was implemented, shipped in 2.5.0, and withdrawn in 2.5.2.**
> In use, a button often needed several clicks before its command appeared in
> the message box. See [Withdrawal](#withdrawal) for what was and was not
> established. The code is not in the tree. It is reachable from merge commit
> `f1aa577` on `main`, at head `aca5ad4`. Everything up to *Withdrawal* is left
> as written when the decision was accepted, because the reasoning is the part
> worth keeping.
>
> **Amended 2026-10-02 (2.6.0):** the `Next:` line came back without the
> button, with the command in a block the architect copies. See
> [ADR-018](ADR-018-next-command-as-a-copy-block.md).

Most commands end by naming the next move as a command, but in no fixed form.
`/restack-journey start` names "the first move as a single command";
`/restack-journey where` recommends "the next move, with the alternative you
rejected"; `/restack-discover confidence` routes to a specific discover
command. The architect then copies or retypes it, and a subcommand typo costs
a round trip.

The Claude desktop app and claude.ai offer a widget tool, `show_widget`, whose
HTML has a global `sendPrompt(text)` that hands text to the chat as if the
architect had typed it. That puts the next move one click away. It also lets a
skill put words in the architect's mouth, and in this toolkit that can go wrong
in three ways:

1. **Gates.** A decision brief is answered through `AskUserQuestion` so the
   decisions log records the architect's answer. A button that sends "proceed"
   passes the gate with no brief and no recorded answer. That breaks rule 2 of
   the stop gates and the decision-brief rule that no decision is logged
   without a recorded answer.
2. **Injection.** A command's arguments (path names, actor names, ADR numbers,
   technologies) come from the architect's documents and from tool output. Put
   into `sendPrompt`, text from those sources becomes a message in the
   architect's voice.
3. **Staleness.** A button stays in the transcript. Clicked a day later, it
   resends a recommendation made against state that has since changed. A typed
   command is fresh by definition. A clicked one is not.

The tool is not available everywhere: terminal Claude Code has none. Its name
also varies. It is `mcp__visualize__show_widget` in one session and
`mcp__<server-id>__show_widget` in another, sometimes deferred and loadable only
through `ToolSearch`. The session that built this had both: one loaded and one
deferred.

### What a click test in the desktop app's Code tab found

The first version sent the bare command, `/restack-adr list`. Clicked, it did
nothing. A diagnostic widget then separated the possible causes:

| Button | Wiring | Text sent | Result |
|---|---|---|---|
| A | inline `onclick` | plain text | text landed in the input box |
| B | script listener | plain text | text landed in the input box |
| C | script listener | `/restack-adr list` | nothing arrived |
| D | script listener | `Run /restack-adr list` | text landed in the input box |

Two facts follow, and the tool's own description mentions neither:

- **In the Code tab, `sendPrompt` fills the input box and does not send.** The
  architect presses send. The tool is documented to send directly, and claude.ai
  may do so; that has not been verified.
- **Text that starts with `/` does not arrive at all.** That is plausibly
  deliberate: a widget that could type harness slash commands would be a
  control-bypass risk. A request phrased for Claude, which is what `sendPrompt`
  is documented for, does arrive.

The fixed button was then tested end to end. Clicked and sent unedited,
`Run /restack-adr list` loaded `/restack-adr` and ran `list`.

## Decision

1. **A tier-1 preamble fragment, `next-step.md`,** is composed into all sixteen
   skills after the completion status. It gives the next move one shape on
   every host: a `Next:` line with the full command, arguments included, and
   why. An `Alternative:` line follows only when the skill actually weighed
   one. There is no `Next:` line while a brief is unanswered, and none where a
   utility has no next move.
2. **Buttons appear where the host can render them, below the lines.** The tool
   is found by capability: a name ending in `show_widget`, loaded or deferred,
   with the `read_me` from the same prefix called once per session as silent
   setup. A `read_me` that describes no `sendPrompt` means no button.
3. **Degrade silently.** With no tool, the lines print and nothing else. The
   skill never mentions that a button could have been there, and never retries
   or explains a failed widget call.
4. **One to three buttons.** The recommended move comes first, with the accent
   border, then the weighed alternative. A third button is allowed only for a
   second alternative written as a line. A button is never a menu.
5. **Never a gate.** No button is rendered while a brief is unanswered,
   including the prose fallback brief. A button never sends `proceed`, `yes`,
   an option letter or an option label. A button may launch a command that
   contains a gate, and that gate still runs as a brief.
6. **The reflection prompt keeps the last word.** It goes below the buttons,
   because a button makes moving on cheaper than reflecting.
7. **A button carries the command, never its arguments.** It sends `Run `
   followed by `/restack-<skill>` and at most its subcommand. It never sends a
   bare `/...`, which hosts drop. Its label is the command alone, plus ` ↗`.
   The pattern `^Run /restack-[a-z]+(-[a-z]+)*( [a-z]+(-[a-z]+)*)?$` accepts
   every command form in the sixteen skills (88 at the time of writing). It
   rejects arguments, gate answers, quote break-outs, free text around the
   command and a bare slash command. The `Next:` line keeps the arguments. A command that arrives without its argument resolves it from the
   state on disk *at that moment* and names it in its first line. If that
   differs from an earlier `Next:` line, it says the line is stale. If the
   state does not settle it to one candidate, it asks.

### Why no arguments

ROADMAP item 7 left this open. An argument is more useful, and it is also
where a stale suggestion does the most damage. Three reasons decide it:

- **Staleness is removed by construction, not checked for.** The argument is
  resolved when the button is clicked, from the state as it is then, not when
  the button was drawn. Suppose the architect clicks a day later, after the path
  map changed. The skill walks the path that is next now, or reports that the
  earlier recommendation is stale.
- **The injection surface becomes a closed set.** Arguments are the only part
  of a command that comes from content. Without them, everything a button can
  send is one of a fixed list of strings that a regular expression can check,
  with no quote character to break out with. "Arguments, but sanitised" depends
  on a model sanitising correctly at render time, every time. Real names also
  defeat a safe character set: "Order Service" has a space and capitals.
- **The choice stays visible.** `sendPrompt` speaks as the architect. Sent by
  a button, `Run /restack-stressor walk checkout` reads as the architect
  choosing `checkout`, both in the transcript and to the skill that receives it.
  The architect chose to move on. The skill chose the path. Without the
  argument, the receiving command names its target in its first line, where the
  architect sees it and can redirect it. In a host that fills the input box,
  the architect can also type the argument before sending, which leaves the
  choice with its owner.

The cost is one line of confirmation on a click, plus a question when the state
holds more than one candidate. Specificity is not lost. The `Next:` line still
names the full command, which `/restack-discover confidence` requires when it
routes to "a **specific** command".

## Consequences

### Positive

- The next move is a click away, with no subcommand typos, on hosts that
  support it. Every other host prints identical text.
- In the Code tab the architect still presses send, so a widget cannot submit
  anything on its own. That is a stronger guarantee for gates than this
  design assumed.
- Next moves have one shape across all sixteen skills, which helps in a
  terminal as much as in the desktop app.
- Gate integrity holds. No button exists while a brief is open, and no button
  can send an answer.
- A bare command is now well defined in every skill, whether a button sent it
  or the architect typed it.

### Negative

- Every skill carries eighty more preamble lines. That includes the tier-1
  utilities, which rarely have a next move.
- Detection is an instruction to the model, not code. If a host renames the
  tool, the suffix match misses it and the skill falls back to text. That is
  the safe direction, but it is silent.
- A button makes moving on cheaper than reflecting. Keeping the reflection
  prompt below the buttons gives it the last word, but nothing makes the
  architect answer it.
- In the Code tab it is two clicks, not one: the button, then send. The
  roadmap's "one click" holds only where a host sends directly.
- The payload's shape rests on observed host behaviour that is not documented:
  that a leading `/` is dropped and `Run /...` is not. A host change could
  break buttons silently. The `Next:` line still carries the command, so the
  loss is convenience, not information.
- Nothing automated covers rendering or clicking. The rules are verified by
  reading. The pattern was verified by a script against every command heading,
  the fragment's own snippet and a set of hostile strings. The click was
  verified by hand in the desktop app's Code tab, as the table above records.

### Neutral

- A future subcommand outside lowercase kebab-case could never become a
  button. All of today's subcommands fit.
- The HTML snippet in the fragment defers to the host's `read_me` wherever the
  two differ. The host owns the theming contract (CSS variables, transparent
  background, light and dark), and the snippet uses only its tokens.

## Alternatives considered

### Carry arguments, restricted to a safe character set
- **Pros:** One click to a fully specified command.
- **Cons:** A stale click still sends the wrong target in the architect's
  voice. Real names have spaces and capitals, so the safe set either rejects
  them or widens until it is no longer safe.
- **Why rejected:** It addresses injection only. Staleness and attribution
  remain.

### Carry arguments, and have each receiving command verify them
- **Pros:** Keeps the one click to a full command.
- **Cons:** All sixteen skills would need a freshness check. And a stale
  argument that still exists, such as a path already walked, passes the check
  even though nobody would choose it now.
- **Why rejected:** Verification answers "does this exist?", not "is this still
  the next move?"

### Render the decision brief's options as buttons
- **Pros:** Faster to answer than the `AskUserQuestion` dialog.
- **Cons:** The skill would compose the answer and submit it in the
  architect's voice, outside the tool that records it. Old briefs' buttons stay
  clickable.
- **Why rejected:** A gate exists so that the architect answers it. A button
  that answers on their behalf is the failure the stop gates name.

### A button for every command of the skill
- **Why rejected:** A menu is a table of contents, not a recommendation, and it
  hands the sequencing judgement back without the reasoning.

### Leave it as text
- **Pros:** No preamble cost, and nothing new to trust.
- **Cons:** Copying, retyping and typos. The next move also keeps three
  different shapes across the skills.
- **Why rejected:** The cost is modest. The standard `Next:` line is worth
  having on its own, on every host.

## Withdrawal

Withdrawn on the day it shipped, by the architect using it, after clicking
the button in the desktop app's Code tab.

**Established.**

- In the Code tab, `sendPrompt` fills the message box and does not send. A
  button is a click and then a send, not one click.
- Text that starts with `/` does not arrive. `Run /restack-...` does, and sent
  unedited it loads and runs the skill.
- Clicks were unreliable. A button often needed several clicks before its
  command appeared in the message box.

**Not established.** Why the clicks were unreliable. The press might not reach
the widget, `sendPrompt` might throw, or the host might drop a call it received.
A diagnostic widget that counts each of these was drawn, but the decision to
withdraw came before it ran. How claude.ai behaves is also unknown.

**Why withdraw rather than fix.** A button is only worth having if it is
quicker and surer than typing. One that sometimes takes three clicks and a send
is neither, and the line above it already carried the full command. Every
remaining unknown is in the host, where ReStack can neither test nor fix it. An
instruction in every skill's preamble that depends on undocumented host
behaviour fails silently the day that behaviour changes.

**The `Next:` line went with it.** It was introduced to give the button
something to mirror. On its own it was a modest gain in consistency, paid for
in every skill's preamble. Skills name their next move as they did in 2.4.0.

**What survives.**

- **The gate rule.** Nothing that speaks in the architect's voice may answer a
  decision brief. That holds for any future shortcut, not only widgets.
- **The argument rule.** If this is picked up again: carry the command, and
  resolve the argument when it runs, from the state on disk. Staleness,
  injection and attribution argue the same way on any host.
- **The host findings above,** so the next attempt starts from them rather than
  rediscovering them.

**If it is picked up again**, it needs two things: a host that documents what
`sendPrompt` does, and a click test stated before the work. The same button,
clicked N times from a freshly rendered widget, must fill the message box N
times.

## References

- [ADR-008](ADR-008-generated-skills-with-tiered-preamble.md): the tiered
  preamble this fragment is composed into
- [ADR-015](ADR-015-vendored-sections-and-base-relative-paths.md): the previous
  tier-1 fragment, and the same "stated once, composed everywhere" pattern
- `scripts/preamble/next-step.md` at `aca5ad4`: the rule as the skills read
  it, removed in 2.5.2
- `scripts/preamble/decision-brief.md`, `scripts/preamble/stop-gates.md`: why a
  button never answers a gate
