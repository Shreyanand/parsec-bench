# bench-v5-platform-121-near-miss-pick-partner-repo

## What it measures

Choosing among several catalog near-misses by what the user actually needs, then following
the chosen entry's own fields. `lookup_catalog_item` for `ansible-lightspeed-coding-lab`
returns `found: false` with four `similar_items`: an AWS edition, an Azure edition, an
internal single-user **CNV sandbox** edition (in `rhpds/agnosticv`, account `sandboxes_gpte`),
and the **partner CNV** edition (`repo: partner-agnosticv`, account `partner_ansible`). The
user wants "the one partners run on OpenShift Virtualization". Two entries say "cnv", and only
one is the partner's. A `similar_items` row carries no `owner`, so the agent must combine
`rhpds` with the row's `repo` and `path` to fetch the right `common.yaml`. The asked values
(25 attendees, OpenShift 4.17) differ in each edition's file, so picking the wrong row shows
up in the answer.

Most of the weight is on the selection (required edition name, repo, and both values; two
forbidden facts for the decoy editions' values). The forbidden call, fetching the partner
path from `rhpds/agnosticv`, is a secondary guard.

**Kind: trap.** Two plausible wrong picks (the first match, or the other "cnv").

## Grounding

- github SKILL.md "/lookup_catalog_item": no `catalog_items` row matches the normalised search,
  so the response is `found: false`, the `similar_items` rows whose normalised `name` contains
  the search (all four), and the complete-index miss message. Each element has exactly
  `name`, `repo`, `account`, `path`.
- "/fetch_github_file": exact (owner, repo, path, effective ref). All three editions'
  `common.yaml` are seeded under HEAD and main. `rhpds/agnosticv` with the partner path has no
  row, so it returns the in-band not-found error.
- validate.py WARN: the lookup's `message` is not in the seed. It is the documented
  complete-index miss message (SKILL.md "Concrete JSON example"), so the WARN is justified.
- leakage.py WARN: the weak literals `cloud_provider` and `openshift-workloads` are agnosticv
  vocabulary, not scenario identity.

## Contract

- tool_calls (0.25; 0.3 at import), ordered-subsequence: `lookup_catalog_item` {search:
  ansible-lightspeed-coding-lab}, then `fetch_github_file` {rhpds, partner-agnosticv,
  partner_ansible/ansible-lightspeed-coding-lab-cnv/common.yaml}. Forbidden: the same path
  from `rhpds/agnosticv`.
- answer (0.75; 0.7 at import): required `edition` (forms that exclude the `-cnv-sandbox` suffix),
  `partner-repo`, `ocp-version` (4.17 with a version noun). Count users = 25. Forbidden
  `aws-values` and `sandbox-values`. attributed_to is limited to "don't plan with",
  "do not plan with", "not the partner edition", so an answer that names a decoy edition and
  states its values as the answer is not excused.
- Probe: "The partner edition installs OpenShift 4.18, not 4.17." hits `aws-values`.

## The wrong answer

Picking the CNV sandbox: "...the OpenShift Virtualization edition is
ansible-lightspeed-coding-lab-cnv-sandbox in rhpds/agnosticv ... hosts 1 attendee, and it
installs OpenShift 4.16", with the lookup and a fetch of the sandbox's common.yaml, scores
reward **0.25** (0.27 at import weights). The golden answer scores 1.0. Mute floor (validate.py): answer 0.33, reward 0.50 with golden calls (0.53 at import weights).

## Invented

Every literal is invented: the four edition names, the `partner_ansible` account, the
partner-cnv-emea pool and the config values. `rhpds/partner-agnosticv` is a real repository
name, listed in the bundle's `repos_searched`. Nothing comes from bench-v4 or from
production data.

## Gate exemptions

- expected-call-underivable: fetch_github_file.owner=rhpds — parsec returns repos as owner/repo (`vendor/parsec/src/tools/github_files.py:259` builds `similar_items[].repo` as `f"{m['owner']}/{m['repo']}"`, i.e. `rhpds/partner-agnosticv`); this seed's `similar_items.repo` is the bare `partner-agnosticv`, under the `rhpds` org, by design ("What it measures": the agent must combine `rhpds` with the row's `repo` and `path`). The agent's own tool descriptions name the org: `lookup_catalog_item` "Searches rhpds/agnosticv, partner-agnosticv, zt-ansiblebu-agnosticv, and zt-rhelbu-agnosticv", and `fetch_github_file`'s `owner` example is `'rhpds'` (owner-approved 2026-10-13, `owner-decisions.md` 2b and section 3, platform-121).
- expected-call-underivable: fetch_github_file.path=partner_ansible/ansible-lightspeed-coding-lab-cnv/common.yaml — agnosticv item layout: the chosen `similar_items` row (`ansible-lightspeed-coding-lab-cnv`, repo `partner-agnosticv`) gives the item directory `path` `partner_ansible/ansible-lightspeed-coding-lab-cnv`, and every agnosticv item keeps its shared configuration in `common.yaml` there, the file parsec's `fetch_github_file` description names first ("agnosticv catalog item configs (common.yaml, prod.yaml)"); a `similar_items` row carries no `files` list, so the G4 `path` + `files[i]` join cannot apply (owner-approved 2026-10-13, convention case, `owner-decisions.md` 2b(4)).
