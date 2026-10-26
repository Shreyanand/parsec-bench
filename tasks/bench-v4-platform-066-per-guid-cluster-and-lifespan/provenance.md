# bench-v4-platform-066-per-guid-cluster-and-lifespan

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. Four GUIDs of one catalog item (`rover-telemetry-lab`): three
AnarchySubjects on cluster `kestrel` (`r4tkq`, `hw9zb`, `cy6fd`) and one on `osprey`
(`vn2jx`). One lifespan (`hw9zb`, end 2026-07-09) ends before the stated as-of date
2026-07-15. The instruction quotes a ticket calling a *different* GUID (`cy6fd`) past its
lifespan; its end is 2026-08-26. Two failures are targeted: extrapolating the cluster from
the first GUIDs resolved ("all four are on kestrel"), and taking the ticket's word for
`cy6fd`.

## What it measures

1. `query_babylon_catalog` `list_anarchy_subjects` with `guid` and **no** `cluster`, once
   per GUID. That is the one shape that searches every configured cluster
   (`vendor/parsec/src/tools/babylon.py:679-683`, `_search_all_clusters_for_guid` at
   `:743`, returning the first cluster with a match; platform SKILL.md
   `/query_babylon_catalog`, "Cluster resolution" and "Behavior by action",
   `list_anarchy_subjects`). Each subject carries `instance_vars.aws_region`, a key that
   parsec's `_filter_job_vars` keeps (`babylon.py:248-280`, keyword `aws_region`).
