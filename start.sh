#!/bin/bash
# 高中化学教学辅助系统 - 快速启动脚本

set -e

echo "========================================"
echo " 高中化学教学辅助系统 - 启动脚本"
echo "========================================"
echo

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.11+"
    exit 1
fi

# 进入后端目录
cd "$(dirname "$0")/backend"

# 检查依赖
if [ ! -d "venv" ]; then
    echo "[1/4] 创建虚拟环境..."
    python3 -m venv venv
fi

echo "[2/4] 激活虚拟环境..."
source venv/bin/activate

echo "[3/4] 安装依赖..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 检查 .env 文件
if [ ! -f ".env" ]; then
    echo "[4/4] 创建配置文件..."
    cp .env.example .env
    echo
    echo "[提示] 请编辑 backend/.env 文件配置数据库信息"
    echo "       主要需要设置: DB_PASSWORD"
    echo
    read -p "按 Enter 继续..."
fi

echo
echo "[完成] 准备工作完成！"
echo
echo "后续步骤:"
echo "  1. 确保 MySQL 已启动并创建数据库: CREATE DATABASE chem_teacher;"
echo "  2. 编辑 backend/.env 文件，填写数据库密码"
echo "  3. 运行: python init_database.py"
echo "  4. 启动: uvicorn app.main:app --reload"
echo "  5. 访问: http://localhost:8000/docs"
echo
