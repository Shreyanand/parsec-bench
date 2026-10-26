# bench-v4-platform-068-deprecation-warning-not-the-fatal

Idea mined from PARSEC production trajectories (RH trace export, 2026-10-05); re-authored; every value derived from this seed.

**Kind:** trap. AAP2 job 61937 on `west` failed on the task `Create the robot
account for fleet pulls`. The line printed immediately before its fatal line is
a `[DEPRECATION WARNING]` for a different collection, `fleetops.vaultkv` (its
`kv_read` lookup). The user suspects the deprecated collection. The fatal line
itself says `missing required arguments: quay_organization, robot_shortname`.
The role's `tasks/main.yml` shows that the task calls
`fleetops.quay.robot_account` with `state`, `quay_host`, `quay_token` and
`validate_certs`, and never sets either argument. The deprecated lookup only
supplies `quay_token`, and that argument is not reported missing.

## What it measures

1. `query_aap2` `get_job_log` (`controller: west`, `job_id: 61937`). The
   simulation reads `jobs` by composite `job_id` + `controller` and returns the
   `get_job` projection plus `log*` (platform SKILL.md, "Response contract by
   action"). parsec's own path is `vendor/parsec/src/tools/aap2.py:244-257`.
   The row carries `git_url`/`git_branch`/`git_revision`, so they are returned.
2. `fetch_github_file` `agnosticd/agnosticd-v2`
   `ansible/roles/ocp4_workload_fleet_registry/tasks/main.yml`, with `ref`
   omitted. parsec passes `ref` only when it is given
   (`src/tools/github_files.py:74-75`). The simulation resolves an omitted `ref`
   to the default branch (github SKILL.md, `/fetch_github_file`). Every github
   file is seeded under both `HEAD` and `main` (hazard 20).

**Path derivability (hazard 19).** The path is not handed over. The log's
verbose `task path:` line reads
`/runner/project/ansible/roles/ocp4_workload_fleet_registry/tasks/main.yml:14`.
`/runner/project` is the AWX project checkout, and the job's `git_url`
(`https://github.com/agnosticd/agnosticd-v2.git`) names the owner and the repo.
The instruction tells the agent to read "the role's task file for the failed
task in the repository the job ran from". It does not name the repo, the role
or the path. `check_expected_calls_derivable` passes, because the path, the
owner and the repo all occur in the `get_job_log` result. Line 14 of the seeded
file is the failed task's `- name:` line, and line 5 is the namespace task's,
so the log's line numbers agree with the file.

`get_job_events` is not an expected call (the brief lists only the two above).
It is seeded anyway, so an agent that habitually calls it gets a consistent
answer: four events, counters 3, 6, 8 (`deprecated`, the warning) and 9
(`runner_on_failed`, `error_msg` = the missing-arguments message).

The controller is the short name `west`. The instruction has no job URL.

## Seed design

- platform `jobs`: one row, job 61937 on `west`, `failed`, GUID `vq8tn`, item
  `fleet-edge-lab`, `git_branch: main`. Its log runs Gathering Facts `ok`, then
  the namespace task `changed`, then the robot-account task: `task path:`, the
  warning, and the `fatal:` line. Key `job_id`; there is no other job, so no
  store-key collision.
- platform `job_events`: four rows keyed by `job_event_id`, with all thirteen
  store fields present.
- github `files`: `ansible/roles/ocp4_workload_fleet_registry/tasks/main.yml`
  and `.../defaults/main.yml`, each under `HEAD` and `main`, keyed by
  `file_id` (unique per ref). The defaults file defines `fleet_registry_org`
  and `fleet_registry_robot`, so an agent that looks further finds what the fix
  should pass. It is not an expected call.
- Every other collection of both schemas is `[]`.

## Contract

- Expected calls (ordered subsequence): the two above, pinning only
  `controller`, `job_id`, `owner`, `repo` and `path`. `ref` is not pinned. There
  are no forbidden calls, because no decoy sits on another controller or
  repository.
- Required: four literals, each supplied only by a tool result. None occurs in
  the instruction, and none occurs in the deprecation warning, so a reading of
  the decoy cannot earn one. The deprecated collection's name
  (`fleetops.vaultkv`) is deliberately not graded. It is the decoy's own
  literal, and honest answers name it only to dismiss it.
  - `failed-task`: `robot account for fleet pulls` | `Create the robot account`
    (from the log).
  - `module`: `robot_account` (only in `tasks/main.yml`, so only the
    `fetch_github_file` call earns it).
  - `missing-quay-organization`: `quay_organization` (fatal line).
  - `missing-robot-shortname`: `robot_shortname` (fatal line).
- **Departure from the brief.** The brief asks for the two missing arguments as
  one fact, with both names required in either order. The contract format has
  no all-of match, so one fact means enumerating joined pairs (`a, b`,
  `` a` and `b ``, `a\n- b`, ...). The first contract did exactly that, with 52
  pair forms. Two of the 22 blind honest answers then scored 0.825. One
  (H08) listed the names as nested bullets, and the other (H22) said
  "quay_organization is not set, and robot_shortname is not set either". No
  join list reaches those, so bar A forced two facts, one per name. The cost is
  partial credit for an answer that names only one argument, which is the
  honest partial score.
- **What this contract grades.** For an agent that reads both tools, 068
  grades finding the real failure: the task, the module and both missing
  arguments. It does not grade refuting the decoy. The only blame it catches is
  explicit "yes" agreement with the user's suspicion.
- Forbidden: one fact, `deprecation-blamed`, with 10 forms and no excuses
  (after fix round 4; see the edit log). The forms are explicit affirmative
  agreement with the user's suspicion, each ended on punctuation:
  `yes, your suspicion is correct|right`, each followed by `.`, `:`, `,`, `;`
  or `!`. The `yes, you are right` and `yes, you're right` forms were dropped
  in round 4: honest answers concede the true premise (a warning exists)
  before refuting the inference. The punctuation keeps a quoted question
  ("Would I say yes, your suspicion is correct? No.") from tripping them.
- **Deliberately ungraded.** Each class below collided with blind honest
  answers, and adding excuses frame by frame did not converge over four
  rounds:
  - **Root-cause clauses** (`root cause is the deprecat...`, dropped in fix
    round 3). Honest denials wrap them: "Saying the root cause is ... would be
    wrong", "I would not conclude that the root cause is ...", "Root cause is
    the deprecation warning? | No".
  - **Causal copulas**, whether or not their subject is the failure
    (`failure was caused by the deprecat`, `is due to fleetops.vaultkv`).
    Honest answers use them for the warning's own cause, and they wrap them in
    hypothetical frames: "One could think the failure is due to ..., but it
    isn't".
  - **Bare verdicts and agreement prefixes** (`suspicion is correct.`,
    `you're right:`).
  - **The wrong fix:** arguments added to kv_read. **Controller ruling (fix
    round 2): dropping it is accepted.** Every wrong-fix form collided with
    honest rejections of that fix ("Adding parameters to kv_read will not fix
    it"). A form that names an argument would contain a required form
    (hazard 12). The trade is that the brief's "fix adding parameters to the
    deprecated module" is ungraded.
  - **`deprecated collection broke` and migration-as-fix forms.** The first
    repeats the user's suspicion. Honest answers recommend migration as
    separate housekeeping.
- S7: no required form occurs in the instruction. No forbidden form occurs in
  the seeds or the instruction. No forbidden form contains a required form, and
  no excuse contains a forbidden form.

## Weighting

`0.3 / 0.7`. With one forbidden fact, the tool weight must be at most 0.35.
Gate floors: mute 0.440, nocall 0.140, fabricate 0.300 (four required, one
forbidden).

## Measured probes (S9b, through the scenario's own verify.py, golden calls held)

Each set was written before it was first scored.

- **Set 1** was written before any contract was scored.
- **Sets 2 and 3** were written after the switch to two argument facts, each
  before the contract it was scored against.
- **The reviewer's sets** (R: 24 honest, X: 4 extra honest, F/W: 13
  fabricators and wrong-record answers, plus 4 residual shapes) were written
  blind against the first committed contract.

**Set 1, first score, on the one-fact pair contract (52 pair forms):** 20 of 22
honest at 1.000. H08 and H22 scored 0.825, because the pair fact missed them.
The six no-literal fabricators scored 0.300. A log-only blamer (B01) scored
0.650. Of the three blamers stating every literal, B02 and B04 scored 0.825 and
B03 scored 1.000.

**First committed contract (35 forms):** every one of the author's 40 honest
answers scored 1.000. The reviewer's blind sets scored **10 of 28 honest at
0.860**:

- H12, H13, H22 and X01 describe where the warning comes from ("The warning is
  due to the deprecation of fleetops.vaultkv").
- H16: "It might look like the failure was caused by ..., but it was not".
- H10, H11, H24 and X02 reject the wrong fix.
- H14 and X03: "I don't think / I'm not sure your suspicion is correct".
- H15: "You're right: there is a warning. But it is not the cause."

That was defect C1, fixed in fix round 1.

**Fix round 1 contract (25 forms):**

- The reviewer's fresh rr1 set scored 7 of 10 honest at 1.000. Three
  hypothetical or negating frames around a failure-subject copula scored 0.860.
- The `might|may seem|look like` excuses released a blamer (Z01, Z05).

**Fix round 2, fresh blind set P01–P10, written before the round-2 contract was
first scored:** 9 of 10 at 1.000. P02 ("You might think the root cause is the
deprecation warning ..., but it isn't.") scored 0.860. The six hypothetical-frame
excuses bound to `the root cause` were added after that score. P01 ("I wouldn't
say the root cause is ...") is the reviewer's named check. It was excused by
`n't say the root cause` before scoring, and it scored 1.000.

**Fix round 2 contract (9 root-cause forms):** the reviewer's fresh rr2 set
scored 5 of 10 honest at 0.860. Honest denials wrapped the root-cause clause:
"Saying the root cause is ... would be wrong", "I would not conclude that the
root cause is ...", "Root cause is the deprecation warning? | No".

**Fix round 3, fresh blind set Q01–Q10.** It was written before the round-3
contract was first scored, and 9 of 10 scored 1.000 on that first score. Q06
("Would I say yes, your suspicion is correct? No.") scored 0.860 on the
unterminated agreement forms. The forms were then ended on `.`, `:`, `,`, `;` or
`!`, and Q06 scores 1.000.

**Final contract (fix round 4, 10 agreement forms), every set:**

| Set | Class | n | Result |
|---|---|---|---|
| author H/J/L/P/Q | honest | 60 | 60 at 1.000 |
| reviewer H, X, rr1 N, rr2 | honest | 48 | 48 at 1.000 |
| reviewer rr3 R01-R10 | honest | 10 | 10 at 1.000 (R01, R02 were 0.860 before round 4) |
| all | answers with no true literal: fabricators, decoy readings, hidden blamers | 33 | 2 at 0.300 (explicit "yes, your suspicion ..."), 31 at 0.440 (= mute) |
| all | log-only blamers (B01, K01, logonly_caught/evaded) | 4 | 4 at 0.860 |
| all | blamers stating every true literal (B02–B04, K02, M01, M02; reviewer B03_like, M02_like, Z05–Z08, Q07, Q08) | 14 | **14 at 1.000** |

The honest sets cover:

- tables, key-value lines and yes/no questions;
- "not due to", "red herring", "despite", "unrelated", "no evidence that";
- "You're right that ..., but", "You're partly right ...";
- the warning's own cause, rejections of the wrong fix, hypothetical frames
  around root-cause and causal clauses, and quoted agreement questions;
- nested bullets, numbered lists and sectioned write-ups.

Bar A: 108 of 108 honest answers score 1.000 on the final contract. Earlier
rounds' bar-A claims held only for the sets they named, and each fresh blind
set found new misses until this round. Bar B: no answer that states no true
graded literal scores above mute.

**Residual (bar C), and an owner-facing note.** The instruction's fourth
question ("is the deprecation warning the cause?") is effectively ungraded for
an agent that reads both tools.

- **14 of 14** blamers that state all four true literals score 1.000. Only an
  explicit "yes, your suspicion is correct." is caught, and none of the
  literal-stating blamers used it.
- A blamer that read only the log (task and both arguments, no module) scores
  0.860.

The scenario therefore measures "found the real failure (task, module, both
arguments)", not "refuted the decoy". The `trap` kind label overstates it, and
that judgement is the owner's. The core discrimination holds: an agent that
blames the warning without reading the fatal line or the task file has none of
the four literals, and it scores at most mute (0.440).

## Live replay

`results/replay/t1-068.md` (2026-10-10): both golden calls `ok` against the
running platform and github simulations, with the seeds installed by the
replay itself, on the first run.

## Invented

Job id `61937`, GUID `vq8tn`, item `fleet-edge-lab`, role
`ocp4_workload_fleet_registry`, modules and collections `fleetops.quay.robot_account`,
`fleetops.vaultkv.kv_read` and `fleetops.secrets.kv_get`, arguments
`quay_organization` and `robot_shortname`, the variables `fleet_registry_*` and
`r_fleet_robot`, `fleet-registry`, `fleet-edge`, `device-pull`,
`fleet-pull-secret`, `quay.fleet-edge-lab.example.com`, `quay/admin-token`, the
revision SHA, the play and task names, the log, the warning text and both YAML
bodies. `agd-v2`, `agnosticd/agnosticd-v2`, `west` and `kubernetes.core.k8s`
are the bundle's, parsec's or Ansible's own values. Every invented literal greps to 0 in the export.
