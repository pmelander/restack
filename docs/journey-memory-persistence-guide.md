# Journey Memory Persistence — Implementation Guide

## What Changed

Journey progress tracking is now **mandatory** and **file-based**. Built-in Claude Code memory is insufficient for long-running architectural journeys.

## Why This Matters

Architectural journeys often:
- Span weeks or months with breaks in between
- Involve multiple architects (handoffs, pairing)
- Require audit trails for learning and governance
- Need iteration history to make informed proceed/iterate decisions
- Resume after context has been lost

**Without file-based memory**, journey state is lost when:
- Sessions end
- Context windows fill up
- Architects change
- Conversations get long and memory degrades

**With file-based memory**, journey state persists across:
- Session breaks
- Architect handoffs
- Multiple iterations of stressor analysis
- Months-long engagements

## What You Need to Do

### When Starting a Journey

1. Execute `/journey start`
2. The skill will create `docs/journey/journey-state.md` with:
   - Aspiration
   - Terrain type
   - Recommended route
   - First move

### As You Progress

**After EVERY journey command**, the state file is updated with:
- What was completed
- What was learned
- What comes next
- Any decisions made

**Key commands that update journey state:**
- `/journey start` — creates initial state
- `/journey where` — updates current position
- `/journey iterate` — logs iteration decision and rationale
- `/journey review` — logs health assessment
- `/journey cadence` — creates ongoing schedule

**Skills within the journey that update state:**
- `/discover *` — logs discoveries, updates confidence
- `/stressor analyze` — logs impact scores, adds to iteration history
- `/stressor residues` — logs residuals identified
- `/adr create` — adds to artifacts list
- `/solution-doc *` — adds to artifacts list
- `/design-review` — logs findings

### When Resuming a Journey

**ALWAYS** start by reading `docs/journey/journey-state.md` to understand:
- Where you are
- What's been done
- What comes next
- What assumptions are being carried
- What gaps exist

Then execute `/journey where` to confirm position and get recommendations.

## File Structure

```
docs/journey/
├── journey-state.md                    # Single source of truth
├── stressor-iteration-history.md       # Detailed iteration log
├── decisions-log.md                    # Lightweight decision log
├── assumptions-register.md             # Assumptions being carried
└── cadence-schedule.md                 # Ongoing rhythm (for live systems)
```

### `journey-state.md` Contains:

1. **Aspiration** — what this system should achieve
2. **Current Position** — where we are, what's complete, what's next
3. **Journey History** — chronological log of commands and key decisions
4. **Iteration Log** — stressor analysis iterations with impact scores
5. **Artifacts Produced** — checklist of outputs with links
6. **Known Gaps & Assumptions** — what we don't know, what we're assuming
7. **Team Context** — constraints, stakeholders, political landscape
8. **Health Assessment** — journey health, risks, corrective actions
9. **Next Session Prep** — what to read when resuming

## Template Available

Use `templates/journey-state-template.md` as a starting point. The template includes:
- Complete structure with all sections
- Guidance on what goes in each section
- Examples of well-formed entries

## Benefits

### For Architects

- **Never lose context** — pick up exactly where you left off
- **Learn from history** — see what worked, what didn't
- **Make informed decisions** — have full iteration history when deciding to proceed/iterate
- **Understand terrain** — know what assumptions you're carrying
- **Audit trail** — justify decisions with documented rationale

### For Teams

- **Seamless handoffs** — new architects can understand the journey instantly
- **Shared context** — everyone sees the same journey state
- **Learning** — journey files become learning material for capability building
- **Governance** — documented trail of architectural thinking

### For Organisations

- **Repeatable process** — journey structure is explicit and followable
- **Quality assurance** — health checks and corrective actions are tracked
- **Knowledge retention** — architectural knowledge survives architect changes
- **Compliance** — audit trail of decisions and their rationale

## Best Practices

### 1. Update Early and Often

Don't wait until "something significant" happens. Update after every command execution. Small, frequent updates are easier than large, retrospective ones.

### 2. Be Honest About Gaps and Assumptions

The gaps and assumptions section is your safety net. If you're carrying an assumption, write it down. If there's something you don't know, admit it. These sections protect you from unknown unknowns becoming known catastrophes.

### 3. Use the Iteration Log Religiously

Every stressor analysis iteration should be logged with:
- Impact scores (with comparison to previous iteration)
- Residuals identified
- Decision rationale (iterate/proceed/accept)

This log is what lets you make informed decisions about when to stop iterating.

### 4. Link Artifacts

Don't just say "HLD exists" — link to it. The journey state file is a map of all journey outputs.

### 5. Reflect, Don't Just Report

Use the "Notes & Reflections" section to capture insights, patterns, and open questions. This is where capability building happens — the reflection is what transfers the thinking.

### 6. Prepare for Resumption

Fill in the "Next Session Prep" section before ending a session. Your future self (or another architect) will thank you.

## Migration Guide

### If You Have an In-Flight Journey

1. Execute `/journey where` — this will create `journey-state.md` retrospectively
2. Review the generated state for accuracy
3. Fill in any gaps (especially iteration history if you've done stressor analysis)
4. From now on, the state file is the source of truth

### If Journey State Exists But Is Stale

1. Read the existing `journey-state.md`
2. Execute `/journey where` to update it
3. Correct any drift between file and reality
4. Continue with updated state

## Integration with CLAUDE.md

The requirements are now documented in `CLAUDE.md` so that:
- Every Claude Code session sees the requirements
- The memory persistence instructions are always active
- New architects working in the codebase understand the pattern

**When executing `/journey` commands, Claude Code will automatically:**
- Read existing journey state before making recommendations
- Update journey state after every command
- Create missing state files when needed
- Maintain the full journey history

## Questions?

Journey memory persistence is a new pattern. If you encounter issues:
1. Check that `docs/journey/` directory exists
2. Verify `journey-state.md` is being updated after commands
3. Ensure the template structure is being followed
4. Report gaps or ambiguities so the pattern can evolve

The pattern will improve based on real-world usage. Your feedback matters.
