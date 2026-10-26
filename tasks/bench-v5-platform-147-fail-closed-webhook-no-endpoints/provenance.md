# bench-v5-platform-147-fail-closed-webhook-no-endpoints

## What it measures

A four-hop RCA (log, catalog item, agnosticv config, cluster-side Splunk) on a failure
class no existing task has: **a fail-closed admission webhook whose backend cannot be
scheduled**. The item installs a policy controller that registers a
`ValidatingWebhookConfiguration`, sets its failure policy to `Fail`, and pins the
controller to `node-role.kubernetes.io/infra` nodes, while `infra_node_count: 0` builds
none. The controller pod stays Pending (`FailedScheduling: 0/6 nodes are available`),
the webhook service has no endpoints, and the API server refuses the storefront
Deployment with a 500 `Internal error occurred: failed calling webhook ...`.

The instruction voices the obvious reading of a 500: the API server fell over under
load, so the remedy is bigger control-plane nodes. The log refutes it (the same API
server created a namespace, two config maps and the webhook registration minutes
before). The agent must read the 500's message for *who* refused, follow the webhook's
service namespace (`guardrail-system`, only in the error text) into Splunk, find why the
pod is not running, and then find the two item settings that cause it.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **attributing an error to the component that relayed it**: the API server
returned the 500, but an admission webhook caused it, and the webhook's backend failed
for a reason (scheduling) that appears in neither the job log nor the config alone.
Good agents commonly name the webhook and stop at "the webhook is down", without the
scheduling cause or the two settings.

## Grounding

- `query_aap2 get_job_log`: composite `job_id` + `controller` on `jobs`.
- `lookup_catalog_item`: the stored row's lookup key is `directory`
  `storefront-funnel-lab`; the bare name and the Babylon form from the job name
  both hit. `path` + `files[0]` gives the expected fetch path (the gate's one-dict
  join). Both item files are seeded under `HEAD` and `main`.
- `query_splunk search_namespace` (platform SKILL.md "Store reads"): reads only
  `splunk_ocp_log_entries`; a row matches when the request strings occur anywhere in the
  stored row as raw text; projection is `time`, `namespace`, `pod`, `container`,
  `image`, `level`, `message`, `cluster`; results newest first per the generated
  `| sort -_time`. Every seeded row carries `guardrail-system` and the cluster name, which
  contains the GUID, so `search_by_guid {guid: h7ctx}` returns the same five rows. That
  is why the expected Splunk call pins no argument: either route is correct. The golden
  `query` and `index` are the documented derivations.
- The job carries `git_revision`, but no expected call reads the job's own repository.

## Contract

Weights 0.3 / 0.7, `unordered-subset`: the Splunk read and the config read are siblings
(each needs only the log), and every pinned argument already forces its dependency.

- `webhook`: the refusing component, in the log.
- `pod-unschedulable`: the controller pod cannot be scheduled, only in Splunk.
- `infra-placement`: the infra node selector / `infra_node_count: 0`, only in common.yaml.
- `fail-closed`: the `Fail` failure policy, only in common.yaml.
- `api-server-up` (derived): the decoy refuted from the log's earlier API successes.
- `resize-wont-help` (derived): the operational judgement on the proposed change.
- forbidden `api-server-outage` and `manifest-invalid`, written as claims (hazard 22).

Mute answer floor: 2 forbidden of 8 answer items, reward 0.475.

## The wrong answer

`/tmp/ext/scratch/bench-v5-platform-147-fail-closed-webhook-no-endpoints/wrong.md`: reads the log, sees the 500, says the API server was
overloaded and endorses bigger control-plane nodes. With the golden calls it scores
**0.3875**; a variant that also names the webhook (`wrong2.md`) scores 0.475. Golden 1.000.

Honest panel, all **1.000**: two authored answers (`honest1-2.md`: prose, and `Key: value`
bullets denying the API-server theory) and three blind answers by a separate agent from the
instruction and the tool results only (`blind-a/b/c.md`). Two blind answers first scored
0.9125 ("The API server was not overloaded"; "Would bigger control-plane nodes help? - No."),
so `api-server-up` and `resize-wont-help` were widened.

## Invented

Every literal is invented: job 8840217, GUID `h7ctx`, the catalog item
`retail_bu/storefront-funnel-lab`, the cluster
`cluster-h7ctx.retail-labs.example.org`, the guardrail controller, its webhook
`vworkload.guardrail.example.io`, its image, the role names `ocp4_workload_guardrail`
and `ocp4_workload_storefront` and their variables, the pod names, the revision and
every timestamp and figure. The incident class (a fail-closed admission webhook whose
only backend pod is unschedulable) is invented in the mould of bench-v4's challenge
tranche; no public postmortem is its source, and nothing comes from bench-v4 or
production data.
