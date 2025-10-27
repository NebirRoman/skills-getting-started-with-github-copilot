import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities dict after each test to keep tests isolated."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original))


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    # basic sanity checks
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_duplicate():
    email = "testuser@example.com"
    activity = "Chess Club"

    # Ensure test email is not already registered
    assert email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Verify participant present in GET /activities
    resp2 = client.get("/activities")
    assert resp2.status_code == 200
    assert email in resp2.json()[activity]["participants"]

    # Duplicate signup should fail with 400
    resp_dup = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp_dup.status_code == 400


def test_remove_participant():
    activity = "Chess Club"
    email = "remove_me@example.com"

    # Add participant directly to ensure they exist
    if email not in activities[activity]["participants"]:
        activities[activity]["participants"].append(email)

    # Remove via API
    resp = client.delete(f"/activities/{activity}/participants?email={email}")
    assert resp.status_code == 200
    assert email not in activities[activity]["participants"]

    # Removing a non-existent participant should return 404
    resp2 = client.delete(f"/activities/{activity}/participants?email=notfound@example.com")
    assert resp2.status_code == 404
