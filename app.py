"""
Demo Python app — security issues fixed.
"""

import sqlite3
import hashlib
import secrets
import os
from flask import Flask, request, jsonify


# ── FIX 1: SQL Injection → parameterized query ─────────────────────────────
def get_user(username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # ✅ Parameterized query — user input never touches the SQL string
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchall()


# ── FIX 2: Command Injection → no shell=True, validated input ──────────────
def run_ping(host: str):
    import ipaddress
    import subprocess
    # ✅ Validate host is a real IP before passing to subprocess
    # ✅ shell=False (default), arguments passed as a list
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return b"Invalid host"
    result = subprocess.run(["ping", "-c", "1", host], capture_output=True)
    return result.stdout


# ── FIX 3: Weak Hashing → SHA-256 with salt ────────────────────────────────
def hash_password(password: str) -> str:
    # ✅ SHA-256 with a random salt (use bcrypt/argon2 in production)
    salt = secrets.token_bytes(16)
    return hashlib.sha256(salt + password.encode()).hexdigest()


# ── FIX 4: Hardcoded Secret → environment variable ─────────────────────────
# ✅ Read secret from environment — set it with: export SECRET_KEY=your-secret
SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is not set")


# ── FIX 5: Insecure Random → secrets module ────────────────────────────────
def generate_token() -> str:
    # ✅ secrets.token_hex is cryptographically secure
    return secrets.token_hex(16)


# ── Flask routes ───────────────────────────────────────────────────────────
app = Flask(__name__)


@app.route("/user")
def user():
    username = request.args.get("username", "")
    results = get_user(username)
    return jsonify(results)


@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    output = run_ping(host)
    return output


@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password", "")
    hashed = hash_password(password)
    return jsonify({"hash": hashed})


if __name__ == "__main__":
    # ✅ debug=False in production — use an env var to control this
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
