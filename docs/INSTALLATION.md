# Installation Guide

This guide will help you install the ReStack skills for Claude Code.

## Prerequisites

- Claude Code installed and configured
- Git (optional, for cloning the repository)
- Text editor (for viewing/editing skills)

## Installation Methods

### Method 1: Direct Installation (Recommended)

This method copies the skills directly to your Claude Code skills directory.

```bash
# Clone the repository
git clone git@github.com:pmelander/restack.git restack
cd restack

# Copy all skills to Claude Code (Claude Code expects skills/<name>/SKILL.md)
cp -R skills/* ~/.claude/skills/

# Verify installation
ls ~/.claude/skills/
```

**Result:** You should see skill folders like:
- `adr/`
- `solution-doc/`
- `tech-stack/`
- `design-review/`
(each containing a `SKILL.md`)

### Method 2: Symlink Installation (For Developers)

This method creates symbolic links, so updates to the repository automatically reflect in Claude Code.

```bash
# Clone the repository
git clone git@github.com:pmelander/restack.git restack
cd restack

# Create symlinks for skills
ln -s "$(pwd)/skills/adr" ~/.claude/skills/adr
ln -s "$(pwd)/skills/solution-doc" ~/.claude/skills/solution-doc
ln -s "$(pwd)/skills/tech-stack" ~/.claude/skills/tech-stack
ln -s "$(pwd)/skills/design-review" ~/.claude/skills/design-review
ln -s "$(pwd)/skills/stressor" ~/.claude/skills/stressor
ln -s "$(pwd)/skills/excel" ~/.claude/skills/excel
ln -s "$(pwd)/skills/arch-learning" ~/.claude/skills/arch-learning
ln -s "$(pwd)/skills/capability-assessor" ~/.claude/skills/capability-assessor
ln -s "$(pwd)/skills/patterns" ~/.claude/skills/patterns
ln -s "$(pwd)/skills/evolve" ~/.claude/skills/evolve
ln -s "$(pwd)/skills/cloud" ~/.claude/skills/cloud
ln -s "$(pwd)/skills/capacity" ~/.claude/skills/capacity
ln -s "$(pwd)/skills/discover" ~/.claude/skills/discover
ln -s "$(pwd)/skills/journey" ~/.claude/skills/journey

# Verify installation
ls -la ~/.claude/skills/
```

**Advantage:** Edit skills in the repository and changes are immediately available in Claude Code.

### Method 3: Windows Installation

For Windows users without symlink support:

```powershell
# Clone the repository
git clone git@github.com:pmelander/restack.git restack
cd restack

# Copy all skills to Claude Code (Claude Code expects skills\<name>\SKILL.md)
Copy-Item -Recurse -Path "skills\*" -Destination "$env:USERPROFILE\.claude\skills\"

# Verify installation
dir "$env:USERPROFILE\.claude\skills\"
```

## Verification

1. **Open Claude Code**
2. **Type `/` in the chat**
3. **Look for these skills:**
   - `/adr` - Architecture Decision Records
   - `/solution-doc` - Solution Documentation Generator
   - `/tech-stack` - Technology Stack Advisor
   - `/design-review` - Design Review

If you see these skills, installation was successful!

## Testing Your Installation

Try creating your first ADR:

```
/adr create Use PostgreSQL for primary database
```

Claude should start asking you questions to fill in the ADR template.

## Directory Structure After Installation

```
~/.claude/
  skills/
    adr/
      SKILL.md              # ✅ Installed
    solution-doc/
      SKILL.md              # ✅ Installed
    tech-stack/
      SKILL.md              # ✅ Installed
    design-review/
      SKILL.md              # ✅ Installed
    [other existing skills]
```

## Updating Skills

### For Direct Installation

```bash
cd restack
git pull origin main
cp -R skills/* ~/.claude/skills/
```

### For Symlink Installation

```bash
cd restack
git pull origin main
# Changes are automatically available!
```

## Uninstallation

To remove the skills:

```bash
# Remove skills
rm -rf ~/.claude/skills/adr
rm -rf ~/.claude/skills/solution-doc
rm -rf ~/.claude/skills/tech-stack
rm -rf ~/.claude/skills/design-review
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
   head -5 ~/.claude/skills/adr/SKILL.md
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
cp -R skills/* ~/my-skills/
```

### Selective Installation

Install only the skills you need:

```bash
# Install only ADR skill
cp -R skills/adr ~/.claude/skills/

# Install only documentation skills
cp -R skills/solution-doc ~/.claude/skills/
```

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
