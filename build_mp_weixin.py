#!/usr/bin/env python3
"""
构建微信小程序产物（uni-app → frontend/dist/build/mp-weixin）。

用法（仓库根目录）：
    python build_mp_weixin.py

前提：
    - 已安装 node、npm
    - 已在 frontend 目录执行过 npm install

构建完成后：
    1. 打开微信开发者工具
    2. 导入项目目录 frontend/（含 project.config.json）
    3. 点击「编译」

开发模式（改代码自动重新编译，需保持终端运行）：
    cd frontend
    npm run dev:mp-weixin
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD_SCRIPT = ROOT / "scripts" / "build_mp_weixin.mjs"
OUTPUT_APP = ROOT / "frontend" / "dist" / "build" / "mp-weixin" / "app.json"


def main() -> int:
    if not BUILD_SCRIPT.is_file():
        print(f"缺少构建脚本: {BUILD_SCRIPT}", file=sys.stderr)
        return 1

    try:
        subprocess.run(["node", str(BUILD_SCRIPT.relative_to(ROOT))], cwd=ROOT, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"构建失败，退出码 {exc.returncode}", file=sys.stderr)
        return exc.returncode

    if not OUTPUT_APP.is_file():
        print(f"构建失败，未找到: {OUTPUT_APP}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
