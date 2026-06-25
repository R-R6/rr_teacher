"""baseline schema

Revision ID: 20260625_0001
Revises:
Create Date: 2026-06-25 00:01:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20260625_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("openid", sa.String(length=100), nullable=True),
        sa.Column("hashed_password", sa.String(length=256), nullable=False),
        sa.Column("role", sa.Enum("teacher", "student", name="user_role"), nullable=True),
        sa.Column("nickname", sa.String(length=50), nullable=True),
        sa.Column("school", sa.String(length=100), nullable=True),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
    )
    op.create_index("ix_user_openid", "user", ["openid"], unique=True)
    op.create_index("ix_user_username", "user", ["username"], unique=True)

    op.create_table(
        "question_tag",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("parent_id", sa.CHAR(length=32), nullable=True),
        sa.Column("tag_type", sa.Enum("book", "knowledge", "type", "difficulty", name="tag_type"), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["parent_id"], ["question_tag.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "paper",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("author_id", sa.CHAR(length=32), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("subtitle", sa.String(length=200), nullable=True),
        sa.Column("filter_params", sa.JSON(), nullable=True),
        sa.Column("sections", sa.JSON(), nullable=True),
        sa.Column("total_score", sa.Integer(), nullable=True),
        sa.Column("exam_duration", sa.Integer(), nullable=True),
        sa.Column("word_url", sa.String(length=512), nullable=True),
        sa.Column("answer_word_url", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_paper_author_id", "paper", ["author_id"], unique=False)

    op.create_table(
        "ocr_record",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("user_id", sa.CHAR(length=32), nullable=False),
        sa.Column("origin_image_url", sa.String(length=512), nullable=False),
        sa.Column("processed_image_url", sa.String(length=512), nullable=True),
        sa.Column("ocr_result_raw", sa.Text(), nullable=True),
        sa.Column("ocr_result_latex", sa.Text(), nullable=True),
        sa.Column("ocr_result_text", sa.Text(), nullable=True),
        sa.Column("ocr_engine", sa.String(length=50), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("manual_corrections", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ocr_record_user_id", "ocr_record", ["user_id"], unique=False)
    op.create_index("ix_ocr_user_created", "ocr_record", ["user_id", "created_at"], unique=False)

    op.create_table(
        "question",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("author_id", sa.CHAR(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=True),
        sa.Column("analysis", sa.Text(), nullable=True),
        sa.Column(
            "question_type",
            sa.Enum("choice", "fill", "experiment", "calculation", "short_answer", name="q_type"),
            nullable=True,
        ),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("source_image_url", sa.String(length=512), nullable=True),
        sa.Column("options", sa.JSON(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("ocr_record_id", sa.CHAR(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["ocr_record_id"], ["ocr_record.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_question_author_id", "question", ["author_id"], unique=False)
    op.create_index("ix_question_author_type", "question", ["author_id", "question_type"], unique=False)
    op.create_index("ix_question_difficulty", "question", ["difficulty"], unique=False)

    op.create_table(
        "question_image",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("question_id", sa.CHAR(length=32), nullable=True),
        sa.Column("ocr_record_id", sa.CHAR(length=32), nullable=True),
        sa.Column("image_url", sa.String(length=512), nullable=False),
        sa.Column("image_type", sa.String(length=50), nullable=True),
        sa.Column("source_bbox", sa.JSON(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["ocr_record_id"], ["ocr_record.id"]),
        sa.ForeignKeyConstraint(["question_id"], ["question.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "question_tag_rel",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("question_id", sa.CHAR(length=32), nullable=False),
        sa.Column("tag_id", sa.CHAR(length=32), nullable=False),
        sa.ForeignKeyConstraint(["question_id"], ["question.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["question_tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("question_id", "tag_id", name="uq_question_tag"),
    )

    op.create_table(
        "paper_item",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("paper_id", sa.CHAR(length=32), nullable=False),
        sa.Column("question_id", sa.CHAR(length=32), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["paper_id"], ["paper.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["question_id"], ["question.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "ocr_usage_log",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("user_id", sa.CHAR(length=32), nullable=False),
        sa.Column("engine", sa.String(length=50), nullable=False),
        sa.Column("usage_day", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ocr_usage_log_user_id", "ocr_usage_log", ["user_id"], unique=False)
    op.create_index(
        "ix_ocr_usage_global_day_engine",
        "ocr_usage_log",
        ["usage_day", "engine"],
        unique=False,
    )
    op.create_index(
        "ix_ocr_usage_user_day_engine",
        "ocr_usage_log",
        ["user_id", "usage_day", "engine"],
        unique=False,
    )

    op.create_table(
        "mistake_book",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("student_id", sa.CHAR(length=32), nullable=False),
        sa.Column("question_id", sa.CHAR(length=32), nullable=False),
        sa.Column("wrong_count", sa.Integer(), nullable=True),
        sa.Column("is_mastered", sa.Boolean(), nullable=True),
        sa.Column("last_wrong_at", sa.DateTime(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["question_id"], ["question.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mistake_book_student_id", "mistake_book", ["student_id"], unique=False)

    op.create_table(
        "practice_record",
        sa.Column("id", sa.CHAR(length=32), nullable=False),
        sa.Column("student_id", sa.CHAR(length=32), nullable=False),
        sa.Column("question_id", sa.CHAR(length=32), nullable=False),
        sa.Column("student_answer", sa.Text(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("duration_seconds", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["question_id"], ["question.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_practice_record_student_id", "practice_record", ["student_id"], unique=False)
    op.create_index("ix_practice_student", "practice_record", ["student_id", "created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_practice_student", table_name="practice_record")
    op.drop_index("ix_practice_record_student_id", table_name="practice_record")
    op.drop_table("practice_record")

    op.drop_index("ix_mistake_book_student_id", table_name="mistake_book")
    op.drop_table("mistake_book")

    op.drop_index("ix_ocr_usage_user_day_engine", table_name="ocr_usage_log")
    op.drop_index("ix_ocr_usage_global_day_engine", table_name="ocr_usage_log")
    op.drop_index("ix_ocr_usage_log_user_id", table_name="ocr_usage_log")
    op.drop_table("ocr_usage_log")

    op.drop_table("paper_item")
    op.drop_table("question_tag_rel")
    op.drop_table("question_image")

    op.drop_index("ix_question_difficulty", table_name="question")
    op.drop_index("ix_question_author_type", table_name="question")
    op.drop_index("ix_question_author_id", table_name="question")
    op.drop_table("question")

    op.drop_index("ix_ocr_user_created", table_name="ocr_record")
    op.drop_index("ix_ocr_record_user_id", table_name="ocr_record")
    op.drop_table("ocr_record")

    op.drop_index("ix_paper_author_id", table_name="paper")
    op.drop_table("paper")

    op.drop_table("question_tag")

    op.drop_index("ix_user_username", table_name="user")
    op.drop_index("ix_user_openid", table_name="user")
    op.drop_table("user")
