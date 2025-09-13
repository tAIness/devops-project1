# app/app.py
from flask import Flask, jsonify, request
import psycopg2
from app.db import with_conn, init_schema

app = Flask(__name__)

@app.get("/health")
def health():
    return {"ok": True}

# initialize schema on boot
with app.app_context():
    init_schema()

@with_conn
def _insert_score(conn, user_name: str, result: int):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO scores (user_name, result) VALUES (%s, %s) RETURNING id;",
                    (user_name, result))
        new_id = cur.fetchone()[0]
    conn.commit()
    return new_id

@with_conn
def _fetch_scores(conn, limit: int = 100):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, user_name, result, created_at
            FROM scores
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    return [
        {"id": r[0], "user_name": r[1], "result": r[2], "created_at": r[3].isoformat()}
        for r in rows
    ]

@with_conn
def _fetch_leaderboard(conn, limit: int = 20):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT user_name, MAX(result) AS best
            FROM scores
            GROUP BY user_name
            ORDER BY best DESC, user_name ASC
            LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
    return [{"user_name": r[0], "best": r[1]} for r in rows]

@app.post("/api/score")
def post_score():
    data = request.get_json(silent=True) or {}
    user_name = (data.get("user_name") or "").strip()
    result = data.get("result")
    if not user_name or not isinstance(result, int):
        return jsonify({"error": "Provide user_name (non-empty) and result (int)"}), 400
    new_id = _insert_score(user_name, result)
    return jsonify({"id": new_id, "user_name": user_name, "result": result}), 201

@app.get("/api/scores")
def list_scores():
    limit = int(request.args.get("limit", 100))
    return jsonify(_fetch_scores(limit))

@app.get("/api/leaderboard")
def leaderboard():
    limit = int(request.args.get("limit", 20))
    return jsonify(_fetch_leaderboard(limit))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
