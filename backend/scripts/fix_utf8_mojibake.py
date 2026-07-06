"""Repair double-encoded UTF-8 text stored in MySQL (latin1 client during init).

Scope: currently fixes `user.nickname` and `user.school` only.
Other text columns (tags, questions, etc.) need the same pattern if affected.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import settings  # noqa: E402

FIX_EXPR = "CONVERT(CAST(CONVERT({column} USING latin1) AS BINARY) USING utf8mb4)"
MOJIBAKE_PATTERN = r"[ÃÂâäåæçèé]"


TEXT_COLUMNS: dict[str, list[str]] = {
    "user": ["nickname", "school"],
}


def looks_like_mojibake(value: str | None) -> bool:
    return bool(value and re.search(MOJIBAKE_PATTERN, value))


def column_needs_repair_sql(column: str) -> str:
    fixed = FIX_EXPR.format(column=column)
    return f"({column} IS NOT NULL AND {column} REGEXP '{MOJIBAKE_PATTERN}' AND {column} <> {fixed})"


def column_repair_expr_sql(column: str) -> str:
    fixed = FIX_EXPR.format(column=column)
    return f"CASE WHEN {column_needs_repair_sql(column)} THEN {fixed} ELSE {column} END"


def table_where_sql(columns: list[str]) -> str:
    return " OR ".join(column_needs_repair_sql(column) for column in columns)


MOJIBAKE_WHERE = table_where_sql(TEXT_COLUMNS["user"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix double-encoded UTF-8 text in MySQL.")
    parser.add_argument("--apply", action="store_true", help="Write fixes to the database.")
    args = parser.parse_args()

    if settings.DB_TYPE != "mysql":
        print("Only MySQL deployments need this repair script.")
        return 0

    engine = create_engine(
        settings.database_url_sync,
        connect_args={"charset": "utf8mb4"},
    )

    with engine.connect() as conn:
        preview_sql = text(
            f"""
            SELECT id, username, nickname, school,
                   {column_repair_expr_sql("nickname")} AS fixed_nickname,
                   {column_repair_expr_sql("school")} AS fixed_school
            FROM user
            WHERE {MOJIBAKE_WHERE}
            """
        )
        rows = conn.execute(preview_sql).mappings().all()

        if not rows:
            print("No mojibake rows found.")
            return 0

        for row in rows:
            print(f"{row['username']}:")
            print(f"  nickname: {row['nickname']!r} -> {row['fixed_nickname']!r}")
            print(f"  school:   {row['school']!r} -> {row['fixed_school']!r}")

        if not args.apply:
            print("\nDry run only. Re-run with --apply to update the database.")
            return 0

        for table, columns in TEXT_COLUMNS.items():
            set_clause = ", ".join(
                f"{column} = {column_repair_expr_sql(column)}" for column in columns
            )
            update_sql = text(f"UPDATE `{table}` SET {set_clause} WHERE {table_where_sql(columns)}")
            result = conn.execute(update_sql)
            print(f"Updated {result.rowcount} row(s) in `{table}`.")

        conn.commit()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
