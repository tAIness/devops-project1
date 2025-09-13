import os  # stdlib

from flask import Flask, request, jsonify  # third-party
import psycopg2  # third-party (only for the exception type)

# first-party
from db import init_db, insert_score, get_scores

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200


@app.route("/score", methods=["POST"])
def save_score():
    """
    Accepts JSON like: {"user_name": "mario", "result": 123}
    """
    data = request.get_json(silent=True) or {}
    user_name = data.get("user_name")
    result = data.get("result")

    if not user_name or not isinstance(result, int):
        return jsonify({"error": "Provide user_name (str) and result (int)"}), 400

    try:
        insert_score(user_name=user_name, result=result)
        return jsonify({"message": "saved"}), 201
    except psycopg2.Error as exc:  # narrower than bare Exception
        return jsonify({"error": "db_error", "detail": str(exc)}), 500


@app.route("/scores", methods=["GET"])
def list_scores():
    """
    Optional query param: ?limit=10
    """
    try:
        limit = int(request.args.get("limit", "10"))
    except ValueError:
        limit = 10

    try:
        rows = get_scores(limit=limit)
        # rows expected as list[dict] from db.get_scores()
        return jsonify(rows), 200
    except psycopg2.Error as exc:
        return jsonify({"error": "db_error", "detail": str(exc)}), 500


if __name__ == "__main__":
    # Initialize table if needed (safe to call more than once)
    init_db()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
