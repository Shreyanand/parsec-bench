---
name: parsec-cost
description: Simulation skill for the parsec cost tools API.
---

# parsec cost tools Simulation

## Core Principles

- Impersonate the parsec cost tools API exactly as documented in the operation
  sections below. Do not invent operations, fields, or error conditions.
- All responses must match the operation's response schema precisely.

## Session State Management

State is kept in collections defined by `schema.json`. Use the `state_*` tools to
read and write entities. Do not list field names or types here — consult
`schema.json` for the authoritative shape.

Collections: account_costs, aws_cost_results, azure_cost_results, azure_service_costs, azure_subscription_costs, capacity_metric_results, capacity_totals, capacity_windows, cost_monitor_results, gcp_cost_results, periods.

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
- `AccountCost.total`: integer-like or decimal cost amount in the inclusive range 0 to 10000000.
- `AwsCostResult.accounts_queried`: integer in the inclusive range 0 to 5000.
- `AwsCostResult.total_cost`: inclusive range 0 to 50000000.
- `AzureCostResult.blobs_processed`: integer in the inclusive range 0 to 100000.
- `AzureCostResult.total_cost`: inclusive range 0 to 50000000.
- `AzureServiceCost.cost`: inclusive range 0 to 5000000.
- `AzureServiceCost.meter_subcategories` numeric values: each inclusive range 0 to 5000000.
- `AzureSubscriptionCost.gpu_cost`: inclusive range 0 to 5000000.
- `AzureSubscriptionCost.total`: inclusive range 0 to 10000000.
- `CapacityTotals.overall_utilization_pct`: inclusive range 0 to 100.
- `CapacityTotals.total_dimensions`: integer in the inclusive range 0 to 10000.
- `CapacityTotals.total_estimated_cost_usd`: inclusive range 0 to 50000000.
- `CapacityTotals.transient_cost_usd`: inclusive range 0 to 50000000.
- `CapacityTotals.transient_excluded`: integer in the inclusive range 0 to 10000.
- `CapacityTotals.unused_estimated_cost_usd`: inclusive range 0 to 50000000.
- `GcpCostResult.breakdown[].cost`: inclusive range 0 to 10000000.
- `GcpCostResult.daily_rows`: integer in the inclusive range 0 to 10000000.
- `GcpCostResult.total_cost`: inclusive range 0 to 50000000.
- Ordering constraints for stored cost hierarchies must hold exactly as stored and never be recomputed or normalized by the simulator.
- When a returned response includes both `AzureSubscriptionCost.total` and `AzureSubscriptionCost.gpu_cost`, `gpu_cost` must be less than or equal to `total`.
- When a returned response includes both `CapacityTotals.unused_estimated_cost_usd` and `CapacityTotals.total_estimated_cost_usd`, `unused_estimated_cost_usd` must be less than or equal to `total_estimated_cost_usd`.
- When a returned response includes both `CapacityTotals.transient_excluded` and `CapacityTotals.total_dimensions`, `transient_excluded` must be less than or equal to `total_dimensions`.
- All numeric fields are non-negative.
- Returned arrays preserve stored order; no numeric sort is applied by the simulator.

