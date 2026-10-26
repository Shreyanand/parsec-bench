---
name: parsec-platform
description: Simulation skill for the parsec platform tools API.
---

# parsec platform tools Simulation

## Core Principles

- Impersonate the parsec platform tools API exactly as documented in the operation
  sections below. Do not invent operations, fields, or error conditions.
- All responses must match the operation's response schema precisely.

## Session State Management

State is kept in collections defined by `schema.json`. Use the `state_*` tools to
read and write entities. Do not list field names or types here — consult
`schema.json` for the authoritative shape.

Collections: babylon_anarchy_actions, babylon_anarchy_subjects, babylon_catalog_items, babylon_components, babylon_deployments, babylon_multiworkshops, babylon_resource_pools, babylon_workshops, jobs, job_events, ocpv_machines, ocpv_machinesets, ocpv_namespaces, ocpv_pvcs, ocpv_storage_classes, ocpv_vms, splunk_aap2_log_entries, splunk_ocp_log_entries, workshops.

## Seed Data and Data Generation

Initial seed entities are defined in `db.json` and loaded into the store on first
use. Do not enumerate seed values here.

## Schema Reference

See `schema.json` for the full JSON Schema of every collection.

## Error Handling

Return an error only when an operation section's explicit when-clause applies.
When no entity matches a read, return the empty-result contract documented for
that operation.

## Realism Guidelines

Preserve IDs once created, keep timestamps monotonic, and reuse references so
related entities stay consistent across calls.

### Numeric Ranges and Ordering
- `BabylonMultiworkshop.asset_count`: 0 to 500.
- `BabylonMultiworkshop.number_seats`: 1 to 1000.
- `BabylonResourcePool.max_unready`: 0 to 500.
- `BabylonResourcePool.min_available`: 0 to 500.
- `BabylonResourcePool.resource_handle_count`: 0 to 2000.
- `BabylonWorkshop.resource_claims_count`: 0 to 1000.
- `BabylonWorkshop.user_assignments_count`: 0 to 1000.
- `BabylonWorkshop.user_count`: 0 to 1000.
- `Job.duration_seconds`: 0 to 172800.
- `Job.job_id`: 1 to 2147483647.
- `Job.log_original_size`: 0 to 50000000.
- `Job.log_trimmed_size`: 0 to 50000000.
- `JobEvent.counter`: 1 to 1000000.
- `JobEvent.job_id`: 1 to 2147483647.
- `OcpvMachineset.available_replicas`: 0 to 1000.
- `OcpvMachineset.ready_replicas`: 0 to 1000.
- `OcpvMachineset.replicas`: 0 to 1000.
- `OcpvVm.vcpus`: 1 to 256.
- Ordering constraints:
  - `Job.log_trimmed_size <= Job.log_original_size`.
  - `OcpvMachineset.available_replicas <= OcpvMachineset.ready_replicas <= OcpvMachineset.replicas`.
  - `BabylonResourcePool.max_unready <= BabylonResourcePool.resource_handle_count` when both describe the same stored pool.
  - `BabylonResourcePool.min_available <= BabylonResourcePool.resource_handle_count` when both describe the same stored pool.
  - `BabylonWorkshop.user_assignments_count <= BabylonWorkshop.user_count`.
  - `BabylonMultiworkshop.asset_count >= 0`, `BabylonWorkshop.resource_claims_count >= 0`, `BabylonWorkshop.user_assignments_count >= 0`, `BabylonWorkshop.user_count >= 0`, `Job.duration_seconds >= 0`, `Job.log_original_size >= 0`, `Job.log_trimmed_size >= 0`, `JobEvent.counter >= 1`, `OcpvMachineset.available_replicas >= 0`, `OcpvMachineset.ready_replicas >= 0`, `OcpvMachineset.replicas >= 0`, `OcpvVm.vcpus >= 1`.

### Derivation Rules
- `query_aap2.get_job_events.event_count = length(events)`.
- `query_aap2.find_jobs.total = length(jobs)` after all filters, ordering, and `max_results` application.
- `query_aap2.get_job_log.log = ""` when the matched `Job` row has no stored `log`.
- `query_aap2.get_job_log.log_original_size = 0` when the matched `Job` row has no stored `log`.
- `query_aap2.get_job_log.log_trimmed_size = 0` when the matched `Job` row has no stored `log`.
- `query_aap2.find_jobs.jobs` are ordered by `finished` descending.
- `query_aap2.get_job_events.events` are ordered by `counter` ascending.
- `query_aap2.find_jobs` keeps a `Job` row only when every supplied filter matches:
  - `status` matches stored `status` exactly.
  - `template_name` matches when stored `job_name` contains the request value case-insensitively.
  - `created_after` keeps the row only when stored `started` is strictly after midnight UTC of that date.
  - `created_before` keeps the row only when stored `started` is strictly before midnight UTC of that date.
- `query_splunk.result_count = length(results)`.
- `query_splunk.total_count = length(results)`.
- `query_splunk.truncated = true` iff `result_count >= max_results`; otherwise `false`.
- `query_ocpv_cluster.list_pvcs.count = length(pvcs)`.
- `query_ocpv_cluster.list_pvcs.pending_count = count(pvcs where status = "Pending")`.
- `query_ocpv_cluster.list_storage_classes.count = length(storage_classes)`.
- `query_ocpv_cluster.list_vms.count = length(vms)`.
- `query_ocpv_cluster.list_machines.machineset_count = length(machinesets)`.
- `query_ocpv_cluster.list_machines.machine_count = length(machines)`.
- `query_ocpv_cluster.get_node_resources.count = length(nodes)`.
- `query_ocpv_cluster.nodes_top.count = length(nodes)`.
- `query_ocpv_cluster.list_pods.count = length(pods)`.
- `query_ocpv_cluster.pods_top.count = length(pods)`.
- `query_ocpv_cluster.get_ocpv_pod_logs.total_pods = 0` when using the documented always-empty result.
- `query_ocpv_cluster.get_ocpv_pod_logs.pods_shown = length(results)`.
- `query_ocpv_cluster.list_pvs.total_pvs = sum of the grouped PV counts represented in summary`.
- `query_ocpv_cluster.list_pvs.total_bound_gi = sum of integer-truncated Gi capacities represented in summary, counting only Gi-suffixed capacities`.
- `query_babylon_catalog.search_catalog.count = length(items)`.
- `query_babylon_catalog.search_catalog.total_scanned = count of stored `BabylonCatalogItem` rows considered after cluster resolution and before `max_results` truncation`.
- `query_babylon_catalog.search_catalog.truncated = true` iff `count >= max_results`; otherwise `false`.
- `query_babylon_catalog.list_deployments.count = length(deployments)`.
- `query_babylon_catalog.list_deployments.truncated = true` iff `count >= max_results`; otherwise `false`.
- `query_babylon_catalog.list_anarchy_subjects.count = length(subjects)`.
- `query_babylon_catalog.list_anarchy_subjects.truncated = true` iff `count >= max_results`; otherwise `false`.
- `query_babylon_catalog.list_anarchy_actions.count = length(actions)`.
- `query_babylon_catalog.list_anarchy_actions.truncated = true` iff `count >= max_results`; otherwise `false`.
- `query_babylon_catalog.list_resource_pools.count = length(pools)`.
- `query_babylon_catalog.list_resource_pools.truncated = true` iff `count >= max_results`; otherwise `false`.
- `query_babylon_catalog.list_workshops.count = length(workshops)`.
- `query_babylon_catalog.list_workshops.truncated = true` iff `count >= max_results`; otherwise `false`.
- `query_babylon_catalog.list_multiworkshops.count = length(multiworkshops)`.
- `query_babylon_catalog.list_multiworkshops.truncated = true` iff `count >= max_results`; otherwise `false`.
- `query_babylon_catalog.get_multiworkshop.summary.total_workshops = length(workshops)`.
- `query_babylon_catalog.get_multiworkshop.summary.active = count(workshops whose `provision_count` indicates active provisioning state)`.
- `query_babylon_catalog.get_multiworkshop.summary.failed = count(workshops whose `provision_count` indicates failed provisioning state)`.
- `BabylonDeployment.current_state` is copied from the first embedded `BabylonAnarchySubject` when present.
- `BabylonDeployment.desired_state` is copied from the first embedded `BabylonAnarchySubject` when present.
- `BabylonResourcePool.provider_name` is copied from the first configured resource entry when present.
- `BabylonResourcePool.resource_name` is copied from the first configured resource entry when present.
- `BabylonWorkshop.resource_claims_count = length(resource_claims)` when `resource_claims` is stored.
- `BabylonMultiworkshop.asset_count = length(assets)`.
- `OcpvVm.vcpus` is the computed virtual CPU count derived from the VM definition represented by the stored row and must remain identical for the same stored row across calls.

