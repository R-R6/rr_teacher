> 数据库迁移治理指南，说明如何使用 Alembic 管理 schema 变更、本地与生产环境差异、迁移命令、部署顺序和回滚策略。

# Database Migration Guide

Last updated: 2026-06-25

This project uses Alembic to manage backend schema changes.

## Rules

- Local development may keep `AUTO_CREATE_TABLES=true` for quick SQLite setup.
- Production and CloudRun must set `AUTO_CREATE_TABLES=false`.
- Every schema change must have a migration under `backend/alembic/versions/`.
- Do not rely on SQLAlchemy `create_all()` to change production tables.
- Back up the production database before running migrations that alter or drop data.

## Commands

Run commands from `backend/`.

```bash
alembic -c alembic.ini upgrade head
alembic -c alembic.ini current
alembic -c alembic.ini history
```

Create a new migration after changing `app/models.py`:

```bash
alembic -c alembic.ini revision --autogenerate -m "describe change"
```

Review the generated migration before committing it. Autogenerate is a helper, not an approval step.

## Deployment Order

1. Back up the database.
2. Deploy the backend image that includes the migration files.
3. Run `alembic -c alembic.ini upgrade head` against the target database.
4. Start or restart the application with `AUTO_CREATE_TABLES=false`.
5. Check `/health` and the affected API paths.

## Rollback

Rollback is migration-specific. Prefer restoring a backup for destructive changes.

For reversible non-destructive changes:

```bash
alembic -c alembic.ini downgrade -1
```

Record the migration revision, backup file, operator, and verification result in the release notes.
