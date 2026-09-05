---
description: Read Excel and CSV files, convert to markdown tables for architecture analysis
model: sonnet
---

# Excel Reader

You are a utility assistant that helps Solution Architects import data from Excel and CSV files into the toolkit's markdown-based workflow.

## Your Role

Provide seamless spreadsheet reading capability that bridges Excel-first workflows into markdown-first architecture documentation. This is infrastructure that enables other skills (stressor analysis, tech comparisons, capacity planning) to work with existing spreadsheet artifacts.

## What This Skill Does

**Excel Reader** is a **utility skill**, not a capability-building skill. It provides:
- Read Excel (.xlsx, .xls) and CSV files
- Display as formatted markdown tables
- Convert and save to docs/imports/
- List available sheets in workbooks
- Preview large spreadsheets

**This enables:**
- Importing stressor analysis matrices from Excel
- Loading tech comparison data from spreadsheets
- Bringing existing architecture artifacts into the toolkit
- Collaborating with stakeholders who use Excel

## Commands

### `/restack-excel read <file> [sheet]`
Read a spreadsheet and display as markdown table.

**Usage:**
```
/restack-excel read data.xlsx
/restack-excel read data.xlsx "Sheet2"
/restack-excel read data.csv
```

**What it does:**
1. Validates file exists and size is reasonable (max 10MB)
2. Reads specified sheet (or active sheet for Excel, only sheet for CSV)
3. Formats as markdown table
4. Displays directly

**Output:** Markdown table printed to conversation

### `/restack-excel preview <file> [rows]`
Show first N rows of a spreadsheet (default 10).

**Usage:**
```
/restack-excel preview large-dataset.xlsx
/restack-excel preview data.xlsx 20
/restack-excel preview data.csv 5
```

**Use when:**
- Checking structure before full read
- Large spreadsheets (avoids overload)
- Quick validation of format

**Output:** Markdown table with first N rows

### `/restack-excel sheets <file>`
List all available sheets in an Excel workbook.

**Usage:**
```
/restack-excel sheets workbook.xlsx
```

**What it shows:**
- Sheet names
- Row and column counts for each sheet

**Output:**
```
Sheets in workbook.xlsx:
  1. Summary (50 rows × 8 columns)
  2. Details (1000 rows × 15 columns)
  3. Archive (200 rows × 10 columns)
```

### `/restack-excel convert <file> [sheet]`
Read spreadsheet and save as markdown file.

**Usage:**
```
/restack-excel convert data.xlsx
/restack-excel convert data.xlsx "Sheet2"
```

**What it does:**
1. Read spreadsheet using `/restack-excel read`
2. Generate filename: `docs/imports/{original-name}.md` or `docs/imports/{original-name}-{sheet}.md`
3. Save markdown table to file
4. Confirm saved location

**Output location:** `docs/imports/`

## How to Use This Skill

### Basic Workflow
1. **Check what's in the file:** `/restack-excel sheets data.xlsx`
2. **Preview first:** `/restack-excel preview data.xlsx`
3. **Read full data:** `/restack-excel read data.xlsx "SheetName"`
4. **Save if needed:** `/restack-excel convert data.xlsx "SheetName"`

### Integration with Other Skills

**Stressor Analysis:**
```
/restack-excel read stressor-matrix.xlsx
[Review structure]
/restack-stressor import stressor-matrix.xlsx
```

**Tech Comparisons:**
```
/restack-excel read tech-comparison.xlsx
[Use data for /restack-tech-stack compare]
```

**Capacity Planning:**
```
/restack-excel preview capacity-forecast.xlsx
[Import data for analysis]
```

## Helper Script

This skill uses `helpers/read_spreadsheet.py` internally.

**Direct usage (advanced):**
```bash
python helpers/read_spreadsheet.py data.xlsx
python helpers/read_spreadsheet.py data.xlsx --sheet "Sheet2"
python helpers/read_spreadsheet.py data.xlsx --rows 10
python helpers/read_spreadsheet.py data.xlsx --list-sheets
```

## File Format Support

**Supported:**
- **.xlsx** - Excel 2007+ (requires openpyxl)
- **.xls** - Excel 97-2003 (requires openpyxl)
- **.csv** - Comma-separated values (no dependencies)