### On-Demand Generation Rules
- No records may be generated on demand for any operation backed by store-authoritative collections.
- If a collection is empty or no stored row matches filters, return the documented empty success shape or in-band error shape; never fabricate rows to satisfy a query.
- For stored rows, numeric fields are returned exactly as stored unless a Derivation Rule above explicitly computes the response value.
- Optional numeric fields omitted from a stored row remain omitted, except where a Derivation Rule explicitly supplies `0` for `Job.log_original_size` and `Job.log_trimmed_size` on `get_job_log`.
- When a response requires ordering rather than new numeric generation:
  - `JobEvent.counter` ordering is ascending in `get_job_events`.
  - `Job.finished` ordering is descending in `find_jobs`.
- When a response requires counts for an empty result, generate them deterministically as `0`:
  - `event_count`, `total`, `result_count`, `total_count`, `count`, `pending_count`, `machineset_count`, `machine_count`, `total_pods`, `pods_shown`, `total_pvs`, `total_bound_gi`, `summary.total_workshops`, `summary.active`, and `summary.failed`.
- When `query_ocpv_cluster` actions have no backing collection (`get_node_resources`, `get_ocpv_pod_logs`, `list_pods`, `nodes_top`, `pods_top`), generate only the documented empty envelopes and zero counts; do not generate per-item numeric values.
- If seeded data for a stored row violates an ordering constraint, preserve the stored row for direct field projections but compute derived counts from the returned list lengths exactly; do not mutate stored numeric fields to repair them.
- Any deterministic regeneration of the same logical empty response must yield the same zero-valued counts, the same ordering rules, and no negative numbers.

## Example Scenarios

Representative user stories this simulation can satisfy with the seeded data:

1. **Find failed automation job** — An operations engineer wants to locate a failed AAP2 job and inspect its detailed execution data to understand what went wrong. (operations: query_aap2, query_aap2)
2. **Trace deployment health in Babylon** — A platform user wants to look up an existing Babylon deployment and review its current provisioning and lifecycle state. (operations: query_babylon_catalog)
3. **Investigate workshop event resources** — An event administrator wants to review a multiworkshop and its workshops to confirm seat usage and attached resources for an upcoming session. (operations: query_babylon_catalog)
4. **Diagnose OCP virtualization issue** — A virtualization admin wants to inspect an OCPV namespace and related VMs, machines, PVCs, and storage classes to troubleshoot an environment problem. (operations: query_ocpv_cluster)
5. **Correlate controller and cluster logs** — A support engineer wants to search Splunk for both AAP2 controller logs and OCP pod logs related to a known incident. (operations: query_splunk, query_splunk)

## API Operation Simulation

### /query_aap2 POST

- Required inputs:
  - `action` always.
  - `job_id` when `action` is `get_job`, `get_job_log`, or `get_job_events`.
  - `controller` when `action` is `get_job`, `get_job_log`, or `get_job_events`.

- Optional inputs:
  - `controller` when `action` is `find_jobs`; when omitted, search across every controller.
  - `failed_only` when `action` is `get_job_events`; default `false`.
  - `changed_only` when `action` is `get_job_events`; default `false`.
  - `status` when `action` is `find_jobs`; exact match on stored `status`.
  - `created_after` when `action` is `find_jobs`; compare against stored `started`, strictly greater than the bound.
  - `created_before` when `action` is `find_jobs`; compare against stored `started`, strictly less than the bound.
  - `template_name` when `action` is `find_jobs`; match rows whose stored `job_name` contains this value case-insensitively.
  - `max_results` when `action` is `find_jobs`; default `50`, clamp to `200` when comparable to an integer. A request above `200` is legal and returns at most `200` rows, not an error.

- Store reads:
  - For `get_job`:
    - Read `jobs` by composite match on `job_id` and `controller`.
  - For `get_job_log`:
    - Read `jobs` by composite match on `job_id` and `controller`.
  - For `get_job_events`:
    - Read `job_events` where `job_id` = request `job_id` and `controller` = request `controller`.
    - Order matching `job_events` rows by `counter` ascending.
    - Apply `failed_only` and `changed_only` filters to the matched `job_events` rows.
  - For `find_jobs`:
    - Read `jobs`.
    - If `controller` is supplied, keep only rows whose `controller` exactly matches it.
    - If `status` is supplied, keep only rows whose `status` exactly matches it.
    - If `template_name` is supplied, keep only rows whose `job_name` contains it case-insensitively.
    - If `created_after` is supplied, keep only rows whose `started` is strictly after that bound.
    - If `created_before` is supplied, keep only rows whose `started` is strictly before that bound.
    - Interpret a date-only `created_after` or `created_before` bound as midnight UTC of that date.
    - Order remaining rows by `finished` descending.
    - Apply `max_results` after filtering and ordering.

- Store writes:
  - None. This operation is read-only.
  - Do not write `jobs`.
  - Do not write `job_events`.

- Response contract by action:
  - When `action` is `get_job`:
    - Return the matched `jobs` row projected to exactly:
      - `job_id`
      - `job_name`
      - `status`
      - `failed`
      - `started`
      - `finished`
      - `duration_seconds`
      - `launch_type`
      - `job_explanation`
      - `template_name`
      - `env_type`
      - `guid`
      - `action`
      - `cloud_provider`
      - `display_name`
      - `controller`
      - `git_url` when the row carries it
      - `git_branch` when the row carries it
      - `git_revision` when the row carries it
    - Never return:
      - `id`
      - `log`
      - `log_original_size`
      - `log_trimmed_size`
      - any other storage-only or non-listed field.
  - When `action` is `get_job_log`:
    - Return the same metadata projection as `get_job`, plus:
      - `log`
      - `log_original_size`
      - `log_trimmed_size`
    - When the matched `jobs` row has no stored `log`, return:
      - `log: ""`
      - `log_original_size: 0`
      - `log_trimmed_size: 0`
    - Never return `id`.
  - When `action` is `get_job_events`:
    - Return an object with exactly:
      - `job_id`
      - `controller`
      - `event_count`
      - `filters`
      - `events`
    - `filters` must be:
      - `{ "failed_only": <exact received value or default false>, "changed_only": <exact received value or default false> }`
    - `events` must be an array of projected event objects, each carrying exactly:
      - `event`
      - `task`
      - `play`
      - `role`
      - `host`
      - `failed`
      - `changed`
      - `stdout`
      - `error_msg`
      - `counter`
    - Never return event storage fields:
      - `job_event_id`
      - `job_id`
      - `controller`
      - `event_key`
    - `event_count` always equals `events.length`.
  - When `action` is `find_jobs`:
    - Return an object with exactly:
      - `total`
      - `jobs`
    - `jobs` must be an array of JobSummary objects, each carrying exactly:
      - `job_id`
      - `job_name`
      - `status`
      - `failed`
      - `started`
      - `finished`
      - `duration_seconds`
      - `template_name`
      - `controller`
    - Never return full Job fields in `jobs`, including:
      - `id`
      - `display_name`
      - `guid`
      - `env_type`
      - `action`
      - `cloud_provider`
      - `launch_type`
      - `job_explanation`
      - any `git_*` field
      - any `log*` field
    - `total` equals `jobs.length` after `max_results` is applied; it is not a corpus count.
  - On every defined failure path except the `max_results` comparison caveat:
    - Return in-band error shape:
      - `{ "error": "<message>" }`