### Derivation Rules
- `AwsCostResult.accounts_queried` equals the number of returned `results` entries.
- `AwsCostResult.total_cost` equals the sum of returned `results[].total`.
- `AccountCost.total` is never recomputed from `items`; it is returned exactly as stored.
- `AzureCostResult.total_cost` equals the sum of returned `results[].total`.
- `AzureSubscriptionCost.total` is never recomputed from `services`; it is returned exactly as stored.
- `AzureSubscriptionCost.gpu_cost` is never recomputed from `services`; it is returned exactly as stored.
- `AzureServiceCost.cost` is never recomputed from `meter_subcategories`; it is returned exactly as stored.
- `AzureCostResult.blobs_processed` is returned exactly as stored when present and omitted when absent.
- `AzureCostResult.cache_last_refresh` is returned exactly as stored when present and omitted when absent.
- `AzureCostResult.meter_filter` is echoed from the request only when the selected stored row carries that field; otherwise it is omitted.
- `AzureCostResult.note` is returned exactly as stored when present and omitted when absent.
- `GcpCostResult.total_cost` is returned exactly as stored and never recomputed from `breakdown`.
- `GcpCostResult.daily_rows` is returned exactly as stored and never inferred from `breakdown` length or dates.
- `GcpCostResult.group_by` defaults to `SERVICE` only for row selection when the request omits it; the returned `group_by` is the selected row's stored value.
- `CapacityMetricResult.totals` equals the stored `CapacityTotals` row referenced by `capacity_totals_id`.
- `CapacityTotals.overall_utilization_pct` is returned exactly as stored and never recomputed from other totals.
- `CapacityTotals.total_estimated_cost_usd` is returned exactly as stored.
- `CapacityTotals.unused_estimated_cost_usd` is returned exactly as stored.
- `CapacityTotals.transient_cost_usd` is returned exactly as stored when present and omitted when absent.
- `CapacityTotals.transient_excluded` is returned exactly as stored when present and omitted when absent.
- `CapacityTotals.total_dimensions` is returned exactly as stored.
- `CapacityTotals.results_truncated` is returned exactly as stored when present and omitted when absent.
- For `query_cost_monitor`, when the selected stored row has `_dashboard_link`, the response object is exactly `{results, _dashboard_link}` using the stored `results` and stored `_dashboard_link`.
- For `query_cost_monitor`, when the selected stored row does not have `_dashboard_link`, the response is the stored `results` array itself, not an object.
- For `query_cost_monitor`, `endpoint` and `cost_monitor_result_id` are storage-only and never appear in the response.
- For any search operation with no matching stored row, every returned count field is 0 in the documented empty result.
- For `query_azure_costs`, when `azure_cost_results` holds no rows at all and the request carries neither `subscription_names` nor `meter_filter`, the response is the documented in-band error and no numeric field is derived.
- For all operations, only documented count-equals-length and sum-of-returned-amounts derivations are allowed; every other numeric field is copied from stored rows unchanged.

### On-Demand Generation Rules
- No entity record may be generated on demand.
- No numeric field may be generated from hashes, random values, request dates, request identifiers, list lengths other than the documented count derivations, or inferred business logic.
- If a logical record is not present in the store, the simulator must return the documented empty result or documented in-band error for that operation instead of synthesizing numeric values.
- Regeneration of the same logical record means re-reading the same stored row and returning the same stored numeric values unchanged.
- `period_id`, `capacity_window_id`, and `capacity_totals_id` are opaque selectors for stored rows and must never be generated or numerically derived from `start`, `end`, or any request window.
- For empty search results, generated numeric values are limited to the documented zero counts only.
- Stored array order and stored map contents must be preserved exactly; the simulator must not generate filler entries to satisfy non-negativity or ordering constraints.
- If an optional numeric field such as `AzureCostResult.blobs_processed`, `CapacityTotals.transient_cost_usd`, or `CapacityTotals.transient_excluded` is absent in the stored row, it remains absent; the simulator must not generate `0` unless the documented empty-result shape explicitly requires a zero count.
- Non-negativity constraints are enforced only by selecting and returning stored rows that already satisfy them; the simulator must not clamp, round, or adjust stored numeric values.

## Example Scenarios

Representative user stories this simulation can satisfy with the seeded data:

1. **AWS service cost review** — A finance analyst wants to review AWS spending for a reporting period grouped by service across selected accounts. (operations: query_aws_costs)
2. **Azure subscription cost check** — A cloud operations user wants to inspect Azure costs for one or more subscriptions and see service and meter-level breakdowns for a period. (operations: query_azure_costs)
3. **GCP project spend breakdown** — A platform owner wants to analyze GCP billing for a reporting period grouped by project or service. (operations: query_gcp_costs)
4. **Capacity utilization analysis** — An infrastructure manager wants to evaluate AWS capacity reservation utilization and estimated unused cost for a chosen window and grouping. (operations: query_aws_capacity_manager)
5. **Cached monitor dashboard lookup** — A stakeholder wants to retrieve a cached aggregated cost-monitor view and any linked dashboard for quick reporting. (operations: query_cost_monitor)

## API Operation Simulation

### /query_aws_costs POST

- **Purpose**
  - Return one stored AWS cost result for the requested date window, with per-account breakdowns and org-level total, or an in-band error object.
  - This is a read-only operation; it does not write any store collection.

- **Required inputs**
  - `account_ids` array of strings
    - Required even when empty.
    - When `account_ids` is `[]`, treat it as an org-wide query.
  - `start_date` string
  - `end_date` string

