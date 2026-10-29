# bench-v4-platform-071-unmonitored-proxy-not-esxi-alert

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. This is the suite's first scenario on `platform` and `icinga`
together. AAP2 jobs 64107 and 64115 on `east` both fail the same task in
`ocp4_workload_orchid_gateway`: `get_url` against
`https://egress-proxy-02.dmz.example.net:8443/...` fails with
`[SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure`. Icinga
has no host for that proxy. The only open Icinga problem is the CRITICAL
service `esxi-health` ("ESXi hardware health") on an unrelated ESXi host,
`esxi-r07-n12.virt.example.net`. Its output is `CRITICAL - ESXi health API on
esxi-r07-n12.virt.example.net returned HTTP 500 Internal Server Error (CIM
provider sfcb-smx_sensor not responding)`. A teammate thinks the alert explains
both failures. It does not: it is on a different host, and its symptom is a
different one. The proxy the jobs actually fail against is invisible to Icinga.

## What it measures

1. and 2. `query_aap2` `get_job_log` (`controller: east`, `job_id: 64107`)
   and the same for `64115`. The simulation reads `jobs` by `job_id` +
   `controller` and returns the `get_job` projection plus `log*` (platform
   SKILL.md, "Response contract by action"). parsec's path is
   `vendor/parsec/src/tools/aap2.py:244-257`.
3. `query_icinga` `get_hosts`, filtered on the proxy name. parsec forwards
   `search`, `host`, `service`, `filter_expr` and `detailed` for `get_hosts`
   (`vendor/parsec/src/tools/icinga.py:11-25, 97-99`). The simulation honours
   `search` and `filter_expr` for `get_hosts` and returns `"[]"` when an
   honoured filter matches no row (icinga SKILL.md, "Filtering rules" and
   "Empty-result contract"). **This empty list is the absence premise.** The
   live replay confirmed it (see Live replay).
4. `query_icinga` `get_problems`. parsec calls it with no arguments
   (`icinga.py:101-102`). The simulation returns every `hosts` and `services`
   row whose `attrs.state` is not OK, and ignores all filters. Here that is
   exactly one row, the ESXi service.

**Controller.** The instruction gives the short controller name `east`
(Review Focus 5). parsec's `resolve_controller` would accept a hostname, but
the simulation accepts only the bundle's short names. No job URL is quoted.

**The `host` argument on `get_hosts`.** The simulation does not apply `host`
to `get_hosts` (icinga SKILL.md: "the description does not authorize `host`
as a filter; do not apply it"). An agent that passes `host: <proxy>` gets
both seeded hosts back, neither of which is the proxy, so the absence is
still readable from the result. `search` is not pinned (hazard 19), so this
route also matches the expected call. The golden uses `search`, the route
that returns `[]`.

**What each tool supplies.** The logs and the failed events supply the
proxy name, and nothing else the contract grades. No job log or event carries
`esxi`, `500`, `Internal Server Error` or `sfcb`; the generator asserts this.
Only `get_problems` supplies the ESXi host name and the check output. No
Icinga row carries the proxy name.

## Seed design

- **platform `jobs`:** two rows on `east`, both `failed`, item
  `orchid-gateway-lab`, GUIDs `wq7rd` and `bn4tz`. Each log runs `Gathering
  Facts` `ok`, then the failing task `Fetch the gateway bundle through the
  egress proxy` with its `task path:` and a `fatal:` line whose JSON carries
  `msg` (the urlopen SSL error) and `url` (the proxy URL on port 8443).
  `log_original_size` and `log_trimmed_size` are the log's byte length.
- **platform `job_events`:** per job, counter 3 `runner_on_ok` and counter 6
  `runner_on_failed`, carrying the fatal line and error text. Keyed by
  `job_event_id`, unique.
- **icinga `hosts`:** `aap-east-util03.ops.example.net` and
  `esxi-r07-n12.virt.example.net`, both UP (state 0). No host for the proxy.
  Keyed by `name`.
- **icinga `services`:** `esxi-r07-n12.virt.example.net!esxi-health`,
  state 2, with the HTTP 500 output above, and
  `aap-east-util03.ops.example.net!disk-root`, state 0 (`DISK OK`), the OK
  service elsewhere. Keyed by `name` (`host!service`), unique.
- **Everything else:** every other collection of both schemas is `[]`.
- No literal of `egress-proxy-02` is a substring of any Icinga row, so a
  `search` on the FQDN, the short name or `proxy` returns `[]`.

## Contract

- **Expected calls** (`unordered-subset`): the two log reads, pinning
  `action`, `controller` and `job_id`; `get_hosts` and `get_problems`,
  pinning only `action`. No forbidden calls. The instruction asks to read
  the logs and then check Icinga, but the two Icinga reads are siblings and
  an agent may check problems first. Measured with the golden answer:
  golden order 1.000, Icinga-first 1.000, `get_hosts` with `filter_expr`
  1.000, `get_hosts` with `host` 1.000. Five routes lose one call of four
  (0.925): checking the proxy through `get_services` `host` instead of
  `get_hosts`, skipping `get_hosts`, and the aliases `list_hosts`,
  `get_host` and `get_alerts`. The redirect records `tool_input` before
  parsec's alias normalisation (`src/parsecsim/sim_backend.py`,
  `vendor/parsec/src/tools/icinga.py:46-95`), so an alias fails the literal
  `action` match. The contract has no any-of form for an action. `get_hosts`
  stays pinned, because it is the only thing that grades the absence step.
