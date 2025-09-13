import flask
import requests
import jsonify
import db
import psycopg2
import json

app = flask(__name__)

with app.app_context():
  try:
    db.init_db()
  except psycopg2.Error as exc:
    app.logger.warning("DB init skipped: %s", exc)

@app.get("/health")
def health() -> tuple[str, int]:
    return "ok", 200

@app.post("/score")
def score():
    payload = requests.get_json(silent=True) or {}
    user = (
        payload.get("user")
        or requests.form.get("user")
        or requests.args.get("user")
        or ""
    ).strip()

    result_raw = (
        payload.get("result")
        or requests.form.get("result")
        or requests.args.get("result")
    )

    if not user:
        return jsonify({"error": "user is required"}), 400
    try:
        result = int(result_raw)
    except (TypeError, ValueError):
        return jsonify({"error": "result must be integer"}), 400

    # FIX: pass both user and result
    db.insert_score(user, result)
    return jsonify({"status": "saved"}), 201

@app.get("/scores")
def scores():
    limit = requests.args.get("limit", default="50")
    try:
        limit_i = max(1, min(500, int(limit)))
    except ValueError:
        limit_i = 50
    return jsonify(db.list_scores(limit=limit_i))

# Ensure table exists on startup
with app.app_context():
    try:
        db.init_db()
    except Exception as exc:  # pragma: no cover
        app.logger.warning("DB init skipped: %s", exc)
