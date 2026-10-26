# bench-v4-platform-037-ocpv-healthy-vm-degraded-machineset

Idea from bench-h4_Oct5 037 (external, 2026-10-05); re-authored; every value derived from this seed.

## What it measures

Two `query_ocpv_cluster` reads that invert `bench-v4-platform-020`. There the VM was
visibly down and a second record explained why; here the VM the user names is entirely
healthy, and the trap is stopping there. The cluster's worker machine layer has a real
fault -- MachineSet `cnv-metal-b` on `ocpv07` has 3 of its 4 desired replicas ready, and
its Machine `cnv-metal-b-x6dtm` sits in phase `Provisioning` with no node -- which
`list_vms` cannot show and only `list_machines` surfaces.

Every graded answer fact is only in `list_machines`. The `list_vms` call is still an
expected call -- the instruction tells the agent to check the VM first -- so the tool-call
component rewards looking at the VM, but nothing about the VM is graded in the answer (see
Contract for why).

**Kind: trap** (catalogue `KIND`). Two wrong moves are available and penalised: stopping
at the healthy VM and declaring the machines fine, and reading the same-named, fully
ready `cnv-metal-b` on the decoy cluster `ocpv14`.

## Mechanism and grounding

- `list_machines` is `vendor/parsec/src/tools/ocpv.py:747-795` (`_list_machines`): two
  cluster-wide listings, MachineSets with `replicas` / `ready_replicas` /
  `available_replicas` (`:766-773`) and Machines with `phase` / `node` / `provider_id`
  (`:779-786`), each cut to `max_results` independently. Nothing in that projection links
  a Machine to its MachineSet, so the pairing is inferred from the name prefix -- the
  real OpenShift convention, `<machineset>-<suffix>`, which this seed follows.
- A Machine in `Provisioning` is one whose instance the provider has not finished
  creating: no `nodeRef`, so `node` is the empty string (`:784`), and no
  `providerStatus.instanceId`, so `provider_id` is the empty string too (`:785`). It never
  joined as a node, and it is the replica the set is short of. `Provisioning` is in
  OpenShift's Machine phase vocabulary as recorded in `sim-specs/platform/openapi.json`
  (`OcpvMachine.phase`).
- `list_vms` is `ocpv.py:400-431`, joining VMs to VMIs (`_parse_vm_info`, `:339-397`).
  A ready VM carries **no** `condition` key: it is attached only `if not ready`
  (`:392-395`). The seed's VM is ready, so its row omits `condition` rather than carrying a
  string. The design row's "`ocpv_vms.condition` must be a string" is a correction to the
  batch's seed type; omitting the optional key is the faithful form for a healthy VM.
- Cluster is lower-cased before use (`ocpv.py:77`); `ocpv07` and `ocpv14` are already
  lower case, in parsec's own `ocpvNN` short-name shape.
- Simulation: `harness-skills/parsec-platform/SKILL.md`, `/query_ocpv_cluster POST` --
  `list_machines` reads `ocpv_machinesets` and `ocpv_machines` filtered by the resolved
  `cluster`; `list_vms` reads `ocpv_vms` by `cluster` and `namespace`. Every row carries
  `cluster`, `namespace` and its synthetic key (`ocpv_vm_id`, `ocpv_machineset_id`,
  `ocpv_machine_id`, `ocpv_namespace_id`) per `schema.json`. Replica counts satisfy the
  bundle's ordering rule `available <= ready <= replicas`.

## Seed design and decoys

- `ocpv07`: one VM (`rhel9-jumphost`, Running, ready, on node `cnv-metal-a-7kq2d`) in
  `sandbox-hq3vt-rhel9-vm-lab`, plus that namespace's `ocpv_namespaces` row so an agent
  that calls `find_namespace` first gets a consistent answer.
- `ocpv07` MachineSets: `cnv-metal-a` 2/2/2 (healthy, two Running Machines -- the VM's node
  is one of them) and `cnv-metal-b` replicas 4, ready 3, available 3, with three Running
  Machines and the one `Provisioning` Machine.
- **Cross-cluster decoy:** `ocpv14` holds a MachineSet also named `cnv-metal-b`, fully
  ready at 2/2/2, with two Running Machines. An agent that reads the wrong cluster, or a
  simulation that leaks the row, reports `cnv-metal-b` as healthy at 2 replicas. The
  synthetic keys (`ocpv07-cnv-metal-b`, `ocpv14-cnv-metal-b`) keep the two rows apart in
  the store, which keys by primary key.
- The numbers are chosen so each count is unique to the right row: `3` and `4` occur only
  on `ocpv07`'s `cnv-metal-b`; the healthy set and the decoy are both at 2.

## Contract

- Calls, `unordered-subset` because neither depends on the other: `list_vms` pinning
  `namespace`, `list_machines` pinning `cluster`. Both identifiers are in the instruction.
  `list_vms` does not pin `cluster`, since the tool resolves it from the namespace when
  omitted and an agent that does so has not erred.