- **Optional inputs**
  - `group_by` string
    - Optional.
    - When omitted, use `SERVICE`.
    - When provided, must be one of `SERVICE`, `INSTANCE_TYPE`, or `LINKED_ACCOUNT`.

- **Caller expectations**
  - none

- **Store reads**
  - Read `periods` to resolve the requested window:
    - find the row where `start` = request `start_date` and `end` = request `end_date`
    - use its `period_id`
  - Then read `aws_cost_results` by matching:
    - `period_id` = resolved `period_id`
  - Do not write `aws_cost_results`.
  - Do not write `periods`.

- **Store writes / state changes**
  - none

- **Selection and filtering rules**
  - When a matching `periods` row exists and a matching `aws_cost_results` row exists for that `period_id`, return that stored `aws_cost_results` row exactly as stored.
  - `account_ids` is an input to the operation, but per the store-authoritative contract, do not synthesize or derive filtered account rows not present in storage.
  - `group_by` defaults to `SERVICE` when omitted, but the response still comes only from a stored matching row; do not generate a regrouped result.
  - Never generate, derive, or synthesize a missing result row or missing field.
  - An optional field omitted in the stored row is omitted in the response.
  - An optional field present in the stored row is returned unchanged.

- **Response shape**
  - Success: an `AwsCostResult` object
    - Fields:
      - `accounts_queried`
      - `aws_cost_result_id`
      - `group_by`
      - `period`
      - `period_id`
      - `results`
      - `total_cost`
  - Failure: an in-band object
    - Fields:
      - `error`

- **Concrete success example**
  ```json
  {
    "accounts_queried": 2,
    "aws_cost_result_id": "acr_001",
    "group_by": "SERVICE",
    "period": {
      "start": "2026-01-01",
      "end": "2026-01-31"
    },
    "period_id": "period_jan_2026",
    "results": [
      {
        "account_id": "111111111111",
        "groups": [
          {
            "key": "AmazonEC2",
            "amount": 120.5,
            "daily": [
              {
                "date": "2026-01-01",
                "amount": 4.0
              },
              {
                "date": "2026-01-02",
                "amount": 3.9
              }
            ]
          }
        ]
      },
      {
        "account_id": "ORG_TOTAL",
        "groups": [
          {
            "key": "AmazonEC2",
            "amount": 220.75,
            "daily": [
              {
                "date": "2026-01-01",
                "amount": 7.2
              },
              {
                "date": "2026-01-02",
                "amount": 7.0
              }
            ]
          }
        ]
      }
    ],
    "total_cost": 220.75
  }
  ```

- **Concrete error example**
  ```json
  {
    "error": "Dates must be YYYY-MM-DD format"
  }
  ```

- **Errors**
  - When `start_date` is not in `YYYY-MM-DD` format, return:
    - `{"error":"Dates must be YYYY-MM-DD format"}`
    - Do NOT return this error if `start_date` is well-formed, even when no stored row matches.
  - When `end_date` is not in `YYYY-MM-DD` format, return:
    - `{"error":"Dates must be YYYY-MM-DD format"}`
    - Do NOT return this error if `end_date` is well-formed, even when no stored row matches.
  - When `group_by` is provided and is not one of `SERVICE`, `INSTANCE_TYPE`, or `LINKED_ACCOUNT`, return:
    - `{"error":"Invalid group_by: x. Must be SERVICE, INSTANCE_TYPE, or LINKED_ACCOUNT"}`
    - with `x` replaced by the provided value
    - Do NOT return this error if `group_by` is omitted; omitted means use default `SERVICE`.
  - When no `periods` row matches `start_date` and `end_date`, return:
    - `{"error":"AWS Cost Explorer query failed: not found"}`
    - Do NOT return this error if a matching `periods` row exists, even when the eventual `aws_cost_results` row is missing.
  - When a matching `periods` row exists but no `aws_cost_results` row matches its `period_id`, return:
    - `{"error":"AWS Cost Explorer query failed: not found"}`
    - Do NOT return this error if a matching `aws_cost_results` row exists for that `period_id`.

- **Empty-result contract**
  - This operation is not a list-returning operation.
  - When no stored row matches, return an in-band not-found error object:
    - `{"error":"AWS Cost Explorer query failed: not found"}`
  - Do not return a synthesized `AwsCostResult`.
  - Do not return an empty object.
  - Do not return an empty list as the top-level response.

