## What it measures

Fetching the event-stage component that a workshop is actually built from, rather than the prod
stage that a bare item name resolves to. Two calls in a chain on `whimbrel`:

1. `list_workshops {cluster: whimbrel, namespace: user-wsantos-redhat-com}` returns two
   workshops. The one the user means, display name "Pacemaker Day (Nov 19)", is
   `pcmk-day-nov19`, with `catalog_item: rhel-ha.pacemaker-lab.event`. A second workshop, "HA
   Office Hours", is built from `rhel-ha.pacemaker-lab.prod`.
2. `get_component {cluster: whimbrel, name: rhel-ha.pacemaker-lab.event}`, using the full name
   from call 1, returns `ha_node` 2 x `c7i.large` and `scm_ref: pcmk-lab-3.2.0`.

The trap is parsec's name probing. `_get_component` normalises the name, and when it has fewer
than two dots it tries `<name>`, then `<name>.prod`, `.event` and `.dev`, in that order
(`vendor/parsec/src/tools/babylon.py:828-840`). So an agent that drops the stage and asks for
`rhel-ha.pacemaker-lab` gets the **prod** component: 3 x `m6a.xlarge`, `pcmk-lab-3.4.1`. The
returned `name` (`...prod`) shows the switch, but nothing else does. The prod figures also match
the lab guide the user mentions, so they look right.

Behaviour: **workshop `catalog_item` (stage suffix included) to `get_component` by the full
name; the bare name resolves to the prod stage.** One count (nodes).

## Grounding

- platform SKILL.md `/query_babylon_catalog`: `list_workshops` reads `babylon_workshops` filtered
  by `cluster` and `namespace`, projected to exactly the twelve listed fields (no `multiworkshop`,
  no `resource_claims`). `get_component` reads `babylon_components` filtered by `cluster`, looks
  up by `name`, and never returns `babylon_component_id`.
- api.json SIMULATION STORE AUTHORITY: "`get_component` reads `babylon_components`". The golden
  call passes the exact stored name, so the lookup is unambiguous. What the simulation does with a
  bare name is not graded. It affects only an agent that shortens the name.
- parsec: `_parse_catalog_item` strips a `prod|dev|event|test` suffix into `stage`
  (`babylon.py:128-134`). A workshop's `catalog_item` is its `catalogItemName` label
  (`babylon.py:554`): the full CatalogItem name, stage included.

## Contract

- Calls, `ordered-subsequence`: `list_workshops` pins `cluster` and `namespace` (from the
  instruction). `get_component` pins `cluster` and `name: rhel-ha.pacemaker-lab.event`, which is a
  verbatim leaf of call 1's result.
- Required: the event item (`pacemaker-lab.event`, from call 1), the node type `c7i.large`, and
  `scm_ref` `pcmk-lab-3.2.0`. Count: 2 nodes. The prod values `3.4.1` and `m6a.xlarge` cannot
  satisfy the digit 2: the matcher rejects a digit next to `.digit`.
- No forbidden facts, because the 0.4 tool weight leaves no room under the mute cap. Weights
  0.4/0.6. `fold_markup` on. Gate: golden 1.000, mute 0.400, nocall 0.000, fabricate n/a.

## The wrong answer

"The workshop is built from rhel-ha.pacemaker-lab. Its component (rhel-ha.pacemaker-lab.prod)
specifies 3 m6a.xlarge cluster nodes ..., built from pcmk-lab-3.4.1." Scores **0.400** with the
golden calls (answer 0/4). Two fresh honest answers, terse prose and key/value lines that deny the
prod build, both score 1.000.

## Invented

The cluster `whimbrel`, the namespace, workshop names and codes, item and component names,
revisions and paths are all invented. The instance type names are real AWS types. Nothing comes
from bench-v4 or production data.
