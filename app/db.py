# app/db.py
import os
from psycopg2.pool import SimpleConnectionPool
import psycopg2

DB_NAME = os.getenv("DB_NAME", "supermario")
DB_USER = os.getenv("DB_USER", "mario")
DB_PASSWORD = os.getenv("DB_PASSWORD", "secret")
DB_HOST = os.getenv("DB_HOST", "db")      # 'db' if using docker-compose service, or set to your host
DB_PORT = int(os.getenv("DB_PORT", "5432"))

_pool = None

def get_pool():
    global _pool
    if _pool is None:
        _pool = SimpleConnectionPool(
            minconn=1, maxconn=5,
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
            host=DB_HOST, port=DB_PORT
        )
    return _pool

def with_conn(fn):
    def _wrap(*args, **kwargs):
        pool = get_pool()
        conn = pool.getconn()
        try:
            return fn(conn, *args, **kwargs)
        finally:
            pool.putconn(conn)
    return _wrap

def init_schema():
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                  id SERIAL PRIMARY KEY,
                  user_name TEXT NOT NULL,
                  result    INT  NOT NULL,
                  created_at TIMESTAMP DEFAULT NOW()
                );
            """)
        conn.commit()
    finally:
        pool.putconn(conn)
