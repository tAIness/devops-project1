# app/app.py
import os
from flask import Flask, request, jsonify
import psycopg2
import psycopg2.extras

from db import get_conn, init_db

app = Flask(__name__)

# Try to create the table at startup (idempotent). If DB isn't ready yet,
# we don't crash; healthcheck/first request will succeed later.
try:
    init_db()
except Exception as e:
    app.logger.warning("init_db failed (will retry on next request): %s", e)


@app.get("/health")
def health():
    """Lightweight probe that also checks DB connectivity."""
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        # Return 200 so container can keep retrying during startup
        return jsonify({"status": "degraded", "detail": str(e)}), 200


@app.post("/api/score")
def api_score():
    """Insert a score. Accepts {"user_name": str, "result": int} (or {"name","ms"})."""
    data = request.get_json(silent=True) or {}

    user_name = data.get("user_name") or data.get("name")
    raw_result = data.get("result", data.get("ms"))

    try:
        result = int(raw_result) if raw_result is not None else None
    except (ValueError, TypeError):
        result = None

    if not user_name or result is None:
        return jsonify({"error": "Provide user_name (str) and result (int)"}), 400

    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO scores(user_name, result) VALUES (%s, %s)",
                (user_name, result),
            )
            conn.commit()
        return jsonify({"ok": True}), 201
    except psycopg2.Error as exc:
        return jsonify({"error": "db_error", "detail": str(exc)}), 500


@app.get("/api/leaderboard")
def api_leaderboard():
    """Return best (lowest) result per user."""
    try:
        with get_conn() as conn, conn.cursor(
            cursor_factory=psycopg2.extras.DictCursor
        ) as cur:
            cur.execute(
              """
               SELECT user_name, MIN(result) AS best
               FROM scores
               GROUP BY user_name
               ORDER BY best ASC, user_name ASC
               LIMIT 20
              """
            )
            rows = [{"user_name": r["user_name"], "best": int(r["best"])} for r in cur.fetchall()]
        return jsonify(rows), 200
    except psycopg2.Error as exc:
        return jsonify({"error": "db_error", "detail": str(exc)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
