# bench-v4-platform-040-workshop-cross-cluster-name-search

Idea from bench-h4_Oct5 040 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. The instruction names the workshop but no cluster, and the
workshop is not on the first cluster the store holds. An agent that guesses a
cluster (or assumes a default) gets `Workshop ... not found` and has nothing to
report; only `get_workshop` by `name` with `cluster` omitted, which searches
every cluster, finds it. A guessed cluster, a guessed registration state, the
sibling workshop's registration flag, a healthy claim's job id and the decoy
workshop's failed job all earn nothing.

## What it measures

A two-hop chain, the suite's first expected use of `get_workshop` and
`list_workshops`:

1. `query_babylon_catalog` `get_workshop` `{name: edge-fleet-handson}`, no
   `cluster`, no `namespace`.
2. `query_babylon_catalog` `list_workshops` `{cluster: emea, namespace:
   user-tnakamura-redhat-com}`, both values taken from call 1's result.

Mechanism, from parsec:

- `vendor/parsec/src/tools/babylon.py:687-689`: with no resolvable cluster,
  `get_workshop` with a `name` goes to `_search_all_clusters_for_workshop`
  (`:1281-1300`), which tries `_get_workshop` on every configured cluster and
  returns the first hit. `_get_workshop` (`:1198-1278`) discovers the
  namespace by a cluster-wide Workshop listing matched on name (`:1211-1233`)
  and returns `cluster`, `namespace`, the labels, `provision_count`,
  `user_count` and `resource_claims` -- each claim traversed by
  `_fetch_resource_claims` (`:1164-1195`) into `resources[]` whose
  `_extract_anarchy_state` (`:388-415`) maps `towerJobs` to
  `tower_jobs.provision.{controller, job_id, status, completed}`.
- **`get_workshop` does not return `open_registration`** (`:1257-1269` build
  the whole result; no `openRegistration` read). Only `list_workshops`'s
  `_extract_workshop_info` (`:544-572`, `open_registration` at `:558`) does,
  and `list_workshops` requires `namespace` (`:1125-1130`). That is why the
  chain needs its second hop, with the cluster and namespace learned from
  the first.
- `harness-skills/parsec-platform/SKILL.md`, `/query_babylon_catalog`:
  "Cluster resolution" lists `get_workshop` with `name` among the four shapes
  that search every cluster, over "the sorted distinct stored `cluster`
  values" of the backing collection; "Store reads by action" says both
  `get_workshop` and `list_workshops` read `babylon_workshops` filtered by
  `cluster` first, `get_workshop` then matching `name` only within each
  searched cluster. There is no separate claim collection: the traversed
  claims are the stored row's `resource_claims` field ("Traversed resource
  claims for detailed workshop output", `schema.json`), so that is where the
  seed puts them.

Pinned arguments: call 1 pins only `action` and `name` (in the instruction).
`cluster` is **not** listed in `absent_args`: an agent that probes clusters by
name and lands on `emea` has found it just as legitimately, so the trap is
graded in the answer, not by a forbidden call. Call 2 pins `cluster` and
`namespace`, both of which appear only in call 1's result
(`check_expected_calls_derivable`). No forbidden call, no free-text argument.

## Seed design

`seeds/platform.json` carries every platform collection; all are empty except
`babylon_workshops` (`workshops`, the child projection no operation reads, is
`[]`). Searched cluster order is `apac`, then `emea`.

| babylon_workshop_id | cluster | name | open_registration | claims (provision job) |
|---|---|---|---|---|
| `emea-edge-fleet-handson-overflow` | emea | `edge-fleet-handson-overflow` | **true** | c2v6n started (64131) |
| `emea-edge-fleet-handson` (**target**) | emea | `edge-fleet-handson` | **false** | h7k2p started (64102), **w9d4x provision-error (64117, failed)**, r5m8t started (64125) |
| `apac-edge-fleet-handson-apj` (decoy) | apac | `edge-fleet-handson-apj` | true | j3t8b started (58824), p6x1z provision-error (58830, failed) |

All three share namespace `user-tnakamura-redhat-com`. The sibling sits in the
target's namespace on `emea`, so `list_workshops` returns two rows and the
agent must read the target's row (store order puts the sibling first); its
`true` is the wrong-row reading. The apac decoy has a different name, so the
all-cluster `get_workshop` never matches it; it is what an agent reads if it
carries the namespace to the wrong cluster (`list_workshops {cluster: apac}`),
and its failed claim's job 58830 is the wrong-workshop job id. Tower job ids
are integers (`BabylonTowerJob.job_id` admits both; `query_aap2` uses
integers). `emea` occurs in no returned literal other than `cluster`.

## Golden results

