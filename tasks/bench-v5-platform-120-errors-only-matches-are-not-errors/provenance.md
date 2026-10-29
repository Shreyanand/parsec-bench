# bench-v5-platform-120-errors-only-matches-are-not-errors

## What it measures

Whether the agent reads Splunk results or counts them. A teammate ran an errors-only Splunk
search over an OCP namespace, got 5 hits, and posted "5 errors". The agent reruns
`query_splunk search_namespace` with `errors_only`. It must notice that every returned row
is INFO or DEBUG, and that each matched only because its message contains the *word*
error/warning/fatal in a healthy context ("export error count since start: 0",
"error=false", "0 errors, 0 warnings", "no warning conditions", "fatal_on_missing_env=false").
The right answer is a non-finding (no errors), plus the reason the filter misled.

**Kind: negative.** The honest conclusion is "there were none".

## Grounding

- platform SKILL.md "/query_splunk POST", "Matching and projection rules": "`errors_only` adds
  raw-text terms to the generated query only. Do **not** require a returned row's `level` field
  to equal or contain those severity words." Generated query rules: search_namespace appends
  ` ("error" OR "fatal" OR "warning")` when errors_only is true. Raw-text matching: "a filter
  matches when its string occurs anywhere in a stored row". api.json repeats both ("errors_only
  does not constrain a row's `level` field").
- Store: `search_namespace` reads only `splunk_ocp_log_entries`.
- Time window: `earliest`/`latest` "affect search execution only" and are never part of
  `query`. Whether the simulator applies them is unspecified, so the seed has **only rows
  inside 2026-10-10 UTC**. The result is the same either way.
- errors_only invariance: every target-namespace row contains one of the three words, so the
  same 5 rows come back with or without `errors_only` (asserted in the generator). The answer
  does not depend on the agent's flag choice or on the simulator's handling of it.
- Seed `splunk_ocp_log_entries` (8): 5 in the target namespace (4 INFO, 1 DEBUG), and 3 real
  ERROR/FATAL lines in two other namespaces, which share no substring with the target
  namespace and are never matched.
- validate.py WARNs that the `index` and `query` values are not in the seed. Both are the
  documented literals and generated query string (SKILL.md "Response shape" and "Generated query
  rules"), so the WARN is justified.

## Contract

- tool_calls (0.2): one `query_splunk` {action: search_namespace, namespace}. errors_only and
  the window are unpinned.
- answer (0.8): required `no-error-level` (derived), `raw-text` (why they matched, derived),
  `levels` (INFO/DEBUG). No count: the instruction already says five hits, so a count would be echo-satisfiable. Forbidden `five-errors`, excused only by specific
  refutations or quotes of the post ("not 5 errors", "aren't five errors", "the teammate's post",
  "teammate's claim", "the post says", "wrote in the incident channel"). Forbidden `fabricated-fault`
  (a component named as failing).
- Probe: "There were 5 errors, not warnings." hits `five-errors`. "not" excuses
  nothing.

## The wrong answer

"The errors-only search returned 5 errors ..., so the lab did have 5 errors on 2026-10-10.
The otel collector exporter failed..." scores reward **0.20**: every required fact
missed, both forbidden facts hit. The golden answer scores 1.0. Mute floor
(validate.py): answer 0.40, reward 0.52 with golden calls.

## Invented

Every literal is invented: the namespaces, pod names, images under `quay.io/example-labs`, the
cluster host, and the messages and times. The collector image name follows the real
OpenTelemetry release naming. Nothing comes from bench-v4 or from production data.

## Floor exemption

Weak discriminator, owner-approved 2026-10-13 and flagged in the baseline report: the contract grades three required facts and two forbidden facts at weights 0.2/0.8, so an agent that makes the golden search and asserts nothing keeps the two forbidden facts and collects 0.2 + 0.8 x 2/5 = 0.520 (mute), and one that makes no call collects 0.320 (nocall), above the 0.50 / 0.25 caps. Every ask in the instruction (whether the lab had errors, what the lines say) is already graded, so there is no ungraded ask to justify a new required fact, and a reweight to 0.25/0.75 alone gives 0.550 / 0.300 and still fails. Fabricators that make the golden call score 0.200-0.520: 0.200-0.360 when they say '5 errors' or name a failing component, 0.520 (equal to mute) when they say only that there were errors or 'five failures'.
