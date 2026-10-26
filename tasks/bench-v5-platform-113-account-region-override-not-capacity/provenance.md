# bench-v5-platform-113-account-region-override-not-capacity

## What it measures

A four-hop RCA about layered configuration. GPU worker launches fail in `ca-west-1`
with `Unsupported` (the instance type is not offered in the zone), next to a
capacity-reservation warning, and the team's theory is last month's GPU capacity
shortage. The lab's own `prod.yaml` sets the instance type but never `aws_region`; the
region is inherited from the account-level `rhoai-gpu-labs/account.yaml`, which a merged
pull request (#20417) moved to `ca-west-1` between the last good run and the failures.
The agent must notice the item is silent on region, reason that the value comes from a
parent layer, and find the change by searching PRs on the *account*, not the item.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **assuming the effective value comes from the file you read**: the item's
config looks correct and unchanged, so an agent without a model of agnosticv's
account → item merge concludes "config is fine, it must be AWS". The second failure is
adopting the loud capacity reading (the instruction voices it, the log carries a
capacity-reservation WARNING) without distinguishing `Unsupported` from
`InsufficientInstanceCapacity`. Even an agent that finds the inheritance must pick the
right PR: the account-keyword search also returns the item's own unrelated PR (#19862),
and the default `state` is `open`, which returns neither.

## Grounding

- `query_aap2 get_job_log`: composite `job_id` + `controller` on `jobs`.
- `lookup_catalog_item`: the Babylon name `rhoai-gpu-labs.llm-finetune-workbench.prod`
  (from the job name) resolves via the `<item>` segment; the result carries
  `account: rhoai-gpu-labs`, which is the derivable PR keyword, and `path` = prod.yaml.
- `fetch_github_file` on rhpds/agnosticv prod.yaml (seeded at `HEAD` and `main`);
  `account.yaml` is also seeded so an agent that reads it directly sees the value.
- `search_agnosticv_prs`: SKILL.md — reads only `pull_requests`; a PR matches when the
  keyword is a substring of `title` (all files returned) or of at least one `files` entry
  (only matching files returned); effective `state` defaults to `open`. Neither seeded
  closed PR has the account in its title, so both match by file path and the golden
  shows only their matching files (#20417's `docs/cost/regions.md` is dropped). The open
  PR #20488 is excluded by `state: closed`. The expected call pins no argument, so
  `closed`, `all`, or a narrower keyword such as `rhoai-gpu-labs/account.yaml` pass.
- Enum values: controller `east`; verdict category `configuration` (RCA taxonomy).

validate.py WARN, justified: `repos_searched` values are not in the seed because SKILL.md
fixes them as a constant four-element array for every `search_agnosticv_prs` response.

## Contract

Weights 0.3 / 0.7, `ordered-subsequence`.

- `region` (`ca-west-1`) — anchor, in the log.
- `pr` (`20417`) — only via the account-keyed PR search.
- `account-yaml` — the parent layer, in no log.
- `inherited` (derived) — the item is silent on region; the value is inherited.
- `not-capacity` (derived) — Unsupported vs capacity.
- verdict `configuration`, confidence required.
- forbidden `capacity-shortage` (attributed_to excuses rejection sentences) and
  `item-edited` (blaming the item or its own PR #19862).

Mute answer floor: 2 forbidden of 8 graded items → 0.25, reward 0.475.

leakage.py WARN (weak literals), justified: `account-wide`, `fold_markup`, `ncloud_provider`, `worker_instance_count`, `worker_instance_type` are contract keys, logger/file names or standard AgnosticD variable names shared by the API's world (`ncloud_provider`-style tokens are `\n` + a key in serialized YAML), not scenario identity.

Excuses (2026-10-12 generic-excuse fix pass): `attributed_to` holds only specific refutations of the claim -- `capacity-shortage`: "not a capacity shortage", "not a capacity problem", "not out of capacity", "capacity is ruled out", "shortage is ruled out", "the team's assumption is wrong". Each forbidden fact was probed with one sentence that asserts it while carrying hedge words ("suggest", "suspect", "rather than", "theory", "isn't"): `.scratch/probes/113-capacity.md`, `.scratch/probes/113-item.md`; every probe is hit. Golden still 1.000.

## The wrong answer

`.scratch/wrong_113.md`: reads the log, takes the reservation warning as a capacity
shortage, calls the item config correct, verdict `resource_failure`. Scores **0.475**
with golden calls (answer 0.25: region plus the item-edited forbidden it avoids). Golden
answer 1.000.

## Invented

Every literal is invented: job 4172093, GUID `w8nfh`, account directory `rhoai-gpu-labs`,
item `llm-finetune-workbench`, PRs 20417/19862/20488 and their authors, branches and
dates, pool `gpu-sandboxes`, role names `infra_aws_capacity_check`,
`infra_aws_cluster_settings`, `infra_aws_gpu_workers`. Whether a given AWS zone offers a
given instance type is part of this invented world, stated by the seeded error. The
incident class (account-level default override inherited by child items) is invented in
the mould of bench-v4's challenge tranche; no public postmortem is its source, and
nothing comes from bench-v4 or production data.
