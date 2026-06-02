"""FastAPI endpoint tests using Arrange-Act-Assert (AAA) pattern."""

import pytest
from fastapi.testclient import TestClient


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html.
        
        Arrange: Create a TestClient instance
        Act: Send GET request to /
        Assert: Verify redirect response with correct location header
        """
        # Arrange
        # (client fixture already provided)

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all available activities.
        
        Arrange: Create a TestClient instance
        Act: Send GET request to /activities
        Assert: Verify response contains expected activities
        """
        # Arrange
        # (client fixture already provided)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_includes_participant_info(self, client):
        """Test that activity details include participant information.
        
        Arrange: Create a TestClient instance
        Act: Send GET request to /activities
        Assert: Verify activity data contains required fields
        """
        # Arrange
        # (client fixture already provided)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success(self, client):
        """Test successful signup for an activity.
        
        Arrange: Prepare email and activity name
        Act: Send POST request to signup endpoint
        Assert: Verify response indicates successful signup
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_adds_participant_to_activity(self, client):
        """Test that signup actually adds the participant to the activity.
        
        Arrange: Prepare email and activity name
        Act: Send signup request, then fetch activities
        Assert: Verify participant appears in activity list
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity_name = "Programming Class"

        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        response = client.get("/activities")

        # Assert
        data = response.json()
        activity = data[activity_name]
        assert email in activity["participants"]

    def test_signup_duplicate_email_fails(self, client):
        """Test that duplicate signup for same activity is rejected.
        
        Arrange: Use existing participant email
        Act: Send signup request for activity they're already in
        Assert: Verify error response with 400 status
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already" in data["detail"].lower() or "signed up" in data["detail"].lower()

    def test_signup_nonexistent_activity_fails(self, client):
        """Test that signup to nonexistent activity returns 404.
        
        Arrange: Prepare email and nonexistent activity name
        Act: Send signup request to invalid activity
        Assert: Verify 404 error response
        """
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple students can sign up for same activity.
        
        Arrange: Prepare two different emails
        Act: Sign up both students to same activity
        Assert: Verify both appear in participants list
        """
        # Arrange
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        activity_name = "Gym Class"

        # Act
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )
        activities_response = client.get("/activities")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        data = activities_response.json()
        activity = data[activity_name]
        assert email1 in activity["participants"]
        assert email2 in activity["participants"]


class TestRemoveParticipantEndpoint:
    """Tests for DELETE /activities/{activity_name}/participants endpoint."""

    def test_remove_participant_success(self, client):
        """Test successful removal of participant from activity.
        
        Arrange: Use existing participant
        Act: Send DELETE request to remove them
        Assert: Verify success response
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]

    def test_remove_participant_removes_from_list(self, client):
        """Test that removal actually removes participant from activity.
        
        Arrange: Use existing participant
        Act: Remove them, then fetch activities
        Assert: Verify participant no longer in list
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        response = client.get("/activities")

        # Assert
        data = response.json()
        activity = data[activity_name]
        assert email not in activity["participants"]

    def test_remove_nonexistent_participant_fails(self, client):
        """Test that removing nonexistent participant returns error.
        
        Arrange: Use email that's not in activity
        Act: Send DELETE request
        Assert: Verify 404 error response
        """
        # Arrange
        email = "nonexistent@mergington.edu"
        activity_name = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_remove_from_nonexistent_activity_fails(self, client):
        """Test that removing from nonexistent activity returns 404.
        
        Arrange: Prepare email and nonexistent activity name
        Act: Send DELETE request to invalid activity
        Assert: Verify 404 error response
        """
        # Arrange
        email = "student@mergington.edu"
        activity_name = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_remove_and_readd_participant(self, client):
        """Test that removed participant can sign up again.
        
        Arrange: Use existing participant
        Act: Remove them, then sign them up again
        Assert: Verify they appear in participants after re-signup
        """
        # Arrange
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Act
        client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        activities_response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = activities_response.json()
        activity = data[activity_name]
        assert email in activity["participants"]


class TestEndpointIntegration:
    """Integration tests combining multiple endpoints."""

    def test_signup_remove_signup_workflow(self, client):
        """Test complete workflow: signup, remove, signup again.
        
        Arrange: Prepare test email and activity
        Act: Execute full workflow (signup -> remove -> signup)
        Assert: Verify final state matches expectation
        """
        # Arrange
        email = "testuser@mergington.edu"
        activity_name = "Programming Class"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Verify in list
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity_name}/participants",
            params={"email": email}
        )
        
        # Act - Verify removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]

        # Act - Sign up again
        signup_again_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act - Verify back in list
        activities = client.get("/activities").json()

        # Assert
        assert signup_response.status_code == 200
        assert remove_response.status_code == 200
        assert signup_again_response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_multiple_activities_independent_state(self, client):
        """Test that signup to one activity doesn't affect others.
        
        Arrange: Prepare test email
        Act: Sign up to one activity, check others unaffected
        Assert: Verify activity lists are independent
        """
        # Arrange
        email = "testuser@mergington.edu"

        # Act
        client.post(
            "/activities/Chess Club/signup",
            params={"email": email}
        )
        activities = client.get("/activities").json()

        # Assert
        assert email in activities["Chess Club"]["participants"]
        assert email not in activities["Programming Class"]["participants"]
        assert email not in activities["Gym Class"]["participants"]
