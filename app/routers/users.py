from fastapi import APIRouter, status

from app.schemas.users_schemas import UserResponse
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
    description="Creates a new user and returns the generated UUID. No input required."
)
async def create_user() -> UserResponse:
    """
    Create a new user with auto-generated UUID
    
    Returns:
        UserResponse: Contains the generated user ID
    """
    user = user_service.create_user()
    return UserResponse(id=user.id)