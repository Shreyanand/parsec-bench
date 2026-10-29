# bench-v5-platform-139-ami-id-pinned-to-one-region

## What it measures

A three-call RCA on a failure class no existing RCA has: a **region-scoped identifier
hard-coded into region-agnostic code**. The role task that launches the workshop's
render nodes passes `region: "{{ aws_region }}"` but pins `image_id: ami-0c7d41e9b25f83a16`, a
literal AMI ID. AMI IDs name an image in one region only. The order that went to
`us-east-1` launched the image; the order that went to `eu-central-1` got
`InvalidAMIID.NotFound` for the same ID.

The two jobs ran the same catalog item from the same commit, so the code cannot explain
the difference by itself. The answer needs both logs, which each carry only their own
region (in the debug line before the launch), and the task file, which shows the
literal ID. The natural wrong inference from the failed log alone is that the image was
deregistered or deleted. The successful log refutes it: the same ID launched more than
two hours after the failure.

## Grounding

- `query_aap2 get_job_log` (`controller: east`, `job_id: 418627` and `418655`): `jobs`
  is read by composite `job_id` + `controller`; the response is the get_job projection
  plus `log*` (platform SKILL.md, "Response contract by action"). Both rows carry the
  same `git_url`, `git_branch` and `git_revision`. The second expected call pins only
  `controller` and `job_id`, because `get_job` on 418655 is a legitimate (if less
  useful) read.
- `fetch_github_file agnosticd/agnosticd-v2 ansible/roles/render_farm_nodes/tasks/main.yml`, with `ref` omitted, resolves to the
  default branch (github SKILL.md). The task file and the role's `defaults/main.yml` are
  seeded under `HEAD`, `main` and the jobs' `git_revision` `9e2a6c41d8b07f35a1c94e6b2d0f7a8c53e1b4d9`, identical content.
- **Path derivability:** the path is a substring of the logs' `task path:` lines; owner
  and repo come from `git_url`. No exemption.
- Enums hit: controller `east`. The error text follows the EC2 API's real wording for
  `InvalidAMIID.NotFound`.

## Contract

- Expected calls: unordered-subset (the two log reads are siblings; the fetch's path is
  pinned, so order is not graded). No forbidden calls.
- Required:
  - `ami-rejected`: the error, from the failed log.
  - `failed-region` and `good-region`: one from each log.
  - `regional-ami` (derived): the ID is hard-coded / region-scoped.
  - `fix` (derived): any per-region resolution of the image.
- Forbidden `ami-retired`: claims that the AMI was deregistered, deleted, removed,
  deprecated or expired. No `attributed_to`; denials are excused by the polarity reading.
- Six items: mute 0.3 + 0.7 x 1/6 = 0.417. Weights 0.3/0.7.

## The wrong answer

> RunInstances failed with InvalidAMIID.NotFound for ami-0c7d41e9b25f83a16. The AMI
> was deregistered overnight, so the role needs a current image ID; update the
> hard-coded value to the new RHEL 9 render image and reorder.

With the golden calls it scores reward **0.533** (answer 0.333). It earns `ami-rejected`
and `regional-ami` ("hard-coded"), misses both regions and the fix, and hits
`ami-retired`. Three fresh honest answers (prose, a table, `Key: value` lines with an
explicit "deregistered: no") score 1.000.

## Invented

Every literal is invented for bench-v5: jobs 418627 and 418655, GUIDs `qpl3n` and
`h8sxt`, account `media_bu`, item `render-farm-workshop`, the role `render_farm_nodes`
and its variables, the AMI ID, the instance IDs and the git revision. AWS region names
and instance type names are real shared system names. Nothing comes from bench-v4 or
from production data.
