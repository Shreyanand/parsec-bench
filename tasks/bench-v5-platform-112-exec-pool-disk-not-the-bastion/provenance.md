# bench-v5-platform-112-exec-pool-disk-not-the-bastion

## What it measures

A four-hop RCA whose trap is host locality. An installer extract fails with
`[Errno 28] No space left on device`, and the instruction voices the obvious reading —
the lab's bastion filled up. The failing task ran on `localhost`, i.e. inside the job's
execution-environment container on an AAP execution node; the bastion reports 4% used.
The catalog item pins its jobs to instance group `exec-pool-b`, and only the
controller's own Splunk logs show that pool's `/var/lib/containers` at 100% because the
podman image-prune timer was left disabled after a maintenance. The agent must place
the error on the right host, find where the item's jobs run, and read platform-side logs
rather than lab-side config.

## Tranche

**Challenge.** Expected to score below 1.0 for a good agent. The agent failure it
exposes is **misattributing where an error happened**: ENOSPC reads as the provisioned
host's disk, the instruction names the bastion, and the catalog item has a
`bastion_root_volume_size` knob right there to turn. The refutation needs two
inferences no single string states (a `localhost` fatal is controller-side; the
bastion's 4% line) and a hop to a log source — `search_aap2_logs` — that most agents
never reach for when a job log already carries an error. Good agents commonly reject
the bastion but stop at "the execution node's disk is full" without the pool, the
cause (prune timer), or the count.

## Grounding

- `query_aap2 get_job_log`: composite `job_id` + `controller` on `jobs` (platform SKILL.md).
- `lookup_catalog_item` → `fetch_github_file`: lookup returns `path` = the item's
  `prod.yaml`; the instance group is there (seeded under `HEAD` and `main`).
- `query_splunk search_aap2_logs`: SKILL.md "Store reads" — reads only
  `splunk_aap2_log_entries`; a row matches when the request strings (`controller`, then
  `guid` and `search_terms` when given) occur anywhere in the stored row as raw text;
  `earliest`/`latest` affect execution only and are never part of `query`; projection is
  `time`, `controller`, `level`, `logger`, `message` (no seeded row carries a task or
  stdout). The golden passes `search_terms: "exec-pool-b"` (derivable from prod.yaml)
  and gets rows 1-5 and 7, newest first. The expected call pins only `action` and
  `controller: west` (from the instruction), so an agent searching without terms or with
  `aap-exec` still passes. One `exec-pool-b` row is seeded on controller `east` so it is
  excluded by the `west` filter; the pool-a success row does not mention `exec-pool-b`
  and is reachable only by a broader search (pool-a's 38% is also in the capacity row).
- Enum values: controller `west`; index `federated:rh_pds-001_aap`.

## Contract

Weights 0.3 / 0.7, `ordered-subsequence`.

- `instance-group` — `exec-pool-b`, only in prod.yaml / Splunk.
- `containers-full` — `/var/lib/containers` at 100%, only in Splunk.
- `prune-disabled` — prune timer off since MW-4471, only in Splunk.
- `localhost-not-bastion` (derived) — the locality inference.
- `fix-wont-help` (derived) — the operational judgement on the colleague's change.
- count `failed-jobs` = 6 (window 8).
- forbidden `bastion-disk` (attributed_to excuses rejection sentences) and
  `installer-corrupt`.

validate.py WARN, justified: the Splunk golden's `query` and `index` values are not in the
seed because SKILL.md "Generated query rules" builds them from the request
(`index=federated:rh_pds-001_aap "west" "exec-pool-b" | spath | sort -_time`) and fixes
`index` by action; they are documented derivations, not authored data.

Mute answer floor: 0.25 of the answer component (2 forbidden of 8), reward 0.475.

leakage.py WARN (weak literals), justified: `awx.main.dispatch`, `execution-environment`, `failed-jobs`, `fold_markup`, `ncloud_provider`, `re-run` are contract keys, logger/file names or standard AgnosticD variable names shared by the API's world (`ncloud_provider`-style tokens are `\n` + a key in serialized YAML), not scenario identity.

Excuses (2026-10-12 generic-excuse fix pass): `attributed_to` holds only specific refutations of the claim -- `bastion-disk`: "is not the bastion", "wasn't the bastion", "bastion did not run out", "bastion is not full", "colleague's diagnosis is wrong", "would not free". Each forbidden fact was probed with one sentence that asserts it while carrying hedge words ("suggest", "suspect", "rather than", "theory", "isn't"): `.scratch/probes/112-bastion.md`, `.scratch/probes/112-corrupt.md`; every probe is hit. Golden still 1.000.

## The wrong answer

`.scratch/wrong_112.md`: reads the job log, blames the bastion's disk and endorses the
volume increase. Scores **0.3875** with golden calls (answer 0.125). Golden answer 1.000.

## Invented

Every literal is invented: job 2817734, GUID `t3vkb`, catalog item
`edge-ai-inference-lab`, hostnames under `edge-labs.example.net` and
`west.rhdp.example.net`, instance groups `exec-pool-a`/`exec-pool-b`, maintenance id
MW-4471, the `instance_group` deployer key, the role `ocp4_installer_fetch` and every
figure. The incident class (execution-node disk exhaustion after image pruning was
disabled) is invented in the mould of bench-v4's challenge tranche; no public postmortem
is its source, and nothing comes from bench-v4 or production data.
