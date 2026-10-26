# bench-v5-cloud-307-azure-two-project-tags

**Kind:** happy. **Calls:** 2. **Weights:** 0.3 / 0.7.

## What it measures

Two sibling `query_azure_pools` `search_by_project` lookups, one per project tag, combined
into one inventory. `search_by_project` matches `projecttag` exactly. The `fsi-fraud-demo`
search therefore does not return the `fsi-fraud-demo-eu` subscriptions, and the second
call is needed.

- `fsi-fraud-demo`: 3 subscriptions (pool-14-207, pool-14-212, pool-19-033).
- `fsi-fraud-demo-eu`: 2 subscriptions (pool-19-041, pool-19-046).
- All 5 are in use.

A happy path whose discrimination is completeness: an agent that runs one search and
assumes the `-eu` tag is a subset loses half the facts.

## Grounding

- cloud SKILL.md `/query_azure_pools POST`:
  - `search_by_project` reads `azure_subscriptions` in the effective database (default
    `pools`) "where `projecttag = project_tag`".
  - Its response is `{database, project_tag, subscriptions[{id, used, projecttag}],
    count, truncated}`.
  - `count` equals the length of `subscriptions`.
- Seed: 9 `pools` rows, plus `pool-14-219` tagged `fsi-fraud-demo` in the `roadshow`
  database. That row is out of scope ("Rows with any other stored `database` value are
  treated as non-existent") and is a leak sentinel. Free rows carry `projecttag: ""`.
- Golden results: rows in seed order.

## Contract

- Required `sub-*`: the five subscription ids.
- Counts:
  - `count-a` = 3. A roadshow leak would make it 4.
  - `count-b` = 2. This one requires the second search.
- Expected calls pin `action` and `project_tag` for both, matched `unordered-subset`.
- No forbidden fact (happy path). Mute 0.00, echo 0.00.

## The wrong answer

`.scratch/wrong/w307.md`, with only the first search: "The -eu tag is presumably already
part of that set". Reward **0.55** (tool_calls 0.5). It misses pool-19-041, pool-19-046 and
count-b.

## Invented

Every literal is invented: subscription ids, pools and project tags. Nothing comes from
bench-v4 or from production data; the bundle's example ids (pool-01-273/274) are avoided.