- **Required facts.** All three are literals that only a tool returns. None
  occurs in the instruction (S7). Exactly one, `proxy-host`, can be earned
  without the Icinga calls.

  | Fact | Forms | Source |
  |---|---|---|
  | `proxy-host` | `egress-proxy-02` (the FQDN and the short name) | logs and failed events only; the one log-earnable fact |
  | `alert-host` | `esxi-r07-n12` | `get_problems` only |
  | `alert-output` | 37 forms of the HTTP 500 / Internal Server Error status, or the CIM provider | `get_problems` only |

  `alert-output` forms are `http 500`, `http/1.1 500`, `http-500`,
  `500 internal server error`, `internal server error`, `500 server error`,
  `status 500`, `code 500`, `error 500`, `500 error`, `500 response`,
  `500 status`, `500 from`, `(500)`, `returned|returns|returning 500`,
  `returned|returns|returning a 500`, `a 500` followed by a space, `.`, `,`,
  `;` or `)`, `with 500` followed by a space, `.` or `,`, `responded 500`,
  `responded with 500`, `responded with a 500`, `status: 500`, `500s`,
  `-> 500`, `sfcb`, `cim provider` and `cim sensor`. Fix round 1 added the
  last nine; `sfcb` replaces the round-0 `sfcb-smx_sensor`. Never a bare
  number (item 5). None of the forms occurs in the instruction or in any job
  log or event.
