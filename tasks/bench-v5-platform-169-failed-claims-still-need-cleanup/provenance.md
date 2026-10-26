## What it measures

A wide fan-out of `list_deployments`, one call per attendee namespace. After an event, the
organiser needs every ResourceClaim from the event's catalog item that still exists, so it can be
deleted. `list_deployments` requires a `namespace` (`vendor/parsec/src/tools/babylon.py:923-928`),
so a cleanup across eight attendees takes eight calls:
`list_deployments {cluster: skua, namespace: user-<attendee>-redhat-com}` for each namespace.

What the eight results hold:

| namespace | claims |
|---|---|
| lmoreau | `gitops-day-hq8vs` (started) |
| kdasgupta | none |
| pferreira | `gitops-day-pw3nd`: **state failed, healthy false, ready false** |
| jnakashima | `gitops-day-cx9tl` (stopped), plus a personal `podman-lab-dr4hw` from `rhel.podman-lab.prod` |
| ebrennan | `gitops-day-ej5rm` and `gitops-day-fk2zb` (ordered twice) |
| sokoye | none |
| mlindgren | only a personal `podman-lab-gm7yd` |
| hcastillo | none |

Answer: 5 leftover event claims (hq8vs, pw3nd, cx9tl, ej5rm, fk2zb), held by 4 attendees.

The traps:
- the failed claim `pw3nd` still exists and still needs deleting. Treating "never came up" as
  "nothing to clean" gives 4 claims and 3 attendees;
- the personal labs from another catalog item must be left out, which a count of every claim
  would not do (7);
- the second claim in ebrennan's namespace is easy to miss.

A same-named namespace on another cluster, `albatross`, holds a further event claim (yt6wc).
Cluster filtering keeps it out.

Behaviour: **per-namespace `list_deployments` fan-out, filtered by `catalog_item`, where a
failed or stopped claim still counts as a leftover.** Two counts (claims, attendees).

## Grounding

- platform SKILL.md `/query_babylon_catalog`, `list_deployments`: requires `namespace`, reads
  `babylon_deployments` filtered by `cluster` and then by `namespace`, and returns `{cluster,
  namespace, deployments, count, truncated}`. Empty-result contract: a namespace with no rows gives
  `deployments: []`, `count: 0`, `truncated: false`, with the envelope kept. No element carries
  `cluster` or the `_id` key.
- schema.json `BabylonDeployment`: `state`, `healthy` and `ready` are stored per row. The failed
  claim is seeded with `state`/`current_state` `failed` and `desired_state` `started`.
- Golden list order is by claim name.

## Contract

- Calls, `unordered-subset`: eight `list_deployments`, each pinning `cluster: skua` and one
  namespace from the instruction. `search` and `guid` are unpinned.
- Required: the five leftover GUIDs, one fact each (`asked_by` "with its GUID").
- Counts: 5 claims (nouns claims / ResourceClaims / labs / leftovers / deployments) and 4
  attendees (attendees / namespaces / people / users), each with a window of 4. No GUID begins
  with a digit.
- Forbidden (`drops-failed-claim`): the totals that leave out pw3nd ("4 leftover", "3
  attendees", ...) and "nothing to clean up there". Honest answers state 5 and 4.
- Weights 0.3/0.7. Agent timeout 900. `fold_markup` on. Gate: golden 1.000, mute 0.388, nocall
  0.087, fabricate 0.300.

## The wrong answer

It lists hq8vs, cx9tl, ej5rm and fk2zb, says pw3nd "never provisioned, so there is nothing to
clean up there", and totals 4 claims held by 3 attendees. It scores **0.738** with the golden
calls. It still names pw3nd, which earns that GUID; without that mention it scores 0.650. Two fresh
honest answers, terse prose and a per-namespace table with a key/value total that denies a
personal lab is an event lab, both score 1.000.

## Invented

The cluster names `skua` and `albatross`, the attendee namespaces, claim names, GUIDs, catalog
items, asset UUIDs and timestamps are all invented. Nothing comes from bench-v4 or production
data.
