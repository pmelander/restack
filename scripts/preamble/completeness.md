## Completeness — Walk Every Path

Enumeration is cheap here and omission is expensive. The default is full
coverage, and a narrower scope is something the architect chooses explicitly in
a decision brief, never something you quietly assume.

- **Paths:** the happy path is one path. Error paths, retry paths, async paths,
  admin paths, batch paths and the path taken during a partial outage are all
  paths, and they usually fail differently. Walking only the happy path
  produces a matrix that understates vulnerability.
- **Stressors:** generate generously and generate weird. A stressor list that
  contains only plausible stressors is a risk register wearing a costume — it
  enumerates what you already feared. The absurd ones are load-bearing: they
  are how you reach the stressors nobody has thought of yet.
- **Actors:** an actor you left off the matrix has vulnerability zero by
  construction. Missing actors are the most common cause of a matrix that
  cannot be made to improve across iterations.

Genuinely out of scope is work unrelated to the aspiration — a separate
migration, another team's system. Flag that as separate scope. Never use it as
cover for a shortcut inside the current path set.
