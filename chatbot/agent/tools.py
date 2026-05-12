from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

from config import TAVILY_API_KEY
from db import queries


# ── Schema Tool ────────────────────────────────────────────────────────────────


@tool
def get_db_schema(table_name: str | None = None) -> str:
    """
    Returns the university database schema.
    If table_name is provided, returns columns and types for that table only.
    Otherwise returns all tables with their column names.

    Always call this before querying data if you are unsure which table or column to use.
    """
    rows = queries.fetch_schema_columns(table_name)

    if not rows:
        return "No schema information found."

    output: list[str] = []
    current_table: str | None = None

    for row in rows:
        tbl = row.get("table_name") or row.get("TABLE_NAME")
        col = row.get("column_name") or row.get("COLUMN_NAME")
        dtype = row.get("data_type") or row.get("DATA_TYPE")

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
    limit: int = Field(10, description="Maximum number of results to return (default 10)")


@tool(args_schema=FacultyInput)
def query_faculty_data(
    name: str | None = None,
    department: str | None = None,
    designation: str | None = None,
    limit: int = 10,
) -> str:
    """
    Query faculty from the university database using optional filters.
    Leave any unused filter as None — all filters are optional.
    Returns a human-readable summary of matching faculty members.
    """
    try:
        rows = queries.fetch_faculty_rows(
            name=name,
            department=department,
            designation=designation,
            limit=limit,
        )
    except Exception as exc:  # noqa: BLE001 — surface DB errors to the model
        return f"Database query failed: {exc!s}. Try get_db_schema to verify tables."

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
        for field in ("specialization", "qualification", "teaching_experience", "phone"):
            val = r.get(field)
            if val and val != "NA":
                parts.append(f"{field.replace('_', ' ').title()}: {val}")
        lines.append(" | ".join(parts))
        lines.append("")

    return "\n".join(lines).strip()


# ── Tavily Web Search Tool ─────────────────────────────────────────────────────

_TOOLS = [get_db_schema, query_faculty_data]

if TAVILY_API_KEY:
    tavily_tool = TavilySearch(
        max_results=4,
        name="tavily_search",
        description=(
            "Search the web for current information about the university, "
            "academic programs, rankings, news, or anything not available "
            "in the internal database."
        ),
    )
    _TOOLS.append(tavily_tool)
else:
    tavily_tool = None  # type: ignore[assignment]

TOOLS = _TOOLS
