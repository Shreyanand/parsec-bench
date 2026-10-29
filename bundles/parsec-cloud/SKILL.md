---
name: parsec-cloud
description: Simulation skill for the parsec cloud tools API.
---

# parsec cloud tools Simulation

## Core Principles

- Impersonate the parsec cloud tools API exactly as documented in the operation
  sections below. Do not invent operations, fields, or error conditions.
- All responses must match the operation's response schema precisely.

## Session State Management

State is kept in collections defined by `schema.json`. Use the `state_*` tools to
read and write entities. Do not list field names or types here — consult
`schema.json` for the authoritative shape.

Collections: access_keys, azure_subscriptions, ec2_instances, events, gcp_projects, iam_users, marketplace_agreements, sandbox_accounts.

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
- `estimated_cost`: integer-like monetary value in the inclusive range 0 to 1000000.
- `estimated_cost_usd`: integer-like monetary value in the inclusive range 0 to 1000000.
- `estimated_cost` and `estimated_cost_usd` must both be non-negative.
- When both `estimated_cost` and `estimated_cost_usd` are present for the same `marketplace_agreement_id`, they must be numerically consistent and not contradict each other; if `currency` is `USD`, `estimated_cost_usd` must equal `estimated_cost` exactly.
- All computed count values returned by operations must be integers in the inclusive range 0 to 100000.
- For Azure pool summaries, `in_use <= total`, `available <= total`, and `total = in_use + available`.
- For Azure overall summaries, `in_use <= total_subscriptions`, `available <= total_subscriptions`, and `total_subscriptions = in_use + available`.
- For GCP project listings, `active <= count`, `delete_requested <= count`, and `count = active + delete_requested`.
- For AWS account inspections, `instance_count`, `event_count`, `user_count`, and `agreement_count` must each be non-negative integers.
- For sandbox account and marketplace inventory searches, `count` must be a non-negative integer.
- For CloudTrail SQL results, `row_count` and `bytes_scanned` must be non-negative integers.
- `bytes_scanned` must be 0 when `row_count` is 0.

### Derivation Rules
- `query_azure_pools` list_pools: each pool's `total` equals the number of stored `azure_subscriptions` rows whose `database` equals the effective request `database` and whose `id` matches the `pool-<pool_id>-<n>` pattern for that pool.
- `query_azure_pools` list_pools: each pool's `in_use` equals the number of those rows with `used = true`.
- `query_azure_pools` list_pools: each pool's `available` equals `total - in_use`.
- `query_azure_pools` list_pools: `summary.total_subscriptions` equals the sum of all pool `total` values.
- `query_azure_pools` list_pools: `summary.in_use` equals the sum of all pool `in_use` values.
- `query_azure_pools` list_pools: `summary.available` equals `summary.total_subscriptions - summary.in_use`.
- `query_azure_pools` list_pools: `summary.pool_count` equals the number of distinct pool ids derivable from matching `id` values in the filtered rows.
- `query_azure_pools` get_pool: `total` equals the length of `subscriptions`.
- `query_azure_pools` get_pool: `in_use` equals the number of returned `subscriptions` entries with `used = true`.
- `query_azure_pools` get_pool: `available` equals `total - in_use`.
- `query_azure_pools` search_by_project: `count` equals the length of `subscriptions`.
- `query_gcp_projects` list_projects: `count` equals the length of `projects`.
- `query_gcp_projects` list_projects: `active` equals the number of returned `projects` entries with `state = ACTIVE`.
- `query_gcp_projects` list_projects: `delete_requested` equals `count - active`.
- `query_cloudtrail`: `row_count` equals the length of `rows`.
- `query_cloudtrail`: `columns` equals the ordered SELECT-list output names after aliasing; an item aliased with AS uses its alias as the column name.
- `query_cloudtrail`: each returned row value equals the unchanged stored field value mapped from the selected SQL column: `eventTime -> event_time`, `eventName -> event_name`, `eventSource -> event_source`, `eventID -> event_id`, `recipientAccountId -> account_id`, `userIdentity.username -> username`.
- `query_cloudtrail`: `bytes_scanned` is deterministic from the matched stored `events` rows and the selected columns; it must be 0 when no rows match and otherwise a positive integer identical across repeated identical queries in the same store state.
- `query_aws_account` describe_instances: `instance_count` equals the length of `instances`.
- `query_aws_account` lookup_events: `event_count` equals the length of `events`.
- `query_aws_account` list_users: `user_count` equals the length of `users`.
- `query_aws_account` describe_marketplace: `agreement_count` equals the length of `agreements`.
- `query_aws_account`: account-id format validation is computed before any store read; `account_id` is valid iff its length is exactly 12 and every character is 0-9.
- `query_aws_account_db`: `count` equals the length of `accounts`.
- `query_marketplace_agreements`: `count` equals the length of `agreements`.
- `query_marketplace_agreements`: numeric values in `estimated_cost` and `estimated_cost_usd` are returned from stored values with Decimal-to-float conversion only; no recomputation, currency conversion, rounding, or enrichment is performed by the simulator.
- `query_marketplace_agreements`: the `min_cost` filter, when used, matches rows where `estimated_cost` is present and `estimated_cost >= min_cost`.
- `query_aws_account` describe_marketplace: `estimated_cost` and `estimated_cost_usd` are echoed exactly from stored `marketplace_agreements` rows when present; no live recomputation is performed by the simulator.

### On-Demand Generation Rules
- No entity record may be generated on demand for any operation.
- No field value may be generated on demand for any stored record.
- If a collection has no matching stored rows, return the documented empty result with computed counts set to 0.
- If a single-record lookup has no matching stored row, return the documented in-band error and do not synthesize a placeholder record.
- For `azure_subscriptions`, `gcp_projects`, `events`, `ec2_instances`, `iam_users`, `marketplace_agreements`, and `sandbox_accounts`, every echoed entity field must come directly from the stored row, unchanged except where the operation explicitly omits storage identity fields.
- Deterministic regeneration is therefore limited to computed aggregates over stored rows only: counts, pool occupancy totals, `delete_requested`, `row_count`, and `bytes_scanned`.
- Ordering of generated aggregate structures must be deterministic from stored data: repeated calls over unchanged matching rows must return identical aggregate numbers and identical row/list membership.
- All generated numeric values must satisfy non-negativity and the ordering constraints above.
- `bytes_scanned`, though computed, must be generated deterministically from the exact matched stored `events` rows and selected columns; identical query text against unchanged stored `events` must yield the same `bytes_scanned`.
- `truncated` is never inferred from a numeric range or hash; it must only reflect the operation's actual returned result shape and remain deterministic for the same request and store state.