Call 1's result is `_get_workshop`'s projection of the target row (the
`BabylonWorkshopDetail` fields), call 2's is `{cluster, namespace, workshops,
count, truncated}` with each row as `_extract_workshop_info` builds it plus
`cluster`. `replay.leaf_mismatches` checks expected keys only, so a live
response carrying extra stored fields still matches. **Replay must confirm**
(Task 8) that the live `get_workshop` returns the stored `resource_claims`
verbatim and that the all-cluster search finds `emea`. If the live
`get_workshop` also echoes the stored `open_registration` (SKILL.md's
"Return every stored entity field exactly as stored"), an agent could answer
the registration question from call 1 and lose only the second expected call
(tool 0.5 of 0.3); the grading of the answer is unaffected. **Live replay (2026-10-08):**
the raw `get_workshop` response carries **no** `open_registration` key (only
`babylon_workshop_id` beyond the golden keys). The all-cluster search finds `emea`.
`resource_claims` come back verbatim. `list_workshops{emea, ns}` returns exactly the two emea
rows, with `open_registration` false on the target and true on the overflow row. Verdict `ok`.

## Contract

Four required facts, none forbidden, weights `0.3 / 0.7` (no forbidden fact, so
the tool weight follows the common brief's "prefer <= 0.4"; the second call is
genuinely dependent on the first's result, the first carries only the name from
the instruction).

- `cluster-emea`: `emea`. Only the all-cluster lookup yields it; the
  instruction names no cluster.
- `registration-closed` (derived): the target's `open_registration: false`,
  stated as a negation or a flag value. 572 forms, generated and then pruned
  so that no form contains another. The count was 603 after fix round 2.
  The subject is plain `registration`,
  which `open registration`, `open_registration` and `openRegistration` all
  contain. The forms fall into four groups:
  - key/value notations: `registration` plus a punctuation separator (`: `,
    ` = `, ` | `, arrows, dashes, bold/backtick variants, ` (`) plus `false`,
    `disabled`, `closed`, `off`, `no`, `not enabled`, `not open`, `inactive`,
    ❌, ✗. The same for `registration status` and `registration state`.
  - worded separators (` is `, ` is set to `, ` set to `): never `no`, and
    `off` only when terminated (`off.`, `off,`, `off (`, `off for`), so
    "registration is officially open" matches nothing.
  - question echoes answered no: "registration turned on? no", "registration
    enabled? no", "registration on? no" and so on.
  - prose, every prefix completed: "registration is not / isn't / is not
    currently / is no longer + enabled, turned on, active, open, on.". Also
    "registration is closed / disabled / inactive / turned off", "n't allow
    open registration", "not open for registration", "cannot self-register".
  - dash separators (` — `, ` – `, ` - `): `no` only when terminated (`no.`,
    `no;`, newline, `no (`, `**no**`, `no —`, `no -`), never `no,`, because
    "Open registration — no, it's on." is a wrong reading. The en dash and the
    hyphen also take `false`, `disabled`, `closed`, `not enabled` and
    `inactive`.
  A bare space-joined form ("registration disabled") appears only with a
  terminator (`.`, `,`, `;`, ` (`, newline, dash), so "Is open registration
  disabled? No, it is enabled" never matches.
- `failed-claim`: `w9d4x`, the failed claim's guid inside
  `edge-fleet-handson-prod-w9d4x`.
- `provision-job-id` (`answer.counts`): value 64117 within 10 tokens of
  `job`/`id`/`provision`/`aap2`/`tower`/`controller`... (hazard 5: no bare
  digit form).

Measured residuals (acceptance bar C, not defects):

- An honest answer that lists every claim's job id earns the job fact, even if
  it does not single out the failed one.
- **Bare `registration: no` is kept by ruling.** Answers commonly end with
  "Open registration: No", so the form stays. The cost: the contrived "Open
  registration: no restrictions, anyone can join" also earns the fact, and an
  answer that is otherwise all decoy scores 0.475 (reviewer probes f9 and
  f11). The same holds for ` = no` and ` | no`.
- An answer that ends on the word "off" with no punctuation ("... and open
  registration is off") misses the fact and scores 0.825. Bare "is off" would
  also match "is officially open", so the form has to be terminated.
- A terminated form cannot match at the very end of an answer. "... open
  registration is off" or "Open registration — No" as the last words, with no
  final punctuation, misses the fact and scores 0.825. Making the form bare
  would let "— now on" and "is officially open" match.
- Contrived wrong readings that still earn the fact score 0.475 (reviewer
  probes g20, g25, g26): "Is registration closed, no? It's open", "Registration
  closed - no, it reopened" and "Registration: closed earlier, now open".
- A fabricator who guesses "closed" for registration earns that one fact
  (0.475 with the golden calls). It is a true literal, and a guess has a 50%
  chance of landing on it.

Ideas-only check (S7): two required forms, `registration": false` and
`registration is false`, also occur in the batch's own files. They are
field-name notations forced by the mechanism: `open_registration` is the
schema's field name and `false` is the graded value. They were not copied.
The batch's instruction runs: status check, can't remember which cluster, more
than one, then the failed claim's job. The first draft of this instruction
shared that order and the phrases "which of our Babylon clusters", "status
check" and "more than one". Fix round 1 rewrote it to open with the failed
claim. Its 3- to 5-word n-grams now have no match in the batch directory. No
seed value, id or name overlaps the batch (`apac` matched only inside the
batch's word "capacity").

## Gate

`bench-validate.py`: golden 1.000, mute 0.300, nocall 0.000, fabricate n/a.
