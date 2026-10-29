# bench-v4-icinga-048-comment-service-vs-host-scope

Idea from bench-h4_Oct5 048 (external, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. A host-scoped `get_comments` on `pay-gw-02` returns two comments, one per
service. The asked-about service, `queue-backlog`, has a comment with no ticket; the other,
`tls-cert-expiry`, carries the host's only ticket id, `OPSREQ-5417`. Putting that ticket on
`queue-backlog` -- or saying `tls-cert-expiry` has none -- is the trap.

## What it measures

One read, `query_icinga {action: get_comments, host: pay-gw-02}`. The agent must attribute each
returned comment by its own `attrs.service_name`, not by which service the question is about.

- parsec: `query_icinga` (`vendor/parsec/src/tools/icinga.py:65-110`) dispatches `get_comments`
  with only `host`/`service`, each when truthy (`icinga.py:104-110`); `list_comments` is an alias
  (`icinga.py:59`). The response is the Icinga MCP sidecar's, verbatim -- a passthrough.
- Bundle: `harness-skills/parsec-icinga/SKILL.md` `/query_icinga POST`: `get_comments` reads only
  `comments`, filters by `host` and `service` when provided, ignores `search`/`filter_expr`/
  `detailed`, and returns the JSON serialization of the matched stored rows under `result`, in
  stored order. Adding `service: queue-backlog` is a legitimate call shape, but it returns only
  the queue-backlog comment and so cannot answer the instruction's second half; nothing forbids it.
- Golden result shape: full stored rows (Icinga2 `name`/`type`/`attrs` envelope), as in siblings
  045/046.

## Seed

`seeds/icinga.json`: `downtimes` [], two hosts, three services (all WARNING, state 1), three
comments in this stored order:

| name | service_name | author | text |
|---|---|---|---|
| `pay-gw-02!tls-cert-expiry!5c0e…` | tls-cert-expiry | dvasquez | `OPSREQ-5417 - renewal is blocked until the CA change window opens. …` |
| `pay-gw-02!queue-backlog!a947…` | queue-backlog | mtanaka | `Backlog builds while the settlement batch runs and drains on its own …` |
| `ledger-db-01!replication-lag!e17d…` | replication-lag | dvasquez | `CHG-77310 - replica rebuild in progress; …` |

- The ticket comment is stored **first**, so an agent that reads "the" comment for the asked-about
  service off the top of the list picks the wrong one.
- The ticket id **opens** the tls-cert-expiry text, so an agent that copies that text onto
  queue-backlog leaves the ticket far from any tls-cert-expiry token (see the count below).
- The comment texts avoid the service-name tokens (`tls`, `cert`, `certificate`, `expiry`; and
  `queue` -- `backlog` is unavoidable in the backlog note) so proximity to them means the answer
  named the service, not that it quoted the text.
- The third comment is on another host (`ledger-db-01`, no substring relation to `pay-gw-02`, so
  it stays out under exact, substring or fuzzy host matching). It reaches only an agent that
  calls `get_comments` without `host`; its ticket uses a different prefix so it cannot satisfy any
  ticket form.
- Every comment's `service_name` names a seeded service on that same host; `entry_time`s are
  integers inside the bundle's range.

## Contract

- Expected call: `query_icinga {action: get_comments, host: pay-gw-02}`. `host` is stated in the
  instruction. No forbidden calls, no `absent_args`.
- Required:
  - `queue-backlog-note`: `settlement` -- the content of the asked-about comment. It occurs in no
    other seed row.
  - `queue-backlog-no-ticket` (derived): queue-backlog bound to a no-ticket predicate
    (`queue-backlog[ comment|'s comment|…] has no ticket / does not point to a / is not tracked /
    : no ticket / …`, `no ticket for queue-backlog`, `not queue-backlog`, `not on the
    queue-backlog`, `apart from tls-cert-expiry, no`, `only the tls-cert-expiry comment`, `ticket is on
    tls-cert-expiry`, `only ticket on the host`), plus
    pronoun and question-echo forms (`it does not point to a ticket`, `ticket? no`, `ticket:
    none`, `. no ticket`, `- no ticket`, `| none |`). The latter are unbound and accepted so an
    honest pronoun, bullet or table answer is not failed; that is the measured cost below. Bare
    `no ticket` / `has no ticket` are deliberately absent so the forbidden `tls-cert-expiry has no
    ticket` forms contain no required form (hazard 12). 658 forms, generated (652, plus six
    `and has/carries/gives/cites/mentions/references no ticket` added 2026-10-09 after an honest
    "... only explains the settlement batch and has no ticket" missed the fact).
  - `tls-cert-expiry-note` (added 2026-10-09): what the other comment says -- the certificate
    renewal is blocked until the CA change window opens. 68 forms: `renewal is blocked`/`renewal
    blocked`/`blocked renewal`, the `renewal is on hold|waits|pending|can't|cannot|stuck|delayed|
    deferred|currently blocked|still blocked` family, `can't/cannot be renewed`, `blocks (the)
    (certificate|cert) renewal`, `change window`, `ca window`, `ca change`, `certificate
    authority`, `blocked until the ca`, `waits/waiting on|for the ca`, the topic forms (`the
    certificate renewal`, `about the renewal`), and since fix round 1 the comment's instruction
    (`leave the warning`, `warning in place`, `keep the warning`, `not restart`, `don't restart`,
    `not be restarted`) and `blocked on the ca`, `renewing the certificate/cert is blocked`,
    `renewal has been blocked`. 87 forms. None occurs in another seed
    row, in the instruction, or inside a forbidden form (the forbidden content-swap forms carry a
    bare `renewal`, which no required form equals). Unbound: a full swap that moves this text onto
    queue-backlog earns it; the forbidden facts catch the swap instead.
  - `ticket-on-tls-cert-expiry` (count): 5417 within 30 tokens of `tls`/`cert`/`certs`/
    `certificate`/`expiry` or of the comment's author `dvasquez` (fix round 1; the first draft of
    this edit used 20 tokens plus content nouns, see the edit log). The pair-binding fact. `OPSREQ` and `5417` tokenize
    separately, so the digit guard accepts `OPSREQ-5417`. Was 14 tokens of the service tokens
    alone until 2026-10-09: once the instruction asks what the comment says, honest answers put
    that content between the service name and the ticket, and 5 of 16 new honest probes missed
    the fact at 14 tokens. Content words are deliberately not nouns: a content transfer that copies
    the tls text onto queue-backlog would earn the fact from them.
