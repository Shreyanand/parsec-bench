# bench-v4-icinga-046-services-search-cross-host

Idea from bench-h4_Oct5 046 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. Of three services matching `fs-capacity` on three hosts, two are CRITICAL and
one is WARNING; the host carrying one CRITICAL match also carries a CRITICAL service whose name
does not match. Calling the WARNING match critical, or reporting the non-matching service as an
affected match, is penalised.

## What it measures

One read, `query_icinga {action: get_services, search: fs-capacity}` with **no** `host`, so the
result spans every host. The agent must then split the matches by severity and read the fill
percentage out of each critical row's plugin output.

- parsec: `query_icinga` (`vendor/parsec/src/tools/icinga.py:65-108`) passes `get_services`
  straight through to the Icinga MCP sidecar with whatever of `search`/`host`/`filter_expr`/
  `detailed` were given (`_build_read_args`, `icinga.py:11-25`, adds `host` only when truthy).
  The response is the sidecar's, verbatim -- a passthrough (CLAUDE.md, `src/simspec/`).
- Bundle: `harness-skills/parsec-icinga/SKILL.md` `/query_icinga POST`: `get_services` reads only
  `services`, filters by `search` and by `host` "when provided", and returns the JSON
  serialization of the matched store rows under `result`, in stored order. `get_problems`
  ignores every filter and returns all non-OK rows -- which is exactly how the decoy reaches an
  agent that answers from a problems view instead of the search.
- Golden result shape: the full stored rows (Icinga2 `name`/`type`/`attrs` envelope), as the
  live v0.2.0 simulation returns them -- confirmed against recorded live `get_services` results
  in `results/bench/baseline-v2/`, `live-full-2/`, `parsec-15/` (e.g. the cert-expiry search in
  017). Not the flattened shape of the older 010-017 goldens.

## Seed

`seeds/icinga.json`, all four collections. Hosts `nas-alpha`, `nas-bravo`, `nas-charlie`, all UP.
Services (stored order):

| name | state | output |
|---|---|---|
| nas-alpha!fs-capacity | 2 CRITICAL | DISK CRITICAL - /srv/export 96% used |
| nas-alpha!ntp-offset | 0 OK | NTP OK - offset 12 ms |
| nas-bravo!fs-capacity | 1 WARNING | DISK WARNING - /srv/export 84% used |
| nas-charlie!fs-capacity | 2 CRITICAL | DISK CRITICAL - /srv/export 91% used |
| nas-charlie!inode-usage | 2 CRITICAL | INODE CRITICAL - /srv/export 97% of inodes used (decoy) |

`fs-capacity` occurs in the `name` of exactly the three matches and nowhere else in the seed --
not in any display name, group or output -- so the expected result is the same under exact,
substring or fuzzy search semantics (SKILL.md does not say which the sidecar uses). The decoy
shares the host and the mount path with a critical match, and nothing in its row says
`capacity`. State integers are Icinga2's real values (0 OK, 1 WARNING, 2 CRITICAL); the
`attrs.state` enum was lost in generation (`LOST_IN_GENERATION`), so the store does not enforce
them, but these are the values parsec's Icinga would emit.

## Contract

- Expected call: `query_icinga {action: get_services}`. `search` is not pinned (hazard 19 --
  free-text), and `host` is not forbidden: an agent that lists hosts and queries each one reaches
  the same rows legitimately.
- Required: `nas-alpha` and `nas-charlie` (the CRITICAL matches; neither is in the instruction).
- Counts: 96 and 91, each with nouns a correct answer puts beside a percentage (`used`, `full`,
  `percent`, `usage`, `utilisation`, `capacity`, `critical`, `disk`, `filesystem(s)`, `volume(s)`,
  `fill`, `respectively`, the mount path tokens, and the host's own name token `alpha`/`charlie`
  for the bare `nas-alpha: 96%` form). `%` is not a token for `_count_present`, so it cannot be a
  noun; the digit guard (`(?<!\d)(?<![\d][.,])N(?!\d)(?![.,]\d)`) accepts `96%`. No other seed
  output carries 96 or 91. **The counts are not bound to a host**: the host token is only one of
  the nouns, so a swapped pairing earns both (see residuals).
- Forbidden (one fact, two wrong readings): `nas-bravo` asserted critical (subject-anchored forms
  incl. table-cell and dash notations, "all three are critical", "are all critical"), or
  `inode-usage` asserted to be *one of the matches* -- determiner-bearing membership forms only
  ("inode-usage is one of the", "is also a match", "also matches", "is an affected", "is a
  third"). `nas-charlie!inode-usage` really is CRITICAL, so no form forbids stating its state.
  `attributed_to` excuses a sentence that says the decoy is outside the match ("does not match",
  "not part of", "excluding", "separate check", "unrelated", ...) or "not all". No form contains
  `nas-alpha`/`nas-charlie` (hazard 12) and none occurs in the seed (hazard 14).

Overlap with the batch (S7): the instruction, every host/service name, path, number and form is
new. Shared generic vocabulary -- `critical`, `disk`, `usage`, `full`, `percent`, `does not
match` -- is forced by the mechanism (Icinga state names, the question's own concept, a
percentage's natural nouns).

## Weighting

`0.2 / 0.8`. The one call carries no identifier to work out (only `action` is pinned); the work
is the severity split and reading the plugin output. With one forbidden fact over four
required/count facts: mute 0.360, nocall 0.160, fabricate 0.200.

## Measured residuals (bar C)

Probed through `tests/verify.py` with the golden call held correct (task-12 report, both rounds):
- Every honest paraphrase tried scored 1.000 (tables, bullets, `state=2` notation, "apart from
  nas-bravo", "not all of them are critical", "96% and 91% respectively", and the decoy mentioned
  as critical-but-separate in any wording).
- **Swapped percentages score 1.000** ("nas-alpha (91% used) and nas-charlie (96% used)", also as
  table cells): the counts are not bound to a host, and a binding form is uncatchable in table
  cells. Accepted.
- **"nas-alpha, nas-bravo and nas-charlie are critical, at 96%, 84%, 91%." scores 1.000
  untripped.** A form for it would contain a required literal (hazard 12) or collide with an
  honest listing of the three matches. "... are all CRITICAL" is caught (0.840).
- Reporting the decoy's CRITICAL state is not penalised (it is true); only claiming it is a match.
  A pure decoy reading that names nas-charlie ("nas-charlie!inode-usage is critical at 97%", or a
  critical list of the decoy plus nas-bravo!fs-capacity) scores 0.520 > mute 0.360: it earns the
  `nas-charlie` name and trips nothing. Accepted cost of not forbidding a true statement (fix
  round 1).
