import os, psycopg2, pytest

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "supermario"),
        user=os.getenv("DB_USER", "mario"),
        password=os.getenv("DB_PASSWORD", "secret"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )

@pytest.fixture(scope="session", autouse=True)
def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS scores (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        score INT NOT NULL,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """)
    conn.commit()
    cur.close()
    conn.close()

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
    assert exists == "scores"
    conn.close()
