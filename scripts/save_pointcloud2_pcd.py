#!/usr/bin/env python3
import argparse
from datetime import datetime
from pathlib import Path
import sys
import time

import rclpy
from sensor_msgs.msg import PointCloud2
from sensor_msgs_py import point_cloud2


def resolve_output_path(output: Path) -> Path:
    if output.suffix.lower() == ".pcd":
        output.parent.mkdir(parents=True, exist_ok=True)
        return output

    output.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return output / f"airy_front_map_{stamp}.pcd"


def write_ascii_pcd(path: Path, points: list[tuple[float, float, float]]) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("# .PCD v0.7 - Point Cloud Data file format\n")
        f.write("VERSION 0.7\n")
        f.write("FIELDS x y z\n")
        f.write("SIZE 4 4 4\n")
        f.write("TYPE F F F\n")
        f.write("COUNT 1 1 1\n")
        f.write(f"WIDTH {len(points)}\n")
        f.write("HEIGHT 1\n")
        f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
        f.write(f"POINTS {len(points)}\n")
        f.write("DATA ascii\n")
        for x, y, z in points:
            f.write(f"{x:.6f} {y:.6f} {z:.6f}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Save one ROS2 PointCloud2 message as an ASCII PCD file.")
    parser.add_argument("--topic", default="/rko_lio/local_map", help="PointCloud2 topic to save")
    parser.add_argument("--output", default="maps", help="Output .pcd path or output directory")
    parser.add_argument("--timeout", type=float, default=10.0, help="Seconds to wait for one map message")
    args = parser.parse_args()

    rclpy.init()
    node = rclpy.create_node("save_airy_front_map")
    received: list[PointCloud2] = []

    def callback(msg: PointCloud2) -> None:
        received.append(msg)

    node.create_subscription(PointCloud2, args.topic, callback, 10)

    deadline = time.monotonic() + args.timeout
    while rclpy.ok() and not received and time.monotonic() < deadline:
        rclpy.spin_once(node, timeout_sec=0.1)

    if not received:
        node.destroy_node()
        rclpy.shutdown()
        print(f"[save_airy_front_map] no PointCloud2 received on {args.topic} within {args.timeout}s", file=sys.stderr)
        return 1

    msg = received[0]
    points = [
        (float(x), float(y), float(z))
        for x, y, z in point_cloud2.read_points(msg, field_names=("x", "y", "z"), skip_nans=True)
    ]

    node.destroy_node()
    rclpy.shutdown()

    if not points:
        print(f"[save_airy_front_map] received empty point cloud on {args.topic}", file=sys.stderr)
        return 1

    output_path = resolve_output_path(Path(args.output))
    write_ascii_pcd(output_path, points)
    print(f"[save_airy_front_map] saved {len(points)} points to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
