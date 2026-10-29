# bench-v5-icinga-213-host-down-is-paused-vm

**Kind:** happy. **Services:** icinga, platform. **Calls:** 2. **Weights:** 0.3 / 0.7.

## What it measures

A cross-service pivot driven by monitoring metadata. Icinga host `lab-bastion-kx7q2` is DOWN
(100% packet loss), and the network team says nothing changed. The host's `vars` carry
`ocpv_cluster: ocpv-juniper`, `ocpv_namespace: sandbox-kx7q2-bastion` and `vm_name`. The
agent must read them from the Icinga host row and use them for `query_ocpv_cluster list_vms`.
There the VM row shows `status: Paused`, `ready: false` (the phase is still `Running`), and a
`condition` with reason `IOError` ("low-level IO error detected on disk rootdisk"). The real
cause is storage I/O on the VM's root disk, not the network. The sibling VM
`showroom-kx7q2` is Running and ready.

## Grounding

- icinga `get_hosts` honours `search` and returns matching `hosts` rows verbatim, `vars`
  included. `lab-bastion-kx7q2` is not a substring of the sibling `lab-showroom-kx7q2`.
- platform `query_ocpv_cluster list_vms` (SKILL.md "Store reads") reads `ocpv_vms` filtered
  by `cluster` **and** `namespace`. Per the README gotcha that scoped fields must be in the
  seed, both are stored on every VM row, and both equal the values in the Icinga host vars,
  so the pivot reaches the rows. An `ocpv_namespaces` row is also seeded, for an agent that
  calls `find_namespace` or omits `cluster`.
- The golden result follows the documented `list_vms` envelope (`cluster`, `namespace`,
  `vms`, `count`). Each VM is projected without `ocpv_vm_id`, `cluster` and `namespace`, and
  `condition` appears only where stored.
- No forbidden calls (not one of the group's eight).
- Validator WARN, justified: golden call 0 returns the documented serialized `result` string.

## Contract

- Expected calls, `ordered-subsequence` (the second depends on the first's vars):
  `get_hosts search=lab-bastion-kx7q2` → `list_vms cluster=ocpv-juniper
  namespace=sandbox-kx7q2-bastion`.
- Required: `paused`; `io-error`; `disk` (derived: where the error is); `cluster-ns`
  (ocpv-juniper, from the vars); `other-vm-ok` (showroom-kx7q2 Running).
- Count: `vms-in-ns` 2.
- Forbidden: `network-cause` ("network outage", "firewall change", "routing issue", ...).
  `attributed_to` holds specific phrases only ("not a network problem", "network team
  insists", ...). The probe "It is not a network team mistake: there was a firewall change."
  is hit.
- Mute floor 1/7 = 0.14.

## The wrong answer

"The VM is in phase Running ... so the guest is up; this looks like a network problem is the
likely cause - probably a firewall change or routing issue" (`.scratch/wrong/213.md`).
Reward 0.50: answer 0.29. It misses paused, the IOError, the disk and the count, and it hits
the forbidden fact.

## Invented

The hosts, addresses, vars, cluster, namespace, VMs, nodes, DataVolumes, the condition text
and the epochs are invented for this task. Nothing comes from bench-v4 or from production
data.
