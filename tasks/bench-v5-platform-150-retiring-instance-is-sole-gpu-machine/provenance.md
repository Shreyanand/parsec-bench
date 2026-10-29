## What it measures

A reverse lookup through `query_ocpv_cluster` `list_machines`, read from the Machine
`provider_id` field, which no existing task reads. AWS names an EC2 instance; only the
Machine whose `provider_id` (`aws:///us-east-2b/i-0b6d2f8e4c1a9735e`) ends in that id ties
it to the cluster. From that one call the agent must:

- name the node (`ip-10-0-148-37.us-east-2.compute.internal`) and the Machine
  (`larch-6qz4t-gpu-us-east-2b-h7qvd`);
- find the owning MachineSet by name (`larch-6qz4t-gpu-us-east-2b`, replicas 1), and see that
  no other Machine in it can absorb the workloads. The three `worker-us-east-2b` Machines
  share the zone but not the set;
- count the Machines whose `provider_id` zone is `us-east-2b`, including the control-plane
  Machine `larch-6qz4t-master-1`, which belongs to no listed MachineSet: 5 of 13.

**Kind: happy.** One call, and everything asked is in its result. The difficulty is the join
(instance id to Machine, Machine to MachineSet by name, zone from `provider_id`) and the two
counts.

## Grounding

- platform SKILL.md "/query_ocpv_cluster": with `cluster` given, the cluster is
  `lower(cluster)`. `list_machines` reads `ocpv_machinesets` and `ocpv_machines` filtered by
  `cluster`, projects machinesets to name/namespace/replicas/ready_replicas/
  available_replicas and machines to name/namespace/phase/node/provider_id, and sets
  `machineset_count` / `machine_count` to the list lengths. `max_results` defaults to 50, so
  all 13 Machines are returned. Lists are given in name order, as live lists come back.
- The `provider_id` format `aws:///<zone>/<instance>` is the SKILL.md example's.
- Seed: `ocpv_machinesets` 4, `ocpv_machines` 13, all on `ocpv-larch`.

## Contract

- tool_calls (0.2): `list_machines` with `cluster: ocpv-larch` (named in the instruction).
- answer (0.8): required `node`, `machine`, `machineset`; counts `others-in-set` (0,
  derived; the extra forms cover "the only machine in", "replicas: 1", "1/1") and
  `zone-machines` (5, derived; "5 of 13").
- No forbidden facts. Items: 5. Mute 0.2 + 0 = 0.200.

## The wrong answer

"Instance i-0b6d2f8e4c1a9735e is node ip-10-0-148-37 in MachineSet
larch-6qz4t-worker-us-east-2b. The other 2 workers in that set can take over. There are 4
machines in us-east-2b." It names the node, but the wrong set and both counts wrong (it reads
the zone's worker set and leaves out the control plane). With the golden call it scores reward **0.360** (answer 0.200: `node` only). Three fresh honest answers (terse prose, a key/value table that denies the worker set, and the golden) score 1.000.

## Invented

Every literal is invented: cluster `ocpv-larch`, infrastructure id `larch-6qz4t`, the
Machine and MachineSet names, instance ids, node names and the retirement date. The zone
names are real AWS names. Nothing comes from bench-v4 or from production data.