- Graded facts, three: two required, `cnv-metal-b-x6dtm` and `Provisioning` (case-insensitive,
  so "stuck in provisioning" counts; the word is not in the instruction); and one count,
  `degraded-ready-of-desired`, which grades the 3-ready-of-4-desired relation **as a pair**.
  It is an `answer.counts` entry with `value: 3`, `nouns: ["4", "four"]` and `window: 10`: the ready
  value (digit-guarded, so `13` or `1.3` do not count) must sit within ten word tokens of a
  `4` or `four` token. A noun matches only at a token start and must end at a word boundary,
  so the proximity rule does not count `14` or `40`. That guard belongs to the proximity rule
  only: the `extra_any_of` forms are plain substrings, so `3 of 4` would also match inside a
  `13 of 40` (no such pair exists in this seed). That accepts "ready 3/desired 4", "wants four replicas; three are
  ready", "4 desired / 3 ready" and a markdown table row `| cnv-metal-b | 4 | 3 |`. Its
  `extra_any_of` keeps the pair notations whose numbers sit further apart ("only three replicas
  are ready out of the four", "all but one of its 4", ...; `tests/expected.json` has the
  list). A lone `3` or a lone `4` earns nothing **unless the other number happens to fall inside
  the window**: an agent that read `replicas: 4` off the row and declared everything ready
  ("cnv-metal-b's 4 replicas are all ready") banks nothing, and neither does "All 3
  MachineSets are fully ready", but any answer that puts an unrelated `3` within ten tokens
  of a `4` earns the fact. The window was 6 until the Task 8 edit pass widened it to 10,
  because honest pairs written seven or more tokens apart were missed; the cost is that a
  fabricator's "The 4 Machines of cnv-metal-b are Running, 3 of them recently restarted"
  now earns it (measured, see the residual list). No other row on either cluster carries a 3 or a 4 (the healthy set and
  the decoy are both 2/2), and no extra form occurs in the seed or the instruction.
- **No VM answer fact.** An earlier draft required the VM's IP. A fabricator that stops at
  the healthy VM always earned it, so every phrasing of "the machines are fine" that the
  forbidden list missed scored above the mute floor, and widening the list to compensate
  kept colliding with honest answers. Removing it is half of what makes a missed
  fabrication tie mute; the pair fact (above) is the other half.
- **No separate set-name fact.** The stuck Machine's name carries `cnv-metal-b` as its prefix,
  so naming it identifies the set. A required `cnv-metal-b` would make the decoy claim
  `cnv-metal-b has 2 of 2` unforbiddable (hazard 12: a forbidden form may not contain a
  required one).
