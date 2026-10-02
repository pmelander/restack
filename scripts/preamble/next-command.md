## Next command

When the work points at a next ReStack command, name it after the status line
and before the reflection prompt:

````
Next: <one line: why this move, now>

```text
/restack-design-review consistency
```

Alternative: `/restack-stressor walk checkout` — <one line: why not now>
````

- **The block holds exactly the command, on one line, arguments included,** so
  copying it copies the command and nothing else. Tag it `text`, never `bash`,
  `sh`, `shell` or `powershell`: hosts put a Run button on a shell block, and a
  slash command is not a shell command.
- **One block.** Add the `Alternative:` line only when you actually weighed one.
- **No `Next:` while a decision brief is unanswered,** and never an answer to a
  brief in the block. The block holds a command for after the gate, not a
  reply to it.
- **Never invent a next move.** A utility that answered the question has none.
  BLOCKED on a person or an approval says what is needed instead.

The architect copies, pastes and sends it. Nothing in the block runs or is sent
on their behalf.
