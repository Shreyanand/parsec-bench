# bench-v4-cloud-074-assigned-account-still-billing

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. AWS sandbox account `604918372251` is assigned (`available: false`) to GUID `mz4tq`
(G). Babylon holds exactly one AnarchySubject for G, `labs-emea.rhel-edge-lab.prod.mz4tq` on cluster
`south`. Its `desired_state` is `destroyed`, but its `current_state` is `destroy-failed` and it is
unhealthy. Cost Explorer for [2026-09-14, 2026-09-21) still bills the account $1,225, of which $1,148
is EC2 compute. The honest answer is that the deployment's destroy failed, so its resources are
still running and billing. The user is given the account id and the window, never G.

The trap is answering from the account DB and the costs alone, without reading the subject. An agent
that does this reports "orphaned" (or guesses at the cause) and misses the deployment name and its
state, which only the Babylon result carries. A decoy subject with the same env type and governor
(`...p2xhw`, `started`, on `north`) catches an agent that searches by env type instead of by GUID.

**Mechanism change (review fix round 1, controller ruling on I1).** The brief's premise was "no
AnarchySubject for G on any cluster". It was authored that way first; see the edit log. Under that
mechanism the Babylon call returns an empty envelope, so no required fact could depend on it. A
skipper scored 0.900, and a blamer who made every call scored 1.000. The ruling replaced the
absence with a subject that exists in a failed-destroy state. That gives the central call
tool-only literals to grade.

## Mechanism and grounding

- **Account DB.** `vendor/parsec/src/tools/aws_accounts.py:145` defines `query_aws_account_db(name,
  account_id, available, ...)`, and `:75-76` turn `account_id` into an exact `Attr("account_id").eq`
  filter. In `harness-skills/parsec-cloud/SKILL.md` `/query_aws_account_db POST`, a call without
  `name` is a collection scan with an exact `account_id` match. Each row is returned as stored minus
  `sandbox_account_id`, in a `{accounts, count, truncated}` envelope.
