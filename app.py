"""
Demo Python app — intentionally contains security issues
so you can see SAST tools catch them in the pipeline.
"""

import subprocess
import sqlite3
import hashlib
import os


# ── ISSUE 1: SQL Injection (Bandit B608, Semgrep, CodeQL) ──────────────────
def get_user(username: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # ✅ Use a parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))
    return cursor.fetchall()

# ── FIXED: OS Command Injection mitigated (Bandit B602, Semgrep) ──────────────
# Avoids shell=True by using a list of arguments and validates input is a valid hostname/IP.
def run_ping(host: str):
    # ✅ Avoids shell=True by using a list of arguments and validates input is a valid hostname/IP.
    import re

    def is_valid_host(host: str) -> bool:
        # Accepts valid IPv4/IPv6 or hostname (basic check)
        hostname_regex = re.compile(
            r"^(?=.{1,253}$)((?!-)[A-Za-z0-9-]{1,63}(?<!-)\.?)+$"
        )
        ipv4_regex = re.compile(
            r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
        )
        ipv6_regex = re.compile(
            r"^\[?([a-fA-F0-9:]+)\]?$"
        )
        return bool(hostname_regex.match(host) or ipv4_regex.match(host) or ipv6_regex.match(host))

    if not is_valid_host(host):
        raise ValueError("Invalid host")

    result = subprocess.run(
        ["ping", "-c", "1", host],
        capture_output=True
    )
    return result.stdout


# ── ISSUE 3: Weak Hashing (Bandit B303, Semgrep) ──────────────────────────
def hash_password(password: str) -> str:
    # ✅ Use a strong password hashing function (e.g., bcrypt) instead of general-purpose hash functions
    import bcrypt
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    # Return salt+hash in the bcrypt format as a UTF-8 string
    return hashed.decode('utf-8')

# ── ISSUE 4: Hardcoded Secret (Bandit B105, Semgrep) ──────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY")   # ✅ Load secret from environment variable


# ── ISSUE 5: Insecure Random (Bandit B311) ────────────────────────────────
import secrets
def generate_token() -> str:
    # ✅ Use secrets for cryptographically secure randomness
    return str(secrets.randbelow(1000000)).zfill(6)



# ── SAFE usage (for comparison) ───────────────────────────────────────────
import secrets

def generate_secure_token() -> str:
    # ✅ secrets module is cryptographically secure
    return secrets.token_hex(16)


def hash_password_safe(password: str) -> str:
    # ✅ use bcrypt or hashlib with sha256+salt in production
    salt = secrets.token_bytes(16)
    return hashlib.sha256(salt + password.encode()).hexdigest()


# ── Flask routes — gives CodeQL real data-flow paths to trace ─────────────
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/user")
def user():
    # ❌ request.args (user input) flows directly into get_user() → SQL injection
    username = request.args.get("username")
    results = get_user(username)
    return jsonify(results)


@app.route("/ping")
def ping():
    # ❌ request.args (user input) flows directly into run_ping() → command injection
    host = request.args.get("host")
    output = run_ping(host)
    return output


@app.route("/login", methods=["POST"])
def login():
    # ❌ user-supplied password hashed with MD5
    password = request.form.get("password")
    hashed = hash_password(password)
    return jsonify({"hash": hashed})


if __name__ == "__main__":
    app.run(debug=True)