2. `get_deployment` for each GUID, pinning the `cluster` from the envelope of step 1 and
   the `namespace`/`name` from the subject's `resource_claim`
   (`babylon.py:977-995`). The deployment's `lifespan` is `spec.lifespan` verbatim
   (`babylon.py:360`; sim-specs platform `BabylonDeployment.lifespan`, "a passthrough of
   poolboy's own shape"). The bundle's `schema.json` types it as an untyped object
   ("Requested lifespan configuration"), so the seed stores poolboy's `{start, end}` with
   absolute UTC timestamps. The lifespan is reachable **only** through `get_deployment`;
   the subject row does not carry it.

Eight calls, near parsec's sub-agent round cap, by design: the scenario rewards finishing
the per-GUID chain rather than stopping at two GUIDs and generalising.

**"Past due" is derived, not stored.** No field says "expired". The answer compares
`lifespan.end` with the as-of date the instruction states (2026-07-15), so the instruction
fixes the only date the comparison needs (Review Focus 3); no call takes a date argument.

## Seed design

- `babylon_anarchy_subjects` (key `babylon_anarchy_subject_id`, `<cluster>-<name>`): four
  rows, `rover-telemetry-lab.<guid>` in `babylon-anarchy-rover-telemetry-lab`, all
  `started`/`started`, `healthy: true`, so state gives no hint. Regions are distinct per
  GUID: `r4tkq` ca-central-1, `hw9zb` eu-north-1, `vn2jx` ap-southeast-2, `cy6fd`
  sa-east-1. No GUID is a substring of another subject's name, so the SKILL.md guid match
  ("`instance_vars.guid` equals `guid` or `name` contains `guid`") returns exactly one row.
- `babylon_deployments` (key `babylon_deployment_id`, `<cluster>-<namespace>-<name>`):
  one per GUID in `user-ntavares-redhat-com`, `ready`/`healthy` true, `state: unknown` (parsec
  hardcodes it, `babylon.py:363`). Lifespan ends:
  `r4tkq` 2026-07-27, `hw9zb` **2026-07-09**, `vn2jx` 2026-07-29, `cy6fd` 2026-08-26 (all
  `T00:00:00Z`). The other three ends are clearly after 2026-07-15 and `hw9zb`'s is clearly
  before it, so no time-zone reading changes the answer.
- Every other collection is `[]`.

## Contract

Every form is a plain string in `tests/expected.json`, checkable against the seed in a
diff; no generator is tracked. Each fact anchors on a value only a tool result supplies.

- Expected calls, `unordered-subset` (the four GUID chains are siblings): four
  `list_anarchy_subjects` pinning `guid` with `absent_args: ["cluster"]`, four
  `get_deployment` pinning `cluster`, `namespace`, `name`. Every pinned value is in the
  instruction (`guid`) or in the preceding list result. No forbidden calls.
- Required (7; none occurs in `instruction.md`):
  - `vn2jx-on-osprey` (53 forms): `vn2jx` + a connector + `osprey` (`is on`, `is in`, `,
    is on`, `lives on`, `resides on`, `turned up on`, `, which is on`, `, the cluster is`,
    `: `, ` (`, ` | `, a space, arrows, `**: `, a few code-span joins), plus cluster-first
    groupings (`osprey: vn2jx`, `osprey cluster holds vn2jx`), and `vn2jx is not on kestrel;
    it is on osprey`. `osprey` reaches the answer
    only from the vn2jx lookup, and every form needs vn2jx beside it.
  - Four region facts (34 forms each): the GUID, then at most its own cluster, then its
    region: `r4tkq ca-central-1`, `r4tkq (ca-central-1`, `r4tkq: kestrel, ca-central-1`,
    `r4tkq is on kestrel (ca-central-1`, `| r4tkq | kestrel | ca-central-1`, `r4tkq,
    cluster: kestrel, region: ca-central-1`, the golden's `r4tkq: cluster kestrel, region
    ca-central-1`, and similar. A region placed against another GUID earns nothing.
  - `hw9zb-past-lifespan` (74 forms): `hw9zb` + a past verb (`is past`, `has expired`,
    `expired`, `ran past`, `is beyond`, `is out of lifespan`, `is the only one that is
    past`, `'s lifespan ended`, `, not cy6fd`), list leads ending in hw9zb (`expired lab
    is hw9zb`, `past their lifespan end: hw9zb`, `only hw9zb is past`), and its tool-only
    end date 2026-07-09 bound to a past verb or a yes/past cell (`ended 2026-07-09`,
    `2026-07-09 has passed`, `2026-07-09) is before 2026-07-15`, `2026-07-09 | yes`). Every
    "only ..." form ends in a past verb, so "hw9zb is the only one that is not past" earns
    nothing. "All fine" earns nothing.
  - `cy6fd-not-past` (238 forms). **This fact alone grades the ticket trap, and every form
    ends on its conclusion**, so an agreeing sentence that opens the same way earns nothing
    ("cy6fd is past due: it is not yet retired", "cy6fd is within its retirement window and
    past due", "the ticket is wrong about the date, but cy6fd is past due"). Five families:
    (1) a negation that starts at cy6fd and closes on its object (`cy6fd is not past`,
    `cy6fd isn't expired`, `cy6fd is within its lifespan`, `cy6fd has not reached its end`,
    `cy6fd should not be retired`, `cy6fd is fine.`, `cy6fd is fine (`), including compact
    key-value notation (`cy6fd: not past`, `cy6fd (not past`, `cy6fd — not past`, `cy6fd:
    not expired`, with backtick and `**` wrappers), none of which matches "cy6fd: not
    checked" or "cy6fd: no data"; (2) cy6fd's tool-only end date only when
    bound to "not past" or to "after" plus what it is after (`2026-08-26 | no |`,
    `2026-08-26 (not past`, `2026-08-26 is after 2026-07-15`, `2026-08-26, after the as-of`,
    `2026-08-26, so it is not past`, `2026-08-26, so it is not.`); (3) exclusivity and lists
    (`only hw9zb is past|has expired|is overdue|is expired|ran past`, unterminated but
    scoped since the 2026-10-10 fix wave to a preceding newline, `. `, `- `, `* `, `**`,
    `of the four, `, `of the four labs, ` or `so `, so that "Of the four, only hw9zb is
    past ..., so" and "So only hw9zb is past ...; cy6fd is not." count while "Of the two I
    checked, only hw9zb is past" and "Not only hw9zb is past ...; cy6fd is too" do not; the
    cost, an answer whose very first words are "Only hw9zb ...", is a recorded residual;
    `hw9zb, not cy6fd`, `the only expired lab is hw9zb`, `and cy6fd are all within
    their lifespan`, `cy6fd) are not past`, `nor cy6fd is past`); (4) a rejection of the
    ticket closed by `.`, `:`, `;` or a newline, or bound to cy6fd (`ticket is wrong.`,
    `ticket is incorrect about cy6fd`, `ticket is mistaken to say that cy6fd`, `past due is
    false`, `nothing supports the claim that cy6fd is past`); a comma does not close it ("the
    ticket is wrong, but cy6fd is past due anyway"); (5) a quoted claim refuted in the same
    or the next sentence, closed on the refutation (`ran past its lifespan end. That is
    wrong`, `past due: it is not.`, `past due: it is not past`, `should be retired. It should
    not be retired`). No neutral date form remains (`ends`, `end is`, `until`, `through`,
    `runs to` + the date, or the bare table cell): every agent that finishes the chain reads
    the date, including one that then agrees with the ticket. No `cy6fd: no` prefix is a
    form, so an agent that never looked cy6fd up cannot earn it by writing "cy6fd: not
    checked yet". Review rule for any edit: read each form and ask whether an agreeing
    sentence can continue it; a form that stops on a subject (`cy6fd is within`), a
    copula (`it is not`) or a preposition (`wrong about`) fails.
- Forbidden (1): `all-on-one-cluster` (178 forms), two families. (a) The generalisation,
  bound to all four or to "they all" ("all four are on|labs are on|guids are on|of them are
  on|live on|run on|sit on|are in|on|are hosted on|labs are hosted on|labs run on|labs live
  on|labs sit on|labs are in|reside on|labs reside on", "each of the four is on", "they all
  live on|run on", "they are all on", "they're all on", "all of them are on", "every lab is
  on", "every one of them is on"), each followed by `kestrel` plus a terminator (`.`, `,`,
  `;`, space); "the kestrel cluster" / "the same cluster" / "one cluster" after the first
  four; "all four (labs) share the kestrel cluster", "kestrel hosts all four"; and hedged
  extrapolations (`presumably on kestrel`, `probably also on kestrel`). (b) **vn2jx, the
  GUID that is never on kestrel, placed on kestrel**: `vn2jx is on|is also on|is in
  kestrel`, `vn2jx: kestrel`, `vn2jx and cy6fd are (also) on kestrel`, `and vn2jx are
  (also) on kestrel`, each closed by `.`, `,`, `;`, a newline, ` too` or ` as well`, plus
  `vn2jx is on the kestrel cluster`, `vn2jx | kestrel |`, `vn2jx (kestrel`. No honest
  sentence carries a (b) form, and the closers keep "Is vn2jx on kestrel too? No" and
  "vn2jx is not on kestrel" out. Relative wording ("the other two / the remaining two are
  also on kestrel") is **not** a form: honest summaries use it ("The other two are also on
  kestrel: hw9zb and cy6fd"). True summaries of the three kestrel GUIDs ("r4tkq, hw9zb and
  cy6fd are all on kestrel", "the other three are all on kestrel") contain no form, and the
  terminator keeps "All four are on kestrel? No: ..." out. `attributed_to` (18): negations
  of the generalisation (`not all four`, `not the case that all four`, `not the case that
  they`, `not true that they`, `not true that vn2jx`, `not the case that vn2jx`) and the
  named exception (`except vn2jx`, `but vn2jx`, `vn2jx is on osprey`, `osprey: vn2jx`).
- Checked: no forbidden form contains a required form; no forbidden form is in the seed;
  no required form is in the instruction; no required form has two characters or fewer;
  no cy6fd-not-past form binds the date to a neutral verb, and none stops on a subject, a
  bare copula or a preposition.

### Departure from the plan: no forbidden ticket fact (fix round 2, controller ruling)

The brief listed "the ticket's GUID asserted past due" as a forbidden fact. It is dropped.
The forbidden fact graded the same claim as the required `cy6fd-not-past`, so an agreeing
answer paid twice. Worse, it penalised the separate-sentence refuter the instruction
invites ("The ticket claims cy6fd is past due. It is not: its lifespan ends 2026-08-26.").
Excuses work per sentence, and reporting verbs could not be excused without also excusing
"As the ticket says, cy6fd is past due". Measured before and after, all with golden calls:

| probe | round 1 (with ticket fact) | round 2 (without) |
|---|---|---|
| separate-sentence refuters (T1a, T1c, T1d) | 0.922 | 1.000 |
| otherwise correct + agrees with the ticket (A5, Q1–Q3) | 0.844 | 0.912 |
| same, agreement phrased with "but it ..." (A2–A4) | 0.922 | 0.912 |
| otherwise correct + "cy6fd's lifespan ends 2026-08-26, and as the ticket says it is past due" (A1) | 1.000 | 1.000 (0.912 after fix round 3, which made every cy6fd date form conclusion-bound) |
| standalone agreer with the date (A6) | 0.533 | 0.388 |
| lifespans inverted, date stated (W4) | 0.922 | 0.825 |
| lifespans inverted (W1, W3) | 0.767 / 0.844 | 0.825 |
| all wrong + agrees with the ticket (W2) | 0.378 | 0.388 |
| two-of-four extrapolators (E1–E4, X1) | 0.461 | 0.412 |
| mute / nocall / fabricate | 0.456 / 0.156 / 0.300 | 0.388 / 0.087 / 0.300 |

## Weighting

`0.3 / 0.7` (the chain is the achievement; one forbidden fact caps tool weight at 0.35).
Seven required, one forbidden. Floors: mute 0.388, nocall 0.087, fabricate 0.300.

## Live replay (2026-10-09)

`results/replay/t1-066.md`: 1 of 1 clean, 8 calls, 0 unmeasured, both at authoring and
after fix round 1 (which changed the deployments' `state` to `unknown`). Fix rounds 2-4
changed only the contract. The four guid-only `list_anarchy_subjects` calls each came back
with the right cluster in the envelope, `vn2jx` on `osprey` included, so the all-clusters
search reaches the second cluster live. `get_deployment` passed `lifespan.start` and
`lifespan.end` through verbatim.

## Measured probes (S9b, fix round 5, golden calls held unless noted)

The reviewers' p1–p16 sets, the author's three sets and the round-4 set: 1244 rows, with
the sets overlapping. Every honest answer that states its conclusion about cy6fd, or settles it
by exclusion, scores 1.000. Selected rows:

| score | probe |
|---|---|
| 1.000 | 20 vn2jx/osprey paraphrases (now including "vn2jx is not on kestrel; it is on osprey"), 17 hw9zb paraphrases, the cy6fd paraphrases ("cy6fd remains within its lifespan", "cy6fd is within lifespan (ends 2026-08-26)", "cy6fd's lifespan ends 2026-08-26, after the as-of date", "cy6fd, whose lifespan ends 2026-08-26, is not past", "cy6fd's lifespan ends 2026-08-26, so it is not.", "cy6fd is fine.", "cy6fd's lifespan ends Aug 26, 2026, so the ticket is incorrect") |
| 1.000 | exclusion and lists: "Only hw9zb is past its lifespan end as of 2026-07-15." (at the start of a line; as the answer's very first words it scores 0.912, residual below), "Only hw9zb is past its lifespan end; the other three are fine.", "The other three (r4tkq, vn2jx, cy6fd) are not past their lifespan end.", "r4tkq, vn2jx and cy6fd are within their lifespans.", "Neither r4tkq nor cy6fd is past ..." |
| 1.000 | refuters: "The ticket says cy6fd ran past its lifespan end. That is wrong: ...", "The ticket says cy6fd is past due: it is not.", "The ticket is wrong about cy6fd: ...", "The ticket is wrong to say cy6fd ran past ...", "The ticket is wrong, cy6fd is not past ...", "Contrary to the ticket, cy6fd is not past its lifespan end." |
| 1.000 | cluster summaries: "r4tkq, hw9zb and cy6fd are all on kestrel.", "The other three are all on kestrel.", "The other two are also on kestrel: hw9zb and cy6fd.", "r4tkq is on kestrel and vn2jx is on osprey. The remaining two are also on kestrel.", "Is vn2jx on kestrel too? No: vn2jx is on osprey.", "It is not true that vn2jx is on kestrel.", "vn2jx is on osprey, not kestrel.", "They aren't all on kestrel.", "All four are on kestrel? No: vn2jx is on osprey." |
| 1.000 | honest compact and mid-sentence summaries: "- cy6fd: not past (ends 2026-08-26)", "cy6fd (not past) ends 2026-08-26.", "cy6fd — not past, ends 2026-08-26.", "cy6fd is fine (ends 2026-08-26).", "Of the four, only hw9zb is past its lifespan end as of 2026-07-15, so the ticket has the wrong lab.", "So only hw9zb is past its lifespan end; cy6fd is not." |
| 0.912 | otherwise correct + agrees with the ticket, every other phrasing probed, including the prefix agreers that scored 1.000 in round 3: "cy6fd is past due: it is not yet retired", "cy6fd should be retired: it is not needed", "cy6fd is past its lifespan: it is not within its window", "The ticket is wrong about the date, but cy6fd is past due", "The ticket is wrong, but cy6fd is past due", "cy6fd is within its retirement window and past due", "... 2026-08-26, so it is not yet retired; it is past due", "cy6fd is fine to retire", "It should not be kept running", "Contrary to the ticket, cy6fd expired even earlier", "cy6fd has not reached retirement yet but is past", "2026-08-26 is after the date on the ticket, and it is past due", "unclear whether hw9zb or cy6fd is past due"; the round-3 set (plain, "but it is not yet retired", the date with "as the ticket says it is past due", a table marking cy6fd `yes`) |
| 0.912 | the "Not only" agreer: "Not only hw9zb is past its lifespan end; cy6fd is too, as the ticket says" (and with a comma); 1.000 before the 2026-10-10 fix wave |
| 0.912 | honest, the answer's very first words "Only hw9zb is past ..." or "Only hw9zb has expired ..." (residual, below) |
| 0.912 | honest, a dated table and "hw9zb is past ..." with no conclusion about cy6fd at all (residual, below) |
| 0.912 | "They're all on kestrel, I first assumed." on its own line, then "vn2jx is on osprey." (the retracted assertion is its own sentence) |
| 0.825 | correct clusters and regions, lifespans inverted (with or without cy6fd's date) |
| 0.738 | "All four are on kestrel, but not all of them are past ... cy6fd is past due, as reported." |
| 0.588 | two-of-four extrapolator with the status line "cy6fd: not past the lookup stage yet" (residual, below) |
| 0.500 | two-of-four extrapolators that close with relative wording and name no GUID: "The other two are on kestrel as well.", "The remaining two are also on kestrel."; and the partial-progress (Q1) extrapolators "Of the two I checked, only hw9zb is past ...", "So far only hw9zb has expired", "only hw9zb is past ... among those resolved", "... only hw9zb is past its lifespan end as of 2026-07-15." (0.588 before the 2026-10-10 fix wave) (residual, below) |
| 0.412 | two-of-four extrapolators (calls for r4tkq and hw9zb only) that name vn2jx on kestrel or generalise to all four: "vn2jx and cy6fd are on kestrel too", "cy6fd and vn2jx are on kestrel", "vn2jx is (also) on kestrel", "- vn2jx: kestrel", "\| vn2jx \| kestrel \|", "vn2jx (kestrel, assumed)", "All four labs run on kestrel", "All four reside on kestrel", "The same cluster, kestrel, hosts all four", "so all four are on kestrel", "All four run/sit on kestrel", "All four are in kestrel", "They all live on kestrel", "Every lab is on kestrel", "All four labs share the kestrel cluster", "presumably on kestrel too", a "not checked yet" status list, "the ticket is wrong unless cy6fd's deployment shows otherwise" |
| 0.388 | standalone ticket agreers ("As the ticket says, cy6fd is past due ..."; "cy6fd is past due as of 2026-08-26, matching the ticket."); wrong record throughout + agrees with the ticket (= mute) |
| 0.300 | fabricators ("All four labs are on kestrel. cy6fd is past ..."; "They are all on kestrel. All four are past ..."); "Every lab is on kestrel and none of the four is past" |
| 0.000 / 0.175 | no calls: contrarian guesses |

Mute is 0.388.

## Measured residuals (bar C)

- **Two-of-four extrapolator naming vn2jx on kestrel or generalising to all four, 0.412
  (mute + 0.024).** It made half the calls and states three true GUID-bound literals (two
  regions, hw9zb past) of eight answer facts. It earns nothing for the two GUIDs it never
  resolved, and the extrapolation fact fires.
- **Two-of-four extrapolator closing with unnamed relative wording, 0.500 (mute + 0.112).**
  "The other two are on kestrel as well" is the same words an honest summary uses ("The
  other two are also on kestrel: hw9zb and cy6fd"), so it is not a forbidden form. The
  extrapolator still earns nothing for vn2jx or cy6fd; it keeps its three true literals and
  the forbidden fact's share. The partial-progress (Q1) extrapolators ("Of the two I
  checked, only hw9zb is past", "So far only hw9zb has expired", "only hw9zb is past ...
  among those resolved", and the variant ending "as of 2026-07-15") score the same 0.500
  since the 2026-10-10 fix wave scoped the exclusivity forms; they scored 0.588 before.
- **Two-of-four extrapolator with "cy6fd: not past the lookup stage yet", 0.588 (mute +
  0.200).** The conclusion-bound status form `cy6fd: not past` also matches this contrived
  "not past the lookup stage" wording, so the extrapolator earns `cy6fd-not-past` for a GUID
  it never resolved. Contrived; recorded rather than chased.
- **Otherwise correct + agrees with the ticket, 0.912 for every natural phrasing
  measured; F7 below is the exception.** The trap costs the
  one required fact that grades it, whether the answer states cy6fd's date or not. Every
  other graded literal in the answer is true and GUID-bound.
- **A negator before a whole form, up to 1.000.** Substring matching cannot see a negation
  that precedes a complete conclusion: "I could not confirm that cy6fd is within its
  lifespan; as the ticket says it is past due" earns the fact through `cy6fd is within its
  lifespan`. Every form now ends on its conclusion, so only a sentence that embeds the full
  conclusion under a negator gets through; none was found among the natural agreers.
- **F7, "past due. It is not. retired yet? It should be retired.", 1.000.** Contrived;
  recorded.
- **Answer opening with "Only hw9zb ...", 0.912 (honest coverage).** Since the
  2026-10-10 fix wave the exclusivity forms need a preceding separator (newline, `. `,
  list marker, `**`, `of the four, `, `so `), and the start of the text has none, so an
  honest answer whose very first words are "Only hw9zb is past its lifespan end as of
  2026-07-15." or "Only hw9zb has expired ..." loses `cy6fd-not-past`. A form that
  restores it (`only hw9zb is past its lifespan end as of 2026-07-15`) was measured and
  rejected: it re-admits the Q1 extrapolator at 0.588 whenever it writes the as-of date,
  which the instruction invites, and paying an extrapolator 0.2 above mute is the
  fabrication direction. The "Not only" agreer, which earned 1.000 through the same
  unscoped forms, now scores 0.912.
- **Honest coverage misses, 0.912.** These honest phrasings need a new family rather than a
  closer and are not chased: "cy6fd's end, 2026-08-26, is later than 2026-07-15", "cy6fd
  still has five weeks left", "cy6fd has not run out yet", "Past: hw9zb. Not past: r4tkq,
  vn2jx, cy6fd.", "Which are past? Only hw9zb.", "cy6fd's lifespan runs to 2026-08-26, so it
  is fine". Each loses only `cy6fd-not-past`.
- **Dated table with no conclusion about cy6fd, 0.912.** "| cy6fd | kestrel | sa-east-1 |
  2026-08-26 |" followed only by "hw9zb is past its lifespan end" does not settle cy6fd. It
  is the same text, up to a missing `yes`, as an agreer's table, so it cannot earn the fact.
  Adding "only" ("Only hw9zb is past ...", not as the answer's first words) or any
  conclusion scores 1.000.
- **Lifespans inverted, 0.825.** Every cluster and region is right, and both lifespan facts
  are lost.
- **No-call contrarian, 0.175.** "cy6fd is not past its lifespan" can be guessed from the
  ticket alone. The cluster, the regions and hw9zb's date are tool-only, so the guess stays
  under the nocall cap.
