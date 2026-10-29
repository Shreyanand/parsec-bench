## What it measures

Scoping `get_workshop` by `namespace` when the workshop name is not unique on the cluster. Two calls
in a dependency chain on `dunlin`:

1. `list_workshops {cluster: dunlin, namespace: user-tfolau-redhat-com}` maps the attendee code
   `h6pvd` (`workshop_id`) to the workshop name `ocp-argo-sync-course`. The listing also holds a
   `-dryrun` sibling (q3zbm).
2. `get_workshop {cluster: dunlin, namespace: user-tfolau-redhat-com, name: ocp-argo-sync-course}`
   returns the per-seat `resource_claims`. 2 of 5 seats failed: `c2rlw`, provision job 5813207 on
   west, and `f9mpk`, job 5813244 on west.

A colleague's clone with the **same name** sits in `user-aokonkwo-redhat-com` on the same cluster:
code v9tsl, 1 of 4 failed, `x8kfv`, job 5806638. The instruction warns about it.

Without `namespace`, parsec's `_get_workshop` lists Workshops cluster-wide and takes the first name
match (`vendor/parsec/src/tools/babylon.py:1212-1222`). Kubernetes lists sort by namespace, so the
colleague's namespace was chosen to sort first, and an unscoped call reads her copy.
`list_workshops` alone cannot answer, because it does not project `resource_claims`.

Behaviour, for the authors of 165-169: **workshop_id → name via `list_workshops`, then
namespace-scoped `get_workshop` against a same-named clone; per-seat failure GUIDs and provision
jobs.** One count (failed seats).

## Grounding

- platform SKILL.md `/query_babylon_catalog`, Store reads, `get_workshop`: it reads `babylon_workshops`
  filtered by `cluster`, and will "match by `name`; if `namespace` is provided, also require exact
  `namespace`". `list_workshops` requires `namespace` and projects exactly `name, namespace,
  catalog_item, workshop_id, display_name, description, open_registration, lifespan,
  provision_count, user_count, user_assignments_count, resource_claims_count`. `get_workshop` returns
  `cluster, name, namespace, display_name, catalog_item, workshop_id, requester, multiworkshop,
  lifespan, provision_count, user_count, resource_claims`.
- `requester` is not seeded (it is optional in `schema.json`), so it is omitted from the golden
  result. parsec returns `""` for a missing annotation (`babylon.py:1264`), and the replay compares
  only the golden keys.
- The `resource_claims` entries follow v4-040's verbatim shape. A failed seat carries `state:
  failed` and `tower_jobs.provision {controller: west, job_id, status: failed}`. `west` is a
  `QueryAap2Request.controller` enum value.
- The store key `babylon_workshop_id` includes the namespace, so the two same-named rows are
  distinct (schema `x-primary-key`).

## Contract

- Calls, `ordered-subsequence`: `list_workshops` pins `cluster` and `namespace`, both from the
  instruction. `get_workshop` pins `cluster`, `namespace` and `name`, with `name` derivable only
  from call 1's result.
- Forbidden call: `get_workshop` with `namespace` absent (`absent_args: ["namespace"]`). The
  instruction states the clone, so an unscoped lookup is a wrong-scope call, not exploration.
- Required: the GUIDs `c2rlw` and `f9mpk`, and the jobs 5813207 and 5813244.
- Count: 2 failed seats, plus pair forms ("2 of 5").
- No forbidden facts: everything true of the clone is a seed literal (hazard 14).
- Weights 0.3/0.7. Mute 0.300, nocall 0.000, fabricate n/a.

## The wrong answer

`/tmp/ext/scratch/163/wrong.md` reads the clone: "One seat failed ... GUID x8kfv ... job 5806638".
It scores **0.30** with the golden calls. With the unscoped `get_workshop` it actually implies
(`list_workshops` followed by `get_workshop` without `namespace`), it scores **0.14**: tool calls 0,
because the forbidden call zeroes the component.

The clone was given four seats so that its "other three seats" does not hand the wrong answer the
count of 2. An earlier draft with three seats scored 0.44.

Honest answers `honest1.md` (prose) and `honest2.md` (Key: value, explicitly naming and excluding
Adaeze's copy) both score **1.000**.

## Invented

The cluster `dunlin`, the namespaces and people, the workshop names, the codes, the GUIDs, the job ids
and the timestamps are all invented. Nothing comes from bench-v4, from the original bench-v5 or from
production data.