- **Idempotency**
  - Read-only and idempotent.
  - Repeating the same request against unchanged stores returns the same success object or the same in-band error object.

- **Derived fields**
  - `group_by`
    - Use request `group_by` when provided; otherwise default to `SERVICE` for request validation/matching.
  - none

### /query_gcp_costs POST

- **Purpose**
  - Return one stored `gcp_cost_results` record for the requested date window and grouping.
  - Return the stored inline `breakdown` array verbatim, in stored order.
  - Return failures **in-band** as `{"error": "..."}`.

- **Required inputs**
  - `start_date` when the request is made.
  - `end_date` when the request is made.

- **Optional inputs**
  - `group_by`
    - When omitted, treat as `SERVICE`.
    - When provided, must be one of `SERVICE` or `PROJECT`.
  - `filter_services`
    - Optional request input.
    - Do **not** use it to read or filter any store collection for this simulator operation.
  - `filter_projects`
    - Optional request input.
    - Do **not** use it to read or filter any store collection for this simulator operation.

- **Store reads**
  - Read `periods` to find the row whose `start` and `end` correspond to `start_date` and `end_date`.
    - Use that row's `period_id`.
  - Read `gcp_cost_results` by:
    - `period_id` = resolved `period_id`
    - `group_by` = request `group_by`, or `SERVICE` when omitted.
  - Do **not** read any other collection.
  - Do **not** join `breakdown` from anywhere else; use the stored inline `breakdown` on the matched `gcp_cost_results` row.
  - Do **not** recompute `total_cost` from `breakdown`.

- **Store writes / state changes**
  - None.
  - This operation is read-only.

- **Response shape**
  - On success, return the matched `gcp_cost_results` row projected as:
    - `breakdown`
    - `daily_rows`
    - `group_by`
    - `period`
    - `total_cost`
  - Return optional fields only if they are present on the stored row; do not synthesize missing optional fields.
  - On failure, return:
    - `{"error": "<message>"}`

- **Concrete success example**
  ```json
  {
    "breakdown": [
      {
        "name": "BigQuery",
        "cost": 123.45
      },
      {
        "name": "Cloud Storage",
        "cost": 67.89
      }
    ],
    "daily_rows": 42,
    "group_by": "SERVICE",
    "period": {
      "start": "2024-01-01",
      "end": "2024-01-31"
    },
    "total_cost": 191.34
  }
  ```

- **Concrete error example**
  ```json
  {
    "error": "Dates must be YYYY-MM-DD format"
  }
  ```

- **Error conditions**
  - When `start_date` or `end_date` is not in `YYYY-MM-DD` format, return:
    - `{"error": "Dates must be YYYY-MM-DD format"}`
    - Do **NOT** return this error if both dates are well-formed strings in `YYYY-MM-DD` format.
  - When the simulator defines GCP BigQuery as not configured for this request path, return:
    - `{"error": "GCP BigQuery not configured"}`
    - Do **NOT** return this error if the installed store is being used as the complete dataset for this operation.
  - When execution reaches the implementation's query-failed path, return:
    - `{"error": "GCP BigQuery query failed: ..."}`
    - Do **NOT** return this error if a matching stored result can be resolved from `periods` and `gcp_cost_results` without backend failure.
  - When no `periods` row matches `start_date` and `end_date`, return an in-band not-found error:
    - `{"error": "GCP BigQuery query failed: no matching cost data"}`
    - Do **NOT** return this error if a `periods` row with corresponding `start` and `end` exists.
  - When a `periods` row matches but no `gcp_cost_results` row matches that `period_id` and effective `group_by`, return an in-band not-found error:
    - `{"error": "GCP BigQuery query failed: no matching cost data"}`
    - Do **NOT** return this error if such a `gcp_cost_results` row exists.

- **Empty-result contract**
  - This is a lookup for one named stored result, not a list-style operation.
  - When no stored row matches the request, return an in-band error object, not a synthesized record and not an empty success object.
  - Do **not** return an empty `breakdown` unless the matched stored `gcp_cost_results` row itself has `breakdown: []`.

- **Idempotency**
  - Idempotent.
  - Repeating the same request against unchanged `periods` and `gcp_cost_results` returns the same response body.

- **Caller expectations**
  - None.

#### Derived fields

- `group_by`
  - Equals request `group_by`, or `SERVICE` when the request omits it, and is used to select the stored row returned.
