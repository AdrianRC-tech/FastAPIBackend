from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4

class User(BaseModel):
    """User domain model - internal representation with all attributes"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "id": "123e4567-e89b-12d3-a456-426614174000",
        }
    })
    
    id: UUID = Field(default_factory=uuid4, description="Unique user identifier")

