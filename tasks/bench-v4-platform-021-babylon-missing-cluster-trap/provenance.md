# bench-v4-platform-021-babylon-missing-cluster-trap

## What it measures

Supplying the `cluster` disambiguator that `query_babylon_catalog` requires. The observed
agent omitted it **twice, independently**, once on `get_component` and once on
`search_catalog`, and got back:

> Could not determine which Babylon cluster to query. Either specify 'cluster' directly,
> or pass 'sandbox_comment' (from query_aws_account_db) to auto-resolve. Configured
> clusters: ['east', 'babydev', 'integration', 'partner0', 'west', 'partner1']

That is `vendor/parsec/src/tools/babylon.py:691-696` verbatim. The instruction states the
cluster and says outright that a lookup has to name one, so this is not a knowledge test
— it measures whether the agent passes an argument it was handed.

## The only scenario needing `absent_args`

This is the one trap in the suite whose wrong move is an **omission** rather than a wrong
value, so it is the only one that needs the `absent_args` predicate added for `bench/v4`.
Both forbidden entries list `cluster` **and** `sandbox_comment`, and either one being
present means the entry does not match — because `babylon.py:691` accepts either as a way
to resolve the cluster, so an agent that used `sandbox_comment` has disambiguated
correctly and must not be penalised.

`search_catalog` is included alongside `get_component` because the real agent's first
omission was on `search_catalog`, and an agent that reaches for a search before a direct
lookup would repeat it there.

## Weighting

`0.4 / 0.6`, the highest tool weight in the suite. The call *is* the task: one argument
decides whether the tool answers at all, and the three answer facts are a direct read of
the record it returns. It stays inside the floor maxima because the contract has no
forbidden answer fact — with one, a `0.4` tool weight would breach, which is the headroom
trade `bench-v4-platform-005` and `-018` both ran into.

## Invented

The component `ocp4-workload-adv-dev-suite`, its lifespans, its agnosticv path and the
bastion instance. **Nothing comes from the gitignored trace export** — the error message
above is quoted from parsec's source, not from a trace.