## Example Scenarios

Representative user stories this simulation can satisfy with the seeded data:

1. **Find available sandbox account** — A platform engineer wants to search the sandbox account pool for an available account and then inspect the selected AWS account in more detail. (operations: query_aws_account_db, query_aws_account)
2. **Review Azure pool usage** — An operations user wants to check which Azure subscriptions in the pool are currently assigned or tagged to projects. (operations: query_azure_pools)
3. **Audit AWS API activity** — A security analyst wants to search CloudTrail Lake for recent AWS API events tied to a user, account, or action. (operations: query_cloudtrail)
4. **Inventory GCP projects** — A cloud administrator wants to list RHDP-created GCP projects under the managed folder to review their current state. (operations: query_gcp_projects)
5. **Check marketplace commitments** — A finance or procurement user wants to search AWS Marketplace agreements to review active products, vendors, and estimated costs. (operations: query_marketplace_agreements)

## API Operation Simulation

### /query_azure_pools POST

- **Purpose**
  - Read-only query over `azure_subscriptions`.
  - Dispatch behavior is selected by `action`.
  - This operation does **not** write any store collection.

- **Caller expectations**
  - none

- **Inputs**
  - **Required**
    - `action`
      - Must be one of:
        - `list_pools`
        - `get_pool`
        - `get_subscription`
        - `search_by_project`
  - **Optional**
    - `database`
      - Defaults to `pools` when omitted.
      - Must be one of:
        - `pools`
        - `aro`
        - `roadshow`
      - Validated before any query behavior.
    - `pool_id`
      - Required **when** `action = "get_pool"`.
      - Ignored otherwise.
    - `subscription_name`
      - Required **when** `action = "get_subscription"`.
      - Ignored otherwise.
    - `project_tag`
      - Required **when** `action = "search_by_project"`.
      - Ignored otherwise.
    - `max_results`
      - Optional for all requests.
      - Used only **when** `action = "get_pool"` or `action = "search_by_project"`.
      - Defaults to `100` when omitted.
      - If greater than `500`, clamp to `500`.
      - Ignored **when** `action = "list_pools"` or `action = "get_subscription"`.

- **Store access**
  - Read from `azure_subscriptions`.
  - First apply database scope:
    - Read only rows where stored `database` equals the effective request `database`.
    - Effective `database` is request `database` if provided, otherwise `pools`.
    - Rows with any other stored `database` value are treated as non-existent for this request.
  - Per action:
    - **When `action = "list_pools"`**
      - Read all `azure_subscriptions` rows in the effective `database`.
      - Derive pool membership from `id` matching the prefix/pattern `pool-<pool_id>-...`.
      - Rows whose `id` does not match that pool-style naming are excluded from `pools` and `summary`.
    - **When `action = "get_pool"`**
      - Read all `azure_subscriptions` rows in the effective `database` whose `id` starts with `pool-<pool_id>-`.
      - Apply `max_results` cap only to the returned `subscriptions` array.
      - Counts are over the matched rows for that pool query.
    - **When `action = "get_subscription"`**
      - Read `azure_subscriptions` in the effective `database` by exact match on `id = subscription_name`.
      - Storage primary key `azure_subscription_id` is **not** used for lookup.
    - **When `action = "search_by_project"`**
      - Read all `azure_subscriptions` rows in the effective `database` where `projecttag = project_tag`.
      - Apply `max_results` cap only to the returned `subscriptions` array.
  - **Writes**
    - None.
    - Do not write `azure_subscriptions`.

- **State changes**
  - None.

- **Response**
  - Response shape depends on `action`.

  - **When `action = "list_pools"`**
    - Return object with exactly:
      - `database`
      - `pools`
        - object keyed by pool id
        - each value exactly:
          - `total`
          - `in_use`
          - `available`
      - `summary`
        - exactly:
          - `total_subscriptions`
          - `in_use`
          - `available`
          - `pool_count`
    - Example:
      ```json
      {
        "database": "pools",
        "pools": {
          "01": {
            "total": 2,
            "in_use": 1,
            "available": 1
          },
          "02": {
            "total": 1,
            "in_use": 0,
            "available": 1
          }
        },
        "summary": {
          "total_subscriptions": 3,
          "in_use": 1,
          "available": 2,
          "pool_count": 2
        }
      }
      ```

  - **When `action = "get_pool"`**
    - Return object with exactly:
      - `database`
      - `pool_id`
      - `subscriptions`
        - array of objects, each exactly:
          - `id`
          - `used`
          - `projecttag` when present on the stored row
        - Do **not** add `azure_subscription_id`.
        - Do **not** add `database` to each subscription entry.
      - `total`
      - `in_use`
      - `available`
      - `truncated`
    - Example:
      ```json
      {
        "database": "pools",
        "pool_id": "01",
        "subscriptions": [
          {
            "id": "pool-01-273",
            "used": true,
            "projecttag": "sandbox-api"
          },
          {
            "id": "pool-01-274",
            "used": false
          }
        ],
        "total": 2,
        "in_use": 1,
        "available": 1,
        "truncated": false
      }
      ```

  - **When `action = "get_subscription"`**
    - Return object with exactly:
      - `database`
      - `subscription`
        - object exactly:
          - `id`
          - `used`
          - `projecttag` when present on the stored row
        - Do **not** add `azure_subscription_id`.
        - Do **not** add `database` inside `subscription`.
    - Example:
      ```json
      {
        "database": "pools",
        "subscription": {
          "id": "pool-01-273",
          "used": true,
          "projecttag": "sandbox-api"
        }
      }
      ```

  - **When `action = "search_by_project"`**
    - Return object with exactly:
      - `database`
      - `project_tag`
      - `subscriptions`
        - array of objects, each exactly:
          - `id`
          - `used`
          - `projecttag` when present on the stored row
        - Do **not** add `azure_subscription_id`.
        - Do **not** add `database` to each subscription entry.
      - `count`
      - `truncated`
    - Example:
      ```json
      {
        "database": "pools",
        "project_tag": "sandbox-api",
        "subscriptions": [
          {
            "id": "pool-01-273",
            "used": true,
            "projecttag": "sandbox-api"
          }
        ],
        "count": 1,
        "truncated": false
      }
      ```

  - **In-band error envelope**
    - Return object with exactly:
      - `error`
    - Example:
      ```json
      {
        "error": "Subscription 'pool-99-999' not found in pools database"
      }
      ```

