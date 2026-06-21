import io
import uuid

import pytest
from fastapi.testclient import TestClient

from main import app
from app.database import SessionLocal
from app.models import User

client = TestClient(app)


def _signup_and_verify():
    """Helper: run a full signup + magic-link verify, return the new user id."""
    email = f"qa_{uuid.uuid4().hex[:8]}@example.com"

    # Signup -> magic link issued
    r = client.post("/auth/signup", json={"email": email})
    assert r.status_code == 200
    assert r.json()["email"] == email

    # Pull the issued token straight from the DB (email send is stubbed in dev)
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        assert user is not None
        token = user.magic_link_token
        assert token
    finally:
        db.close()

    # Verify with the right token
    r = client.post("/auth/verify-magic-link", json={"email": email, "token": token})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body

    # Verifying again with the now-cleared token must fail
    r = client.post("/auth/verify-magic-link", json={"email": email, "token": token})
    assert r.status_code == 400

    return body["user"]["id"]


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "healthy"}


def test_auth_signup_and_verify_flow():
    assert _signup_and_verify()


def test_verify_with_bad_token_rejected():
    email = f"qa_{uuid.uuid4().hex[:8]}@example.com"
    client.post("/auth/signup", json={"email": email})
    r = client.post("/auth/verify-magic-link", json={"email": email, "token": "wrong"})
    assert r.status_code == 400


def test_account_get_update_and_subscription():
    user_id = _signup_and_verify()

    # Default subscription is free
    r = client.get(f"/account/{user_id}/subscription")
    assert r.status_code == 200
    assert r.json()["tier"] == "free"

    # Update profile
    r = client.patch(f"/account/{user_id}", json={"profile_name": "QA Bot", "handicap": 12})
    assert r.status_code == 200
    assert r.json()["profile_name"] == "QA Bot"
    assert r.json()["handicap"] == 12

    # Read back
    r = client.get(f"/account/{user_id}")
    assert r.status_code == 200
    assert r.json()["profile_name"] == "QA Bot"


def test_account_missing_user_404():
    r = client.get(f"/account/{uuid.uuid4()}")
    assert r.status_code == 404


def test_drills_list_ok():
    r = client.get("/drills")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_swings_list_ok():
    r = client.get("/swings/user/all")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_swing_status_missing_404():
    r = client.get(f"/swings/{uuid.uuid4()}/status")
    assert r.status_code == 404


def test_swing_upload_unknown_user_404():
    # Unknown user is rejected before any S3/Celery work happens
    files = {"file": ("swing.mp4", io.BytesIO(b"not-a-real-video"), "video/mp4")}
    data = {"user_id": str(uuid.uuid4())}
    r = client.post("/swings/upload", files=files, data=data)
    assert r.status_code == 404
