"""
User management module — all security issues fixed.
"""

import os
import sqlite3
import subprocess
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)


# ── FIX 1: Path Traversal ──────────────────────────────────────────────────
@app.route("/download")
def download_file():
    filename = request.args.get("filename", "")
    reports_dir = os.path.abspath("/app/reports")
    if not filename or "/" in filename or "\\" in filename:
        return jsonify({"error": "Invalid filename"}), 400
    filepath = os.path.abspath(os.path.join(reports_dir, filename))
    if not filepath.startswith(reports_dir + os.sep):
        return jsonify({"error": "Invalid file path"}), 400
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath)


# ── FIX 2: Insecure Deserialization ───────────────────────────────────────
@app.route("/load-session", methods=["POST"])
def load_session():
    # ✅ JSON cannot execute code — safe replacement for pickle
    session_data = request.get_json()
    return jsonify({"user": session_data})


# ── FIX 3: XXE ────────────────────────────────────────────────────────────
@app.route("/import-users", methods=["POST"])
def import_users():
    xml_data = request.get_data()
    # ✅ defusedxml disables external entity processing
    try:
        import defusedxml.ElementTree as SafeET
    except ImportError:
        return jsonify({"error": "Safe XML parser not available"}), 500
    try:
        tree = SafeET.fromstring(xml_data)
        users = [child.text for child in tree]
        return jsonify({"imported": users})
    except Exception:
        return jsonify({"error": "Invalid XML data"}), 400


# ── FIX 4: Hardcoded Credentials ──────────────────────────────────────────
# ✅ All credentials read from environment variables
DB_HOST = os.environ.get("DB_HOST", "")
DB_USER = os.environ.get("DB_USER", "")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "")


# ── FIX 5: SQL Injection in Search ────────────────────────────────────────
@app.route("/search")
def search_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = request.args.get("q", "")
    # ✅ Parameterized LIKE query
    results = cursor.execute(
        "SELECT username, email FROM users WHERE username LIKE ?",
        (f"%{query}%",)
    ).fetchall()
    return jsonify(results)


# ── FIX 6: Command Injection in Log Rotation ──────────────────────────────
@app.route("/admin/rotate-logs")
def rotate_logs():
    import shutil
    log_name = request.args.get("log", "app.log")
    # ✅ Validate filename, use shutil instead of shell command
    log_name = os.path.basename(log_name)
    if not log_name.endswith(".log"):
        return jsonify({"error": "Invalid log name"}), 400
    src = f"/var/log/{log_name}"
    dst = f"/var/log/{log_name}.bak"
    try:
        shutil.move(src, dst)
    except Exception:
        return jsonify({"error": "Log rotation failed"}), 500
    return jsonify({"status": "rotated"})


if __name__ == "__main__":
    # ✅ debug mode controlled by environment variable
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
