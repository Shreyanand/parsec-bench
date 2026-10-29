# bench-v4-platform-038-anarchy-subject-guid-cross-cluster

Idea from bench-h4_Oct5 038 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. The instruction names the wrong cluster (`south`); carrying it into
`get_component` is the targeted wrong move, and the same-named component seeded on
`south` makes that move return real-looking wrong data rather than an error.

## What it measures

The cluster-withheld variant of `bench-v4-platform-019`. There the cluster is handed
over; here the instruction only offers a teammate's uncertain guess, and the subject is
not on that cluster. Two things have to happen in order:

1. `list_anarchy_subjects` with `guid` and **no** `cluster`, which is the one shape that
   searches every configured cluster (`vendor/parsec/src/tools/babylon.py:679-683`,
   `_search_all_clusters_for_guid` at `:743`; `harness-skills/parsec-platform/SKILL.md`
   "Cluster resolution", the all-clusters list for `list_anarchy_subjects` with `guid`).
   Only this call finds the subject, on `north`. A guid-scoped call on `south` returns an
   empty list, which is a legitimate first step and is not penalised.
2. `get_component` on the **resolved** cluster. `get_component` has no all-clusters branch
   (`babylon.py:691-697` falls through to the "Could not determine which Babylon cluster"
   error; SKILL.md lists `cluster` or `sandbox_comment` as its only resolutions), so the
   agent has to carry `north` forward explicitly. The governor name `rhel9-hana-lab` comes
   from the first result.

## Seed design

- `babylon_anarchy_subjects`: the target `rhel9-hana-lab.kx8vn` on `north`
  (`stop-failed` / `stopped`, unhealthy, stop job 71584 on controller prod1), and a
  same-governor decoy `rhel9-hana-lab.wr2pd` on `south` (`started` / `started`, healthy).
  The decoy's name does not contain `kx8vn`, so the SKILL.md guid match
  (`instance_vars.guid = guid` or `name` contains `guid`) cannot return it; it is reachable
  only by an unfiltered listing of `south`, which is the wrong-record trap. None of the
  decoy's values satisfy any required form.
- `babylon_components`: `rhel9-hana-lab` on both clusters. `north`: `azure`, three
  expected instances (bastion, control_plane, worker, count 1 each). `south`: `ec2`, two
  (bastion, node). `expected_instances` follows parsec's role extraction shape
  `{purpose, instance_type, count}` (`babylon.py:185-195`, `_extract_instances_from_roles`),
  and each `definition` carries the role variables that would produce it.
- The subject's `instance_vars` deliberately carry no `cloud_provider`, so the provider is
  only obtainable from the north component -- one call is not enough for it.
- Each instance has count 1 so "how many instances" has one reading (entries = total).

## Golden results

`list_anarchy_subjects` is written in the live 2026-10-06 freeze's envelope,
`{subjects, count, truncated, errors}` -- no top-level `cluster` or `namespaces_searched`
(CLAUDE.md records this wart for `bench-v4-platform-019`). The resolved cluster is
therefore taken from the subject row's own stored `cluster` field, which is what
`check_expected_calls_derivable` sees. **Live replay (2026-10-08):** the live row carries
`cluster: "north"` (plus the synthetic `babylon_anarchy_subject_id`), the envelope is as
written, and the replay verdict is `ok`. The dependency holds.

## Contract

- Expected call 1 pins `guid` and carries `absent_args: ["cluster"]`, so a guid call that
  guessed a cluster does not earn the credit reserved for the all-clusters search.
- Expected call 2 pins `cluster: north` and `name: rhel9-hana-lab`.
- One forbidden call: `get_component` on `south` (the hinted cluster). No blanket list.
  Cost, measured: an agent that fetches both clusters' components and answers correctly
  scores 0.600 (tool 0) -- the forbidden call is the price of the carry-over it represents.
- Required: cluster `north`, current `stop-failed` (also `stop failed`, `stop_failed`,
  `stopfailed`, `failed to stop`), desired `stopped`, provider `azure`; `counts`: 3
  instances (nouns include `node`/`nodes`, window 10). No forbidden answer facts: every wrong reading
  (decoy subject, decoy component, hinted cluster) is a seed literal, which hazard 14
  forbids as a `none_of` form, and an assertion form ("on south") collides with the honest
  "not on south". Without forbidden facts a fabricator stating no true literal scores
  exactly mute.

## Weighting

`0.4 / 0.6` (no forbidden answer fact, so the cap is 0.4). Mute 0.400, nocall 0.000.
At 0.4 the wrong-cluster carry-over agent -- right subject, south component -- scores
0.360, below mute; at 0.3 it would have scored 0.420, above it.

## Measured residuals (S9b bar C)

- **One-call agent.** An agent that reports the cluster and both states but never fetches
  the component scores 0.560. It did half the chain and states three true literals.
- **Format limitation: a stray "stopped".** A fabricator writing "the environment is
  stopped" banks `desired-state` and scores 0.520. verify.py has no proximity matcher
  for string facts. Anchoring the form ("desired state is stopped") would fail honest
  phrasings ("wants to be stopped", a table cell), which breaks bar A. Forbidding a
  bare "is stopped" would contain the required form, which breaks hazard 12. So it is
  left.
- **Format limitation: negation.** "It is on south, not north ... the component uses
  ec2, not azure" scores 0.640. The negated true literals still match by substring, and
  this is unfixable for the same reasons.
- **Empty `cluster` argument.** `absent_args: ["cluster"]` also rejects an explicit
  `cluster: ""` or null on the guid call. Such an agent scores 0.800, which is accepted:
  passing the key is not the documented all-clusters shape.

## Ideas-only check

No literal is shared with the batch scenario or with `bench-v4-platform-019`. Hits from the
batch grep: `azure`, `ec2` and `stopped` occur only in the batch's unrelated default
cloud/cost seeds; they are parsec's cloud-provider vocabulary and an Anarchy state name,
forced by the mechanism.

## Invented

GUIDs `kx8vn`/`wr2pd`, clusters `north`/`south`, governor `rhel9-hana-lab`, both subjects
and components, job ids 71584/71102, namespaces and instance types. Nothing comes from the
gitignored trace export.
