"""Routes deliberately containing issues for SAST and remediation exercises.

DO NOT deploy this module to a public or production environment. Each route has
an intentionally insecure pattern identified by a `VULNERABILITY:` comment.
"""

from pathlib import Path
import os
import sqlite3

from flask import Blueprint, current_app, jsonify, render_template, request, session

from .database import get_db

bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/register")
def register():
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "")
    password = data.get("password", "")
    email = data.get("email", "")
    if not username or not password or not email:
        return jsonify({"error": "username, password, and email are required"}), 400

    # VULNERABILITY: password stored in plaintext rather than using a password hash.
    try:
        get_db().execute(
            "INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
            (username, password, email),
        )
        get_db().commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "username already exists"}), 409
    return jsonify({"message": "registered"}), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or request.form
    username = data.get("username", "")
    password = data.get("password", "")

    # VULNERABILITY: SQL injection caused by interpolating untrusted input.
    query = f"SELECT id, username, role FROM users WHERE username = '{username}' AND password = '{password}'"
    user = get_db().execute(query).fetchone()
    if user is None:
        return jsonify({"error": "invalid credentials"}), 401
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    return jsonify({"message": "logged in", "user": user["username"]})


@bp.get("/profile/<username>")
def profile(username: str):
    # VULNERABILITY: IDOR / broken access control; any profile can be requested.
    user = get_db().execute(
        "SELECT username, email, role FROM users WHERE username = ?", (username,)
    ).fetchone()
    if user is None:
        return jsonify({"error": "user not found"}), 404
    return jsonify(dict(user))


@bp.post("/upload")
def upload():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "file is required"}), 400

    # VULNERABILITY: user-controlled filename, no extension/content/size validation.
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)
    destination = upload_dir / uploaded.filename
    uploaded.save(destination)
    return jsonify({"message": "uploaded", "filename": uploaded.filename}), 201


@bp.get("/api/users")
def api_users():
    # VULNERABILITY: unauthenticated endpoint exposes all users and plaintext passwords.
    rows = get_db().execute("SELECT id, username, password, email, role FROM users").fetchall()
    return jsonify([dict(row) for row in rows])


@bp.get("/admin")
def admin():
    # VULNERABILITY: trusts a query parameter instead of server-side authorization.
    if request.args.get("role") != "admin":
        return jsonify({"error": "admin access required"}), 403
    return jsonify({"message": "welcome to the admin panel", "users": get_db().execute("SELECT COUNT(*) FROM users").fetchone()[0]})


@bp.get("/diagnostics")
def diagnostics():
    # VULNERABILITY: leaks sensitive configuration and environment values.
    return jsonify({"secret_key": current_app.config["SECRET_KEY"], "environment": dict(os.environ)})
