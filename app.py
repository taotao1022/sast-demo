"""
Demo Python app — intentionally contains security issues
so you can see SAST tools catch them in the pipeline.
"""

import subprocess
import sqlite3
import random
import secrets
import os
import bcrypt
from flask import Flask, request, jsonify


# ── ISSUE 1: SQL Injection ─────────────────────────────────────────────────
def get_user(username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # ✅ Parameterized query
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cursor.fetchall()


# ── ISSUE 2: OS Command Injection ──────────────────────────────────────────
def run_ping(host: str):
    # ✅ No shell=True, args passed as a list
    import ipaddress
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return b"Invalid host"
    result = subprocess.run(["ping", "-c", "1", host], capture_output=True)
    return result.stdout


# ── ISSUE 3: Weak Hashing ──────────────────────────────────────────────────
def hash_password(password: str) -> str:
    # ✅ bcrypt is slow by design — resistant to brute-force attacks
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


# ── ISSUE 4: Hardcoded Secret ──────────────────────────────────────────────
SECRET_KEY = "super-secret-key-1234"  # ❌ hardcoded credential


# ── ISSUE 5: Insecure Random ───────────────────────────────────────────────
def generate_token() -> str:
    # ❌ random is not cryptographically secure
    return str(random.randint(100000, 999999))


# ── SAFE usage (for comparison) ───────────────────────────────────────────
def generate_secure_token() -> str:
    # ✅ secrets module is cryptographically secure
    return secrets.token_hex(16)


def hash_password_safe(password: str) -> str:
    # ✅ SHA-256 with salt
    salt = secrets.token_bytes(16)
    return hashlib.sha256(salt + password.encode()).hexdigest()


# ── Flask routes — gives CodeQL real data-flow paths to trace ─────────────
app = Flask(__name__)


@app.route("/user")
def user():
    # ❌ user input flows into SQL query
    username = request.args.get("username")
    results = get_user(username)
    return jsonify(results)


@app.route("/ping")
def ping():
    # ❌ user input flows into shell command
    host = request.args.get("host")
    output = run_ping(host)
    return output


@app.route("/login", methods=["POST"])
def login():
    # ❌ password hashed with MD5
    password = request.form.get("password")
    hashed = hash_password(password)
    return jsonify({"hash": hashed})


def execute_query(query: str):
    conn = sqlite3.connect("users.db")
    # ❌ SQL injection — for gate demo
    conn.execute(query)


if __name__ == "__main__":
    # ✅ Controlled by environment variable, defaults to False
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug_mode)
