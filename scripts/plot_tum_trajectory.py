#!/usr/bin/env python3
"""把 rko_lio dump 的 TUM 轨迹画成图（俯视 / 侧视 / 3D），默认存 PNG。

TUM 格式：timestamp tx ty tz qx qy qz qw

用法：
    pip install matplotlib numpy
    python3 scripts/plot_tum_trajectory.py <tum_file> [<tum_file> ...] [-o out.png] [--show]

可传多个文件叠加对比；每个文件名（去扩展名）作为图例。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np


def load_tum(path: Path) -> np.ndarray:
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data.reshape(1, -1)
    return data  # (N, 8): t x y z qx qy qz qw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tum_files", nargs="+", type=Path, help="一个或多个 TUM 轨迹文件")
    parser.add_argument("-o", "--output", default=None, help="输出 PNG 路径（默认与首个输入同名 .png）")
    parser.add_argument("--show", action="store_true", help="弹出交互窗口（需要显示环境）")
    args = parser.parse_args()

    import matplotlib

    if not args.show:
        matplotlib.use("Agg")  # 无显示也能存图

    # 选一个含中文字形的字体，避免标题/图例出现"豆腐块"乱码。
    import matplotlib.font_manager as fm

    cjk_priority = [
        "Noto Sans CJK SC", "Noto Sans CJK TC", "Noto Sans CJK JP", "Noto Sans CJK HK",
        "Source Han Sans SC", "Source Han Sans CN", "WenQuanYi Micro Hei", "WenQuanYi Zen Hei",
        "Microsoft YaHei", "SimHei", "SimSun", "Droid Sans Fallback",
    ]
    available = {f.name for f in fm.fontManager.ttflist}
    cjk_font = next((name for name in cjk_priority if name in available), None)
    if cjk_font:
        matplotlib.rcParams["font.sans-serif"] = [cjk_font, "DejaVu Sans"]
        matplotlib.rcParams["axes.unicode_minus"] = False  # 负号用 ASCII，避免缺字形
        print(f"[plot_tum] 使用中文字体: {cjk_font}")
    else:
        print("[plot_tum] 未找到中文字体，标题回退为英文（不影响数据）")

    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  注册 3D 投影

    # 没有中文字体时回退英文，保证不出"豆腐块"。
    titles = ("俯视 XY", "侧视 XZ", "3D 轨迹") if cjk_font else ("Top-down XY", "Side XZ", "3D trajectory")
    label_xy = ("x [m]", "y [m]")
    label_xz = ("x [m]", "z [m]")

    fig = plt.figure(figsize=(14, 5))

    ax_xy = fig.add_subplot(1, 3, 1)
    ax_xz = fig.add_subplot(1, 3, 2)
    ax_3d = fig.add_subplot(1, 3, 3, projection="3d")

    for f in args.tum_files:
        traj = load_tum(f)
        label = f.stem
        x, y, z = traj[:, 1], traj[:, 2], traj[:, 3]
        ax_xy.plot(x, y, lw=1.2, label=label)
        ax_xz.plot(x, z, lw=1.2, label=label)
        ax_3d.plot(x, y, z, lw=1.2, label=label)

    for ax, (xl, yl), title in [
        (ax_xy, label_xy, titles[0]),
        (ax_xz, label_xz, titles[1]),
    ]:
        ax.set_xlabel(xl)
        ax.set_ylabel(yl)
        ax.set_title(title)
        ax.set_aspect("equal", adjustable="datalim")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=7)

    ax_3d.set_xlabel("x"); ax_3d.set_ylabel("y"); ax_3d.set_zlabel("z")
    ax_3d.set_title(titles[2])
    ax_3d.legend(fontsize=7)

    out = Path(args.output) if args.output else args.tum_files[0].with_suffix(".png")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    print(f"[plot_tum] saved: {out}")
    if args.show:
        plt.show()
    return 0


if __name__ == "__main__":
    sys.exit(main())
