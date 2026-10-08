## Journey Files (write them with the helper)

The decisions log, the assumptions register and the journey history have one
canonical shape each. `journey.py`, shipped in `/restack-journey`, writes them
in that shape: it takes the next `D<n>` and `A-<n>`, puts the row or entry in
the right place, keeps a register row and its status lines in step, and
refuses a file that is not canonical rather than guessing (ADR-023 in the
ReStack repository). Use it for every write to these three files.

Run it with the Bash tool, from the project root:

```bash
JY="$HOME/.claude/skills/restack-journey/scripts/journey.py"
[ -f "$JY" ] || JY="skills/restack-journey/scripts/journey.py"
command -v cygpath >/dev/null 2>&1 && JY="$(cygpath -m "$JY")"
PY=""; for p in python3 python; do "$p" -c "" 2>/dev/null && { PY="$p"; break; }; done
if [ -f "$JY" ] && [ -n "$PY" ]; then MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' "$PY" "$JY" check; else echo "journey helper unavailable: write the journey files by hand in their canonical shape"; fi
```

For another command, replace `check` in the last line. Keep the `cygpath`
line and the two `MSYS` variables: without them Git Bash on Windows rewrites an
argument that starts with `/` (`--command "/restack-journey ..."`) into a
Windows path, and with the variables but without `cygpath` the script's own
path is no longer translated for a Windows Python.

| When | Command |
|---|---|
| **before** issuing a decision brief | `decision open "<question>" --gate <terrain\|confidence\|iterate\|approach\|brief>` prints the brief's number, `D<n>` |
| the architect has answered | `decision answer D<n> --answer "..." --rationale "..." --actors no --assumptions none` (or `--actors "yes: added <actor>"`; `--assumptions "settles A-3, A-7; changes A-9; raises A-12"`; `--supersedes D<m>` when it reverses one) |
| a belief the design relies on is unverified | `assume add "<belief>" --source "..." --validates "..." --depends "..."` prints `A-<n>` |
| only someone outside the design can settle it (a handoff ask) | the same, plus `--ask "<recipient>"`: the team or role that would answer |
| it is an open design question, a check the build must run, or something only the running system can show | the same, plus `--kind decide`, `--kind test` or `--kind observe` |
| a row's kind is wrong or missing | `assume kind A-<n> <decide\|test\|observe\|belief>`, after the architect confirms it |
| the work just touched an ADR, decision, residual, actor or iteration | `assume touching <ID or phrase> ...`: the not-closed rows that name it (read-only) |
| you need one row's whole record | `assume show A-<n>`: the row (its current state) and its own status lines |
| you need the register's load | `register`: exposure apart from carried, by kind and age, and four worklists (read-only) |
| an existing row turns out to be an ask, or a recipient is renamed | `assume route A-<n> "<recipient>"`, after the architect confirms who |
| the architect says an ask has gone out | `assume asked A-<n> [A-<m> ...] --to "<recipient>"`: keeps each status, records the send |
| a send was recorded that did not happen | `assume unasked A-<n> [A-<m> ...] --why "..."`: keeps each status, cancels the row's last send |
| something settles or changes an assumption | `assume status A-<n> "<status>" --why "..."` |
| a row disagrees with a status line already recorded | `assume sync A-<n>` (or `--all`): the row takes the line's status and date, no new line |
| an answered decision never said whether it changed the actor set | `decision note D<n> --actors no` (or `"yes: added <actor>"`), marked as recorded later |
| a ReStack command finishes (not a `/restack-journey where` that found the position current and wrote nothing) | `history add --command "/restack-<skill> <cmd>" --outcome "..." [--decision D<n>]` |

**Close what the work settles.** Registering a row is half the job. Before a
command finishes after a decision is answered, an ADR is written or amended, an
iteration is gated, an ablation is answered or a review finding is confirmed,
run `assume touching` on what that work was about: the ADRs, decisions,
residuals and actors it names, and `iteration <n>` at an iterate gate. Put the
rows it lists to the architect, one choice question each, statuses drawn from
the evidence and **Still open** last, and write each answer with
`assume status`. The list is a worklist: a row that only mentions the thing
in passing stays as it is. A decision's `--assumptions` is the answer to the
same question, and it is required: `none` is a fine answer, a missing one is
not. It records the claim and changes no status.

**The position goes stale, and says so.** Current Position, the phase line and
`Last Updated` are `/restack-journey where`'s assessment, and only `where` (or
`start`) rewrites them. Never bring them up to date from another command: the
file would look current while the assessment is not (ADR-032 in the ReStack
repository). Once the recorded next move has run, or a decision has been
answered after the position was written, `history add` ends with
`note: Current Position of <date>: ... Stale: ...`. Carry it into the
handoff: the `Next:` line is `/restack-journey where` unless this work has a
step of its own that must come first, and then add
`Alternative: /restack-journey where — the position is stale` under it. This
holds when the work ends on a wait too: `where` is what records the wait, so
the file and the reply say the same thing.

**The row is the current state.** Its status lines are its history. Read the
row; read the lines when you need to know how it got there.

**A `--why` comes from the record.** Quote or point at what settled it: the
discovery note, the code read, the architect's answer, the line that already
says so. If the record holds no reason, ask; never write a plausible one.

**An ask is recorded as sent only when the architect says it went**, in a
question that asks exactly that. Writing an asks pack is not sending it, and
neither is the architect reading it or saying which sections are going out.
`journey.py asks` lists what is open, by recipient, with when each was last
asked.

**Number a brief before you ask it.** `decision open` writes the entry with
`Answer: (open)`. If the session is interrupted, the open entry is the record:
on resumption, re-issue that brief under the same number, unchanged. Never
infer an answer from an open entry, and never reuse its number.

**If the helper refuses**, it says why. "Not canonical" means the file is in
an older shape. Do not restructure it by hand. Append in the file's own shape
for now, and offer the migration: run `migrate` (a dry run, writing nothing),
show the architect what it would do and what it leaves for their judgement, and
write with `migrate --write` only after they agree. Restructuring someone's
journey files is their call.

**If the helper is unavailable**, the snippet says so: write the files by hand,
in the canonical shapes the templates define.
