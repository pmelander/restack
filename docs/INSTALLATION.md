# Installation Guide

This guide will help you install the ReStack skills for Claude Code.
[INSTALL.md](../INSTALL.md) has the short version and the steps an agent
follows when installing on someone's behalf.

## Prerequisites

- Claude Code installed and configured
- Git, to clone the repository and for `/restack-upgrade`
- Python, for the update check and the optional extras

### Optional extras

Neither is required; `setup` reports whether each is present.

| | Install | Affects |
|---|---|---|
| **openpyxl** | `pip install -r requirements.txt` | `/restack-excel` reading `.xlsx`. CSV works without it. |
| **Codex CLI** | `npm i -g @openai/codex` then `codex login` | The outside opinion in `/restack-stressor` and `/restack-design-review`. Without it they fall back to a fresh subagent — same model family, so it shares blind spots; its disagreement still counts, its agreement is weak evidence. |

## Installing

The install is always a **copy in your user profile**, `~/.claude/skills/restack-*`.
It does not depend on the clone it came from, so the clone can be deleted
afterwards ([ADR-019](adr/ADR-019-copy-only-install.md)).

```bash
git clone --depth 1 https://github.com/pmelander/restack.git restack-install
cd restack-install && ./setup
cd .. && rm -rf restack-install          # optional
```

Windows, without a POSIX shell:

```powershell
git clone --depth 1 https://github.com/pmelander/restack.git restack-install
cd restack-install; .\setup.ps1
cd ..; Remove-Item -Recurse -Force restack-install      # optional
```

`setup` prints what it installed, updated, removed and left unchanged, and ends
with a summary line. Re-running it is safe — that is also how you repair a
partial install. `setup` and `setup.ps1` behave identically; Git Bash users can
run either.

| Option | Effect |
|---|---|
| `--dry-run` / `-DryRun` | show what would change; write nothing |
| `--quiet` / `-Quiet` | summary only |

`--symlink` and `--target` were removed in 2.7.0 and are refused with a
message. `CLAUDE_SKILLS_DIR` is ignored, with a note.

**Result:** seventeen directories in `~/.claude/skills/`, each named `restack-*`
and each containing a `SKILL.md`. Verify with:

```bash
ls -d ~/.claude/skills/restack-* | wc -l    # expect 16
```

### What setup does that a plain copy does not

- Removes ReStack skills that no longer exist upstream. A plain copy leaves a
  renamed or deleted skill installed forever.
- Reports what changed instead of overwriting silently.
- Refuses to install a skill directory with no `SKILL.md` — Claude Code would
  ignore it and the command would simply never appear.
- Verifies that every section a skill names was installed.
- Records the install in `~/.restack/install.json`, including the repository
  it came from, which is where `/restack-upgrade` fetches releases.
- Only ever touches entries named `restack-*`, so it cannot damage another
  skill suite.
- Replaces a link left by a symlinked install from before 2.7.0 with a copy,
  removing the link as a link. The directory it pointed at is not touched.

### Why every skill is prefixed

Claude Code resolves a skill by its folder name, so `~/.claude/skills/design-review/`
is the command `/design-review` — and only one folder can own that name. Several
popular skill suites ship a `design-review`, a `review`, or a `patterns`, so an
unprefixed install silently overwrites whichever was there first, and you lose a
skill without being told.

The `restack-` prefix makes ReStack coexist with anything else you have
installed. The folder name and the command are always the same string, so there
is no install-time renaming to remember. See
[ADR-009](adr/ADR-009-prefix-skill-names.md).

**Upgrading from an unprefixed install?** Versions before the rename installed
as `~/.claude/skills/adr/`, `~/.claude/skills/stressor/` and so on. `setup`
cannot remove those — it only touches `restack-*`, deliberately, since an
unprefixed `design-review` may belong to a suite you still want. Inspect them
before deleting anything:

```bash
for s in adr arch-learning capability-assessor capacity cloud design-review discover evolve excel journey patterns solution-doc stressor tech-stack; do
  [ -d ~/.claude/skills/$s ] && { head -3 ~/.claude/skills/$s/SKILL.md; echo "  ^ ~/.claude/skills/$s"; }
done
```

## Developing ReStack

Keep a clone, edit the templates and sections, regenerate, and install:

```bash
python scripts/gen_skills.py && ./setup
```

