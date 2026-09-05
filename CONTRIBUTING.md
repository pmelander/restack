# Contributing to ReStack

Thank you for your interest in contributing! This toolkit is designed to evolve with the needs of Solution Architects using Claude Code.

## How to Contribute

### Types of Contributions

1. **New Skills** - Add new architecture skills
2. **Skill Improvements** - Enhance existing skills
3. **Templates** - Add or improve document templates
4. **Examples** - Provide real-world examples
5. **Documentation** - Improve guides and docs
6. **Bug Fixes** - Fix issues in skills or docs

## Development Setup

### Prerequisites

- Git installed
- Claude Code installed
- Text editor (VS Code, Vim, etc.)
- Basic understanding of Markdown

### Getting Started

```bash
# Fork and clone the repository
git clone <your-fork-url>
cd restack

# Create a feature branch
git checkout -b feature/your-feature-name

# Install skills locally for testing
ln -s "$(pwd)/skills"/* ~/.claude/skills/
```

## Skill Development Guidelines

### Skill Structure

Every skill should follow this structure:

```markdown
---
description: Brief description of what this skill does
model: sonnet
---

# Skill Name

You are an expert [role description]...

## Your Role
[Clear description of the skill's purpose]

## Commands
[Available slash commands]

## Templates
[Document templates and formats]

## Best Practices
[Guidelines for effective use]

## Workflow
[Step-by-step process]
```

### Skill Best Practices

1. **Clear Commands**: Define explicit slash commands
2. **Ask Questions**: Gather context before generating
3. **Use Templates**: Provide consistent output formats
4. **Include Examples**: Show users what good looks like
5. **Be Thorough**: Cover edge cases and alternatives
6. **Consider Workflow**: Follow natural work patterns

### Testing Your Skill

Before submitting:

1. **Test the skill in Claude Code**
   ```
   /your-skill-name [test with various inputs]
   ```

2. **Verify output quality**
   - Does it generate useful output?
   - Is the format consistent?
   - Are templates properly structured?

3. **Test edge cases**
   - Empty inputs
   - Complex scenarios
   - Error conditions

4. **Get feedback**
   - Use it yourself for real work
   - Ask colleagues to try it

## Contribution Process

### 1. Create an Issue

Before starting work, create an issue describing:
- What you want to add/change
- Why it's needed
- Proposed approach

### 2. Develop Your Contribution

**For New Skills:**

> **`SKILL.md` is generated — do not edit it.** Write
> `skills/<name>/SKILL.md.tmpl` and run the generator. Hand edits to a
> generated file are silently lost at the next build, and CI rejects the drift.
> See [ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md).

```bash
# Create the skill directory and template
mkdir -p skills/skill-name/sections
$EDITOR skills/skill-name/SKILL.md.tmpl

# Declare the tier in frontmatter (1 utility, 2 decision-shaping, 3 residuality
# core), resolve {{PREAMBLE}} at the top of the body, and put any situational
# depth in sections/ registered in sections/manifest.json.

# Generate — Claude Code loads skills/<name>/SKILL.md
python scripts/gen_skills.py skill-name

# Verify the tree is consistent before committing (both run in CI)
python scripts/gen_skills.py --check
python scripts/check_skills.py

# Add example output
mkdir examples/skill-name
touch examples/skill-name/example-output.md

# Update README.md, QUICKREF.md, GETTING_STARTED.md, and CLAUDE.md to list the new skill
# Commit BOTH the .tmpl and the generated SKILL.md
```