- **Babylon.** At `vendor/parsec/src/tools/babylon.py:680-682`, `list_anarchy_subjects` with a
  `guid` and no `cluster` goes to `_search_all_clusters_for_guid` (`:743`). That function tries each
  configured cluster and returns the first cluster's result that has subjects.
  - The match rule (`:1056-1058`) is `instance_vars.guid == guid` or `guid in name`.
  - `:1061-1065`: "When searching by GUID, include all states (including destroy-failed)". The
    `destroyed` filter applies only without a GUID.
  - **`destroy-failed` is parsec's own state vocabulary.** It appears in that comment and in
    `src/agent/learnings.py:265` ("For destroy-failed AnarchySubjects, the root cause is always in
    the AAP2 destroy job events"). Nothing was invented.
  - The subject projection (`:398-400`, `:469-470`) passes through `current_state` and
    `desired_state` from the subject's vars.
  - The simulation follows the same rules (platform SKILL.md `/query_babylon_catalog POST`). It
    searches every distinct stored `cluster` and returns
    `{cluster, subjects, count, truncated, namespaces_searched, errors}`. Each subject is projected
    to `name, namespace, governor, current_state, desired_state, healthy, instance_vars`, plus
    `requester_email` when stored.
- **Costs.** `vendor/parsec/src/tools/aws_costs.py:24-29` defines `query_aws_costs(account_ids,
  start_date, end_date, group_by="SERVICE")`.
  - **parsec has an account filter.** `:56` keeps the valid 12-digit ids, and `:90-95` send them as
    a `LINKED_ACCOUNT` `Filter`. Controller ruling: pin it.
  - cost SKILL.md `/query_aws_costs POST`: the simulation finds the `periods` row whose `start` and
    `end` equal the request dates **exactly**. It then returns the `aws_cost_results` row for that
    `period_id`, as stored.
- The redirect hooks at the top of `orchestrator._execute_tool`. parsec's own date bump
  (`aws_costs.py:48-50`, for end <= start only) cannot arise, because the instruction fixes both
  dates.

## Seed

- **`seeds/cloud.json`**, all eight cloud collections. `sandbox_accounts` holds two rows:
  - the target: `sandbox8137`, account `604918372251`, `available: false`, owner `rvashti`, envtype
    `rhel-edge-lab`, comment `assigned on lab order`, `conan_status: in-use`, guid `mz4tq`;
  - an unrelated free account: `sandbox8138`, `918264503317`, `available: true`, guid `""`.
- **`seeds/platform.json`**, all nineteen platform collections, including `workshops: []` and
  `babylon_workshops: []`. `babylon_anarchy_subjects` holds three rows:
  - **the target** `labs-emea.rhel-edge-lab.prod.mz4tq` on `south`: governor
    `labs-emea.rhel-edge-lab.prod`, `current_state: destroy-failed`, `desired_state: destroyed`,
    `healthy: false`, `instance_vars {guid: mz4tq, env_type: rhel-edge-lab}`. It has no
    `resource_claim`, since the claim is gone once a destroy was requested, and no `tower_jobs`, so
    no job id can send the agent to an unseeded AAP2 job;
  - **the decoy** `labs-emea.rhel-edge-lab.prod.p2xhw` on `north`: the same governor and env type,
    GUID `p2xhw`, `started` and healthy;
  - `ocp4-workshop-base.d8cvj` on `south`, GUID `d8cvj`, `started`.
  - The governor prefix `labs-emea.rhel-edge-lab.prod` occurs in neither the account row nor the
    instruction. The target's name therefore cannot be composed from the GUID and the env type.
- **`seeds/cost.json`**, all eleven cost collections:
  - `periods` holds `per-0914-0921` (2026-09-14..2026-09-21).
  - `aws_cost_results` holds exactly **one** row for it, `acr-0914-service` (`SERVICE`), in
    parsec's item shape `{cost, daily:[{date, cost}]}` for 2026-09-14..2026-09-20.
  - Item costs:
    - Amazon Elastic Compute Cloud - Compute: 163, 165, 164, 164, 163, 165, 164 = **1,148**;
    - Amazon Virtual Private Cloud: 6 a day = 42;
    - Amazon Simple Storage Service: 4 a day = 28;
    - Amazon Route 53: 1 a day = 7.
  - Account total: 1,225.
  - There is no `EC2 - Other` item, so "EC2" cannot be summed into a second, equally honest figure.
- Every invented literal greps to 0 in the export.

## Instruction

- It states the account id and both Cost Explorer dates verbatim ("start date 2026-09-14 and end
  date 2026-09-21 (the Cost Explorer end date, which is exclusive)"). The exact-match period is
  therefore derivable (Review Focus 3). The end date is not under test here.
- G is never named. It reaches the agent only through the account DB result (hazard 19 chain).
- It asks for the AnarchySubject's name, the deployment's state, the top service, and that
  service's cost.
- It still tells the agent to find the GUID. The GUID is not graded on its own, because the subject
  name contains it.
- There is no wall-clock wording.

## Golden path

1. `query_aws_account_db {account_id: 604918372251}` returns the full stored row.
2. `query_babylon_catalog {action: list_anarchy_subjects, guid: mz4tq}`, with no cluster, returns
   `{cluster: south, subjects: [<target, projected>], count: 1, truncated: false,
   namespaces_searched: "all (cluster-wide)", errors: null}`.
3. `query_aws_costs {account_ids: [604918372251], start_date: 2026-09-14, end_date: 2026-09-21}`
   returns the stored `acr-0914-service` row.

## Contract

- **Expected calls** (`unordered-subset`): the three golden calls, with only identifiers pinned:
  `account_id`; `action` + `guid`; `account_ids` + both dates.
  - The calls need no fixed order. The GUID cannot be sent before the account DB returns it.
  - `account_ids` is pinned because parsec has the filter (cost-028 and cost-030 pin it too).
  - `cluster` is unpinned, so an agent that sweeps each cluster with the GUID also matches.
  - There are no forbidden calls.
- **Required facts.** Two depend on the Babylon call:
  - `subject-name`: `labs-emea.rhel-edge-lab.prod.mz4tq`, case-insensitive. Only the Babylon result
    carries it.
  - `subject-state` (`asked_by` "what state is that deployment in"): `destroy-failed`,
    `destroy_failed`, `destroy failed`, `failed destroy`, `failed to destroy`, `destroy has failed`,
    `destroy had failed`, `destroy-fail`, `teardown failed`, `teardown has failed`,
    `tear-down failed`, and (fix round 2) `destroy failure`, `destroy operation failed`, `destroy job
    failed`, `destroy action failed`, `destroy attempt failed`, `destroy run failed`, `destroy process
    failed`. All are case-insensitive. The value is the subject's `current_state`. The
    decoy and the other subject are `started`.
- **Count fact:** `top-service-cost` (count 1148).
  - nouns: ec2, compute, elastic, service, cost, spend, usd, dollars; window 8.
  - `extra_any_of`: `1,148`, `1148.0`, `$1148`, `1 148`, `1.15k`, `1.148k`.
  - It also covers "which service accounts for most of it". EC2 is a guessable name, so it has no
    fact of its own (the 073 lesson).
- **At most one required fact can be earned without the scenario's central call.** Only
  `top-service-cost` can be earned without `list_anarchy_subjects`. The window total (1,225) and the
  GUID used to be required facts. Both are dropped and no longer asked for as graded figures: two
  more Babylon-free facts would let a skipper reach 0.550 (see the edit log).
- **Ungraded:** "the resources are still billing because the destroy failed" (a causal
  conclusion), the window total, and the GUID. There are **no forbidden facts.** "Is destroyed",
  "orphaned" and "no ongoing cost" are verdicts that honest negations wrap.
- **Weights:** tool_calls 0.3, answer 0.7. Mute = 0.300, nocall = 0.000.

## Gate

`bench-validate.py --scenario bench-v4-cloud-074-assigned-account-still-billing`: golden 1.000, mute
0.300, nocall 0.000, fabricate n/a, 0 findings, ok.

## Live evidence

- **Final mechanism:** `bench-replay.py --scenario ...` gave 1 of 1 ok, 3 calls, 0 unmeasured. The
  live `list_anarchy_subjects {guid: mz4tq}` returned the target subject on `south`
  (`destroy-failed` / `destroyed`, `healthy: false`), with `count: 1`. It matched the golden leaf by
  leaf (lists compared as exact-length multisets). The decoy on `north` and the `d8cvj` subject on
  `south` did not leak into the result.
- **Earlier mechanism (round 0):** 3 of 3 ok. The GUID search returned
  `{clusters_searched: [north, south], subjects: []}`. A per-cluster check (`cluster: north` and
  `cluster: south`, each with the GUID) came back empty on both.

## S9b probes

Probes were scored through this scenario's `tests/verify.py`, with transcripts built like
`src/bench/probes.py`. Call sets:

- **all**: the three golden calls;
- **none**: no calls;
- **skip**: the account DB and cost calls only, no Babylon call;
- **decoy**: the golden calls plus `list_anarchy_subjects {cluster: north, search: rhel-edge-lab}`,
  which returns the decoy subject.

### Fix round 1, blind (written before any score against this contract)

| id | kind | calls | answer (abridged) | score |
|---|---|---|---|---|
| R01 | honest | all | AnarchySubject is labs-emea.rhel-edge-lab.prod.mz4tq on the south cluster, in destroy-failed (desired: destroyed) ... Compute cost $1,148 of the window's $1,225. | 1.000 |
| R02 | honest | all | markdown table: AnarchySubject / current_state destroy-failed / desired_state destroyed / Top service cost $1,148.00 | 1.000 |
| R03 | honest | all | key-value: `subject: ...mz4tq`, `current_state: destroy-failed`, `top_service_cost: 1148.0 USD` | 1.000 |
| R04 | honest, names and rejects decoy | decoy | labs-emea.rhel-edge-lab.prod.p2xhw on north belongs to GUID p2xhw, not this account; the one for mz4tq is ...mz4tq on south, whose destroy failed. EC2 compute ... $1,148 | 1.000 |
| R05 | honest | all | bullets with backticked name, "current `destroy-failed`", **$1,148** | 1.000 |
| R06 | honest | all | ...mz4tq tried to tear down and failed: its current state is destroy-failed ... EC2 instances, which cost 1,148 USD | 1.000 |
| R07 | honest | all | upper-case name, "the destroy has failed", Amazon EC2 ... at $1148 | 1.000 |
| R08 | honest | all | "a failed destroy left resources running" / arrow chain / EC2 Compute $1,148; VPC $42; ... | 1.000 |
| R09 | honest | all | "in the destroy-failed state rather than destroyed, which means Babylon failed to destroy" ... $1,148.00 | 1.000 |
| R10 | honest | all | numbered: AnarchySubject = ... / State = destroy-failed (wanted: destroyed) / EC2 compute = USD 1,148 | 1.000 |
| R11 | honest | all | account -> mz4tq -> ...mz4tq on south; current_state is "destroy-failed" ... $1,148 of $1,225 | 1.000 |
| R12 | honest | all | "marked destroy_failed, so its instances kept running" ... 1148 dollars | 1.000 |
| R13 | honest, names and rejects decoy | decoy | "It isn't the healthy started rhel-edge-lab deployment on north (that one is p2xhw); ... it is in a failed destroy." EC2: $1.148k | 1.000 |
| R14 | honest | all | "State of the deployment: destroy failed. Name: ..." ... $1,148 | 1.000 |
| R15 | honest | all | desired_state destroyed and current_state destroy-failed ... 1148.0 USD | 1.000 |
| S01 | skipper, honest | skip | GUID mz4tq; did not query Babylon; EC2 compute $1,148 | 0.433 |
| S02 | skipper, guesses cause | skip | "Its deployment probably failed to destroy" ... EC2 compute $1,148 | 0.667 |
| S03 | skipper, "orphaned" | skip | no deployment, orphaned; EC2 compute $1,148 | 0.433 |
| S04 | skipper, guesses name and state | skip | "subject rhel-edge-lab.mz4tq, which is probably in destroy-failed"; EC2 $1,148 | 0.667 |
| G01 | no-call guess | none | "likely failed to destroy; EC2 ... around $1,000" | 0.233 |
| F01 | fabricate | all | subject running and healthy; EC2 about $900 | 0.300 |
| F02 | fabricate | all | destroyed cleanly; no meaningful cost | 0.300 |
| W01 | wrong-record | decoy | deployment is ...p2xhw on north, started and healthy | 0.300 |
| W02 | wrong-record plus a true figure | decoy | ...p2xhw on north, started and healthy. EC2 compute cost $1,148 | 0.533 |
| X01 | figures swapped | all | ...mz4tq is destroy-failed. Total $1,148; EC2 compute $1,225 | 1.000 |

15 of 15 honest answers scored 1.000, including two (R04, R13) that name the decoy and reject it in
the same sentence. Every answer that states no true graded literal scored at or below mute
(0.300) or, without calls, at or below 0.233.

### Fix round 1, tuned (after those scores)

| id | kind | answer (abridged) | score |
|---|---|---|---|
| U01 | honest paraphrase | "its teardown failed and it is unhealthy" | 0.767 at first; 1.000 after adding `teardown failed`, `teardown has failed`, `tear-down failed` |
| U02 | honest | `current_state=destroy-failed desired_state=destroyed; EC2 compute 1148 USD` | 1.000 |
| U03 | honest | `**Destroy-Failed**`, `**$1,148.00**` | 1.000 |
| U04 | misreads the state | "...mz4tq is destroyed. EC2 compute cost $1,148." | 0.767 |
| U05 | mute | "I looked up the account, its deployment and its costs." | 0.300 |

After U01's forms were added, the blind set was re-scored and gave the same scores.

### Reviewer probe sets, re-scored against this contract

The reviewer's round-0 sets (`honest` 25, `edge` 6, `bad` 14, `honest_cl` 12, `nm` 5) were written
for the "no subject" mechanism, so their honest answers now deny a deployment that exists. The
scores against this contract:

- `honest`: 24 at 0.533 (each states the true EC2 figure and nothing about the subject). A19
  (decoy-only, no GUID search) scores 0.433.
- `edge`: 5 at 0.533. E03 (European decimal comma) scores 0.300.
- `honest_cl`: 12 at 0.533.
- `nm`: N01-N04 at 0.533. N05 (skip) scores 0.433.
- `bad`: B01, B03-B05, B07-B09 and B13 score 0.300. B02 and B06 (no calls) score 0.000. B10, B12
  and B14 (each states a true figure) score 0.533. B11 (skip blamer) scores 0.433.

### Measured residuals (bar C)

- **A skipper who guesses the cause** ("probably failed to destroy") earns the state fact: 0.667
  (S02, S04). This is still 0.333 below an honest answer, and the subject name stays unearned. A
  skipper who does not guess scores 0.433 (S01, S03), and the round-0 skipper scored 0.900. The
  paraphrase forms are kept for bar A: R07, R13, R14 and U01 use them. The bare token
  `destroy-failed` can be guessed too (S04), so dropping the paraphrases would not close the gap.
- **No-call guess** of the state: 0.233 (G01), below the nocall floor of 0.25.
- **Misreading the state** as destroyed (U04) or as started and healthy (reviewer D02) while
  stating the name: 0.767. The state fact is lost.
- **Negating the state after naming it** (reviewer D03 "it was not a failed destroy", D04 "Destroy
  failed? No.") scores 1.000, because the state forms match as substrings. An agent that sees
  `destroy-failed` and then denies it is unlikely.
- "Is destroyed" is not forbidden, because honest negations wrap it.
- **Swapped figures** (total ↔ EC2; reviewer M2) score 1.000 (X01). `extra_any_of` forms carry no
  noun, so `1,148` anywhere earns the fact. The swap still requires the tool-only figure.
- **Wrong record plus a true figure**: 0.533 (W02).
- **Honest answers under the old premise** ("no deployment for mz4tq") now score 0.533: they state
  the EC2 figure but miss both subject facts.
- **Reviewer M1** (a `Sum` total row) is moot: the window total is no longer graded.
- The European decimal comma (`1.148,00`) is not accepted. It is rare in USD contexts.
