from urllib.parse import quote

from src.app import activities


def test_root_redirects_to_static_index(test_client):
    # Arrange
    expected_url = "/static/index.html"

    # Act
    response = test_client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_url


def test_get_activities_returns_all_activities(test_client):
    # Arrange
    activity_name = "Chess Club"

    # Act
    response = test_client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert activity_name in payload
    assert payload[activity_name]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_adds_participant(test_client):
    # Arrange
    activity_name = "Chess Club"
    new_email = "newstudent@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = test_client.post(path, params={"email": new_email})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity_name}"
    assert new_email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400(test_client):
    # Arrange
    activity_name = "Chess Club"
    duplicate_email = "michael@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = test_client.post(path, params={"email": duplicate_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_activity_not_found_returns_404(test_client):
    # Arrange
    activity_name = "Nonexistent Club"
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = test_client.post(path, params={"email": "someone@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_activity_full_returns_400(test_client):
    # Arrange
    activity_name = "Chess Club"
    activity = activities[activity_name]
    activity["participants"] = [f"student{i}@mergington.edu" for i in range(activity["max_participants"])]
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = test_client.post(path, params={"email": "latecomer@mergington.edu"})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Activity is full"


def test_delete_participant_removes_participant(test_client):
    # Arrange
    activity_name = "Chess Club"
    email_to_remove = "michael@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = test_client.delete(path, params={"email": email_to_remove})

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email_to_remove} from {activity_name}"
    assert email_to_remove not in activities[activity_name]["participants"]


def test_delete_nonexistent_participant_returns_404(test_client):
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing@mergington.edu"
    path = f"/activities/{quote(activity_name)}/signup"

    # Act
    response = test_client.delete(path, params={"email": missing_email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
