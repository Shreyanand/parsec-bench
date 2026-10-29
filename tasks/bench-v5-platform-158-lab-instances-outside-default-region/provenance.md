## What it measures

Whether the agent carries the lab's region from the provisioning record into the EC2 lookup,
instead of relying on `describe_instances`' default region. Three hops across two services:

1. `query_aap2 get_job_log` on east/5148806: successful. The log's first task sets
   `sandbox_name: sandbox5824` and **`aws_region: ap-southeast-2`**. No other result carries the region.
2. `query_aws_account_db {name: sandbox5824}`: account **418092736615**, GUID n7rkd, in use.
3. `query_aws_account describe_instances {account_id: 418092736615, region: ap-southeast-2}`: 3 instances.
   `bastion` (t3.medium) is **stopped**; `node1` and `node2` (m6i.xlarge) are running.

Without `region`, `describe_instances` reads us-east-1 and returns `instance_count: 0`. That reads
as "the lab has no instances" or "it was torn down", which is the wrong answer to escalate. The
honest answer gives the account, the region, the three instances and their states. The stopped
bastion explains the attendee's report.

**Kind: trap.** A documented default argument that silently empties the result.

## Grounding

- platform SKILL.md "/query_aap2": `get_job_log` returns the `get_job` projection plus `log`,
  `log_original_size` and `log_trimmed_size`.
- cloud SKILL.md "/query_aws_account_db": with `name`, reads `sandbox_accounts` by name and
  returns the stored row minus `sandbox_account_id`, with `count` and `truncated`. A filterless
  scan returns both seeded rows, and only one carries GUID n7rkd. The expected call pins no
  argument, so either route counts.
- cloud SKILL.md "/query_aws_account": `region` "Default: `us-east-1`". `describe_instances`
  reads `ec2_instances` where `account_id` and `region` both match, and returns rows exactly as
  stored (minus the storage key) with `instance_count`. With no us-east-1 rows for 418092736615, the
  default-region call returns the documented empty success result.
- **Slot note (coordinator-approved):** the slot offered `lookup_catalog_item` or
  `query_aap2`. `lookup_catalog_item` is a github-service tool, and this task declares cloud
  and platform, so it uses `query_aap2`.
- Seed: platform `jobs` 1 (with log). cloud `sandbox_accounts` 2, `ec2_instances` 3.

## Contract

- tool_calls (0.3), ordered-subsequence (each hop's argument comes from the previous result):
  `query_aap2` {controller: east, job_id: 5148806} (action unpinned), `query_aws_account_db`
  {} (any lookup), and `query_aws_account` {action: describe_instances, account_id: 418092736615,
  region: ap-southeast-2}. `region` is pinned because it is the point, and it is derivable from the log.
- answer (0.7), `fold_markup` on: required `account-id`, `region`, `bastion-id`,
  `bastion-stopped` and `node-type` (m6i.xlarge). Count `instances` (3, derived). Forbidden
  `no-instances` and `torn-down`, written as claims about the lab or account. "us-east-1 has no
  instances" is true, so it is not forbidden (hazard 14).
- Items: 8. Mute 0.3 + 0.7 x 2/8 = 0.475.

## The wrong answer

"The lab is in sandbox5824, AWS account 418092736615. I checked the account's EC2 instances and
describe_instances returned instance_count 0, so the lab has no instances: it looks like it was torn
down after provisioning. Escalate to the cloud team to re-provision the lab." (The default-region
lookup.) Even credited with the golden calls it scores **0.3875** (answer 0.125: only `account-id`
hits; both forbidden facts fire). Its real trajectory would also miss the pinned
`describe_instances` call (no `region`), so the tool component drops to 0.667. Two fresh honest
answers (terse prose, and `Key: value` lines plus a table with "Torn down: No") score 1.000.

## Invented

Every literal is invented: the GUID, job id, job and template names, sandbox names, account ids,
hosted zone, service UUIDs, instance ids, tags and times. `east` is a controller name from the
api.json enum; `ap-southeast-2`, `us-east-1` and the instance types are real AWS names. Nothing comes from
bench-v4 or from production data.
