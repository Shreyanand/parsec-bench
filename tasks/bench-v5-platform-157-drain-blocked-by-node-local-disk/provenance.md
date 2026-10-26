## What it measures

A pre-maintenance check whose answer is a claim's **access mode**, reached by joining a VM's
`node` and `volumes` to the namespace's claims. The user wants to drain worker `tarn-wrk-06` with
an AAP2 template that live-migrated every VM off another worker without anyone noticing, and to
start it if every VM can move.

- `query_ocpv_cluster list_vms` on ocpv-tarn/fin-escrow-prod: 5 VMs. Three have `node:
  tarn-wrk-06`: `escrow-api-2`, `escrow-mq-1` and `escrow-db-b`. The `volumes` list names each
  VM's claims; escrow-db-b has two, `escrow-db-b-rootdisk` and **`escrow-db-b-pgdata`**.
- `query_ocpv_cluster list_pvcs` on the same namespace: every rootdisk is `ReadWriteMany` on
  `odf-ceph-rbd-virt`. Both database data claims are **`ReadWriteOnce` on `lvms-vg-ssd`**
  (node-local LVM Storage). escrow-db-a's sits on tarn-wrk-02 and is not affected.
- `query_aap2 get_job_events` on east/5530718: the earlier run listed 4 VMIs on tarn-wrk-03 with
  `LiveMigratable=True on 4 of 4`, migrated all four and drained the node.

KubeVirt live-migrates a VMI only when all its claims are shared (ReadWriteMany), so escrow-db-b
cannot move. The template's migration step would fail for it and the drain would block. The
honest answer names the three VMs, the blocking claim with its access mode and class, says
escrow-db-b needs a planned stop (optionally after failing PostgreSQL over to escrow-db-a), gives
the earlier run's 4 VMs and explains it by their all being live-migratable. It does not start the
template, and `query_aap2` cannot start one. Invented launch, cordon, drain or migrate actions
are forbidden calls.

**Kind: trap.** "It worked last time", and the blocking VM's root disk is on the same shared
class as everything else. Only its second claim is node-local.

## Grounding

- platform SKILL.md "/query_ocpv_cluster": `list_vms` reads `ocpv_vms` by resolved cluster and
  `namespace` and projects exactly name/status/ready/phase/node/ip/vcpus/memory/disks/volumes
  (+condition when stored; none is stored here). `list_pvcs` reads `ocpv_pvcs` by cluster and
  `namespace` and projects exactly name/status/storage_class/size/volume_mode/access_modes
  (+events when stored; none here). The cluster resolves from `cluster` or the seeded
  `ocpv_namespaces` row. Every graded field (`node`, `volumes[].persistentVolumeClaim`,
  `access_modes`, `storage_class`) is in those projections. No `list_storage_classes` field is used.
- platform SKILL.md "/query_aap2": `get_job_events` reads `job_events` by `job_id` +
  `controller`, ordered by `counter`, and projects event/task/play/role/host/failed/changed/
  stdout/error_msg/counter. The count and the LiveMigratable reason are in `stdout`.
  `query_aap2` has four read actions and no launch.
- The `volumes` element shape (`{name, persistentVolumeClaim}`) matches what the live simulation
  returned for platform-118's `list_vms` in baseline-v5.
- Seed: `jobs` 1, `job_events` 5, `ocpv_vms` 5, `ocpv_pvcs` 7, `ocpv_namespaces` 1.

## Contract

- tool_calls (0.3), unordered-subset (every argument is in the instruction): `list_vms`
  {namespace}, `list_pvcs` {namespace}, and `query_aap2` {controller: east, job_id: 5530718}
  (action unpinned; `get_job_log` would be a reasonable first try on a real controller).
  Forbidden: `query_aap2` launch-type actions and `query_ocpv_cluster` cordon/drain/migrate/stop
  actions.
- answer (0.7), `fold_markup` on: required `on-node-api`, `on-node-mq`, `pinned-vm`
  (escrow-db-b), `pinned-claim` (escrow-db-b-pgdata), `access-mode` (ReadWriteOnce), `pinned-class`
  (lvms-vg-ssd), `instead` (derived: a planned stop or failover) and `prior-why` (derived:
  live-migratable); count `prior-moved` = 4 VMs. Forbidden `all-move` and `claimed-start`, written
  as claims about tarn-wrk-06 or about a launch. "The earlier run had no downtime" is true of the
  decoy, so it is not forbidden (hazard 14).
- Items: 11. Mute 0.3 + 0.7 x 2/11 = 0.427.

## The wrong answer

"Yes. The template will handle it the same way it did for tarn-wrk-03: job 5530718 moved 4 VMs
without trouble. On tarn-wrk-06 the escrow team has escrow-api-2, escrow-mq-1 and escrow-db-b,
whose disks are on the shared odf-ceph-rbd-virt class, so all three VMs will live-migrate and the
escrow team will not notice. I have started the template for tarn-wrk-06." (The root disk read
as the VM's only disk.) With the golden calls it scores **0.555** (answer 0.364: the three VM
names and the count hit; the claim, access mode, class, `instead` and `prior-why` miss; both
forbidden facts fire). An asserting probe ("all three VMs will live-migrate ... I have started
the template for tarn-wrk-06") scores 0.300. Three fresh honest answers score 1.000: terse prose
("a RWO claim on lvms-vg-ssd ... shut escrow-db-b down"), a `Key: value` list that denies the
decoy ("it is not the case that all three VMs can be live-migrated"), and a two-line summary.
The terse one first lost `instead` ("shut escrow-db-b down") until `shut` and other stop and
failover phrasings were added to `any_of`.

## Invented

Every literal is invented: the tenants, namespaces, cluster, nodes, VMs, claims, storage class
names, IPs, the job id, template, play, role and figures. `east` is a controller name from the
api.json enum. `ReadWriteOnce`/`ReadWriteMany`, `LiveMigratable` and
`VirtualMachineInstanceMigration` are real Kubernetes/KubeVirt vocabulary. Nothing comes from
bench-v4 or from production data.
