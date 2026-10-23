
import io
import pytest
import app as trustvault
from werkzeug.security import check_password_hash


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Keep tests separate from your real database and uploads.
    test_db = tmp_path / "test_trustvault.db"
    test_uploads = tmp_path / "test_uploads"
    test_uploads.mkdir()

    monkeypatch.setattr(trustvault, "DATABASE", str(test_db))
    monkeypatch.setattr(trustvault, "UPLOAD_FOLDER", test_uploads)

    trustvault.app.config.update(
        TESTING=True,
        SECRET_KEY="test-only-secret-key",
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )
    trustvault.init_db()

    with trustvault.app.test_client() as test_client:
        yield test_client


def get_csrf(client, url):
    response = client.get(url)
    assert response.status_code == 200
    with client.session_transaction() as session:
        return session["csrf_token"]


def register(client, username, password="StrongTest123!"):
    token = get_csrf(client, "/register")
    return client.post(
        "/register",
        data={
            "username": username,
            "password": password,
            "csrf_token": token,
        },
        follow_redirects=True,
    )


def login(client, username, password="StrongTest123!"):
    token = get_csrf(client, "/login")
    return client.post(
        "/login",
        data={
            "username": username,
            "password": password,
            "csrf_token": token,
        },
        follow_redirects=True,
    )


def test_login_page_loads(client):
    assert client.get("/login").status_code == 200


def test_dashboard_requires_login(client):
    response = client.get("/dashboard")
    assert response.status_code == 302


def test_registration_stores_password_hash(client):
    register(client, "alice")

    with trustvault.get_db() as db:
        user = db.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            ("alice",),
        ).fetchone()

    assert user is not None
    assert user["password_hash"] != "StrongTest123!"
    assert check_password_hash(
        user["password_hash"], "StrongTest123!"
    )


def test_invalid_csrf_token_is_rejected(client):
    response = client.post(
        "/register",
        data={
            "username": "badcsrf",
            "password": "StrongTest123!",
            "csrf_token": "wrong-token",
        },
    )
    assert response.status_code == 400


def test_wrong_password_is_rejected(client):
    register(client, "alice")
    response = login(client, "alice", "WrongPassword123!")
    assert b"Invalid username or password" in response.data


def test_user_cannot_download_another_users_document(client):
    # Register and log in as Alice.
    register(client, "alice")
    login(client, "alice")

    # Upload Alice's document.
    token = get_csrf(client, "/dashboard")
    upload_response = client.post(
        "/upload",
        data={
            "csrf_token": token,
            "document": (io.BytesIO(b"private Alice document"), "alice.txt"),
        },
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 302

    # Find Alice's document ID in the isolated test database.
    with trustvault.get_db() as db:
        document = db.execute(
            "SELECT id FROM documents WHERE original_name = ?",
            ("alice.txt",),
        ).fetchone()

    assert document is not None
    document_id = document["id"]

    # Log out, then register and log in as Bob.
    client.get("/logout")
    register(client, "bob")
    login(client, "bob")

    # Bob must not be able to download Alice's document.
    response = client.get(f"/download/{document_id}")
    assert response.status_code == 404