- **Error conditions**
  - **When** `database` is provided and is not one of `pools`, `aro`, `roadshow`
    - Return:
      - `{"error":"Invalid database '<value>'"}`
    - Do **NOT** return this error if:
      - `database` is omitted; use default `pools` instead.
      - `database` is one of the allowed values.

  - **When** `action` is not one of the supported values
    - Return:
      - `{"error":"Unknown action '<value>'"}`
    - Do **NOT** return this error if:
      - `action` is one of `list_pools`, `get_pool`, `get_subscription`, `search_by_project`.

  - **When** `action = "get_pool"` and `pool_id` is missing
    - Return:
      - `{"error":"pool_id is required for get_pool"}`
    - Do **NOT** return this error if:
      - `action` is not `get_pool`.
      - `pool_id` is present.

  - **When** `action = "get_subscription"` and `subscription_name` is missing
    - Return:
      - `{"error":"subscription_name is required for get_subscription"}`
    - Do **NOT** return this error if:
      - `action` is not `get_subscription`.
      - `subscription_name` is present.

  - **When** `action = "search_by_project"` and `project_tag` is missing
    - Return:
      - `{"error":"project_tag is required for search_by_project"}`
    - Do **NOT** return this error if:
      - `action` is not `search_by_project`.
      - `project_tag` is present.

  - **When** `action = "get_subscription"` and no `azure_subscriptions` row in the effective `database` has `id = subscription_name`
    - Return:
      - `{"error":"Subscription '<subscription_name>' not found in <database> database"}`
    - Do **NOT** return this error if:
      - A row exists in `azure_subscriptions` with matching `id` in the effective `database`.
      - A row exists only in a different `database`; that row is out of scope for this request and still counts as not found in the effective `database`.

  - **When** the underlying helper reports Cosmos is not configured
    - Return:
      - `{"error":"Azure Cosmos not configured"}`
    - Do **NOT** return this error if:
      - The installed store is available, including when the matching dataset is empty.

  - **When** any other caught exception occurs after dispatch begins
    - Return:
      - `{"error":"Azure pools query failed: <exception text>"}`
    - Do **NOT** return this error if:
      - The condition matches one of the explicit in-band validation or not-found cases above.

- **Empty-result contract**
  - **For `list_pools`**
    - When no rows in the effective `database` have pool-style `id` values:
      - Return:
        - `database` = effective database
        - `pools` = `{}`
        - `summary.total_subscriptions` = `0`
        - `summary.in_use` = `0`
        - `summary.available` = `0`
        - `summary.pool_count` = `0`
    - Do not return an error for an empty listing.

  - **For `get_pool`**
    - When no rows in the effective `database` match `id` prefix `pool-<pool_id>-`:
      - Return:
        - `database` = effective database
        - `pool_id` = requested `pool_id`
        - `subscriptions` = `[]`
        - `total` = `0`
        - `in_use` = `0`
        - `available` = `0`
        - `truncated` = `false`
    - Do not return a not-found error for an empty pool listing.

  - **For `search_by_project`**
    - When no rows in the effective `database` have `projecttag = project_tag`:
      - Return:
        - `database` = effective database
        - `project_tag` = requested `project_tag`
        - `subscriptions` = `[]`
        - `count` = `0`
        - `truncated` = `false`
    - Do not return an error for an empty search result.

  - **For `get_subscription`**
    - Empty result is **not** returned as an empty object or null.
    - Return the in-band not-found error envelope instead.

- **Idempotency**
  - Read-only operation.
  - Repeating the same request against unchanged `azure_subscriptions` returns the same result.
  - No writes, no side effects.

#### Derived fields

- `database`
  - Effective request `database`: request `database` if provided, otherwise `"pools"`.
- `pools`
  - Group effective-database rows by pool id parsed from `id` values matching `pool-<pool_id>-...`; exclude non-matching rows.
- `pools.<pool_id>.total`
  - Count of matched rows in that pool.
- `pools.<pool_id>.in_use`
  - Count of matched rows in that pool where `used` is `true`.
- `pools.<pool_id>.available`
  - `total - in_use` for that pool.
- `summary.total_subscriptions`
  - Sum of `total` across all returned pools.
- `summary.in_use`
  - Sum of `in_use` across all returned pools.
- `summary.available`
  - `summary.total_subscriptions - summary.in_use`.
- `summary.pool_count`
  - Number of keys in `pools`.
- `total`
  - For `get_pool`, count of all matched rows for the requested pool before truncating the returned `subscriptions` array.
- `in_use`
  - For `get_pool`, count of matched rows where `used` is `true`.
- `available`
  - For `get_pool`, `total - in_use`.
- `truncated`
  - For `get_pool` and `search_by_project`, `true` when matched row count exceeds effective `max_results`, else `false`.
- `count`
  - For `search_by_project`, count of returned `subscriptions` entries.

### /query_gcp_projects POST

- **Purpose**
  - Run one of two read-only queries against `gcp_projects`, selected by `action`:
    - `list_projects`: return a list result with `folder_id`, `projects`, and counts.
    - `get_project`: return one project's detail at the top level.
- **Store authority**
  - Read only `gcp_projects`.
  - Do not write any collection.
  - Do not read any other collection.
  - Do not generate or synthesise records or field values not present in `gcp_projects`, except the documented derived counts and fallback `folder_id`.

