#!/bin/sh
# SPDX-License-Identifier: LicenseRef-PARADOX-NC-Research-1.0
# Run one frozen confirmatory experiment through the guard (paradox run), at low
# priority, with a log and the process exit status, then apply the frozen
# analysis (provenance table, decision rules, figures, SHA-256 manifest).
# Usage: scripts/m3_run.sh EXP-00N   (EXP-004 also reads results/EXP-002)
set -u
exp="$1"
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root" || exit 2
out="results/$exp"
if [ -e "$out/results.json" ]; then
  echo "refusing: $out/results.json already exists (never overwrite raw results)" >&2
  exit 4
fi
mkdir -p "$out"
start="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
nice -n 10 .venv/bin/paradox run --config "research/experiments/$exp/config.json" --out "$out" --pdf >"$out/run_log.txt" 2>&1
status=$?
end="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
printf '{"experiment_id": "%s", "command": "nice -n 10 .venv/bin/paradox run --config research/experiments/%s/config.json --out %s --pdf", "wrapper_started_utc": "%s", "wrapper_finished_utc": "%s", "exit_status": %d, "git_revision": "%s"}\n' \
  "$exp" "$exp" "$out" "$start" "$end" "$status" "$(git rev-parse HEAD)" >"$out/exit_status.json"
if [ "$status" -ne 0 ]; then
  echo "$exp: paradox run exited with status $status; see $out/run_log.txt" >&2
  exit "$status"
fi
extra=""
[ "$exp" = "EXP-004" ] && extra="--exp002 results/EXP-002"
nice -n 10 .venv/bin/python -m paradox.analysis "$exp" "$out" --exit-status "$status" $extra >>"$out/run_log.txt" 2>&1
astatus=$?
# refresh the SHA-256 manifest last, so it also covers the completed log
.venv/bin/python -c "import sys; from paradox.analysis import write_sha256_manifest; write_sha256_manifest(sys.argv[1])" "$out"
echo "$exp: run exit $status, analysis exit $astatus"
exit "$astatus"
