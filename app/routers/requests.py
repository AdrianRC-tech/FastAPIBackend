from fastapi import APIRouter, HTTPException, status, Header
from uuid import UUID

from app.schemas.requests_schema import RequestResponse
from app.services.user_service import user_service
from app.services.quota_service import quota_service

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post(
    "/",
    response_model=RequestResponse,
    summary="Submit a user request",
    description="Process a request for a user. Limited to 10 requests per 60-second window."
)
async def create_request(x_user_id: UUID = Header(..., description="User ID")) -> RequestResponse:
    """
    Process a user request with rate limiting
    
    Args:
        x_user_id: User ID provided in X-User-ID header
        
    Returns:
        RequestResponse: Success message with current quota
        
    Raises:
        HTTPException: 404 if user not found
        HTTPException: 429 if quota exceeded
    """
    # Verify user exists
    user = user_service.get_user(x_user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {x_user_id} not found"
        )
    
    # Check quota
    if not quota_service.can_make_request(x_user_id):
        current_quota = quota_service.get_current_quota(x_user_id)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Current quota: {current_quota}/{quota_service.max_requests}. "
                   f"Please wait before making another request."
        )
    
    # Record the request
    quota_service.record_request(x_user_id)
    
    return RequestResponse(
        status="success",
        message="Request processed successfully",
        user_id=x_user_id
    )