- Concrete response examples:
  - `get_job`
    ```json
    {
      "job_id": 4812,
      "job_name": "Provision cluster",
      "status": "successful",
      "failed": false,
      "started": "2026-03-01T10:00:00Z",
      "finished": "2026-03-01T10:12:34Z",
      "duration_seconds": 754,
      "launch_type": "manual",
      "job_explanation": "",
      "template_name": "cluster-provision",
      "env_type": "prod",
      "guid": "3f0d7d8a-1111-2222-3333-abcdefabcdef",
      "action": "provision",
      "cloud_provider": "aws",
      "display_name": "Provision cluster for guid 3f0d7d8a-1111-2222-3333-abcdefabcdef",
      "controller": "east",
      "git_url": "https://git.example.com/org/repo.git",
      "git_branch": "main",
      "git_revision": "abc123def456"
    }
    ```
  - `get_job_log`
    ```json
    {
      "job_id": 4812,
      "job_name": "Provision cluster",
      "status": "successful",
      "failed": false,
      "started": "2026-03-01T10:00:00Z",
      "finished": "2026-03-01T10:12:34Z",
      "duration_seconds": 754,
      "launch_type": "manual",
      "job_explanation": "",
      "template_name": "cluster-provision",
      "env_type": "prod",
      "guid": "3f0d7d8a-1111-2222-3333-abcdefabcdef",
      "action": "provision",
      "cloud_provider": "aws",
      "display_name": "Provision cluster for guid 3f0d7d8a-1111-2222-3333-abcdefabcdef",
      "controller": "east",
      "log": "PLAY [all] **********************************************************",
      "log_original_size": 20480,
      "log_trimmed_size": 8192
    }
    ```
  - `get_job_events`
    ```json
    {
      "job_id": 4812,
      "controller": "east",
      "event_count": 2,
      "filters": {
        "failed_only": false,
        "changed_only": true
      },
      "events": [
        {
          "event": "runner_on_ok",
          "task": "Create VPC",
          "play": "Provision infrastructure",
          "role": "network",
          "host": "localhost",
          "failed": false,
          "changed": true,
          "stdout": "changed: [localhost]",
          "error_msg": "",
          "counter": 17
        },
        {
          "event": "runner_on_ok",
          "task": "Create cluster",
          "play": "Provision infrastructure",
          "role": "cluster",
          "host": "localhost",
          "failed": false,
          "changed": true,
          "stdout": "changed: [localhost]",
          "error_msg": "",
          "counter": 18
        }
      ]
    }
    ```
  - `find_jobs`
    ```json
    {
      "total": 2,
      "jobs": [
        {
          "job_id": 4815,
          "job_name": "Delete cluster",
          "status": "failed",
          "failed": true,
          "started": "2026-03-02T09:00:00Z",
          "finished": "2026-03-02T09:05:00Z",
          "duration_seconds": 300,
          "template_name": "cluster-delete",
          "controller": "west"
        },
        {
          "job_id": 4812,
          "job_name": "Provision cluster",
          "status": "successful",
          "failed": false,
          "started": "2026-03-01T10:00:00Z",
          "finished": "2026-03-01T10:12:34Z",
          "duration_seconds": 754,
          "template_name": "cluster-provision",
          "controller": "east"
        }
      ]
    }
    ```
  - Error
    ```json
    {
      "error": "job_id is required for get_job"
    }
    ```

- Error conditions:
  - Return `{ "error": "job_id is required for get_job" }` when `action` is `get_job` and `job_id` is missing.
    - Do NOT return this error if `action` is not `get_job`.
  - Return `{ "error": "controller is required for get_job" }` when `action` is `get_job` and `controller` is missing.
    - Do NOT return this error if `action` is not `get_job`.
  - Return `{ "error": "job_id is required for get_job_log" }` when `action` is `get_job_log` and `job_id` is missing.
    - Do NOT return this error if `action` is not `get_job_log`.
  - Return `{ "error": "controller is required for get_job_log" }` when `action` is `get_job_log` and `controller` is missing.
    - Do NOT return this error if `action` is not `get_job_log`.
  - Return `{ "error": "job_id is required for get_job_events" }` when `action` is `get_job_events` and `job_id` is missing.
    - Do NOT return this error if `action` is not `get_job_events`.
  - Return `{ "error": "controller is required for get_job_events" }` when `action` is `get_job_events` and `controller` is missing.
    - Do NOT return this error if `action` is not `get_job_events`.
  - Return `{ "error": "Unknown action: '<value>'. Use get_job, get_job_log, get_job_events, or find_jobs." }` when `action` is not one of `get_job`, `get_job_log`, `get_job_events`, `find_jobs`.
    - Do NOT return this error if `action` is one of the supported values.
  - Return `{ "error": "Unknown AAP2 controller: '<value>'. Configured: east, west, event0, partner0" }` when `controller` is supplied and is not one of `east`, `west`, `event0`, `partner0`.
    - Do NOT return this error when `controller` is omitted for `find_jobs`.
  - Return an in-band not-found error when `action` is `get_job` or `get_job_log` and no `jobs` row matches both `job_id` and `controller`.
    - Do NOT return this error if a matching `jobs` row exists, even when that row has no stored `log`.
  - Return an in-band not-found error when `action` is `get_job_events` and no `jobs` row matches both `job_id` and `controller`.
    - Do NOT return this error merely because no `job_events` rows match after filtering; that is an empty successful result.
  - Allow a non-error clamp when `action` is `find_jobs` and `max_results` is greater than `200`; use `200`.
    - Do NOT return an error for requesting more than `200`.
  - Caveat: when `max_results` cannot be compared to an integer, the implementation raises out of the tool rather than returning the in-band error shape.
    - Do NOT simulate an in-band `{ "error": ... }` for that specific comparison failure.

- Empty-result contract:
  - For `find_jobs`:
    - When no `jobs` row matches all supplied filters, return:
      - `{ "total": 0, "jobs": [] }`
    - Never invent rows.
  - For `get_job_events`:
    - When the job exists but no `job_events` rows match after applying `failed_only` and `changed_only`, return:
      - `job_id` and `controller` for the requested job,
      - `event_count: 0`,
      - `filters` echoing the received/defaulted booleans,
      - `events: []`.
  - For `get_job` and `get_job_log`:
    - When no `jobs` row matches `job_id` and `controller`, return the in-band not-found error shape, not an empty object and not a synthesized row.

- Idempotency:
  - Read-only operation; repeated identical requests against unchanged stores return the same shape and do not modify state.
  - `find_jobs` ordering is deterministic by `finished` descending.
  - `get_job_events` ordering is deterministic by `counter` ascending.

#### Derived fields

- `get_job_events.event_count` = length of returned `events`.
- `get_job_events.filters.failed_only` = request `failed_only` if supplied, else `false`.
- `get_job_events.filters.changed_only` = request `changed_only` if supplied, else `false`.
- `find_jobs.total` = length of returned `jobs` after `max_results` is applied.
- `get_job_log.log` = `""` when the matched `jobs` row has no stored `log`; otherwise stored `log`.
- `get_job_log.log_original_size` = `0` when the matched `jobs` row has no stored `log_original_size`; otherwise stored `log_original_size`.
- `get_job_log.log_trimmed_size` = `0` when the matched `jobs` row has no stored `log_trimmed_size`; otherwise stored `log_trimmed_size`.

### /query_splunk POST

- **Purpose**
  - Execute one of four search actions:
    - `search_by_guid`
    - `search_namespace`
    - `search_aap2_logs`
    - `search_raw`
  - This operation is **read-only**.
  - It **must not write any store collection**.
  - It owns no entity and must not synthesise rows or fields.

- **Required inputs**
  - `action` — always required.
  - `guid` — required **when** `action = "search_by_guid"`.
  - `namespace` — required **when** `action = "search_namespace"`.
  - `controller` — required **when** `action = "search_aap2_logs"`.
  - `raw_query` — required **when** `action = "search_raw"`.

- **Optional inputs**
  - `guid` — optional **when** `action = "search_aap2_logs"`; ignored otherwise.
  - `namespace` — ignored **when** `action != "search_namespace"`.
  - `cluster_name` — optional **when** `action` is `search_by_guid` or `search_namespace`; ignored otherwise.
  - `controller` — ignored **when** `action != "search_aap2_logs"`.
  - `search_terms` — optional **when** `action` is `search_by_guid`, `search_namespace`, or `search_aap2_logs`; ignored for `search_raw`.
  - `earliest` — optional for all actions; default `"-24h"`.
  - `latest` — optional for all actions; default `"now"`.
  - `errors_only` — optional for all actions; default `false`; ignored for `search_raw`.
  - `raw_query` — ignored **when** `action != "search_raw"`.
  - `max_results` — optional for all actions; default `200`; clamp to `500` if greater than `500`.

