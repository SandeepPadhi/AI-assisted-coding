"""
Base repository interface for the food delivery app.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')


class BaseRepository(ABC, Generic[T]):
    """Abstract base class for all repositories."""
    
    @abstractmethod
    def save(self, entity: T) -> T:
        """Save an entity to the repository."""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Get an entity by its ID."""
        pass
    
    @abstractmethod
    def list_all(self) -> List[T]:
        """Get all entities from the repository."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete an entity by its ID."""
        pass
