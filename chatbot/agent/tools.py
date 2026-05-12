import os
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field
from db import execute_query
from config import TAVILY_API_KEY


# ── Schema Tool ────────────────────────────────────────────────────────────────

@tool
def get_db_schema(table_name: str | None = None) -> str:
    """
    Returns the university database schema.
    If table_name is provided, returns columns and types for that table only.
    Otherwise returns all tables with their column names.

    Always call this before querying data if you are unsure which table or column to use.
    """
    sql = """
        SELECT table_name, column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = DATABASE()
          AND (:table_name IS NULL OR table_name = :table_name)
        ORDER BY table_name, ordinal_position
    """
    rows = execute_query(sql, {"table_name": table_name})

    if not rows:
        return "No schema information found."

    output: list[str] = []
    current_table: str | None = None

    for row in rows:
        tbl = row["TABLE_NAME"] if "TABLE_NAME" in row else row["table_name"]
        col = row["COLUMN_NAME"] if "COLUMN_NAME" in row else row["column_name"]
        dtype = row["DATA_TYPE"] if "DATA_TYPE" in row else row["data_type"]

        if tbl != current_table:
            current_table = tbl
            output.append(f"\nTable: {tbl}")
        output.append(f"  - {col} ({dtype})")

    return "\n".join(output)


# ── Faculty Query Tool ─────────────────────────────────────────────────────────

class FacultyInput(BaseModel):
    name: str | None = Field(None, description="Faculty member's name (partial match supported)")
    department: str | None = Field(None, description="Department name (partial match supported)")
    designation: str | None = Field(None, description="e.g. Professor, Assistant Professor, Associate Professor")
    joined_year: int | None = Field(None, description="Year the faculty member joined")
    limit: int = Field(10, description="Maximum number of results to return (default 10)")


@tool(args_schema=FacultyInput)
def query_faculty_data(
    name: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    joined_year: int | None = None,
    limit: int = 10,
) -> str:
    """
    Query faculty from the university database using optional filters.
    Leave any unused filter as None — all filters are optional.
    Returns a human-readable summary of matching faculty members.
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
    if joined_year:
        conditions.append("joined_year = :joined_year")
        params["joined_year"] = joined_year

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    params["limit"] = limit

    rows = execute_query(f"SELECT * FROM faculty {where} LIMIT :limit", params)

    if not rows:
        return "No faculty records found matching your query."

    lines: list[str] = []
    for r in rows:
        parts = [
            f"Name: {r.get('name', 'N/A')}",
            f"Designation: {r.get('designation', 'N/A')}",
            f"Department: {r.get('department', 'N/A')}",
            f"School: {r.get('school', 'N/A')}",
            f"Email: {r.get('email', 'N/A')}",
        ]
        # Include optional fields only if present and not 'NA'
        for field in ("specialization", "qualification", "teaching_experience", "phone"):
            val = r.get(field)
            if val and val != "NA":
                parts.append(f"{field.replace('_', ' ').title()}: {val}")
        lines.append(" | ".join(parts))
        lines.append("")  # blank line between records

    return "\n".join(lines).strip()


# ── Tavily Web Search Tool ─────────────────────────────────────────────────────

_TOOLS = [get_db_schema, query_faculty_data]

if TAVILY_API_KEY:
    tavily_tool = TavilySearch(
        max_results=4,
        name="tavily_search",
        description=(
            "Search the web for current information about BBAU — news, rankings, "
            "admission updates, events, or anything not available in the internal database."
        ),
    )
    _TOOLS.append(tavily_tool)
else:
    tavily_tool = None

TOOLS = _TOOLS