- `none`

### /query_azure_costs POST

- **Purpose**
  - Query Azure billing data for a requested date window, optionally filtered by `subscription_names` and/or `meter_filter`.
  - Return either:
    - a cached result from `azure_cost_results` with `source: "cache"`, or
    - a live-path result from `azure_cost_results` with `source: "live"`, or
    - an in-band error object `{ "error": "..." }`.

- **Inputs**
  - **Required**
    - `start_date` (`string`)
      - Must be in `YYYY-MM-DD` format.
    - `end_date` (`string`)
      - Must be in `YYYY-MM-DD` format.
  - **Optional**
    - `subscription_names` (`array[string]`)
      - Optional generally.
      - **When** the request is served on the live path, this remains optional only if `meter_filter` is present.
    - `meter_filter` (`string`)
      - Optional generally.
      - **When** `azure_cost_results` holds no rows at all and `subscription_names` is omitted, `meter_filter` is effectively required; otherwise return the documented in-band error before reading any result row.
  - **Caller expectations**
    - none

- **Store reads**
  - Read `azure_cost_results` as a collection-wide existence gate:
    - check whether `azure_cost_results` contains **any rows at all**.
    - This is an unfiltered row-count style gate; it is **not** filtered by request fields.
  - Read `periods` to resolve the requested window:
    - find the row whose `start` equals request `start_date` and whose `end` equals request `end_date`.
    - use that row's `period_id`.
    - **Do not** derive `period_id` from the request dates.
  - On the cache path:
    - read `azure_cost_results` by `period_id` resolved from `periods`.
    - from those rows, select the stored row(s) matching the request's cached-result criteria.
    - return the stored cached result row exactly as stored.
  - On the live path:
    - read `azure_cost_results` for the stored live-path result corresponding to the request.
    - return the stored live-path row exactly as stored.
  - **Do not write** `azure_cost_results`.
  - **Do not write** `periods`.

- **Routing / behavior**
  - **When** `start_date` or `end_date` is not in `YYYY-MM-DD` format:
    - return the in-band date-format error.
  - **When** `azure_cost_results` contains at least one row:
    - take the **cache path**.
    - resolve the request window through `periods`, then use that `period_id` to find cached result rows.
    - **When** the cache path finds no matching stored row for the request:
      - return a normal success payload with `results: []`, not a fallback to live.
  - **When** `azure_cost_results` contains no rows at all:
    - take the **live path**.
    - **When** both `subscription_names` and `meter_filter` are absent:
      - return the documented in-band meter-filter error **before** reading any result row.
    - otherwise return the stored live-path result row for the request.
  - **When** a cache read fails internally:
    - do **not** return a cache-failure error;
    - fall through to the live path behavior.
  - `Azure blob storage not configured` is never returned in this simulation.

- **Response shape**
  - Success returns one of the stored success shapes:
    - cache shape: object matching `AzureCostFromCache`
    - live shape: object matching `AzureCostFromBlobs`
  - Failure returns:
    - `{ "error": "string" }`

- **Concrete success example**
  ```json
  {
    "source": "cache",
    "subscriptions_queried": "2",
    "total_cost": 153.42,
    "period": {
      "start": "2026-06-01",
      "end": "2026-06-30"
    },
    "cache_last_refresh": "2026-07-01T00:00:00Z",
    "meter_filter": "Virtual Machines",
    "results": [
      {
        "subscription_name": "pool-01-374",
        "total_cost": 101.12,
        "meter_categories": [
          {
            "meter_category": "Virtual Machines",
            "meter_subcategory": "NC Series",
            "cost": 101.12
          }
        ]
      },
      {
        "subscription_name": "pool-02-118",
        "total_cost": 52.3,
        "meter_categories": [
          {
            "meter_category": "Virtual Machines",
            "meter_subcategory": "NC Series",
            "cost": 52.3
          }
        ]
      }
    ]
  }
  ```

- **Concrete error example**
  ```json
  {
    "error": "meter_filter is required when querying all subscriptions without cache. Please provide a meter_filter such as 'Virtual Machines', 'Storage', or a specific meter subcategory."
  }
  ```

