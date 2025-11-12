import pytest


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_success(self, client):
        """Test successfully fetching all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self, client):
        """Test that activities contain required fields"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity

    def test_get_activities_participants_list(self, client):
        """Test that participants are returned as a list"""
        response = client.get("/activities")
        data = response.json()
        
        assert isinstance(data["Chess Club"]["participants"], list)
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client):
        """Test successfully signing up for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the list"""
        # Signup
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        # Verify
        response = client.get("/activities")
        activities = response.json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_nonexistent_activity(self, client):
        """Test signup for a non-existent activity"""
        response = client.post(
            "/activities/NonExistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_signup_already_registered(self, client):
        """Test signup when student is already registered"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_multiple_students(self, client):
        """Test that multiple students can sign up for the same activity"""
        client.post("/activities/Chess%20Club/signup?email=student1@mergington.edu")
        client.post("/activities/Chess%20Club/signup?email=student2@mergington.edu")
        
        response = client.get("/activities")
        activities = response.json()
        assert len(activities["Chess Club"]["participants"]) == 4

    def test_signup_different_activities(self, client):
        """Test that a student can signup for different activities"""
        student_email = "student@mergington.edu"
        
        client.post(f"/activities/Chess%20Club/signup?email={student_email}")
        client.post(f"/activities/Gym%20Class/signup?email={student_email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert student_email in activities["Chess Club"]["participants"]
        assert student_email in activities["Gym Class"]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client):
        """Test successfully unregistering from an activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]

    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant"""
        # Unregister
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify
        response = client.get("/activities")
        activities = response.json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
        assert len(activities["Chess Club"]["participants"]) == 1

    def test_unregister_nonexistent_activity(self, client):
        """Test unregister from a non-existent activity"""
        response = client.delete(
            "/activities/NonExistent%20Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]

    def test_unregister_not_registered(self, client):
        """Test unregister when student is not registered"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"]

    def test_unregister_multiple_participants(self, client):
        """Test unregistering one participant doesn't affect others"""
        # Unregister one
        client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        
        # Verify other is still there
        response = client.get("/activities")
        activities = response.json()
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_after_signup(self, client):
        """Test unregistering a newly signed up student"""
        # Signup
        client.post("/activities/Chess%20Club/signup?email=newstudent@mergington.edu")
        
        # Unregister
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        # Verify
        response = client.get("/activities")
        activities = response.json()
        assert "newstudent@mergington.edu" not in activities["Chess Club"]["participants"]