- **Caller expectations**
  - none

- **Store reads**
  - **When** `action = "search_by_guid"`:
    - read `splunk_ocp_log_entries`
    - evaluate matches against stored rows only
    - a row matches **when** the requested strings occur anywhere in that stored row as raw text
    - do **not** read `splunk_aap2_log_entries`
  - **When** `action = "search_namespace"`:
    - read `splunk_ocp_log_entries`
    - evaluate matches against stored rows only
    - a row matches **when** the requested strings occur anywhere in that stored row as raw text
    - do **not** read `splunk_aap2_log_entries`
  - **When** `action = "search_aap2_logs"`:
    - read `splunk_aap2_log_entries`
    - evaluate matches against stored rows only
    - a row matches **when** the requested strings occur anywhere in that stored row as raw text
    - do **not** read `splunk_ocp_log_entries`
  - **When** `action = "search_raw"`:
    - read exactly one collection selected by the raw query's index
    - if the selected index is the OCP index, read `splunk_ocp_log_entries`
    - if the selected index is the AAP index, read `splunk_aap2_log_entries`
    - never read both collections for one `search_raw` request

- **Matching and projection rules**
  - Raw-text matching means:
    - a filter matches **when** its string occurs anywhere in a stored row
    - it is **not** a field comparison
    - substring matches are allowed
  - `errors_only` adds raw-text terms to the generated query only.
    - Do **not** require a returned row's `level` field to equal or contain those severity words.
  - Return only stored rows that match.
  - Never generate or rewrite a row so it mentions the requested `guid`, `namespace`, `cluster_name`, `controller`, or search text.
  - For OCP actions, project each matched row to exactly:
    - `time`
    - `namespace`
    - `pod`
    - `container`
    - `image`
    - `level`
    - `message`
    - `cluster`
  - For AAP2 action, project each matched row to:
    - always:
      - `time`
      - `controller`
      - `level`
      - `logger`
      - `message`
    - plus `task`, `role`, `task_action`, and `playbook` **when** the stored row carries a task
    - plus `stdout` **when** the stored row carries `stdout`
  - Never return storage-only ids such as:
    - `splunk_ocp_log_entry_id`
    - `splunk_aap2_log_entry_id`

- **State changes / writes**
  - none
  - Must not write:
    - `splunk_ocp_log_entries`
    - `splunk_aap2_log_entries`

- **Response shape**
  - Success response is always an object with exactly:
    - `results`
    - `result_count`
    - `total_count`
    - `truncated`
    - `query`
    - `index`
  - Error response is returned in-band as an object with:
    - `error`
    - optional `hint`
    - optional `valid_actions`

- **Success response construction**
  - `results`
    - array of projected matched rows
  - `result_count`
    - number of rows in `results`
  - `total_count`
    - total number of matched stored rows before truncation
  - `truncated`
    - `true` **when** `total_count > effective_max_results`; otherwise `false`
  - `query`
    - exact built query string for generated-query actions
    - stripped `raw_query` for `search_raw`
  - `index`
    - `"federated:rh_pds-001_ocp_app"` for `search_by_guid` and `search_namespace`
    - `"federated:rh_pds-001_aap"` for `search_aap2_logs`
    - `"custom"` for `search_raw`

- **Generated query rules**
  - **When** `action = "search_by_guid"`:
    - `query` is:
      - `index=federated:rh_pds-001_ocp_app "<guid>"`
      - then ` "<cluster_name>"` **when** `cluster_name` is provided and non-empty
      - then ` ("error" OR "fatal" OR "warning")` **when** `errors_only = true`
      - then ` "<search_terms>"` **when** `search_terms` is provided and non-empty
      - then ` | spath | sort -_time`
  - **When** `action = "search_namespace"`:
    - `query` is:
      - `index=federated:rh_pds-001_ocp_app "<namespace>"`
      - then ` "<cluster_name>"` **when** `cluster_name` is provided and non-empty
      - then ` ("error" OR "fatal" OR "warning")` **when** `errors_only = true`
      - then ` "<search_terms>"` **when** `search_terms` is provided and non-empty
      - then ` | spath | sort -_time`
  - **When** `action = "search_aap2_logs"`:
    - `query` is:
      - `index=federated:rh_pds-001_aap "<controller>"`
      - then ` "<guid>"` **when** `guid` is provided and non-empty
      - then ` ("ERROR" OR "CRITICAL" OR "WARNING" OR "failed")` **when** `errors_only = true`
      - then ` "<search_terms>"` **when** `search_terms` is provided and non-empty
      - then ` | spath | sort -_time`
  - **When** `action = "search_raw"`:
    - `query` is `raw_query.strip()`
  - `earliest` and `latest` affect search execution only; they are never included in `query`.
  - `query` never starts with `search` for generated-query actions.

- **Concrete success example**
  ```json
  {
    "results": [
      {
        "time": "2026-09-14T12:34:56Z",
        "namespace": "guid-1234-worker",
        "pod": "api-7d9c6f7d8b-abcde",
        "container": "manager",
        "image": "quay.io/example/app:1.2.3",
        "level": "INFO",
        "message": "provision completed",
        "cluster": "cluster1.example.com"
      }
    ],
    "result_count": 1,
    "total_count": 1,
    "truncated": false,
    "query": "index=federated:rh_pds-001_ocp_app \"guid-1234\" | spath | sort -_time",
    "index": "federated:rh_pds-001_ocp_app"
  }
  ```

- **Concrete error example**
  ```json
  {
    "error": "guid is required for search_by_guid action"
  }
  ```

- **Error conditions**
  - **When** `action` is not one of `search_by_guid`, `search_namespace`, `search_aap2_logs`, `search_raw`:
    - return:
      - `error`: `Unknown action: <action>`
      - `valid_actions`: `["search_by_guid", "search_namespace", "search_aap2_logs", "search_raw"]`
    - Do NOT return this error if `action` is one of the four valid values.
  - **When** `action = "search_by_guid"` and `guid` is absent or empty:
    - return `{"error":"guid is required for search_by_guid action"}`
    - Do NOT return this error if `guid` is a non-empty string.
  - **When** `action = "search_namespace"` and `namespace` is absent or empty:
    - return `{"error":"namespace is required for search_namespace action"}`
    - Do NOT return this error if `namespace` is a non-empty string.
  - **When** `action = "search_aap2_logs"` and `controller` is absent or empty:
    - return `{"error":"controller is required for search_aap2_logs action"}`
    - Do NOT return this error if `controller` is a non-empty string.
  - **When** `action = "search_raw"` and `raw_query` is absent or empty:
    - return `{"error":"raw_query is required for search_raw action"}`
    - Do NOT return this error if `raw_query` is a non-empty string.
  - **When** `action = "search_raw"` and `raw_query.strip()` does not start with `search ` or `|`:
    - return `{"error":"raw_query must start with 'search' or '|'"}`
    - Do NOT return this error if the stripped raw query starts with `search ` or `|`.
  - **When** `action = "search_raw"` and `raw_query` contains any of these substrings case-insensitively:
    - `| delete`
    - `| outputlookup`
    - `| sendalert`
    - `| collect`
    - `| outputcsv`
    - `| sendemail`
    - return `{"error":"Dangerous command '<matched command>' not allowed in raw queries"}`
    - Do NOT return this error if none of those substrings occur case-insensitively.
  - **When** Splunk client configuration lookup fails with the not-configured condition:
    - return:
      - `error`: `Splunk not configured. Set splunk.host and splunk.token in config.`
      - `hint`: `See config.yaml for Splunk configuration options.`
    - Do NOT return this error if configuration is available.
  - **When** the downstream search returns an API/client failure:
    - return `{"error":"Splunk API error: ..."}`
    - Do NOT return this error if the search completes normally.
  - **When** the downstream search fails during execution/querying:
    - return `{"error":"Splunk query failed: ..."}`
    - Do NOT return this error if the search completes normally.
  - **When** `max_results` cannot be compared to an integer for clamping:
    - the operation may raise out of band rather than returning the in-band error shape
    - Do NOT return an in-band error for this condition unless the simulator explicitly models that external exception path.

