# bench-v4-platform-042-deployment-via-resource-claim

Idea from bench-h4_Oct5 042 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. The deployment behind an AnarchySubject is the ResourceClaim the
subject's `resource_claim` field names, not a ResourceClaim at the subject's own
name/namespace. The store holds a healthy ResourceClaim at exactly those wrong
coordinates, so the shortcut returns plausible wrong data rather than a loud
not-found.

## What it measures

A two-hop chain on `query_babylon_catalog`, and the first use of `get_deployment` in
the suite:

1. `list_anarchy_subjects` with `cluster: west` and `guid: tq4hm`
   (`vendor/parsec/src/tools/babylon.py:710-713` dispatch; guid filter at
   `:1056-1059`, `instance_vars.guid == guid` or the guid inside the name). The
   subject row carries `resource_claim: {name, namespace}`, which parsec builds from
   the poolboy `resource-claim-name`/`resource-claim-namespace` annotations
   (`babylon.py:474-478`). It is declared inline in `sim-specs/platform` because an
   earlier freeze flattened it to a reference string and lost the namespace half
   (CLAUDE.md, "A re-freeze can change simulated tool BEHAVIOUR").
2. `get_deployment` with the **claim's** `name` and `namespace`
   (`babylon.py:708-709`, `_get_deployment` at `:977-995`, a `k8s_get_resource` of
   one ResourceClaim by namespace and name). Both are required
   (`babylon.py:979-980`); SKILL.md `/query_babylon_catalog` "Store reads by
   action" reads `babylon_deployments`, filters by `cluster`, then exact-matches
   `namespace` and `name`.

The subject's name (`ansible-lightspeed-lab.tq4hm`, governor.guid) and the claim's
(`ansible-lightspeed-lab-tq4hm`) differ by one character, and the namespaces differ
entirely (`babylon-anarchy-ansible-lightspeed-lab` vs `user-rortiz-redhat-com`).
Neither claim coordinate appears in the instruction; both come only from the first
result, so `check_expected_calls_derivable` passes on derivation, not on a hint. The
instruction does say the deployment is "the ResourceClaim that actually backs that
subject", which names the concept without naming the field or its values.

## Seed design

- `babylon_anarchy_subjects`: one row on `west`, `current_state: provisioning`,
  `desired_state: started`, **`healthy: true`** (parsec reads the subject's
  `healthy` from its own vars, `babylon.py:471`, independent of the ResourceClaim's
  status). The subject alone therefore looks fine, so an agent stopping at the first
  call has no true health fact to report.
- `babylon_deployments`:
  - the real deployment, `ansible-lightspeed-lab-tq4hm` in `user-rortiz-redhat-com`:
    `healthy: false`, `ready: false`, `state: provisioning`, catalog item
    `ansible-lightspeed-lab.prod` in `babylon-catalog-prod`, asset UUID
    `c41e7b2a-5d93-4f08-b6a1-7e2d90f3c58d`.
  - the decoy, at the subject's own coordinates (`ansible-lightspeed-lab.tq4hm` in
    `babylon-anarchy-ansible-lightspeed-lab`): `healthy: true`, `ready: true`,
    `state: started`, catalog item `ansible-lightspeed-lab.event` in
    `babylon-catalog-event`, asset UUID `8d0f3e61-…`. A stale claim from an earlier
    event order, in effect. None of its values satisfies a required form.
  - both carry `babylon_deployment_id` and `cluster`. `catalog_namespace` values are
    parsec's own `CATALOG_NAMESPACES` (`babylon.py:31`); `babylon-catalog-prod` and the
    cluster name `west` (parsec `config/config.yaml:80`, commented example, the spec's cluster enum) also
    occur in the batch's directory, forced by parsec rather than copied.
- `get_deployment` with the claim name in the subject's namespace, or the subject's
  name in the claim's namespace, matches no row and returns the SKILL.md in-band
  not-found.

## Golden results

`list_anarchy_subjects` uses the live envelope `{subjects, count, truncated, errors}`
(no top-level `cluster`; CLAUDE.md records this for `bench-v4-platform-019`), each row
with its stored `cluster` and without the synthetic `babylon_anarchy_subject_id`, as
in 019 and 038. `get_deployment` returns `BabylonDeploymentDetail`,
`{cluster, deployment}` (`babylon.py:994-995`), the deployment being the full stored
row minus `babylon_deployment_id`. **Live replay (2026-10-08):** the live simulation returns
the `BabylonDeploymentDetail` row **flat**, with no `{cluster, deployment}` envelope. It
follows SKILL.md's "one `BabylonDeploymentDetail`" literally, so `cluster` is a field of the
row itself. The golden result is now that flat row, minus `babylon_deployment_id`. The
subject's own coordinates (`babylon-anarchy-ansible-lightspeed-lab` /
`ansible-lightspeed-lab.tq4hm`) return the healthy decoy deployment
(`ansible-lightspeed-lab.event`, healthy/ready true), as designed. The live
`list_anarchy_subjects` row carries `resource_claim` as an object with `name` and
`namespace`.

