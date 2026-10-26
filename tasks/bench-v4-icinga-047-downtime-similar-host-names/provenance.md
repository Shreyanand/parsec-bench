# bench-v4-icinga-047-downtime-similar-host-names

Idea from bench-h4_Oct5 047 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. Host `checkout-web` and host `checkout-web-canary` each carry one scheduled
downtime. The asked-about host's name is a prefix of the other's, so a host-filtered
`get_downtimes` may return both. Reporting the canary's author, reason or window as
`checkout-web`'s -- or saying `checkout-web` has two downtimes -- is the trap.

## What it measures

One read, `query_icinga {action: get_downtimes, host: checkout-web}`. The agent must attribute
each returned downtime by its own `attrs.host_name`.

- parsec: `query_icinga` (`vendor/parsec/src/tools/icinga.py:65-110`) builds `filter_args` from
  `host`/`service` only, each when truthy, and returns the Icinga MCP sidecar's response verbatim
  (`icinga.py:104-110`). parsec implements no matching itself.
- Bundle: `harness-skills/parsec-icinga/SKILL.md` `/query_icinga POST`: `get_downtimes` reads only
  `downtimes` and "filter `downtimes` by `host` when provided" (SKILL.md:194-199); ignores
  `search`/`filter_expr`/`detailed`; returns the JSON serialization of matching stored rows under
  `result`. **Whether that filter is exact or substring is not specified.** The batch's "fuzzy
  match" claim was about its own patched bundle, not ours.
- **Written to hold under either semantics.** Under exact matching only the checkout-web row
  returns and the scenario is a straight read; under substring matching both rows return, canary
  first (stored order). Every graded fact comes from the checkout-web row and shares no token with
  the canary row, so neither the canary row nor a full swap of its values can satisfy any required
  fact.
- **Golden result is authored for exact matching** (one row). Task 16's live replay decides: if
  the live simulation returns both rows, the golden result is updated to the two-row list (canary
  first) and the observed semantics recorded here. No contract change is needed in either case.

## Seed

`seeds/icinga.json`: two hosts (`checkout-web`, `checkout-web-canary`, both UP, `downtime_depth`
1), `comments` [], `services` [], two `downtimes` in this stored order:

| name | host_name | author | comment | window (UTC) |
|---|---|---|---|---|
| `checkout-web-canary!c05e…` | checkout-web-canary | obanerjee | Soak test of build 7.3.0 on the canary pool; … | 2026-12-02 08:00 -> 2026-12-04 08:00 |
| `checkout-web!7d2c…` | checkout-web | ikarlsson | Database failover rehearsal - checkout writes are paused … | 2026-11-14 13:00 -> 17:00 |

Authors, comment vocabulary, months and days are disjoint, so the required forms below cannot be
earned from the canary row. Both downtimes are host downtimes (`service_name` ""); epochs are
inside the bundle's numeric ranges, `end_time > start_time`.

## Contract

- Expected call: `query_icinga {action: get_downtimes, host: checkout-web}`; `host` is stated in
  the instruction. No forbidden calls, no `absent_args`.
- Required (all from the checkout-web row; none occurs in `instruction.md`):
  - `author`: `karlsson`.
  - `reason`: `failover` / `fail-over` / `fail over` / `rehearsal`.
  - `window`: the UTC date 2026-11-14 in ISO, slash, dot, US and day/month-name notations
    (including `fourteenth`), plus
    the raw `start_time`/`end_time` epochs. Both ends share the date, so the date grades the
    window; the canary's is 2-4 December.
