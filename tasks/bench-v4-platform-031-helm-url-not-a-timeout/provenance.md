# bench-v4-platform-031-helm-url-not-a-timeout

**Tranche: challenge.** Expected to score below 1.000. The agent failure it exposes
is accepting the symptom's own explanation: a download that times out after ten
retries reads as a transient network fault, and the actual cause is a dead upstream
path composed from two role variables.

## Where it comes from

Converted from **RHDP-002** in `test-artifacts/rh-sre-datasets` (the public
`redhat-et/rh-sre-datasets` repository), a scenario built from a real October-2025
postmortem: an AAP job failed on `ocp4_workload_showroom : Install helm command`
after ten retries, because `mirror.openshift.com` restructured its helm client
directory and the role's templated URL resolved to a path that no longer served a
file.

**Same shape, invented identifiers.** The job id, GUID, catalog item name, cluster,
timestamps and namespace here are all invented; nothing identifying from the source
scenario reaches this directory. What is kept is what makes the failure what it is:
the two variable names, the URL composition, the mirror host, and the fact that other
clients from the same host downloaded successfully in the same window.

## What it targets, in the source dataset's own dimensions

RHDP-002 scores `code_config_understanding: 1`, `cross_source_correlation: 1`,
`multiple_plausible_causes: 1`, `variable_precedence: 1`. A calibration of our
existing thirty scenarios against those dimensions found the suite thin on exactly
the first: **every one of the eight scored RHDP scenarios requires reading config or
code, where only 12 of our 30 did.** This scenario requires it — the two variable
names exist nowhere but the role's `defaults/main.yml`, so an agent that never reads
config cannot supply them.

It is also cross-source by construction: the refutation of "the mirror is down" is
two Splunk rows, and the composition is a GitHub file, and neither is in the job log.

## The forbidden facts, and the one that was dropped

The source scenario's `alternatives.yaml` records three ruled-out causes with
`why_wrong` and contradicting evidence. Two became forbidden facts:

- **mirror-outage** — recorded at plausibility *high*, "the first hypothesis during
  any download timeout". Refuted here by two seeded Splunk rows showing the oc client
  and odo downloading from the same host minutes earlier.
- **transient** — the operational conclusion that follows from the wrong diagnosis,
  and the one that costs a real team another failed provision.

The third, **bastion network connectivity** (plausibility *medium*), was **dropped for
floor arithmetic, not because it is uninteresting**. A forbidden fact is satisfied by
absence, so each one a mute answer collects is free. With the tool weight at 0.3 and
three forbidden facts among eleven, the mute floor computes to
`0.3 + 0.7 × (3/11) = 0.491`; the measured margin is thinner than it looks once the
other facts are counted, and at eight facts with two forbidden the floor is
`0.3 + 0.7 × (2/8) = 0.475`, which is what the gate reports. Adding the third would
have meant adding required facts to pay for it, and the instruction does not ask for
anything more.

**The forbidden forms name the assertion, never the host.** `mirror.openshift.com`
appears throughout the seed — in the job log, the Splunk rows and the config — so
forbidding the bare hostname would defuse its own trap and punish an answer that
correctly explains what it ruled out (hazard 14).

## Derivability

The gate's `check_expected_calls_derivable` initially rejected this scenario: the
`fetch_github_file` call needed an `owner`, `repo` and `path` that appeared in neither
the instruction nor any earlier golden result. Fixed by seeding the route rather than
by handing the values over in the instruction:

- the job log names the failing task, so `ocp4_workload_showroom` is derivable
- the job's `display_name` reaches a seeded `catalog_items` row that supplies
  `owner` and `repo`
- a seeded `repo_search_results` row for `ocp4_workload_showroom` supplies the path

That makes it the four-hop chain the real platform+github traces follow, and the
five expected calls are each reachable from what came before.

Search rows are seeded under **both** `HEAD` and `main`, because `search_github_repo`
filters `ref == "HEAD"` when `ref` is omitted while `fetch_github_file` resolves an
omitted `ref` to the default branch (hazard 20).

## Gate

Golden path 1.000; floors mute 0.475, nocall 0.175, fabricate 0.300 — all inside
their maxima, and fabricate below mute. Zero seed, lint, collision or entanglement
findings.
