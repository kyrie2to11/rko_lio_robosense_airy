#!/usr/bin/env bash
# Build RoboSense rslidar_sdk + rslidar_msg under third_party/ for use with rko_lio.
#
# third_party/ carries COLCON_IGNORE, so it is skipped by the main rko_lio build;
# here we build with an explicit --base-paths src to bypass it.
#
# Build flags:
#   -DENABLE_IMU_DATA_PARSE=ON  publish the front Airy's built-in IMU
#   -DPOINT_TYPE=XYZIRT         per-point `timestamp` + `ring` for rko_lio deskew
#
# rslidar_sdk here is pinned to the kyrie2to11/rko_lio_robosense fork (commit
# pinned by the superproject), which already carries the fixes we need:
#   * Airy IMU output in m/s^2 + FLU axes + orientation_covariance=-1 (1ad07a2)
#   * -DPOINT_TYPE honored from the cmake cache               (dca7a40)
# So no source patching is needed.
#
# NOTE: no `set -u` — /opt/ros/<distro>/setup.bash references unbound vars
# (AMENT_TRACE_SETUP_FILES) which would abort under nounset.
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
: "${ROS_DISTRO:=jazzy}"

source "/opt/ros/${ROS_DISTRO}/setup.bash"

cd "$SCRIPT_DIR"
colcon build --base-paths src --symlink-install \
  --cmake-args -DENABLE_IMU_DATA_PARSE=ON -DPOINT_TYPE=XYZIRT

echo
echo "[build_robosense] done. Source the workspace before launching:"
echo "    source ${SCRIPT_DIR}/install/setup.bash"

