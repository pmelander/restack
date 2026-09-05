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
/restack-adr create <title>              # Create new ADR
/restack-adr list                        # List all ADRs
/restack-adr update <number>             # Update existing ADR
/restack-adr search <term>               # Search ADRs
```

### Solution Documentation
```bash
/restack-solution-doc hld                # High-Level Design
/restack-solution-doc lld [component]    # Low-Level Design
/restack-solution-doc deployment         # Deployment Guide
/restack-solution-doc runbook            # Operations Runbook
/restack-solution-doc complete           # Generate all docs
/restack-solution-doc update <type>      # Update existing doc
```

### Technology Stack Advisor
```bash
/restack-tech-stack recommend                      # Full stack recommendation
/restack-tech-stack evaluate <technology>          # Evaluate specific tech
/restack-tech-stack compare <tech1> vs <tech2>     # Compare technologies
/restack-tech-stack migrate from <old> to <new>    # Migration analysis
/restack-tech-stack report                         # Generate tech report
```

### Design Review
```bash
/restack-design-review architecture      # Review system architecture
/restack-design-review api               # Review API design
/restack-design-review data              # Review data architecture
/restack-design-review security          # Security-focused review
/restack-design-review performance       # Performance-focused review
/restack-design-review complete          # Comprehensive review
```

### Stressor Analysis
```bash
/restack-stressor walk [path-name]           # Traverse a path, evaluating each actor in sequence
/restack-stressor generate [count]           # Generate creative stressors
/restack-stressor analyze                    # Build impact matrix (actors × stressors)
/restack-stressor vulnerabilities            # Identify most-impacted actors
/restack-stressor residues                   # Suggest residuals (new actors, intentions, paths)
/restack-stressor iterate                    # Re-walk after adding residuals
/restack-stressor workshop                   # Facilitate team stressor workshop
/restack-stressor import <file> [sheet]      # Import stressor matrix from Excel/CSV
/restack-stressor compliance <pack>          # Inject compliance stressor pack
```

### Architect's Journey
```bash
/restack-journey start           # Begin a new journey — assess terrain, map the route
/restack-journey where           # Where am I? What comes next?
/restack-journey iterate         # Iterate stressor loop or proceed?
/restack-journey review          # Journey health check — completeness and quality
/restack-journey cadence         # Establish an ongoing iteration rhythm
```

### Environment Discovery
```bash
/restack-discover paths                  # Map paths through an existing system
/restack-discover actor <name>           # Investigate what an actor actually does
/restack-discover intentions             # Trace how an intention propagates
/restack-discover gaps                   # Identify and prioritise confidence gaps
/restack-discover organisation           # Map organisational resistance as stressors
/restack-discover confidence             # Assess readiness to proceed to stressor analysis
```

### Cloud Architect
```bash
/restack-cloud design <architecture>     # Design cloud-native architecture
/restack-cloud iac <provider>            # Generate Terraform/CloudFormation/Bicep/CDK
/restack-cloud review                    # Well-Architected review (6 pillars)
/restack-cloud cost                      # Cost analysis and optimisation
/restack-cloud migrate <to-cloud>        # Migration strategy using the 6 R's
/restack-cloud dr                        # Disaster recovery strategy
```

### Capacity Planner
```bash
/restack-capacity estimate               # Estimate resource requirements
/restack-capacity scale <strategy>       # Design scaling approach
/restack-capacity bottleneck             # Identify capacity constraints
/restack-capacity load-test              # Design load testing strategy
/restack-capacity forecast               # Model future capacity needs
/restack-capacity right-size             # Identify and reduce over-provisioning
```

### Excel Reader (Utility)
```bash
/restack-excel read <file> [sheet]       # Read spreadsheet as markdown
/restack-excel preview <file> [rows]     # Preview first N rows
/restack-excel sheets <file>             # List available sheets
/restack-excel convert <file> [sheet]    # Save to docs/imports/
```

### Architecture Learning Analyzer
```bash
/restack-arch-learning analyze           # Analyze ADR history
/restack-arch-learning patterns          # Extract decision patterns
/restack-arch-learning outcomes          # Review decision outcomes
/restack-arch-learning retrospective     # Facilitate team retrospective
/restack-arch-learning lessons           # Generate lessons learned report
/restack-arch-learning trends            # Identify trends over time
```

### Team Capability Assessor
```bash
/restack-capability-assessor assess      # Assess team maturity
/restack-capability-assessor gaps        # Identify capability gaps
/restack-capability-assessor roadmap     # Create development roadmap
/restack-capability-assessor track       # Track growth over time
/restack-capability-assessor exercises   # Get capability-building activities
/restack-capability-assessor compare     # Compare against benchmarks
```

### Pattern Extractor
```bash
/restack-patterns extract                # Extract patterns from knowledge
/restack-patterns catalog                # View pattern library
/restack-patterns suggest <scenario>     # Get pattern recommendations
/restack-patterns effectiveness          # Track pattern success
/restack-patterns anti-patterns          # Document what doesn't work
/restack-patterns evolve                 # Update patterns based on learning
```

### Evolutionary Architecture Coach
```bash
/restack-evolve assess                   # Assess evolutionary readiness
/restack-evolve fitness-functions        # Define fitness functions
/restack-evolve brittleness              # Identify brittle areas
/restack-evolve increment                # Plan incremental improvements
/restack-evolve health                   # Track architectural health
/restack-evolve coach                    # Interactive coaching session
```

---

## Common Workflows

### New Project (Greenfield)
```
1. /restack-journey start              # assess terrain, map the route
2. /restack-tech-stack recommend
3. /restack-adr create [for each major decision]
4. /restack-solution-doc hld
5. /restack-stressor walk              # walk primary paths first
6. /restack-stressor generate          # generate stressors
7. /restack-stressor analyze           # build impact matrix
8. /restack-stressor residues          # identify residuals
9. /restack-journey iterate            # proceed or loop?
10. /restack-design-review architecture
11. /restack-solution-doc deployment
```

### Existing System (Brownfield / Minefield)
```
1. /restack-journey start              # assess terrain, map the route
2. /restack-discover paths             # map what's actually there
3. /restack-discover actor <critical>  # investigate opaque actors
4. /restack-discover gaps              # prioritise unknowns
5. /restack-discover organisation      # translate resistance into stressors
6. /restack-discover confidence        # explicit go/no-go before walking
7. /restack-stressor walk              # walk discovered paths
8. /restack-stressor generate          # generate stressors
9. /restack-stressor analyze           # build matrix on real paths
10. /restack-stressor residues         # identify residuals
11. /restack-journey iterate           # proceed or loop?
12. /restack-adr create [key decisions]
```

### Pre-Production Review
```
1. /restack-design-review complete
2. [Fix critical issues]
3. /restack-design-review [specific flagged areas]
4. /restack-solution-doc complete
```

### Cloud Migration
```
1. /restack-cloud migrate to <provider>
2. /restack-cloud design <target architecture>
3. /restack-cloud review
4. /restack-cloud iac terraform
5. /restack-adr create [document key cloud decisions]
6. /restack-cloud dr
```

### Capacity Planning
```
1. /restack-capacity estimate
2. /restack-capacity bottleneck
3. /restack-capacity scale auto
4. /restack-capacity load-test
5. /restack-capacity forecast
```

### Compliance (via Antifragility)
```
1. /restack-stressor compliance <pack>   # Inject regulatory stressors
2. /restack-stressor walk                # Walk paths under compliance stressors
3. /restack-stressor analyze             # Build impact matrix
4. /restack-stressor residues            # Residuals address compliance structurally
5. /restack-adr create [document residuals as decisions]
```

### Organisational Learning Rhythm
```
Monthly:
  /restack-evolve health
  /restack-arch-learning analyze
  /restack-patterns effectiveness

Quarterly:
  /restack-capability-assessor assess
  /restack-capability-assessor roadmap
  /restack-arch-learning retrospective
  /restack-patterns evolve
  /restack-evolve assess
  /restack-journey cadence               # review and refresh ongoing rhythm
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

> **Note:** Risk Assessor excluded (covered by Residuality/Stressor Analysis — ADR-006). Compliance Checker replaced by `/restack-stressor compliance` packs (ADR-007).
