---
name: parsec-icinga
description: Simulation skill for the parsec-icinga API.
---

# parsec-icinga Simulation

## Core Principles

- Impersonate the parsec-icinga API exactly as documented in the operation
  sections below. Do not invent operations, fields, or error conditions.
- All responses must match the operation's response schema precisely.

## Session State Management

State is kept in collections defined by `schema.json`. Use the `state_*` tools to
read and write entities. Do not list field names or types here — consult
`schema.json` for the authoritative shape.

Collections: comments, downtimes, hosts, services.

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
- There are no schema-declared numeric fields at the top level of `IcingaComment`, `IcingaDowntime`, `IcingaHost`, or `IcingaService`.
- Numeric values may appear inside `attrs` in stored rows, including temporal values such as `attrs.entry_time`, `attrs.start_time`, and `attrs.end_time`; the simulator must not impose synthetic ranges on them and must return stored integers unchanged.
- If a stored `IcingaDowntime` row contains both `attrs.start_time` and `attrs.end_time`, preserve the stored ordering exactly; do not reorder, clamp, or recompute either value.
- If a stored row contains numeric status fields inside `attrs` such as `attrs.state` or `attrs.downtime_depth`, preserve their stored values exactly; do not normalize or remap them.
- No cross-record numeric ordering may be invented; result ordering must not be based on computed numeric scores or timestamps.

### Derivation Rules
- `result` in the `query_icinga` response equals a JSON string serialization of the exact array of matching stored rows; the array elements themselves are not computed.
- For `get_hosts`, the returned array is derived only from stored `hosts` rows that match the honoured filters.
- For `get_services`, the returned array is derived only from stored `services` rows that match the honoured filters.
- For `get_problems`, the returned array is derived from stored `hosts` and stored `services` rows whose `attrs.state` is not OK; all request filters are ignored for this action.
- For `get_downtimes`, the returned array is derived only from stored `downtimes` rows filtered by honoured `host` and `service`; `search`, `filter_expr`, and `detailed` never affect inclusion or exclusion.
- For `get_comments`, the returned array is derived only from stored `comments` rows filtered by honoured `host` and `service`; `search`, `filter_expr`, and `detailed` never affect inclusion or exclusion.
- For `get_comments` and `get_downtimes`, a `host` filter matches rows whose `attrs.host_name` equals the requested host exactly, including both host-level rows and service-level rows on that host; `service` further narrows by exact `attrs.service_name`.
- For `get_services`, a `host` filter matches rows whose `attrs.host_name` equals the requested host exactly.
- A row in a hard non-OK state remains included in `get_problems` even if its stored `attrs.downtime_depth` is greater than zero.
- A row in a hard non-OK state remains included in `get_problems` even if it is acknowledged in stored `attrs`.
- If an honoured filter matches no stored row, the derived result array is empty.
- If a filter is ignored for the selected action, it contributes nothing to derivation and cannot reduce the result array.
- If `action` is one of `get_service`, `get_service_details`, `get_service_status`, `list_services`, or `check_service`, derive results exactly as for canonical `get_services`.
- If `action` is one of `get_host`, `get_host_details`, `get_host_status`, `list_hosts`, or `check_host`, derive results exactly as for canonical `get_hosts`.
- If `action` is one of `get_alerts`, `search_alerts`, or `list_problems`, derive results exactly as for canonical `get_problems`.
- If `action` is `list_downtimes`, derive results exactly as for canonical `get_downtimes`.
- If `action` is `list_comments`, derive results exactly as for canonical `get_comments`.
- If an alias action contains `detail`, treat it as the canonical action with `detailed` forced true; this affects only action normalization and does not compute or alter any stored field values.
- If `action` is not a canonical action and not one of the recognized aliases, the response equals `{"error": "Unknown icinga action: <action>"}`.
- No field inside any returned row is computed from `name`, `type`, `attrs`, request parameters, hashes, ranges, or timestamps; every returned field value equals the stored value verbatim.