- **Inputs**
  - **Required**
    - `action`
      - Must be one of:
        - `list_projects`
        - `get_project`
  - **Optional**
    - `project_id`
      - Required **when** `action = "get_project"`.
      - Ignored **when** `action = "list_projects"`.
    - `state_filter`
      - Optional **when** `action = "list_projects"`.
      - Ignored **when** `action = "get_project"`.
      - Comparison is case-insensitive against stored `state`; values outside the declared enum are not rejected and simply match no rows.
    - `max_results`
      - Optional **when** `action = "list_projects"`.
      - Ignored **when** `action = "get_project"`.
      - Default is `100` when omitted.
      - Clamp to `500` **when** provided value is greater than `500`.
      - If `max_results` cannot be compared to an integer, the operation may raise out instead of returning the in-band error shape.

- **Caller expectations**
  - none

- **Store reads / state changes**
  - **When `action = "list_projects"`**
    - Read `gcp_projects` as the complete dataset.
    - Filter rows:
      - include all rows **when** `state_filter` is omitted.
      - include only rows whose stored `state` equals `state_filter` case-insensitively **when** `state_filter` is provided.
    - Apply `max_results` after defaulting/clamping.
    - Return only stored row fields projected as:
      - `project_id`
      - `name`
      - `state`
      - `create_time`
      - `labels`
    - Compute counts from the returned/stored rows for this listing result only:
      - `count`
      - `active`
      - `delete_requested`
      - `truncated`
    - Set `folder_id` to the configured folder id, and if unconfigured fall back to the hard-coded default id; it is never empty.
  - **When `action = "get_project"`**
    - Read `gcp_projects` and find one row where `project_id = request.project_id`.
    - Return that row projected as:
      - `project_id`
      - `name`
      - `state`
      - `create_time`
      - `labels`
      - `parent`
    - Do not return `gcp_project_id`.
  - **Writes**
    - None; this operation is read-only and idempotent.

- **Response shape**
  - **When `action = "list_projects"` and request is successful**
    - Return an object with:
      - `folder_id`: string
      - `projects`: array of objects, each with:
        - `project_id`
        - `name`
        - `state`
        - `create_time`
        - `labels`
      - `count`: integer
      - `active`: integer
      - `delete_requested`: integer
      - `truncated`: boolean
  - **Concrete example**
    ```json
    {
      "folder_id": "123456789012",
      "projects": [
        {
          "project_id": "cluster-4d99p",
          "name": "Demo Cluster",
          "state": "ACTIVE",
          "create_time": "2024-05-01T12:34:56Z",
          "labels": {
            "env": "demo"
          }
        }
      ],
      "count": 1,
      "active": 1,
      "delete_requested": 0,
      "truncated": false
    }
    ```
  - **When `action = "get_project"` and a matching row exists**
    - Return an object with:
      - `project_id`
      - `name`
      - `state`
      - `create_time`
      - `labels`
      - `parent`
  - **Concrete example**
    ```json
    {
      "project_id": "cluster-4d99p",
      "name": "Demo Cluster",
      "state": "ACTIVE",
      "create_time": "2024-05-01T12:34:56Z",
      "labels": {
        "env": "demo"
      },
      "parent": "folders/123456789012"
    }
    ```
  - **When an in-band error is returned**
    - Return exactly:
      - `error`: string
  - **Concrete example**
    ```json
    {
      "error": "project_id is required (e.g. 'cluster-4d99p')"
    }
    ```

- **Derived fields**
  - `folder_id`: configured folder id, or the hard-coded default id when unconfigured.
  - `count`: number of elements in `projects`.
  - `active`: number of returned `projects` whose `state` is `ACTIVE`.
  - `delete_requested`: `count - active`; this includes every non-`ACTIVE` state, not only `DELETE_REQUESTED`.
  - `truncated`: `true` when more matching stored rows exist than were returned because of `max_results`; otherwise `false`.

- **Error conditions**
  - **When** `action = "get_project"` and `project_id` is missing
    - Return:
      ```json
      {
        "error": "project_id is required (e.g. 'cluster-4d99p')"
      }
      ```
    - **Do NOT return this error if** `action = "list_projects"`; `project_id` is ignored there.
  - **When** `action` is not recognised
    - Return:
      ```json
      {
        "error": "Unknown action <action>"
      }
      ```
    - **Do NOT return this error if** `action` is `list_projects` or `get_project`.
  - **When** `action = "get_project"` and no row in `gcp_projects` has `project_id = request.project_id`
    - Return an in-band not-found envelope:
      ```json
      {
        "error": "Project 'cluster-4d99p' not found: ..."
      }
      ```
    - **Do NOT return this error if** `action = "list_projects"`; no-match listing returns the empty list result instead.
  - **When** an internal exception occurs inside the query handling path
    - Return:
      ```json
      {
        "error": "GCP projects query failed: ..."
      }
      ```
    - **Do NOT return this error if** the condition is one of the explicit in-band cases above (`project_id` missing, unknown `action`, or named project not found), which have their own error envelopes.
  - **When** `max_results` cannot be compared to an integer during clamping
    - The operation may raise out instead of returning the in-band error envelope.
    - **Do NOT return this error if** `max_results` is omitted or is a comparable integer value.

- **Empty-result contract**
  - **When** `action = "list_projects"` and no stored row matches, including when `gcp_projects` is empty
    - Return:
      - `projects: []`
      - `count: 0`
      - `active: 0`
      - `delete_requested: 0`
      - `truncated: false`
      - `folder_id`: still present and non-empty via configured value or hard-coded default
    - Example:
      ```json
      {
        "folder_id": "123456789012",
        "projects": [],
        "count": 0,
        "active": 0,
        "delete_requested": 0,
        "truncated": false
      }
      ```
  - **When** `action = "list_projects"` and `state_filter` is provided but matches no stored `state`
    - Return the same empty list result; do not reject the filter value solely because it is outside the declared enum.
  - **When** `action = "get_project"` and no stored row matches `project_id`
    - Return the in-band not-found error object, not an empty object and not a synthesised record.

