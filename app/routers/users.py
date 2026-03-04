from fastapi import APIRouter, HTTPException, status
from uuid import UUID

from app.schemas.users_schemas import UserResponse, QuotaResponse
from app.services.user_service import user_service
from app.services.quota_service import quota_service

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

@router.get(
    "/{user_id}/quota",
    response_model=QuotaResponse,
    summary="Get user quota information",
    description="Returns the current quota usage for a user in the last 60-second window"
)
async def get_user_quota(user_id: UUID) -> QuotaResponse:
    """
    Get current quota information for a user
    
    Args:
        user_id: UUID of the user
        
    Returns:
        QuotaResponse: Current quota statistics
        
    Raises:
        HTTPException: 404 if user not found
    """
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    requests_made = quota_service.get_current_quota(user_id)
    remaining = quota_service.get_remaining_requests(user_id)
    
    return QuotaResponse(
        user_id=user_id,
        requests_made=requests_made,
        max_requests=quota_service.max_requests,
        window_seconds=quota_service.window_seconds,
        remaining_requests=remaining
    )