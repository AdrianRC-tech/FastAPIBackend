from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class RequestResponse(BaseModel):
    """DTO: Response after successfully processing a request"""
    model_config = ConfigDict(json_schema_extra = {
        "example": {
            "status": "success",
            "message": "Request processed successfully",
            "user_id": "123e4567-e89b-12d3-a456-426614174000",
        }
    })
    status: str = Field(default="success", description="Request status")
    message: str = Field(default="Request processed successfully", description="Status message")
    user_id: UUID = Field(description="User ID that made the request")