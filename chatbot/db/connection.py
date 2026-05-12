from sqlalchemy import create_engine, text

from config import DATABASE_URL

_engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def execute_query(sql: str, params: dict | None = None) -> list[dict]:
    """
    Run a parameterized statement and return rows as dicts.
    Uses SQLAlchemy :name bound parameters (works with PyMySQL).
    """
    params = params or {}
    with _engine.connect() as conn:
        result = conn.execute(text(sql), params)
        return [dict(row._mapping) for row in result]
