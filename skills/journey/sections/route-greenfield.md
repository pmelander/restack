### Greenfield route

You have an aspiration and a blank canvas. The paths do not exist yet — you
design them, then stress what you designed before anyone builds it. This is the
cheapest terrain to be wrong in and the only one where stressor analysis runs
against a system that can still be reshaped freely.

```
1.  /journey start             establish aspiration, classify terrain
2.  /tech-stack recommend      choose the technology foundation
3.  /adr create                document each technology decision
4.  /solution-doc hld          design the system: actors, paths, intentions
5.  /stressor walk             walk each designed path
6.  /stressor generate         stress-test before a line is written
7.  /stressor analyze          build the impact matrix
8.  /stressor residues         what residuals does the design need?
      |
      +-- ITERATE GATE: /journey iterate --> loop to 5, or proceed
      |
9.  /adr create                document each residual as a decision
10. /cloud design              if cloud-hosted, design the infrastructure
11. /capacity estimate         size the system
12. /design-review complete    validate before building
13. /solution-doc deployment   operational readiness
```

**Sequencing note.** Steps 2-3 before 4 is deliberate: the technology
foundation constrains what actors are even available to you. But hold it
loosely — if the stressor loop at 5-8 produces residuals the chosen stack
cannot express cheaply, that is a signal to reopen the ADR, not to bend the
residual to fit the stack.

**Expected iterations: 2-3.** Greenfield matrices improve fast because you can
add an actor by deciding to. If you are past four iterations and impact is not
falling, the problem is usually the path map, not the residuals — the design has
paths you have not walked.

**The failure mode here** is skipping 5-8 because the design is new and
therefore feels sound. A design nobody has stressed is a set of happy paths.
The whole value of greenfield is that residuals are nearly free at this stage
and cost a rewrite later.

**Where discovery still applies.** Any integration point with an existing system
is brownfield terrain inside a greenfield project. Run `/discover actor` against
each external system you depend on before walking a path that crosses it.
