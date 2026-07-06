"""add user usage plan

Revision ID: 20260706_0002
Revises: 20260625_0001
Create Date: 2026-07-06 19:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "20260706_0002"
down_revision: Union[str, None] = "20260625_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(table_name: str) -> bool:
    bind = op.get_context().bind
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(index_name: str, table_name: str) -> bool:
    bind = op.get_context().bind
    inspector = inspect(bind)
    try:
        indexes = inspector.get_indexes(table_name)
        return any(idx["name"] == index_name for idx in indexes)
    except Exception:
        return False


def _create_index_if_needed(index_name: str, table_name: str, columns: list, **kwargs) -> None:
    if not _index_exists(index_name, table_name):
        op.create_index(index_name, table_name, columns, **kwargs)


def upgrade() -> None:
    if not _table_exists("user_usage_plan"):
        op.create_table(
            "user_usage_plan",
            sa.Column("id", sa.CHAR(length=32), nullable=False),
            sa.Column("user_id", sa.CHAR(length=32), nullable=False),
            sa.Column("plan_code", sa.String(length=50), nullable=False),
            sa.Column("plan_name", sa.String(length=100), nullable=True),
            sa.Column("daily_ocr_limit", sa.Integer(), nullable=True),
            sa.Column("monthly_ocr_limit", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("source", sa.String(length=50), nullable=False),
            sa.Column("starts_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", name="uq_user_usage_plan_user"),
        )
        _create_index_if_needed("ix_user_usage_plan_user_id", "user_usage_plan", ["user_id"], unique=False)


def downgrade() -> None:
    if _table_exists("user_usage_plan"):
        op.drop_index("ix_user_usage_plan_user_id", table_name="user_usage_plan")
        op.drop_table("user_usage_plan")
