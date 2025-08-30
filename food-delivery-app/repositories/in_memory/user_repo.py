"""
In-memory user repository implementation.
"""
from typing import List, Optional
from entities.user import User
from repositories.base_repository import BaseRepository


class InMemoryUserRepository(BaseRepository[User]):
    def __init__(self):
        self._users: dict[str, User] = {}
    
    def save(self, user: User) -> User:
        self._users[user.id] = user
        return user
    
    def get_by_id(self, id: str) -> Optional[User]:
        return self._users.get(id)
    
    def list_all(self) -> List[User]:
        return list(self._users.values())
    
    def delete(self, id: str) -> bool:
        if id in self._users:
            del self._users[id]
            return True
        return False
