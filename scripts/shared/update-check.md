### Update check: one line at session open

This tells the architect that a newer ReStack exists. It prints at most one
line, at most once a day, and it never asks a question or upgrades anything. A
skill set that changes under an in-flight journey breaks the journey's audit
trail, so upgrading is the architect's call, made between sessions.

**When to run it.** Only as the first step of `/restack-journey start`,
`/restack-journey where` or `/restack-discover paths`, before any question,
probe or brief. **Skip it** if a decision brief is open in this conversation
(issued and not yet answered), or if you are inside a stop gate. A notice there
competes with the decision. It will run at the next session open instead.

Run it with the Bash tool:

```bash
UC="$HOME/.claude/skills/restack-upgrade/scripts/update_check.py"
[ -f "$UC" ] || UC="skills/restack-upgrade/scripts/update_check.py"
for py in python3 python; do "$py" -c "" 2>/dev/null && { "$py" "$UC" 2>/dev/null; break; }; done
```

If only PowerShell is available:

```powershell
$uc = "$HOME/.claude/skills/restack-upgrade/scripts/update_check.py"
if ((Test-Path $uc) -and (Get-Command python -ErrorAction SilentlyContinue)) { python $uc }
```

**If it prints a line**, show that line verbatim, once, at the top of your
reply, then go straight on with the command. Do not ask about it, explain it,
or run `/restack-upgrade`. It is not the session's next move either: never
recommend `/restack-upgrade` as the command to run next.

**If it prints nothing**, say nothing, and never mention that a check ran.
Silence covers every case where there is nothing to report: up to date, already
checked today, snoozed, opted out, offline, no git checkout, or no Python.

**If the architect asks to snooze it or turn it off**, run the snippet again
with ` snooze` or ` off` appended after `"$UC"`. Show its one-line reply, then
resume the command where you left it. The same commands exist as
`/restack-upgrade snooze` and `/restack-upgrade off`.

The opt-out is `{"update_check": false}` in `~/.restack/config.json`, or
`RESTACK_UPDATE_CHECK=off` in the environment. The script reads it before
anything touches the network.
