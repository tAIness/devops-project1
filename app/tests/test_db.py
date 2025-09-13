import os
import time
import psycopg2
import pytest

pytestmark = pytest.mark.db  # mark these as DB tests

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "supermario"),
        user=os.getenv("DB_USER", "mario"),
        password=os.getenv("DB_PASSWORD", "secret"),
        host=os.getenv("DB_HOST", "127.0.0.1"),   # <-- use loopback by default
        port=os.getenv("DB_PORT", "5432"),
    )

@pytest.fixture(scope="session", autouse=True)
def init_db():
    # retry a bit to allow the service to come up
    for _ in range(20):
        try:
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    id SERIAL PRIMARY KEY,
                    user_name TEXT,
                    result INT
                );
            """)
            conn.commit()
            conn.close()
            return
        except Exception as e:
            print(f"DB not ready yet: {e}")
            time.sleep(2)
    pytest.fail("DB not reachable after retries")

def test_connection():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    assert cur.fetchone()[0] == 1
    conn.close()

def test_table_exists():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT to_regclass('public.scores');")
    exists = cur.fetchone()[0]
    assert exists == "scores", "scores table should exist"
    conn.close()
