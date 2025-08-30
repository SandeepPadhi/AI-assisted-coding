"""
User manager for orchestrating user-related business rules.
"""
from typing import List, Optional
from entities.user import User
from repositories.base_repository import BaseRepository
from errors import EntityNotFoundError, UserError, BusinessRuleViolationError


class UserManager:
    def __init__(self, user_repository: BaseRepository[User]):
        self.user_repository = user_repository
    
    def create_user(self, id: str, name: str, email: str, phone: str) -> User:
        """Create a new user with validation."""
        try:
            user = User(id=id, name=name, email=email, phone=phone)
            return self.user_repository.save(user)
        except Exception as e:
            raise UserError(f"Failed to create user: {str(e)}")
    
    def get_user(self, user_id: str) -> User:
        """Get user by ID, raising exception if not found."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise EntityNotFoundError(f"User not found with ID: {user_id}")
        return user
    
    def get_user_optional(self, user_id: str) -> Optional[User]:
        """Get user by ID, returning None if not found."""
        return self.user_repository.get_by_id(user_id)
    
    def list_all_users(self) -> List[User]:
        """Get all users."""
        return self.user_repository.list_all()
    
    def deactivate_user(self, user_id: str) -> None:
        """Deactivate a user account."""
        user = self.get_user(user_id)
        user.deactivate()
        self.user_repository.save(user)
    
    def activate_user(self, user_id: str) -> None:
        """Activate a user account."""
        user = self.get_user(user_id)
        user.activate()
        self.user_repository.save(user)
    
    def validate_user_can_order(self, user_id: str) -> None:
        """Validate that a user can place an order."""
        user = self.get_user(user_id)
        if not user.can_place_order():
            raise BusinessRuleViolationError(f"User {user_id} is not active and cannot place orders")