- **Empty-result contract**
  - **When** no stored row matches:
    - return normal success shape
    - `results` must be `[]`
    - `result_count` must be `0`
    - `total_count` must be `0`
    - `truncated` must be `false`
    - `query` and `index` must still be populated normally
  - Never:
    - synthesise a log entry
    - rewrite a stored row to force a match
    - convert an empty result into an error

- **Idempotency**
  - Read-only operation.
  - Repeating the same request against unchanged stores returns the same response shape and the same matched rows, subject only to the stored data and any simulated downstream failure path.

#### Derived fields

- `result_count` — `results.length`
- `total_count` — count of all matched stored rows before applying `max_results`
- `truncated` — `total_count > min(max_results, 500)`
- `query` — built from `action` and request parameters exactly as specified above, or `raw_query.strip()` for `search_raw`
- `index` — fixed literal chosen by `action` (`custom` for `search_raw`)

### /query_ocpv_cluster POST

- Required inputs:
  - `action`
- Optional inputs:
  - `cluster`
    - When provided, resolve the target cluster from this value after lower-casing it.
  - `namespace`
    - Required when `action` is one of:
      - `find_namespace`
      - `list_pvcs`
      - `list_vms`
      - `get_ocpv_pod_logs`
      - `list_pods`
      - `pods_top`
    - Also required for cluster discovery when `cluster` is omitted and `action` is not `find_namespace`.
  - `name`
    - Optional case-insensitive substring filter on resource names.
    - Ignored when `action = find_namespace`.
  - `search`
    - Optional case-insensitive grep over pod log lines.
    - Used only when `action = get_ocpv_pod_logs`.
    - Ignored for every other action.
  - `sandbox_comment`
    - Optional cluster-discovery input when `cluster` is omitted.
  - `max_results`
    - Optional; default `50`.
    - Used differently by action:
      - `list_pvcs`, `list_vms`, `list_pods`, `pods_top`: limits returned items.
      - `list_machines`: limits `machinesets` and `machines` separately.
      - `list_pvs`: limits returned groups.
      - `get_ocpv_pod_logs`: limits log lines per pod; pods shown are still capped at 5.
      - Ignored by `list_storage_classes`, `get_node_resources`, `nodes_top`.
- Caller expectations:
  - none

- Cluster resolution:
  - When `cluster` is provided:
    - Use `lower(cluster)` as the resolved cluster.
  - When `cluster` is omitted and `sandbox_comment` resolves a cluster:
    - Use that resolved cluster.
  - When `cluster` is omitted and `action != find_namespace`:
    - Resolve cluster by reading `ocpv_namespaces` for a row with matching `namespace`; use that row's `cluster`.
  - When `action = find_namespace`:
    - Do not resolve cluster first; this action itself searches `ocpv_namespaces` by `namespace`.

- Store reads:
  - General rule:
    - For every action except `find_namespace`, read only rows whose stored `cluster` equals the resolved cluster.
  - `find_namespace`:
    - Read `ocpv_namespaces`, matching by `namespace`.
  - `list_pvcs`:
    - Read `ocpv_pvcs`, filtered by `cluster` and `namespace`; apply optional case-insensitive `name` substring filter to the claim name.
  - `list_pvs`:
    - Read `ocpv_pvcs`, filtered by `cluster`; apply optional case-insensitive `name` substring filter to the resource name if present.
    - Aggregate matched rows by `(node, storage_class)`.
  - `list_storage_classes`:
    - Read `ocpv_storage_classes`, filtered by `cluster`; apply optional case-insensitive `name` substring filter to the storage class name.
  - `list_vms`:
    - Read `ocpv_vms`, filtered by `cluster` and `namespace`; apply optional case-insensitive `name` substring filter to the VM name.
  - `list_machines`:
    - Read `ocpv_machinesets`, filtered by `cluster`; apply optional case-insensitive `name` substring filter to the MachineSet name.
    - Read `ocpv_machines`, filtered by `cluster`; apply optional case-insensitive `name` substring filter to the Machine name.
  - `get_node_resources`:
    - Read no collection; always return the documented empty result.
  - `get_ocpv_pod_logs`:
    - Read no collection; always return the documented empty result.
  - `list_pods`:
    - Read no collection; always return the documented empty result.
  - `nodes_top`:
    - Read no collection; always return the documented empty result.
  - `pods_top`:
    - Read no collection; always return the documented empty result.

- Writes:
  - None; this operation is read-only.
  - Do not write any store collection.

- Response contract by action:
  - `find_namespace`
    - When a matching `ocpv_namespaces` row exists:
      - Return an object with exactly:
        - `cluster`
        - `namespace`
        - `status`
      - `status` is copied verbatim from the matched row's stored `status`.
      - Do not return `ocpv_namespace_id`.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "namespace": "sandbox-1234-demo",
        "status": "Active"
      }
      ```
  - `list_pvcs`
    - Return an object with exactly:
      - `cluster`
      - `namespace`
      - `pvcs`
      - `count`
      - `pending_count`
    - Each `pvcs` element is the stored row projected to exactly:
      - `name`
      - `status`
      - `storage_class`
      - `size`
      - `volume_mode`
      - `access_modes`
      - `events` when stored
    - Do not include storage keys ending in `_id`.
    - Do not include `cluster` or `namespace` inside each element.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "namespace": "sandbox-1234-demo",
        "pvcs": [
          {
            "name": "vm-rootdisk",
            "status": "Pending",
            "storage_class": "ocs-external-storagecluster-ceph-rbd",
            "size": "30Gi",
            "volume_mode": "Filesystem",
            "access_modes": ["ReadWriteOnce"],
            "events": ["waiting for first consumer to be created before binding"]
          }
        ],
        "count": 1,
        "pending_count": 1
      }
      ```
  - `list_pvs`
    - Return an object with exactly:
      - `cluster`
      - `summary`
      - `total_pvs`
      - `total_bound_gi`
    - `summary` is a list of aggregate rows grouped by `(node, storage_class)`, not individual PVs.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "summary": [
          {
            "node": "worker-0",
            "storage_class": "ocs-external-storagecluster-ceph-rbd",
            "count": 3,
            "bound_gi": 90
          }
        ],
        "total_pvs": 3,
        "total_bound_gi": 90
      }
      ```
  - `list_storage_classes`
    - Return an object with exactly:
      - `cluster`
      - `storage_classes`
      - `count`
    - Each `storage_classes` element is the stored row projected to exactly the fields declared by that action's response shape.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "storage_classes": [
          {
            "name": "ocs-external-storagecluster-ceph-rbd"
          }
        ],
        "count": 1
      }
      ```
  - `list_vms`
    - Return an object with exactly:
      - `cluster`
      - `namespace`
      - `vms`
      - `count`
    - Each `vms` element is the stored row projected to exactly:
      - `name`
      - `status`
      - `ready`
      - `phase`
      - `node`
      - `ip`
      - `vcpus`
      - `memory`
      - `disks`
      - `volumes`
      - `condition` when stored
    - Do not include storage keys ending in `_id`.
    - Do not include `cluster` or `namespace` inside each element.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "namespace": "sandbox-1234-demo",
        "vms": [
          {
            "name": "rhel9-workstation",
            "status": "Running",
            "ready": true,
            "phase": "Running",
            "node": "worker-0",
            "ip": "10.0.0.25",
            "vcpus": 4,
            "memory": "16Gi",
            "disks": 2,
            "volumes": 2
          }
        ],
        "count": 1
      }
      ```
  - `get_node_resources`
    - Return an object with exactly:
      - `cluster`
      - `nodes`
      - `count`
    - Always return the documented empty result.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "nodes": [],
        "count": 0
      }
      ```
  - `get_ocpv_pod_logs`
    - Return an object with exactly:
      - `cluster`
      - `namespace`
      - `total_pods`
      - `pods_shown`
      - `results`
    - Always return the documented empty result.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "namespace": "sandbox-1234-demo",
        "total_pods": 0,
        "pods_shown": 0,
        "results": []
      }
      ```
  - `list_pods`
    - Return an object with exactly:
      - `cluster`
      - `namespace`
      - `pods`
      - `count`
    - Always return the documented empty result.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "namespace": "sandbox-1234-demo",
        "pods": [],
        "count": 0
      }
      ```
  - `nodes_top`
    - Return an object with exactly:
      - `cluster`
      - `nodes`
      - `count`
    - Always return the documented empty result.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "nodes": [],
        "count": 0
      }
      ```
  - `pods_top`
    - Return an object with exactly:
      - `cluster`
      - `namespace`
      - `pods`
      - `count`
    - Always return the documented empty result.
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "namespace": "sandbox-1234-demo",
        "pods": [],
        "count": 0
      }
      ```
  - `list_machines`
    - Return an object with exactly:
      - `cluster`
      - `machinesets`
      - `machineset_count`
      - `machines`
      - `machine_count`
    - Each `machinesets` element is projected to exactly:
      - `name`
      - `namespace`
      - `replicas`
      - `ready_replicas`
      - `available_replicas`
    - Each `machines` element is projected to exactly:
      - `name`
      - `namespace`
      - `phase`
      - `node`
      - `provider_id`
    - Example:
      ```json
      {
        "cluster": "ocpv08",
        "machinesets": [
          {
            "name": "worker-us-east-1a",
            "namespace": "openshift-machine-api",
            "replicas": 3,
            "ready_replicas": 3,
            "available_replicas": 3
          }
        ],
        "machineset_count": 1,
        "machines": [
          {
            "name": "worker-us-east-1a-abcde",
            "namespace": "openshift-machine-api",
            "phase": "Running",
            "node": "worker-0",
            "provider_id": "aws:///us-east-1a/i-1234567890abcdef0"
          }
        ],
        "machine_count": 1
      }
      ```