## Contract

- Expected calls (ordered subsequence): the two above, pinning only identifiers.
- Forbidden calls (the two targeted traps, not a blanket list): `get_deployment` with
  `name: ansible-lightspeed-lab.tq4hm` (the subject's own name, any namespace), and
  with `namespace: babylon-anarchy-ansible-lightspeed-lab` (the subject's own
  namespace, any name). Either zeroes `tool_calls`, including for an agent that then
  recovers and makes the right call (measured 0.700 with an honest answer).
- Required, all only obtainable from the claim-backed deployment:
  - `deployment-not-healthy` and `deployment-not-ready` (derived; forms are the
    negations and flag notations a correct answer uses: `not healthy`, `unhealthy`,
    `healthy: false`, `healthy=false`, `"healthy": false`, table cells `healthy |
    false`, `Healthy? No`, `neither healthy nor ready`, `healthy and ready are both
    false`, …). None is satisfied by the subject's `healthy: true` or the decoy's
    healthy/ready reading.
  - `catalog-item` `ansible-lightspeed-lab.prod` (subject shows only the governor
    `ansible-lightspeed-lab`; decoy `.event`).
  - `asset-uuid` `c41e7b2a-5d93-4f08-b6a1-7e2d90f3c58d`.
- **Departure from the brief:** the brief lists "deployment name" as a fact. It is not
  graded, because the claim name is in the *first* call's result: an agent that stops
  at `list_anarchy_subjects` and declares the lab healthy would bank it, and then every
  fabrication phrasing the forbidden list misses would beat mute (common brief, "No
  required fact may be earnable by the agent the trap targets"). The instruction does
  not ask for the name either.
- Forbidden answer fact `deployment-declared-healthy`: the decoy reading, anchored to
  the deployment/claim or the `-tq4hm` claim name, an affirmative "yes, healthy", or
  a true `ready` flag value. Bare `healthy: true` is not forbidden, since the subject
  honestly carries it. `attributed_to` excuses a sentence containing `healthy?` or `ready?` (a question about the flag), conditional/remediation sentences
  (`once`, `until`, `when`, `if`, `unless`, `would`, `should`, `wait`, `after`,
  `expected to`) and any sentence containing `false` (because "the deployment is
  healthy: false" contains "deployment is healthy").

## Weighting

`0.3 / 0.7`. A forbidden answer fact caps tool weight at 0.35; at 0.3 the floors are
mute 0.440, nocall 0.140, fabricate 0.300 (four required + one forbidden: 0.3 +
0.7·1/5). The chain is a real achievement (the second call's two identifiers must be
read off the first result, against a tempting shortcut), so the tool weight sits near
the cap rather than at 0.2.

## Measured residuals (S9b)

- A fabricator whose healthy claim carries an excused word ("…healthy and ready, and
  the report is false") or no anchored form ("It looks fine: healthy, ready") ties
  mute at 0.440; it never exceeds it, since no required fact is earnable without the
  deployment row.
- An answer stating a true graded literal (the asset UUID or catalog item) while also
  declaring the deployment healthy in an unanchored phrasing scores above mute:
  partial credit under acceptance bar C.
