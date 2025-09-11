"""Simple Flask app exposing health and root endpoints."""

from flask import Flask

app = Flask(__name__)

@app.get("/health")
def health():
    """Return a simple health-check response."""
    return "ok\n", 200

@app.get("/")
def home():
    """Return home page content."""
    return "Hello from the app!\n", 200