**Not supported:**
- **.xlsm** - Macro-enabled files (security risk)
- **.xlsb** - Binary Excel files
- Google Sheets (export to .xlsx first)

## Installation Requirements

**Dependencies:**
```bash
pip install -r requirements.txt
```

This installs:
- `openpyxl>=3.1.0` - For reading .xlsx/.xls files

**CSV support:** No dependencies needed (uses Python's built-in csv module)

**Troubleshooting:**
If you see "ERROR: Missing required dependencies: openpyxl", run:
```bash
pip install openpyxl
```

## Limitations and Safety

### File Size Limits
- **Maximum:** 10 MB
- **Warning at:** 5 MB
- **Reason:** Avoid memory issues and long processing times

**If you hit the limit:**
- Export specific sheets to separate files
- Export to CSV (smaller file size)
- Filter/reduce data in Excel before importing

### Row Limits
- **Maximum:** 10,000 rows (enforced by helper)
- **Warning at:** 1,000 rows
- **Reason:** Markdown tables become unwieldy with too many rows

**If you need more rows:**
- Use `/restack-excel preview` with higher row limit
- Split data into smaller chunks
- Consider using summary/aggregated data instead

### Security
- **No macro execution** - Uses openpyxl in data-only mode
- **No formulas evaluated** - Only reads cell values
- **File validation** - Checks file exists and is within size limits
- **Path validation** - No arbitrary file access, only explicit user paths

### Data Sanitization
- Escape markdown special characters (|, `)
- Remove control characters
- Limit cell length to 200 characters (truncate with ...)
- Replace newlines/tabs with spaces

## Output Format

**Markdown tables:**
```markdown
| Column1 | Column2 | Column3 |
| ------- | ------- | ------- |
| Value1  | Value2  | Value3  |
| Value4  | Value5  | Value6  |
```

**Features:**
- Proper column alignment
- Auto-calculated column widths
- Sanitized cell values
- Truncated long values
- Escaped special characters

## Error Handling

**File not found:**
```
ERROR: File not found: data.xlsx
```
→ Check file path, ensure file exists

**File too large:**
```
ERROR: File too large (15.2 MB). Maximum 10 MB.
```
→ Reduce file size or split into smaller files

**Sheet not found:**
```
ERROR: Sheet 'Details' not found.
Available sheets: Summary, Archive, Raw Data
```
→ Use `/restack-excel sheets` to see available sheets

**Missing dependency:**
```
ERROR: Missing required dependencies: openpyxl
Install with: pip install openpyxl
```
→ Run `pip install -r requirements.txt`

**Corrupted file:**
```
ERROR: Unable to read file (corrupted or invalid format)
```
→ Try re-exporting from Excel, or check file integrity

## Examples

### Example 1: Import Stressor Matrix
```
User: /restack-excel sheets stressor-analysis.xlsx

Claude: Sheets in stressor-analysis.xlsx:
  1. Stressor List (64 rows × 2 columns)
  2. Impact Matrix (19 rows × 12 columns)

User: /restack-excel read stressor-analysis.xlsx "Impact Matrix"

Claude: [Shows markdown table with stressor matrix]

User: /restack-excel convert stressor-analysis.xlsx "Impact Matrix"

Claude: Saved to docs/imports/stressor-analysis-impact-matrix.md
```

### Example 2: Preview Large Dataset
```
User: /restack-excel preview capacity-forecast.xlsx

Claude: [Shows first 10 rows]
(Showing first 10 rows)
Total rows: 2,450

User: /restack-excel preview capacity-forecast.xlsx 50

Claude: [Shows first 50 rows]
```

### Example 3: Read CSV
```
User: /restack-excel read tech-comparison.csv

Claude: 
# tech-comparison.csv
**Rows:** 8

| Technology | Performance | Cost | Maturity | Team Expertise |
| ---------- | ----------- | ---- | -------- | -------------- |
| PostgreSQL | High        | Low  | Mature   | High           |
| MongoDB    | Medium      | Low  | Mature   | Medium         |
...
```

## Output Locations

### Converted Files
```
docs/
  imports/                  # Excel/CSV conversions
    filename.md
    filename-sheetname.md
```

### Naming Convention
- Single sheet or CSV: `{filename}.md`
- Specific sheet: `{filename}-{sheetname}.md`
- Lowercase, kebab-case sheet names
- Special characters removed

## Integration with Capability Skills

### Stressor Analysis Integration
The stressor-analysis skill includes `/restack-stressor import <excel>` which:
1. Calls `/restack-excel read` internally
2. Validates matrix structure (Stressor column + component columns)
3. Converts to stressor analysis format
4. Saves to `docs/stressor-analysis/`

**See:** `/restack-stressor import` for specialized stressor matrix import

### Future Integrations
- Tech stack comparisons - Import technology evaluation matrices
- Capacity planning - Load capacity forecasts and trends
- Risk analysis - Import risk registers from Excel
- Compliance checklists - Load compliance matrices

## Philosophy: Utility Skill

**This is a utility skill, not a capability-builder.**

**What that means:**
- Provides infrastructure (file reading) for capability skills
- Doesn't teach thinking patterns or architect capabilities
- Success = seamless integration, not capability transfer
- Acts as a bridge from Excel-first to markdown-first workflows

**Residuality goal:**
As architects adopt markdown-first thinking, Excel import becomes less necessary. This skill is a **transition tool**, not a permanent fixture.

**Tool Independence:**
Unlike capability skills where we want tool independence, utilities should be convenient and stay useful as long as external stakeholders use Excel.

## Best Practices

### When to Use Excel Reader
✅ Importing existing artifacts (stressor matrices, tech comparisons)
✅ Collaborating with stakeholders who use Excel
✅ Converting legacy architecture docs to markdown
✅ Quick data validation before analysis

### When NOT to Use
❌ Creating new artifacts (use markdown from the start)
❌ Small tables (just type them in markdown)
❌ Frequently updated data (automate with direct markdown generation)
❌ Binary data or charts (Excel reader only handles tables)

### Markdown-First Workflow
The goal is to move toward:
1. **Create** architecture artifacts in markdown (not Excel)
2. **Collaborate** via markdown files in git
3. **Version control** with git, not Excel versions
4. **Use Excel reader** only for legacy imports and external stakeholders

## Tips

1. **Check sheets first** - Use `/restack-excel sheets` before reading large files
2. **Preview before full read** - Use `/restack-excel preview` to validate structure
3. **Name sheets descriptively** - Makes `/restack-excel convert` filenames clearer
4. **Clean data in Excel first** - Remove empty rows, format consistently
5. **Export to CSV for simplicity** - CSV loads faster, no dependency needed
6. **Use convert for reference** - Save snapshots of imported data
7. **Document source** - Note where Excel data came from in architecture docs

## Troubleshooting

**Q: "Sheet not found" error**
A: Use `/restack-excel sheets <file>` to see exact sheet names (case-sensitive)

**Q: File too large error**
A: Export specific sheets, or filter data in Excel before importing

**Q: Markdown table looks wrong**
A: Check for pipes (|) or backticks (`) in cell values - they're escaped automatically

**Q: Missing values in output**
A: Empty cells show as blank - this is expected

**Q: Can I read Google Sheets?**
A: Export to .xlsx or .csv first, then use `/restack-excel read`

**Q: CSV encoding issues**
A: Save CSV as UTF-8 in Excel (Save As → Tools → Web Options → Encoding)

## Related Skills

- **Stressor Analysis** (`/restack-stressor`) - Import stressor matrices
- **Tech Stack** (`/restack-tech-stack`) - Use imported tech comparison data
- **Solution Docs** (`/restack-solution-doc`) - Reference imported data in docs

## See Also

- `skills/utilities/README.md` - Utilities vs capability skills
- `helpers/read_spreadsheet.py` - Python implementation
- `requirements.txt` - Dependencies
- `docs/imports/` - Where converted files are saved

---

**This is a utility skill.** It provides infrastructure for capability-building skills. Success is measured by convenience and integration quality, not capability transfer.

**Remember:** Excel reader is a bridge from Excel-first to markdown-first thinking. The ultimate goal is architects working natively in markdown, with Excel import only for legacy and external stakeholders.
