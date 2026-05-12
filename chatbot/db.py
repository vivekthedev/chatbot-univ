from sqlalchemy import create_engine, text
from config import DATABASE_URL

# Single engine instance shared across all tool calls
_engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def execute_query(sql: str, params: dict = {}) -> list[dict]:
    """
    Execute a parameterized SQL query and return results as a list of dicts.
    Uses SQLAlchemy :named_param style placeholders.

    Example:
        execute_query("SELECT * FROM faculty WHERE name LIKE :name", {"name": "%Kumar%"})
    """
    with _engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(row._mapping) for row in result]
