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
   session_data = request.get_json()
return jsonify({"user": session_data})
    import json
    try:
        user = json.loads(session_data)
    except Exception as e:
        return jsonify({"error": "Invalid session data"}), 400
    return jsonify({"user": str(user)})


# ── Scenario 3: XML External Entity (XXE) ─────────────────────────────────
@app.route("/import-users", methods=["POST"])
def import_users():
    xml_data = request.get_data()
    # ✅ Use defusedxml to safely parse XML and prevent XXE attacks
    try:
        import defusedxml.ElementTree as SafeET
    except ImportError:
        return jsonify({"error": "Safe XML parser not available"}), 500
    try:
        tree = SafeET.fromstring(xml_data)
        users = [child.text for child in tree]
        return jsonify({"imported": users})
    except Exception as e:
        return jsonify({"error": "Invalid XML data"}), 400


# ── Scenario 4: Hardcoded Database Credentials ─────────────────────────────
DB_HOST = "prod-db.internal"
DB_USER = "admin"
DB_PASS = "Pr0d@dm1n2024!"   # ❌ hardcoded production password
DB_NAME = "users"


# ── Scenario 5: SQL Injection in Search ────────────────────────────────────
@app.route("/search")
def search_users():
    from sqlalchemy import create_engine, Column, String
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker

    # SQLAlchemy setup (typically move to global init in production)
    engine = create_engine('sqlite:///users.db')
    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'
        username = Column(String, primary_key=True)
        email = Column(String)

    Session = sessionmaker(bind=engine)
    session = Session()

    query = request.args.get("q", "")
    # Use ORM for parameterized, injection-safe LIKE filter
    users = session.query(User).filter(User.username.like(f"%{query}%")).all()
    results = [{"username": user.username, "email": user.email} for user in users]
    return jsonify(results)


# ── Scenario 6: OS Command in Log Rotation ─────────────────────────────────
@app.route("/admin/rotate-logs")
def rotate_logs():
    import os
    import subprocess

    log_name = request.args.get("log", "app.log")
    # Prevent directory traversal by permitting only basename
    log_name = os.path.basename(log_name)
    src = f"/var/log/{log_name}"
    dest = f"/var/log/{log_name}.bak"
    try:
        # Use subprocess to safely pass arguments as a list
        subprocess.check_call(['mv', src, dest])
    except subprocess.CalledProcessError:
        return jsonify({"error": "Log rotation failed"}), 500
    return jsonify({"status": "rotated"})

if __name__ == "__main__":
    import os
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)