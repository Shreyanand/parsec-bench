# bench-v5-platform-106-yaml-float-version

## What it measures

A three-hop RCA (log, catalog item, agnosticv config) on a failure class no training RCA
has: YAML type coercion. The catalog item says `ocp4_installer_version: 4.20`, unquoted.
YAML parses that as the float `4.2`, so the installer role requests `latest-4.2/...`,
which has never existed, and the download server correctly answers 404. The user
believes the artifact server is flaking and asks for a relaunch. The trap has two
halves:

- accepting the flake theory (a forbidden fact);
- attempting the relaunch through an action `query_aap2` does not have (a forbidden
  call).

## Grounding

- `query_aap2 get_job_log` (`event0`, `915738`): composite `jobs` read. `event0` is an
  api.json controller enum value.
- `lookup_catalog_item`: the job name carries `summit_events.summit-mesh-lab.event`. The
  exact key is the directory `summit-mesh-lab`, or the `<item>` segment of the qualified
  form. `search` is unpinned.
- `fetch_github_file rhpds/agnosticv summit_events/summit-mesh-lab/common.yaml`, `ref`
  omitted. Seeded under `HEAD` and `main`.
- **Forbidden calls:** `query_aap2` with `action` `relaunch_job`, `relaunch` or
  `launch_job`. None is in the api.json action enum, which is get_job, get_job_log,
  get_job_events and find_jobs. The simulation would return the in-band "Unknown action"
  error, but attempting the call is the wrong move the instruction tempts.

## Contract

- Expected calls: ordered-subsequence over the three hops. Weights 0.3/0.7.
- Required:
  - `url-4-2`: from the log.
  - `float-parse`: derived. The YAML coercion explanation.
  - `quote-fix`: requires having seen the unquoted line.
- Verdict: `configuration`, exclusive, with a confidence.
- Forbidden fact `server-blamed`: "artifact server is down", "outage", "transient",
  "flaky" and similar. No `attributed_to`; the golden answer declines the theory without
  those words.
- No citation item (the group's five citations are in 101-104 and 107). The golden
  answer still cites the file and line.

## The wrong answer

> HTTP 404 ... for the latest-4.2 path. The artifact server is flaking right now, so this
> is transient; I relaunched the job. connectivity_failure, medium.

With the golden calls, `score.py` gives **0.44** (answer 0.2). With the wrong
transcript (log read, then `relaunch_job`), reward is **0.14**: the tool component is
zeroed by the forbidden call.

## Invented

Every literal is invented for bench-v5: job 915738, GUID `t5gwe`, account
`summit_events`, item `summit-mesh-lab`, the host `artifacts.labcdn.example`, the bastion
domain and the git revision.
