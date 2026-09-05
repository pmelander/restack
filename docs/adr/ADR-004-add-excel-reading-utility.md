# ADR-004: Add Excel Reading Utility Skill

**Status:** Accepted

**Date:** 2026-05-17

**Deciders:** Solution Architect Team

**Technical Story:** Adding Excel/CSV reading capability to bridge spreadsheet workflows into markdown-first toolkit

## Context

Architects frequently receive data and artifacts in Excel format:
- Stressor analysis matrices from stakeholders
- Technology comparison spreadsheets from teams
- Capacity planning forecasts from operations
- Risk registers and compliance checklists from governance

Currently, there's no way to import this data into the toolkit. Users must:
- Manually copy-paste → Error-prone, time-consuming
- Recreate in markdown → Duplicates effort
- Leave data in Excel → Breaks toolkit workflow

**Why This Matters:**
- Excel is ubiquitous in enterprise architecture
- Stakeholders and teams often work in spreadsheets
- Importing existing artifacts reduces friction
- Enables collaboration across tool preferences

**Specific Use Case:**
After implementing stressor-analysis skill, the user shared an Excel file with a stressor matrix and suggested adding Excel reading capability. This would enable:
- Importing stressor matrices from Excel workshops
- Loading existing architecture artifacts
- Collaborating with Excel-first teams

## Decision

We will **add Excel reading as a standalone utility skill** in a new `skills/utilities/` category.

**What we're building:**
- **Utility skill:** `skills/utilities/excel-reader.md`
- **Python helper:** `helpers/read_spreadsheet.py` (uses openpyxl)
  — *moved to `skills/restack-excel/read_spreadsheet.py` in September 2026 so it
  survives installation; see [ADR-010](ADR-010-skills-are-self-contained.md)*
- **Commands:** `/restack-excel read`, `/restack-excel preview`, `/restack-excel sheets`, `/restack-excel convert`
- **Integration:** `/restack-stressor import` command wraps excel reader
- **Dependencies:** `requirements.txt` with openpyxl

**What makes it a utility:**
- Provides infrastructure (file reading), not capability-building
- Bridges Excel-first workflows → markdown-first thinking
- Enables other skills (stressor, tech stack, capacity planning)
- Success = convenience and integration, not learning transfer

## Alternatives Considered

### Alternative 1: Integrate into Stressor Analysis Only
**What:** Add `/restack-stressor import <excel>` without general excel-reader skill

**Pros:**
- Focused, purpose-built for stressor matrices
- Simpler, no new skill to learn
- Tightly integrated

**Cons:**
- Not reusable for other needs (tech comparisons, capacity planning)
- Locks Excel reading into one skill
- Future skills need to duplicate Excel reading logic
- Misses opportunity for general utility

**Why rejected:** Too narrow. Many future skills will need spreadsheet data. General utility provides better value.

### Alternative 2: External Helper Only (No Skill)
**What:** Create `helpers/read_spreadsheet.py` with no skill wrapper, call via Bash when needed

**Pros:**
- Simplest implementation
- No new skill overhead
- Can be called from any context

**Cons:**
- Less discoverable (no `/` command)
- Inconsistent with toolkit UX
- Requires users to know Python/CLI syntax
- No error messages or guidance
- Doesn't feel integrated

**Why rejected:** Poor UX. Skills provide discoverability, error messages, and integration. The helper alone would feel bolted-on.

### Alternative 3: Place in Phase 1 (With Core Skills)
**What:** Put excel-reader in `skills/phase-1/` alongside adr, solution-doc, tech-stack, design-review, stressor

**Pros:**
- Highly visible, first-class citizen
- Easier to discover
- Same installation as core skills

**Cons:**
- Confuses capability-building vs infrastructure
- Phase 1 is for thinking skills (decision-making, systems thinking, antifragility)
- Excel reading doesn't "build a capability" in the residuality sense
- Dilutes Phase 1's focus on capability development

**Why rejected:** Philosophically inconsistent. Phase 1 teaches thinking; utilities provide tooling. Clear separation maintains toolkit coherence.

### Alternative 4: Bi-directional (Import AND Export)
**What:** Support both Excel → markdown AND markdown → Excel

**Pros:**
- More powerful
- Could export stressor matrices back to Excel for stakeholders
- Round-trip workflow

**Cons:**
- More complex (export is harder than import)
- Pushes users back to Excel (opposite of goal)
- Contradicts markdown-first philosophy
- More maintenance burden

**Why rejected:** Export contradicts the goal of shifting to markdown-first thinking. Excel reader should be a **bridge into** markdown, not a round-trip tool. If users need to share with Excel users, they can copy-paste or screenshot.

## Consequences

### Positive

**For Architects:**
- **Import existing artifacts** without manual copy-paste
- **Collaborate with Excel users** seamlessly
- **Reduce friction** when adopting toolkit
- **Bridge workflows** from Excel-first to markdown-first

**For Skills:**
- **Stressor analysis** can import matrices from workshops
- **Tech stack** can load comparison data
- **Future skills** (capacity planning, risk analysis) can reuse
- **Composable** - skills call excel-reader when needed

**For the Toolkit:**
- **Clear utilities category** separates infrastructure from capabilities
- **Pattern established** for future utilities (diagram generators, template managers)
- **Reusable helper** - one script serves many skills
- **Professional feel** - handles common enterprise scenario

**For Residuality Philosophy:**
- **Bridge tool** that enables capability development
- **Eventually less needed** as architects shift to markdown-first
- **Reduces adoption friction** without compromising capability focus
- **Clear separation** between utilities (tools) and skills (capabilities)

### Negative

