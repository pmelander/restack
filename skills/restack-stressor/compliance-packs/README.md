# Compliance Packs

Compliance packs are curated stressor sets derived from regulatory frameworks. They plug into the `/restack-stressor compliance <pack>` command, injecting regulation-specific stressors into a standard stressor analysis.

## Philosophy

Compliance controls exist because real harms happened. A compliance pack expresses those harms as stressors — so the residues architects design in response address the underlying harm structurally, not just procedurally.

**Compliance becomes a byproduct of good antifragile design, not a separate audit exercise.**

## Adding a Pack

1. Create a new file: `<framework-name>.md` (e.g., `gdpr.md`, `hipaa.md`)
2. Follow the pack structure defined in `skills/restack-stressor/SKILL.md`
3. Each stressor must:
   - Be phrased as a **concrete scenario** (not a control statement)
   - Include a **regulation reference** (article, section, or control ID)
   - Explain the **real harm** the regulation was created to prevent
4. List common residues that emerge from the analysis
5. Include a traceability note for audit purposes
6. Submit as a PR

## Available Packs

| File | Framework | Status |
|------|-----------|--------|
| `gdpr.md` | General Data Protection Regulation | ✅ Complete |
| `hipaa.md` | Health Insurance Portability and Accountability Act | 📋 Planned |
| `pci-dss.md` | Payment Card Industry Data Security Standard | 📋 Planned |
| `iso27001.md` | ISO/IEC 27001 Information Security | 📋 Planned |
| `soc2.md` | SOC 2 Trust Services Criteria | 📋 Planned |

## Key Principle

> Every compliance control exists because something went wrong.
> Understanding *why* a control exists is more valuable than knowing *what* it requires.
> Design architecture that makes the underlying harm structurally impossible.