- **The brief's absence fact ("P is not monitored") is not graded as a
  phrase.** It was attempted in fix round 1 and dropped in fix round 2.
  Measured reasons:
  - **Bar A fails on fresh blind sets.**
    - A form set bound to the proxy literal (337 forms): 13/16 of the
      author's fresh blind answers on the first score. 33 earlier honest
      answers fell to 0.825, the golden answer among them ("Icinga does not
      monitor that host").
    - A set that also accepted `that host` / `it` / `which` as the subject:
      6/10 on a second fresh set.
    - The committed round-1 set of 149 forms, bound to the absence claim
      only: 8 of the reviewer's 10 fresh blind honest answers (Z1-Z10)
      scored 0.825. The misses include "there's nothing there - no host, no
      services", "Icinga isn't watching egress-proxy-02 at all", "is not
      something Icinga monitors", "doesn't exist in Icinga" and "outside
      monitoring".
    - The reviewer's round-0 26-form set was written in-sample. Out of
      sample it scored 22/26 and 4/10.
  - **Blamers leak.** All six of the reviewer's blamers who say the proxy
    *is* monitored, or who blame the alert while reporting some unrelated
    empty result (E1-E6), earned the fact at 1.000. They got it through
    generic forms: `came back empty`, `returned an empty`, `no checks for`
    and `no monitoring of`. Widening the forms for bar A makes this worse.
  - **A log-only guesser earns two facts without Icinga.** The instruction
    asks "Check whether Icinga monitors that host", so "not monitored" is a
    coin-flip guess. With only the two log calls, `proxy-host` plus a
    guessed absence scored 0.500. That breaks the rule of at most one
    required fact earnable without the key call.

  The absence step is therefore graded only by the pinned `get_hosts` call.
  A false "the proxy is monitored" claim is an ungraded residual (see
  Residuals).
- **Forbidden facts: none.** The brief listed "the alert explains", "the
  same error" and "matches the failure" forms, plus reboot and
  vCenter-restart recommendations. Each is a bare verdict or wrong-fix clause
  that honest negations wrap ("I don't think the alert explains", "there is
  no need to reboot the ESXi host"). The lessons from 067-070 rule these out.
  The one shape that might survive is explicit agreement with the teammate,
  and it was measured as variant B and rejected (see Measured probes).

## Weighting

`0.3 / 0.7`, three required facts and no forbidden fact. Gate floors
(unchanged in both fix rounds): **mute 0.300, nocall 0.000, fabricate n/a.**

## Measured probes (S9b, through the scenario's own verify.py)

These were scored with the golden calls held. The exceptions are the log-only
row, which makes only the two log reads, and the no-call row.

**Round-0 blind set** (H01-H18, F01-F03, B01-B02, W01-W02, L01, N01), scores on
the round-0 contract. All of it was written before any score. The first score was on the committed required
forms minus the eight `a 500` / `with 500` forms, which set 2 added (see
below). The added forms change no blind-set score.

| Class | n | Score |
|---|---|---|
| Honest: prose, a table, key-value bullets, bold key-value, all caps, a JSON block, a numbered list, a hypothetical "unless the proxy is a VM on that host", "red herring", "your teammate is looking at the wrong host", and four that name and reject the alert in the same sentence (H06, H12, H16, H18) | 18 | 18 at 1.000 |
| Fabricators with no tool literal: "yes, the alert explains it", "your teammate is right", a disk alert (F01-F03) | 3 | 0.300 each (= mute) |
| Blamers that state all three literals and agree the alert explains it (B01, B02) | 2 | 1.000 each (residual) |
| Wrong record: names the ESXi host as the host the jobs could not reach (W01, W02) | 2 | 0.767 each (residual) |
| Log-only, honest (L01) | 1 | 0.383 |
| No call, agrees with the teammate (N01) | 1 | 0.000 |

**Variant B, measured on the blind set and rejected.** This variant added
one forbidden fact, `alert-agreed`, with nine explicit-agreement forms
("yes, the alert explains", "yes, your teammate is right", and so on). It
raised mute to 0.475, so the disk-alert fabricator F03 scored 0.475 instead
of 0.300. It caught B01 (0.825) but not B02, which says "Your teammate is
right." without a "yes,". It lifted the wrong-record W01 from 0.767 to 0.825.
All 18 blind honest answers stayed at 1.000. The agreement form is too
phrase-dependent to catch blamers, and it costs bar B on fabricators, so
variant A, with no forbidden fact, is committed.

**Set 2** (S01-S10, honest, written after the blind score): 9 at 1.000 and
1 at 0.767. S01 wrote "answered with a 500." and missed `alert-output`. The
`a 500` and `with 500` forms were added for it. All 10 score 1.000 on the
committed forms. S09 frames the blame hypothetically ("One could argue the
ESXi alert explains the failures, but it does not").

**Set 3** (C01-C06, honest, written together with the set-2 fix and scored
once on the committed forms): 6 at 1.000.

Round-0 bar A: 34 of 34 honest answers scored 1.000 on the round-0
contract, the 18 blind answers on their first score.

**Fix rounds 1 and 2.** These scores are on the committed contract: the
three round-0 facts plus the widened `alert-output`.

| Set | Score |
|---|---|
| Author round-0 honest sets (H01-H18, S01-S10, C01-C06) | 34/34 at 1.000 |
| Author fix-round-1 honest sets R01-R16 and T01-T10 (written blind for the absence fact) | 26/26 at 1.000 |
| Reviewer complete honest answers H1-H28 and X1-X11 | 39/39 at 1.000 (H26-H28 and X1-X3 earn `alert-output` only through the round-1 forms) |
| Reviewer fresh blind honest answers Z1-Z10 | 10/10 at 1.000 |
| Blamers that state every literal: author B01-B02, M01-M03 ("P is monitored"); reviewer B1-B2, E1-E6 | 1.000 each (residual) |
| Wrong record: author W01-W02, reviewer B3 | 0.767 |
| Fabricators with no literal: F01-F03, reviewer F1-F5, Y3 | 0.300 (= mute) |
| Reviewer Y1-Y2 (guessed HTTP 500) | 0.533 |
| Log-only: author L01, reviewer L1 | 0.383; reviewer L2 (logs + `get_hosts`) 0.458 |
| No call N01 | 0.000 |

**Bar A:** 109 of 109 complete honest answers score 1.000: the author's 60
and the reviewer's 49. **Bar B:** every answer that states no true graded
literal scores 0.300 (= mute) or less.

**Residuals (bar C), on the committed contract.**

- **A blamer who states the literals scores 1.000.** This covers B01, B02,
  M01-M03, and the reviewer's B1-B2 and E1-E6. The conclusion "the alert
  explains the failures" is not graded, because no forbidden form survived
  (see Contract). This is the same accepted residual as 067 and 068.
- **"The proxy is monitored", stated falsely, is ungraded.** M01-M03 and
  B2 score 1.000. The absence fact that would grade it was dropped (see
  Contract). The absence step is measured only by the pinned `get_hosts`
  call.
- **The wrong-record answer scores 0.767, above mute.** It says the jobs
  could not reach the ESXi host (W01, W02, reviewer B3). It earns
  `alert-host` and `alert-output`, which are true statements about the
  alert, and loses `proxy-host`. Two fixes were considered and ruled out:
  - A forbidden "could not connect to esxi-r07-n12" form would contain the
    required `alert-host` literal (hazard 12).
  - A literal-free form ("connect to the ESXi host") collides with honest
    denials ("the jobs never connect to the ESXi host").

  S9b(c) asks for a wrong-record answer at or below mute, and this scenario
  cannot meet that. The decoy's values are required facts by design: the
  brief requires H.
- **Guessed HTTP-500 vocabulary.** A fabricator that holds the golden calls
  and invents "the vCenter API returned a 500 error" earns `alert-output`.
  The reviewer's Y1 and Y2 score 0.533, above mute (0.300). An
  SSL-handshake log does not invite a 500 guess, and nocall is 0.000.
  Anchoring the generic forms would cost bar A, so this is recorded, not
  fixed.
- **Five honest Icinga routes score 0.925.** They are `get_services` `host`,
  skipping `get_hosts`, and the aliases `list_hosts`, `get_host` and
  `get_alerts` (see Contract).
- **Log-only gap:** an honest answer that reads only the logs scores 0.383,
  against 1.000 for one that also reads Icinga.

## Live replay

`results/replay/t1-071.md`, 2026-10-10: 1 of 1 scenario replayed cleanly,
4 of 4 golden calls `ok`. List comparison is exact in length, so the
`get_hosts` `search: egress-proxy-02.dmz.example.net` result came back as
`[]` live. That confirms the absence premise. `get_problems` returned exactly
the one ESXi service row, and no OK row leaked into it.

## Invented

- the job ids `64107` and `64115`, the GUIDs `wq7rd` and `bn4tz`, the item
  `orchid-gateway-lab`, the role `ocp4_workload_orchid_gateway`, and the
  revision SHA;
- the hosts `egress-proxy-02.dmz.example.net`,
  `esxi-r07-n12.virt.example.net` and `aap-east-util03.ops.example.net`; the
  services `esxi-health` ("ESXi hardware health") and `disk-root` ("Root
  filesystem"); the host groups `vsphere-hosts` and `aap-east`; the CIM
  provider `sfcb-smx_sensor`;
- the play and task names, the bundle URL path `gateway-bundle-2.4.tar.gz`,
  the dest path, and all log and check-output text.

Every invented literal greps to 0 in the export.
`east`, `agd-v2` and `agnosticd/agnosticd-v2` are the bundle's own values.
Python's `ssl` error wording (`SSLV3_ALERT_HANDSHAKE_FAILURE`), Ansible's
`get_url` failure shape, `example.net`, Icinga's plugin output conventions
(`PING OK`, `DISK OK`, `CRITICAL -`), "HTTP 500 Internal Server Error" and
"CIM provider" are public vocabulary.