- Forbidden `canary-downtime-on-checkout-web` (268 forms, generated): `checkout-web` /
  `checkout-web downtime` / `checkout-web's downtime` / `the downtime on|for checkout-web`
  followed by the canary's author (`(obanerjee`, `: obanerjee`, `| obanerjee`, `was scheduled|set|
  created|entered by obanerjee`, `by obanerjee`), its reason (`: soak`, `| soak`, `is (for) a
  soak`, `is down for a soak`, `is for build 7.3.0`, ...) or its December window (`: dec`, `runs
  from dec`, `from 2026-12-02`, `starts on 2 dec`, ...); plus merge claims (`checkout-web has
  two|2 (scheduled) downtimes`, `two downtimes on checkout-web:`/`.`, `both downtimes are on|belong
  to checkout-web.`, `obanerjee scheduled the checkout-web downtime`). Every form names
  `checkout-web` followed by a space, colon, pipe, bracket or full stop, so a **true** statement
  about `checkout-web-canary` (the name continues with a hyphen) never matches -- an honest answer
  may describe the canary's downtime in full. No form contains `canary` and none contains a
  required form (hazard 12); none occurs in the seed (hazard 14). Excuses: `not both`, `is wrong`,
  `incorrect`, `mistaken`, `not the case`, `downtimes?` (for "Does checkout-web have two
  downtimes? No"), `not two`, `not true`, `prefix`, `also matched`, `is on checkout-web-canary`.
  The last excuses an honest aside ("(obanerjee's soak test is on checkout-web-canary, not
  here)"); it would also excuse a swap sentence that happens to say the soak test is on the
  canary, which is an unlikely shape -- the recorded trade. No bare `canary` excuse.
  Fix round 1 added `checkout-web` followed by `** — `, `** – `, `** - `, `**: `, ` — `, ` – `,
  ` - `, `` `: ``, `` ` — ``, `` ` - `` or `, is ` and then `obanerjee` / `soak` / `dec` /
  `2026-12-02` (44 forms), for one-line double swaps; `checkout-web-canary** — ...` cannot match
  them.

S7: no required form occurs in `instruction.md`; no forbidden form occurs in the seed. Overlap with
the batch: no host, author, comment, timestamp, instruction fragment or form is shared. "scheduled
downtime" and the `-canary` suffix are forced by the mechanism (an Icinga downtime; two hosts whose
names are prefix-related). The batch's instruction warned about the canary host; this one does not,
so the agent is not told which row to drop, and the batch's `canary-excluded` fact (an echo of its
instruction) is gone.

## Weighting

`0.2 / 0.8`. The one call needs only the host the instruction gives; the work is attribution.
Three required, one forbidden: mute 0.400, nocall 0.200, fabricate 0.200.

## Measured residuals (bar C)

Probed through `tests/verify.py` with the golden call held correct (task-15 report): 16 honest
paraphrases -- tables with both hosts, bullets, an answer describing the canary row in full,
"checkout-web is not down for a soak", "Not both downtimes ... are on checkout-web", "Does
checkout-web have two downtimes? No", raw epochs, US/EU dates -- all 1.000. Full swaps (the
canary's author/reason/window under checkout-web, in prose, key-value, table) 0.200 tripped; a
heading-and-bullet *single* swap ("**checkout-web**" then "- Author: obanerjee" lines) and a pronoun
swap ("It was scheduled by obanerjee ...") 0.400 untripped, equal to mute because no required fact
is earned. Pure fabrications and "no downtime" 0.400.

- **Double swap in heading/newline blocks scores 1.000, untripped, and is unfixable**: "###
  checkout-web\n- Author: obanerjee ...\n### checkout-web-canary\n- Author: ikarlsson ..." gives
  each host the other's values. The verifier splits sentences on newlines, so no form spans the
  heading and its lines, and checkout-web's true values sit under the canary heading where only a
  `canary`-bearing form could catch them (excluded by brief). One-line double swaps (bold, dash,
  em dash, backtick, table, prose) score 0.800, tripped (fix round 1).
- **Honest collision, 0.800**: "Compared with checkout-web: soak testing happens on
  checkout-web-canary ..." trips `checkout-web: soak`. Kept: that colon form catches the natural
  key-value swap ("checkout-web: obanerjee, soak test ...").

- **Merges score 0.800, tripped**: "checkout-web has two downtimes: ... ikarlsson ... and ...
  obanerjee ..." states every true literal plus the false membership claim.
- **Partial swap 0.600, untripped**: "ikarlsson scheduled it, but the reason is a soak test ...,
  Dec 2 to Dec 4." A subject-free `the reason is a soak` cannot be forbidden: an honest sentence
  about the canary says exactly that.
