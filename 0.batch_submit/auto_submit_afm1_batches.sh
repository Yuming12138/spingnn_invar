#!/bin/bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ARRAY_SCRIPT="${ROOT_DIR}/0.batch_submit/submit_afm1_array.sh"

if [ ! -f "${ARRAY_SCRIPT}" ]; then
  echo "Missing array script: ${ARRAY_SCRIPT}"
  exit 1
fi

TOTAL="${TOTAL:-505}"
BATCH_SIZE="${BATCH_SIZE:-10}"
CONCURRENCY="${CONCURRENCY:-1}"
POLL_SECONDS="${POLL_SECONDS:-60}"

submit_batch() {
  local start="$1"
  local end="$2"
  local intensity="$3"
  local job_id
  job_id=$(sbatch --array="${start}-${end}%${CONCURRENCY}" --export=ALL,INTENSITY="${intensity}",ROOT_DIR="${ROOT_DIR}" "${ARRAY_SCRIPT}" | awk '{print $4}')
  echo "${job_id}"
}

wait_jobs() {
  local job_ids="$1"
  while true; do
    if squeue -h -j "${job_ids}" | grep -q .; then
      sleep "${POLL_SECONDS}"
    else
      break
    fi
  done
}

start=1
while [ "${start}" -le "${TOTAL}" ]; do
  end=$((start + BATCH_SIZE - 1))
  if [ "${end}" -gt "${TOTAL}" ]; then
    end="${TOTAL}"
  fi
  job_high=$(submit_batch "${start}" "${end}" high)
  job_med=$(submit_batch "${start}" "${end}" medium)
  job_low=$(submit_batch "${start}" "${end}" low)
  wait_jobs "${job_high},${job_med},${job_low}"
  start=$((end + 1))
done
