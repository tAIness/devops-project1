import os, time, psycopg2, pytest

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
    # retry loop
    for i in range(10):
        try:
            conn = get_conn()
            break
        except psycopg2.OperationalError as e:
            print(f"DB not ready yet, retry {i+1}/10: {e}")
            time.sleep(3)
    else:
        raise RuntimeError("Postgres did not become ready in time")

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