### On-Demand Generation Rules
- No records may be generated on demand for `comments`, `downtimes`, `hosts`, or `services`.
- No numeric field values may be generated on demand, including values inside `attrs`.
- If the relevant store collection is empty, return an empty result array serialized into `result`; do not synthesize fallback rows.
- If an honoured filter identifies no stored rows, return an empty result array serialized into `result`; do not synthesize a matching row.
- Regeneration rules are therefore identity rules only: the same logical record yields identical numbers because the simulator must read and return the same stored row unchanged.
- Preserve stored row order if the backing store has one; otherwise use a deterministic stable order by `name` within the selected stored rows, without computing any numeric tie-breaker.
- Never enforce non-negativity by modification; if a stored numeric value inside `attrs` is negative, zero, or positive, return it unchanged.

## Example Scenarios

Representative user stories this simulation can satisfy with the seeded data:

1. **Check host status overview** — An operator wants to review current host states and identify any active problems from existing monitoring data. (operations: query_icinga)
2. **Inspect service health** — A support engineer wants to look up service status information for monitored services on known hosts. (operations: query_icinga)
3. **Review scheduled downtimes** — A maintenance coordinator wants to find hosts or services that already have downtime entries in the system. (operations: query_icinga)
4. **Read operator comments** — An on-call user wants to see existing comments attached to monitored objects to understand prior investigation context. (operations: query_icinga)
5. **Search combined monitoring state** — A NOC analyst wants a consolidated query across hosts, services, comments, and downtimes to assess the current environment. (operations: query_icinga)

## API Operation Simulation

### /query_icinga POST

- **Purpose**
  - Read from the Icinga simulation stores and return an in-band result object.
  - Success response shape is always:
    - `{"result": "<JSON string>"}`
  - Failure for unknown action is in-band:
    - `{"error": "Unknown icinga action: <action>"}`

- **Required inputs**
  - `action` — required.
    - When `action` is one of:
      - `get_hosts`
      - `get_services`
      - `get_problems`
      - `get_downtimes`
      - `get_comments`
      - run that canonical action.
    - When `action` is one of these aliases, normalize before dispatch:
      - `get_service`
      - `get_service_details`
      - `get_service_status`
      - `list_services`
      - `check_service`
      - → treat as `get_services`
      - `get_host`
      - `get_host_details`
      - `get_host_status`
      - `list_hosts`
      - `check_host`
      - → treat as `get_hosts`
      - `get_alerts`
      - `search_alerts`
      - `list_problems`
      - → treat as `get_problems`
      - `list_downtimes`
      - → treat as `get_downtimes`
      - `list_comments`
      - → treat as `get_comments`

- **Optional inputs**
  - `search` — optional.
    - When effective action is `get_hosts` or `get_services`, apply it as a filter.
    - When effective action is `get_problems`, `get_downtimes`, or `get_comments`, ignore it completely.
  - `host` — optional.
    - When effective action is `get_services`, filter rows where `attrs.host_name` equals `host` exactly.
    - When effective action is `get_downtimes` or `get_comments`, filter rows where `attrs.host_name` equals `host` exactly.
      - This includes both:
        - host-level rows where `attrs.service_name` is empty or absent
        - service rows on that host where `attrs.service_name` is set
    - When effective action is `get_hosts`, the description does not authorize `host` as a filter; do not apply it.
    - When effective action is `get_problems`, ignore it completely.
  - `service` — optional.
    - When effective action is `get_downtimes` or `get_comments`, filter rows where `attrs.service_name` equals `service` exactly.
    - When both `host` and `service` are provided for `get_downtimes` or `get_comments`, both filters must match.
    - For all other actions, do not apply it.
  - `filter_expr` — optional.
    - When effective action is `get_hosts` or `get_services`, apply it as a filter expression.
    - When effective action is `get_problems`, `get_downtimes`, or `get_comments`, ignore it completely.
  - `detailed` — optional, default `false`.
    - When the original alias contains `"detail"`, force `detailed = true`.
    - When effective action is `get_hosts` or `get_services`, use it to shape the returned stored rows.
    - When effective action is `get_problems`, `get_downtimes`, or `get_comments`, ignore it completely.

