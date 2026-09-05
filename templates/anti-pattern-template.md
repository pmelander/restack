# Anti-Pattern: [Name]

**Type:** [Architectural / Decision / Technology / Process]  
**Category:** [Specific category]  
**Severity:** [Critical / High / Medium / Low]  
**Last Updated:** [YYYY-MM-DD]  
**Status:** [Active Warning / Historical / Resolved]

---

## Summary

**One-line description:**  
[Single sentence describing what this anti-pattern is]

**TL;DR:**  
Don't [X] because [Y]. Instead, do [Z].

---

## What It Is

[Clear, detailed description of the anti-pattern - what does it look like in practice?]

**Visual Representation:**
```
[ASCII diagram or description showing the problematic structure]

Example of a bad approach:
┌──────────┐      ┌──────────┐
│ Service A│◀────▶│ Service B│
└──────────┘      └──────────┘
      │                │
      └────▶ Shared DB ◀┘
      
Problem: Tight coupling through shared database
```

**Alternative Names:**
- [Alias 1]
- [Alias 2]

---

## Why It Fails

### Root Causes

**1. [Primary Root Cause]**
   - [Explanation of why this fundamentally doesn't work]
   - [Theoretical or practical reason for failure]

**2. [Secondary Root Cause]**
   - [Another fundamental problem]

**3. [Tertiary Root Cause]**
   - [Additional failure mode]

### Long-term Consequences

**Technical Debt:**
- [How this creates technical debt]
- [Compounding effects over time]

**Operational Impact:**
- [Production problems this causes]
- [Operational burden]

**Team Impact:**
- [Developer productivity effects]
- [Knowledge transfer problems]
- [Morale impact]

**Business Impact:**
- [Feature velocity slowdown]
- [Risk to business objectives]
- [Cost implications]

---

## Common Triggers

**What leads teams to do this:**

**1. [Trigger 1]**
   - **Context:** [When this trigger appears]
   - **Why it seems attractive:** [Short-term benefit]
   - **Reality check:** [Why it backfires]

**2. [Trigger 2]**
   - [Similar structure]

**3. [Trigger 3]**
   - [Similar structure]

**Psychological Factors:**
- [Pressure: Time pressure, resource constraints]
- [Knowledge: Gaps in understanding]
- [Culture: Organizational factors]

---

## Symptoms & Warning Signs

**How to recognize this anti-pattern:**

### Early Warning Signs ⚠️

Catch it before it becomes entrenched:
- [Early symptom 1: Observable at the beginning]
- [Early symptom 2]
- [Early symptom 3]

### Active Symptoms 🚨

Clear signs you're using this anti-pattern:
- [Active symptom 1: Definitely present]
- [Active symptom 2]
- [Active symptom 3]

### Late-Stage Symptoms 💥

Advanced state, significant refactoring needed:
- [Late symptom 1: Problem deeply embedded]
- [Late symptom 2]
- [Late symptom 3]

### Measurement

**Metrics that indicate this anti-pattern:**
- [Metric 1: What to measure and threshold]
- [Metric 2: Example: Deployment frequency < 1/month]
- [Metric 3]

---

## Examples From Our Organization

### Example 1: [System/Project Name]

**What Happened:**  
[Describe the specific instance of this anti-pattern]

**Context:**  
[Why did the team do this? What constraints existed?]

**Consequences:**  
- [Specific problem 1 that resulted]
- [Specific problem 2]
- [Quantified impact if available: X hours wasted, Y incidents]

**Resolution:**  
[How was it fixed, if it was]

**Lessons Learned:**  
- [Key lesson 1]
- [Key lesson 2]

**Cost:**  
[Effort to fix, impact while existed]

### Example 2: [System/Project Name]

[Similar structure]

### Example 3: [System/Project Name]

[Similar structure]

---

## Correct Alternative

**Instead of [Anti-Pattern], do [Pattern]:**

### Recommended Approach

[Detailed description of the correct pattern or approach to use instead]

**Why This Works Better:**

- **[Benefit 1]**
  - [How this addresses the root cause]
  
- **[Benefit 2]**
  - [Another advantage]
  
- **[Benefit 3]**
  - [Additional benefit]

### Structure

```
[ASCII diagram of correct approach]

Better approach:
┌──────────┐      ┌──────────┐
│ Service A│─────▶│ Service B│
│  + DB A  │      │  + DB B  │
└──────────┘      └──────────┘
         │          │
         └─────API─┘
         
Solution: Database per service, communicate via API
```

### Key Principles

1. **[Principle 1]**
   - [Explanation]

2. **[Principle 2]**
   - [Explanation]

3. **[Principle 3]**
   - [Explanation]

### References

**Correct pattern:** [link to the replacement in `docs/patterns/`]

**ADRs Using Correct Approach:**
- [ADR-XXX: Title](link)

---

## Migration Strategy

**If you're already using this anti-pattern, here's how to fix it:**

### Assessment Phase

**1. Measure Current State**
   - [What to measure]
   - [How to assess impact]
   - [Create baseline metrics]

**2. Identify Scope**
   - [How widespread is the problem?]
   - [Which systems affected?]
   - [Dependency analysis]

**3. Estimate Effort**
   - [How much work to fix?]
   - [Resource requirements]
   - [Timeline estimation]

### Planning Phase

**1. Prioritization**
   - [Which instances to fix first?]
   - [Risk-based prioritization]
   - [Quick wins vs. long-term fixes]

**2. Migration Strategy**
   - **Big Bang:** [When appropriate and approach]
   - **Strangler Fig:** [When appropriate and approach]
   - **Incremental:** [When appropriate and approach]
   - **Recommended:** [Which strategy for this anti-pattern]

**3. Risk Mitigation**
   - [Risk 1 and mitigation]
   - [Risk 2 and mitigation]
   - [Risk 3 and mitigation]

### Execution Phase

**Step-by-Step Refactoring:**

**Step 1: [Phase name]**
- **What:** [What to do]
- **How:** [Implementation approach]
- **Validation:** [How to verify success]
- **Rollback:** [How to revert if needed]
- **Effort:** [Estimated time]

**Step 2: [Phase name]**
- [Similar structure]

**Step 3: [Phase name]**
- [Similar structure]

### Validation Phase

**Success Criteria:**
- [ ] [Criteria 1: Measurable outcome]
- [ ] [Criteria 2]
- [ ] [Criteria 3]

**Metrics to Track:**
- [Metric 1: Should improve from X to Y]
- [Metric 2]
- [Metric 3]

### Timeline & Effort

**Typical Refactoring:**
- **Small Instance:** [X hours/days]
- **Medium Instance:** [Y days/weeks]
- **Large Instance:** [Z weeks/months]

**Our Specific Case:**
- **Estimated Effort:** [Timeline]
- **Team Size:** [Required team]
- **Dependencies:** [What else needed]

---

## Prevention

**How to avoid this anti-pattern in future:**

### Design Phase

**1. Review Checklist**
   - [ ] [Check 1: Question to ask during design]
   - [ ] [Check 2]
   - [ ] [Check 3]

**2. Red Flags**
   - [Warning sign 1 to watch for]
   - [Warning sign 2]

**3. Questions to Ask**
   - [Question 1: Critical question for design review]
   - [Question 2]

### Development Phase

**1. Code Review Checks**
   - [What reviewers should look for]
   - [Automated checks if possible]

**2. Testing**
   - [Tests that would catch this]
   - [Validation approach]

### Process Phase

**1. Architectural Review**
   - Include anti-pattern review in design reviews
   - Reference this doc in review checklist
   - Validate against pattern catalog

**2. Team Education**
   - [Training needed]
   - [Documentation to share]
   - [Examples to discuss]

**3. Governance**
   - [Policy 1: Organizational rule]
   - [Policy 2]

### Tools & Automation

**Automated Detection:**
- [Tool/script to detect this anti-pattern]
- [Metric threshold alerting]
- [CI/CD gate if applicable]

**Linting Rules:**
- [Rule 1]
- [Rule 2]

---

## Related Anti-Patterns

### Often Appears With:

- **[Anti-Pattern 1]**
  - [How they're related]
  - [Combined impact]

- **[Anti-Pattern 2]**
  - [Relationship]

### Can Lead To:

- **[Downstream Anti-Pattern 1]**
  - [How this anti-pattern causes the next one]

### Similar But Different:

- **[Similar Anti-Pattern]**
  - [Key difference]
  - [How to distinguish]

---

## Case Studies

### Industry Examples

**Company/Project 1:**
- **Context:** [Situation]
- **Anti-pattern Used:** [How it manifested]
- **Impact:** [Consequences]
- **Resolution:** [How they fixed it]
- **Source:** [Reference/link]

**Company/Project 2:**
- [Similar structure]

### Success Stories

**Example of Avoiding This:**

**Project:** [Name]  
**Context:** [Temptation to use anti-pattern]  
**Decision:** [How team avoided it]  
**Outcome:** [Positive result]  
**Lesson:** [Key takeaway]

---

## References

### Internal

**Post-Mortems:**
- [Incident XXX](link) - [How this anti-pattern contributed]

**ADRs:**
- [ADR-XXX: Deprecating This Approach](link)
- [ADR-YYY: Adopting Correct Pattern](link)

**Discussion Threads:**
- [Tech discussion about this problem](link)

### External

**Articles:**
- [Article Title](URL) - [Key points]
- [Article Title](URL) - [Key points]

**Books:**
- [Book Title] by [Author] - Chapter/Section
- [Book Title] - [Relevant content]

**Videos:**
- [Talk Title](URL) - [Speaker, Key insights]

**Academic Papers:**
- [Paper Title](URL) - [Findings]

---

## Severity Assessment

### Impact Analysis

| Dimension | Severity | Justification |
|-----------|----------|---------------|
| Development Velocity | [Critical/High/Med/Low] | [Why] |
| System Reliability | [Critical/High/Med/Low] | [Why] |
| Security | [Critical/High/Med/Low] | [Why] |
| Maintainability | [Critical/High/Med/Low] | [Why] |
| Scalability | [Critical/High/Med/Low] | [Why] |
| Cost | [Critical/High/Med/Low] | [Why] |
| **Overall** | **[Severity]** | |

### Priority Matrix

**When to Fix:**
- **Critical Severity:** Fix immediately, block releases
- **High Severity:** Fix within sprint, high priority
- **Medium Severity:** Fix within quarter, medium priority
- **Low Severity:** Fix opportunistically, low priority

**This Anti-Pattern:** [Priority level] - [Justification]

---

## Statistics

**In Our Organization:**

**Occurrences:** [X instances identified]  
**Systems Affected:** [Y systems]  
**Total Impact:** [Z hours/dollars/incidents]  
**Resolved:** [N instances fixed]  
**In Progress:** [M instances being addressed]  
**Remaining:** [R instances still present]

**Trend:**
- [YYYY-Q1]: X instances
- [YYYY-Q2]: Y instances
- [YYYY-Q3]: Z instances
- **Current**: N instances

[Graph or trend direction: ↗️ Increasing / → Stable / ↘️ Decreasing]

---

## Discussion

### Open Questions

- [Question 1: Area of debate or uncertainty]
- [Question 2]

### Feedback

**Last Team Review:** [YYYY-MM-DD]

**Key Discussion Points:**
- [Point 1]
- [Point 2]

**Proposed Updates:**
- [Proposed change 1]
- [Proposed change 2]

---

## Change Log

**[YYYY-MM-DD]** - v1.0
- Initial documentation of anti-pattern

**[YYYY-MM-DD]** - v1.1
- Added example from [project]
- Updated severity based on [incident]

**[YYYY-MM-DD]** - v1.2
- Added migration strategy section
- Updated prevention measures

**[YYYY-MM-DD]** - v2.0
- Major update after [significant event]
- Changed severity from [X] to [Y]
- Added new examples

---

**Remember:** Anti-patterns are not moral judgments. They document what doesn't work in our context so we can learn and improve. The goal is prevention through awareness, not blame.

---

**Document Owner:** [Name/Team]  
**Last Updated:** [YYYY-MM-DD]  
**Next Review:** [YYYY-MM-DD]