- Error conditions:
  - When `action` is not one of the supported enum values:
    - Return:
      ```json
      {
        "error": "Unknown action: bad_action. Use: find_namespace, list_pvcs, list_pvs, list_storage_classes, list_vms, get_node_resources, get_ocpv_pod_logs, list_pods, nodes_top, pods_top, list_machines",
        "cluster": ""
      }
      ```
    - Do NOT return this error if `action` is one of the documented values.
  - When `action` is namespace-scoped and `namespace` is omitted:
    - Applies to:
      - `find_namespace`
      - `list_pvcs`
      - `list_vms`
      - `get_ocpv_pod_logs`
      - `list_pods`
      - `pods_top`
    - Return an in-band error object with `error` and `cluster`.
    - Example:
      ```json
      {
        "error": "namespace is required for list_pvcs",
        "cluster": ""
      }
      ```
    - Do NOT return this error if `namespace` is present.
  - When `cluster` is omitted, `sandbox_comment` does not resolve a cluster, and cluster discovery cannot resolve one from `namespace`:
    - Return an in-band error object with `error` and `cluster`.
    - Example:
      ```json
      {
        "error": "No cluster specified and could not resolve one. Available clusters: [\"ocpv08\"]",
        "cluster": ""
      }
      ```
    - Do NOT return this error if an explicit `cluster` is provided, or `sandbox_comment` resolves a cluster, or namespace discovery finds a matching `ocpv_namespaces` row.
  - When `action = find_namespace` and no `ocpv_namespaces` row matches `namespace`:
    - Return:
      ```json
      {
        "error": "Namespace 'sandbox-9999-demo' not found on any OCPV cluster",
        "clusters_searched": ["ocpv08"]
      }
      ```
    - Do NOT return this error if a matching `ocpv_namespaces` row exists.
  - When `action = get_ocpv_pod_logs` and the implementation hits the documented permission failure branch:
    - Return an in-band error object with:
      - `error`
      - `cluster`
      - `namespace`
    - Example:
      ```json
      {
        "error": "No permission to list pods in sandbox-1234-demo on ocpv08.",
        "cluster": "ocpv08",
        "namespace": "sandbox-1234-demo"
      }
      ```
    - Do NOT return this error if the request is otherwise handled through the documented empty-result path.
  - When any other exception occurs during cluster resolution or dispatch:
    - Return an in-band error object with:
      - `error`
      - `cluster`
    - `cluster` is whatever value had been resolved so far, including `""`.
    - Example:
      ```json
      {
        "error": "unexpected failure text",
        "cluster": "ocpv08"
      }
      ```
    - Do NOT return this error if the request matches one of the documented success or specific in-band error paths above.

- Empty-result contract:
  - For list-style actions, when no stored row matches:
    - Return the action's normal success envelope.
    - Return the list field as `[]`.
    - Return every count field as `0`.
    - Do not synthesize rows or placeholder values.
  - `find_namespace` is not a list-style action:
    - When no match exists, return the documented in-band not-found error with `error` and `clusters_searched`.
  - Actions with no backing collection:
    - `get_node_resources`
    - `get_ocpv_pod_logs`
    - `list_pods`
    - `nodes_top`
    - `pods_top`
    - Always return their documented empty success envelope, unless a documented in-band error path applies.
  - For stored optional fields:
    - When an optional field is absent on a matched stored row, omit it from that element.
    - Do not compute or invent it.

- Idempotency behavior:
  - Read-only operation; no state changes.
  - Repeating the same request against unchanged stores returns the same shape and values, subject only to store contents.

#### Derived fields

- `find_namespace.status`
  - Copied unchanged from the matched `ocpv_namespaces.status`; not computed.
- `list_pvcs.count`
  - `len(pvcs)` after filtering and `max_results` truncation.
- `list_pvcs.pending_count`
  - Count of returned `pvcs` whose `status` is `Pending`.
- `list_pvs.summary`
  - Aggregate matched `ocpv_pvcs` rows by `(node, storage_class)`.
- `list_pvs.total_pvs`
  - Sum of per-group PV counts in `summary`.
- `list_pvs.total_bound_gi`
  - Sum of Gi-suffixed bound capacities included in `summary`; integer-truncated and lower-bound only.
- `list_storage_classes.count`
  - `len(storage_classes)`.
- `list_vms.count`
  - `len(vms)` after filtering and `max_results` truncation.
- `get_node_resources.count`
  - `len(nodes)`.
- `get_ocpv_pod_logs.total_pods`
  - Number of matched pods; with no backing collection here, `0`.
- `get_ocpv_pod_logs.pods_shown`
  - Number of returned pod log entries, capped at 5; with no backing collection here, `0`.
- `list_pods.count`
  - `len(pods)`.
- `nodes_top.count`
  - `len(nodes)`.
- `pods_top.count`
  - `len(pods)`.
- `list_machineset_count`
  - none
- `list_machines.machineset_count`
  - `len(machinesets)` after filtering and `max_results` truncation.
- `list_machines.machine_count`
  - `len(machines)` after filtering and `max_results` truncation.

### /query_babylon_catalog POST

- Required inputs:
  - `action`
  - `namespace` when `action` is `list_deployments`, `get_deployment`, `list_workshops`, `list_multiworkshops`, or `get_babylon_pod_logs`
  - `name` when `action` is `get_component`, `get_workshop`, or `get_multiworkshop`
  - both `name` and `namespace` when `action` is `get_deployment`
- Optional inputs:
  - `cluster`
    - when omitted for `list_anarchy_subjects` or `list_anarchy_actions` and `guid` is present, search every configured cluster represented by distinct stored `cluster` values in the action's collection until one cluster has a match
    - when omitted for `get_workshop` or `get_multiworkshop` and `name` is present, search every configured cluster represented by distinct stored `cluster` values in the action's collection until one cluster has a match
    - when omitted for any other action, resolve from `sandbox_comment`; if not resolvable, return in-band error
  - `sandbox_comment`
    - used only to resolve `cluster` when `cluster` is omitted and the action is not using an all-clusters search path
  - `search`
    - action-specific filter:
      - `search_catalog`: case-insensitive substring over `ci_name`, `display_name`, `keywords`
      - `list_deployments`: `name`, `catalog_item`
      - `list_anarchy_subjects`: `name`, `governor`
      - `list_resource_pools`: `name`
      - `list_workshops`: `name`, `catalog_item`, `display_name`
      - `list_multiworkshops`: `name`, `display_name`
      - `list_anarchy_actions`: `name`, `subject_name`, `action`
      - `get_babylon_pod_logs`: grep over log lines
  - `env_type`
    - used only when `action` is `search_catalog`; case-insensitive substring test against `ci_name`
  - `account_id`
    - used only when `action` is `list_deployments`; exact equality against `provision_data.sandbox_account_id`
  - `guid`
    - used only by:
      - `list_deployments`: exact equality against `provision_data.guid`, falling back to `instance_vars.guid`
      - `list_anarchy_subjects`: match when `instance_vars.guid` equals `guid` or `name` contains `guid`
      - `list_anarchy_actions`: match when `subject_name` contains `guid`
      - `get_babylon_pod_logs`: grep term only when `search` is absent
  - `max_results`
    - default `50`
    - used by list/search actions and `get_babylon_pod_logs`
    - ignored by `get_component`, `get_deployment`, `get_workshop`, `get_multiworkshop`

