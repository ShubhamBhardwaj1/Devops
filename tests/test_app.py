from pathlib import Path

import pytest

from app.app import create_app


@pytest.fixture()
def app(tmp_path: Path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "test.db"),
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_homepage_renders_dashboard(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SecureGuard" in response.data


def test_registration_and_login(client):
    registered = client.post(
        "/register",
        json={"username": "alice", "password": "password123", "email": "alice@example.test"},
    )
    logged_in = client.post("/login", json={"username": "alice", "password": "password123"})
    assert registered.status_code == 201
    assert logged_in.status_code == 200


def test_unknown_profile_is_not_found(client):
    response = client.get("/profile/no-such-user")
    assert response.status_code == 404
