# Baseline

**Mean reward 0.828 over the 194 measured tasks.** 91 of
them score 1.000. 6 tasks have no valid sample and are excluded;
they are listed below with the reason.

## Setup

| | |
|---|---|
| agent under test | parsec `28e2c40`, patched by `patch/parsec-simulation-redirect.patch` |
| agent model | `claude-sonnet-4-6`, through a LiteLLM gateway |
| simulation harness | simulation-harness `4f6ecca` (v0.2.0), five instances |
| simulation model | `azure/gpt-5.4`, one model call per simulated tool call |
| bundles | the five in `bundles/`, byte-identical to the ones measured |
| verifier | `tests/verify.py` as shipped in every task |
| samples | one scored sample per task, run sequentially, from runs between 2026-10-09 and 2026-10-16 |
| agent time | 8.1 hours, summed over the scored samples |

**Which sample is scored.** Each task's first sample, with two exceptions. A
sample ruled invalid because of the environment (a gateway failure, or a
simulated tool that timed out or contradicted the seed) is replaced by a valid
re-run. A task whose seed was corrected after its first sample is scored from a
sample taken after the correction. Every score is the current verifier's reading
of the stored transcript, so `baseline/<id>/verifier/` re-derives exactly from
`baseline/<id>/agent/agent.jsonl` and the task's contract.

**Read one number as one sample.** Every tool response is written by a model, so
a task's reward moves between runs with nothing changed. Compare per task, and
re-run a task before concluding anything from a single difference.

## By category

**Primary service**

| | tasks | scored | baseline mean |
|---|---:|---:|---:|
| platform | 104 | 100 | 0.871 |
| icinga | 38 | 37 | 0.776 |
| cloud | 29 | 28 | 0.685 |
| cost | 29 | 29 | 0.881 |

**Kind**

| | tasks | scored | baseline mean |
|---|---:|---:|---:|
| happy | 45 | 43 | 0.795 |
| trap | 117 | 115 | 0.851 |
| negative | 26 | 25 | 0.833 |
| chain breaks | 12 | 11 | 0.709 |

**Tranche.** Regression tasks are expected to score 1.000. Challenge tasks are
expected to score below it.

| | tasks | scored | baseline mean |
|---|---:|---:|---:|
| regression | 188 | 182 | 0.825 |
| challenge | 12 | 12 | 0.866 |

**Services per task**

| | tasks | scored | baseline mean |
|---|---:|---:|---:|
| 1 service | 131 | 129 | 0.854 |
| 2 services | 63 | 59 | 0.787 |
| 3 services | 6 | 6 | 0.662 |

## Rows to read with care

**Routing caps (24).** On these tasks parsec routed the question to a
sub-agent whose tool set lacks an expected tool, so the expected call could not
be made. The score measures parsec's routing decision, not its use of that tool.
Without them, the mean is 0.878.

- `bench-v4-cloud-060-marketplace-cost-not-in-usd` (0.400): measures parsec's routing, not its marketplace tool use (the cost sub-agent has no query_marketplace_agreements)
- `bench-v4-cloud-074-assigned-account-still-billing` (0.667): measures parsec's routing, not its cost tool use (the babylon sub-agent has no query_aws_costs)
- `bench-v4-cost-064-reservation-release-active-job-check` (0.760): measures parsec's routing, not its AAP2 tool use (the cost sub-agent has no query_aap2)
- `bench-v4-icinga-010-stuck-anarchysubjects` (0.495): measures parsec's routing, not its Icinga tool use (the babylon sub-agent has no query_icinga)
- `bench-v4-icinga-013-acknowledged-not-an-issue` (0.480): measures parsec's routing, not its Icinga tool use (the babylon sub-agent has no query_icinga)
- `bench-v4-icinga-072-alert-output-not-decoy-metrics` (0.000): measures parsec's routing, not its Icinga tool use (the ocpv sub-agent has no query_icinga)
- `bench-v4-platform-071-unmonitored-proxy-not-esxi-alert` (0.383): measures parsec's routing, not its Icinga tool use (the babylon sub-agent has no query_icinga)
- `bench-v5-cloud-304-marketplace-active-past-end` (0.229): measures parsec's routing, not its marketplace tool use (the cost sub-agent has no query_marketplace_agreements)
- `bench-v5-cloud-305-marketplace-vendor-org-wide` (0.114): measures parsec's routing, not its marketplace tool use (the cost sub-agent has no query_marketplace_agreements)
- `bench-v5-cloud-308-azure-leftover-tag-on-free-sub` (0.233): measures parsec's routing, not its Azure pools tool use (the babylon sub-agent has no query_azure_pools)
- `bench-v5-cloud-310-stopped-lab-restarted-billing` (0.783): measures parsec's routing, not its cost tool use (the babylon sub-agent has no query_aws_costs)
- `bench-v5-cloud-312-gcp-event-label-roster` (0.133): parsec routed to babylon, which lacks the expected query_gcp_projects; measures parsec's routing, not its use of that tool
- `bench-v5-cloud-315-min-cost-drops-unestimated` (0.267): parsec routed to cost, which lacks the expected query_marketplace_agreements; measures parsec's routing, not its use of that tool
- `bench-v5-cloud-316-cleaned-sandbox-live-iam-keys` (0.360): parsec routed to babylon+cost (scored re-run), which lacks the expected query_aws_account; measures parsec's routing, not its use of that tool
- `bench-v5-cloud-318-free-sandboxes-lack-ami-agreement` (0.725): parsec routed to security+babylon, which lacks the expected query_azure_pools; measures parsec's routing, not its use of that tool
- `bench-v5-cloud-319-billing-lab-unknown-to-babylon` (0.588): parsec routed to babylon+cost, which lacks the expected query_aws_account; measures parsec's routing, not its use of that tool
- `bench-v5-cost-410-released-sandbox-still-spending` (0.620): measures parsec's routing, not its AAP2 tool use (the cost sub-agent has no query_aap2)
- `bench-v5-cost-419-chargeback-predates-current-tenant` (0.554): parsec routed to cost+icinga, which lacks the expected query_aap2; measures parsec's routing, not its use of that tool
- `bench-v5-icinga-211-thresholds-file-never-deployed` (0.200): measures parsec's routing, not its Icinga/GitHub tool use (the cost sub-agent has no query_icinga, fetch_github_file or search_github_repo); no tool call at all, which the agent states
- `bench-v5-icinga-213-host-down-is-paused-vm` (0.550): measures parsec's routing, not its OCPV tool use (the icinga sub-agent has no query_ocpv_cluster)
- `bench-v5-icinga-225-monitor-outlived-its-namespace` (0.671): parsec routed to icinga+babylon, which lacks the expected query_ocpv_cluster; measures parsec's routing, not its use of that tool
- `bench-v5-platform-125-controller-reboot-not-the-playbook` (0.550): measures parsec's routing, not its AAP2 tool use (the icinga sub-agent has no query_aap2)
- `bench-v5-platform-157-drain-blocked-by-node-local-disk` (0.836): parsec routed to ocpv, which lacks the expected query_aap2; measures parsec's routing, not its use of that tool
- `bench-v5-platform-159-renewal-run-never-saw-host` (0.702): parsec routed to aap2+babylon, which lacks the expected query_icinga; measures parsec's routing, not its use of that tool

