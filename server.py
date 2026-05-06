"""
server.py — Minimal Flask server to satisfy Render's port-binding requirement.
This provides a basic API health check and keeps the service alive on Render.
"""

import os
from flask import Flask, jsonify
from database.db_manager import db
from database.seed_data import seed

app = Flask(__name__)

# Initialise database on startup (similar to main.py)
db.connect()
db.init_schema()
seed()

@app.route("/")
def index():
    return jsonify({
        "status": "online",
        "app": "Horizon Cinemas Booking System",
        "message": "Backend service is running successfully."
    })

@app.route("/health")
def health():
    try:
        # Check if DB is responsive
        db.fetchone("SELECT 1")
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

if __name__ == "__main__":
    # Get port from environment variable for Render
    PORT = int(os.getenv("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT)