- **Idempotency**
  - This is a read-only operation.
  - Repeating the same request against unchanged `gcp_projects` returns the same result shape and values, aside from any exception text in failure cases.

### /query_cloudtrail POST

- **Purpose**
  - Run one SQL `SELECT` query against stored `events`.
  - Read-only operation: **do not write any store collection**.

- **Inputs**
  - **Required**
    - `query` (`string`)
      - Must be a SQL `SELECT` statement.
      - The caller writes `FROM cloudtrail_events`; the operation substitutes the configured CloudTrail Lake data store id before execution.
      - When the SQL contains `eventTime` comparisons:
        - rewrite those timestamp literals to `YYYY-MM-DD HH:MM:SS`
        - inject a derived `calendarday` partition predicate
      - When `requestParameters` or `responseElements` is used with `LIKE`:
        - wrap that expression in `CAST(CAST(... AS JSON) AS varchar)`
  - **Optional**
    - `max_results` (`integer`)
      - Default: `100`
      - When provided and greater than `500`, silently clamp to `500`.
      - When omitted, use `100`.

- **Caller expectations**
  - The caller should usually include an `eventTime` comparison in the SQL; without one, the backend is likely to reject the query.
  - This is not a simulator-side validation rule unless one of the explicit error conditions below applies.

- **Store access**
  - Read only `events`.
  - Read `events` as the complete authoritative dataset for this operation.
  - Evaluate SQL filtering and ordering against stored fields using this column-to-field mapping:
    - `eventTime` -> `event_time`
    - `eventName` -> `event_name`
    - `eventSource` -> `event_source`
    - `eventID` -> `event_id`
    - `recipientAccountId` -> `account_id`
    - `userIdentity.username` -> `username`
  - For each matching stored row:
    - selected column values come from the mapped stored field, unchanged
    - if a SELECT item uses `AS`, use the alias as the output column name and row key
  - **Do not read any collection other than `events`.**
  - **Do not generate or synthesize rows or field values not present in stored `events`.**

- **State changes**
  - None.
  - **Do not write `events` or any other collection.**

- **Response**
  - Success response is one of:
    - **Matching rows found**
      - Object with:
        - `columns`: array of selected column names, in query result order
        - `rows`: array of objects keyed by those same column names
        - `row_count`: number of returned rows
        - `bytes_scanned`: numeric service-reported/scalar result field
        - `truncated`: boolean
    - **No matching rows**
      - Object with:
        - `columns`: `[]`
        - `rows`: `[]`
        - `row_count`: `0`
        - `bytes_scanned`: `0`
      - Do **not** include `truncated` in this empty-result case.
    - **In-band error**
      - Object with:
        - `error`: string

- **Concrete success example**
  ```json
  {
    "columns": ["eventTime", "eventName", "user"],
    "rows": [
      {
        "eventTime": "2026-08-11T07:42:19Z",
        "eventName": "CreateUser",
        "user": "alice"
      }
    ],
    "row_count": 1,
    "bytes_scanned": 4096,
    "truncated": false
  }
  ```

- **Error conditions**
  - When `query`, after stripping whitespace and a leading `(`, is not a `SELECT` statement:
    - return:
      ```json
      { "error": "Only SELECT queries are allowed against CloudTrail Lake" }
      ```
    - Do NOT return this error if the statement is a `SELECT`, even if it later fails for another reason.
  - When the CloudTrail event data store id is not configured:
    - return:
      ```json
      { "error": "CloudTrail event data store ID not configured" }
      ```
    - Do NOT return this error if the data store id is configured, even when the query matches no stored rows.
  - When the backend reports query status `FAILED`, `CANCELLED`, or `TIMED_OUT`:
    - return:
      ```json
      { "error": "CloudTrail Lake query <status>: <message>" }
      ```
    - Do NOT return this error if the query instead exhausts the local 300s polling budget; that case uses the timeout message below.
  - When polling exceeds the 300s budget:
    - return:
      ```json
      { "error": "CloudTrail Lake query timed out after 300s. Try narrowing the eventTime range to reduce data scanned." }
      ```
    - Do NOT return this error if the query completed within the polling budget, even with zero rows.
  - When any other exception occurs during setup or execution:
    - return:
      ```json
      { "error": "CloudTrail Lake query failed: <exception text>" }
      ```
    - Do NOT return this error if a more specific in-band error above applies.

- **Empty-result contract**
  - When no stored row in `events` matches the rewritten/evaluated query:
    - return exactly:
      - `columns: []`
      - `rows: []`
      - `row_count: 0`
      - `bytes_scanned: 0`
    - omit `truncated`
  - Do **not** return an error merely because no rows matched, unless the request is effectively a lookup for one named record and the implementation explicitly chooses an in-band not-found error; otherwise this search operation uses the documented empty result.
  - Do **not** invent plausible rows for an empty `events` collection; an empty collection is a valid deliberate test condition.

- **Idempotency**
  - Read-only search operation.
  - Repeating the same request against unchanged `events` should return the same rows and counts, subject only to row ordering implied by the SQL and any backend-reported `bytes_scanned`/`truncated` values.

#### Derived fields

- `row_count`
  - Equal to `rows.length`.
- `columns`
  - Derived from the query `SELECT` list after alias resolution; each item named by its `AS` alias if present, otherwise by the selected column expression's result name.
- `bytes_scanned`
  - Scalar returned for the executed query; for the documented empty-result contract, return `0`.
- `truncated`
  - Indicates whether the returned rows were cut off by result limits/pagination handling; omit entirely on the documented empty-result response.

### /query_aws_account POST

- **Purpose**
  - Read-only inspection of one AWS member account.
  - Dispatches by `action` to exactly one backing collection:
    - `describe_instances` → `ec2_instances`
    - `lookup_events` → `events`
    - `list_users` → `iam_users`
    - `describe_marketplace` → `marketplace_agreements`
  - `sandbox_accounts` is used only for role-assumption diagnostics and does not answer any action directly.

