# Installation Guide

This guide will help you install the ReStack skills for Claude Code.

## Prerequisites

- Claude Code installed and configured
- Git (optional, for cloning the repository)
- Text editor (for viewing/editing skills)

## Installation Methods

### Method 1: setup script (recommended)

```bash
git clone https://github.com/pmelander/restack.git ~/restack
cd ~/restack && ./setup
```

Windows, without a POSIX shell:

```powershell
git clone https://github.com/pmelander/restack.git $HOME
estack
cd $HOME
estack
.\setup.ps1
```

`setup` prints what it installed, updated, removed and left unchanged, and ends
with a summary line. Re-running it is safe — that is also how you repair a
partial install.

Useful flags:

| Flag | Effect |
|---|---|
| `--dry-run` | show what would change; write nothing |
| `--symlink` | symlink instead of copy, so repository edits are live |
| `--target DIR` | install somewhere other than `~/.claude/skills` |
| `--quiet` | summary only |

`CLAUDE_SKILLS_DIR` overrides the target for all of them.

**Result:** fifteen directories in `~/.claude/skills/`, each named `restack-*`
and each containing a `SKILL.md`. Verify with:

```bash
ls -d ~/.claude/skills/restack-*/ | wc -l    # expect 15
```

### What setup does that a plain copy does not

- Removes ReStack skills that no longer exist upstream. A plain copy leaves a
  renamed or deleted skill installed forever.
- Reports what changed instead of overwriting silently.
- Refuses to install a skill directory with no `SKILL.md` — Claude Code would
  ignore it and the command would simply never appear.
- Records the install in `~/.restack/install.json`, which is how
  `/restack-upgrade` finds your checkout later.
- Only ever touches directories named `restack-*`, so it cannot damage another
  skill suite.

### Why every skill is prefixed

Claude Code resolves a skill by its folder name, so `~/.claude/skills/design-review/`
is the command `/design-review` — and only one folder can own that name. Several
popular skill suites ship a `design-review`, a `review`, or a `patterns`, so an
unprefixed install silently overwrites whichever was there first, and you lose a
skill without being told.

The `restack-` prefix makes ReStack coexist with anything else you have
installed. The folder name and the command are always the same string, so there
is no install-time renaming to remember and the symlink method below works
unchanged. See [ADR-009](adr/ADR-009-prefix-skill-names.md).

**Upgrading from an unprefixed install?** Versions before the rename installed
as `~/.claude/skills/adr/`, `~/.claude/skills/stressor/` and so on. `setup`
cannot remove those — it only touches `restack-*`, deliberately, since an
unprefixed `design-review` may belong to a suite you still want. Inspect them
before deleting anything:

```bash
for s in adr arch-learning capability-assessor capacity cloud design-review          discover evolve excel journey patterns solution-doc stressor tech-stack; do
  [ -d ~/.claude/skills/$s ] && { head -3 ~/.claude/skills/$s/SKILL.md; echo "  ^ ~/.claude/skills/$s"; }
done
```

### Method 2: Symlink Installation (For Developers)

This method creates symbolic links, so updates to the repository automatically
reflect in Claude Code.

**It needs a shell that can actually create symlinks.** Git Bash on Windows
silently *copies* otherwise — `ln -s` returns 0 and you get a directory. setup
probes for this and installs by copy with a warning rather than claiming edits
are live. Enable Developer Mode (Settings › For developers), use an elevated
shell, or prefix the command with `MSYS=winsymlinks:nativestrict`.

```bash
# Clone the repository
git clone git@github.com:pmelander/restack.git restack
cd restack

# Symlink every skill — stays correct as skills are added or renamed
for d in skills/restack-*/; do
  ln -sfn "$(pwd)/${d%/}" ~/.claude/skills/"$(basename "$d")"
done

# Verify — expect 14
ls -d ~/.claude/skills/restack-*/ | wc -l
```

**Advantage:** Edit skills in the repository and changes are immediately available in Claude Code.

### Method 3: Windows

`setup.ps1` is the Windows-native equivalent and takes the same options.

```powershell
git clone https://github.com/pmelander/restack.git $HOME
estack
cd $HOME
estack
.\setup.ps1                 # -DryRun, -Symlink, -Target, -Quiet
```

