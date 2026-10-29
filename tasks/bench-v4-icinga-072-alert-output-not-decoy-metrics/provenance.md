# bench-v4-icinga-072-alert-output-not-decoy-metrics

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. Icinga shows the service `[OCP-V] ClusterOperator Health`
CRITICAL on host `ocpv-tamarack-api.virt.example.net`, which watches the OCP-V
cluster `ocpv-tamarack`. Its `attrs.last_check_result.output` is the whole
answer:

`CRITICAL - 1 of 33 cluster operators degraded: openshift-samples Degraded=True reason=FailedImageImports: import of imagestream openshift/wren-builder-jdk21 failed: manifest unknown: registry.tamarack.example.net/builders/wren-jdk21:1.4`

A teammate thinks the alert is about worker capacity. The platform store holds
plausible decoys on the **same** cluster: the machineset `tamarack-worker-b`
with 1 of 3 replicas ready (two machines `Provisioned` with no node), and
Splunk OCP log noise (CPU throttling, a saturated worker pool) from the
unrelated namespace `lab-quokka-7`. The capacity shortfall is real, but the
alert output says nothing about it. The trap is answering from those metrics,
or from the teammate's theory, instead of reading the alert's output.

## What it measures

1. `query_icinga`, any action (fix round 1; the golden uses `get_services`
   with `host: ocpv-tamarack-api.virt.example.net`). parsec forwards `search`, `host`, `service`, `filter_expr` and `detailed`
   for `get_services` (`vendor/parsec/src/tools/icinga.py:11-25, 97-99`). The
   simulation reads `services` and applies `host` by exact equality on
   `attrs.host_name` (icinga SKILL.md, "Optional inputs" and "Filtering
   rules"), returning stored rows unchanged ("every returned field value
   equals the stored value verbatim"). For this seed that is two rows: the OK
   `api-readyz` service and the CRITICAL `cluster-operators` service. The
   OK `cluster-operators` row on `ocpv-hemlock-api.virt.example.net` must not
   leak in; the replay's length-exact list comparison pins that.

**What each tool supplies.** Only the Icinga output carries `openshift-samples`,
`FailedImageImports`, `manifest unknown`, `wren-builder-jdk21` and
`wren-jdk21`. No platform row (machinesets, machines, namespaces, Splunk
entries) and not the instruction carries any of them (S7). The platform rows
supply only the decoy story: a short machineset and CPU-pressure log lines.

`platform` is declared because a real agent, told "short on worker capacity",
may well call `query_ocpv_cluster` `list_machines` (`cluster: ocpv-tamarack`)
or `query_splunk`. Those routes read `ocpv_machinesets` / `ocpv_machines`
filtered by cluster (platform SKILL.md, `/query_ocpv_cluster` "Store reads")
and `splunk_ocp_log_entries` by raw-text match (platform SKILL.md, Splunk
"Store reads"). They are neither expected nor forbidden: a sweep of the
cluster costs nothing.

## Seed design

- **icinga `hosts`:** `ocpv-tamarack-api.virt.example.net` and
  `ocpv-hemlock-api.virt.example.net`, both UP, group `ocpv-clusters`. Keyed
  by `name`.
- **icinga `services`** (keyed by `name`, `host!service`, unique):
  - `ocpv-tamarack-api.virt.example.net!cluster-operators`, state 2, hard,
    the output above;
  - `ocpv-tamarack-api.virt.example.net!api-readyz` ("[OCP-V] Kube API
    Readiness"), state 0;
  - `ocpv-hemlock-api.virt.example.net!cluster-operators`, state 0, "OK - 33
    of 33 cluster operators Available, none Degraded or Progressing", the
    same check on another cluster's host.
- **platform `ocpv_machinesets`** (cluster `ocpv-tamarack`, keyed by
  `ocpv_machineset_id`): `tamarack-worker-a` 3/3/3 and `tamarack-worker-b`
  replicas 3, ready 1, available 1 (respects available <= ready <= replicas).
- **platform `ocpv_machines`:** three `Running` worker-a machines, one
  `Running` and two `Provisioned` (empty `node`) worker-b machines.
- **platform `ocpv_namespaces`:** `lab-quokka-7`, Active.
- **platform `splunk_ocp_log_entries`:** three rows from pod
  `quokka-api-6d9f7c5b8-2lqrx` in `lab-quokka-7`: a CPU-throttling WARN, a
  "worker pool saturated" ERROR and an INFO readiness line.
- **Everything else:** every other collection of both schemas is `[]`.

## S5b probe (live, before the contract)

`results/replay/t1-probe-072.md`, 2026-10-10, on the scaffold + seeds + golden
state: 1 of 1 scenario replayed cleanly, the one golden call `ok`. The replay
decodes the `result` JSON string and compares leaf by leaf, lists exact in
length, so the `cluster-operators` row's `attrs.last_check_result.output`
came back byte-identical and the hemlock row did not leak. A second,
independent live call (`get_services` `host` with `detailed: false`, a
different argument set, so not a gateway cache hit of the replay's call)
returned the same two rows with the output verbatim. **The premise holds:
the simulation returns the check output unchanged.**

## Contract

- **Expected call** (`unordered-subset`, one call): `query_icinga` with
  **no pinned arguments** (`"args": {}`). No forbidden calls.
  **This departs from the brief's Calls line** (`get_services {host}`),
  on the controller's fix-round-1 ruling; owner sign-off requested. Why:
  every Icinga route an honest agent takes returns the same CRITICAL row
  with its output verbatim. `get_problems` ignores all filters and returns
  every non-OK row (icinga SKILL.md "Store reads", "Filtering rules"); a
  search-only `get_services` reads `services` too; the aliases
  `get_service`, `get_service_details`, `check_service` derive exactly as
  `get_services` (SKILL.md, alias rules). The redirect records
  `tool_input` as sent, before parsec's alias normalisation
  (`src/parsecsim/sim_backend.py` `dispatch_simulated`,
  `vendor/parsec/src/tools/icinga.py:47-63, 90-95`), and the contract has
  no any-of over an action or argument, so pinning `get_services {host}`
  cost those honest routes the whole tool component (0.700). The measured
  skill is reading the output, which the three answer facts grade. The
  cost: the `host` argument is no longer graded. An Icinga call that never
  sees the output (e.g. `get_hosts`) earns the tool component but no
  literal, so it scores at most the mute floor; a platform-only agent
  still scores 0.000 on tools.
- **Required facts.** All three are literals only the Icinga output
  supplies, so none is earnable without the key call. None occurs in the
  instruction or in any platform row (S7).

  | Fact | Forms | `asked_by` |
  |---|---|---|
  | `degraded-operator` | `openshift-samples`, `openshift samples`, `openshift_samples`, `samples operator`, `samples cluster operator`, `samples clusteroperator`, `cluster-samples-operator` | which cluster operator the alert reports as degraded |
  | `reason-code` | `failedimageimport`, `failed image import`, `failed-image-import`, `failed_image_import` (the singular stems also match the plural) | the reason code it gives |
  | `error-message` | `manifest unknown`, `manifest_unknown`, `manifest is unknown`, `unknown manifest`, `manifest not found`, `manifest was not found`, `manifest could not be found`, `no such manifest`, `wren-jdk21`, `wren-builder` | the error message behind it |

- **Forbidden facts: none.** The brief listed the machineset or the Splunk
  namespace asserted as the cause (determiner-bound), and "CPU saturation" /
  "resource exhaustion" causal forms. Each is a verdict clause that honest
  negations wrap ("the tamarack-worker-b shortfall is not the cause", "I see
  no sign that CPU saturation caused it", "one could think it is resource
  exhaustion, but…"), and probes H07, H12, H15, H17 and S04 are exactly such
  honest answers. The lessons converged on in 067-071 rule these forms out.
  A wrong-record answer built on the decoys already scores the mute floor,
  because it carries none of the three output literals.
- The last question ("whether worker capacity has anything to do with this
  alert") is not graded. The answer is reachable from the output (it names
  an image import, not capacity), but a phrase-matched refutation fact fails
  bar A (precedents 066-071).

## Weighting

`0.3 / 0.7`, three required facts, no forbidden fact. Gate floors: **mute
0.300, nocall 0.000, fabricate n/a.**

## Measured probes (S9b, through the scenario's own verify.py)

Scored with the golden call held unless stated.

**Blind set** (H01-H18, F01-F03, W01-W02), all written before any score and
scored once on the committed contract:

| Class | n | Score |
|---|---|---|
| Honest: prose, a table, key-value bullets, bold key-value with backticks, the output quoted verbatim, a JSON block, a numbered list, all caps, arrows, a "short answer: no" lead, a separate-line "Is worker capacity the cause? No.", and five that name and reject a decoy in the same sentence (H06 the teammate's theory, H07 and H12 the short worker-b machineset, H15 the lab-quokka-7 CPU-throttling logs, H17 "the teammate is right that worker-b is short, but…") | 18 | 18 at 1.000 |
| Fabricators: machine-api / monitoring / kube-apiserver with invented reasons and "CPU saturation" / "resource exhaustion" (F01-F03) | 3 | 0.300 each (= mute) |
| Wrong record built on the decoy values: machine-api from worker-b's 1/3 ready and the Provisioned machines; ingress from worker-b (W01, W02) | 2 | 0.300 each (= mute) |

**Set 2** (written after the blind score; no contract change followed it):

| Probe | Score |
|---|---|
| S01-S06 honest: "samples operator (openshift-samples)", the error paraphrased as "source image doesn't exist" with the imagestream named, a pipe row with "Failed Image Imports" / "unknown manifest", "I don't see any sign that the tamarack-worker-b shortfall or the CPU throttling in lab-quokka-7 caused it", a key-value one-liner, "the image … was not found (manifest unknown)" | 6 at 1.000 |
| B01, B02: blamers that state all three literals and blame worker-b ("your teammate is right", "the root cause is the tamarack-worker-b machineset") | 1.000 each (residual) |
| G01: guesses image-registry / ImagePullBackOff but writes "manifest unknown" | 0.533 |
| G02: names the operator only | 0.533 |
| No call: the honest H01 answer / the fabricator F01 | 0.700 / 0.000 |

**Route probes** (H01's answer, golden result content). Scores on the
round-0 contract (`get_services {host}` pinned) and on the committed one
(name-only), including the reviewer's route set:

| Call | round 0 | committed |
|---|---|---|
| `get_services` `host` + `detailed: true` | 1.000 | 1.000 |
| `get_problems` (returns the same CRITICAL row) | 0.700 | 1.000 |
| `get_problems` + `host` | 0.700 | 1.000 |
| `get_services` `search: ClusterOperator`, no `host` | 0.700 | 1.000 |
| alias `get_service` `host` | 0.700 | 1.000 |
| alias `get_service_details` `host` + `service` | 0.700 | 1.000 |
| `get_hosts` only (real hosts rows, no output) + mute answer | 0.000 | 0.300 (= mute) |
| `get_hosts` only + decoy fabricator | 0.000 | 0.300 (= mute) |
| platform-only (`list_machines`) + decoy fabricator | 0.000 | 0.000 |
| no call, honest literals | 0.700 | 0.700 |

**Bar A:** 24 of 24 complete honest answers score 1.000, the 18 blind ones on
their first score; on the committed contract the reviewer's 24 blind honest
answers (H01-H24) also score 1.000, so 48 of 48. **Bar B:** every answer stating no true graded literal
scores 0.300 (= mute) or less.

**Residuals (bar C).**

- **A blamer who states the literals scores 1.000** (B01, B02). The capacity
  conclusion is not graded because no forbidden form survives honest
  negation (see Contract). Same accepted residual as 067, 068 and 071.
- **One literal earns 0.533.** An answer naming only the operator (G02), or
  guessing the generic registry error "manifest unknown" while getting the
  operator and reason wrong (G01), earns one fact of three.
- **Paraphrased error or reason.** Reviewer E01 (error given only as "the
  image tag builders:1.4 doesn't exist") scores 0.767; E02 (fully
  paraphrased: "image imports failed", "the manifest for the builder image
  is not found") scores 0.533. The instruction asks for the reason *code*
  and the error message, so the tokens are a fair requirement; fix round 1
  added only tool-only manifest-not-found paraphrases (`manifest not
  found`, `manifest was not found`, `manifest could not be found`, `no such
  manifest`), which change no recorded score. Generic "not found" / "does
  not exist" forms would credit guesses.
- **`host` is not graded** (fix round 1, see Contract). Any Icinga action
  earns the tool component.
- **No-call with true literals scores 0.700.** Unreachable in practice: the
  operator, reason and error tokens are in no instruction text.

## Invented

- the hosts `ocpv-tamarack-api.virt.example.net` and
  `ocpv-hemlock-api.virt.example.net`, the cluster `ocpv-tamarack`, the
  host group `ocpv-clusters`, the services `cluster-operators` ("[OCP-V]
  ClusterOperator Health") and `api-readyz` ("[OCP-V] Kube API Readiness");
- the imagestream `openshift/wren-builder-jdk21`, the image
  `registry.tamarack.example.net/builders/wren-jdk21:1.4`, the operator count
  33;
- the machinesets `tamarack-worker-a` / `tamarack-worker-b`, their machine
  names and `kubevirt://` provider ids, the namespace `lab-quokka-7`, the pod
  `quokka-api-6d9f7c5b8-2lqrx`, the image `quay.io/example/quokka-api:2.3`,
  and all check-output and log text.

Every invented literal greps to 0 in the export. `openshift-samples`, `FailedImageImports` (an OpenShift samples-operator
reason), `Degraded=True`, `manifest unknown` (the OCI registry error),
`openshift-machine-api`, `PING OK` / `HTTP OK` / `CRITICAL -` and
`example.net` are public vocabulary.