- **Inputs**
  - **Required**
    - `account_id` (`string`)
      - Must be exactly 12 characters.
      - Every character must be `0-9`.
      - Format check happens **before reading any collection**.
    - `action` (`string`)
      - Expected values:
        - `describe_instances`
        - `lookup_events`
        - `list_users`
        - `describe_marketplace`
  - **Optional**
    - `region` (`string`)
      - Default: `us-east-1`
      - Used for:
        - `describe_instances`
        - `lookup_events`
        - `list_users`
      - Ignored for store selection for `describe_marketplace`; that action is pinned to `us-east-1` behaviorally, but the response still carries the request/defaulted `region`.
    - `filters` (`object`)
      - Free-form object.
      - Unrecognized keys are ignored.
      - Known keys by action:
        - **When `action = "describe_instances"`**
          - `filters.state` optional
          - `filters.instance_ids` optional
        - **When `action = "lookup_events"`**
          - `filters.event_name` optional
        - **When `action = "describe_marketplace"`**
          - `filters.agreement_ids` optional
        - **When `action = "list_users"`**
          - No `filters` keys are used.

- **Caller expectations**
  - None stated for caller-visible conversation or confirmation.

- **Store reads / writes**
  - **Writes**
    - None. This operation is read-only.
  - **Reads**
    - **First, before any store read**
      - Validate `account_id` format character-by-character.
      - If invalid, return the invalid-account-id error immediately and read no collection.
    - **Role-assumption diagnostics only**
      - Read `sandbox_accounts` by matching `account_id` when role assumption fails and diagnostic fields are needed.
      - Use:
        - `account_id` from `sandbox_accounts.account_id`
        - `account_name` from `sandbox_accounts.name` when present; otherwise `""` in the response field
        - `account_status` from sandbox account state only as the diagnostic value required by the operation contract
      - Do not use `sandbox_accounts` to populate successful action payloads.
    - **When `action = "describe_instances"`**
      - Read `ec2_instances` where:
        - `account_id` = request `account_id`
        - `region` = request/defaulted `region`
      - Return matching stored rows as `instances`.
      - If `filters.state` is present, apply it as an additional filter on the stored rows for instance state.
      - If `filters.instance_ids` is present, apply it as an additional filter on the stored rows for instance ids.
    - **When `action = "lookup_events"`**
      - Read `events` where:
        - `account_id` = request `account_id`
      - Return matching stored rows as `events`.
      - If `filters.event_name` is present, apply it as an additional filter on the stored rows for event name.
    - **When `action = "list_users"`**
      - Read `iam_users` where:
        - `account_id` = request `account_id`
      - Return matching stored rows as `users`.
    - **When `action = "describe_marketplace"`**
      - Read `marketplace_agreements` where:
        - `account_id` = request `account_id`
      - Return matching stored rows as `agreements`.
      - If `filters.agreement_ids` is present, restrict to those agreement ids.

- **Behavior**
  - On every success payload and on every in-band dispatcher error **except** the two explicitly excluded error paths below, include:
    - `account_id`
    - `action`
    - `region`
  - Return each matched row **exactly as stored**, with every field the row schema declares and no synthesized fields.
  - Do not summarize rows down to partial objects.
  - Do not generate records or fill empty results with plausible data.
  - Optional fields present on a stored row are returned unchanged.
  - Optional fields absent from a stored row are omitted.

- **Response shape**
  - **Success envelope + per-action payload**
    - Common envelope fields:
      - `account_id`
      - `action`
      - `region`
    - Plus exactly one of:
      - **`describe_instances`**
        - `instance_count` (`integer`)
        - `instances` (`array`)
      - **`lookup_events`**
        - `event_count` (`integer`)
        - `events` (`array`)
      - **`list_users`**
        - `user_count` (`integer`)
        - `users` (`array`)
      - **`describe_marketplace`**
        - `agreement_count` (`integer`)
        - `agreements` (`array`)
    - Counts equal the length of the returned list.
  - **Role-assumption failure**
    - `account_id`
    - `action`
    - `region`
    - `account_status`
    - `account_name`
    - `error`
  - **Other in-band errors**
    - Either:
      - `{ "error": "Invalid AWS account ID: <x>. Must be 12 digits." }`
    - Or:
      - `account_id`
      - `action`
      - `region`
      - `error`

- **Concrete JSON example**
  ```json
  {
    "account_id": "123456789012",
    "action": "list_users",
    "region": "us-east-1",
    "user_count": 2,
    "users": [
      {
        "user_name": "alice",
        "account_id": "123456789012",
        "access_keys": [
          {
            "access_key_id": "AKIAEXAMPLE1",
            "status": "Active"
          }
        ]
      },
      {
        "user_name": "bob",
        "account_id": "123456789012",
        "access_keys": []
      }
    ]
  }
  ```

- **Errors**
  - **When `account_id` is not exactly 12 characters long, or any character is not `0-9`**
    - Return:
      - `{"error":"Invalid AWS account ID: <account_id>. Must be 12 digits."}`
    - Do **not** include `account_id`, `action`, or `region`.
    - Do NOT return this error if the id is exactly 12 digits and all characters are `0-9`.
  - **When `action` is not one of the supported values and account-id format passed and role assumption reached dispatcher**
    - Return in-band error with:
      - `account_id`
      - `action`
      - `region`
      - `error`
    - Error text: `Unknown action: <x>. Valid: [...]`
    - Do NOT return this error if `action` is one of:
      - `describe_instances`
      - `lookup_events`
      - `list_users`
      - `describe_marketplace`
  - **When the role cannot be assumed because the account is suspended/closed**
    - Return in-band error with:
      - `account_id`
      - `action`
      - `region`
      - `account_status`
      - `account_name`
      - `error`
    - Do NOT return this error if role assumption succeeds.
  - **When the role cannot be assumed for a non-suspension reason**
    - Return in-band error with:
      - `account_id`
      - `action`
      - `region`
      - `account_status`
      - `account_name`
      - `error`
    - Error indicates the account may not have `OrganizationAccountAccessRole` or may not be in the organization.
    - Do NOT return this error if role assumption succeeds.
  - **When `describe_marketplace` hits SearchAgreements access denial / forbidden**
    - Return in-band error with:
      - `account_id`
      - `action`
      - `region`
      - `error`
    - Do NOT return this error if marketplace access succeeds, including when the result is empty.
  - **When an outer exception handler catches any other failure**
    - Return:
      - `{"error":"AWS account query failed: ..."}`
      - or the implementation's in-band outer-failure shape if envelope assignment already occurred before the exception site
    - This is one of the two error paths that may lack `account_id`, `action`, and `region`.
    - Do NOT return this error if the operation completes one of the documented success or in-band error paths.
  - **Do not treat these as errors**
    - When no stored rows match a list/search action after a valid 12-digit `account_id`, return the documented empty success result, not an error.
    - When `describe_marketplace` yields the documented validation-empty condition, return successful empty results with its note behavior, not an error.
    - When per-agreement enrichment fails, keep the call successful and place the failure as an entry inside `agreements`; do not fail the whole operation.

