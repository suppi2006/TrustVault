
import os
import sqlite3
import secrets
import hmac
from pathlib import Path
from werkzeug.utils import secure_filename

from functools import wraps
from flask import (
    Flask, request, redirect, url_for,
    session, render_template_string, abort,send_from_directory

)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Development key only. Set SECRET_KEY in the deployment environment.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "local-dev-key-change-before-deployment")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

app.config["SESSION_COOKIE_SECURE"] = (
    os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
)

DATABASE = "trustvault.db"

UPLOAD_FOLDER = Path(app.root_path) / "private_uploads"
UPLOAD_FOLDER.mkdir(exist_ok=True)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".png", ".jpg", ".jpeg"}


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        """)
        
        db.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER NOT NULL,
                original_name TEXT NOT NULL,
                stored_name TEXT NOT NULL UNIQUE,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER,
                document_id INTEGER,
                action TEXT NOT NULL,
                details TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def allowed_file(filename):
    return (
        "." in filename
        and Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
    )


def add_audit_log(actor_id, document_id, action, details):
    with get_db() as db:
        db.execute(
            """
            INSERT INTO audit_logs
                (actor_id, document_id, action, details)
            VALUES (?, ?, ?, ?)
            """,
            (actor_id, document_id, action, details)
        )


def csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


def check_csrf():
    submitted = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not expected or not hmac.compare_digest(submitted, expected):
        abort(400, "Invalid form token. Refresh the page and try again.")


PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TrustVault</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f1f5f9;
            margin: 0;
            padding: 30px 16px;
            color: #172554;
        }
        .card {
            max-width: 430px;
            margin: 45px auto;
            padding: 28px;
            background: white;
            border-radius: 14px;
            box-shadow: 0 4px 18px #00000012;
        }
        h1, h2 { text-align: center; }
        h1 { color: #1d4ed8; }
        label { display: block; margin-top: 16px; }
        input {
            box-sizing: border-box;
            width: 100%;
            padding: 11px;
            margin-top: 6px;
            border: 1px solid #cbd5e1;
            border-radius: 7px;
        }
        button, .button {
            display: inline-block;
            box-sizing: border-box;
            width: 100%;
            margin-top: 18px;
            padding: 12px;
            border: 0;
            border-radius: 7px;
            background: #1d4ed8;
            color: white;
            text-align: center;
            text-decoration: none;
            cursor: pointer;
        }
        .message { text-align: center; color: #475569; }
        .error { color: #b91c1c; }
        .success { color: #166534; }
        a { color: #1d4ed8; }
    </style>
</head>
<body>
    <main class="card">
        <h1>🔐 TrustVault</h1>
        {% if message %}
            <p class="message {{ kind }}">{{ message }}</p>
        {% endif %}
        {{ content|safe }}
    </main>
</body>
</html>
"""


def page(content, message="", kind=""):
    return render_template_string(
        PAGE,
        content=content,
        message=message,
        kind=kind
    )


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return page("""
        <h2>Secure Document Sharing</h2>
        <p class="message">Create an account or log in to continue.</p>
        <a class="button" href="/register">Create account</a>
        <a class="button" href="/login">Log in</a>
    """)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    kind = "error"

    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if len(username) < 3 or len(username) > 40:
            message = "Username must be 3 to 40 characters."
        elif len(password) < 12:
            message = "Use a password with at least 12 characters."
        else:
            password_hash = generate_password_hash(password)
            try:
                with get_db() as db:
                    db.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (username, password_hash)
                    )
                message = "Account created. You can now log in."
                kind = "success"
            except sqlite3.IntegrityError:
                message = "That username is already taken."

    content = """
        <h2>Create account</h2>
        <form method="post">
            <input type="hidden" name="csrf_token" value="{{ token }}">
            <label>Username</label>
            <input name="username" minlength="3" maxlength="40" required>
            <label>Password (at least 12 characters)</label>
            <input type="password" name="password" minlength="12" required>
            <button type="submit">Register</button>
        </form>
        <p class="message">Already registered? <a href="/login">Log in</a></p>
    """
    return page(render_template_string(content, token=csrf_token()), message, kind)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""

    if request.method == "POST":
        check_csrf()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        with get_db() as db:
            user = db.execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?",
                (username,)
            ).fetchone()

        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            csrf_token()
            return redirect(url_for("dashboard"))

        message = "Invalid username or password."

    content = """
        <h2>Log in</h2>
        <form method="post">
            <input type="hidden" name="csrf_token" value="{{ token }}">
            <label>Username</label>
            <input name="username" required>
            <label>Password</label>
            <input type="password" name="password" required>
            <button type="submit">Log in</button>
        </form>
        <p class="message">New here? <a href="/register">Create an account</a></p>
    """
    return page(render_template_string(content, token=csrf_token()), message, "error")



