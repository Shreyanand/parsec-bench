#!/bin/bash
# Harbor verifier entrypoint for an authored bench scenario.
#
# Writes /logs/verifier/reward.json (the four scalars Harbor reads),
# reward.txt, and reward-detail.json (why the number is what it is).
#
# Copied verbatim into every scenario by scripts/bench-new.py; the tracked
# original is src/bench/templates/test.sh.
set -o pipefail
mkdir -p /logs/verifier
python3 /tests/verify.py \
  --expected /tests/expected.json \
  --agent-logs /logs/agent \
  --out /logs/verifier
exit $?
