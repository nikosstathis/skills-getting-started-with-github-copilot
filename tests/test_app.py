"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    # Store original state
    from app import activities
    original = {k: v.copy() for k, v in activities.items()}
    for key in original:
        original[key]["participants"] = original[key]["participants"].copy()
    
    yield
    
    # Restore original state
    for key in activities:
        activities[key]["participants"] = original[key]["participants"].copy()


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_success(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_activities_have_required_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)
    
    def test_activities_have_participants(self, client):
        """Test that activities have participant lists"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have participants
        assert len(activities["Chess Club"]["participants"]) > 0
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        
        # Sign up
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        # Verify
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
    
    def test_signup_activity_not_found(self, client, reset_activities):
        """Test signup for non-existent activity"""
        response = client.post(
            "/activities/Non-Existent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple activities"""
        email = "student@mergington.edu"
        
        # Sign up for Chess Club
        response1 = client.post(
            f"/activities/Chess Club/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Sign up for Programming Class
        response2 = client.post(
            f"/activities/Programming Class/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify both
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_success(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        response = client.delete(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        
        # Unregister
        client.delete(f"/activities/Chess Club/unregister?email={email}")
        
        # Verify
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Chess Club"]["participants"]
    
    def test_unregister_activity_not_found(self, client, reset_activities):
        """Test unregister from non-existent activity"""
        response = client.delete(
            "/activities/Non-Existent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]
    
    def test_unregister_not_registered(self, client, reset_activities):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]


class TestIntegration:
    """Integration tests for signup and unregister workflow"""
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test the full workflow of signing up and then unregistering"""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        # Initial state
        response = client.get("/activities")
        initial_count = len(response.json()[activity]["participants"])
        
        # Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200
        
        # Check signup worked
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count + 1
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        unregister_response = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Check unregister worked
        response = client.get("/activities")
        assert len(response.json()[activity]["participants"]) == initial_count
        assert email not in response.json()[activity]["participants"]
    
    def test_cannot_signup_twice(self, client, reset_activities):
        """Test that a student cannot sign up twice for the same activity"""
        email = "testuser@mergington.edu"
        activity = "Chess Club"
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Second signup - should fail
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        
        # Verify only one entry
        response = client.get("/activities")
        count = response.json()[activity]["participants"].count(email)
        assert count == 1
