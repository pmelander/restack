# ReStack - Quick Reference

## Installation

```bash
git clone git@github.com:pmelander/restack.git restack
cd restack
cp -R skills/* ~/.claude/skills/
pip install -r requirements.txt
```

---

## All Commands

### Architecture Decision Records
```bash
/adr create <title>              # Create new ADR
/adr list                        # List all ADRs
/adr update <number>             # Update existing ADR
/adr search <term>               # Search ADRs
```

### Solution Documentation
```bash
/solution-doc hld                # High-Level Design
/solution-doc lld [component]    # Low-Level Design
/solution-doc deployment         # Deployment Guide
/solution-doc runbook            # Operations Runbook
/solution-doc complete           # Generate all docs
/solution-doc update <type>      # Update existing doc
```

### Technology Stack Advisor
```bash
/tech-stack recommend                      # Full stack recommendation
/tech-stack evaluate <technology>          # Evaluate specific tech
/tech-stack compare <tech1> vs <tech2>     # Compare technologies
/tech-stack migrate from <old> to <new>    # Migration analysis
/tech-stack report                         # Generate tech report
```

### Design Review
```bash
/design-review architecture      # Review system architecture
/design-review api               # Review API design
/design-review data              # Review data architecture
/design-review security          # Security-focused review
/design-review performance       # Performance-focused review
/design-review complete          # Comprehensive review
```

### Stressor Analysis
```bash
/stressor walk [path-name]           # Traverse a path, evaluating each actor in sequence
/stressor generate [count]           # Generate creative stressors
/stressor analyze                    # Build impact matrix (actors × stressors)
/stressor vulnerabilities            # Identify most-impacted actors
/stressor residues                   # Suggest residuals (new actors, intentions, paths)
/stressor iterate                    # Re-walk after adding residuals
/stressor workshop                   # Facilitate team stressor workshop
/stressor import <file> [sheet]      # Import stressor matrix from Excel/CSV
/stressor compliance <pack>          # Inject compliance stressor pack
```

### Architect's Journey
```bash
/journey start           # Begin a new journey — assess terrain, map the route
/journey where           # Where am I? What comes next?
/journey iterate         # Iterate stressor loop or proceed?
/journey review          # Journey health check — completeness and quality
/journey cadence         # Establish an ongoing iteration rhythm
```

### Environment Discovery
```bash
/discover paths                  # Map paths through an existing system
/discover actor <name>           # Investigate what an actor actually does
/discover intentions             # Trace how an intention propagates
/discover gaps                   # Identify and prioritise confidence gaps
/discover organisation           # Map organisational resistance as stressors
/discover confidence             # Assess readiness to proceed to stressor analysis
```

### Cloud Architect
```bash
/cloud design <architecture>     # Design cloud-native architecture
/cloud iac <provider>            # Generate Terraform/CloudFormation/Bicep/CDK
/cloud review                    # Well-Architected review (6 pillars)
/cloud cost                      # Cost analysis and optimisation
/cloud migrate <to-cloud>        # Migration strategy using the 6 R's
/cloud dr                        # Disaster recovery strategy
```

### Capacity Planner
```bash
/capacity estimate               # Estimate resource requirements
/capacity scale <strategy>       # Design scaling approach
/capacity bottleneck             # Identify capacity constraints
/capacity load-test              # Design load testing strategy
/capacity forecast               # Model future capacity needs
/capacity right-size             # Identify and reduce over-provisioning
```

### Excel Reader (Utility)
```bash
/excel read <file> [sheet]       # Read spreadsheet as markdown
/excel preview <file> [rows]     # Preview first N rows
/excel sheets <file>             # List available sheets
/excel convert <file> [sheet]    # Save to docs/imports/
```

### Architecture Learning Analyzer
```bash
/arch-learning analyze           # Analyze ADR history
/arch-learning patterns          # Extract decision patterns
/arch-learning outcomes          # Review decision outcomes
/arch-learning retrospective     # Facilitate team retrospective
/arch-learning lessons           # Generate lessons learned report
/arch-learning trends            # Identify trends over time
```

### Team Capability Assessor
```bash
/capability-assessor assess      # Assess team maturity
/capability-assessor gaps        # Identify capability gaps
/capability-assessor roadmap     # Create development roadmap
/capability-assessor track       # Track growth over time
/capability-assessor exercises   # Get capability-building activities
/capability-assessor compare     # Compare against benchmarks
```

### Pattern Extractor
```bash
/patterns extract                # Extract patterns from knowledge
/patterns catalog                # View pattern library
/patterns suggest <scenario>     # Get pattern recommendations
/patterns effectiveness          # Track pattern success
/patterns anti-patterns          # Document what doesn't work
/patterns evolve                 # Update patterns based on learning
```

### Evolutionary Architecture Coach
```bash
/evolve assess                   # Assess evolutionary readiness
/evolve fitness-functions        # Define fitness functions
/evolve brittleness              # Identify brittle areas
/evolve increment                # Plan incremental improvements
/evolve health                   # Track architectural health
/evolve coach                    # Interactive coaching session
```

