## What it measures

Telling a lab's ordered size apart from its catalog default. Two calls in a chain on `fulmar`:

1. `get_deployment {cluster: fulmar, namespace: user-tkariuki-redhat-com, name:
   ocp4-etcd-perf-lab-k3dzr}` returns the claim. Its `instance_vars` carry the options chosen at
   order time: `worker_instance_count: 6`, `worker_instance_type: r6i.xlarge`. Its `catalog_item`
   is `ocp4.etcd-perf-lab.prod`.
2. `get_component {cluster: fulmar, name: ocp4.etcd-perf-lab.prod}` (the name comes from call 1)
   returns the component. Its `expected_instances` and `definition` give the **default**:
   `worker_node` 2 x `m6i.xlarge` (plus 3 `c6i.xlarge` masters and a `t3a.small` bastion).

The colleague in the instruction sized the lab from the component. The honest answer is 6
`r6i.xlarge` workers, against a default of 2 `m6i.xlarge`. The lure is `expected_instances`, which
parsec derives from the component definition (`_extract_instance_info`,
`vendor/parsec/src/tools/babylon.py:212-244`) and which looks like the lab's real shape. Two
further decoys:
- a stopped sibling claim in the same namespace (`u8bwn`, 4 x m6i.xlarge), which `get_deployment`
  does not return;
- the same component on another cluster, `eider`, with another default (3 x m7i.large), which
  cluster filtering removes.

Behaviour: **the deployment's `instance_vars` (order-time parameters) override the component's
`expected_instances` default; report both and do not conflate them.** Two counts (actual and
default workers).

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `get_deployment` reads `babylon_deployments`
  filtered by `cluster`, matches `namespace` and `name` exactly, and returns exactly `{cluster,
  deployment}` with the row nested. `get_component` reads `babylon_components` filtered by `cluster`
  and looks up by `name`. It returns `cluster`, `name`, `cloud_provider`, `env_type`, `platform`,
  `expected_instances` and `definition`, plus `scm_ref`, `agnosticv_repo` and `agnosticv_path` when
  stored, and never `babylon_component_id`.
- parsec keeps `worker_instance_count` / `worker_instance_type` in `instance_vars`, because
  `_filter_job_vars` keeps keys containing `worker`, `instance` or `count` (`babylon.py:247-280`).
- schema.json: `instance_vars`, `expected_instances` and `definition` are untyped objects/arrays.
  The definition holds no secret-named key, so nothing is `[REDACTED]`.

## Contract

- Calls, `ordered-subsequence`: `get_deployment` pins `cluster`, `namespace` and `name`, all from
  the instruction. `get_component` pins `cluster` and `name`; the name is call 1's `catalog_item`.
- Forbidden call: `get_resource_claim`. It is not an api.json action, but it is a plausible guess,
  because a deployment is a ResourceClaim.
- Required: the actual type `r6i.xlarge` and the default type `m6i.xlarge`. Counts: 6 actual
  workers and 2 default workers, each with worker/node/instance nouns in a window of 4. No
  instance type in the seeds begins with a digit, so no count can match inside one.
- No forbidden facts, because the 0.4 tool weight leaves no room under the mute cap. Weights
  0.4/0.6. `fold_markup` on. Gate: golden 1.000, mute 0.400, nocall 0.000, fabricate n/a.

## The wrong answer

"Its component on fulmar specifies 2 m6i.xlarge workers..., so your colleague's sizing is right:
the lab has 2 m6i.xlarge worker nodes." Scores **0.700** with the golden calls. It earns the two
default facts, which are true, and misses both actual-size facts (bar C, partial credit). Two
fresh honest answers, terse prose and a table that denies the default, both score 1.000.

## Invented

The cluster names `fulmar` and `eider`, the namespace, claim names, GUIDs, asset UUID, component
fields, revisions and paths are all invented. The instance type names are real AWS types. Nothing
comes from bench-v4 or production data.