- Forbidden `ticket-misattributed` (628 forms; 358 before 2026-10-09): queue-backlog asserted to carry the
  ticket (`queue-backlog is tracked in`, `queue-backlog has a ticket`, `queue-backlog: opsreq`,
  `queue-backlog | opsreq`, `the queue-backlog comment points to a ticket`, `the ticket for
  queue-backlog is opsreq`, `opsreq-5417 is for/on/belongs to queue-backlog`), "both comments"
  carrying it, tls-cert-expiry asserted to have none (`tls-cert-expiry has no ticket`, `… does
  not point to a ticket`, `… is not tracked`), and the content swap (`queue-backlog: renewal`,
  `queue-backlog | renewal`, `tls-cert-expiry: backlog`, `tls-cert-expiry | backlog`), the swapped
  author (`queue-backlog (dvasquez`, `tls-cert-expiry (mtanaka`), `comment on/for queue-backlog
  references/points to/cites` + `opsreq`/`ticket`/`a ticket`, `yes, it points to` + the same
  objects, `so yes, it points to/references/cites` + objects, `so yes, it is tracked in`,
  `queue-backlog is tracked by` + objects, `queue-backlog has ticket opsreq`/`has ticket:`,
  `queue-backlog is tied to/is linked to opsreq`, `for queue-backlog, ticket opsreq`,
  `both comments ... reference/cite` + `opsreq`/`ticket`/`the same`, `two/all comments cite
  opsreq`, `queue-backlog -> opsreq`, `for
  queue-backlog the ticket is opsreq`, `every comment has a ticket`. With the
  required ticket fact a count, ticket-bearing forbidden forms are legal: none occurs in the seed
  (hazard 14) and none contains a required `any_of` form (hazard 12). Excuses (`attributed_to`):
  "but it isn't", "but it is not", "but that is wrong", "would be wrong", "is wrong", "mistaken",
  "incorrect", "not correct", "not the case", "not both", "not every", "not all comments" -- for an answer that names the wrong reading in order to reject it.
  2026-10-09 added 270 forms: a queue-backlog subject (`queue-backlog `, `queue-backlog comment `,
  `queue-backlog's comment/note `, `comment on/for (the) queue-backlog `, `note on queue-backlog `)
  with the verbs the fact lacked (`mentions`, `refers to`, `gives`, `carries`, `citing`,
  `pointing to`, `tied to`, `linked to`, ...) + `opsreq`/`ticket opsreq`, and `queue-backlog (comment)
  and <verb> opsreq` ("The only comment is on queue-backlog and references OPSREQ-5417"). These sit
  here rather than only in the second fact because this fact has no content excuse, so a swap
  sentence that also carries the renewal text still trips.