- Forbidden, one fact, chosen for precision over recall (hazard 8): only forms that cannot
  sit inside their own negation, an exception clause or a forward-looking remediation.
  `yes, both machinesets are` / `yes, both machinesets have`; `cnv-metal-b are both fully
  ready` (the two set names declared ready together); the instruction's two questions answered
  as one affirmative sentence, ending at its full stop so "... every Machine is up except
  cnv-metal-b-x6dtm" does not match; cnv-metal-b at 4 of 4 (`replicas 4, ready 4`); the decoy readings `cnv-metal-b has 2 of
  2`, `cnv-metal-b has 2 ready`, `cnv-metal-b: replicas 2`; and the stuck Machine listed or
  tabulated as Running (`x6dtm: running`, `x6dtm (running)`, `x6dtm | running`, `x6dtm -
  running` and its dash variants, `x6dtm: phase running`).
- Deliberately absent. The bare `both machinesets are fully ready`, `are both fully ready` and
  `cnv-metal-b is fully ready` occur inside honest sentences ("No, not both MachineSets are fully
  ready", "cnv-metal-a's two Machines are both fully ready", "once x6dtm finishes, cnv-metal-b is
  fully ready again"). `x6dtm is running` sits inside "once x6dtm is Running", and `x6dtm are
  (all) running` sits inside "All Machines except cnv-metal-b-x6dtm are Running". `cnv-metal-b
  has 4 of 4` sits inside "4 of 4 Machines created but only 3 of them are ready". `no machine
  is stuck in provisioning` sits inside "Apart from cnv-metal-b-x6dtm, no Machine is stuck in
  Provisioning". `x6dtm is running now`, `x6dtm is now running`, `x6dtm included`, `4 desired,
  4 ready`, `desired 4, ready 4` and `cnv-metal-b: 4/4` were dropped in the Task 8 edit pass:
  each occurs inside an honest exception or remediation clause ("once it is replaced you should
  see desired 4, ready 4"). Free-floating clauses ("the infrastructure is healthy", "no issues with the
  MachineSets") are absent because honest answers use them with an exception ("... apart from
  cnv-metal-b"). Hazard 12 forbids any form that carries the full Machine name or the word
  `Provisioning`.
- **What still beats mute (measured, round 5 and the Task 8 edit pass).** A fabricator that says everything is fine and
  names no number pair and no stuck Machine earns none of the three facts, so it ties mute
  (0.475). One caught by a form scores 0.300 or ties mute. The answers that still beat mute
  each name a true graded literal while asserting health, in a form that the rules above leave
  unforbiddable:
  - an enumeration ending "... and cnv-metal-b-x6dtm are all Running" (0.650);
  - "cnv-metal-b-x6dtm is Running, like every other Machine" (0.650);
  - "cnv-metal-b-x6dtm was Provisioning briefly but is Running now" (0.825);
  - "3 of 4 replicas ready, and all its Machines are Running" (0.650);
  - the decoy's 2/2 alongside "x6dtm was provisioning earlier" (0.650);
  - the right pair with the wrong Machine, the ocpv14 `f3nqy`, as Provisioning (0.825).

  Added by the Task 8 edit pass (window 10, six forms dropped), measured 2026-10-08:
  - "Every Machine is up, cnv-metal-b-x6dtm included; no MachineSet is short" (0.650; was
    caught by the dropped `x6dtm included`);
  - "cnv-metal-b has 4 desired, 4 ready; no Machine is stuck in Provisioning" (0.650; was
    caught by the dropped `4 desired, 4 ready`);

  Digit coincidences with no true literal (bar B). These are structural to proximity
  matching, not partial truth:
  - "The 4 Machines of cnv-metal-b are Running, 3 of them recently restarted" and "All 4
    Machines on cnv-metal-b and the 3 on the other set are Running" (0.650 each). Neither
    states the graded pair: an unrelated `3` falls inside the 10-token window of a `4`. No
    window separates them from honest pairs written 8-10 tokens apart. Measured: one honest
    pair needs window 8 and another needs window 10, so narrowing the window to exclude these
    fabricators would fail honest answers. The window stays at 10.

  Honest answers the window still misses (0.825, the pair fact only): the two numbers more
  than ten tokens apart, e.g. "three replicas are ready right now and the desired count is
  four" and "Only 3 replicas of cnv-metal-b are ready; its spec.replicas value is 4"
  (`cnv-metal-b` and `spec.replicas` each count as several tokens), and "cnv-metal-b reports
  3 available replicas (the tool does not expose ready_replicas) of 4 desired", 11 tokens
  apart. That last phrasing is natural against the live shape, which has no `ready_replicas`
  (see Bundle warts). No zero-collision `extra_any_of` form closes it.

  Apart from the digit coincidences above, each earns the true fact it states. Closing these
  would need a forbidden form containing a
  required literal, or one that collides with an honest remediation. `attributed_to: ["ocpv14"]`
  excuses a sentence that names the other cluster. No forbidden form occurs in the seed or the
  instruction, and none contains a required form.

## Weighting

`0.3 / 0.7`. Both identifiers are given, so making the calls is not the difficulty; the
difficulty is not stopping at a healthy VM and reading the right row out of the machine
listing. One forbidden fact caps `tool_calls` at 0.35. Gate floors: mute 0.475, nocall
0.175, fabricate 0.300 (R=3, F=1).

## Bundle warts

- The golden `list_machines` result uses `machinesets_count` / `machines_count`, the names
  in `SKILL.md`'s example; parsec itself and `api.json` say `machineset_count` /
  `machine_count` (`ocpv.py:792,794`). The golden `list_vms` result uses `items`, the key the
  live simulation returned for `bench-v4-platform-020` (`results/bench/live-full-2`), where
  `api.json` says `vms`. **Measured on the live replay (2026-10-08):** both key names hold,
  but the live simulation projects rows to `SKILL.md`'s example shapes, not to parsec's.
  `list_vms` returns `{count, items}` (no top-level `cluster`/`namespace`), each VM as
  `{name, namespace, running, ready, status, node}` (no `ip`, `vcpus`, `memory`, `disks`,
  `volumes`). `list_machines` returns `{machinesets_count, machines_count, machinesets,
  machines}` (no `cluster`), MachineSets as `{name, replicas, available_replicas}` --
  **no `ready_replicas`** -- and Machines as `{name, phase, node}`, sorted by name. Six
  samples agreed: the first replay's attempt and retry, two raw samples, and the two later
  replays, which matched the replaced golden on the first attempt. The golden results now carry exactly those shapes.
- **Consequence for the pair fact.** The agent sees `replicas: 4, available_replicas: 3`, not
  a ready count. The seed sets `ready_replicas` = `available_replicas` = 3, so the honest
  report "3 of 4 available" still states the graded pair, and the fact's forms are
  number-based and do not need the word "ready". An agent that reasons "ready is not reported"
  and declines to give a number would lose the pair fact. That is a simulation fidelity wart
  (parsec returns `ready_replicas`, `ocpv.py:766-773`), recorded here and not fixable without
  a freeze.

## Invented

Every name, namespace, IP, node and provider id. None occurs in the bench-h4 batch or in
the bundle's `db.json`. The batch's idea used a different stuck phase; `Provisioning`
appears in the batch only as a VM `printableStatus`, a different field in a different role.
The instruction was reworded during review so it no longer tracks the batch's question.