**Known simulation divergences.** The simulation departs from the documented
behaviour in a way the task survives. The graded facts stay reachable, and the
score is reported as measured.

- `bench-v5-platform-120-errors-only-matches-are-not-errors` (0.680): the errors_only search drops the row whose only match is error=false, so the agent sees 4 hits where the instruction says 5; graded facts remain reachable
- `bench-v5-platform-131-deployment-first-resource-blind-spot` (1.000): list_deployments `guid` does not fall back to instance_vars.guid, so the healthy-looking deployment the trap depends on never appears; required facts remain reachable

## Unmeasured (6)

These tasks are in no mean.

- `bench-v4-icinga-014-check-script-path-moved`: Both samples (0.550, 0.550) were invalid: search_github_repo answers only the exact seeded search key, so the graded file was never reached, and get_services returned [] for a valid filter_expr on 2 of 2 samples
- `bench-v5-cloud-306-account-db-reservation-none-free`: The simulator matches query_aws_account_db `reservation` exactly, not as the documented substring, so the two gpu-ee-dryrun rows never come back; required fact dryrun-is-different is unreachable and the forbidden trap can never fire
- `bench-v5-platform-102-no-proxy-misses-api-domain`: Its seed was corrected after its first sample; every sample taken after the correction failed on the environment (gateway rate limits, model API timeouts or simulated-tool timeouts), so no valid sample exists.
- `bench-v5-platform-104-cfn-dependency-and-what-changed`: Its seed was corrected after its first sample; every sample taken after the correction failed on the environment (gateway rate limits, model API timeouts or simulated-tool timeouts), so no valid sample exists.
- `bench-v5-platform-107-host-pattern-skipped-play`: Its seed was corrected after its first sample; every sample taken after the correction failed on the environment (gateway rate limits, model API timeouts or simulated-tool timeouts), so no valid sample exists.
- `bench-v5-platform-115-find-jobs-default-page-not-the-total`: The simulator ignores find_jobs `created_before` (and once `max_results:200`), so two October decoy jobs leak in and the graded counts become 59/20 instead of the seeded 57/19

## Every task

`reward = completion × (w_tool × tool_calls + w_answer × answer)`, with each
task's own weights in its `tests/expected.json`. The id links to the stored
trajectory and verifier output. `baseline/results.json` has the same rows, plus
each task's services, tools and chain length.