- **Empty-result contract**
  - Applies only after `account_id` passes the 12-digit format check.
  - **When `action = "describe_instances"` and no `ec2_instances` rows match**
    - Return success with:
      - `account_id`
      - `action`
      - `region`
      - `instance_count: 0`
      - `instances: []`
  - **When `action = "lookup_events"` and no `events` rows match**
    - Return success with:
      - `account_id`
      - `action`
      - `region`
      - `event_count: 0`
      - `events: []`
  - **When `action = "list_users"` and no `iam_users` rows match**
    - Return success with:
      - `account_id`
      - `action`
      - `region`
      - `user_count: 0`
      - `users: []`
  - **When `action = "describe_marketplace"` and no `marketplace_agreements` rows match**
    - Return success with:
      - `account_id`
      - `action`
      - `region`
      - `agreement_count: 0`
      - `agreements: []`
  - Never return an empty list for an invalid 11-digit or 13-digit `account_id`, including one that matches a stored id after dropping a leading zero.

- **Idempotency**
  - Read-only operation.
  - Repeating the same request against unchanged stores returns the same payload shape and the same stored rows.
  - No state is created, updated, or deleted.

#### Derived fields
- `instance_count` = length of `instances`
- `event_count` = length of `events`
- `user_count` = length of `users`
- `agreement_count` = length of `agreements`
- `account_id` = copied from request onto the dispatched result, except for the invalid-account-id error and outer exception path that occur before/around that assignment
- `action` = copied from request onto the dispatched result, except for the invalid-account-id error and outer exception path that occur before/around that assignment
- `region` = request `region` if provided, otherwise default `us-east-1`; copied onto the dispatched result even for `describe_marketplace`

### /query_aws_account_db POST

- **Purpose**
  - Query `sandbox_accounts` for sandbox account metadata.
  - Read-only operation; it never writes any store collection.

- **Inputs**
  - **Required inputs**
    - none
  - **Optional inputs**
    - `name`
      - When provided, perform a `name` lookup and **ignore** `account_id`, `available`, `owner`, `zone`, `envtype`, `reservation`, and `max_results`.
    - `account_id`
      - When `name` is not provided, apply as an exact-match filter.
    - `available`
      - When `name` is not provided, apply as an exact-match filter.
      - `false` is a real filter value; do not treat it as omitted.
    - `owner`
      - When `name` is not provided, apply as a case-insensitive substring filter.
      - Match against `owner`; when a row's `owner` is empty, fall back to `owner_email`.
    - `zone`
      - When `name` is not provided, apply as a case-insensitive substring filter against `zone`.
    - `envtype`
      - When `name` is not provided, apply as a case-insensitive substring filter against `envtype`.
    - `reservation`
      - When `name` is not provided, apply as a case-insensitive substring filter against `reservation`.
    - `max_results`
      - When `name` is not provided, cap the number of returned rows.
      - Silently clamp values above `500` down to `500`.
      - When omitted, use `100`.
      - Ignored when `name` is provided.

- **Store access**
  - Read only `sandbox_accounts`.
  - **When `name` is provided**
    - Read `sandbox_accounts` by `name`.
    - Return at most the matching stored row(s) for that exact `name`, without applying any other request parameter.
  - **When `name` is not provided**
    - Read `sandbox_accounts` as a collection scan.
    - Apply exact-match filters from request:
      - `account_id` equals request `account_id`, when provided.
      - `available` equals request `available`, when provided.
    - Apply client-side case-insensitive substring filters after reading rows:
      - `owner` against row `owner`, falling back to row `owner_email` when `owner` is empty.
      - `zone` against row `zone`.
      - `envtype` against row `envtype`.
      - `reservation` against row `reservation`.
    - Limit returned rows to effective `max_results`.
  - **Projection of each returned row**
    - Return each matched stored row as an open object containing the stored fields exactly as stored, **except** omit `sandbox_account_id`.
    - Do not generate or derive any row field not present in the stored row.
    - If an optional stored field is absent, omit it from that row in the response.

- **State changes**
  - none
  - Must not write any fields in `sandbox_accounts`.

- **Response**
  - **Success shape**
    - Object with exactly:
      - `accounts`: array of matched rows, each row equal to the stored `sandbox_accounts` item minus `sandbox_account_id`
      - `count`: integer equal to `accounts.length`
      - `truncated`: boolean indicating whether more matching rows existed beyond the returned `accounts` limit
  - **Concrete success example**
    ```json
    {
      "accounts": [
        {
          "account_id": "123456789012",
          "available": true,
          "name": "sandbox4440",
          "owner": "alice",
          "owner_email": "alice@example.com",
          "envtype": "ocp4-cluster",
          "reservation": "event",
          "zone": "dev.example.com",
          "comment": "ready",
          "conan_status": "clean",
          "guid": "9d7d2d8e-1111-2222-3333-444444444444",
          "hosted_zone_id": "Z123EXAMPLE",
          "service_uuid": "svc-123",
          "annotations": {
            "team": "platform"
          }
        }
      ],
      "count": 1,
      "truncated": false
    }
    ```
  - **In-band error shape**
    - Object with exactly:
      - `error`: string
  - **Concrete error example**
    ```json
    {
      "error": "AWS accounts query failed: backend unavailable"
    }
    ```