`-Symlink` needs Developer Mode or an elevated shell; without either, use the
default copy. Git Bash users can run `./setup` instead — the two are
behaviourally identical.

## Verification

1. **Open Claude Code**
2. **Type `/` in the chat**
3. **Look for these skills:**
   - `/restack-adr` - Architecture Decision Records
   - `/restack-solution-doc` - Solution Documentation Generator
   - `/restack-tech-stack` - Technology Stack Advisor
   - `/restack-design-review` - Design Review

If you see these skills, installation was successful!

## Testing Your Installation

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
  ... 15 in total, all prefixed restack-
  restack-excel/        SKILL.md + read_spreadsheet.py
  restack-upgrade/      SKILL.md
  [your other skills, untouched]

~/.restack/
  install.json          version, repo path, method, date
```

## Updating

```
/restack-upgrade
```

It finds your checkout from `~/.restack/install.json`, compares installed,
local and remote versions, pulls, re-runs `setup`, and summarises the changelog
between the two. Uncommitted changes or unpushed commits stop it and require an
explicit answer — it will not discard work.

By hand:

```bash
cd ~/restack && git pull && ./setup
```

A symlink install still needs `./setup` after a pull, because a newly added
skill has no symlink yet. Edits to existing skills are live without it.

`/restack-upgrade` is also the repair path — re-running `setup` fixes almost
every partial-install symptom. Use `./setup --dry-run` first to see what it
would change.

## Uninstallation

To remove the skills:

```bash
# Remove skills
rm -rf ~/.claude/skills/restack-adr
rm -rf ~/.claude/skills/restack-solution-doc
rm -rf ~/.claude/skills/restack-tech-stack
rm -rf ~/.claude/skills/restack-design-review
```

Or on Windows:

```powershell
Remove-Item -Recurse "$env:USERPROFILE\.claude\skills\adr"
Remove-Item -Recurse "$env:USERPROFILE\.claude\skills\solution-doc"
Remove-Item -Recurse "$env:USERPROFILE\.claude\skills\tech-stack"
Remove-Item -Recurse "$env:USERPROFILE\.claude\skills\design-review"
```

## Troubleshooting

### Skills Don't Appear in Claude Code

1. **Check the skills directory exists:**
   ```bash
   ls ~/.claude/skills/
   ```
   If it doesn't exist, create it:
   ```bash
   mkdir -p ~/.claude/skills/
   ```

2. **Verify file permissions:**
   ```bash
   ls -la ~/.claude/skills/*.md
   ```
   Files should be readable (at least `r--` permissions).

3. **Restart Claude Code**
   Sometimes Claude Code needs a restart to pick up new skills.

### Skill Command Not Working

1. **Check the skill file has proper frontmatter:**
   ```bash
   head -5 ~/.claude/skills/restack-adr/SKILL.md
   ```
   Should show YAML frontmatter with `---` delimiters.

2. **Check for syntax errors:**
   Open the skill file and look for any formatting issues.

### Windows Symlink Issues

If symlinks don't work on Windows:
- Use Method 3 (direct copy) instead
- Or enable Developer Mode in Windows Settings to allow symlinks

## Advanced Configuration

### Custom Skill Directory

If you use a different skills directory, adjust the paths accordingly:

```bash
# If your skills are in ~/my-skills/
./setup --target ~/my-skills
```

### Selective installation

`setup` installs all fifteen. If you want a subset, copy the directories you
want — the skills work independently, though `/restack-journey` will reference
commands that are not installed:

```bash
cp -R skills/restack-journey skills/restack-stressor ~/.claude/skills/
```

Note that `/restack-upgrade` and `setup` still manage the full set: re-running
`setup` would install the rest. A subset is best kept with `--target` and a
skills directory of your own.

## Next Steps

1. **Read the documentation:** Check `docs/` for usage guides
2. **View examples:** See `examples/` for sample outputs
3. **Customize templates:** Edit `templates/` to match your standards
4. **Contribute:** Submit PRs for improvements or new skills!

## Support

For issues or questions:
- Check the [README.md](../README.md)
- Review [CLAUDE.md](../CLAUDE.md) for development details
- Open an issue on GitHub (if public repository)

## What's Next?

See [ROADMAP.md](../ROADMAP.md) for future considerations and contributing opportunities.
