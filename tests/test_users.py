from uuid import UUID


def test_create_user_returns_201_with_uuid(client):
    """Test POST /users/ creates user and returns UUID."""
    response = client.post("/users/")
    
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    
    # Verify it's a valid UUID
    UUID(data["id"])


def test_create_user_returns_different_uuids(client):
    """Test that each user gets a unique UUID."""
    response1 = client.post("/users/")
    response2 = client.post("/users/")
    
    uuid1 = response1.json()["id"]
    uuid2 = response2.json()["id"]
    
    assert uuid1 != uuid2


def test_get_quota_returns_404_for_unknown_user(client):
    """Test GET /users/{id}/quota returns 404 for non-existent user."""
    unknown_uuid = "123e4567-e89b-12d3-a456-426614174999"
    
    response = client.get(f"/users/{unknown_uuid}/quota")
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_quota_returns_422_for_invalid_uuid(client):
    """Test GET /users/{id}/quota returns 422 for invalid UUID format."""
    response = client.get("/users/not-a-valid-uuid/quota")
    
    assert response.status_code == 422


def test_get_quota_returns_initial_zero_for_new_user(client):
    """Test new user has 0 requests in quota."""
    create_response = client.post("/users/")
    user_id = create_response.json()["id"]
    
    quota_response = client.get(f"/users/{user_id}/quota")
    
    assert quota_response.status_code == 200
    data = quota_response.json()
    assert data["user_id"] == user_id
    assert data["requests_made"] == 0
    assert data["max_requests"] == 10
    assert data["window_seconds"] == 60
    assert data["remaining_requests"] == 10