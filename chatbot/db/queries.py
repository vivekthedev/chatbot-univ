"""Raw SQL helpers used by agent tools (no business logic in tools layer)."""

from __future__ import annotations

from .connection import execute_query


def fetch_schema_columns(table_name: str | None = None) -> list[dict]:
    """Rows from information_schema.columns for the current database."""
    sql = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND (:table_name IS NULL OR table_name = :table_name)
        ORDER BY table_name, ordinal_position
    """
    return execute_query(sql, {"table_name": table_name})


def fetch_faculty_rows(
    *,
    name: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Parameterized faculty listing. The live `faculty` table has no `joined_year`
    column (see dump); filters are name / department / designation only.
    """
    conditions: list[str] = []
    params: dict = {}

    if name:
        conditions.append("name LIKE :name")
        params["name"] = f"%{name}%"
    if department:
        conditions.append("department LIKE :department")
        params["department"] = f"%{department}%"
    if designation:
        conditions.append("designation LIKE :designation")
        params["designation"] = f"%{designation}%"

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params["limit"] = limit

    sql = f"SELECT * FROM faculty {where} LIMIT :limit"
    return execute_query(sql, params)
