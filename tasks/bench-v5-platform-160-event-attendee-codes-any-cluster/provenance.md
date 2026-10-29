## What it measures

A happy single call: `get_multiworkshop` by **name only, with no cluster**, which is one of the
all-clusters search paths of `query_babylon_catalog`. No other task in either split makes this call
without a cluster.

The user knows the MultiWorkshop name, `aap-reseller-day-lis-1203`, but not its cluster. The call is
`query_babylon_catalog {action: get_multiworkshop, name: aap-reseller-day-lis-1203}`. It searches the
distinct clusters in `babylon_multiworkshops` (`egret` and `plover`) and finds the parent on `egret`.
The result gives the answer directly:

- the cluster, `egret`;
- the dates, 2026-12-03 to 2026-12-04;
- `seats` 36;
- the three child workshops, with their attendee `workshop_id`s: `rdl-collection-trust` w2gyh,
  `rdl-controller-as-code` m8rqe and `rdl-rulebook-starter` t4ckz.

Two near misses are kept out by the store rules, not by the agent. The first is
`rdl-hackathon-sandbox` (j5nfa), which sits in the same namespace but has `multiworkshop: ""`. The
second is the Madrid sibling event on `plover` (40 seats, 2026-11-19..20, codes z7hbu and n3fdx).

Behaviour, for the authors of 165-169: **all-clusters `get_multiworkshop` by name; reading the
seat count, the dates and the per-child `workshop_id`s.** Two counts (seats, labs).

## Grounding

- platform SKILL.md `/query_babylon_catalog`, Optional inputs, `cluster`: "when omitted for
  `get_workshop` or `get_multiworkshop` and `name` is present, search every configured cluster
  represented by distinct stored `cluster` values in the action's collection until one cluster has
  a match". Store reads, `get_multiworkshop`: the parent comes from `babylon_multiworkshops`. The
  children are the `babylon_workshops` rows with the same `cluster` and `namespace` whose
  `multiworkshop` equals the parent's `name`. The api.json STORE AUTHORITY paragraph says the same.
- Response: the parent fields `cluster, name, namespace, display_name, seats, start_date, end_date,
  purpose`, plus `summary` and `workshops`. Each child carries `name, display_name, catalog_item,
  workshop_id, provision_count, resource_claims`. parsec builds `seats` from `numberSeats`
  (`vendor/parsec/src/tools/babylon.py:1487`). The store column is `number_seats`, and the golden
  result follows v4-043's verbatim shape.
- `requester` is omitted from the golden result because `BabylonMultiworkshop` has no such store
  field. The replay compares only the keys the golden result has.
- The children have not provisioned yet: `provision_count` is all zeros and `resource_claims` is
  `[]`. So `summary` is `{total_workshops: 3, active: 0, failed: 0}`, and parsec sums
  `provision_count.active`/`failed` (`babylon.py:1519-1520`, `:1539`). Nothing graded depends on `summary`.

## Contract

- One expected call, `ordered-subsequence`: `get_multiworkshop` with `name` pinned and `cluster`
  deliberately unpinned. An agent that discovers `egret` some other way and passes it has done the
  same work.
- Required: the cluster `egret`, the start date and the end date (ISO, "December 3", "3 Dec", and
  ranges such as "December 3-4"), and the three workshop IDs.
- Counts: seats 36; labs 3, where "workshops" also counts as the noun.
- No forbidden facts or calls. This is a happy task, so the weights are 0.2/0.8. The mute floor
  is 0.200, the nocall floor 0.000, and fabricate is n/a.

## The wrong answer

`/tmp/ext/scratch/160/wrong.md` is the refusal: "Babylon needs a cluster name for MultiWorkshop
lookups ... I can't retrieve" it. It scores **0.20** (tool calls only).

`wrong2.md` adds the same-namespace hackathon sandbox as a fourth lab ("4 labs ... j5nfa"). It
scores **0.90**: it loses the labs count, and this is partial credit by design.

Honest answers `honest1.md` (terse prose) and `honest2.md` (Key: value lines plus a table, which
explicitly excludes the sandbox and the Madrid event) both score **1.000**.

## Invented

The cluster names `egret` and `plover`, the namespace, the event and workshop names, the catalog
items, the workshop IDs, the seats and the dates are all invented.
Nothing comes from bench-v4, from the original bench-v5 or from production data.
