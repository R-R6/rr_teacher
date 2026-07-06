"""add billing tables

Revision ID: 20260706_0003
Revises: 20260706_0002
Create Date: 2026-07-06 21:30:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "20260706_0003"
down_revision: Union[str, None] = "20260706_0002"
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


def _drop_index_if_exists(index_name: str, table_name: str) -> None:
    if _table_exists(table_name) and _index_exists(index_name, table_name):
        op.drop_index(index_name, table_name=table_name)


def upgrade() -> None:
    if not _table_exists("billing_offer"):
        op.create_table(
            "billing_offer",
            sa.Column("id", sa.CHAR(length=32), nullable=False),
            sa.Column("code", sa.String(length=50), nullable=False),
            sa.Column("name", sa.String(length=100), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("free_total", sa.Integer(), nullable=False),
            sa.Column("paid_total", sa.Integer(), nullable=False),
            sa.Column("amount_cents", sa.Integer(), nullable=False),
            sa.Column("currency", sa.String(length=10), nullable=False),
            sa.Column("payment_window_minutes", sa.Integer(), nullable=False),
            sa.Column("starts_at", sa.DateTime(), nullable=True),
            sa.Column("ends_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index_if_needed("ix_billing_offer_code", "billing_offer", ["code"], unique=True)

    if not _table_exists("billing_eligibility"):
        op.create_table(
            "billing_eligibility",
            sa.Column("id", sa.CHAR(length=32), nullable=False),
            sa.Column("offer_id", sa.CHAR(length=32), nullable=False),
            sa.Column("user_id", sa.CHAR(length=32), nullable=False),
            sa.Column("type", sa.String(length=30), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("slot_no", sa.Integer(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("converted_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["offer_id"], ["billing_offer.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index_if_needed("ix_billing_eligibility_offer_id", "billing_eligibility", ["offer_id"])
        _create_index_if_needed("ix_billing_eligibility_user_id", "billing_eligibility", ["user_id"])
        _create_index_if_needed("ix_billing_eligibility_offer_user", "billing_eligibility", ["offer_id", "user_id"])
        _create_index_if_needed(
            "ix_billing_eligibility_offer_type_status",
            "billing_eligibility",
            ["offer_id", "type", "status"],
        )

    if not _table_exists("billing_order"):
        op.create_table(
            "billing_order",
            sa.Column("id", sa.CHAR(length=32), nullable=False),
            sa.Column("order_no", sa.String(length=64), nullable=False),
            sa.Column("user_id", sa.CHAR(length=32), nullable=False),
            sa.Column("offer_id", sa.CHAR(length=32), nullable=False),
            sa.Column("eligibility_id", sa.CHAR(length=32), nullable=False),
            sa.Column("product_type", sa.String(length=50), nullable=False),
            sa.Column("channel", sa.String(length=30), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("amount_total", sa.Integer(), nullable=False),
            sa.Column("currency", sa.String(length=10), nullable=False),
            sa.Column("transaction_id", sa.String(length=128), nullable=True),
            sa.Column("payment_params", sa.JSON(), nullable=True),
            sa.Column("raw_payload", sa.JSON(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("paid_at", sa.DateTime(), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["eligibility_id"], ["billing_eligibility.id"]),
            sa.ForeignKeyConstraint(["offer_id"], ["billing_offer.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("order_no", name="uq_billing_order_no"),
        )
        _create_index_if_needed("ix_billing_order_user_id", "billing_order", ["user_id"])
        _create_index_if_needed("ix_billing_order_offer_id", "billing_order", ["offer_id"])
        _create_index_if_needed("ix_billing_order_eligibility_id", "billing_order", ["eligibility_id"])
        _create_index_if_needed("ix_billing_order_transaction_id", "billing_order", ["transaction_id"])
        _create_index_if_needed("ix_billing_order_user_status", "billing_order", ["user_id", "status"])
        _create_index_if_needed(
            "ix_billing_order_eligibility_status",
            "billing_order",
            ["eligibility_id", "status"],
        )

    if not _table_exists("billing_entitlement"):
        op.create_table(
            "billing_entitlement",
            sa.Column("id", sa.CHAR(length=32), nullable=False),
            sa.Column("user_id", sa.CHAR(length=32), nullable=False),
            sa.Column("offer_id", sa.CHAR(length=32), nullable=True),
            sa.Column("eligibility_id", sa.CHAR(length=32), nullable=True),
            sa.Column("order_id", sa.CHAR(length=32), nullable=True),
            sa.Column("type", sa.String(length=50), nullable=False),
            sa.Column("status", sa.String(length=20), nullable=False),
            sa.Column("source", sa.String(length=50), nullable=False),
            sa.Column("starts_at", sa.DateTime(), nullable=True),
            sa.Column("expires_at", sa.DateTime(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["eligibility_id"], ["billing_eligibility.id"]),
            sa.ForeignKeyConstraint(["offer_id"], ["billing_offer.id"]),
            sa.ForeignKeyConstraint(["order_id"], ["billing_order.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", "type", name="uq_billing_entitlement_user_type"),
        )
        _create_index_if_needed("ix_billing_entitlement_user_id", "billing_entitlement", ["user_id"])
        _create_index_if_needed("ix_billing_entitlement_offer_id", "billing_entitlement", ["offer_id"])
        _create_index_if_needed("ix_billing_entitlement_eligibility_id", "billing_entitlement", ["eligibility_id"])
        _create_index_if_needed("ix_billing_entitlement_order_id", "billing_entitlement", ["order_id"])

    if not _table_exists("billing_event_log"):
        op.create_table(
            "billing_event_log",
            sa.Column("id", sa.CHAR(length=32), nullable=False),
            sa.Column("user_id", sa.CHAR(length=32), nullable=True),
            sa.Column("offer_id", sa.CHAR(length=32), nullable=True),
            sa.Column("eligibility_id", sa.CHAR(length=32), nullable=True),
            sa.Column("order_id", sa.CHAR(length=32), nullable=True),
            sa.Column("entitlement_id", sa.CHAR(length=32), nullable=True),
            sa.Column("event_type", sa.String(length=50), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["eligibility_id"], ["billing_eligibility.id"]),
            sa.ForeignKeyConstraint(["entitlement_id"], ["billing_entitlement.id"]),
            sa.ForeignKeyConstraint(["offer_id"], ["billing_offer.id"]),
            sa.ForeignKeyConstraint(["order_id"], ["billing_order.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        _create_index_if_needed("ix_billing_event_log_user_id", "billing_event_log", ["user_id"])
        _create_index_if_needed("ix_billing_event_log_offer_id", "billing_event_log", ["offer_id"])
        _create_index_if_needed("ix_billing_event_log_eligibility_id", "billing_event_log", ["eligibility_id"])
        _create_index_if_needed("ix_billing_event_log_order_id", "billing_event_log", ["order_id"])
        _create_index_if_needed("ix_billing_event_log_entitlement_id", "billing_event_log", ["entitlement_id"])
        _create_index_if_needed("ix_billing_event_log_event_type", "billing_event_log", ["event_type"])


def downgrade() -> None:
    if _table_exists("billing_event_log"):
        _drop_index_if_exists("ix_billing_event_log_event_type", "billing_event_log")
        _drop_index_if_exists("ix_billing_event_log_entitlement_id", "billing_event_log")
        _drop_index_if_exists("ix_billing_event_log_order_id", "billing_event_log")
        _drop_index_if_exists("ix_billing_event_log_eligibility_id", "billing_event_log")
        _drop_index_if_exists("ix_billing_event_log_offer_id", "billing_event_log")
        _drop_index_if_exists("ix_billing_event_log_user_id", "billing_event_log")
        op.drop_table("billing_event_log")

    if _table_exists("billing_entitlement"):
        _drop_index_if_exists("ix_billing_entitlement_order_id", "billing_entitlement")
        _drop_index_if_exists("ix_billing_entitlement_eligibility_id", "billing_entitlement")
        _drop_index_if_exists("ix_billing_entitlement_offer_id", "billing_entitlement")
        _drop_index_if_exists("ix_billing_entitlement_user_id", "billing_entitlement")
        op.drop_table("billing_entitlement")

    if _table_exists("billing_order"):
        _drop_index_if_exists("ix_billing_order_eligibility_status", "billing_order")
        _drop_index_if_exists("ix_billing_order_user_status", "billing_order")
        _drop_index_if_exists("ix_billing_order_transaction_id", "billing_order")
        _drop_index_if_exists("ix_billing_order_eligibility_id", "billing_order")
        _drop_index_if_exists("ix_billing_order_offer_id", "billing_order")
        _drop_index_if_exists("ix_billing_order_user_id", "billing_order")
        op.drop_table("billing_order")

    if _table_exists("billing_eligibility"):
        _drop_index_if_exists("ix_billing_eligibility_offer_type_status", "billing_eligibility")
        _drop_index_if_exists("ix_billing_eligibility_offer_user", "billing_eligibility")
        _drop_index_if_exists("ix_billing_eligibility_user_id", "billing_eligibility")
        _drop_index_if_exists("ix_billing_eligibility_offer_id", "billing_eligibility")
        op.drop_table("billing_eligibility")

    if _table_exists("billing_offer"):
        _drop_index_if_exists("ix_billing_offer_code", "billing_offer")
        op.drop_table("billing_offer")