- **Store reads**
  - When effective action is `get_hosts`:
    - Read from `hosts`.
    - Read all rows in `hosts`, then apply honoured filters for this action.
  - When effective action is `get_services`:
    - Read from `services`.
    - Read all rows in `services`, then apply honoured filters for this action.
  - When effective action is `get_problems`:
    - Read from `hosts`.
    - Read from `services`.
    - Return stored rows from both collections whose `attrs.state` is not OK.
    - Ignore every request filter for this action.
    - Do not suppress a row because it is acknowledged.
    - Do not suppress a row because `downtime_depth` is greater than zero.
  - When effective action is `get_downtimes`:
    - Read from `downtimes`.
    - Apply only `host` and `service`.
    - Do not apply `search`, `filter_expr`, or `detailed`.
  - When effective action is `get_comments`:
    - Read from `comments`.
    - Apply only `host` and `service`.
    - Do not apply `search`, `filter_expr`, or `detailed`.

- **Filtering rules**
  - **For `get_hosts` / `get_services`**
    - Apply `search` when provided.
    - Apply `filter_expr` when provided.
    - For `get_services`, apply `host` when provided by exact equality on `attrs.host_name`.
    - For `get_hosts`, do not apply `host` or `service`.
    - For `filter_expr`, resolve variables against the stored row as follows:
      - `service.name` = short service name, i.e. the part after `!` in the row `name`
      - `host.name` = short host name, i.e. the part before `!` in the row `name` for service rows
      - `service.display_name`, `service.state`, `host.state`, and similar names resolve to the correspondingly named field under `attrs`
      - `match(pattern, value)` uses glob semantics
    - A filter that matches no stored rows returns an empty array.
  - **For `get_problems`**
    - Ignore `search`.
    - Ignore `host`.
    - Ignore `service`.
    - Ignore `filter_expr`.
    - Ignore `detailed`.
    - Return all host and service rows in non-OK state from the stores.
  - **For `get_downtimes` / `get_comments`**
    - Apply `host` only by exact equality on `attrs.host_name`.
    - Apply `service` only by exact equality on `attrs.service_name`.
    - Ignore `search`.
    - Ignore `filter_expr`.
    - Ignore `detailed`.
    - A request carrying ignored filters must return exactly the same rows as the same request without those ignored filters.

- **Writes / state changes**
  - None.
  - This operation is read-only.
  - Do not write any store collection.

- **Response shape**
  - On success:
    - Object with exactly:
      - `result`: string
    - The string value is the JSON serialization of the array of matching stored rows.
    - Each array element is a stored row returned unchanged from the store.
    - Do not compute, synthesize, or fill in fields.
    - If an optional field is absent on a stored row, it remains absent in the serialized row.
  - Concrete success example:
    ```json
    {
      "result": "[{\"name\":\"web01\",\"attrs\":{\"host_name\":\"web01\",\"state\":0}}]"
    }
    ```
  - On unknown action:
    - Object with exactly:
      - `error`: string
  - Concrete error example:
    ```json
    {
      "error": "Unknown icinga action: list_alerts"
    }
    ```

- **Error conditions**
  - When `action` is neither:
    - one of the canonical enum values, nor
    - one of the documented aliases,
    - return:
      - `{"error": "Unknown icinga action: <action>"}`
    - Do NOT return this error if `action` is an alias that normalizes to a canonical action.
  - Do not return an error merely because:
    - honoured filters match no rows
    - ignored filters are present
    - a collection is empty
  - Do not return a not-found error for empty search/list results.
    - Do NOT return this error if the request is a listing/search action and no stored rows match; return an empty serialized array instead.

- **Empty-result contract**
  - When the effective action is any of the supported read actions and no stored rows match after applying only the filters that action honours:
    - return success with:
      - `result` set to the JSON string of an empty array: `"[]"`
  - When a filter is ignored for that action:
    - it must not narrow the result
    - it must not cause an empty result on its own
  - When the underlying collection is empty:
    - return `{"result":"[]"}` for that action, unless the action is unknown.

- **Idempotency**
  - This is a read-only search operation.
  - Repeating the same request against unchanged stores returns the same response content.
  - No state is mutated.

#### Derived fields

- `result`
  - Computed as `JSON.stringify(array_of_matching_store_rows)` after action normalization and application of only the filters that the effective action honours.
