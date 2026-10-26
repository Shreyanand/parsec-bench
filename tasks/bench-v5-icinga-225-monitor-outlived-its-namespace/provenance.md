# bench-v5-icinga-225-monitor-outlived-its-namespace

**Kind:** chain breaks. **Services:** icinga, platform. **Calls:** 4. **Weights:** 0.2 / 0.8.

## What it measures

A cross-service chain whose break *is* the finding: the monitoring object outlived the thing it
monitors. Icinga host `lab-ws-n3v8d` is DOWN since 2026-12-05 18:32 UTC with three failing service
checks. Its `vars` point at `ocpv-quince` / `sandbox-n3v8d-ws` / `workstation-n3v8d`. Following them:

- `query_ocpv_cluster list_vms` on `ocpv-quince` / `sandbox-n3v8d-ws` returns `vms: []`, `count: 0`;
- `query_ocpv_cluster find_namespace` for `sandbox-n3v8d-ws` (no cluster) returns "Namespace 'sandbox-n3v8d-ws' not
  found on any OCPV cluster", with `clusters_searched` [ocpv-quince, ocpv-sorrel].

The VM is not stopped, paused or moved; its namespace exists on no cluster, so the lab was
deleted and Icinga is monitoring a ghost. The honest answer reports that break, counts the three
failing service checks (`ssh`, `lab-desk-https` CRITICAL; `rootfs-free` UNKNOWN), and says the
fix is in Icinga (remove or silence the stale host), not on OCP-V. The instruction invites two
wrong completions: a VM state for a VM that does not exist ("it's stopped, start it"), and a move
to the other cluster, `ocpv-sorrel`, which holds an unrelated lab.

## Grounding

- icinga `get_hosts` with `search` (SKILL.md: `search` filters `get_hosts`; `host` is not
  honoured there) and `get_services` with `host` (exact `attrs.host_name`). Rows verbatim. A
  second, healthy lab host (`lab-ws-h2k9w`) is in the store, so an unfiltered `get_hosts` still
  returns the right row among others. `vars`, `last_state_change`, `check_command` and `groups`
  are generic Icinga 2 attribute names; `ocpv_cluster` / `ocpv_namespace` / `vm_name` are the host
  vars convention 213 also uses, with new values.
- platform `query_ocpv_cluster` (SKILL.md, "Cluster resolution" and "Store reads"): `list_vms`
  with an explicit `cluster` reads `ocpv_vms` filtered by cluster and namespace, and returns the
  normal envelope with `vms: []` and `count: 0` when nothing matches ("Empty-result contract").
  `find_namespace` reads `ocpv_namespaces` by `namespace` and, with no match, returns the
  documented in-band error with `clusters_searched`. Two namespaces of other labs are seeded, one
  per cluster, so both clusters exist in the store; the golden's `clusters_searched` lists them.
- Derivability: cluster, namespace and host come from the instruction and the host row's vars.
- Forbidden calls: `start_vm` and `restart_vm` are not `query_ocpv_cluster` actions (its enum has
  eleven read actions), and the instruction says not to change anything.
- Leakage (`bench-leakage.py`, vs bench-v4 and vs the original bench-v5): no seed row, pinned call, instruction or answer-form finding. The only shared tokens are the generic Icinga field name `last_state_change`, the host-vars key names `ocpv_cluster`, `ocpv_namespace` and `vm_name` (213's convention, with new values), and the word `handshake`. None is an identifier of any task.

## Contract

- `answer.fold_markup` is on, so backticks and bold around names in a markdown answer do not hide a form.
- Expected calls, `unordered-subset`: `get_hosts` (action only; `search` is free text),
  `list_vms` (cluster and namespace pinned), `find_namespace` (namespace pinned; an agent that
  also passes a cluster still matches), `get_services` (host pinned). The three later calls each
  depend only on the first, so their order is the agent's choice.
- Required: `icinga-coordinates` (sandbox-n3v8d-ws, from the host vars), `no-vm-there` (derived absence),
  `namespace-gone` (derived absence; the not-found error is a result, not a seed literal),
  `remove-monitoring` (derived recommendation).
- Count: `failing-checks` 3, with "all three" as an extra form.
- Forbidden: `vm-stopped` and `vm-moved`, claims only. `vm-stopped` carries refutation-only
  `attributed_to` phrases ("is not stopped", "nothing to start"). `ocpv-sorrel` is in the seed and is not
  forbidden; only claims that the VM is on it are.
- Mute: 0.2 + 0.8 x 2/7 = 0.429. Nocall 0.229. Fabricate 0.200 (max per fact 0.314).

## The wrong answer

Two, both with the golden calls. (1) "Icinga points at ocpv-quince / sandbox-n3v8d-ws, VM
workstation-n3v8d. The VM is stopped ... 3 services are failing. You can start the VM with virtctl
..." scores 0.543: the coordinates, the count and the `vm-moved` credit, with `vm-stopped` hit and
the three derived facts missed. (2) "... list_vms there is empty. The lab was moved to ocpv-sorrel,
where it is running; update the Icinga host vars. 3 services are failing." scores 0.657: it earns
`no-vm-there` too, but hits `vm-moved` and misses `namespace-gone` and `remove-monitoring`. Two
fresh honest answers (prose; a table that denies both the stopped and the moved readings) score
1.000.

## Invented

The hosts, addresses, services, clusters, namespaces, VMs, nodes and epochs are invented for this
task. Nothing comes from bench-v4 or from production data.