- **Derived fields**
  - `count`: `len(accounts)`
  - `truncated`: `true` when more matched rows exist than were returned after applying the effective limit; otherwise `false`

- **Error conditions**
  - When an internal exception occurs while processing the query, return:
    - `{"error":"AWS accounts query failed: <exception text>"}`
    - Do NOT return this error if no stored row matches the request; that is a successful empty result.
  - When `name` does not match any stored row, do **not** error.
    - Do NOT return this error if the collection is empty; that is also a successful empty result.

- **Empty-result contract**
  - This is a list/search-style operation.
  - When no stored row matches, return success with:
    - `accounts: []`
    - `count: 0`
    - `truncated: false`
  - This applies both:
    - when `name` is provided and no row has that `name`
    - when scanning/filtering yields no matches
  - Do not synthesize placeholder rows or fields.

- **Idempotency**
  - Read-only and idempotent.
  - Repeating the same request against unchanged `sandbox_accounts` returns the same result shape and same stored row content.

### /query_marketplace_agreements POST

- **Purpose**
  - Query stored `marketplace_agreements` inventory only.
  - Do **not** read any collection other than `marketplace_agreements`.
  - Do **not** call live AWS APIs.
  - Do **not** generate or synthesize agreements or fields not present in the store.

- **Inputs**
  - **Required inputs**
    - none
  - **Optional inputs**
    - `account_id`
      - When supplied, use it to switch the access path from a table scan to a query on the `account_id` GSI.
    - `account_name`
      - When supplied, apply a case-insensitive substring match client-side after reading matching stored rows.
    - `status`
      - When supplied, apply exact case-sensitive equality as a server-side/store-side filter.
    - `classification`
      - When supplied, apply exact equality as a server-side/store-side filter.
    - `min_cost`
      - When supplied, apply an inclusive `>=` filter against stored `estimated_cost`.
      - `0` is a real filter value and must not be treated as absent.
    - `product_name`
      - When supplied, apply a case-insensitive substring match client-side after reading matching stored rows.
    - `vendor_name`
      - When supplied, apply a case-insensitive substring match client-side after reading matching stored rows.
    - `max_results`
      - When supplied, cap the returned `agreements` array length.
      - When omitted, use `100`.
      - When greater than `500`, clamp to `500`.
      - This cap applies only to the returned array, not to how much of the store is read to satisfy filtering.

- **Store access**
  - Read only `marketplace_agreements`.
  - Access path:
    - When `account_id` is supplied:
      - read `marketplace_agreements` by the `account_id` GSI, then apply any additional filters.
    - When `account_id` is not supplied:
      - scan `marketplace_agreements`, then apply filters.
  - Filtering order/behavior:
    - Apply store-side/server-side filters for:
      - `status == <status>`
      - `classification == <classification>`
      - `estimated_cost >= <min_cost>`
    - Apply client-side case-insensitive substring filters for:
      - `account_name`
      - `product_name`
      - `vendor_name`
  - Response row projection:
    - For each returned stored row, include every stored field **except**:
      - `marketplace_agreement_id`
      - `pk`
      - `error`
      - `term_types`
    - If an optional field is absent on the stored row, omit it from that agreement object.
    - Convert DynamoDB Decimal values to JSON numbers/floats throughout the returned agreement objects.

- **Writes / state changes**
  - none
  - This operation is read-only.

- **Response**
  - Success body keys are exactly:
    - `agreements`
    - `count`
    - `truncated`
  - Success shape:
    - `agreements`: array of projected stored rows after filtering and max-results cap
    - `count`: integer equal to `agreements.length`
    - `truncated`: boolean indicating whether more matching rows existed than were returned because of the `max_results` cap
  - Concrete success example:
    ```json
    {
      "agreements": [
        {
          "account_id": "123456789012",
          "account_name": "prod-shared",
          "agreement_end": "2026-01-31T00:00:00Z",
          "agreement_id": "agr-abc123",
          "agreement_start": "2025-02-01T00:00:00Z",
          "auto_renew": true,
          "classification": "SaaS (Auto-Renew)",
          "currency": "USD",
          "estimated_cost": 1499.99,
          "estimated_cost_usd": 1499.99,
          "last_updated": "2026-01-15T12:34:56Z",
          "offer_type": "PrivateOffer",
          "product_id": "prod-xyz789",
          "product_name": "Acme Security Suite",
          "status": "ACTIVE",
          "terms": [
            {
              "type": "Usage"
            }
          ],
          "vendor_name": "Acme Corp"
        }
      ],
      "count": 1,
      "truncated": false
    }
    ```
  - Error shape:
    - In-band error object, not an HTTP error envelope:
      - `error`: string
  - Concrete error example:
    ```json
    {
      "error": "Marketplace agreements query failed: simulated backend failure"
    }
    ```

- **Error conditions**
  - When reading or filtering `marketplace_agreements` raises any exception, return:
    - `{"error":"Marketplace agreements query failed: <exception text>"}`
    - Do **NOT** return this error if the filters simply match no stored rows; that is a successful empty result.
  - When `max_results` is greater than `500`, do **not** return an error; clamp it to `500`.
    - Do **NOT** return this error if the request is otherwise well-formed, because this operation clamps rather than rejects.
  - When `status`, `classification`, `account_name`, `product_name`, `vendor_name`, `account_id`, or `min_cost` do not match any stored row, do **not** return an error.
    - Do **NOT** return this error if the store is empty; an empty store is a deliberate valid condition for this operation.

- **Empty-result contract**
  - When no stored row matches the request filters, return success with:
    - `agreements: []`
    - `count: 0`
    - `truncated: false`
  - Example:
    ```json
    {
      "agreements": [],
      "count": 0,
      "truncated": false
    }
    ```

- **Idempotency**
  - This read-only search operation is idempotent.
  - Repeating the same request against unchanged `marketplace_agreements` returns the same filtered result shape, subject only to store contents.

- **Caller expectations**
  - none

- **Derived fields**
  - `count` — equals the length of `agreements`.
  - `truncated` — `true` when the number of matching stored rows exceeds the returned `agreements` length because of the effective `max_results` cap; otherwise `false`.