- **Errors**
  - **When** `start_date` is not in `YYYY-MM-DD` format, or `end_date` is not in `YYYY-MM-DD` format:
    - return:
      - `{"error":"Dates must be YYYY-MM-DD format"}`
    - **Do NOT return this error if …**
      - both dates are well-formed, even if no stored row matches the request.
  - **When** `azure_cost_results` holds no rows at all **and** `subscription_names` is absent **and** `meter_filter` is absent:
    - return:
      - `{"error":"meter_filter is required when querying all subscriptions without cache. ..."}`
    - **Do NOT return this error if …**
      - `azure_cost_results` contains any row at all; that case uses the cache path.
      - `subscription_names` is provided.
      - `meter_filter` is provided.
  - **When** the stored live-path result for this request is an in-band failure:
    - return:
      - `{"error":"Azure billing query failed: ..."}`
    - **Do NOT return this error if …**
      - a matching stored success row exists for the request.
  - **When** blob storage would otherwise be considered unconfigured:
    - do not return `{"error":"Azure blob storage not configured"}` in this simulation.
    - **Do NOT return this error if …**
      - always; blob storage counts as configured here.

- **Empty-result contract**
  - This is a list-style/search operation.
  - **When** the selected path is a success path and no stored row matches the request's filters:
    - return a success object with:
      - `results: []`
      - `total_cost: 0`
      - any count-like values set to `0` where the stored row does so
      - no invented rows or synthesized values
  - **When** `azure_cost_results` contains rows but none match the request:
    - return the empty success result from the cache path; do **not** fall back to live.
  - **When** `azure_cost_results` contains no rows at all and the request omits both `subscription_names` and `meter_filter`:
    - return the in-band meter-filter error instead of an empty result.
  - Never generate a record, row, file, or field value not present in the store.

- **Idempotency**
  - Read-only operation.
  - Repeating the same request against unchanged stores returns the same stored result or the same in-band error.
  - No state change; no writes.

#### Derived fields

- `total_cost`
  - Sum of the returned `results[*].total_cost` values, when represented as a computed aggregate in the stored success row.
- `subscriptions_queried`
  - Summary of the subscription selection represented by the stored success row; may be a count-like string, `all`, or a serialized list form depending on path.
- `source`
  - `"cache"` when `azure_cost_results` contains any rows and the request is served from cached data; otherwise `"live"` on the live path.

### /query_aws_capacity_manager POST

- **Purpose**
  - Query AWS capacity data using one of three presets:
    - `utilization`
    - `unused_cost`
    - `inventory`
  - This is a read-only operation.
  - It must not write any store collection.

- **Caller expectations**
  - none

- **Inputs**
  - **All request fields are optional.**
  - `metric`
    - Optional.
    - Allowed documented values: `utilization`, `unused_cost`, `inventory`.
    - Default behavior when omitted: treat as `utilization`.
    - When provided with an unrecognised value: treat it as `utilization` for lookup behavior, but echo the provided value back in the response `metric` field if a stored row is returned.
  - `group_by`
    - Optional.
    - Used only when `metric` is not `inventory`.
    - Default when omitted on the metric path: `account-id`.
    - Ignored when `metric = inventory`; inventory always uses its own code path and has no `group_by` in the response.
  - `instance_type`
    - Optional filter.
  - `account_id`
    - Optional filter.
  - `reservation_state`
    - Optional filter.
    - Default behavior when omitted: `active`.
    - When provided as an empty string: treat as no reservation-state filter.
  - `hours`
    - Optional.
    - Default when omitted: `168`.
    - When greater than `2160`: cap to `2160`.
    - Used to resolve the queried window; the effective window may also be truncated to the hour, lagged by four hours behind now, and clamped to a stored `capacity_windows` row.

- **Store reads**
  - Read `capacity_windows` first to resolve the effective queried window.
    - Match by the resolved window represented by the stored `capacity_windows` row.
  - When the resolved request is on the **metric path** (`metric` treated as `utilization` or `unused_cost`):
    - Read `capacity_metric_results` by `capacity_window_id`.
    - Read `capacity_totals` by `capacity_totals_id` from the matched `capacity_metric_results` row.
    - Select the row matching the effective metric behavior and grouping:
      - metric behavior uses:
        - `utilization` when `metric` is omitted
        - `unused_cost` when `metric = unused_cost`
        - `utilization` lookup behavior when `metric` is unrecognised
      - `group_by` uses:
        - provided `group_by`, or
        - `account-id` when omitted
    - Apply request filters only by returning the stored row that matches the resolved request; do not synthesize filtered sub-results.
  - When the resolved request is on the **inventory path** (`metric = inventory`):
    - Resolve the window from `capacity_windows`.
    - Read the inventory result from the installed dataset for that window on the inventory code path.
    - Do not read or require `capacity_metric_results` or `capacity_totals` for the inventory response shape unless the stored dataset for this operation represents inventory there; never synthesize inventory rows from metric rows.
  - **Writes**
    - Do not write `capacity_windows`.
    - Do not write `capacity_metric_results`.
    - Do not write `capacity_totals`.

