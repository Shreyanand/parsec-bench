# bench-v4-icinga-016-hosts-most-problems

## What it measures

The same single `get_problems` call as `-015`, and deliberately the **same seeded
fleet**, asked a different question: group by host rather than by severity, and find
the cross-cutting pattern.

Reusing the fleet is intentional. Two scenarios over identical data, scored differently,
isolate the reading from the retrieval — an agent that can enumerate severities but
cannot spot that one check is failing in two regions fails only this one.

## The trap in the question

There is no single worst host: three tie at two problems each. An agent that pattern-matches
"which host has the most" into naming one host is wrong, and `false-single-host` catches
the phrasings that do it. `worst-host-count` asks for the number instead, which is
answerable.

## The pattern fact

`the-pattern` is the judgment the question is really about: the two Babylon hosts carry
the *same two checks*, one per region. It is marked `derived` because it is a synthesis
over seven rows that no seed string states. `repeated-check` requires naming one of the
two repeated checks, which is only possible after grouping by check rather than by host.

## Grounding

`get_problems` takes no arguments and is one of the five actions
`vendor/parsec/src/tools/icinga.py:97-104` accepts. The question mirrors a real
trajectory ("Which hosts currently have the most active Icinga problems, and is there a
common pattern -- same cluster, same check type?"), which is where the three-part shape
of the question comes from.

## Weighting

`0.2 / 0.8`. One argument-free call; everything measured is in the aggregation.

## Invented

The seeded fleet is shared with `-015` and is invented there. **Nothing comes from the
gitignored trace export.**
