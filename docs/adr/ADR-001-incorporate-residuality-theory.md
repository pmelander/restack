# ADR-001: Incorporate Residuality Theory into Toolkit Design

**Status:** Accepted

**Date:** 2026-05-17

**Deciders:** Solution Architect Team, Claude Code Development

**Technical Story:** Phase 1 Refactor - Shift from tool-centric to capability-building approach

## Context

After completing ReStack's Phase 1 with four core skills (ADR, Solution Documentation, Tech Stack Advisor, Design Review), we discovered Barry O'Reilly's Residuality Theory, which fundamentally challenges how we think about the value our toolkit should deliver.

**The Problem:**
Our initial Phase 1 implementation focused on **output generation** - producing documents, reports, and artifacts. While useful, this approach has limitations:
- Tools generate artifacts but don't necessarily build lasting capabilities
- Focus on "what" (documents) rather than "why" (thinking and learning)
- No mechanism to capture learning or measure capability growth
- Missing feedback loops to understand what persists after use
- Phase 2 was planned as more analysis tools, continuing the tool-centric pattern

**Residuality Theory Core Principles:**
1. **Persistent Value** - What remains after the immediate work is done?
2. **Capability Building** - Are we building lasting organizational capabilities?
3. **Behavioral Change** - Are we changing how people think and work?
4. **Learning Systems** - Are we creating systems that learn and adapt?
5. **Evolutionary Thinking** - Do we support continuous evolution vs point-in-time snapshots?

**Key Questions Raised:**
- What capabilities should persist in a Solution Architect after using our toolkit?
- How do we measure if the toolkit builds better architectural thinking, not just better documents?
- Should tools teach architectural thinking, or just automate tasks?
- What's the residual value 6 months after someone uses these skills?

**Forces at Play:**
- **Immediate Utility** vs **Long-term Capability** - Need both, but must balance
- **Automation** vs **Education** - Tools can do too much, reducing learning
- **Speed** vs **Depth** - Fast outputs vs deep understanding
- **Individual** vs **Organizational** - Building personal skills vs team capabilities
- **Static** vs **Evolutionary** - Point-in-time artifacts vs continuous learning

## Decision

We will **refactor ReStack to explicitly incorporate Residuality Theory principles**, shifting from a tool-centric approach to a capability-building system.

**Phase 1 Refactor:**
Enhance existing skills to include:
1. **Reflection Prompts** - Each skill asks "What did you learn?" and captures insights
2. **Learning Capture** - Document not just decisions but the thinking behind them
3. **Capability Focus** - Make explicit what capability each skill builds
4. **Outcome Tracking** - Enable follow-up to learn from past decisions
5. **Teaching Mode** - Skills explain *why*, not just *what*

**Phase 2 Redesign:**
Shift from "Deep Analysis Tools" to "Capability Building Skills":
- Focus on building lasting organizational capabilities
- Emphasize learning systems over point-in-time analysis
- Create feedback loops and evolutionary thinking
- Measure capability growth over time

**Specific Changes:**
1. Each skill includes a "Capability Being Built" section
2. Skills ask reflective questions throughout the workflow
3. Add optional "learning review" mode for past decisions
4. Create capability maturity assessment framework
5. Phase 2 skills focus on meta-capabilities (learning to learn)

## Consequences

### Positive

**For Users:**
- **Lasting Impact** - Build architectural thinking capabilities that persist
- **Learning Organization** - Teams learn, not just produce artifacts
- **Better Decision-Making** - Understand *why*, not just *what*
- **Continuous Improvement** - Systems for learning from past decisions
- **Higher ROI** - Value compounds over time as capabilities grow

**For the Toolkit:**
- **Differentiation** - Unique approach vs other documentation tools
- **Strategic Alignment** - Aligns with modern thinking (Residuality Theory)
- **Sustainable Value** - Creates lasting organizational change
- **Evolutionary Design** - Built to evolve with teams
- **Measurable Impact** - Can track capability growth

**For Solution Architects:**
- **Skill Development** - Become better architects, not just faster documenters
- **Mental Models** - Build stronger architectural thinking patterns
- **Career Growth** - Develop capabilities that transfer across roles
- **Teaching Ability** - Learn to teach others through reflection

### Negative

**Complexity:**
- Skills become more complex with reflection and learning components
- May slow down initial usage (more questions to answer)
- Requires more thoughtful interaction vs quick automation

**Measurement Challenge:**
- Hard to quantify capability growth
- Subjective assessment of learning
- Longer feedback cycles to see residual value

**User Adoption:**
- Some users may just want fast output, not learning
- Requires mindset shift from tool usage to capability building
- May need more onboarding and explanation

**Development Effort:**
- More complex skill design
- Need to design capability frameworks
- Requires ongoing iteration based on feedback

### Neutral

- Shifts toolkit positioning from "automation tool" to "capability platform"
- Changes success metrics from "documents generated" to "capabilities built"
- Requires different documentation approach (teach, not just instruct)
- May attract different user base (growth-minded architects)

## Alternatives Considered

### Alternative 1: Keep Tool-Centric Approach
- **Pros:** 
  - Simpler to build and use
  - Faster immediate value
  - Clearer value proposition
  - Lower learning curve
