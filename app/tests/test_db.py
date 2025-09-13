import os
import psycopg2
import pytest

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )

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
