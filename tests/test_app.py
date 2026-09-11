from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


BASELINE_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture
def client():
    """Provide a clean TestClient with a reset in-memory activity store."""
    original_activities = deepcopy(app_module.activities)

    app_module.activities.clear()
    app_module.activities.update(deepcopy(BASELINE_ACTIVITIES))

    with TestClient(app_module.app) as test_client:
        yield test_client

    app_module.activities.clear()
    app_module.activities.update(original_activities)


def test_get_activities_returns_all_activities(client):
    # Arrange
    # No special setup is needed because the fixture resets the in-memory data.

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert "Programming Class" in payload
    assert payload["Chess Club"]["participants"] == [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]


def test_signup_adds_student_to_activity(client):
    # Arrange
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in app_module.activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup?email={email}"
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert app_module.activities[activity_name]["participants"].count(email) == 1


def test_unregister_participant_removes_student_from_activity(client):
    # Arrange
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in app_module.activities[activity_name]["participants"]