- Caller expectations:
  - none

- Store reads and writes:
  - Read-only operation; do not write any store collection.
  - Cluster resolution:
    - when `cluster` is provided, use it as given
    - when `cluster` is omitted and `sandbox_comment` resolves a cluster, use that resolved cluster
    - when `cluster` is omitted and the action is an all-clusters search path, search distinct stored `cluster` values in the relevant collection
  - For every action except all-clusters search miss handling, resolve cluster first, then filter the action's collection by stored `cluster` before any other argument.
  - `search_catalog`
    - read `babylon_catalog_items`, filtered by `cluster`
  - `get_component`
    - read `babylon_components`, filtered by `cluster`
    - lookup by resolved component `name`
  - `list_deployments`
    - read `babylon_deployments`, filtered by `cluster`
  - `get_deployment`
    - read `babylon_deployments`, filtered by `cluster`
    - match `namespace` and `name` exactly
  - `list_anarchy_subjects`
    - read `babylon_anarchy_subjects`, filtered by `cluster` for normal path
    - for all-clusters search, search distinct `cluster` values from `babylon_anarchy_subjects`
  - `list_anarchy_actions`
    - read `babylon_anarchy_actions`, filtered by `cluster` for normal path
    - for all-clusters search, search distinct `cluster` values from `babylon_anarchy_actions`
  - `list_resource_pools`
    - read `babylon_resource_pools`, filtered by `cluster`
  - `list_workshops`
    - read `babylon_workshops`, filtered by `cluster`
  - `get_workshop`
    - read `babylon_workshops`, filtered by `cluster`
    - when `cluster` omitted, search distinct `cluster` values from `babylon_workshops`
    - match by `name`; if `namespace` is provided, also require exact `namespace`
  - `list_multiworkshops`
    - read `babylon_multiworkshops`, filtered by `cluster`
  - `get_multiworkshop`
    - read parent from `babylon_multiworkshops`, filtered by `cluster`
    - when `cluster` omitted, search distinct `cluster` values from `babylon_multiworkshops`
    - match by `name`; if `namespace` is provided, also require exact `namespace`
    - read children from `babylon_workshops` where `cluster` = parent `cluster`, `namespace` = parent `namespace`, and `multiworkshop` = parent `name`
  - `get_babylon_pod_logs`
    - read no collection; always return documented empty result

- Behavior by `action`:
  - `search_catalog`
    - return rows from `babylon_catalog_items` projected to exactly:
      - `ci_name`, `display_name`, `namespace`, `stage`, `multiuser`, `asset_uuid`, `keywords`
    - apply `search` and `env_type` filters after cluster filter
    - response keys: `cluster`, `items`, `count`, `total_scanned`, `truncated`
    - `truncated` is `true` when `count >= max_results` boundary is met before truncation result is returned
  - `get_component`
    - return the stored component projected to:
      - `cluster`, `name`, `cloud_provider`, `env_type`, `platform`, `expected_instances`, `definition`
      - plus `scm_url`, `scm_ref`, `agnosticv_repo`, `agnosticv_path`, `sub_components` when stored
    - never return `babylon_component_id`
    - in `definition`, matching secret values are masked to `[REDACTED]`
  - `list_deployments`
    - require `namespace`
    - filter by `namespace`
    - optional filters:
      - `search` over `name`, `catalog_item`
      - `account_id` exact match on `provision_data.sandbox_account_id`
      - `guid` exact match on `provision_data.guid`, falling back to `instance_vars.guid`
    - response keys: `cluster`, `namespace`, `deployments`, `count`, `truncated`
  - `get_deployment`
    - require both `name` and `namespace`
    - return exactly `{cluster, deployment}` with the stored deployment nested under `deployment`
    - never flatten deployment fields to top level
  - `list_anarchy_subjects`
    - when `guid` is absent, omit rows whose `current_state` is `destroyed`
    - when `guid` is present and `cluster` omitted, search every distinct cluster in `babylon_anarchy_subjects` until one cluster has a match
    - match `guid` when `instance_vars.guid` equals `guid` or `name` contains `guid`
    - optional `namespace` narrows results; without `namespace`, search cluster-wide
    - response keys on normal result: `cluster`, `subjects`, `count`, `truncated`, `namespaces_searched`, `errors`
    - `errors` is `null` when empty; never omit it and never return `[]`
    - `namespaces_searched` is:
      - `"all (cluster-wide)"` when request has no `namespace`
      - `[<namespace>]` when request has `namespace`
    - each subject is projected to exactly:
      - `name`, `namespace`, `governor`, `current_state`, `desired_state`, `healthy`, `instance_vars`
      - plus `resource_claim`, `requester_email`, `tower_jobs` when stored
  - `list_anarchy_actions`
    - when `guid` is present and `cluster` omitted, search every distinct cluster in `babylon_anarchy_actions` until one cluster has a match
    - match `guid` only when `subject_name` contains `guid`
    - optional `namespace` narrows results; without `namespace`, search cluster-wide
    - response keys on normal result: `cluster`, `actions`, `count`, `truncated`, `namespaces_searched`, `errors`
    - `errors` is `null` when empty; never omit it and never return `[]`
    - `namespaces_searched` is:
      - `"all (cluster-wide)"` when request has no `namespace`
      - `[<namespace>]` when request has `namespace`
    - each action is projected to exactly:
      - `name`, `namespace`, `action`, `after`, `subject_name`, `subject_namespace`, `governor`, `state`, `finished`
  - `list_resource_pools`
    - ignore request `namespace`
    - return rows from `babylon_resource_pools` projected to:
      - `name`, `namespace`, `min_available`, `max_unready`, `lifespan`, `resource_handle_count`
      - plus `provider_name`, `resource_name` when stored
    - response keys: `cluster`, `pools`, `count`, `truncated`
  - `list_workshops`
    - require `namespace`
    - return rows from `babylon_workshops` in that namespace projected to exactly:
      - `name`, `namespace`, `catalog_item`, `workshop_id`, `display_name`, `description`, `open_registration`, `lifespan`, `provision_count`, `user_count`, `user_assignments_count`, `resource_claims_count`
    - response keys: `cluster`, `namespace`, `workshops`, `count`, `truncated`
    - `user_count` here is an integer
  - `get_workshop`
    - require `name`
    - when `cluster` omitted, search every distinct cluster in `babylon_workshops` until one row matches
    - return exactly:
      - `cluster`, `name`, `namespace`, `display_name`, `catalog_item`, `workshop_id`, `requester`, `multiworkshop`, `lifespan`, `provision_count`, `user_count`, `resource_claims`
    - `user_count` is an empty object `{}` when the field is absent in the source
  - `list_multiworkshops`
    - require `namespace`
    - return rows from `babylon_multiworkshops` in that namespace projected to exactly:
      - `name`, `namespace`, `display_name`, `number_seats`, `start_date`, `end_date`, `purpose`, `assets`, `asset_count`
    - response keys: `cluster`, `namespace`, `multiworkshops`, `count`, `truncated`
  - `get_multiworkshop`
    - require `name`
    - when `cluster` omitted, search every distinct cluster in `babylon_multiworkshops` until one parent row matches
    - read child workshops from `babylon_workshops` with same `cluster` and `namespace` and `multiworkshop` equal to parent `name`
    - return parent fields:
      - `cluster`, `name`, `namespace`, `display_name`, `requester`, `seats`, `start_date`, `end_date`, `purpose`
      - plus `summary` and `workshops`
    - each child workshop carries:
      - `name`, `display_name`, `catalog_item`, `workshop_id`, `provision_count`, `resource_claims`
  - `get_babylon_pod_logs`
    - require `namespace`
    - read no store collection
    - always return documented empty result with `pods` empty
    - matching secret log lines are dropped silently; because no collection backs this action, no log lines are returned in simulation