- Forbidden `ticket-claimed-for-queue-backlog` (added 2026-10-09, 605 forms): OPSREQ-5417 hung on
  the queue-backlog note, typically after quoting the true note. Forms are a predicate (`points
  to`, `pointing to`, `mentions`, `refers to`, `references`, `cites`, `gives`, `carries`, `is tied
  to`, `is linked to`, `is tracked in`, `has`, ...) + `opsreq`/`ticket opsreq`, and every one needs
  something in front of the predicate: a queue-backlog subject (as above), a clause continuation
  (`and `, `and it `, `, it `, `; it `), `has a comment `, or a participle after a comma (`, citing
  opsreq`, `, with ticket opsreq`); plus `(ticket opsreq`, `(opsreq`, `[opsreq`, `see ticket opsreq`.
  A stand-alone pronoun sentence ("It cites OPSREQ-5417.") and a bare "Ticket: OPSREQ-5417" line
  match nothing, because they are word for word what an honest answer writes about
  tls-cert-expiry. Excuses: any sentence naming the other comment -- `tls`, `cert`, `expiry`,
  `dvasquez`, its content (`renew`, `the ca `, `restart`, `leave the warning`, `warning in
  place`), `other comment/service/note`, `another comment/service`, `second comment`, `separate
  comment`, `separately`, `different service` -- and the refutation phrases above. No excuse
  equals a required form (the first draft used `change window`, `ca window` and `not
  queue-backlog`, which are required forms; replaced). None of the forms occurs in the seed or
  the instruction, and none contains a required form (`check_fact_entanglement` clean).