There is no symlinked development mode any more. Your sessions load what you
last installed, never what another session is half-way through editing.
`/restack-upgrade` never touches your clone. If what you installed is ahead of
the latest release, it asks before replacing it.

## Verification

1. **Open Claude Code**
2. **Type `/` in the chat**
3. **Look for the `/restack-*` skills**, for example `/restack-journey`,
   `/restack-stressor`, `/restack-adr` and `/restack-design-review`.

Try creating your first ADR:

```
/restack-adr create Use PostgreSQL for primary database
```

Claude should start asking you questions to fill in the ADR template.

## Directory structure after installation

```
~/.claude/skills/
  restack-journey/      SKILL.md + sections/
  restack-discover/     SKILL.md + sections/
  restack-stressor/     SKILL.md + sections/ + compliance-packs/
  restack-adr/          ...
  ... 17 in total, all prefixed restack-
  restack-excel/        SKILL.md + read_spreadsheet.py
  restack-trace/        SKILL.md + scripts/trace.py
  restack-upgrade/      SKILL.md + scripts/update_check.py
  [your other skills, untouched]

~/.restack/
  install.json          version, source, directory installed from, method, date (written by setup)
  config.json           your settings: {"update_check": false} opts out (optional)
  update-check.json     last update check and any snooze (written by the check)
  upstream.git/         a bare cache of main, for the update check
```

## Updating

```
/restack-upgrade
```

It clones the latest release from the repository you installed from into a
temporary directory, runs that release's `setup`, verifies the install,
summarises the changelog, and deletes the temporary directory. It needs no
clone of yours and never touches one.

By hand, the same thing:

```bash
git clone --depth 1 https://github.com/pmelander/restack.git restack-install
cd restack-install && ./setup && cd .. && rm -rf restack-install
```

You do not have to remember to check. Once a day, `/restack-journey start` or
`where` and `/restack-discover paths` print one line when a newer version
exists. `/restack-upgrade snooze` hides it for a week, and `/restack-upgrade off`
turns the check off. See [INSTALL.md](../INSTALL.md#update-check-and-opt-out).

`/restack-upgrade` is also the repair path — re-running `setup` fixes almost
every partial-install symptom.

## Uninstallation

```bash
rm -rf ~/.claude/skills/restack-*
rm -rf ~/.restack
```

No trailing slash. On a symlinked install from before 2.7.0, `rm -rf link/`
would delete the contents of the checkout the link points at.

On Windows PowerShell:

```powershell
Get-ChildItem "$env:USERPROFILE\.claude\skills" -Filter 'restack-*' -Force | ForEach-Object {
  if ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) { [IO.Directory]::Delete($_.FullName, $false) }
  else { Remove-Item -LiteralPath $_.FullName -Recurse -Force }
}
Remove-Item -Recurse -Force "$env:USERPROFILE\.restack"
```

## Troubleshooting

### Skills Don't Appear in Claude Code

1. **Check they are installed:**
   ```bash
   ls -d ~/.claude/skills/restack-*
   ```
   If nothing is listed, install again (see *Installing*).

2. **Check the skill file has proper frontmatter:**
   ```bash
   head -5 ~/.claude/skills/restack-adr/SKILL.md
   ```
   It should show YAML frontmatter between `---` delimiters.

3. **Restart Claude Code.** A fresh session is the sure way to pick up new
   skills.

### All `/restack-*` commands vanished after deleting a checkout

That was a symlinked install from before 2.7.0: the links pointed into the
checkout. Install again; from 2.7.0 the install is a copy and cannot break
this way.

### The update notice never appears

Run `/restack-upgrade check`. It shows whether the check is off, which source
it fetches from, and the result of the last attempt.

## Selective installation

`setup` installs all seventeen. If you want a subset, copy the directories you
want — the skills work independently, though `/restack-journey` will reference
commands that are not installed:

```bash
cp -R skills/restack-journey skills/restack-stressor ~/.claude/skills/
```

`/restack-upgrade` and `setup` manage the full set, so running either installs
the rest again.

## Next Steps

1. **Read the documentation:** Check `docs/` for usage guides
2. **View examples:** See `examples/` for sample outputs
3. **Contribute:** Submit PRs for improvements or new skills!

## Support

For issues or questions:
- Check the [README.md](../README.md)
- Review [CLAUDE.md](../CLAUDE.md) for development details
- Open an issue on GitHub

See [ROADMAP.md](../ROADMAP.md) for future considerations and contributing opportunities.
