# bench-v5-icinga-212-fix-on-main-not-on-pinned-ref

**Kind:** trap. **Services:** icinga, github. **Calls:** 4. **Weights:** 0.3 / 0.7.

## What it measures

Comment author/time reasoning combined with a pinned ref. `mount-latency` on
`nfs-home-dub-2` is CRITICAL ("/home/autofs/proj stat() took 12.4 s").

- An operator comment by `hkowalczyk` (2026-11-15 14:20 UTC) says the autofs false positive
  was fixed in the plugin "on main".
- A later comment by `amensah` (2026-11-17 08:05 UTC) says it came back.
- The service's vars pin `plugin_ref: v3.4.0`.
- On `main` the plugin skips autofs. At `v3.4.0` it does not.

The correct answer: this is still the old false positive, because the check runs the pinned
tag, and the fix exists only on main. An agent that reads only main, or trusts the comment,
concludes either that the fix is live or that 12.4 s must be real NFS latency.

## Grounding

- icinga `get_comments`: reads only `comments`. `host` matches `attrs.host_name` exactly and
  returns host-level and service-level rows (api.json SIMULATION STORE AUTHORITY).
  **The golden call uses host only**, because the README's residual for icinga-048 records
  that `get_comments` with extra arguments flaked on the simulation. The bare host-filtered
  call has not been seen to fail. The expected call pins only `action` and `host`, so an
  agent adding `service: mount-latency` also matches. That call returns the two
  service-level comments, and every graded comment fact comes from those two rows. The
  third, host-level comment (kernel rollout) is a decoy that only the host-only call shows.
- icinga `get_services` with `host` returns `vars.plugin` / `vars.plugin_ref` verbatim.
- github `fetch_github_file`: the plugin is seeded under `HEAD`, `main` (with the autofs
  skip) **and** `v3.4.0` (without it). An omitted ref resolves to the default branch,
  which is main.
- The forbidden actions `get_check_source` and `get_plugin_version` are neither enum values
  nor aliases.
- Validator WARNs, justified: golden calls 0 and 1 return the documented serialized `result`
  string.

## Contract

- Expected calls, `unordered-subset`: `get_services host`, `get_comments host`, fetch the
  plugin (path pinned, ref free), and fetch it with `ref: v3.4.0`. The matcher assigns the
  more specific spec first, so one tag fetch cannot satisfy both fetch specs.
- Required: `pinned-ref`; `fix-only-on-main` (derived from comparing the two refs);
  `false-positive` (with forms that a sentence quoting the comment's "false positive" cannot
  satisfy); `claimant`; `claim-date`; `since` (amensah).
- No counts.
- Forbidden: `real-latency` ("real NFS latency problem", "fix is deployed", ...).
  `attributed_to` holds specific phrases only ("comment claims", "claimed the fix", "not a
  real NFS latency"). The probe "The comment is wrong, not a false positive: the NFS server
  is slow." is hit.
- Mute floor 1/7 = 0.14.

## The wrong answer

"hkowalczyk commented on 2026-11-15 ... the plugin on main does skip autofs, so the fix is
deployed ... this must be a real NFS latency problem" (`.scratch/wrong/212.md`). Reward
0.60: answer 0.43. It misses the pin, the main-versus-tag fact and the verdict, and it hits
the forbidden fact.

## Invented

The host, services, vars, comments, authors, script versions, tag, outputs and epochs are
invented for this task. Nothing comes from bench-v4 or from production data.
