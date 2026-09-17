# Handing a batch to the stressor analysis

A batch is an input, not an analysis. `/restack-stressor` owns the walk, the
impact matrix and the residuals; this skill exists because the generation step
in front of them was a prompt and a hope.

## What changes for the walk

Nothing about the walk protocol. A generated statement is walked exactly like
one the room produced: take it to each actor in path order and ask what
happens. Two things are worth saying to the room first:

**Say which track each statement came from.** A team that knows a stressor was
drawn blind argues about it differently from one that assumes an architect
chose it. "Nobody picked this one" removes the question of whether it was
picked for a reason, and that question is the one that turns a walk into a
defence.

**Do not pre-sort by apparent relevance.** The ordering to avoid is aimed
first, uncoupled last - the room's attention is finite and spending it in that
order guarantees the blind draws get the tired end of the session. Shuffle, or
lead with the uncoupled ones while the room is fresh.

## Matrix shape

`/restack-stressor import` expects the first column to be stressors and the
remaining columns to be actors, with binary values. A batch converts directly:
one row per statement, in spec order so a row traces back to its draw.

Keep the spec alongside the matrix. When a row turns out to be the interesting
one, the question that follows is always "what else was in that cell" - and
that is answerable from the specs, by re-running the sampler with the same seed
and reading the neighbouring draws.

## Feeding the next iteration

restack's own warning about iteration two is that you start generating
stressors your existing residuals already handle, and the matrix looks healthy
while teaching nothing. The generator makes that worse, not better, if it is
run with the same taxonomy every time: a combinatorial sampler is very good at
producing the same distribution repeatedly.

Between iterations:

- Put the new residuals into the `aimed` brief and ask for events they do not
  cover. A queue that absorbs load spikes is an actor that can fill, stall,
  reorder or silently drop.
- Retune the taxonomy weights from what the last matrix showed. A dimension
  whose values all scored alike is not discriminating and can lose weight; one
  cell that produced every interesting row should gain some.
- Change the batch seed. Reusing it reproduces the batch exactly, which is
  useful for debugging a render and useless as a second iteration.

## What this skill does not do

It does not decide whether a stressor matters, build the matrix, identify
residuals, or assess a design. It produces statements with a fixed
distribution, and hands them over.
