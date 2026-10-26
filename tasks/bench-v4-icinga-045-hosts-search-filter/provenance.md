# bench-v4-icinga-045-hosts-search-filter

Idea from bench-h4_Oct5 045 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. A host search for `ledger-api` returns two hosts: one DOWN with a distinctive
check output, one UP. Three other hosts are in the store, two of them DOWN, none matching.
Calling the UP match down (or "both down"), or reporting a non-matching DOWN host as one of the
matches, is penalised.

## What it measures

One read, `query_icinga {action: get_hosts, search: ledger-api}`. The agent must split the two
matches by `attrs.state` and quote the failing host's `last_check_result.output`.

- parsec: `query_icinga` (`vendor/parsec/src/tools/icinga.py:65-108`) passes `get_hosts` through
  to the Icinga MCP sidecar with only the truthy read args (`_build_read_args`, `icinga.py:11-25`;
  `detailed` always forwarded). The response is the sidecar's, verbatim -- a passthrough.
- Bundle: `harness-skills/parsec-icinga/SKILL.md` `/query_icinga POST`: `get_hosts` reads only
  `hosts`, filters by `search` and `filter_expr` when provided (lines 174-178), returns the JSON
  serialization of the matched store rows under `result`, in stored order. `get_problems` ignores
  every filter and returns all non-OK rows -- the route by which the two non-matching DOWN hosts
  reach an agent that answers from a problems view.
- Recorded parsec runs (results/bench/*/bench-v4-icinga-*/agent/agent.jsonl) query Icinga with
  `filter_expr: match("*x*", <obj>.name)` at least as often as with `search`. `ledger-api` occurs
  only in the two matching hosts' `name`/`display_name`/`host_name` -- not in any group, output
  or other host -- so the matched set is the same under `search` (exact, substring or fuzzy) and
  under a `match("*ledger-api*", host.name)` glob.
- Golden result shape: full stored rows (Icinga2 `name`/`type`/`attrs` envelope), the shape
  recorded live for `get_services` and used by sibling 046.

## Seed

`seeds/icinga.json`: `comments` [], `downtimes` [], `services` [], five hosts in name order:

| name | attrs.state | last_check_result.output |
|---|---|---|
| build-runner-11 | 0 UP | PING OK - Packet loss = 0%, RTA = 1.12 ms |
| ldap-replica-07 | 1 DOWN | CRITICAL - Host Unreachable (10.44.9.31) (non-match decoy) |
| ledger-api-fra | 1 DOWN | PING CRITICAL - Time to live exceeded (10.61.4.22) |
| ledger-api-lon | 0 UP | PING OK - Packet loss = 0%, RTA = 0.84 ms (in-search decoy) |
| mq-broker-02 | 1 DOWN | PING CRITICAL - Packet loss = 100% (non-match decoy) |

State integers are Icinga2's host values (0 UP, 1 DOWN); `last_check_result.state`/`exit_status`
are the plugin's (0 OK, 2 CRITICAL). The decoy the brief asks for is `ledger-api-lon`: the search
does return it, and excluding it from the DOWN list needs reading its row. The failing output is
deliberately not a generic down-host phrase: "unreachable" and "packet loss 100%" are what the
non-matching decoys say and what a fabricator guesses; "time to live exceeded" is not.

## Contract

- Expected call: `query_icinga {action: get_hosts}`. `search` is not pinned (hazard 19); a
  `filter_expr` route reaches the same rows. No forbidden calls.
- Required:
  - `down-match-fra`: `ledger-api-fra` (not in the instruction).
  - `fra-check-output`: the output detail -- "time to live (exceeded)", "time-to-live", "ttl
    exceeded/expired", "ttl" followed by `.`/`,`/`)`, or the address `10.61.4.22`. Nothing else in
    the seed says any of these.
  - `lon-is-up` (derived, with note): `ledger-api-lon` followed by a state notation -- verb forms
    (`is`, `remains`, `, which is`, `looks`, `reports` + up/healthy/reachable/ok/not down/ping ok),
    punctuation forms (`: `, ` (`, `--`, em dash, `-`, `|`, `=`, arrows + up/state 0/...), state
    forms (`has state`, `(state `, `status: ` + up/0), backtick/bold variants, plus the short
    `lon is up` family. Name and state are graded **together** so that the forbidden
    `ledger-api-lon is down` forms contain no required form (hazard 12); a name-only fact would
    have let a pure decoy reading ("ledger-api-lon is DOWN") bank a point.
- Forbidden (one fact, two wrong readings): `ledger-api-lon` + down/failing in the same notations,
  "both (hosts|matches|...) are down", "are both down"; and membership claims for the two
  non-matching DOWN hosts ("mq-broker-02 is one of the", "also matches", "is also a match", "is a
  third"; same for `ldap-replica-07`). Both decoys really are DOWN, so their state is never
  forbidden. `attributed_to` excuses a sentence saying "not both", "only one of", "do(es) not
  match", "not part of", "excluded", "unrelated", "are both down?", etc.

S7: no required form occurs in `instruction.md`; no forbidden form occurs in the seed; no
forbidden form contains a required one. Overlap with the batch: no host name, address, output,
group, instruction fragment or form is shared. Generic vocabulary shared with it -- `DOWN`,
`check output`, `search`, "does not match" -- is forced by the mechanism (Icinga host states, the
question's concept).

## Weighting

`0.2 / 0.8`. The one call carries no identifier to work out (only `action` is pinned); the work
is the state split and reading the output. Three required facts and one forbidden: mute 0.400,
nocall 0.200, fabricate 0.200.

## Measured residuals (bar C)

Probed through `tests/verify.py` with the golden call held correct (task-13 report):
- 20 honest paraphrases (tables, bullets, `state = 1`/`state 0` notation, "not both are down",
  "Are both down? No.", "lon is UP", "TTL expired", decoys named as down-but-non-matching) all
  1.000.
- **A get_problems reading that lists `ledger-api-fra, mq-broker-02 and ldap-replica-07` as the
  down matches with the TTL output scores 0.800.** It earns the true fra name and output; a form
  catching the list would contain `ledger-api-fra` (hazard 12) or collide with an honest mention
  of the decoys. It loses only `lon-is-up`. Accepted.
- "ledger-api-fra and ledger-api-lon are both down; fra reports Time to live exceeded" scores
  0.600 (tripped; earns the true fra facts).
- **Separate-sentence state is missed**: "The second match is ledger-api-lon. Its state is UP."
  scores 0.800 (misses `lon-is-up`). The composite needs name and state adjacent; a cross-sentence
  form would have to be a bare state word, which a decoy reading earns. Accepted.
- "ledger-api-lon is unreachable and DOWN. ledger-api-fra is UP." scores 0.600: it trips nothing
  (no fra-is-up form is possible without containing the required `ledger-api-fra`) and earns the fra
  name. "ledger-api-lon looks ok in the list but it is actually DOWN; ledger-api-fra is up." scores
  0.800 (earns the name and the `looks ok` composite). Both are bar C: they state true graded
  literals alongside a false one.
- `lon-is-up` is not bound to a sentence: an answer that says `ledger-api-lon is up` while
  wrongly calling something else down still earns it. The state is true, so that is correct.
