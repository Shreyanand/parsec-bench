## What it measures

A wide fan-out drift audit: the same lab compared across four clusters. The 8 calls are exactly:

1. `search_catalog` with `cluster: condor`
2. `get_component` with `cluster: condor`, `name: netauto.fundamentals`
3. `search_catalog` with `cluster: heron`
4. `get_component` with `cluster: heron`, `name: netauto.fundamentals`
5. `search_catalog` with `cluster: kite`
6. `get_component` with `cluster: kite`, `name: netauto.fundamentals`
7. `search_catalog` with `cluster: puffin`
8. `get_component` with `cluster: puffin`, `name: netauto.fundamentals-ng`

So that is `search_catalog` x4 plus `get_component` x4, and the instruction asks for exactly this: "for each one, find the catalog item, look up its component". Every pinned `get_component` argument is derivable:

- `cluster` comes from the instruction and is echoed in the search envelope.
- `name` is the `ci_name` of the non-instructor row that search returns on that cluster.

On puffin that `ci_name` is `netauto.fundamentals-ng`, so guessing the name from the other clusters fails there.

The answer is in `scm_ref`, a field no training task reads. heron is on `v2.9.4`, and the other three are on `v3.2.0`.

## Grounding

- platform SKILL.md `/query_babylon_catalog`:
  - `search_catalog` reads `babylon_catalog_items` filtered by `cluster`, with `search` a substring over `ci_name`/`display_name`/`keywords`.
  - `get_component` reads `babylon_components` filtered by `cluster` and looks up by name. It returns `scm_url`/`scm_ref`/`agnosticv_*` "when stored".
- The component `name` equals the catalog `ci_name` exactly, so no suffix probing is needed.
- `cluster` is a free request string. Every row carries `cluster`, and the primary keys are `<cluster>-<name>`, which are unique.
- Each cluster also has `netauto.fundamentals-instructor` ("... - Instructor Edition", `scm_ref v3.3.0-rc1`, its own agnosticv path). Inspecting it is allowed and not forbidden as a call, as the reviewer asked. Reporting its ref or path as the student lab's is a forbidden fact.

## Contract

- Calls, `unordered-subset`: the 8 above. `search` is unpinned. The per-cluster dependency is enforced by derivability, because the puffin name exists only in puffin's search result. The clusters are independent of one another, so no cross-cluster order is graded.
- Required: the outlier ref `v2.9.4`, the majority ref `v3.2.0`, and puffin's `netauto.fundamentals-ng`.
- Count: 3 clusters on the majority ref.
- Forbidden fact `instructor-as-item`: `v3.3.0-rc1` or the instructor path. The excuses are specific to the decoy ("Instructor Edition", "netauto.fundamentals-instructor", "instructor variant", ...), so an answer may mention the decoy's ref when it names the decoy.
- Weights 0.3/0.7.

## The wrong answer

- `.scratch/probe/135-wrong.md` guesses `netauto.fundamentals` on all four clusters without searching and says the lab "may not be published" on puffin.
  - With its own 4 calls (`135-wrong-calls.json`) it scores **0.53** (tool calls 0.375).
  - With the golden calls it scores 0.72.
- `135-wrong2.md` reports the Instructor Edition's ref for every cluster. It scores **0.30**.

## Invented

The catalog items, UUIDs, refs, paths, the scm URL and the four clusters are invented. `rhpds/agnosticv` and the AWS instance type names are shared real vocabulary. Nothing comes from bench-v4 or production data.
