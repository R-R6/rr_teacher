#!/bin/sh
# CloudRun / 生产容器入口脚本
# 启动 uvicorn 前，对 MySQL 执行 Alembic 迁移（建表/升 schema），
# 确保 lifespan 里的探针查询（SELECT COUNT(*) FROM question）不会因表缺失而崩溃。
#
# 说明：
# - DB_TYPE=mysql 时才跑迁移；sqlite（本地开发）走 AUTO_CREATE_TABLES 自动建表，跳过迁移。
# - 迁移失败时容器退出启动，确保问题及时发现而非带病运行。
set -e

if [ "$DB_TYPE" = "mysql" ]; then
    echo "[entrypoint] DB_TYPE=mysql, running alembic upgrade head ..."
    alembic -c alembic.ini upgrade head
    echo "[entrypoint] alembic upgrade completed"
else
    echo "[entrypoint] DB_TYPE=$DB_TYPE, skip alembic migration"
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 2