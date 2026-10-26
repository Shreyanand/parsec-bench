## What it measures

A counting task over one `query_babylon_catalog` `list_anarchy_actions` `{cluster: kite}` call. The listing holds 13 kite rows, returned out of time order. To answer correctly the agent has to:

- restrict to rows whose `finished` falls in 2026-10-05..2026-10-11. One failed destroy finished on 10-03 and one failed provision on 10-12, so both are excluded.
- count the `state: failed` rows by kind. There are 5: stop 2, provision 1, start 1, destroy 1.
- de-duplicate them by `subject_name`. That gives 4 labs, because `ocp-virt-lab.p7mhx` failed its stop twice.
- decide recovery from later successful rows of the same kind. `k2rwd`'s provision retry and `v8jnc`'s start retry both succeeded. `p7mhx` has no successful stop. `d4fqs`'s only destroy retry is `pending`: `finished` is "" and `after` is 2026-10-13. So 2 labs are still broken.

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `list_anarchy_actions` reads `babylon_anarchy_actions`, "filtered by `cluster` for normal path". Optional `namespace` and `search` narrow the listing. Each action is projected to exactly `name, namespace, action, after, subject_name, subject_namespace, governor, state, finished`. The schema says `finished` is "Finished timestamp string, or empty when unfinished".
- `cluster` is a free request string, and every row carries `cluster`. Two failed rows on `heron` cannot reach a kite listing.
- validate.py WARN, justified: `13` (count) and `all (cluster-wide)` (namespaces_searched) are not seed values. They are the documented derived envelope values.

## Contract

- Call: `list_anarchy_actions` pinned on `cluster: kite`; `search`/`namespace` are unpinned.
- Forbidden call: `query_babylon_catalog` `action: get_anarchy_actions`. It is not an api.json enum value, and the in-band result is `Unknown action`.
- Counts: 5 failed actions, 4 distinct labs, 2 stop failures.
- Required: the two still-broken labs, `p7mhx` and `d4fqs`.
- Forbidden facts:
  - `actions-as-labs`: "5 labs".
  - `window-leak`: "6/7 failed actions", which includes the 10-03 or 10-12 rows.
  - Neither has excuses; an honest answer has no reason to state them.
- Weights 0.2/0.8.

## The wrong answer

- `.scratch/probe/128-wrong.md` includes the 10-12 failure ("6 failed actions"), calls it "5 labs" and lists every failed lab as needing attention. It scores **0.54** with the golden calls: two forbidden facts hit, two counts missed.
- `128-wrong2.md` ("5 failed actions across 5 labs, every failed lab still broken") scores **0.43**.

## Invented

The GUIDs, action names, governors, timestamps and the clusters `kite`/`heron` are invented. Nothing comes from bench-v4 or production data.
