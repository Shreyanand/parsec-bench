## What it measures

The deployment's health covers one component, and the lab has two. The user's lab, GUID `f3nlx` on `merlin`, is a two-component bundle.

- `list_deployments` returns its ResourceClaim `rhoai-gpu-bundle-f3nlx` as `healthy: true, ready: true, state: started`.
- That summary comes only from the claim's first resource, the base environment.
- `list_anarchy_subjects` for the GUID shows a second subject, `rhoai-gpu-bundle-gpu-workers.f3nlx`, in `current_state: provision-failed` with `healthy: false`. Its `tower_jobs.provision` is job 5562091 on west.

The rules this rests on, quoted:

> api.json `/query_babylon_catalog` description: "`list_deployments` / `get_deployment` — what *is* deployed: ResourceClaims with sandbox account mappings. Both read only the claim's **first** resource, so a multi-component item's secondary failures are invisible here."
>
> platform SKILL.md, Derivation Rules: "`BabylonDeployment.current_state` is copied from the first embedded `BabylonAnarchySubject` when present." (and the same for `desired_state`)

The seeded deployment row is consistent with that: its `current_state`/`desired_state` (started/started) and `healthy`/`ready` are the base subject's values.

## Grounding

- `list_deployments` reads `babylon_deployments`, filtered by `cluster`, then by the required `namespace`. `guid` is an exact match on `provision_data.guid`, "falling back to `instance_vars.guid`". The schema has no `provision_data`, so the rows carry `instance_vars.guid`. Envelope: `{cluster, namespace, deployments, count, truncated}`.
- `list_anarchy_subjects`: with a guid, a row matches when `instance_vars.guid` equals it or the name contains it. Both target subjects carry `instance_vars.guid: f3nlx`.
- `cluster` is a free request string. Every row carries `cluster: merlin`, and every deployment carries `namespace`.
- validate.py WARN, justified: `all (cluster-wide)` is the documented `namespaces_searched` literal.
- leakage.py WARN, justified: `provision-failed` is a real Anarchy lifecycle state, part of the shared vocabulary. No identifier is shared, and the task is clean.

## Contract

- Calls, `unordered-subset`: `list_deployments {cluster, namespace}` and `list_anarchy_subjects {}` (only `action`; it pinned `cluster` before 2026-10-25). The GUID is in the instruction, so neither depends on the other; a cluster-wide listing and the all-clusters GUID search both count.
- Required: the failed component (`gpu-workers`), its `provision-failed` state, and job 5562091.
- Count: 2 subjects or components.
- Forbidden fact `all-healthy`: "everything is healthy", "lab is healthy", and similar. The excuses are specific attributions of the claim's self-report ("reports itself", "reports healthy", "portal shows", "looks green", ...). Probed:
  - "Everything is healthy, but the summary only reflects the first resource." still hits (0.30).
  - "The deployment reports itself healthy, but ... not fully healthy" is excused.
- Weights 0.3/0.7.

## The wrong answer

`.scratch/probe/131-wrong.md` reads the deployment row and declares "Everything is healthy on the Babylon side". It scores **0.30** with the golden calls: answer 0.

## Invented

The GUIDs, names, UUIDs, job ids, email address, lifespans and the cluster `merlin` are invented. Nothing comes from bench-v4 or production data.
