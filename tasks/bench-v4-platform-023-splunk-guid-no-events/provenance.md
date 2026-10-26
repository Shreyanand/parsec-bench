# bench-v4-platform-023-splunk-guid-no-events

## What it measures

Whether the agent treats silence as evidence. The search legitimately returns nothing, and
the correct answer separates what that establishes (no ERROR-level entries for this GUID in
this window) from what it does not (anything about the cause).

`inferred-from-silence` is where the discrimination sits, and two of its forms are the
tempting ones rather than the obvious ones: `never started` and `was never provisioned` are
what an agent reaches for when an error search comes back empty, because absence of error
logs *feels* like evidence the thing never ran. It is not.

## The store is populated, deliberately

Two `splunk_aap2_log_entries` rows are seeded for a **different** GUID. That matters: the
empty result has to be "no entries for this GUID", not "Splunk returned nothing at all",
which an agent could reasonably read as the tool being broken. The seed makes the emptiness
specific.

## Grounding

`search_by_guid` is one of the four actions `sim-specs/platform/openapi.json` declares for
`query_splunk`, with `guid`, `earliest`, `latest` and `errors_only` as its arguments. The
one real `query_splunk` call in the trajectories used
`{action: search_by_guid, guid: ..., earliest: -24h, errors_only: true}` — so the *shape*
including `errors_only` is attested, though that call failed with "Splunk not configured"
and returned no data. Everything here is authored.

The generated `schema.json` also drops the `index` enum
(`["custom", "federated:rh_pds-001_aap", "federated:rh_pds-001_ocp_app"]`) —
`CLAUDE.md` records it in `LOST_IN_GENERATION`. This scenario passes no `index`, so the
loss does not bite here, but a future Splunk scenario that grades on the index would be
grading the simulator's imagination.

## Absolute window, stated in the instruction

The instruction names `2026-06-21T00:00:00Z` and a 48-hour span rather than saying "the last
two days". The seeded rows sit inside that absolute window, so the correct answer does not
change with the run date.

## Weighting

`0.2 / 0.8`. One call whose arguments are all handed over; everything measured is the
reasoning about an empty result.

## Invented

The GUID `hq7wz`, both log entries for the other GUID, and every timestamp. **Nothing comes
from the gitignored trace export.**
