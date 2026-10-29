# bench-v4-platform-020-ocpv-vm-inventory

## What it measures

A three-call OCP-V read where the answer to "why is this machine down" is in the *third*
result rather than the second. An agent that stops after `list_vms` can say the VM is
Stopped but cannot say why. The namespace is supplied by the instruction and reused across
all three calls; it is not discovered, because no tool maps a GUID to a sandbox namespace
(see the 2026-09-14 entry in the edit log).

## Coverage-driven, and stated as such

**This is the only `query_ocpv_cluster` scenario in the suite, and it has zero
corresponding trajectories.** `query_ocpv_cluster` appears nowhere in the 126 scoreable
traces. It exists here because the tool is modelled in `sim-specs/platform/openapi.json`
and the tool-coverage floor requires it to be exercised at least once.

That matters for how any suite-level number is read: this scenario is not evidence about
real workload, and the design document's spread table says the same about `cost` and
`cloud`. Per-shape means are meaningful; the suite mean is not workload-weighted.

## Grounding

`find_namespace`, `list_vms` and `list_pvcs` are three of the eleven actions
`sim-specs/platform/openapi.json` declares for `query_ocpv_cluster`. The
`sandbox-{guid}-{catalog-item}` namespace shape is the one `CLAUDE.md` records as parsec's
own convention, and it is why `platform` groups these four tools as one service: a guid
names the AAP2 job, the AnarchySubject, and this namespace alike.

`OcpvVm` requires `node` and `ip`, and the stopped VM carries the **empty string** for
both. The spec used to declare them `['string', 'null']` and this seed used `null`; both
were wrong. `vendor/parsec/src/tools/ocpv.py:349,351` defaults each to `""`, never null, so
parsec itself never emits a null here — and generation collapses a multi-type union to a
bare string anyway, so a null-valued row could not be stored at all. The spec was corrected
to a plain string on 2026-09-14 and the seed follows it.

**`OcpvVmVolume` has no store table in the bundle at all**, so volumes are seeded inline
on each VM as the generated `OcpvVm.volumes` array of objects, not as their own
collection.

## Weighting

`0.3 / 0.7`. The GUID, cluster and namespace are all given, so the calls are not the
difficulty; the answer needs the right record out of three VMs and then the PVC state from a
third call. The ratio was left unchanged when the namespace stopped being discovered
(2026-09-14), because the `namespace` required fact was removed at the same time -- the
answer side lost the fact that had become free, rather than the tool side gaining weight.

## Invented

The GUID `tk8vn`, the namespace, all three VMs, all three PVCs, the node names and the
storage class. `ocs-storagecluster-ceph-rbd` is the conventional OpenShift Data Foundation
RBD storage-class name. **Nothing comes from the gitignored trace export.**