> **Where this structure came from.** The template + tiered preamble + on-demand
> sections pattern is adapted from [gstack](https://github.com/garrytan/gstack),
> which is worth reading if you are extending the authoring system rather than
> writing a skill — it is a larger, more mature implementation of the same
> mechanics. What we changed and what we left out is recorded in
> [ADR-008](docs/adr/ADR-008-generated-skills-with-tiered-preamble.md).

**Changing shared behaviour** — how decision briefs are formatted, what counts
as evidence, how a command reports completion — belongs in
`scripts/preamble/*.md`, not in an individual skill. Edit the fragment,
regenerate, and every skill at that tier picks it up.

**For Improvements:**

- Clearly document what changed and why
- Maintain backward compatibility when possible
- Update related documentation

### 3. Document Your Changes

- Update `README.md` if adding new skill
- Update `CLAUDE.md` with any architectural changes
- Add/update examples in `examples/`
- Update `docs/USAGE.md` with usage instructions

### 4. Create an ADR for Significant Changes

For major decisions, create an ADR:

```bash
# Use the ADR template
cp templates/adr-template.md docs/adr/ADR-XXX-your-decision.md

# Fill in the template
# Document context, decision, consequences, alternatives
```

### 5. Test Thoroughly

- Test the skill with Claude Code
- Verify all commands work
- Check output quality
- Test edge cases

### 6. Submit a Pull Request

```bash
# Commit your changes
git add .
git commit -m "feat(phase-X): add skill-name skill

Detailed description of what was added and why.

Closes #issue-number"

# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub
```

## Commit Message Guidelines

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(phase-1): add api-designer skill

Add comprehensive API design skill for REST and GraphQL API design,
validation, and documentation generation.

Closes #42

---

fix(adr): correct ADR numbering logic

ADR numbers were not sequential when ADRs were deleted. Updated to
find the highest existing number and increment.

Fixes #38

---

docs(usage): add tech-stack advisor examples

Add detailed examples showing how to use tech-stack advisor for
common scenarios like technology comparison and migration planning.
```

## Code Review Process

1. **Automated Checks**: PR must pass basic checks
2. **Peer Review**: At least one maintainer review
3. **Testing**: Changes must be tested
4. **Documentation**: Updates must include docs

### Review Criteria

- ✅ Follows skill structure guidelines
- ✅ Includes proper documentation
- ✅ Tested with Claude Code
- ✅ Examples provided (for new skills)
- ✅ Templates are well-formatted
- ✅ Commit messages follow convention

## Skill Guidelines

When contributing a new skill, consider where it fits:

- **Widely applicable** — useful to any architect on any engagement (e.g. stressor analysis, ADRs)
- **Deep analysis** — requires multiple steps or integrates with existing artefacts (e.g. capability assessment, pattern extraction)
- **Specialised** — domain-specific or scenario-specific (e.g. cloud architecture, compliance packs)

## Documentation Standards

### README Updates

When adding a skill, update README.md:

```markdown
### Phase X: Category Name
- ✅ `skill-name` - Brief description
```

### CLAUDE.md Updates

Document architectural decisions and patterns:

```markdown
## Skill Development Pattern

[Describe any new patterns or approaches]
```

### Usage Guide Updates

Add to `docs/USAGE.md`:

```markdown
## Skill Name

### Using the Skill

[Detailed usage instructions]

### Examples

[Real-world examples]

### Best Practices

[Guidelines for effective use]
```

## Template Guidelines

When creating templates:

1. **Use Standard Formats**: Follow industry standards
2. **Be Comprehensive**: Cover all necessary sections
3. **Include Comments**: Guide users on what to fill in
4. **Show Examples**: Provide example content
5. **Keep Consistent**: Match existing template style

## Example Guidelines

When adding examples:

1. **Use Realistic Scenarios**: Base on real-world situations
2. **Show Best Practices**: Demonstrate proper usage
3. **Be Complete**: Full examples, not fragments
4. **Add Context**: Explain why the example is good
5. **Vary Complexity**: Include simple and complex examples

## Getting Help

- 💬 **Questions**: Open an issue with the `question` label
- 🐛 **Bugs**: Open an issue with the `bug` label
- 💡 **Ideas**: Open an issue with the `enhancement` label
- 📖 **Documentation**: Check `docs/` directory

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in the community

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT).

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Reach out to maintainers

Thank you for helping make this toolkit better for all Solution Architects! 🎉