---

## Common Workflows

### New Project (Greenfield)
```
1. /journey start              # assess terrain, map the route
2. /tech-stack recommend
3. /adr create [for each major decision]
4. /solution-doc hld
5. /stressor walk              # walk primary paths first
6. /stressor generate          # generate stressors
7. /stressor analyze           # build impact matrix
8. /stressor residues          # identify residuals
9. /journey iterate            # proceed or loop?
10. /design-review architecture
11. /solution-doc deployment
```

### Existing System (Brownfield / Minefield)
```
1. /journey start              # assess terrain, map the route
2. /discover paths             # map what's actually there
3. /discover actor <critical>  # investigate opaque actors
4. /discover gaps              # prioritise unknowns
5. /discover organisation      # translate resistance into stressors
6. /discover confidence        # explicit go/no-go before walking
7. /stressor walk              # walk discovered paths
8. /stressor generate          # generate stressors
9. /stressor analyze           # build matrix on real paths
10. /stressor residues         # identify residuals
11. /journey iterate           # proceed or loop?
12. /adr create [key decisions]
```

### Pre-Production Review
```
1. /design-review complete
2. [Fix critical issues]
3. /design-review [specific flagged areas]
4. /solution-doc complete
```

### Cloud Migration
```
1. /cloud migrate to <provider>
2. /cloud design <target architecture>
3. /cloud review
4. /cloud iac terraform
5. /adr create [document key cloud decisions]
6. /cloud dr
```

### Capacity Planning
```
1. /capacity estimate
2. /capacity bottleneck
3. /capacity scale auto
4. /capacity load-test
5. /capacity forecast
```

### Compliance (via Antifragility)
```
1. /stressor compliance <pack>   # Inject regulatory stressors
2. /stressor walk                # Walk paths under compliance stressors
3. /stressor analyze             # Build impact matrix
4. /stressor residues            # Residuals address compliance structurally
5. /adr create [document residuals as decisions]
```

### Organisational Learning Rhythm
```
Monthly:
  /evolve health
  /arch-learning analyze
  /patterns effectiveness

Quarterly:
  /capability-assessor assess
  /capability-assessor roadmap
  /arch-learning retrospective
  /patterns evolve
  /evolve assess
  /journey cadence               # review and refresh ongoing rhythm
```

---

## Output Locations

```
docs/
  adr/                          # Architecture Decision Records
  architecture/                 # HLD, LLD documents
  deployment/                   # Deployment guides
  operations/                   # Runbooks
  reviews/                      # Design review reports
  technology/                   # Tech stack reports
  stressor-analysis/            # Stressor matrices and residue recommendations
  imports/                      # Imported Excel/CSV data
  arch-learning/                # Organisational learning outputs
  capability-assessments/       # Team maturity assessments
  patterns/                     # Pattern catalog and library
  evolutionary-architecture/    # Fitness functions, health dashboards
  capacity/                     # Capacity estimates and forecasts
  cloud/                        # Cloud architecture docs and IaC
```

---

## Best Practices

### ADRs
- ✅ Create for significant, lasting decisions only
- ✅ Document trade-offs honestly
- ✅ Update status when superseded
- ✅ Link related ADRs

### Stressor Analysis
- ✅ Walk paths before building the impact matrix — actors on paths are the columns
- ✅ Include absurd stressors — they reveal unknown unknowns
- ✅ Use compliance packs to let regulatory requirements emerge as residuals
- ✅ Iterate after adding residuals to measure improvement
- ✅ Run as a team workshop for shared mental models

### Cloud Architecture
- ✅ Design cloud-native, not lift-and-shift
- ✅ Review against all 6 Well-Architected pillars
- ✅ Generate IaC — never provision by hand
- ✅ Define DR strategy before you need it

### Capacity Planning
- ✅ State all assumptions explicitly
- ✅ Load test before production — never trust estimates alone
- ✅ Design for 10x current load
- ✅ Right-size continuously, not once

### Organisational Capabilities
- ✅ Assess capabilities before building roadmaps
- ✅ Start pattern library with 10-15 high-value patterns
- ✅ Automate fitness function checks
- ✅ Review ADR outcomes regularly to build institutional learning

---

## Phase Status

| Phase | Skills | Status |
|-------|--------|--------|
| Phase 1: Individual Capabilities | ADR, Solution Doc, Tech Stack, Design Review, Stressor Analysis | ✅ Complete |
| Utilities | Excel Reader | ✅ Complete |
| Phase 2: Organisational Capabilities | Arch Learning, Capability Assessor, Pattern Extractor, Evolutionary Coach | ✅ Complete |
| Phase 3: Specialised Tools | Cloud Architect, Capacity Planner, Environment Discovery, Architect's Journey | ✅ Complete |

> **Note:** Risk Assessor excluded (covered by Residuality/Stressor Analysis — ADR-006). Compliance Checker replaced by `/stressor compliance` packs (ADR-007).
