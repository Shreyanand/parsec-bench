# bench-v4-platform-034-rate-limit-not-an-outage

**Tranche: challenge.** Expected to score below 1.000. Two failures it exposes, and
an agent can fall into either: calling an AWS throttling error an AWS outage, and
mistaking the loudest number in the evidence for the cause.

## Where it comes from

Converted from **RHDP-003**, built from a real postmortem: a mass cleanup launched
~300 destroy jobs at once, each making three Route53 `ListResourceRecordSets` calls,
which saturated the account-wide 5-requests-per-second limit. Failed AnarchyRun
objects then accumulated in etcd to 4.77 GB of a 6 GB quota, because the cleanup
policy removes successful runs only.

**Same shape, invented identifiers**, and one deliberate change of scale: the source's
~300 concurrent jobs became **8** seeded rows. A count fact has to match what the
store can actually serve, and the mechanism is unaffected -- eight jobs each making
three calls inside 21 seconds still breaches five per second, and the contract's
`three-lookups` fact is what makes that arithmetic explicit. The hosted zone is
renamed; the record count and the etcd figures are kept because they are the
refutation and the cascade.

## What it targets

RHDP-003 carries `cross_source_correlation: 3`, the joint-highest in the source set,
and `multiple_plausible_causes: 2`. The calibration of our first thirty found the
suite thin on cross-source work: 15 of 30 used a single tool. This one needs the job
list for the burst, one job log for the error, and the catalog config for the two
settings that cause it -- and no single source carries the diagnosis.

## Two traps, both seeded

- **aws-outage**, plausibility *high* in the source. Refuted by a seeded Splunk probe:
  one isolated call against the same hosted zone in the same window returns 3,543
  records in 412ms. Throttling and unavailability are different failures, and the
  probe settles which one this is.
- **etcd-as-cause**. The instruction deliberately repeats the worry that the cluster
  is running out of etcd space, and 4.77 GB of a 6 GB quota is the most alarming
  figure in the evidence. It is downstream: the runs accumulated *because* they
  failed. This is the same shape as RHDP-001's operator stall and `-033`'s OOM, and it
  is the failure mode the source dataset's rubrics ask about most often -- whether the
  agent distinguished a cascading symptom from its cause.

Both forbidden facts require a copula or causal preposition rather than the bare
words, with `attributed_to` on the outage fact excusing the sentence that names the
possibility in order to dismiss it. That is `-032`'s lesson applied in advance: there
the bare form `registry outage` caught the scenario's own golden answer.

The third alternative, DNS zone corruption (*medium*), and the fourth, network
connectivity (*low*), were dropped for floor arithmetic, as in all three earlier
conversions. Nine facts with two forbidden gives a mute floor of 0.456; a third
forbidden fact would need more required facts to pay for it and the instruction asks
for nothing more.

## Gate

Golden path 1.000 on the first run; floors mute 0.456, nocall 0.156, fabricate 0.300
-- all inside their maxima and fabricate below mute. Zero findings. First conversion
to pass the gate without an iteration, which is what the three earlier ones bought.