@app.route("/upload", methods=["POST"])
@login_required
def upload_document():
    check_csrf()

    file = request.files.get("document")

    if not file or file.filename == "":
        return redirect(url_for("dashboard"))

    if not allowed_file(file.filename):
        abort(400, "File type not allowed.")

    original_name = secure_filename(file.filename)

    if not original_name:
        abort(400, "Invalid filename.")

    stored_name = secrets.token_hex(16) + Path(original_name).suffix.lower()
    file_path = UPLOAD_FOLDER / stored_name

    file.save(file_path)

    try:
        with get_db() as db:
            cursor = db.execute(
                """
                INSERT INTO documents (owner_id, original_name, stored_name)
                VALUES (?, ?, ?)
                """,
                (session["user_id"], original_name, stored_name)
            )
            document_id = cursor.lastrowid

        add_audit_log(
            session["user_id"],
            document_id,
            "UPLOAD",
            "Document uploaded"
        )

    except Exception:
        file_path.unlink(missing_ok=True)
        raise

    return redirect(url_for("dashboard"))


@app.route("/download/<int:document_id>")
@login_required
def download_document(document_id):
    with get_db() as db:
        document = db.execute(
            """
            SELECT id, original_name, stored_name
            FROM documents
            WHERE id = ? AND owner_id = ?
            """,
            (document_id, session["user_id"])
        ).fetchone()

    # Do not allow access to another user's document.
    if document is None:
        abort(404)

    file_path = UPLOAD_FOLDER / document["stored_name"]

    if not file_path.is_file():
        abort(404)

    add_audit_log(
        session["user_id"],
        document["id"],
        "DOWNLOAD",
        "Document downloaded"
    )

    return send_from_directory(
        str(UPLOAD_FOLDER),
        document["stored_name"],
        as_attachment=True,
        download_name=document["original_name"]
    )

@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        documents = db.execute(
            """
            SELECT id, original_name, created_at
            FROM documents
            WHERE owner_id = ?
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

    content = """
        <h2>Welcome, {{ username }}!</h2>
        <h3>Upload a document</h3>

        <form method="post" action="/upload" enctype="multipart/form-data">
            <input type="hidden" name="csrf_token" value="{{ token }}">
            <label>Select a PDF, TXT, PNG or JPG file (maximum 5 MB)</label>
            <input type="file" name="document"
                   accept=".pdf,.txt,.png,.jpg,.jpeg" required>
            <button type="submit">Upload document</button>
        </form>

        <h3>Your documents</h3>
        {% if documents %}
            <ul>
            {% for doc in documents %}
                
<li>
    {{ doc["original_name"] }} — {{ doc["created_at"] }}
    <a href="{{ url_for('download_document', document_id=doc['id']) }}">
        Download
    </a>
</li>

            {% endfor %}
            </ul>
        {% else %}
            <p class="message">No documents uploaded yet.</p>
        {% endif %}

        <form method="post" action="/logout">
            <input type="hidden" name="csrf_token" value="{{ token }}">
            <button type="submit">Log out</button>
        </form>
    """

    return page(
        render_template_string(
            content,
            username=session["username"],
            token=csrf_token(),
            documents=documents
        )
    )


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("home"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
