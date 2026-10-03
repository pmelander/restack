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
PY=""; for p in python3 python; do "$p" -c "" 2>/dev/null && { PY="$p"; break; }; done
if [ -f "$JY" ] && [ -n "$PY" ]; then "$PY" "$JY" check; else echo "journey helper unavailable: write the journey files by hand in their canonical shape"; fi
```

For another command, replace `check` in the last line:

| When | Command |
|---|---|
| **before** issuing a decision brief | `decision open "<question>" --gate <terrain\|confidence\|iterate\|approach\|brief>` prints the brief's number, `D<n>` |
| the architect has answered | `decision answer D<n> --answer "..." --rationale "..." --actors no` (or `--actors "yes: added <actor>"`; `--supersedes D<m>` when it reverses one) |
| a belief the design relies on is unverified | `assume add "<belief>" --source "..." --validates "..." --depends "..."` prints `A-<n>` |
| something settles or changes an assumption | `assume status A-<n> "<status>" --why "..."` |
| a `/restack-journey` command finishes | `history add --command "/restack-journey <cmd>" --outcome "..." [--decision D<n>]` |

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
