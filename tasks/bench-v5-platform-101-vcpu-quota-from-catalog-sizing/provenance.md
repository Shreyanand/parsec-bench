# bench-v5-platform-101-vcpu-quota-from-catalog-sizing

## What it measures

A three-hop RCA chain (log, catalog item, agnosticv config) on a failure class no
training RCA has: an AWS per-account vCPU quota (`VcpuLimitExceeded`). The log supplies
the limit (64). Only the catalog item's `common.yaml` supplies the sizing, and the
answer is a sum over three sizing lines (3 x 16 + 3 x 8 + 4 = 76) compared against the
limit. The agnosticd config defaults are seeded as a decoy: a fetch of
`default_vars.yml` gives a 22 vCPU total (m6i.large 2 + 3 x m6i.xlarge 12 + 1 x m6i.2xlarge
8) that fits under the limit. That is the wrong-file mistake. (Corrected 2026-10-13: this
said 44 vCPU, which the seed never gave.)

## Grounding

- `query_aap2 get_job_log` (`controller: west`, `job_id: 238114`): `jobs` is read by
  composite job_id + controller. The response is the get_job projection plus `log*`
  (platform SKILL.md, "Response contract by action"). The row carries the git fields.
- `lookup_catalog_item`: the job name carries `analytics_bu.ocp-lakehouse-bench.prod`.
  Its exact key is the normalised `directory` `ocp-lakehouse-bench`, and the
  `<account>.<item>.<stage>` form also resolves to it (github SKILL.md). `search` is
  unpinned because an agent may legitimately phrase it either way.
- `fetch_github_file rhpds/agnosticv analytics_bu/ocp-lakehouse-bench/common.yaml`,
  with `ref` omitted, resolves to the default branch. Every file is seeded under `HEAD`
  and `main`.
- Enums hit: controller `west`. The verdict uses a TAXONOMY member.

## Contract

- Expected calls: ordered-subsequence over the three hops. Only the fetch pins
  owner, repo and path.
- Forbidden call: fetching the agnosticv path from `agnosticd/agnosticd-v2`. This is the
  wrong-repository move for a catalog-item file, analogous to platform-003's guard.
- Required: `error-code` is the log literal. `why-over` is derived: it states the
  comparison, not just the numbers.
- Counts: `limit` is 64, from the log. `requested` is 76, derived from the fetch.
- Citation: `rhpds/agnosticv:analytics_bu/ocp-lakehouse-bench/common.yaml:19`.
  `gen_101.py` counts the line from the seeded text (`worker_instance_type:`).
- Verdict: `resource_failure`, exclusive, confidence required.
- Forbidden facts: the defaults total and an "AWS outage" reading.
- Weights 0.3/0.7.

## The wrong answer

> VcpuLimitExceeded, limit 64; the config defaults give about 22 vCPU, which fits, so this
> is a transient AWS capacity shortage. resource_failure, medium.

With the golden calls it scores reward **0.650** (answer 0.500). It misses `why-over`,
the `requested` count and the citation, and hits `aws-outage`. It does not hit
`defaults-total`: it attributes the 22 vCPU to the config defaults, which is true of that
file, so no form may catch it (hazard 14). The same answer with "44 vCPU" (an
arithmetically wrong reading of the defaults) scores 0.5625, through the `44 vCPU` form;
that form was briefly replaced and is restored (2026-10-13 review remedy R1, see below).

## Invented

Every literal is invented for bench-v5: job 238114, GUID `wd4kx`, account `analytics_bu`,
item `ocp-lakehouse-bench`, config `lakehouse-bench`, the stack and resource names, the
request id, the git revision, the sizing and the limit. Nothing comes from bench-v4 or
from production data.
