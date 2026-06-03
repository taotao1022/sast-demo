"""
User management module — added by junior developer.
Contains several real-world security mistakes.
"""

import os
import pickle
import sqlite3
import subprocess
import xml.etree.ElementTree as ET
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)


# ── Scenario 1: Path Traversal ─────────────────────────────────────────────
@app.route("/download")
def download_file():
    filename = request.args.get("filename")
    # ❌ Path traversal: attacker can pass "../../etc/passwd"
    filepath = os.path.join("/app/reports", filename)
    return send_file(filepath)


# ── Scenario 2: Insecure Deserialization ───────────────────────────────────
@app.route("/load-session", methods=["POST"])
def load_session():
    session_data = request.get_data()
    # ❌ Deserializing user-supplied data with pickle — remote code execution
    user = pickle.loads(session_data)
    return jsonify({"user": str(user)})


# ── Scenario 3: XML External Entity (XXE) ─────────────────────────────────
@app.route("/import-users", methods=["POST"])
def import_users():
    xml_data = request.get_data()
    # ❌ XXE: attacker can read local files via XML external entities
    tree = ET.fromstring(xml_data)
    users = [child.text for child in tree]
    return jsonify({"imported": users})


# ── Scenario 4: Hardcoded Database Credentials ─────────────────────────────
DB_HOST = "prod-db.internal"
DB_USER = "admin"
DB_PASS = "Pr0d@dm1n2024!"   # ❌ hardcoded production password
DB_NAME = "users"


# ── Scenario 5: SQL Injection in Search ────────────────────────────────────
@app.route("/search")
def search_users():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = request.args.get("q", "")
    # ❌ SQL injection via search input
    results = cursor.execute(
        "SELECT username, email FROM users WHERE username LIKE '%" + query + "%'"
    ).fetchall()
    return jsonify(results)


# ── Scenario 6: OS Command in Log Rotation ─────────────────────────────────
@app.route("/admin/rotate-logs")
def rotate_logs():
    log_name = request.args.get("log", "app.log")
    # ❌ Command injection: attacker can pass "app.log; rm -rf /"
    os.system(f"mv /var/log/{log_name} /var/log/{log_name}.bak")
    return jsonify({"status": "rotated"})


if __name__ == "__main__":
    app.run(debug=True)   # ❌ debug=True left on
