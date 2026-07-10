#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

MAP_TOPIC="${RKO_LIO_MAP_TOPIC:-/rko_lio/local_map}"
OUTPUT="${RKO_LIO_MAP_OUTPUT:-${REPO_DIR}/maps}"
TIMEOUT="${RKO_LIO_MAP_TIMEOUT_SEC:-10}"
export ROS_LOG_DIR="${ROS_LOG_DIR:-${REPO_DIR}/log/ros}"
if ! mkdir -p "${ROS_LOG_DIR}" 2>/dev/null; then
  export ROS_LOG_DIR="/tmp/rko_lio_ros_log"
  mkdir -p "${ROS_LOG_DIR}"
fi

source_setup() {
  local setup_file="$1"
  local nounset_was_on=0

  case "$-" in
    *u*)
      nounset_was_on=1
      set +u
      ;;
  esac

  source "${setup_file}"

  if [[ "${nounset_was_on}" -eq 1 ]]; then
    set -u
  fi
}

source_setup /opt/ros/jazzy/setup.bash

THIRD_PARTY_SETUP="${REPO_DIR}/third_party/install/setup.bash"
if [[ -f "${THIRD_PARTY_SETUP}" ]]; then
  source_setup "${THIRD_PARTY_SETUP}"
fi

RKO_SETUP="${REPO_DIR}/install/setup.bash"
if [[ -f "${RKO_SETUP}" ]]; then
  source_setup "${RKO_SETUP}"
fi

echo "[save_airy_front_map] topic: ${MAP_TOPIC}"
echo "[save_airy_front_map] output: ${OUTPUT}"
echo "[save_airy_front_map] timeout: ${TIMEOUT}s"

python3 "${SCRIPT_DIR}/save_pointcloud2_pcd.py" \
  --topic "${MAP_TOPIC}" \
  --output "${OUTPUT}" \
  --timeout "${TIMEOUT}"
