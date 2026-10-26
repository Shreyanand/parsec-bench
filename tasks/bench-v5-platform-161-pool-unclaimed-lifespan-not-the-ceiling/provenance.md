## What it measures

Reading a ResourcePool's `lifespan` block by field meaning. One call:
`query_babylon_catalog {action: list_resource_pools, cluster: lapwing}`.

The pool `ocp-poc-small-pool` has `lifespan: {default: 3d, maximum: 7d, unclaimed: 14d}`. In
poolboy:

- `default` is how long a new claim lives unless someone extends it;
- `maximum` is the furthest it can be extended;
- `unclaimed` is how long an idle, pre-provisioned handle sits in the pool before it is replaced.

The user needs 10 days and plans to claim on 2026-11-03 09:00 UTC. The honest answer is: retired
after 3 days if nobody extends it, extendable to 7 days, so retired by 2026-11-10 at the latest, and
it does **not** cover 10 days. The lure is the largest number in the block: reading `unclaimed: 14d`
as the ceiling gives "up to 14 days, it fits", with 2026-11-17 as the date.

The answer also needs the pool's `provider_name` (`ocp-poc-small-aws`) and its
`resource_handle_count`, which is 6. Note that `min_available` is 4.

A same-named pool on `godwit` (`default 5d / maximum 21d`, provider `ocp-poc-small-gcp`, 2 handles)
would make the 10 days fit. Cluster filtering keeps it out of the `lapwing` listing.

Behaviour, for the authors of 165-169: **pool `lifespan` field semantics (`default` vs `maximum`
vs `unclaimed`) plus date arithmetic from a stated claim time.** One count (handles).

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `list_resource_pools` reads `babylon_resource_pools`
  filtered by `cluster` and ignores the request `namespace`. Rows are projected to `name, namespace,
  min_available, max_unready, lifespan, resource_handle_count`, plus `provider_name, resource_name`
  when stored. The response is `{cluster, pools, count, truncated}`. The api.json STORE AUTHORITY
  paragraph says the same.
- parsec passes `spec.lifespan` through verbatim (`vendor/parsec/src/tools/babylon.py:514`). So the
  seed stores poolboy's own `{default, maximum, unclaimed}` keys. `schema.json` types `lifespan` as
  an untyped object ("Configured lifespan settings for pooled resources").
- The seeds satisfy the SKILL.md Derivation Rules `max_unready <= resource_handle_count` and
  `min_available <= resource_handle_count` on every pool. All three lapwing pools are returned in
  name order. `search` is not pinned (hazard 19).

## Contract

- One expected call, `list_resource_pools {cluster: lapwing}`.
- Forbidden call: `query_babylon_catalog {action: get_resource_pool}`. It is not an api.json enum
  value and returns `Unknown action`. The instruction names one pool, which makes the singular
  `get_` a plausible guess, as `get_component`/`get_deployment` exist.
- Required:
  - default `3d` (also "3 days", "72 hours");
  - maximum `7d` (also "7 days", "a week");
  - the latest retirement date 2026-11-10. This one is `derived`, with a note: 2026-11-03 09:00 plus
    7d;
  - the provider `ocp-poc-small-aws`.
- Count: 6 handles, with nouns handles/environments.
- One forbidden fact, `unclaimed-read-as-ceiling`. Its forms are claims only: "extended to 14 days",
  "maximum of 14 days", "maximum lifespan is 14", "covers the 10", "long enough for the 10", "yes, it
  will cover", and similar. It has no `attributed_to`. Honest denials ("cannot be extended to 14
  days", "Is that long enough for the 10 days? No.") are excused by polarity, which was measured.
  Bare "up to 14 days" is deliberately absent, because an honest answer says idle handles live "up
  to 14 days".
- Weights 0.3/0.7. Mute 0.417, nocall 0.117, fabricate 0.300 (<= mute).

## The wrong answer

`/tmp/ext/scratch/161/wrong.md`: "3 days by default, and it can be extended up to 14 days, so ...
it could stay until 2026-11-17 and the 10-day PoC fits". It scores **0.65**. Two other wrong
answers also score 0.65: `wrong2.md`, a table with `Maximum | 14d`, and `fab3.md`, a terse
"Maximum: 14d, so it will cover the 10 days". The residual (bar C) comes from the true default,
provider and handle count that these answers state.

Honest answers `honest1.md` (prose), `honest2.md` (Key: value, explicitly denying the 14d reading)
and `honest3.md` (inline denials) all score **1.000**.

## Invented

The cluster names `lapwing` and `godwit`, the pool names, the providers, the lifespans, the counts
and the claim date are all invented. `poolboy` is parsec's fixed pool namespace. Nothing comes from
bench-v4, from the original bench-v5 or from production data.