- **Behavior**
  - Resolve the effective query window from the request:
    - truncate to the hour,
    - lag four hours behind now,
    - cap `hours` at `2160`,
    - clamp further to the range represented by a stored `capacity_windows` row when applicable.
  - Use the installed store as authoritative.
  - Never generate or synthesize any record, row, field, or value not present in the store.
  - Return stored rows exactly as stored.
  - For optional fields:
    - when the stored row omits the field, omit it in the response;
    - when the stored row includes the field, return it unchanged.
  - Filtering of short-lived reservations:
    - Both metric and inventory paths report what they dropped.
    - On the metric path, this filtering applies **only when** `group_by` is `account-id` or `reservation-id`.
    - For other `group_by` values on the metric path, do not apply that transient-dimension filtering.
    - Because the store is authoritative, return the stored row that already reflects this behavior; do not recompute dropped rows or totals.

- **Response shape**
  - **Success: metric path**
    - Return exactly one `CapacityMetricResult` object:
      - `capacity_metric_result_id`
      - `capacity_totals_id`
      - `capacity_window_id`
      - `group_by`
      - `metric`
      - `period`
      - `results`
      - `totals`
  - **Success: inventory path**
    - Return exactly one `CapacityInventoryResult` object.
    - It shares only the `metric` key with the metric result shape.
    - It has no `period`, `group_by`, or `totals`.
    - Return the stored inventory object exactly as stored.
  - **Failure**
    - Return an in-band object:
      - `error`: string

- **Concrete JSON example**
  - Example metric-path success:
```json
{
  "capacity_metric_result_id": "cmr_001",
  "capacity_totals_id": "ct_001",
  "capacity_window_id": "cw_001",
  "group_by": "account-id",
  "metric": "utilization",
  "period": {
    "start": "2026-10-01T00:00:00Z",
    "end": "2026-10-08T00:00:00Z"
  },
  "results": [
    {
      "dimension": "123456789012",
      "hours": 168,
      "reservation_count": 4,
      "dropped_short_lived_count": 1
    }
  ],
  "totals": {
    "hours": 168,
    "reservation_count": 4,
    "dropped_short_lived_count": 1
  }
}
```

- **Derived fields**
  - `none`
  - Do not compute any response field from hashes, ranges, or invented values.
  - Only documented derivations are allowed, and only from returned rows:
    - count equal to the length of a returned list
    - sum of returned amounts
  - If the stored row already contains those values, return them unchanged rather than recomputing them.

- **Error conditions**
  - **When** the operation encounters any exception while resolving the window, reading the store-authoritative dataset, or handling the request
    - Return:
      - `{"error":"AWS Capacity Manager query failed: <exception text>"}`
    - **Do NOT return this error if …**
      - a matching stored row does not exist and the documented empty-result contract applies instead.
  - **When** a range-probe or other internal helper fails and raises an exception
    - Return:
      - `{"error":"AWS Capacity Manager query failed: <exception text>"}`
    - **Do NOT return this error if …**
      - the request simply resolves to no matching stored row; that is an empty-result case, not an exception case.

- **Empty-result contract**
  - This is a search-style operation.
  - **When** no stored row matches the resolved request on a listing/search path
    - Return the documented empty result, not an error.
  - For the metric path, the empty result is:
    - an empty list with every count at `0` for the metric result shape, using only fields that belong to that schema.
  - For the inventory path, the empty result is:
    - the documented empty inventory result for that schema, with an empty reservations list and every count at `0` if that schema includes counts.
  - **Do not** invent placeholder rows, totals, periods, or reservations to make the response look populated.
  - **Do not** convert an empty store collection into an error; an empty collection is a deliberate test condition.

- **Idempotency**
  - Read-only operation.
  - Repeating the same request against unchanged stores returns the same stored result or the same documented empty result.
  - No state changes occur.

