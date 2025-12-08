from typing import Any, List, Optional
import os

try:
    import streamlit as st
except Exception:
    st = None

try:
    import psycopg2
    import psycopg2.extras
except Exception:
    psycopg2 = None
    psycopg2_extras = None


def get_connection_string() -> Optional[str]:
    # Prefer Streamlit secrets when available
    if st is not None and hasattr(st, 'secrets') and isinstance(st.secrets, dict):
        conn = st.secrets.get('DB_CONNECTION_STRING') or st.secrets.get('db', {}).get('connection_string')
        if conn:
            return conn
    # Fallback to environment variable
    return os.environ.get('DB_CONNECTION_STRING')


def get_connection():
    conn_str = get_connection_string()
    if not conn_str:
        raise RuntimeError('Database connection string not set. Set st.secrets["DB_CONNECTION_STRING"] or env DB_CONNECTION_STRING')
    if psycopg2 is None:
        raise RuntimeError('psycopg2 is required but not installed. Please install psycopg2-binary')
    return psycopg2.connect(conn_str)


def db_query(query: str, params: Optional[tuple] = None) -> List[dict]:
    """Execute a SELECT query and return list of dict rows."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or ())
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    finally:
        try:
            conn.close()
        except Exception:
            pass


def db_execute(query: str, params: Optional[tuple] = None, returning: bool = False) -> Any:
    """Execute INSERT/UPDATE/DELETE. If returning=True, fetch one row from RETURNING clause."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params or ())
            if returning:
                try:
                    row = cur.fetchone()
                except Exception:
                    row = None
            else:
                row = None
        conn.commit()
        return row
    except Exception:
        conn.rollback()
        raise
    finally:
        try:
            conn.close()
        except Exception:
            pass
