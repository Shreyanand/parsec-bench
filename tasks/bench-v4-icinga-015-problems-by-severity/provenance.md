# bench-v4-icinga-015-problems-by-severity

## What it measures

Aggregation and prioritisation from a single call — the shape 18 real icinga-only
trajectories take, most of them one or two calls with a formatted summary as the
answer. Three counts, a prioritisation judgment, and reading the suppression fields.

## Why the counts need the proximity matcher and not substrings

The seeded check outputs contain the numbers 14, 6, 3, 1, 3 and 19. A bare `"3"` as a
substring assertion would match inside three different outputs by coincidence, which is
exactly the trap CLAUDE.md records from `bench-aap2-002`. Each count therefore uses
`nouns` proximity: the digit has to sit within five tokens of `critical`, `warning` or
`unknown`. Every value was checked against the seed's own literals before being
accepted.

## The prioritisation fact

`worst-first` requires naming the 14-subject east-1 backlog. That is not a matter of
taste: it is the largest CRITICAL by more than double, and stuck AnarchySubjects block
provisions. Naming a WARNING or the suppressed UNKNOWN first is a prioritisation error
the scenario is built to catch.

`suppressed-noted` requires reading `acknowledgement` and `downtime_depth`. Without it
an agent can report seven equally urgent problems, which is a worse answer that would
otherwise score the same.

## Grounding

`get_problems` is one of the five actions `vendor/parsec/src/tools/icinga.py:97-104`
accepts, and it takes no arguments — 17 real calls in the corpus use it that way. The
service names, display names and host names follow the shapes the trajectories show
(`[Anarchy] Stuck AnarchySubjects`, `[Reporting] Pod pools status`, `pod-pools-status`).

## Weighting

`0.2 / 0.8`. One call with no arguments — the trajectory is as close to free as this
suite gets, so almost all the weight sits on the reading.

## Invented

All seven problem rows, every count in their outputs, and the four host names.
**Nothing comes from the gitignored trace export.**
