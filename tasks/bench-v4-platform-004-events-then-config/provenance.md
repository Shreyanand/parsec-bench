# bench-v4-platform-004-events-then-config

## What it measures

The `get_job_events` leg specifically. Everything the answer needs about *which*
task failed is in the log too — but the **role** is only in the `job_events` row,
so an agent that stops at `get_job_log` cannot supply it. That is the point of the
`role` required fact, and it is why `failed_only: true` appears in the expected
call rather than a bare `get_job_events`.

It also uses the numeric count matcher on a value read from a config file, and
carries a forbidden fact for the wrong host — the seed deliberately makes a
successful second host available so that naming the first host seen is a
distinguishable mistake.

## Grounding

The `job_events` rows carry all thirteen fields the generated
`harness-skills/parsec-platform/schema.json` requires on `JobEvent`, including
`event_key`, `job_id` and `controller`, none of which
`sim-specs/platform/openapi.json` declares — the store-versus-response rule. The
`event_key` values follow the `<controller>-<job_id>-<counter>` shape the seed
helper builds; nothing upstream prescribes a format.

`failed_only` is a declared argument of `query_aap2`'s `get_job_events` action in
`sim-specs/platform/openapi.json`, and 25 real `get_job_events` calls in the
trajectories use it — the argument is attested as the idiomatic one, though this
scenario's data is entirely authored.

## Weighting

`0.3 / 0.7`. The job id and controller are given and the config path is handed
over verbatim, so the calls are cheap; but `failed_only` is a real argument choice
and the answer carries four independent facts.

## Invented

Job id `90405`, the guid `vt8dr`, the hostnames, the role name
`ocp4_cluster_nodes`, the log text, the `default_vars.yml` body, the event rows and
every timestamp. **Nothing comes from the gitignored trace export.**
