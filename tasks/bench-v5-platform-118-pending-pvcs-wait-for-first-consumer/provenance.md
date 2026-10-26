# bench-v5-platform-118-pending-pvcs-wait-for-first-consumer

## What it measures

Whether the agent will return a non-finding on OpenShift Virtualization storage. A dashboard
shows three Pending PVCs. The honest answer comes from three reads, and only the three
together establish it:
- `list_pvcs`: all three are Pending with the event "WaitForFirstConsumer: waiting for first
  consumer to be created before binding".
- `list_storage_classes`: their class `lvms-nvme-thin` (topolvm.io, the default) has
  `binding_mode: WaitForFirstConsumer`.
- `list_vms`: the three VMs that would consume them are Stopped (`VMINotExists`).

Local LVM volumes bind on the node where the consumer is scheduled, so Pending is the
designed state until the VMs start. Deleting and recreating the claims (the instruction
offers it) would change nothing.

**Kind: negative.** The correct answer is "nothing is wrong, take no action".

## Grounding

- platform SKILL.md "/query_ocpv_cluster": cluster resolution from `namespace` via
  `ocpv_namespaces` when `cluster` is omitted. `list_pvcs` reads `ocpv_pvcs` by cluster +
  namespace, returns `events` when stored, and `pending_count` = Pending rows returned.
  `list_storage_classes` reads `ocpv_storage_classes` by cluster, unfiltered, and `count` is a
  true total (api.json `OcpvStorageClassListResult`). `list_vms` reads `ocpv_vms` by cluster +
  namespace, with `condition` when stored.
- Seed: `ocpv_namespaces` 2 (target + a neighbour), `ocpv_pvcs` 4 (3 Pending + 1 Bound in the
  neighbour namespace, which list_pvcs on the target never returns), `ocpv_storage_classes` 2,
  `ocpv_vms` 3.

## Contract

- tool_calls (0.3), unordered-subset (sibling reads): `list_pvcs` {namespace},
  `list_storage_classes`, `list_vms` {namespace}. `cluster` is unpinned (passing
  `ocpv-cobalt` or relying on discovery both work).
- answer (0.7): required `wffc`, `vms-stopped`, `expected` (derived). (No count: the instruction already says "three", so a count would be echo-satisfiable.)
  Forbidden `storage-broken` (capacity or provisioner failure) and `recreate` (recommending
  deletion). attributed_to is specific refutations only ("nothing is broken", "is not full",
  "should not be deleted", "would change nothing", ...).
- Probe: "The storage is full, not broken, so delete the claims rather than wait." hits both
  forbidden facts. "not" and "rather than" excuse nothing.

## The wrong answer

"The 3 PVCs are Pending because the lvms-nvme-thin provisioner has failed ... out of
capacity. Yes, delete the pending PVCs and recreate them..." scores reward **0.30**: three
required facts missed, both forbidden facts hit. The golden answer scores 1.0. Mute floor
(validate.py): answer 0.40, reward 0.58 with golden calls.

## Invented

Every literal is invented: cluster `ocpv-cobalt`, namespaces `sandbox-r7tbm-*` and
`sandbox-f4hxk-*`, the claim, VM and class names and sizes. Nothing comes from bench-v4 or
from production data.

## Floor exemption

Weak discriminator, flagged in the baseline report (controller ruling 2026-10-13, in place of the owner-approved required fact and reweight; flagged to the owner): the contract grades three required facts and two forbidden facts at weights 0.3/0.7, so an agent that makes the golden calls and asserts nothing keeps the two forbidden facts and collects 0.3 + 0.7 x 2/5 = 0.580 (mute), and one that makes no call collects 0.280 (nocall), above the 0.50 / 0.25 caps; the fabricate probe scores 0.300 (max 0.440, below mute). A reweight to 0.25/0.75 alone gives 0.550 / 0.300 and still fails. The approved new required fact for the ask 'should we?' (no-recreate) was tried and lost the fact on most fresh honest answers: after eight rounds and 132 forms, the last blind batch of 8 honest answers lost it on 6 of 8 (1.000 -> 0.875; 24 of 56 blind answers lost it across the rounds), because it grades a free-form 'no'. So it was not added.
