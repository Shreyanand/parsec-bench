# bench-v4-platform-032-shared-secret-not-a-registry-outage

**Tranche: challenge.** Expected to score below 1.000. The agent failure it exposes
is diagnosing per-item when the evidence is cross-item: three unrelated catalog
items failing identically at once is only explicable by something they share, and
the shared thing is visible nowhere in any one job's log.

## Where it comes from

Converted from **RHDP-007** in `test-artifacts/rh-sre-datasets`, built from a real
postmortem: the OpenShift console team rotated the pull secret behind
`ocp4_token` without notifying RHDP operations, and all 177 catalog items that
depend on it for registry authentication began failing at once.

**Same shape, invented identifiers.** Job ids, GUIDs, catalog item names,
timestamps and the affected count are invented; the source names real people and
real CIs and none of that appears here. What is kept is the mechanism: one shared
vault-encrypted credential, referenced from catalog config, whose stored copy has
gone stale while the config referencing it is unchanged and correct.

## What it targets

RHDP-007 scores every dimension at 1 and is the source dataset's joint-easiest at
4, which is why it was chosen second: it establishes the conversion at the low end
before the harder ones. It still requires reading config — the credential name and
its include path exist nowhere but the catalog file — which the calibration found
our suite thin on: all eight scored RHDP scenarios need it where only 12 of our
first 30 did.

The discriminating step is breadth. One item failing is an item problem; three
failing the same way in one window is a shared-dependency problem. That inference
needs `find_jobs` as well as `get_job_log`, and an agent that reads one log
carefully and stops cannot reach it.

## The forbidden facts

From the source's `alternatives.yaml`, which records three ruled-out causes:

- **registry-outage**, plausibility *high* — the first reading of any registry auth
  failure. Refuted by the log: a token being *refused* means the registry answered,
  which an unreachable registry does not.
- **ssh-credentials**, plausibility *medium* — the errors are about image pulls, not
  shell access. An agent that reads "authentication" without reading *which*
  authentication lands here.

The third, TLS certificate rotation on the SSO endpoint (*low*), was dropped for
floor arithmetic: a forbidden fact is free to a mute answer, so a third would have
needed more required facts to pay for it, and the instruction asks for nothing more.
Same trade as `-031` records.

**The forbidden forms require a copula or a causal preposition**, and that was found
the hard way. The bare form `registry outage` caught this scenario's *own golden
answer*, which says "so this is not a registry outage" — hazard 12, a forbidden form
colliding with an honest refutation. Narrowing was tested as item 8 prescribes,
against seven differently-phrased fabrications and six honest refutations rather
than the one answer in hand:

| forms | fabrications caught | honest answers wrongly caught |
|---|---|---|
| bare (`registry outage`, `registry is unavailable`, …) | 6 of 7 | **4 of 6** |
| copula/preposition forms | **7 of 7** | **0 of 6** |

Strictly dominant, so it is not the usual trade. The forms also name the assertion
rather than the host: `registry.redhat.io` is throughout the seed, so forbidding the
bare hostname would defuse its own trap (hazard 14).

## Two authoring notes

**No verdict fact, deliberately.** The source's category is `credential`. Our
taxonomy offers both `secrets` (the cause) and `authentication_failure` (the
symptom), and an agent choosing either is defensible — so grading the choice would
penalise a reasonable answer, which is the failure mode that cost `-014` and `-016`
points earlier. The mechanism is required in prose instead.

**The config lives in `prod.yaml`, not `common.yaml`.** The gate's
`check_expected_calls_derivable` rejected the first draft: `lookup_catalog_item`
returns the catalog item's `prod.yaml` path plus bare filenames in `files`, so a
composed `common.yaml` path is derivable by no agent. Putting the config where the
lookup already points fixes it without handing anything over in the instruction.

**The credential's value is opaque on purpose.** The seeded config says the token is
ansible-vault encrypted in the include, so the agent reasons from the shared
*reference* rather than from the secret — which is what the real responders had to
do, and what the source records as a contributing factor.

## Gate

Golden path 1.000; floors mute 0.475, nocall 0.175, fabricate 0.300 — all inside
their maxima and fabricate below mute. Zero findings.
