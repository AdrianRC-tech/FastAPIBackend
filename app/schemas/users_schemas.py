from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class UserResponse(BaseModel):
    """DTO: Response when creating a user - returns generated UUID"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "123e4567-e89b-12d3-a456-426614174000"
        }
    })
    
    id: UUID = Field(description="Generated user ID")

class QuotaResponse(BaseModel):
    """DTO: Response for quota check endpoint"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
            "requests_made": 7,
            "max_requests": 10,
            "window_seconds": 60,
            "remaining_requests": 3
        }
    })

    user_id: UUID = Field(description="User ID")
    requests_made: int = Field(description="Requests made in current 60-second window")
    max_requests: int = Field(default=10, description="Maximum allowed requests per window")
    window_seconds: int = Field(default=60, description="Time window in seconds")
    remaining_requests: int = Field(description="Remaining requests in current window")