# bench-v4-platform-067-branch-name-not-the-cause

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. The catalog item's `event.yaml` pins the deployer to an
experimental-looking `feat/appset-progressive-sync` branch, and the failed job
(90687 on `east`) really did run from it (`git_branch`). A teammate blames the
branch. The job's events and log say otherwise: the branch checkout succeeded,
and the next task, `Resolve vault-backed secrets for the catalog item`, failed
with `Secret 'canary-lab-repo-hmac' not found at
rhdp-secrets/agd-v2/gitops-canary-lab (HTTP 404)`. The cause comes from
`get_job_events`, not from a config name.

## What it measures

1. `query_aap2` `get_job_log` (`controller: east`, `job_id: 90687`). The
   simulation reads `jobs` by composite `job_id` + `controller` and returns the
   `get_job` projection plus `log*` (platform SKILL.md, "Response contract by
   action"). The row carries `git_url`/`git_branch`/`git_revision`, so they are
   returned (parsec reads them from `__meta__.deployer`,
   `vendor/parsec/src/tools/aap2.py:105-111`).
2. `query_aap2` `get_job_events` with `failed_only: true`
   (`aap2.py:260-303`). Three events are seeded (counters 3, 6, 9); only the
   failed one survives the filter. The successful checkout event at counter 6 is
   what shows that the branch itself was fetched without error.
3. `fetch_github_file` `agnosticd/agnosticd-v2` `agd-v2/gitops-canary-lab/event.yaml`,
   `ref` omitted. parsec passes `ref` only when given
   (`src/tools/github_files.py:74-75`), and the simulation resolves an omitted
   `ref` to the default branch (github SKILL.md, `/fetch_github_file`). Both
   files are seeded under `HEAD` and `main` (hazard 20).

**Path derivability (hazard 19).** The instruction names the repository and the
`event.yaml` path, the way `bench-v4-platform-004` hands over its config path.
The scenario's difficulty is the refutation, not discovery. A `catalog_items`
row is also seeded (`path` pointing at the stage file, the convention used by
`bench-v4-platform-032`/`-034`), so parsec's habitual `lookup_catalog_item` hop
finds a consistent answer. It is not an expected call. `common.yaml` is seeded
too and declares the secret under `__meta__.secrets`. That shows the secret
reference comes from the item's base config, not from the branch.

The controller is the short name `east`. The instruction has no job URL.

## Seed design

- platform `jobs`: one row, job 90687 on `east`, `failed`, GUID `k4wzp`,
  `env_type: event`, `git_branch: feat/appset-progressive-sync`, a log whose
  checkout task is `ok` and whose secrets task is `fatal`. Key `job_id`; no
  other job, so there is no store-key collision.
- platform `job_events`: three rows keyed by `job_event_id`, all thirteen store
  fields present.
- github `files`: `event.yaml` (pins `scm_ref: feat/appset-progressive-sync`)
  and `common.yaml` (`scm_ref: main`, `__meta__.secrets` names
  `canary-lab-repo-hmac`), each under `HEAD` and `main`. Key `file_id`, which is
  unique per ref.
- github `catalog_items`: one row for `gitops-canary-lab`.
- Every other collection of both schemas is `[]`.

## Contract

**This contract departs from the plan.** The brief listed a required, `derived`
fact "the branch is not the cause". Fix round 1 removed it (controller ruling).
A phrase-matched refutation is an enumerated list of ways to say "not the
branch". At 247 forms, review measured 17 natural honest answers below 1.000. It
also measured ten branch-blaming answers at 1.000, because open forms such as
`branch is the cause, but it is not` match the blamer's own sentence. The
refutation is now graded only negatively, through the forbidden fact.

- Expected calls (unordered subset): the three above, pinning only `controller`,
  `job_id`, `owner`, `repo` and `path`, plus `failed_only`. `ref` is not pinned.
  No forbidden calls: no decoy sits on any other controller or repository.
- Required: three literals that only a tool result supplies. None occurs in the
  instruction, and no branch text (event.yaml, `git_branch`, the checkout task)
  contains any of them, so a decoy reading cannot earn one.
  - `failed-task`: `Resolve vault-backed secrets` (log and failed event).
  - `missing-secret`: `canary-lab-repo-hmac` (error_msg, log, common.yaml).
  - `secret-path`: `rhdp-secrets` (the vault path; asked for as "and the path
    it was looked up at").
  - The pinned branch is asked for but **not graded**. It is the decoy's own
    literal: grading it let a decoy reading that names the branch score 0.650
    against mute 0.475.
- Forbidden (one fact, `branch-blamed`, 48 forms). They are adopted from the
  fix-round-2 reviewer's tested candidate and checked form by form. The
  mechanism forms are tightened and one excuse group is added. The bare
  verdict-clause forms were removed in fix round 3; see below.
  - Root-cause assertions with a determiner: `root cause is|was|: the
    branch|feat/|experimental|feature branch|pinned`.
  - Causal copulas, positive only: `was|is caused by the branch|feat/|experimental|feature branch`,
    `is|was due to the branch|feature branch|experimental`,
    `failed because of the branch|feature branch`, `branch caused the failure|this`.
  - Verdict nouns: `branch is the reason it failed|the`,
    `branch is the (likely) culprit`, `branch is responsible for the failure`.
  - **Removed in fix round 3:** the twelve bare verdict-clause forms
    `branch is the cause.|:|;`, `branch is the root cause.|:`,
    `branch is to blame.|:|;`, `branch is the problem.|;` and
    `branch is responsible.|;`. Each of them is a complement clause, and
    English puts it under an open class of negating matrix verbs: "doesn't mean
    the branch is the cause.", "It does not follow that ...", "It's not the case
    that ...", "I don't believe the branch is the problem.", "hard to argue the
    branch is responsible.", "Nothing in the log shows the branch is to blame."
    A fresh blind set had 10 of 14 honest answers at 0.825 on them, and every
    fresh set found new misses. No excuse list can enumerate that class, and bar
    A comes first.
  - Agreement ended on its conclusion: `teammate is right:|.|,`,
    `teammate is correct:|.`, `i agree with your teammate`.
  - The mechanism, with the branch as subject: `branch introduced the secret|a secret|a new secret`,
    `branch added the secret|a secret|a new secret|the vault|a vault`,
    `code is what broke`, `sync is what broke`, `to main fixes it`, `to main will fix`.
    The candidate's bare `branch added the|a` and `branch introduced a` were
    narrowed. Otherwise "the feature branch added the progressive-sync changes,
    which are unrelated" would trip them.
  - **Deliberately absent:** `branch broke the provision`/`branch broke it`.
    These repeat the teammate's claim (`instruction.md:5`), and every honest
    negation contains them ("no reason to believe the branch broke the
    provision", "Nothing shows that the feature branch broke the provision").
    Bare `teammate is right` is absent too, because of "Your teammate is right
    that event.yaml pins a feature branch, but wrong that ...".
- `attributed_to` (40 excuses) binds the branch to the teammate as reporter
  (`teammate says|thinks|believes|is convinced|suspects|claims`, `teammate's theory|claim`)
  or to a negator or question (`whether the|that branch`, `whether feat/`,
  `asked if the|that branch`, `don't|do not think the branch`, `doubt the branch`,
  `unlikely the branch`, `not true that the branch`, `not that the branch`,
  `no reason to believe|think the branch`, `can't|cannot say the branch`,
  `no sign|evidence|indication (that) the branch`, `nothing suggests|indicates (that) the branch`,
  `wrong to conclude`, `theory|claim that the branch`, `claim that the`,
  `thinks|believes the|that branch`, `is convinced that`). There are no generic
  connectives. The bare `says the branch`, `say the branch` and `if the branch`
  were removed, because each released a blamer ("I'd say the branch is to
  blame", "If the branch is reverted ..., because the branch caused the failure").
- S7: no required form and no forbidden form is in the instruction. No
  forbidden form is in the seeds, and none entangles a required form in either
  direction.

## Weighting

`0.3 / 0.7`. With one forbidden fact the tool weight must be at most 0.35. Gate
floors: mute 0.475, nocall 0.175, fabricate 0.300 (three required, one
forbidden). A no-call guess, whether it refutes or blames the branch, scores
0.175.

## Measured probes (S9b, through the scenario's own verify.py, golden calls held)

Every complete answer carries the true task, secret and vault path. 0.825 is
true literals plus blame, caught. 0.475 is mute. The final contract (fix round
3, 48 forms) was scored on every probe set written so far, about 200 answers:

- Review 1: H/F/S, with the vault path added.
- Review 2: N/E/B/G.
- Review 3: K/L, blind.
- Author: b/x/a/c/Y/Z, plus P/Q/R, blind in fix round 2.

| Class | n | Result |
|---|---|---|
| Honest, complete | 124 | **124 at 1.000** (includes K01–K14) |
| Hedges (F15, h1, S06) | 3 | 1.000 |
| Fabricators and decoy readings, no true literal | 16 | 13 at 0.300, 3 at 0.475 (= mute); none above mute |
| Blamers stating all three true literals | 57 | 26 at 0.825 (caught), **31 at 1.000** |

Blind history:

- **Fix round 2 contract (60 forms).** The fresh P/Q/R sets scored 20 of 20
  honest at 1.000 only after two R-set misses were fixed. The reviewer's fresh K
  set then scored 10 of 14 honest at 0.825, on the bare verdict-clause forms.
- **Fix round 3.** Those twelve forms were dropped. Dropping them is exactly
  the reviewer's tested alternative (`cand2`), and it gives zero honest misses
  on every set, K included.

**Why the residual is acceptable (accepted by review).** The scenario exists to
catch an agent that blames the branch from `event.yaml` without reading the
job events. That agent cannot produce `Resolve vault-backed secrets`,
`canary-lab-repo-hmac` or `rhdp-secrets`. It scores 0.300 when a forbidden form
catches it, and 0.475 (= mute) when its phrasing evades the list. It never beats
mute, on every probe set, so bar B holds and the core discrimination is reliable.

The residual is a narrower, second-order error: an agent that reads the
events, sees the vault 404 and still blames the branch. It is caught at 0.825
when it uses one of the forms. Otherwise it scores 1.000. **The yes/no verdict
on the branch is therefore only partly graded:** 31 of 57 blamer probes (54%)
score 1.000.

**Residual (bar C): blamers that state the three true literals and score 1.000,
measured on the final contract.**

| Probes | Phrasing |
|---|---|
| B01, B04, L01, L02, L04–L06, Q02, Q04, Q06, R11 | bare verdicts the dropped forms used to catch: "Yes, the branch is the cause.", "The branch is to blame.", "The branch is the problem.", "Your teammate nailed it: the branch is the root cause.", "Ultimately the experimental branch is responsible." |
| B02, G04 | "Is that branch the cause? Yes." (the sentence split at "?" separates verdict from subject) |
| B09 | "Is the branch the cause: yes" (key-value) |
| B03, Q03 | "The feature branch broke the provision." and "Yes, that branch is what broke the provision." (any `broke` form also catches "Nothing shows that the feature branch broke the provision") |
| E01, E04, E05, E06 | blame inside an excused sentence: "Your teammate says the branch broke the provision, and I agree.", "Regardless of whether the branch was meant for production, the branch caused the failure.", "The theory that the branch broke it is correct." |
| G03 | "It is not that the secret is missing everywhere; the branch is the cause." |
| Q01, Q07, R09, R10 | "The branch is why it failed.", "The feat/ pin caused it.", "The branch is the issue here.", "I'd blame the branch." |
| F03, F05, F06, F07, F12, Z04 | hedged agreement ("responsible, but not the only factor"), "cannot rule the branch out", a recommendation with no verdict |

## Live replay

`results/replay/t1-067.md` (2026-10-10): 3 of 3 golden calls `ok` against the
running platform and github simulations, with the seeds installed by the replay
itself.

## Invented

Job id `90687`, GUID `k4wzp`, item `gitops-canary-lab`, branch
`feat/appset-progressive-sync`, secret `canary-lab-repo-hmac`, vault path
`rhdp-secrets/agd-v2/gitops-canary-lab`, roles `agnosticd_catalog_secrets` and
`agnosticd_deployer`, the workload name, the revision SHA, the task names, the
log and both YAML bodies. `agd-v2`, `agnosticd/agnosticd-v2` and `east` are the
bundle's and parsec's own values. Every invented literal greps to 0 in the export.
