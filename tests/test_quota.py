def _create_user(client):
    """Helper to create a user and return its ID."""
    response = client.post("/users/")
    return response.json()["id"]


def test_quota_response_has_all_fields(client):
    """Test quota response includes all required fields."""
    user_id = _create_user(client)
    
    # Make 3 requests with the created user
    for _ in range(3):
        client.post("/requests/", headers={"X-User-ID": user_id})
    
    response = client.get(f"/users/{user_id}/quota")
    data = response.json()
    
    assert "user_id" in data
    assert "requests_made" in data
    assert "max_requests" in data
    assert "window_seconds" in data
    assert "remaining_requests" in data


def test_quota_remaining_requests_calculated_correctly(client):
    """Test remaining_requests = max_requests - requests_made."""
    user_id = _create_user(client)
    
    # Make 3 requests
    for _ in range(3):
        client.post("/requests/", headers={"X-User-ID": user_id})
    
    response = client.get(f"/users/{user_id}/quota")
    data = response.json()
    
    expected_remaining = data["max_requests"] - data["requests_made"]
    assert data["remaining_requests"] == expected_remaining
    assert data["remaining_requests"] == 7


def test_quota_counts_only_valid_requests(client):
    """Test that failed requests (404, 429) don't count toward quota."""
    user_id = _create_user(client)
    
    # Try request with unknown user (404)
    unknown_uuid = "123e4567-e89b-12d3-a456-426614174999"
    client.post("/request/", headers={"X-User-ID": unknown_uuid})
    
    # Make valid request
    client.post("/requests/", headers={"X-User-ID": user_id})
    
    # Check quota - should only count the valid one
    response = client.get(f"/users/{user_id}/quota")
    assert response.json()["requests_made"] == 1


def test_multiple_users_have_independent_quotas(client):
    """Test that different users have independent quota counters."""
    user1_id = _create_user(client)
    user2_id = _create_user(client)
    
    # User 1 makes 3 requests
    for _ in range(3):
        client.post("/requests/", headers={"X-User-ID": user1_id})
    
    # User 2 makes 5 requests
    for _ in range(5):
        client.post("/requests/", headers={"X-User-ID": user2_id})
    
    # Check quotas
    quota1 = client.get(f"/users/{user1_id}/quota").json()
    quota2 = client.get(f"/users/{user2_id}/quota").json()
    
    assert quota1["requests_made"] == 3
    assert quota2["requests_made"] == 5
    assert quota1["remaining_requests"] == 7
    assert quota2["remaining_requests"] == 5


def test_quota_window_is_60_seconds(client):
    """Test that the quota window is 60 seconds."""
    user_id = _create_user(client)
    
    response = client.get(f"/users/{user_id}/quota")
    data = response.json()
    
    assert data["window_seconds"] == 60


def test_quota_max_requests_is_10(client):
    """Test that max requests per window is 10."""
    user_id = _create_user(client)
    
    response = client.get(f"/users/{user_id}/quota")
    data = response.json()
    
    assert data["max_requests"] == 10