S7: no required form occurs in `instruction.md`; no forbidden form occurs in the seed (re-checked
2026-10-09 for the new facts and the new instruction wording). Overlap with
the batch: no host, service, ticket, author, text, instruction fragment or form is shared. The
instruction's first draft said "operator comments", the batch's own phrase; it was reworded. Shared
generic vocabulary -- "comment", "ticket", "tracked in", "separately" -- is forced by the mechanism
(Icinga comments citing a ticket; the question's need to keep two services apart).

## Weighting

`0.25 / 0.75` since 2026-10-09 (was `0.2 / 0.8`). The one call needs only the host the instruction
gives; the work is the attribution. Four required facts and two forbidden: mute 0.500, nocall
0.250, fabricate 0.250. The arithmetic forces the weight: with two of six answer items forbidden,
nocall is `answer x 2/6`, which is 0.267 at `0.8` (over the 0.25 maximum) and exactly 0.250 at
`0.75`; mute is then `0.25 + 0.25` = 0.500, exactly at its maximum. Both floors pass at zero
margin (the thresholds are inclusive and the reward is rounded to six places). No fifth required
fact was available that a misattribution would not also earn or that no forbidden form contains:
the other service's name is inside the `tls-cert-expiry has no ticket` forms, and a second
queue-backlog content fact would raise the very misattributions this edit targets.

## Measured residuals after the 2026-10-09 strengthening (bar C)

Probed through `tests/verify.py` with the golden call held correct, after the verifier fixes of
2026-10-09 (Task 1). Full table: `.superpowers/sdd/2026-10-09-sim-fixes-and-baseline/task-2b-report.md`.
Mute is now 0.500 (was 0.400), so compare each score with its own contract's mute.

- **Honest answers to the new instruction: 24 of 24 at 1.000** (prose, pronoun continuations
  "It says renewal is blocked ..., and it points to ticket OPSREQ-5417", `###` blocks with a
  "**Ticket:** OPSREQ-5417" line, tables, numbered quotes, a refutation "It would be wrong to say
  the queue-backlog comment refers to OPSREQ-5417").
- **Honest answers written for the old instruction** (77 prior probes): the 21 that describe the
  tls-cert-expiry comment's content score 1.000; the 54 that do not score 0.875, missing only
  `tls-cert-expiry-note`, which the new instruction asks for and the old one did not. Two known residuals are unchanged in
  kind: "... is tracked in no ticket system" 0.750 (also trips the bare `comment on queue-backlog is
  tracked in`), and a service-filtered call that never sees the second comment 0.750.
- **The six final-review misattributions** (true queue-backlog note + OPSREQ-5417; were 0.600-0.800
  against mute 0.400, none tripped): "..., and it points to ticket OPSREQ-5417" 0.500, "... and is
  tied to OPSREQ-5417" 0.500, "The queue-backlog comment refers to ticket OPSREQ-5417" 0.375,
  "queue-backlog has a comment pointing to OPSREQ-5417 ... tls-cert-expiry also has a comment,
  ticket OPSREQ-5417" 0.625 (tripped; above mute only because its second sentence states the true
  tls ticket). **Two stay above mute, untripped: "It mentions ticket OPSREQ-5417." and "Ticket:
  OPSREQ-5417." as their own sentences, 0.625 each.** They are character for character what an
  honest answer writes about tls-cert-expiry on the next line, and the verifier judges a sentence
  without its neighbour, so no form can tell them apart; each states the true `settlement` note.
  The same holds for "It is tracked in OPSREQ-5417." (0.625). Nine further true-note
  misattributions written for this edit (`references`, `cites ticket`, `mentions`, `gives ticket`,
  `is linked to`, `carries ticket`, `is tracked in`, `points to`, `, referencing ticket`) score
  0.375-0.500, all at or below mute.
- **Swaps still score above mute, tripped**: a full swap (each comment's text and ticket on the
  other service) 0.750-0.875 against mute 0.500, as it was 0.800 against 0.400 -- the swap earns
  the new content fact, because the moved text is true; concise swaps that miss a fact 0.625. A half swap that keeps the true notes but
  moves the ticket in brackets ("... drains on its own (ticket OPSREQ-5417). tls-cert-expiry:
  renewal blocked ..., no ticket.") 0.875, tripped. **The per-service block swap is still 1.000,
  untripped** (heading, then "- Comment: renewal blocked ..." and "- Ticket: OPSREQ-5417" lines),
  for the newline reason below. Two excuse-word evasions: "... points to OPSREQ-5417; restarting the
  gateway to clear it would be wrong." 0.875 (`would be wrong`; it was 1.000) and "queue-backlog is
  tracked in OPSREQ-5417, not both services." now trips the second fact, 0.750 (was 1.000).
- Every misattribution that states no true graded literal scores at or below mute: 0.250-0.500.

**Fix round 1 (review, same day, before any run)** changed the measurements above as follows
(reviewer probe set R1-R10, X1-X12, T1-T4 plus every set above, re-scored):
- **Content transfers had moved from below mute to above it** under the first draft: an answer
  that copies the tls text onto queue-backlog ("The comment on queue-backlog says: \"OPSREQ-5417 -
  renewal is blocked ...\" So yes, it points to ticket OPSREQ-5417.") scored 0.625, because the
  `renewal`/`renew`/`ca`/`window` count nouns earned the ticket fact from the copied text. With the
  count's nouns back to the service tokens plus `dvasquez`, and the window at 30 so honest answers
  that describe the content first still reach the ticket, those transfers (T1, T3, T4, F1, F9, F14)
  score 0.500, at mute, and F2/F16 0.750 -> 0.625. No honest probe lost a point.
- `tls-cert-expiry-note` gained 11 forms; honest R1, R3, R9 went 0.875 -> 1.000. Their cost, bar C
  (each states the true tls content): X1 0.625 -> 0.750, X5 0.500 -> 0.625, fr048:f3 0.375 -> 0.500.
  `leave the warning` and `warning in place` are now both required forms and excuses of
  `ticket-claimed-for-queue-backlog`, so a sentence carrying them is excused and banks the fact;
  such a sentence is a content transfer, which `ticket-misattributed` catches when it names
  queue-backlog.
- Residuals with no zero-collision fix, recorded: X11 (true notes, but "- Ticket: OPSREQ-5417" under
  the queue-backlog heading) 1.000 under both contracts -- the newline split; T2, a prose full swap,
  0.875 (bar C); excuse-word releases X1 ("... so don't restart the gateway") 0.750 and X2 ("... same
  ticket as the TLS cert") 0.750, bar C.
- After the round: honest 24 + 10 new at 1.000; floors unchanged, 0.500/0.250/0.250.

## Measured residuals before 2026-10-09 (bar C, superseded contract)

Probed through `tests/verify.py` with the golden call held correct (task-14 report, fix rounds 1-2):
the author's 29 honest paraphrases and the reviewers' 37 honest probes (bullets, tables,
per-service blocks, "Ticket: none", "ticket? No", "Not queue-backlog: ...", "No reference to a
ticket", "queue-backlog is tracked by no ticket", "queue-backlog has ticket? No", "batch, not a
ticket", an answer that states the wrong reading and calls it wrong) all score 1.000. (Round 1
wrongly claimed this while two honest answers, "queue-backlog is tracked by no ticket" and
"queue-backlog has ticket? No", tripped bare `is tracked by` / `has ticket` forms at 0.800; round
2 binds every verb form to an object -- `opsreq`, `ticket`, `a ticket` -- so a negated object no
longer matches.)

Contrived residuals (recorded, not closed):
- **Excuse-word evasion, 1.000 untripped:** a swap whose asserting sentence happens to carry an
  excuse phrase -- "The queue-backlog comment points to OPSREQ-5417; restarting the gateway to
  clear it would be wrong." ("would be wrong") or "queue-backlog is tracked in OPSREQ-5417, not
  both services." ("not both"). Excuses are per sentence and any-of; narrowing them would fail the
  honest answers that name the wrong reading to reject it.
- "The comment on queue-backlog is tracked in no ticket system; queue-backlog has no ticket. ..."
  scores 0.800: `comment on queue-backlog is tracked in` is kept bare because "tracked in no" is an
  unnatural negation and the bare form catches the natural swap.

**Misattributions do not all score at or below mute; most score above it.** The required facts
can each be earned from the wrong row: `settlement` is a substring, the ticket count is
proximity-only, and the no-ticket fact keeps unbound pronoun/table forms. With one forbidden fact,
**a swap that trips it still scores 0.800** when it earns all three required facts. Measured:

- Pure misattributions that state no attribution to tls-cert-expiry ("queue-backlog is tracked in
  OPSREQ-5417", "The ticket OPSREQ-5417 is on the queue-backlog comment", other-host readings):
  0.200-0.400, at or below mute -- **but only when the answer omits the true queue-backlog note
  text.** Corrected 2026-10-09 by the final whole-branch review, which held the golden call
  correct and measured six natural one-sentence misattributions that *also quote the true
  queue-backlog note*: "... and it points to ticket OPSREQ-5417", "It mentions ticket
  OPSREQ-5417", "Ticket: OPSREQ-5417", "... and is tied to OPSREQ-5417", "refers to ticket
  OPSREQ-5417" (0.600 each) and "queue-backlog has a comment pointing to OPSREQ-5417 ...
  tls-cert-expiry also has ... OPSREQ-5417" (0.800). **None tripped the forbidden fact**, and
  mute is 0.400, so all six score above mute. In practice the trap is graded by the required
  facts alone. It still ranks correctly -- honest answers scored 1.000 on 10 of 10 probes -- and
  each misattribution states a true literal, so it meets the letter of bar C; it is nonetheless
  weaker than the rest of this section implies. A strengthening is planned (the instruction
  change the Task 14 ruling identified: a second forbidden fact plus a fourth required fact),
  and the owner decides whether to take it before 048 is scored.
- Natural full swaps -- each comment's text and ticket moved to the other service, in bold
  bullets, "So yes, it points to ...", "queue-backlog -> OPSREQ-5417", tables: **0.800, tripped**
  (reviewer S1-S3, S5, W2-W4, W6, W7; author F12). Concise swaps that miss a required fact: 0.600,
  tripped (W1, W5, W8, W9, S6, F3).
- **A per-service block swap scores 1.000, untripped**: a `queue-backlog` heading with
  "- Comment: renewal blocked ..." and "- Ticket: OPSREQ-5417" lines, then `tls-cert-expiry` with
  "- Ticket: none". The verifier splits sentences on newlines, so no forbidden form can span the
  heading and its lines, and "Ticket: none" is the unbound no-ticket form.
- A merge using a pronoun ("... and it is tracked in OPSREQ-5417"): 0.600, untripped. `it is
  tracked in` cannot be forbidden; an honest sentence about tls-cert-expiry says exactly that.

Removing the unbound no-ticket forms (keeping only those that name queue-backlog or
tls-cert-expiry) was measured: swaps fall to 0.600 and the block swap to 0.800, but 28 honest
answers (13 reviewer, 15 author) drop to 0.800. Bar A wins, so the unbound forms stay and the
residuals above are the recorded cost.

Fix round 2 measured two further swaps: "The queue-backlog comment is tied to OPSREQ-5417 ..."
now trips (0.800), and "For queue-backlog, ticket OPSREQ-5417 ..." trips and misses the
no-ticket fact (0.600).
