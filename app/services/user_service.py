from typing import Dict, Optional
from uuid import UUID
from app.models.user import User

class UserService:
    """Service for managing users - handles user CRUD operations"""
    
    def __init__(self):
        self.users_db: Dict[UUID, User] = {}
    
    def create_user(self) -> User:
        """
        Create a new user with auto-generated UUID
        
        Returns:
            User: Newly created user with unique ID
        """
        user = User()
        self.users_db[user.id] = user
        return user
    
    def get_user(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by ID
        
        Args:
            user_id: UUID of the user
            
        Returns:
            User if found, None otherwise
        """
        return self.users_db.get(user_id)

# Global instance
user_service = UserService()