import pytest


class TestGetActivities:
    """Test the GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        """Test that we get all activities with their details"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert len(activities) == 9
        assert "Basketball" in activities
        assert "Tennis" in activities
        assert "Art Club" in activities

    def test_get_activities_contains_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_basketball_has_participants(self, client):
        """Test that Basketball activity has initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "james@mergington.edu" in activities["Basketball"]["participants"]


class TestSignup:
    """Test the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]

    def test_signup_updates_participant_list(self, client):
        """Test that signup actually adds participant to list"""
        # Signup first
        client.post("/activities/Tennis/signup?email=newsignup@mergington.edu")
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert "newsignup@mergington.edu" in activities["Tennis"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_already_registered(self, client):
        """Test that a student cannot sign up twice for the same activity"""
        # Try to signup with an existing participant
        response = client.post(
            "/activities/Basketball/signup?email=james@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_multiple_students_same_activity(self, client):
        """Test that multiple different students can signup for the same activity"""
        client.post("/activities/Art%20Club/signup?email=student1@mergington.edu")
        response = client.post("/activities/Art%20Club/signup?email=student2@mergington.edu")
        
        assert response.status_code == 200
        
        # Verify both are in the list
        response = client.get("/activities")
        activities = response.json()
        assert "student1@mergington.edu" in activities["Art Club"]["participants"]
        assert "student2@mergington.edu" in activities["Art Club"]["participants"]


class TestUnregister:
    """Test the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successful unregistration from an activity"""
        response = client.post(
            "/activities/Basketball/unregister?email=james@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "james@mergington.edu" in data["message"]
        assert "Basketball" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes participant from list"""
        # Unregister first
        client.post("/activities/Tennis/unregister?email=alex@mergington.edu")
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert "alex@mergington.edu" not in activities["Tennis"]["participants"]

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_not_registered(self, client):
        """Test that unregistering a student not in activity fails"""
        response = client.post(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_signup_then_unregister(self, client):
        """Test signup followed by unregister"""
        # Signup
        client.post("/activities/Chess%20Club/signup?email=clockmaker@mergington.edu")
        
        # Verify signup worked
        response = client.get("/activities")
        assert "clockmaker@mergington.edu" in response.json()["Chess Club"]["participants"]
        
        # Unregister
        client.post("/activities/Chess%20Club/unregister?email=clockmaker@mergington.edu")
        
        # Verify removed
        response = client.get("/activities")
        assert "clockmaker@mergington.edu" not in response.json()["Chess Club"]["participants"]


class TestRoot:
    """Test the root endpoint"""

    def test_root_redirects(self, client):
        """Test that root redirects to static HTML"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