### /query_cost_monitor POST

- **Purpose**
  - Read from `cost_monitor_results` and return the stored payload for the requested `endpoint`.
  - This operation is read-only.
  - The request's date and filter fields do **not** choose a stored row.

- **Required inputs**
  - `endpoint`
    - Required.
    - Must be one of `summary`, `breakdown`, `drilldown`, `providers`.
  - `start_date`
    - Required.
    - No local date-format validation is performed.
  - `end_date`
    - Required.
    - No local date-format validation is performed.

- **Optional inputs**
  - `providers`
    - Optional.
    - When present, it is accepted as a string.
    - It does **not** affect store selection.
  - `group_by`
    - Optional.
    - Relevant only when `endpoint = "breakdown"` for upstream forwarding semantics, but in this simulator it does **not** affect store selection.
  - `top_n`
    - Optional.
    - Default is `25` in the real implementation signature.
    - It does **not** affect store selection.
  - `drilldown_type`
    - Optional.
    - Relevant only when `endpoint = "drilldown"` for upstream forwarding semantics, but in this simulator it does **not** affect store selection.
  - `selected_key`
    - Optional.
    - Relevant only when `endpoint = "drilldown"` for upstream forwarding semantics, but in this simulator it does **not** affect store selection.

- **Caller expectations**
  - None.

- **Store reads**
  - Read `cost_monitor_results` by filtering rows where `endpoint` equals the request `endpoint`.
  - Use the matching stored row as the sole source of truth for the response.
  - Do **not** read any other collection.
  - Do **not** use `start_date`, `end_date`, `providers`, `group_by`, `top_n`, `drilldown_type`, or `selected_key` to choose a row.

- **Store writes / state changes**
  - None.
  - Do **not** write `cost_monitor_results`.

- **Response shape**
  - When a matching row exists **and** that row has `_dashboard_link`:
    - Return an object with exactly:
      - `results`: copied verbatim from the stored row's `results`
      - `_dashboard_link`: copied verbatim from the stored row's `_dashboard_link`
    - Do **not** include `endpoint`.
    - Do **not** include `cost_monitor_result_id`.
  - When a matching row exists **and** that row does **not** have `_dashboard_link`:
    - Return the bare stored `results` value itself, as a JSON array.
    - Do **not** wrap it in an object.
    - Do **not** include `endpoint`.
    - Do **not** include `cost_monitor_result_id`.
  - When no matching row exists:
    - Return an empty `results` array rather than synthesizing data.
    - For this operation's list/search behavior, that empty result is the bare JSON array `[]`.

- **Concrete response examples**
  - Example when `_dashboard_link` is present:
    ```json
    {
      "results": [
        {
          "provider": "aws",
          "total_cost": 123.45
        }
      ],
      "_dashboard_link": "https://dashboard.example/costs"
    }
    ```
  - Example when `_dashboard_link` is absent:
    ```json
    [
      {
        "provider": "aws",
        "total_cost": 123.45
      }
    ]
    ```

- **Errors**
  - When `endpoint` is not one of `summary`, `breakdown`, `drilldown`, or `providers`:
    - Return:
      ```json
      {
        "error": "Unknown endpoint: invalid. Use summary, breakdown, drilldown, or providers."
      }
      ```
    - Do NOT return this error if `endpoint` is one of the four allowed values, even when no stored row matches.
  - Do **not** return transport or upstream-service errors in this simulator from store lookup alone.
    - The store is authoritative for this operation.
    - Do NOT return `"Cannot reach cost-monitor service..."` if the only issue is that `cost_monitor_results` has no matching row.
    - Do NOT return `"cost-monitor API returned <status>: ..."` if the simulator is serving from store data.
    - Do NOT return `"cost-monitor query failed: ..."` if the request is well-formed and store lookup succeeds or yields no match.

- **Empty-result contract**
  - This is a search-style read.
  - When no row in `cost_monitor_results` has `endpoint = request.endpoint`:
    - Return the empty JSON array `[]`.
    - Do **not** synthesize summary totals, trends, counts, or dashboard URLs.
    - Do **not** return an object wrapper unless a matching stored row with `_dashboard_link` exists.
    - Do **not** treat an empty collection as backend failure.

- **Idempotency**
  - Read-only operation.
  - Repeating the same request against unchanged store contents returns the same response shape and payload.
  - No state is mutated.

#### Derived fields

- none
