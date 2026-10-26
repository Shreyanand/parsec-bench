# bench-v4-platform-019-anarchysubject-state

## What it measures

A two-call Babylon read where both calls need the `cluster` argument, and the second's
`name` comes from the first's result. It is the positive counterpart to
`bench-v4-platform-021`: here `cluster` is supplied and the calls succeed, there its
absence is the trap.

## Why `expected_instances` is a count and not a literal

The component record carries `expected_instances` as a **list** of five instance names,
not as a number. So the count has to be derived from the result rather than copied out of
it, which is a genuinely different operation from reading `cloud_provider` off the same
record.

## A second store-versus-response constraint

`BabylonComponentDetail.expected_instances` is an array of **objects** in
`harness-skills/parsec-platform/schema.json`, not of strings. The first draft seeded five
plain instance names, which reads naturally and is what a response would plausibly carry;
the offline gate rejected every row with `is not of type 'object'`. Each entry is now
`{name, count, flavor}`. Same lesson as `bench-v4-platform-007`'s `matches`: read the
generated schema, never the tracked spec, when writing a seed.

## The second subject is not decoration

The seed holds a second AnarchySubject in `started`/`started` and healthy. An agent that
lists subjects and reports the first or the healthiest gets `current-state` wrong.

## Grounding

`list_anarchy_subjects` and `get_component` are two of the twelve actions
`sim-specs/platform/openapi.json` declares for `query_babylon_catalog`; 10 real
`list_anarchy_subjects` calls and 5 `get_component` calls appear in the trajectories.
`vendor/parsec/src/tools/babylon.py:693` is why `cluster` matters — without it, or a
`sandbox_comment` to resolve from, the tool refuses.

The generated `schema.json` requires `healthy` as `['boolean', 'null']` and both
`instance_vars` and `definition` as objects; the seed matches. `governor`,
`current_state` and `desired_state` are all required fields on
`BabylonAnarchySubject`.

## Weighting

`0.3 / 0.7`. The GUID and cluster are handed over, but the governor name has to come out
of the first call's result for the second call to be possible, which is a real dependency
rather than two independent lookups.

## Invented

The GUID `bl42c`, both AnarchySubjects, the component definition, the five instance names
and job id `90420`. **Nothing comes from the gitignored trace export.**
