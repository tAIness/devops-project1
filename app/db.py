# app/db.py
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.pool import SimpleConnectionPool

# Single source of truth for DB connection in containers:
# service name 'db', default creds match docker-compose defaults.
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://supermario:supermario@db:5432/supermario",
)

_MIN_CONN = int(os.getenv("DB_POOL_MIN", "1"))
_MAX_CONN = int(os.getenv("DB_POOL_MAX", "10"))


def _get_pool() -> SimpleConnectionPool:
    """Create (once) and return a global connection pool."""
    pool = getattr(_get_pool, "_pool", None)
    if pool is None:
        _get_pool._pool = SimpleConnectionPool(
            minconn=_MIN_CONN,
            maxconn=_MAX_CONN,
            dsn=DATABASE_URL,
        )
        pool = _get_pool._pool
    return pool


@contextmanager
def get_conn() -> Iterator[psycopg2.extensions.connection]:
    """
    Borrow a connection from the pool.
    Usage:
        with get_conn() as conn, conn.cursor() as cur: ...
    """
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def init_db() -> None:
    """Idempotent table creation."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
                id SERIAL PRIMARY KEY,
                user_name TEXT NOT NULL,
                result INTEGER NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """
        )
        conn.commit()
