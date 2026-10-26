from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module


TEST_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["student@example.com"],
    },
    "Art Club": {
        "description": "Explore drawing, painting, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 15,
        "participants": [],
    },
}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(app_module, "activities", deepcopy(TEST_ACTIVITIES))
    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details(client):
    # Arrange
    expected_activities = deepcopy(TEST_ACTIVITIES)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client):
    # Arrange
    email = "new-student@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Signed up new-student@example.com for Chess Club"
    }
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert email in participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post(
        "/activities/Robotics%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }


def test_signup_requires_email(client):
    # Arrange
    activity_path = "/activities/Chess%20Club/signup"

    # Act
    response = client.post(activity_path)

    # Assert
    assert response.status_code == 422


def test_remove_participant_removes_registration(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered student@example.com from Chess Club"
    }
    participants = client.get("/activities").json()["Chess Club"]["participants"]
    assert email not in participants


def test_remove_participant_rejects_unknown_activity(client):
    # Arrange
    email = "student@example.com"

    # Act
    response = client.delete(
        "/activities/Robotics%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_remove_participant_rejects_unregistered_email(client):
    # Arrange
    email = "missing-student@example.com"

    # Act
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }