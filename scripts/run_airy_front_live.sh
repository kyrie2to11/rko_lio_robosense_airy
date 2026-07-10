#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

RSLIDAR_CONFIG="${RKO_LIO_RSLIDAR_CONFIG:-${REPO_DIR}/config/rslidar_airy_front.yaml}"
LIO_CONFIG="${RKO_LIO_CONFIG:-${REPO_DIR}/config/rko_lio_airy_front.yaml}"
SDK_PID=""
LIO_PID=""

source_setup() {
  local setup_file="$1"
  local nounset_was_on=0

  case "$-" in
    *u*)
      nounset_was_on=1
      set +u
      ;;
  esac

  # ROS and colcon setup scripts may read unset environment variables.
  source "${setup_file}"

  if [[ "${nounset_was_on}" -eq 1 ]]; then
    set -u
  fi
}

cleanup() {
  if [[ -n "${LIO_PID}" ]] && kill -0 "${LIO_PID}" 2>/dev/null; then
    kill "${LIO_PID}" 2>/dev/null || true
  fi
  if [[ -n "${SDK_PID}" ]] && kill -0 "${SDK_PID}" 2>/dev/null; then
    kill "${SDK_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

if [[ ! -f "${RSLIDAR_CONFIG}" ]]; then
  echo "[run_airy_front_live] rslidar config not found: ${RSLIDAR_CONFIG}" >&2
  exit 1
fi
if [[ ! -f "${LIO_CONFIG}" ]]; then
  echo "[run_airy_front_live] rko_lio config not found: ${LIO_CONFIG}" >&2
  exit 1
fi

source_setup /opt/ros/jazzy/setup.bash

THIRD_PARTY_SETUP="${REPO_DIR}/third_party/install/setup.bash"
if [[ ! -f "${THIRD_PARTY_SETUP}" ]]; then
  echo "[run_airy_front_live] missing ${THIRD_PARTY_SETUP}; run ./third_party/build_robosense.sh first" >&2
  exit 1
fi
source_setup "${THIRD_PARTY_SETUP}"

RKO_SETUP="${REPO_DIR}/install/setup.bash"
if [[ ! -f "${RKO_SETUP}" ]]; then
  echo "[run_airy_front_live] missing ${RKO_SETUP}; build rko_lio first" >&2
  exit 1
fi
source_setup "${RKO_SETUP}"

echo "[run_airy_front_live] rslidar_sdk config: ${RSLIDAR_CONFIG}"
echo "[run_airy_front_live] rko_lio config: ${LIO_CONFIG}"

ros2 run rslidar_sdk rslidar_sdk_node --ros-args -p "config_path:=${RSLIDAR_CONFIG}" &
SDK_PID=$!

sleep "${RSLIDAR_STARTUP_DELAY_SEC:-2}"

ros2 launch rko_lio odometry.launch.py "config_file:=${LIO_CONFIG}" "$@" &
LIO_PID=$!

wait "${LIO_PID}"
