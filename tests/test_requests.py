import time


def _create_user(client):
    """Helper to create a user and return its ID."""
    response = client.post("/users/")
    return response.json()["id"]


def test_post_request_success_for_existing_user(client):
    """Test POST /requests/ succeeds for valid user."""
    user_id = _create_user(client)
    
    response = client.post("/requests/", headers={"X-User-ID": user_id})
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["user_id"] == user_id


def test_post_request_increments_quota(client):
    """Test each request increments the quota counter."""
    user_id = _create_user(client)
    
    for i in range(1, 6):
        response = client.post("/requests/", headers={"X-User-ID": user_id})
        assert response.status_code == 200
        
        # Check quota to verify increment
        quota_response = client.get(f"/users/{user_id}/quota")
        quota_data = quota_response.json()
        assert quota_data["requests_made"] == i


def test_post_request_returns_404_for_unknown_user(client):
    """Test POST /request/ returns 404 for non-existent user."""
    unknown_uuid = "123e4567-e89b-12d3-a456-426614174999"
    
    response = client.post("/requests/", headers={"X-User-ID": unknown_uuid})
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_post_request_returns_422_when_header_missing(client):
    """Test POST /request/ returns 422 when X-User-ID header is missing."""
    response = client.post("/requests/")
    
    assert response.status_code == 422


def test_post_request_returns_422_for_invalid_uuid_header(client):
    """Test POST /request/ returns 422 for invalid UUID in header."""
    response = client.post("/requests/", headers={"X-User-ID": "not-a-uuid"})
    
    assert response.status_code == 422


def test_post_request_returns_429_after_quota_exceeded(client):
    """Test POST /request/ returns 429 when quota limit (10) is exceeded."""
    user_id = _create_user(client)
    
    # Make 10 successful requests
    for _ in range(10):
        response = client.post("/requests/", headers={"X-User-ID": user_id})
        assert response.status_code == 200
    
    # 11th request should fail with 429
    blocked_response = client.post("/requests/", headers={"X-User-ID": user_id})
    assert blocked_response.status_code == 429
    assert "Rate limit exceeded" in blocked_response.json()["detail"]
    assert "10/10" in blocked_response.json()["detail"]


def test_post_request_error_message_shows_quota_status(client):
    """Test 429 error message includes current quota details."""
    user_id = _create_user(client)
    
    # Make 10 requests
    for _ in range(10):
        client.post("/requests/", headers={"X-User-ID": user_id})
    
    # Check error message
    response = client.post("/requests/", headers={"X-User-ID": user_id})
    detail = response.json()["detail"]
    
    assert "10" in detail  # Current quota
    assert "10" in detail  # Max quota


def test_quota_resets_after_window_expires(client):
    """Test quota resets after 60-second window expires."""
    from app.services.quota_service import quota_service
    
    # Temporarily set window to 1 second for testing
    original_window = quota_service.window_seconds
    quota_service.window_seconds = 1
    
    try:
        user_id = _create_user(client)
        
        # Make 10 requests (hit limit)
        for _ in range(10):
            response = client.post("/requests/", headers={"X-User-ID": user_id})
            assert response.status_code == 200
        
        # 11th request should fail
        blocked = client.post("/requests/", headers={"X-User-ID": user_id})
        assert blocked.status_code == 429
        
        # Wait for window to expire
        time.sleep(1.1)
        
        # Should be able to make request again
        allowed_again = client.post("/requests/", headers={"X-User-ID": user_id})
        assert allowed_again.status_code == 200
    
    finally:
        # Restore original window
        quota_service.window_seconds = original_window