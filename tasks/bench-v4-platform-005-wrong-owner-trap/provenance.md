# bench-v4-platform-005-wrong-owner-trap

## What it measures

The single most common documented wrong move in the trajectories: fetching from
`rhpds/agnosticd-v2`, which does not exist, when the AgnosticD content repository
is `agnosticd/agnosticd-v2`. **21 real `search_github_repo` calls 404'd on exactly
that owner/repo pair**, more than any other failure signature in the corpus.

The trap is graded twice over, on purpose. `tool_calls.forbidden` catches the wrong
call on the wire and zeroes the whole `tool_calls` component; a forbidden answer
fact catches an agent that guessed the owner, got a 404, retried correctly, and
then still reported the wrong repository in its answer.

## Grounding

`vendor/parsec/src/tools/aap2_fix.py:14` defines
`_AGNOSTICD_V2_REPO = "agnosticd/agnosticd-v2"`. That constant is the authority for
the correct owner, and every `PatternMatch` in that module that names the content
repo uses it.

The wrong pair is not invented either: it is what the observed agent actually
tried, 21 times, and `git`-visible parsec source never spells it that way.

## Weighting

`0.3 / 0.7`, and the first draft got this wrong in a way worth recording.

The argument for weighting tool_calls heavily here is real — the catalog lookup and
the repository it resolves to *are* the exercise — so the scenario was first
authored at `0.5 / 0.5` with two required-side answer items and one forbidden fact.
**The gate refused it:** floor_mute measured `0.667` against a maximum of `0.50`,
and floor_fabricate `0.500` against `0.35`. With a forbidden fact present, a tool
weight of 0.5 pays a mute agent two thirds of the reward, which is what CLAUDE.md
means by a forbidden fact and a high tool weight competing for the same headroom.

The fix followed the rule rather than the threshold: the instruction was extended to
ask for two further facts that only the defaults file supplies (the admin user and
the operator channel), which made the scenario *harder*, and the tool weight came
down to 0.3. Measured after: golden `1.000`, floors mute `0.440`, no-call `0.140`,
fabricate `0.300`. No threshold was touched and no forbidden fact was weakened.

## Invented

The catalog item name `agd-v2.ocp4-workload-adv-dev-suite.prod`, the role path, the
`defaults/main.yml` body, the Gitea version `1.22.3` and the operator channel
`latest`. The admin user `opentlc-mgr` is the conventional RHDP administrative
account name and is used here as an ordinary seed literal. The workload role name
follows AgnosticD's `ocp4_workload_*` convention;
`ocp4_workload_advanced_developer_suite` itself is invented. **Nothing comes from
the gitignored trace export.**