- **Cons:** 
  - Limited lasting impact
  - Doesn't build capabilities
  - Commoditizable (any tool can generate docs)
  - No learning or evolution
- **Why rejected:** Misses opportunity to create lasting organizational value. Tools that just automate don't differentiate or compound value over time.

### Alternative 2: Build Separate "Learning Mode"
- **Pros:**
  - Allows users to choose fast mode vs learning mode
  - Doesn't complicate core workflows
  - Opt-in complexity
- **Cons:**
  - Learning becomes optional (most won't choose it)
  - Splits focus between two modes
  - Residuality becomes feature, not foundation
- **Why rejected:** Learning and capability-building should be core, not optional. If it's separate, it won't happen.

### Alternative 3: Wait Until Phase 3 for Capability Focus
- **Pros:**
  - Complete Phase 1 & 2 as planned first
  - Learn from usage before adding complexity
  - Staged approach reduces risk
- **Cons:**
  - Phase 1 & 2 build wrong mental model
  - Harder to retrofit later
  - Miss opportunity to learn from capability-focused design
  - Users already invested in tool-centric approach
- **Why rejected:** Better to get the foundation right now than refactor later. Residuality should inform everything, not be bolted on.

### Alternative 4: Create All-New "Residuality Skills"
- **Pros:**
  - Clean slate design
  - Keep existing skills unchanged
  - Parallel tracks for different user needs
- **Cons:**
  - Duplicates effort
  - Confuses users (which skills to use?)
  - Splits community
  - Doesn't improve existing work
- **Why rejected:** Better to enhance what exists than fragment the toolkit.

## Implementation Strategy

**Phase 1 Refactor (Weeks 1-2):**
1. Add "Capability Focus" section to each Phase 1 skill
2. Introduce reflection prompts at key decision points
3. Add "What did you learn?" capture at end of workflows
4. Update documentation to explain residuality approach

**Phase 2 Redesign (Weeks 3-4):**
1. Reframe Phase 2 skills around capability building
2. Design capability maturity assessment framework
3. Create learning feedback loop mechanisms
4. Update roadmap with new Phase 2 direction

**Phase 3 Vision (Future):**
1. Meta-capabilities (learning to learn)
2. Organizational capability measurement
3. Team capability building
4. Knowledge evolution tracking

## Success Metrics

**Traditional Metrics (Still Important):**
- Skills installed and used
- Documents generated
- User satisfaction

**Residuality Metrics (New Focus):**
- **Capability Growth:** Can users demonstrate improved architectural thinking?
- **Behavioral Change:** Are teams making better decisions over time?
- **Knowledge Persistence:** Do learnings persist beyond individual use?
- **Self-Sufficiency:** Do users need the tool less as they internalize capabilities?
- **Teaching Ability:** Can users teach others what they've learned?
- **Decision Quality:** Do reviewed decisions show better outcomes?

**Long-term Indicators (6-12 months):**
- Teams establish architectural practices independently
- Organizations develop their own architectural patterns
- Users contribute back learnings and improvements
- Toolkit becomes less necessary as capabilities internalize

## Risks and Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Users want fast automation, not learning | High | Medium | Provide "quick mode" that still captures minimal learning |
| Capability growth hard to measure | Medium | High | Start with qualitative feedback, iterate to quantitative |
| Complexity slows adoption | Medium | Medium | Excellent onboarding, clear value proposition |
| Residuality concepts unclear to users | Medium | High | Create simple explainers, use throughout documentation |
| Refactor breaks existing features | High | Low | Thorough testing, maintain backward compatibility |

## Migration Path

**For Existing Users (if any):**
1. Existing skills continue to work (backward compatible)
2. New reflection prompts are optional initially
3. Documentation explains new approach
4. Examples show before/after

**For New Users:**
1. Start with residuality-informed skills
2. Understand capability-building from day one
3. Natural learning progression

## References

- Barry O'Reilly, *Residuality Theory* (2026)
- Residuality Overview PDF
- [Lean Enterprise](https://www.oreilly.com/library/view/lean-enterprise/9781491946527/) - O'Reilly, Humble, Molesky
- [Unlearn](https://barryoreilly.com/unlearn/) - Barry O'Reilly
- [Learning Organizations](https://en.wikipedia.org/wiki/Learning_organization) - Peter Senge
- [Evolutionary Architecture](https://evolutionaryarchitecture.com/) - Ford, Parsons, Kua

## Open Questions

- [ ] What's the right balance between automation and learning?
- [ ] How do we measure capability growth quantitatively?
- [ ] Should we create a "capability maturity model" for architects?
- [ ] How do we capture organizational learnings, not just individual?
- [ ] What's the best way to create feedback loops on past decisions?

## Next Actions

1. Refactor ADR skill with residuality principles (Task #4)
2. Refactor remaining Phase 1 skills (Task #4)
3. Design capability measurement framework (Task #2)
4. Redesign Phase 2 roadmap (Task #3)
5. Update all documentation with residuality thinking
6. Create examples demonstrating capability building
7. Develop user guide explaining residuality approach

---

**This ADR itself demonstrates residuality thinking:**
- We're not just deciding to add features
- We're fundamentally shifting what value the toolkit creates
- We're asking: "What should persist after someone uses this toolkit?"
- Answer: **Better architectural thinking capabilities, not just better documents**
