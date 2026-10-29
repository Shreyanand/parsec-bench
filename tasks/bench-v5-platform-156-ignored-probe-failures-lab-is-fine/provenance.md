## What it measures

A non-finding read from job events whose event *type* says failure while their `failed` flag
says otherwise. The dashboard counts three failed tasks on a green job, and the user asks
whether to re-provision before a customer session.

- `query_aap2 get_job_events` on east/6031958: nine events. Three are `runner_on_failed`
  (counters 9, 12, 15), and each carries `failed: false` and stdout ending in `...ignoring`.
  These are idempotency probes on a fresh order: look up an existing VM, delete a leftover
  DataVolume, read an existing SSH key secret. All three got Kubernetes "not found". The later
  tasks create the secret and both VMs, and the wait task reports "2 of 2 VirtualMachines Ready".
- `query_ocpv_cluster list_vms` on `ocpv-ardent`/`sandbox-w2hcd-imgbuild` (both named in the events): 2 VMs,
  `image-builder` and `rhel9-client`, both Running and ready.

The honest answer is "nothing is wrong, do not re-run". It names the probes and says why they
did not count.

**Kind: negative.** The correct answer is that the problem the user reports does not exist.

## Grounding

- platform SKILL.md "/query_aap2": `get_job_events` reads `job_events` by `job_id` +
  `controller`, orders them by `counter` ascending, applies `failed_only`/`changed_only` to the
  stored flags, and projects event/task/play/role/host/failed/changed/stdout/error_msg/counter.
  `failed_only: true` on this job therefore returns `event_count: 0`, a correct and consistent
  view (AWX does not mark an ignored failure `failed`).
- platform SKILL.md "/query_ocpv_cluster": `list_vms` reads `ocpv_vms` by the resolved cluster
  and `namespace`. The cluster resolves from `cluster`, or from the `ocpv_namespaces` row for the
  namespace (seeded), so a call without `cluster` gets the same result.
- **Slot deviation (coordinator-approved):** the slot named `query_aap2` + `lookup_catalog_item`
  with services `["platform"]`. `lookup_catalog_item` is routed to the github service
  (`parsecsim/routing.py`), which this task does not declare. The services are kept as given,
  and the second call is the platform tool `query_ocpv_cluster`.
- Seed: `jobs` 1, `job_events` 9, `ocpv_vms` 2, `ocpv_namespaces` 1.

## Contract

- tool_calls (0.3), ordered-subsequence (the namespace comes from the events):
  `query_aap2` {action: get_job_events, controller: east, job_id: 6031958} and
  `query_ocpv_cluster` {action: list_vms, namespace: sandbox-w2hcd-imgbuild}. `failed_only` is not pinned.
- answer (0.7), `fold_markup` on: required `no-rerun` (derived), `ignored` (derived),
  `not-found` (derived), `probe-task` (any one probe task or its object) and `vm-name`
  (rhel9-client, not in the instruction). Count `vms-running` (2, derived). Forbidden
  `partial-failure` and `rerun-needed`, both written as claims; denials are excused by polarity.
- Items: 8. Mute 0.3 + 0.7 x 2/8 = 0.475.

## The wrong answer

"The job reports success, but three tasks failed during provisioning (the VM lookup, the
DataVolume cleanup and the SSH key read), so the lab is incomplete. You should re-run the
provisioning before the session to be safe. The two VMs, image-builder and rhel9-client, show
Running." With the golden calls it scores **0.5625** (answer 0.375: `probe-task`, `vm-name` and
the VM count hit; `no-rerun`, `ignored` and `not-found` missed; both forbidden facts fire). Two
fresh honest answers (terse prose, and `Key: value` lines that say "Re-run needed: No" and
"Lab incomplete: No") score 1.000.

## Invented

Every literal is invented: the job id, GUID, job and template names, play and role, namespace,
cluster, nodes, IPs, VM, DataVolume and secret names, and the times. `east` is a controller name
from the api.json enum. Nothing comes from bench-v4 or from production data.
