from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def get_activity_participants(activity_name: str):
    response = client.get("/activities")
    response.raise_for_status()
    activities = response.json()
    return activities[activity_name]["participants"]


def test_get_activities_returns_all_activities():
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    activities = response.json()
    assert activity_name in activities
    assert activities[activity_name]["description"]
    assert isinstance(activities[activity_name]["participants"], list)


def test_signup_adds_participant_and_returns_success():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest-newparticipant@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    response = client.post(signup_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in get_activity_participants(activity_name)

    # Cleanup
    client.delete(signup_url)


def test_signup_duplicate_participant_returns_bad_request():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest-duplicate@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    first_signup = client.post(signup_url)
    second_signup = client.post(signup_url)

    # Assert
    assert first_signup.status_code == 200
    assert second_signup.status_code == 400
    assert second_signup.json()["detail"] == "Student already signed up for this activity"

    # Cleanup
    client.delete(signup_url)


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest-remove@mergington.edu"
    signup_url = f"/activities/{quote(activity_name)}/signup?email={quote(email)}"

    # Act
    client.post(signup_url)
    delete_response = client.delete(signup_url)

    # Assert
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in get_activity_participants(activity_name)
