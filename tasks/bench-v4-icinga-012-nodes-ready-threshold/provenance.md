# bench-v4-icinga-012-nodes-ready-threshold

## What it measures

Comparing live state against a *configured* threshold, and computing the margin
between them. An answer that reuses the alert's own wording ("22 of 25 Ready") without
reading the GitOps definition cannot supply the warn or critical lines, and cannot
compute how much headroom is left.

## The facts that prove the GitHub leg happened

`expectedNodes` (25) appears in the alert output too, so it proves nothing.
`warnBelowReady` (24) and `critBelowReady` (20) appear **only** in the definition, and
`margin` (2) is derived from the live count and the critical line together — stated by
neither source.

## Grounding

`vendor/parsec/src/tools/icinga.py:97-104` for the accepted actions. The
`OCP Prod Nodes Ready` display name and the `Infra Grafana Cluster us-east-1` host are
the shapes a real 9-call trajectory investigates. The GitOps `CheckDefinition` document
is authored, following the Icinga-as-GitOps arrangement the `icinga-triage` playbook
describes (`skills/icinga-triage/SKILL.md`, which pairs live Icinga state with "Icinga
GitOps config from GitHub").

## The forbidden fact is about severity, not fabrication

This is the one shape B scenario where the state is WARNING rather than CRITICAL. Three
unready nodes sounds alarming, and an agent that escalates without reading the
thresholds says so. `wrong-severity` catches that; it is a wrong *reading*, which is
the failure this scenario is built to detect.

## Weighting

`0.3 / 0.7`. Both identifiers are handed over. Two calls, four answer facts, three of
which need the definition.

## Invented

The node counts 25/22, the thresholds 24 and 20, the 300-second interval, the check
definition document and its path. **Nothing comes from the gitignored trace export.**