- Response shape:
  - Success response is one of these exact envelopes, depending on `action`:
    - `search_catalog`: `{cluster, items, count, total_scanned, truncated}`
    - `get_component`: projected component object
    - `list_deployments`: `{cluster, namespace, deployments, count, truncated}`
    - `get_deployment`: `{cluster, deployment}`
    - `list_anarchy_subjects`: `{cluster, subjects, count, truncated, namespaces_searched, errors}`
    - `list_anarchy_actions`: `{cluster, actions, count, truncated, namespaces_searched, errors}`
    - `list_resource_pools`: `{cluster, pools, count, truncated}`
    - `list_workshops`: `{cluster, namespace, workshops, count, truncated}`
    - `get_workshop`: `{cluster, name, namespace, display_name, catalog_item, workshop_id, requester, multiworkshop, lifespan, provision_count, user_count, resource_claims}`
    - `list_multiworkshops`: `{cluster, namespace, multiworkshops, count, truncated}`
    - `get_multiworkshop`: `{cluster, name, namespace, display_name, requester, seats, start_date, end_date, purpose, summary, workshops}`
    - `get_babylon_pod_logs`: `{cluster, namespace, pods, message}`
    - all-clusters no-match for `list_anarchy_subjects`: `{clusters_searched, subjects, count, truncated, errors}`
    - all-clusters no-match for `list_anarchy_actions`: `{clusters_searched, actions, count, truncated, errors}`
    - in-band error: `{error}` or `{error, cluster}` depending on failure point
  - Never:
    - rename keys
    - replace list keys with collection names or generic `items`
    - drop envelope keys
    - include storage-only fields ending in `_id`
    - include `cluster` inside list elements
    - include `multiworkshop` in list elements or outside `get_workshop`

- Concrete JSON example:
```json
{
  "cluster": "east",
  "subjects": [
    {
      "name": "guid-qglkb",
      "namespace": "babylon-guid-qglkb",
      "governor": "babylon",
      "current_state": "running",
      "desired_state": "running",
      "healthy": true,
      "instance_vars": {
        "guid": "qglkb"
      },
      "tower_jobs": [
        {
          "id": 123
        }
      ]
    }
  ],
  "count": 1,
  "truncated": false,
  "namespaces_searched": "all (cluster-wide)",
  "errors": null
}
```

- Error conditions:
  - Return `{ "error": "No Babylon clusters configured. Set babylon.clusters in config." }` when cluster resolution requires configured clusters and none are available.
    - Do NOT return this error if the request provides `cluster`.
  - Return `{ "error": "Could not determine which Babylon cluster to query. ... Configured clusters: [...]" }` when `cluster` is omitted, the action is not on an all-clusters search path, and `sandbox_comment` does not resolve a cluster.
    - Do NOT return this error if the action is `list_anarchy_subjects` or `list_anarchy_actions` with `guid`, or `get_workshop`/`get_multiworkshop` with `name`, because those use all-clusters search instead.
  - Return `{ "error": "name is required for get_component" }` when `action` is `get_component` and `name` is absent.
    - Do NOT return this error if `action` is any other value.
  - Return `{ "error": "namespace is required for list_deployments. ..." }` when `action` is `list_deployments` and `namespace` is absent.
    - Do NOT return this error if `namespace` is merely unused by the chosen action.
  - Return `{ "error": "Both name and namespace are required for get_deployment" }` when `action` is `get_deployment` and either `name` or `namespace` is absent.
    - Do NOT return this error if both are present, even when no row matches.
  - Return `{ "error": "namespace is required for list_workshops. ..." }` when `action` is `list_workshops` and `namespace` is absent.
    - Do NOT return this error if `action` is `get_workshop`.
  - Return `{ "error": "name is required for get_workshop" }` when `action` is `get_workshop` and `name` is absent.
    - Do NOT return this error if `action` is `list_workshops`.
  - Return `{ "error": "namespace is required for list_multiworkshops. ..." }` when `action` is `list_multiworkshops` and `namespace` is absent.
    - Do NOT return this error if `action` is `get_multiworkshop`.
  - Return `{ "error": "name is required for get_multiworkshop" }` when `action` is `get_multiworkshop` and `name` is absent.
    - Do NOT return this error if `action` is `list_multiworkshops`.
  - Return `{ "error": "namespace is required for get_babylon_pod_logs. ..." }` when `action` is `get_babylon_pod_logs` and `namespace` is absent.
    - Do NOT return this error if `action` is any other value.
  - Return `{ "error": "AgnosticVComponent not found: tried [...]. Error: ...", "cluster": "<resolved cluster>" }` when `action` is `get_component` and no component row matches the resolved/probed name.
    - Do NOT return this error if a matching component row exists after name normalization/suffix probing.
  - Return `{ "error": "Workshop '<name>' not found on cluster <cluster>.", "cluster": "<resolved cluster>" }` when `action` is `get_workshop` and no workshop row matches.
    - Do NOT return this error if a matching row exists on any searched cluster in the all-clusters path.
  - Return an in-band not-found error with `cluster` when `action` is `get_deployment` or `get_multiworkshop` and no named row matches on the resolved cluster.
    - Do NOT return this error for list/search actions; those return documented empty results.
  - Return `{ "error": "Unknown action: <action>. Use: ..." }` when `action` is not one of the supported enum values.
    - Do NOT return this error if `action` is one of the documented actions, even if it yields no matches.
  - Return `{ "error": "Babylon query failed: ...", "cluster": "<resolved cluster>" }` when an exception occurs after dispatch or inside a caught per-action failure path.
    - Do NOT return this error for ordinary no-match cases that have a documented empty result or not-found error.

- Empty-result contract:
  - For `search_catalog`, `list_deployments`, `list_resource_pools`, `list_workshops`, `list_multiworkshops`:
    - return the normal envelope with the correct list key as `[]`
    - return `count: 0`
    - return `truncated: false`
    - preserve envelope keys such as `cluster` and `namespace` where applicable
  - For `list_anarchy_subjects` and `list_anarchy_actions` on a resolved cluster with no matches:
    - return normal listing envelope
    - list key is `[]`
    - `count: 0`
    - `truncated: false`
    - `errors: null`
    - `namespaces_searched` still follows request shape rules
  - For `list_anarchy_subjects` and `list_anarchy_actions` with `guid` and no `cluster`, when no searched cluster has a match:
    - return `{clusters_searched, subjects|actions, count, truncated, errors}`
    - omit `cluster`
    - omit `namespaces_searched`
    - list key is `[]`
    - `count: 0`
    - `truncated: false`
    - `errors: null`
  - For `get_babylon_pod_logs`:
    - always return documented empty result with `pods: []`
  - For lookup actions `get_component`, `get_deployment`, `get_workshop`, `get_multiworkshop`:
    - do not return an empty success object; return the documented in-band not-found error instead

- Idempotency behavior:
  - Read-only operation; idempotent for the same request against unchanged store contents.
  - No store state changes.
  - All variability comes from current store contents and action-specific filtering.

#### Derived fields

- `count`: length of the returned list for the action's list key
- `truncated`: `true` when the number of matched rows before truncation is greater than or equal to `max_results`; otherwise `false`
- `total_scanned`: number of rows scanned for `search_catalog` after cluster scoping and before result truncation
- `expected_instances`: returned from stored component field; not computed here
- `namespaces_searched`:
  - `"all (cluster-wide)"` when request omits `namespace`
  - `[namespace]` when request includes `namespace`
- `errors`: `null` when there are no errors on anarchy listing responses
- `user_count` in `get_workshop`: `{}` when the source field is absent
- `summary.total_workshops`: length of returned `workshops` in `get_multiworkshop`
- `summary.active`: count of returned child workshops considered active by stored child data
- `summary.failed`: count of returned child workshops considered failed by stored child data
