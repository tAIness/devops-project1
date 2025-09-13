import os
from functools import lru_cache
from contextlib import contextmanager
from psycopg2.pool import SimpleConnectionPool

def _env(name: str, default: str) -> str:
    return os.getenv(name, default)

@lru_cache(maxsize=1)
def get_pool() -> SimpleConnectionPool:
    """
    Lazily create one connection pool and reuse it (no globals).
    Defaults match docker-compose; override via env in CI/Prod.
    """
    return SimpleConnectionPool(
        minconn=1,
        maxconn=int(_env("DB_MAXCONN", "5")),
        dbname=_env("DB_NAME", "supermario"),
        user=_env("DB_USER", "mario"),
        password=_env("DB_PASSWORD", "secret"),
        host=_env("DB_HOST", "db"),   # CI uses 'postgres'; compose uses 'db'
        port=int(_env("DB_PORT", "5432")),
    )

@contextmanager
def conn():
    pool = get_pool()
    c = pool.getconn()
    try:
        yield c
    finally:
        pool.putconn(c)

def init_db() -> None:
    """Create table if it doesn't exist."""
    with conn() as c, c.cursor() as cur:
        cur.execute(
            "CREATE TABLE IF NOT EXISTS scores ("
            "id SERIAL PRIMARY KEY, "
            "user_name TEXT NOT NULL, "
            "result INT NOT NULL, "
            "created_at TIMESTAMP DEFAULT NOW()"
            ")"
        )
        c.commit()

def insert_score(user_name: str, result: int) -> None:
    with conn() as c, c.cursor() as cur:
        cur.execute(
            "INSERT INTO scores (user_name, result) VALUES (%s, %s)",
            (user_name, int(result)),
        )
        c.commit()

def list_scores(limit: int = 50):
    with conn() as c, c.cursor() as cur:
        cur.execute(
            "SELECT user_name, result, created_at "
            "FROM scores ORDER BY id DESC LIMIT %s",
            (limit,),
        )
        rows = cur.fetchall()
        return [
            {"user": u, "result": r, "created_at": str(ts)}
            for (u, r, ts) in rows
        ]
