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