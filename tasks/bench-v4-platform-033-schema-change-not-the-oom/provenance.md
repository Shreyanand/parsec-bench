# bench-v4-platform-033-schema-change-not-the-oom

**Tranche: challenge.** Expected to score below 1.000. The agent failure it exposes
is stopping at the loudest anomaly in the logs. A test worker was killed out of
memory minutes before the breaking merge, and that is the most alarming line in the
evidence — but it is why the change was not stopped, not why provisioning fails.

## Where it comes from

Converted from **RHDP-008**, built from a real postmortem: a pull request migrated
the ansible control plane schema from `ansible_control_plane.type/secret` to an
`ansible_controllers` list plus `ansible_controller_select_mode`, and the Babylon
Anarchy governor's own defaults were left reading the removed field. Every catalog
item goes through the governor, so all of them failed at once. The PR merged despite
its automated tests failing with OOM errors.

**Same shape, invented identifiers**, with one deliberate exception: the PR number
19034 is kept, because it is a public pull-request number in a public repository and
it is the value that makes the finding actionable. Job id, GUID, catalog item,
controller, hostnames, credentials and timestamps are invented.

## What it targets

RHDP-008 carries `variable_precedence: 2`, the highest in the source set, and
`code_config_understanding: 2`. The calibration of our first thirty scenarios found
both dimensions thin: all eight scored RHDP scenarios require reading config where
only 12 of our 30 did, and nothing in our suite tested one schema superseding
another.

The chain is three genuinely derived calls: the job log names the undefined field,
the field name reaches the pull request through `search_agnosticv_prs`, and the PR's
own file list supplies the owner, repo and path for the governor defaults.

## The trap is two-sided, deliberately

The source's `alternatives.yaml` records "OOM errors on test infrastructure are the
real root cause" at plausibility **high**. So the OOM is seeded — a killed worker, a
required check reporting no result, a review override — because a trap whose tempting
answer has no evidence behind it is not a trap.

Forbidding "the OOM is the root cause" only punishes the wrong answer. So the
contract also **requires** the agent to place the OOM correctly, as the reason a
breaking change reached production. An agent that ignores the OOM entirely fails
`tests-role`; one that blames it fails `oom-as-cause`. Only correctly demoting it to
a contributing factor satisfies both.

The forbidden forms require a causal construction (`root cause is the OOM`, `caused
by the out of memory`, `due to the OOM`) rather than the bare words, and
`attributed_to` excuses the sentence that names the OOM in order to demote it. That
is `-032`'s lesson applied in advance: there, the bare form `registry outage` caught
the scenario's own golden answer, and the fix was to require a copula so an assertion
is distinguishable from a refutation.

The third alternative, an AAP controller version mismatch (*medium*), is the second
forbidden fact. The fourth, collection incompatibility (*low*), was dropped for floor
arithmetic as in both earlier conversions.

## Weights

`0.25 / 0.75`, not the usual `0.3 / 0.7`. Five required facts and two forbidden ones
put the mute floor at exactly 0.50 under a 0.3 tool weight — passing, but with no
margin. The chain here is three real derivations, which argues for a higher tool
weight, but the discrimination lives in the answer, so the weight moved rather than
the facts. Adding a sixth fact would have meant asking for something the instruction
does not, which is the defect item 4 describes. CLAUDE.md caps a forbidden-bearing
contract at 0.35; 0.25 is inside it.

## One thing the gate caught

`bench.lint` rejected the first instruction for saying the failures began "this
evening". Seed timestamps are absolute and age, so the scenario would have been
correct on the day and wrong a month later. Removed rather than fixed by editing
timestamps, which only resets the same clock (item 3).

## Gate

Golden path 1.000; floors mute 0.464, nocall 0.214, fabricate 0.250 — all inside
their maxima and fabricate below mute. Zero findings.
