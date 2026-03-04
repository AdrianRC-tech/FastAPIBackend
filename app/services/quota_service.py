from typing import Dict, List
from datetime import datetime, timedelta
from collections import defaultdict
from uuid import UUID

class QuotaService:
    """
    Service for managing rate limiting using sliding window algorithm
    
    Tracks request timestamps per user and enforces quota limits
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize quota service
        
        Args:
            max_requests: Maximum requests allowed per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Stores list of request timestamps per user
        self.request_log: Dict[UUID, List[datetime]] = defaultdict(list)
    
    def _cleanup_old_requests(self, user_id: UUID) -> None:
        """
        Remove request timestamps older than the window
        
        Args:
            user_id: UUID of the user
        """
        cutoff_time = datetime.now() - timedelta(seconds=self.window_seconds)
        self.request_log[user_id] = [
            timestamp for timestamp in self.request_log[user_id]
            if timestamp > cutoff_time
        ]
    
    def can_make_request(self, user_id: UUID) -> bool:
        """
        Check if user can make a request based on current quota
        
        Args:
            user_id: UUID of the user
            
        Returns:
            True if user is within quota, False otherwise
        """
        self._cleanup_old_requests(user_id)
        return len(self.request_log[user_id]) < self.max_requests
    
    def record_request(self, user_id: UUID) -> None:
        """
        Record a new request timestamp for the user
        
        Args:
            user_id: UUID of the user
        """
        self.request_log[user_id].append(datetime.now())
    
    def get_current_quota(self, user_id: UUID) -> int:
        """
        Get the number of requests made in the current window
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Number of requests in current window
        """
        self._cleanup_old_requests(user_id)
        return len(self.request_log[user_id])
    
    def get_remaining_requests(self, user_id: UUID) -> int:
        """
        Get the number of remaining requests allowed
        
        Args:
            user_id: UUID of the user
            
        Returns:
            Number of remaining requests
        """
        current = self.get_current_quota(user_id)
        return max(0, self.max_requests - current)

# Global instance
quota_service = QuotaService()