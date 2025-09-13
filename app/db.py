# app/db.py
from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor

# ---- connection settings from env ----
DB_NAME = os.getenv("DB_NAME", "supermario")
DB_USER = os.getenv("DB_USER", "mario")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))


def _get_pool() -> SimpleConnectionPool:
    """Lazy-create and reuse a single connection pool (no globals/classes)."""
    pool = getattr(_get_pool, "pool", None)
    if pool is None:
        _get_pool.pool = SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
        )
        pool = _get_pool.pool
    return pool


@contextmanager
def get_conn() -> Iterator[psycopg2.extensions.connection]:
    pool = _get_pool()
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)


def init_db() -> None:
    """Create the scores table if it doesn't exist."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS scores (
              id SERIAL PRIMARY KEY,
              user_name TEXT NOT NULL,
              result INTEGER NOT NULL,
              created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
            """
        )
        conn.commit()


def insert_score(user_name: str, result: int) -> None:
    """Insert one score row."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO scores (user_name, result) VALUES (%s, %s);",
            (user_name, result),
        )
        conn.commit()


def get_scores(limit: int = 10) -> list[dict]:
    """Return latest scores as a list of dicts."""
    with get_conn() as conn, conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(
            """
            SELECT id, user_name, result, created_at
            FROM scores
            ORDER BY id DESC
            LIMIT %s;
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [dict(r) for r in rows]