**Complexity:**
- New category (`utilities/`) to explain and maintain
- Python dependency (openpyxl) requires installation
- Another skill for users to learn
- Helper script to maintain and test

**Maintenance:**
- openpyxl updates and compatibility
- Edge cases: corrupted files, huge files, encoding issues
- Multiple file formats (.xlsx, .xls, .csv)
- User support for installation problems

**Philosophy Risk:**
- Could encourage Excel-first thinking if overused
- Might slow markdown adoption
- Risk of becoming a crutch instead of a bridge
- Users might expect export too (scope creep)

**Technical Debt:**
- Python dependency increases setup complexity
- Cross-platform testing (Windows/Mac/Linux)
- Security concerns (file uploads, macro execution)
- Performance with large files

### Neutral

- Adds `skills/utilities/` directory (new category)
- First utility skill (establishes pattern)
- Read-only (import only, no export)
- Requires documenting utilities vs capabilities distinction

## Implementation Details

### File Structure
```
skills/utilities/
  README.md              # Explain utilities vs capabilities
  excel-reader.md        # Skill specification

helpers/
  read_spreadsheet.py    # Python implementation

requirements.txt         # openpyxl>=3.1.0

examples/excel-reader/
  sample-data.xlsx       # Test file
  sample-data.md         # Expected output
```

### Commands
- `/restack-excel read <file> [sheet]` - Read and display as markdown table
- `/restack-excel preview <file> [rows]` - Show first N rows (default 10)
- `/restack-excel sheets <file>` - List available sheets
- `/restack-excel convert <file> [sheet]` - Save to docs/imports/

### Integration
- `/restack-stressor import <excel>` wraps `/restack-excel read` for stressor matrices
- Future skills can call excel-reader as needed
- Helper script works standalone via CLI for advanced users

### Security & Limits
- Max file size: 10 MB (warn at 5 MB)
- Max rows: 10,000 (warn at 1,000)
- No macro execution (openpyxl data-only mode)
- Sanitize markdown special chars
- Validate file paths

### Dependencies
- **Required:** Python 3.8+, pip
- **Library:** openpyxl>=3.1.0 (for .xlsx/.xls)
- **Built-in:** csv module (for .csv, no extra dep)
- **Cross-platform:** Pure Python, works everywhere

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Dependency installation issues | High | Medium | Clear error messages, install instructions, fallback to CSV |
| Users rely on Excel instead of markdown | Medium | Medium | Position as bridge tool, document markdown-first philosophy |
| Large files cause performance issues | Medium | Medium | File size limits (10MB), row limits (10k), preview mode |
| Corrupted files crash helper | Low | Medium | Try/catch, validation, graceful error messages |
| Security concerns (macro execution) | High | Low | Use openpyxl data-only mode, never eval macros, validate paths |
| Scope creep (export, Google Sheets) | Medium | High | Document read-only decision in ADR, defer export requests |

## Metrics for Success

**Usage Metrics:**
- Number of `/restack-excel read` commands used
- Excel imports per stressor analysis session
- Utility skill adoption rate

**Quality Metrics:**
- Successful imports (no errors)
- File format coverage (.xlsx, .xls, .csv)
- Cross-platform compatibility (Windows/Mac/Linux)

**Residuality Metrics:**
- Markdown artifacts created from Excel imports
- Decline in Excel usage over time (good!)
- Architects naturally creating in markdown first

**Integration Metrics:**
- Skills using excel-reader (stressor, tech-stack, future)
- Helper script reuse count
- Utility pattern adoption for other tools

## References

- User request: "maybe we should add a tool or skill to read Excel documents?"
- Stressor Analysis skill: `skills/phase-1/stressor-analysis.md`
- Excel example from user: Stressor Analysis.xlsx (banking system)
- openpyxl documentation: https://openpyxl.readthedocs.io/
- [ADR-001: Incorporate Residuality Theory](ADR-001-incorporate-residuality-theory.md)
- [ADR-003: Add Stressor Analysis Skill](ADR-003-add-stressor-analysis-skill.md)

## Open Questions

- [ ] Should we support .xlsm (macro-enabled) in read-only mode? → NO (security risk)
- [ ] Do we need export (markdown → Excel)? → Defer (contradicts markdown-first goal)
- [ ] Should we support Google Sheets API? → Defer (complexity, just export to .xlsx first)
- [ ] Maximum file size of 10MB sufficient? → Yes, can adjust if needed
- [ ] Should we create industry-specific Excel templates? → Maybe Phase 2

## Next Actions

1. ✅ Create `helpers/read_spreadsheet.py` with openpyxl
2. ✅ Create `skills/utilities/` directory
3. ✅ Create `skills/utilities/README.md` (explain category)
4. ✅ Create `skills/utilities/excel-reader.md` (skill spec)
5. ✅ Create `requirements.txt` with openpyxl
6. ✅ Add `/restack-stressor import` to stressor-analysis.md
7. 📋 Create example files (sample-data.xlsx)
8. 📋 Update documentation (README, QUICKREF, GETTING_STARTED, ROADMAP, CLAUDE.md)
9. 📋 Test on Windows/Mac/Linux
10. 📋 Commit with message: `feat(utilities): Add Excel/CSV reading capability`

---

**This ADR establishes the utilities category and adds Excel reading as the first utility skill. It maintains the toolkit's capability-building focus (Phase 1/2/3) while providing essential infrastructure that enables those capabilities.**

**Remember:** Excel reader is a **bridge**, not a destination. The goal is markdown-first thinking; Excel import is for legacy and collaboration only.

**Philosophy Check:** ✅ Utilities provide tooling, capabilities teach thinking. This is clearly infrastructure, correctly categorized, and philosophically aligned with residuality theory.
