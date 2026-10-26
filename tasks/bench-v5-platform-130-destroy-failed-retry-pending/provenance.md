## What it measures

Whether "retired" means destroyed. The lab's AnarchySubject on `harrier` has `desired_state: destroyed`, but `current_state: destroy-failed`. Its AnarchyActions, which are returned out of time order, show:

- provision, successful
- stop, successful
- destroy, `failed`, finished 2026-10-09T02:41:30Z
- a second destroy, `pending`, with `after: 2026-10-13T06:00:00Z` and `finished: ""`

The agent has to read the action history rather than the desired state, and it has to read `after` as the earliest time the retry may run. As of the instruction's date (2026-10-12), the retry has not run.

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `list_anarchy_subjects` reads `babylon_anarchy_subjects`, and `list_anarchy_actions` reads `babylon_anarchy_actions`, each filtered by `cluster`. For actions, `guid` matches "only when `subject_name` contains `guid`". Projection: `name, namespace, action, after, subject_name, subject_namespace, governor, state, finished`.
- Schema: `after` is the "Do-not-run-before timestamp string". `finished` is "Finished timestamp string, or empty when unfinished".
- `cluster` is a free request string, and every row carries `cluster: harrier`. A destroy for another subject succeeded at the same time (`ansible-rhel-ws.m9bfx`), which shows the destroy run itself was not globally broken. Its subject name does not contain `j8tvd`, so a guid-scoped listing never returns it.
- validate.py WARN (if shown), justified: counts and `all (cluster-wide)` are derived envelope values.

## Contract

- Calls, `unordered-subset`: `list_anarchy_subjects` and `list_anarchy_actions`, each pinned only on `action` (since 2026-10-25; both pinned `cluster: harrier` before). They are siblings with no dependency; a cluster-wide listing and the all-clusters GUID search both count.
- Forbidden call: `query_babylon_catalog` `action: get_anarchy_action`. It is not an api.json enum value, and the in-band result is `Unknown action`. It is a plausible guess, because `get_deployment`/`get_workshop` exist alongside their `list_` forms.
- Required:
  - `not-destroyed` (derived)
  - `destroy-failed`
  - the failure date 2026-10-09
  - the retry's not-before date 2026-10-13
- Forbidden fact `claims-destroyed`: "has been destroyed", "is destroyed", "teardown completed", and similar. It has no excuses; an honest answer never needs these strings (the negations "not been destroyed"/"hasn't been destroyed" do not contain them).
- Weights 0.3/0.7.

## The wrong answer

- `.scratch/probe/130-wrong.md` ("desired_state destroyed and there is a destroy action, so it has been destroyed") scores **0.30** with the golden calls.
- `130-wrong2.md` reads every date right but still says "has been destroyed". It scores **0.72**.

## Invented

The GUIDs, action names, job ids, emails, timestamps and the cluster `harrier` are invented. Nothing comes from bench-v4 or production data.

leakage.py WARN, justified: `destroy-failed` is a real Anarchy lifecycle state, part of the shared system vocabulary just as `stop-failed`/`started` are. It also appears as a state in a training seed. No training task grades it as the answer to a failed-destroy-with-pending-retry question, and leakage.py reports the task clean. `06:00` is a time of day.
