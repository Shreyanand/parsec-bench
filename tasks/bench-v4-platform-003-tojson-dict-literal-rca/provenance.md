# bench-v4-platform-003-tojson-dict-literal-rca

## What it measures

The third `KNOWN_PATTERNS` RCA, and the one where the right repository is *not*
the usual content repo. It also asks for a recommendation, which the playbook
requires and the previous two scenarios do not.

## Grounding

`vendor/parsec/src/tools/aap2_fix.py`, `KNOWN_PATTERNS[2]`:

- its regex is `configuration string is not in JSON format`, which the seeded log
  matches;
- its explanation is "Python dict literal string piped through to_json filter. In
  ansible-core 2.19+, this produces a quoted string instead of a JSON object.
  Convert the Python dict literal to a proper YAML dict." The `dict-literal` fact
  is derived from the first half and `the-fix` from the second;
- it is the **only** pattern carrying `before`/`after`
  (`aap2_fix.py:83-84`): `some_var: "{{ python_dict_string | to_json }}"` becomes
  `some_var: "{{ proper_yaml_dict | to_json }}"`. The seeded task is that `before`
  shape with concrete values, and `the-fix` fact's forms come from the `after`;
- its `repo` is `agnosticd/cloud_provider_openshift_cnv` (`aap2_fix.py:81`), not
  `_AGNOSTICD_V2_REPO`. That is why the forbidden call list names
  `agnosticd/agnosticd-v2` here: an agent that reaches for the usual content repo
  by habit fetches the wrong one, and this is the one scenario where that habit is
  the mistake rather than the wrong *owner*.

The path shape `roles/<role>/tasks/main.yml` is attested at `aap2_fix.py:198`.

`application_bug` is the taxonomy member for a wrong value committed in role
source. Note it is in `TAXONOMY_EXCLUSIVE`, so naming a second operational
category here does fail the fact.

## Weighting

`0.3 / 0.7`. The job id and controller are given; the repo and path are derived,
and the repo is the discriminating half.

## Invented

Job id `90404`, the guid `h7m2q`, the role name `create_inventory`, the log text,
the task file body and every timestamp. The role name is invented rather than
attested — `aap2_fix.py` gives only the `<role>/tasks/<task>.yaml` shape, not any
particular role. **Nothing comes from the gitignored trace export.**