| id | kind | tranche | reward | completion | tool_calls | answer | agent s | note |
|---|---|---|---:|---:|---:|---:|---:|---|
| [`bench-v4-platform-001-ee-entrypoint-rca`](baseline/bench-v4-platform-001-ee-entrypoint-rca/) | happy | regression | **0.525** | 1 | 0.000 | 0.750 | 228 |  |
| [`bench-v4-platform-002-collection-not-found-rca`](baseline/bench-v4-platform-002-collection-not-found-rca/) | happy | regression | **0.860** | 1 | 1.000 | 0.800 | 212 |  |
| [`bench-v4-platform-003-tojson-dict-literal-rca`](baseline/bench-v4-platform-003-tojson-dict-literal-rca/) | happy | regression | **0.420** | 1 | 0.000 | 0.600 | 337 |  |
| [`bench-v4-platform-004-events-then-config`](baseline/bench-v4-platform-004-events-then-config/) | happy | regression | **0.733** | 1 | 0.500 | 0.833 | 69 |  |
| [`bench-v4-platform-005-wrong-owner-trap`](baseline/bench-v4-platform-005-wrong-owner-trap/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 111 |  |
| [`bench-v4-platform-006-version-tag-not-a-ref`](baseline/bench-v4-platform-006-version-tag-not-a-ref/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 64 |  |
| [`bench-v4-platform-007-directory-path-fetch`](baseline/bench-v4-platform-007-directory-path-fetch/) | trap | regression | **0.850** | 1 | 0.500 | 1.000 | 40 |  |
| [`bench-v4-platform-008-log-does-not-say`](baseline/bench-v4-platform-008-log-does-not-say/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 195 |  |
| [`bench-v4-platform-009-catalog-item-no-config`](baseline/bench-v4-platform-009-catalog-item-no-config/) | chain breaks | regression | **0.825** | 1 | 1.000 | 0.750 | 146 |  |
| [`bench-v4-platform-018-find-jobs-window`](baseline/bench-v4-platform-018-find-jobs-window/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 34 |  |
| [`bench-v4-platform-019-anarchysubject-state`](baseline/bench-v4-platform-019-anarchysubject-state/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 54 |  |
| [`bench-v4-platform-020-ocpv-vm-inventory`](baseline/bench-v4-platform-020-ocpv-vm-inventory/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 61 |  |
| [`bench-v4-platform-021-babylon-missing-cluster-trap`](baseline/bench-v4-platform-021-babylon-missing-cluster-trap/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 37 |  |
| [`bench-v4-platform-022-job-on-no-controller`](baseline/bench-v4-platform-022-job-on-no-controller/) | negative | regression | **0.700** | 1 | 0.000 | 1.000 | 55 |  |
| [`bench-v4-platform-023-splunk-guid-no-events`](baseline/bench-v4-platform-023-splunk-guid-no-events/) | chain breaks | regression | **1.000** | 1 | 1.000 | 1.000 | 70 |  |
| [`bench-v4-platform-031-helm-url-not-a-timeout`](baseline/bench-v4-platform-031-helm-url-not-a-timeout/) | trap | challenge | **0.840** | 1 | 0.800 | 0.857 | 366 |  |
| [`bench-v4-platform-032-shared-secret-not-a-registry-outage`](baseline/bench-v4-platform-032-shared-secret-not-a-registry-outage/) | trap | challenge | **1.000** | 1 | 1.000 | 1.000 | 169 |  |
| [`bench-v4-platform-033-schema-change-not-the-oom`](baseline/bench-v4-platform-033-schema-change-not-the-oom/) | trap | challenge | **0.786** | 1 | 1.000 | 0.714 | 102 |  |
| [`bench-v4-platform-034-rate-limit-not-an-outage`](baseline/bench-v4-platform-034-rate-limit-not-an-outage/) | trap | challenge | **0.847** | 1 | 0.750 | 0.889 | 236 |  |
| [`bench-v4-platform-036-secret-redacted-not-absent`](baseline/bench-v4-platform-036-secret-redacted-not-absent/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 61 |  |
| [`bench-v4-platform-037-ocpv-healthy-vm-degraded-machineset`](baseline/bench-v4-platform-037-ocpv-healthy-vm-degraded-machineset/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 103 |  |
| [`bench-v4-platform-038-anarchy-subject-guid-cross-cluster`](baseline/bench-v4-platform-038-anarchy-subject-guid-cross-cluster/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 53 |  |
| [`bench-v4-platform-040-workshop-cross-cluster-name-search`](baseline/bench-v4-platform-040-workshop-cross-cluster-name-search/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 69 |  |
| [`bench-v4-platform-041-resource-pool-unfiltered-list`](baseline/bench-v4-platform-041-resource-pool-unfiltered-list/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 58 |  |
| [`bench-v4-platform-042-deployment-via-resource-claim`](baseline/bench-v4-platform-042-deployment-via-resource-claim/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 54 |  |
| [`bench-v4-platform-043-multiworkshop-asset-failure`](baseline/bench-v4-platform-043-multiworkshop-asset-failure/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 70 |  |
| [`bench-v4-platform-044-search-catalog-env-type`](baseline/bench-v4-platform-044-search-catalog-env-type/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 33 |  |
| [`bench-v4-platform-062-provisioning-job-trace`](baseline/bench-v4-platform-062-provisioning-job-trace/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 135 |  |
| [`bench-v4-platform-065-other-guid-job-not-the-failure`](baseline/bench-v4-platform-065-other-guid-job-not-the-failure/) | trap | regression | **0.860** | 1 | 1.000 | 0.800 | 124 |  |
| [`bench-v4-platform-066-per-guid-cluster-and-lifespan`](baseline/bench-v4-platform-066-per-guid-cluster-and-lifespan/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 133 |  |
| [`bench-v4-platform-067-branch-name-not-the-cause`](baseline/bench-v4-platform-067-branch-name-not-the-cause/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 60 |  |
| [`bench-v4-platform-068-deprecation-warning-not-the-fatal`](baseline/bench-v4-platform-068-deprecation-warning-not-the-fatal/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 85 |  |
| [`bench-v4-platform-069-typo-variable-not-located`](baseline/bench-v4-platform-069-typo-variable-not-located/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 62 |  |
| [`bench-v4-platform-070-invented-fix-variables`](baseline/bench-v4-platform-070-invented-fix-variables/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 66 |  |
| [`bench-v4-platform-071-unmonitored-proxy-not-esxi-alert`](baseline/bench-v4-platform-071-unmonitored-proxy-not-esxi-alert/) | trap | regression | **0.383** | 1 | 0.500 | 0.333 | 135 | routing cap |
| [`bench-v5-platform-101-vcpu-quota-from-catalog-sizing`](baseline/bench-v5-platform-101-vcpu-quota-from-catalog-sizing/) | happy | regression | **0.800** | 1 | 1.000 | 0.714 | 222 |  |
| `bench-v5-platform-102-no-proxy-misses-api-domain` | happy | regression | UNMEASURED | | | | | see below |
| [`bench-v5-platform-103-olm-channel-not-in-catalog`](baseline/bench-v5-platform-103-olm-channel-not-in-catalog/) | happy | regression | **0.860** | 1 | 1.000 | 0.800 | 129 |  |
| `bench-v5-platform-104-cfn-dependency-and-what-changed` | happy | regression | UNMEASURED | | | | | see below |
| [`bench-v5-platform-105-failed-revision-not-main`](baseline/bench-v5-platform-105-failed-revision-not-main/) | trap | regression | **0.710** | 1 | 0.500 | 0.800 | 206 |  |
| [`bench-v5-platform-106-yaml-float-version`](baseline/bench-v5-platform-106-yaml-float-version/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 197 |  |
| `bench-v5-platform-107-host-pattern-skipped-play` | trap | regression | UNMEASURED | | | | | see below |
| [`bench-v5-platform-108-duplicate-guid-concurrent-run`](baseline/bench-v5-platform-108-duplicate-guid-concurrent-run/) | trap | regression | **0.783** | 1 | 0.667 | 0.833 | 2106 |  |
| [`bench-v5-platform-109-quoted-false-is-truthy`](baseline/bench-v5-platform-109-quoted-false-is-truthy/) | trap | regression | **0.325** | 1 | 0.500 | 0.250 | 1477 |  |
| [`bench-v5-platform-110-renamed-catalog-item`](baseline/bench-v5-platform-110-renamed-catalog-item/) | chain breaks | regression | **0.875** | 1 | 1.000 | 0.833 | 329 |  |
| [`bench-v5-platform-111-recycled-sandbox-swallowed-teardown`](baseline/bench-v5-platform-111-recycled-sandbox-swallowed-teardown/) | trap | challenge | **0.940** | 1 | 0.800 | 1.000 | 1392 |  |
| [`bench-v5-platform-112-exec-pool-disk-not-the-bastion`](baseline/bench-v5-platform-112-exec-pool-disk-not-the-bastion/) | trap | challenge | **0.838** | 1 | 0.750 | 0.875 | 1094 |  |
| [`bench-v5-platform-113-account-region-override-not-capacity`](baseline/bench-v5-platform-113-account-region-override-not-capacity/) | trap | challenge | **1.000** | 1 | 1.000 | 1.000 | 937 |  |
| [`bench-v5-platform-114-ee-nightly-float-not-a-commit`](baseline/bench-v5-platform-114-ee-nightly-float-not-a-commit/) | trap | challenge | **1.000** | 1 | 1.000 | 1.000 | 311 |  |
| `bench-v5-platform-115-find-jobs-default-page-not-the-total` | trap | regression | UNMEASURED | | | | | see below |
| [`bench-v5-platform-116-timeout-headroom-from-history`](baseline/bench-v5-platform-116-timeout-headroom-from-history/) | happy | regression | **0.675** | 1 | 0.500 | 0.750 | 127 |  |
| [`bench-v5-platform-117-dependency-project-sync-failed`](baseline/bench-v5-platform-117-dependency-project-sync-failed/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 2015 |  |
| [`bench-v5-platform-118-pending-pvcs-wait-for-first-consumer`](baseline/bench-v5-platform-118-pending-pvcs-wait-for-first-consumer/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 206 |  |
| [`bench-v5-platform-119-pvc-storage-class-not-on-cluster`](baseline/bench-v5-platform-119-pvc-storage-class-not-on-cluster/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 61 |  |
| [`bench-v5-platform-120-errors-only-matches-are-not-errors`](baseline/bench-v5-platform-120-errors-only-matches-are-not-errors/) | negative | regression | **0.680** | 1 | 1.000 | 0.600 | 206 | simulation divergence |
| [`bench-v5-platform-121-near-miss-pick-partner-repo`](baseline/bench-v5-platform-121-near-miss-pick-partner-repo/) | trap | regression | **0.500** | 1 | 0.500 | 0.500 | 1305 |  |
| [`bench-v5-platform-122-search-total-not-page`](baseline/bench-v5-platform-122-search-total-not-page/) | trap | regression | **0.720** | 1 | 1.000 | 0.600 | 82 |  |
| [`bench-v5-platform-123-prod-stage-overrides-common`](baseline/bench-v5-platform-123-prod-stage-overrides-common/) | happy | regression | **0.912** | 1 | 1.000 | 0.875 | 58 |  |
| [`bench-v5-platform-124-event-accounts-not-returned`](baseline/bench-v5-platform-124-event-accounts-not-returned/) | chain breaks | regression | **0.900** | 1 | 1.000 | 0.857 | 386 |  |
| [`bench-v5-platform-125-controller-reboot-not-the-playbook`](baseline/bench-v5-platform-125-controller-reboot-not-the-playbook/) | trap | regression | **0.550** | 1 | 0.500 | 0.571 | 46 | routing cap |
| [`bench-v5-platform-126-stop-job-from-tower-jobs`](baseline/bench-v5-platform-126-stop-job-from-tower-jobs/) | happy | regression | **0.850** | 1 | 0.500 | 1.000 | 50 |  |
| [`bench-v5-platform-127-catalog-keyword-match-prod-stage`](baseline/bench-v5-platform-127-catalog-keyword-match-prod-stage/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 35 |  |
| [`bench-v5-platform-128-failed-action-census-by-kind`](baseline/bench-v5-platform-128-failed-action-census-by-kind/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 51 |  |
| [`bench-v5-platform-129-destroyed-subject-hidden-without-guid`](baseline/bench-v5-platform-129-destroyed-subject-hidden-without-guid/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 35 |  |
| [`bench-v5-platform-130-destroy-failed-retry-pending`](baseline/bench-v5-platform-130-destroy-failed-retry-pending/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 161 |  |
| [`bench-v5-platform-131-deployment-first-resource-blind-spot`](baseline/bench-v5-platform-131-deployment-first-resource-blind-spot/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 112 | simulation divergence |
| [`bench-v5-platform-132-event-seat-math-standalone-workshop`](baseline/bench-v5-platform-132-event-seat-math-standalone-workshop/) | trap | regression | **0.710** | 1 | 0.500 | 0.800 | 54 |  |
| [`bench-v5-platform-133-component-sub-components-hop`](baseline/bench-v5-platform-133-component-sub-components-hop/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 66 |  |
| [`bench-v5-platform-134-pool-search-canary-two-clusters`](baseline/bench-v5-platform-134-pool-search-canary-two-clusters/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 38 |  |
| [`bench-v5-platform-135-catalog-component-drift-fanout`](baseline/bench-v5-platform-135-catalog-component-drift-fanout/) | trap | regression | **0.505** | 1 | 0.750 | 0.400 | 242 |  |
| [`bench-v5-platform-136-provision-key-mode-too-open`](baseline/bench-v5-platform-136-provision-key-mode-too-open/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 105 |  |
| [`bench-v5-platform-137-generated-password-forbidden-chars`](baseline/bench-v5-platform-137-generated-password-forbidden-chars/) | happy | regression | **0.850** | 1 | 0.500 | 1.000 | 397 |  |
| [`bench-v5-platform-138-project-prefix-not-a-dns-label`](baseline/bench-v5-platform-138-project-prefix-not-a-dns-label/) | happy | regression | **0.883** | 1 | 1.000 | 0.833 | 85 |  |
| [`bench-v5-platform-139-ami-id-pinned-to-one-region`](baseline/bench-v5-platform-139-ami-id-pinned-to-one-region/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 107 |  |
| [`bench-v5-platform-140-lookup-normalises-underscore-path`](baseline/bench-v5-platform-140-lookup-normalises-underscore-path/) | trap | regression | **0.860** | 1 | 1.000 | 0.800 | 170 |  |
| [`bench-v5-platform-141-nested-loop-item-collision`](baseline/bench-v5-platform-141-nested-loop-item-collision/) | trap | regression | **0.883** | 1 | 1.000 | 0.833 | 79 |  |
| [`bench-v5-platform-142-duplicate-yaml-key-last-wins`](baseline/bench-v5-platform-142-duplicate-yaml-key-last-wins/) | trap | regression | **0.883** | 1 | 1.000 | 0.833 | 98 |  |
| [`bench-v5-platform-143-empty-storage-class-skips-default`](baseline/bench-v5-platform-143-empty-storage-class-skips-default/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 300 |  |
| [`bench-v5-platform-144-version-compared-as-string`](baseline/bench-v5-platform-144-version-compared-as-string/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 98 |  |
| [`bench-v5-platform-145-prod-stage-deploys-from-fork`](baseline/bench-v5-platform-145-prod-stage-deploys-from-fork/) | chain breaks | regression | **0.342** | 1 | 0.750 | 0.167 | 186 |  |
| [`bench-v5-platform-146-assumed-role-session-outlived`](baseline/bench-v5-platform-146-assumed-role-session-outlived/) | trap | challenge | **1.000** | 1 | 1.000 | 1.000 | 224 |  |
| [`bench-v5-platform-147-fail-closed-webhook-no-endpoints`](baseline/bench-v5-platform-147-fail-closed-webhook-no-endpoints/) | trap | challenge | **0.438** | 1 | 0.000 | 0.625 | 90 |  |
| [`bench-v5-platform-148-precheck-caches-nxdomain`](baseline/bench-v5-platform-148-precheck-caches-nxdomain/) | trap | challenge | **0.750** | 1 | 0.750 | 0.750 | 95 |  |
| [`bench-v5-platform-149-alphabetised-workloads-before-operator`](baseline/bench-v5-platform-149-alphabetised-workloads-before-operator/) | trap | challenge | **0.950** | 1 | 0.800 | 1.000 | 289 |  |
| [`bench-v5-platform-150-retiring-instance-is-sole-gpu-machine`](baseline/bench-v5-platform-150-retiring-instance-is-sole-gpu-machine/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 45 |  |
| [`bench-v5-platform-151-backup-schedule-is-commented-out`](baseline/bench-v5-platform-151-backup-schedule-is-commented-out/) | negative | regression | **0.800** | 1 | 1.000 | 0.750 | 42 |  |
| [`bench-v5-platform-152-path-search-cannot-find-variable-uses`](baseline/bench-v5-platform-152-path-search-cannot-find-variable-uses/) | trap | regression | **0.922** | 1 | 1.000 | 0.889 | 53 |  |
| [`bench-v5-platform-153-override-uses-removed-variable-name`](baseline/bench-v5-platform-153-override-uses-removed-variable-name/) | trap | regression | **0.922** | 1 | 1.000 | 0.889 | 50 |  |
| [`bench-v5-platform-154-change-touched-unscoped-host`](baseline/bench-v5-platform-154-change-touched-unscoped-host/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 95 |  |
| [`bench-v5-platform-155-order-time-was-queue-wait`](baseline/bench-v5-platform-155-order-time-was-queue-wait/) | happy | regression | **0.617** | 1 | 0.500 | 0.667 | 118 |  |
| [`bench-v5-platform-156-ignored-probe-failures-lab-is-fine`](baseline/bench-v5-platform-156-ignored-probe-failures-lab-is-fine/) | negative | regression | **0.850** | 1 | 0.500 | 1.000 | 196 |  |
| [`bench-v5-platform-157-drain-blocked-by-node-local-disk`](baseline/bench-v5-platform-157-drain-blocked-by-node-local-disk/) | trap | regression | **0.836** | 1 | 0.667 | 0.909 | 82 | routing cap |
| [`bench-v5-platform-158-lab-instances-outside-default-region`](baseline/bench-v5-platform-158-lab-instances-outside-default-region/) | trap | regression | **0.275** | 1 | 0.333 | 0.250 | 93 |  |
| [`bench-v5-platform-159-renewal-run-never-saw-host`](baseline/bench-v5-platform-159-renewal-run-never-saw-host/) | chain breaks | regression | **0.702** | 1 | 0.667 | 0.714 | 86 | routing cap |
| [`bench-v5-platform-160-event-attendee-codes-any-cluster`](baseline/bench-v5-platform-160-event-attendee-codes-any-cluster/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 44 |  |
| [`bench-v5-platform-161-pool-unclaimed-lifespan-not-the-ceiling`](baseline/bench-v5-platform-161-pool-unclaimed-lifespan-not-the-ceiling/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 35 |  |
| [`bench-v5-platform-162-shared-session-needs-multiuser-item`](baseline/bench-v5-platform-162-shared-session-needs-multiuser-item/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 45 |  |
| [`bench-v5-platform-163-cloned-workshop-name-needs-namespace`](baseline/bench-v5-platform-163-cloned-workshop-name-needs-namespace/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 82 |  |
| [`bench-v5-platform-164-workshop-item-replaced-by-v2`](baseline/bench-v5-platform-164-workshop-item-replaced-by-v2/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 140 |  |
| [`bench-v5-platform-165-renamed-item-same-asset-uuid`](baseline/bench-v5-platform-165-renamed-item-same-asset-uuid/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 99 |  |
| [`bench-v5-platform-166-failed-stop-job-already-retried`](baseline/bench-v5-platform-166-failed-stop-job-already-retried/) | trap | regression | **0.700** | 1 | 0.000 | 1.000 | 69 |  |
| [`bench-v5-platform-167-ordered-workers-override-default`](baseline/bench-v5-platform-167-ordered-workers-override-default/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 76 |  |
| [`bench-v5-platform-168-event-stage-component-not-prod`](baseline/bench-v5-platform-168-event-stage-component-not-prod/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 160 |  |
| [`bench-v5-platform-169-failed-claims-still-need-cleanup`](baseline/bench-v5-platform-169-failed-claims-still-need-cleanup/) | trap | regression | **0.912** | 1 | 1.000 | 0.875 | 109 |  |
| [`bench-v4-icinga-010-stuck-anarchysubjects`](baseline/bench-v4-icinga-010-stuck-anarchysubjects/) | happy | regression | **0.495** | 1 | 0.250 | 0.600 | 46 | routing cap |
| [`bench-v4-icinga-011-aap2-job-status-alert`](baseline/bench-v4-icinga-011-aap2-job-status-alert/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 57 |  |
| [`bench-v4-icinga-012-nodes-ready-threshold`](baseline/bench-v4-icinga-012-nodes-ready-threshold/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 41 |  |
| [`bench-v4-icinga-013-acknowledged-not-an-issue`](baseline/bench-v4-icinga-013-acknowledged-not-an-issue/) | negative | regression | **0.480** | 1 | 0.000 | 0.600 | 10 | routing cap |
| `bench-v4-icinga-014-check-script-path-moved` | chain breaks | regression | UNMEASURED | | | | | see below |
| [`bench-v4-icinga-015-problems-by-severity`](baseline/bench-v4-icinga-015-problems-by-severity/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 42 |  |
| [`bench-v4-icinga-016-hosts-most-problems`](baseline/bench-v4-icinga-016-hosts-most-problems/) | happy | regression | **0.840** | 1 | 1.000 | 0.800 | 43 |  |
| [`bench-v4-icinga-017-invented-action-trap`](baseline/bench-v4-icinga-017-invented-action-trap/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 37 |  |
| [`bench-v4-icinga-045-hosts-search-filter`](baseline/bench-v4-icinga-045-hosts-search-filter/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 39 |  |
| [`bench-v4-icinga-046-services-search-cross-host`](baseline/bench-v4-icinga-046-services-search-cross-host/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 33 |  |
| [`bench-v4-icinga-047-downtime-similar-host-names`](baseline/bench-v4-icinga-047-downtime-similar-host-names/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 30 |  |
| [`bench-v4-icinga-048-comment-service-vs-host-scope`](baseline/bench-v4-icinga-048-comment-service-vs-host-scope/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 28 |  |
| [`bench-v4-icinga-072-alert-output-not-decoy-metrics`](baseline/bench-v4-icinga-072-alert-output-not-decoy-metrics/) | trap | regression | **0.000** | 1 | 0.000 | 0.000 | 88 | routing cap |
| [`bench-v5-icinga-201-soft-critical-not-yet-hard`](baseline/bench-v5-icinga-201-soft-critical-not-yet-hard/) | trap | regression | **0.883** | 1 | 1.000 | 0.833 | 33 |  |
| [`bench-v5-icinga-202-flapping-recovery-is-not-resolution`](baseline/bench-v5-icinga-202-flapping-recovery-is-not-resolution/) | trap | regression | **0.867** | 1 | 1.000 | 0.833 | 81 |  |
| [`bench-v5-icinga-203-perfdata-headroom-to-critical`](baseline/bench-v5-icinga-203-perfdata-headroom-to-critical/) | happy | regression | **0.480** | 1 | 0.000 | 0.600 | 96 |  |
| [`bench-v5-icinga-204-downtime-window-expired`](baseline/bench-v5-icinga-204-downtime-window-expired/) | trap | regression | **0.600** | 1 | 1.000 | 0.500 | 34 |  |
| [`bench-v5-icinga-205-notifications-disabled-nobody-paged`](baseline/bench-v5-icinga-205-notifications-disabled-nobody-paged/) | happy | regression | **0.733** | 1 | 1.000 | 0.667 | 211 |  |
| [`bench-v5-icinga-206-stale-ok-check`](baseline/bench-v5-icinga-206-stale-ok-check/) | trap | regression | **0.733** | 1 | 1.000 | 0.667 | 51 |  |
| [`bench-v5-icinga-207-host-down-masks-service-alerts`](baseline/bench-v5-icinga-207-host-down-masks-service-alerts/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 44 |  |
| [`bench-v5-icinga-208-service-not-monitored`](baseline/bench-v5-icinga-208-service-not-monitored/) | negative | regression | **0.400** | 1 | 1.000 | 0.250 | 85 |  |
| [`bench-v5-icinga-209-backup-freshness-upstream-service`](baseline/bench-v5-icinga-209-backup-freshness-upstream-service/) | happy | regression | **0.333** | 1 | 0.333 | 0.333 | 259 |  |
| [`bench-v5-icinga-210-command-vars-override-script-default`](baseline/bench-v5-icinga-210-command-vars-override-script-default/) | trap | regression | **0.883** | 1 | 1.000 | 0.833 | 82 |  |
| [`bench-v5-icinga-211-thresholds-file-never-deployed`](baseline/bench-v5-icinga-211-thresholds-file-never-deployed/) | chain breaks | regression | **0.200** | 1 | 0.000 | 0.286 | 10 | routing cap |
| [`bench-v5-icinga-212-fix-on-main-not-on-pinned-ref`](baseline/bench-v5-icinga-212-fix-on-main-not-on-pinned-ref/) | trap | regression | **0.800** | 1 | 1.000 | 0.714 | 198 |  |
| [`bench-v5-icinga-213-host-down-is-paused-vm`](baseline/bench-v5-icinga-213-host-down-is-paused-vm/) | happy | regression | **0.550** | 1 | 0.500 | 0.571 | 319 | routing cap |
| [`bench-v5-icinga-214-hostgroup-membership-rollup`](baseline/bench-v5-icinga-214-hostgroup-membership-rollup/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 34 |  |
| [`bench-v5-icinga-215-ack-comment-author-and-expiry`](baseline/bench-v5-icinga-215-ack-comment-author-and-expiry/) | happy | regression | **0.657** | 1 | 1.000 | 0.571 | 39 |  |
| [`bench-v5-icinga-216-flexible-downtime-duration`](baseline/bench-v5-icinga-216-flexible-downtime-duration/) | happy | regression | **0.767** | 1 | 1.000 | 0.667 | 30 |  |
| [`bench-v5-icinga-217-longest-open-problem`](baseline/bench-v5-icinga-217-longest-open-problem/) | happy | regression | **0.883** | 1 | 1.000 | 0.833 | 34 |  |
| [`bench-v5-icinga-218-host-downtime-leaves-services-live`](baseline/bench-v5-icinga-218-host-downtime-leaves-services-live/) | trap | regression | **0.800** | 1 | 0.000 | 1.000 | 40 |  |
| [`bench-v5-icinga-219-host-down-pings-old-address`](baseline/bench-v5-icinga-219-host-down-pings-old-address/) | trap | regression | **0.771** | 1 | 1.000 | 0.714 | 79 |  |
| [`bench-v5-icinga-220-no-p99-in-latency-check`](baseline/bench-v5-icinga-220-no-p99-in-latency-check/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 32 |  |
| [`bench-v5-icinga-221-crc-counter-never-resets`](baseline/bench-v5-icinga-221-crc-counter-never-resets/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 80 |  |
| [`bench-v5-icinga-222-lag-check-runs-on-satellite`](baseline/bench-v5-icinga-222-lag-check-runs-on-satellite/) | trap | regression | **0.900** | 1 | 0.667 | 1.000 | 138 |  |
| [`bench-v5-icinga-223-executed-plugin-not-the-shell-twin`](baseline/bench-v5-icinga-223-executed-plugin-not-the-shell-twin/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 105 |  |
| [`bench-v5-icinga-224-dead-first-replica-eats-timeout`](baseline/bench-v5-icinga-224-dead-first-replica-eats-timeout/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 343 |  |
| [`bench-v5-icinga-225-monitor-outlived-its-namespace`](baseline/bench-v5-icinga-225-monitor-outlived-its-namespace/) | chain breaks | regression | **0.671** | 1 | 0.500 | 0.714 | 162 | routing cap |
| [`bench-v4-cloud-024-guid-to-account`](baseline/bench-v4-cloud-024-guid-to-account/) | happy | regression | **0.200** | 1 | 0.000 | 0.250 | 10 |  |
| [`bench-v4-cloud-025-gcp-project-status`](baseline/bench-v4-cloud-025-gcp-project-status/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 29 |  |
| [`bench-v4-cloud-026-gpu-abuse-triage`](baseline/bench-v4-cloud-026-gpu-abuse-triage/) | chain breaks | regression | **0.925** | 1 | 0.750 | 1.000 | 116 |  |
| [`bench-v4-cloud-027-azure-pool-database-trap`](baseline/bench-v4-cloud-027-azure-pool-database-trap/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 54 |  |
| [`bench-v4-cloud-055-azure-subscription-not-found`](baseline/bench-v4-cloud-055-azure-subscription-not-found/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 39 |  |
| [`bench-v4-cloud-057-cloudtrail-select-only-refusal`](baseline/bench-v4-cloud-057-cloudtrail-select-only-refusal/) | trap | regression | **0.400** | 1 | 0.000 | 0.500 | 10 |  |
| [`bench-v4-cloud-058-malformed-account-id`](baseline/bench-v4-cloud-058-malformed-account-id/) | trap | regression | **0.600** | 1 | 0.000 | 0.750 | 10 |  |
| [`bench-v4-cloud-059-blank-owner-email-fallback`](baseline/bench-v4-cloud-059-blank-owner-email-fallback/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 38 |  |
| [`bench-v4-cloud-060-marketplace-cost-not-in-usd`](baseline/bench-v4-cloud-060-marketplace-cost-not-in-usd/) | trap | regression | **0.400** | 1 | 0.000 | 0.500 | 55 | routing cap |
| [`bench-v4-cloud-074-assigned-account-still-billing`](baseline/bench-v4-cloud-074-assigned-account-still-billing/) | trap | regression | **0.667** | 1 | 0.667 | 0.667 | 78 | routing cap |
| [`bench-v5-cloud-301-gcp-delete-counter-not-a-state`](baseline/bench-v5-cloud-301-gcp-delete-counter-not-a-state/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 76 |  |
| [`bench-v5-cloud-302-cloudtrail-local-time-window`](baseline/bench-v5-cloud-302-cloudtrail-local-time-window/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 46 |  |
| [`bench-v5-cloud-303-lookup-events-resource-names-instance`](baseline/bench-v5-cloud-303-lookup-events-resource-names-instance/) | trap | regression | **0.800** | 1 | 1.000 | 0.750 | 92 |  |
| [`bench-v5-cloud-304-marketplace-active-past-end`](baseline/bench-v5-cloud-304-marketplace-active-past-end/) | trap | regression | **0.229** | 1 | 0.000 | 0.286 | 72 | routing cap |
| [`bench-v5-cloud-305-marketplace-vendor-org-wide`](baseline/bench-v5-cloud-305-marketplace-vendor-org-wide/) | happy | regression | **0.114** | 1 | 0.000 | 0.143 | 162 | routing cap |
| `bench-v5-cloud-306-account-db-reservation-none-free` | negative | regression | UNMEASURED | | | | | see below |
| [`bench-v5-cloud-307-azure-two-project-tags`](baseline/bench-v5-cloud-307-azure-two-project-tags/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 54 |  |
| [`bench-v5-cloud-308-azure-leftover-tag-on-free-sub`](baseline/bench-v5-cloud-308-azure-leftover-tag-on-free-sub/) | trap | regression | **0.233** | 1 | 0.000 | 0.333 | 82 | routing cap |
| [`bench-v5-cloud-309-deleted-iam-user-trail-remains`](baseline/bench-v5-cloud-309-deleted-iam-user-trail-remains/) | chain breaks | regression | **0.767** | 1 | 1.000 | 0.667 | 136 |  |
| [`bench-v5-cloud-310-stopped-lab-restarted-billing`](baseline/bench-v5-cloud-310-stopped-lab-restarted-billing/) | trap | regression | **0.783** | 1 | 0.667 | 0.833 | 97 | routing cap |
| [`bench-v5-cloud-311-owner-handover-inventory`](baseline/bench-v5-cloud-311-owner-handover-inventory/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 57 |  |
| [`bench-v5-cloud-312-gcp-event-label-roster`](baseline/bench-v5-cloud-312-gcp-event-label-roster/) | happy | regression | **0.133** | 1 | 0.000 | 0.167 | 30 | routing cap |
| [`bench-v5-cloud-313-azure-no-single-pool-fits`](baseline/bench-v5-cloud-313-azure-no-single-pool-fits/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 48 |  |
| [`bench-v5-cloud-314-deleterule-two-event-sources`](baseline/bench-v5-cloud-314-deleterule-two-event-sources/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 107 |  |
| [`bench-v5-cloud-315-min-cost-drops-unestimated`](baseline/bench-v5-cloud-315-min-cost-drops-unestimated/) | trap | regression | **0.267** | 1 | 0.000 | 0.333 | 176 | routing cap |
| [`bench-v5-cloud-316-cleaned-sandbox-live-iam-keys`](baseline/bench-v5-cloud-316-cleaned-sandbox-live-iam-keys/) | trap | regression | **0.360** | 1 | 0.500 | 0.300 | 76 | routing cap |
| [`bench-v5-cloud-317-namesake-user-other-account`](baseline/bench-v5-cloud-317-namesake-user-other-account/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 56 |  |
| [`bench-v5-cloud-318-free-sandboxes-lack-ami-agreement`](baseline/bench-v5-cloud-318-free-sandboxes-lack-ami-agreement/) | negative | regression | **0.725** | 1 | 0.667 | 0.750 | 120 | routing cap |
| [`bench-v5-cloud-319-billing-lab-unknown-to-babylon`](baseline/bench-v5-cloud-319-billing-lab-unknown-to-babylon/) | chain breaks | regression | **0.588** | 1 | 0.500 | 0.625 | 168 | routing cap |
| [`bench-v4-cost-028-highest-spend-provider`](baseline/bench-v4-cost-028-highest-spend-provider/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 52 |  |
| [`bench-v4-cost-029-no-cost-rows-for-guid`](baseline/bench-v4-cost-029-no-cost-rows-for-guid/) | negative | regression | **0.800** | 1 | 1.000 | 0.750 | 35 |  |
| [`bench-v4-cost-030-threshold-not-an-anomaly`](baseline/bench-v4-cost-030-threshold-not-an-anomaly/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 103 |  |
| [`bench-v4-cost-050-partial-account-coverage`](baseline/bench-v4-cost-050-partial-account-coverage/) | negative | regression | **0.825** | 1 | 1.000 | 0.750 | 34 |  |
| [`bench-v4-cost-051-gcp-net-of-credits`](baseline/bench-v4-cost-051-gcp-net-of-credits/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 31 |  |
| [`bench-v4-cost-053-capacity-dropped-reservations`](baseline/bench-v4-cost-053-capacity-dropped-reservations/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 64 |  |
| [`bench-v4-cost-054-monitor-no-dashboard-link`](baseline/bench-v4-cost-054-monitor-no-dashboard-link/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 45 |  |
| [`bench-v4-cost-064-reservation-release-active-job-check`](baseline/bench-v4-cost-064-reservation-release-active-job-check/) | trap | regression | **0.760** | 1 | 0.667 | 0.800 | 64 | routing cap |
| [`bench-v4-cost-073-end-exclusive-alert-day`](baseline/bench-v4-cost-073-end-exclusive-alert-day/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 50 |  |
| [`bench-v4-cost-075-vm-count-not-in-billing`](baseline/bench-v4-cost-075-vm-count-not-in-billing/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 48 |  |
| [`bench-v5-cost-401-monitor-drilldown-wrong-month`](baseline/bench-v5-cost-401-monitor-drilldown-wrong-month/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 36 |  |
| [`bench-v5-cost-402-unused-cost-preset-has-no-utilisation`](baseline/bench-v5-cost-402-unused-cost-preset-has-no-utilisation/) | negative | regression | **0.840** | 1 | 1.000 | 0.800 | 51 |  |
| [`bench-v5-cost-403-capacity-results-truncated-at-50`](baseline/bench-v5-cost-403-capacity-results-truncated-at-50/) | trap | regression | **0.840** | 1 | 1.000 | 0.800 | 678 |  |
| [`bench-v5-cost-404-azure-gpu-cost-counts-standard-disks`](baseline/bench-v5-cost-404-azure-gpu-cost-counts-standard-disks/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 49 |  |
| [`bench-v5-cost-405-azure-cache-stale-for-month-close`](baseline/bench-v5-cost-405-azure-cache-stale-for-month-close/) | negative | regression | **0.825** | 1 | 1.000 | 0.750 | 35 |  |
| [`bench-v5-cost-406-gcp-daily-rows-is-not-day-coverage`](baseline/bench-v5-cost-406-gcp-daily-rows-is-not-day-coverage/) | negative | regression | **0.860** | 1 | 1.000 | 0.800 | 62 |  |
| [`bench-v5-cost-407-aws-historical-query-came-back-org-wide`](baseline/bench-v5-cost-407-aws-historical-query-came-back-org-wide/) | trap | regression | **0.600** | 1 | 1.000 | 0.500 | 36 |  |
| [`bench-v5-cost-408-three-cloud-total-gcp-query-failed`](baseline/bench-v5-cost-408-three-cloud-total-gcp-query-failed/) | negative | regression | **0.720** | 1 | 1.000 | 0.600 | 94 |  |
| [`bench-v5-cost-409-top-spender-chain-to-instance-type`](baseline/bench-v5-cost-409-top-spender-chain-to-instance-type/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 89 |  |
| [`bench-v5-cost-410-released-sandbox-still-spending`](baseline/bench-v5-cost-410-released-sandbox-still-spending/) | trap | regression | **0.620** | 1 | 0.667 | 0.600 | 83 | routing cap |
| [`bench-v5-cost-411-org-week-linked-account-league`](baseline/bench-v5-cost-411-org-week-linked-account-league/) | happy | regression | **1.000** | 1 | 1.000 | 1.000 | 51 |  |
| [`bench-v5-cost-412-azure-vm-line-has-no-series-split`](baseline/bench-v5-cost-412-azure-vm-line-has-no-series-split/) | negative | regression | **0.720** | 1 | 1.000 | 0.600 | 57 |  |
| [`bench-v5-cost-413-gcp-unknown-project-bucket`](baseline/bench-v5-cost-413-gcp-unknown-project-bucket/) | negative | regression | **1.000** | 1 | 1.000 | 1.000 | 46 |  |
| [`bench-v5-cost-414-az-id-is-not-a-zone-name`](baseline/bench-v5-cost-414-az-id-is-not-a-zone-name/) | negative | regression | **0.771** | 1 | 1.000 | 0.714 | 112 |  |
| [`bench-v5-cost-415-breakdown-ranked-by-hours-not-cost`](baseline/bench-v5-cost-415-breakdown-ranked-by-hours-not-cost/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 35 |  |
| [`bench-v5-cost-416-peak-day-is-a-cross-service-sum`](baseline/bench-v5-cost-416-peak-day-is-a-cross-service-sum/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 72 |  |
| [`bench-v5-cost-417-commit-usage-excludes-tax-and-support`](baseline/bench-v5-cost-417-commit-usage-excludes-tax-and-support/) | trap | regression | **1.000** | 1 | 1.000 | 1.000 | 136 |  |
| [`bench-v5-cost-418-capacity-window-starts-mid-review`](baseline/bench-v5-cost-418-capacity-window-starts-mid-review/) | negative | regression | **0.825** | 1 | 1.000 | 0.750 | 89 |  |
| [`bench-v5-cost-419-chargeback-predates-current-tenant`](baseline/bench-v5-cost-419-chargeback-predates-current-tenant/) | trap | regression | **0.554** | 1 | 0.500 | 0.571 | 108 | routing cap |
