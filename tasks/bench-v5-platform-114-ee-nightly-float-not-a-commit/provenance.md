# bench-v5-platform-114-ee-nightly-float-not-a-commit

## What it measures

A three-hop RCA in which the code stood still and the runtime moved. A workload task
fails with `Unsupported parameters ... install_timeout`, which reads like a code change,
and the instruction voices exactly that theory ("somebody pushed a breaking change to
agnosticd"). The failing job's own `git_revision` equals the good run's revision, which
the user supplies; the job's runtime-info line shows the `:latest` EE was rebuilt after
the good run and carries `rhdp.openshift_helpers 4.0.0`; the EE repo's
`requirements.yml` lists that one collection as `>=3.2.0` with no upper bound while
pinning the others below their next major. The agent must refute the theory from a
metadata field, follow the runtime to its build definition, and find the unbounded spec.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **accepting the user's change-blame theory without comparing revisions, and
not considering that the runtime can drift while the code is fixed**. "Unsupported
parameter" points at the role, the instruction points at agnosticd, and an agent will
happily go read the role task file and "find" the parameter there. The refutation is a
comparison of `git_revision` (returned on `get_job_log`, easy to skip) with a value in
the instruction; the cause is in a repository (the EE build repo) that no catalog item
or agnosticd file names, reachable only from the runtime line in the log. A recovered
API-wait retry block is the secondary decoy. Good agents commonly name the EE and the
4.0.0 bump but miss the unbounded spec or never state the revision equality.

## Grounding

- `query_aap2 get_job_log`: composite `job_id` + `controller`; the response carries
  `git_url`, `git_branch`, `git_revision` because the stored row has them (platform
  SKILL.md response contract). The good job 5528440 is seeded too (same revision, no log)
  so an agent that checks it with `get_job` gets a consistent answer.
- `search_github_repo`: exact `(owner, repo, ref, search)` row, omitted `ref` → `HEAD`;
  rows seeded under `HEAD` and `main` for `openshift_helpers`, `rhdp.openshift_helpers`
  and `requirements`. The repo `rhpds/ee-rhdp-multicloud` is derivable from the log's
  "built ... from github.com/rhpds/ee-rhdp-multicloud@main". Expected call pins only
  `owner`/`repo`.
- `fetch_github_file`: `requirements.yml` and `execution-environment.yml` at `HEAD` and
  `main`; omitted `ref` resolves to the default branch.
- Enum values: controller `east`.

## Contract

Weights **0.25 / 0.75** (the group's one non-0.3 weight): three calls, discrimination in
the answer. Calls `ordered-subsequence`.

- `param` (`install_timeout`) and `version` (`4.0.0`) — anchors from the log.
- `unbounded` — `>=3.2.0` / no upper bound, only in requirements.yml.
- `same-revision` (derived) — the refutation of the teammate's theory.
- `nightly-rebuild` (derived) — the image moved between the runs.
- forbidden `commit-blame` (attributed_to excuses rejection sentences; excuse phrases are
  specific — a bare "not a" excused "does not accept" in the first draft and was removed)
  and `api-timeout`.

Mute answer floor: 2 forbidden of 7 → 0.286, reward 0.464 with golden calls.

leakage.py WARN (weak literals), justified: `fold_markup`, `requirements.yml` are contract keys, logger/file names or standard AgnosticD variable names shared by the API's world (`ncloud_provider`-style tokens are `\n` + a key in serialized YAML), not scenario identity.

Excuses (2026-10-12 generic-excuse fix pass): `attributed_to` holds only specific refutations of the claim -- `commit-blame`: "no agnosticd change", "not an agnosticd change", "not a code change", "nothing changed in agnosticd", "bisecting will find nothing", "teammate's theory is wrong". Each forbidden fact was probed with one sentence that asserts it while carrying hedge words ("suggest", "suspect", "rather than", "theory", "isn't"): `.scratch/probes/114-api.md`, `.scratch/probes/114-commit.md`; every probe is hit. Golden still 1.000.

## The wrong answer

`.scratch/wrong_114.md`: blames a breaking agnosticd change in the devspaces role and
adds the API retries as a sign of an unhealthy cluster. Scores **0.357** with golden
calls (answer 0.143: only the parameter). Golden answer 1.000.

## Invented

Every literal is invented: jobs 5530918/5528440, GUIDs `h6ztr`/`q9fjx`, revision
`e41d07a9b2c6`, item `devspaces-workshop`, the EE repo and image
`rhpds/ee-rhdp-multicloud`, the collection `rhdp.openshift_helpers` with its 4.0.0
release and `operator_install` module, the role names `runtime_info`,
`ocp4_wait_for_api`, `ocp4_workload_devspaces`, and all timestamps. Collection names
`amazon.aws`, `kubernetes.core`, `community.general` are real public names used only as
pinned neighbours. The incident class (unpinned dependency float in a nightly `:latest`
EE) is invented in the mould of bench-v4's challenge tranche; no public postmortem is
its source, and nothing comes from bench-v4 or production data.
