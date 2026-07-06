#!/usr/bin/env python3
"""
构建并推送 chem-backend Docker 镜像到腾讯云 TCR。

用法（仓库根目录）：
    python build_and_push_backend.py
    python build_and_push_backend.py v32

前提：
    - 已安装 docker、node
    - 已执行过 docker login ccr.ccs.tencentyun.com（登录一次即可，无需每次运行本脚本）
    - 在 CloudBase 云托管更新版本时，把镜像 tag 改为下方 IMAGE_VERSION

部署提醒：
    CloudBase → 云托管 → chem-backend → 更新版本
    镜像：ccr.ccs.tencentyun.com/chem-teacher/backend:<IMAGE_VERSION>
    环境变量需含 ADMIN_USERNAMES=teacher1
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

# ── 改这里：下次发版递增版本号 ──
IMAGE_VERSION = "v31"

REGISTRY = "ccr.ccs.tencentyun.com/chem-teacher/backend"
ROOT = Path(__file__).resolve().parent
ADMIN_DIST = ROOT / "frontend" / "admin-dist" / "index.html"
ADMIN_BUILD = ROOT / "admin-web" / "scripts" / "build.mjs"


def run(cmd: list[str], *, cwd: Path | None = None) -> None:
    label = " ".join(cmd)
    print(f"\n==> {label}")
    subprocess.run(cmd, cwd=cwd or ROOT, check=True)


def normalize_tag(raw: str) -> str:
    value = raw.strip()
    return value if value.startswith("v") else f"v{value}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build and push chem-backend Docker image")
    parser.add_argument(
        "version",
        nargs="?",
        default=IMAGE_VERSION,
        help=f"image tag, e.g. v31 (default: {IMAGE_VERSION})",
    )
    args = parser.parse_args()
    tag = normalize_tag(args.version)
    image = f"{REGISTRY}:{tag}"

    if not ADMIN_BUILD.is_file():
        print(f"缺少构建脚本: {ADMIN_BUILD}", file=sys.stderr)
        return 1

    run(["node", str(ADMIN_BUILD.relative_to(ROOT))])

    if not ADMIN_DIST.is_file():
        print(f"admin-console 构建失败，未找到: {ADMIN_DIST}", file=sys.stderr)
        return 1

    run(["docker", "build", "-f", "backend/Dockerfile", "-t", image, "."])
    run(["docker", "push", image])

    print("\n==> 完成")
    print(f"    镜像: {image}")
    print("    云托管更新版本时使用上述镜像地址，发布后验证 /health 与 /admin-console/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
