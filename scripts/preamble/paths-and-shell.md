## Paths and shell

**`<base>` is this skill's own directory.** Claude Code prints it when the skill
loads ("Base directory for this skill: ..."). Every section and helper this
skill names is written against it, as `<base>/sections/<file>.md`. If no base
directory was printed, use `~/.claude/skills/<skill-name>`. Never resolve a
skill path against the working directory: that is the architect's project, and
a Glob there for `skills/...` returns nothing, or a different checkout's copy.
Paths under `docs/` are the opposite case: they are the architect's project,
relative to the working directory.

**Scripted file edits.** Prefer the Edit tool for a change to one file. When a
script really is the right tool, and especially on Windows (Git Bash or
PowerShell 5.1):

- Write a multi-line script to a scratch file and run the file. Do not embed it
  in a shell heredoc: Git Bash fails on Python triple-quoted strings inside one
  with "unexpected EOF".
- Set `PYTHONIOENCODING=utf-8` before running Python that prints non-ASCII
  (Σ, →, å/ä/ö). The Windows console defaults to cp1252 and the print raises.
- Read and write with an explicit `encoding="utf-8"`, and write `newline="\n"`.
