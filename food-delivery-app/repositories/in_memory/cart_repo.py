"""
In-memory cart repository implementation.
"""
from typing import List, Optional
from entities.cart import Cart
from repositories.base_repository import BaseRepository


class InMemoryCartRepository(BaseRepository[Cart]):
    def __init__(self):
        self._carts: dict[str, Cart] = {}
    
    def save(self, cart: Cart) -> Cart:
        self._carts[cart.id] = cart
        return cart
    
    def get_by_id(self, id: str) -> Optional[Cart]:
        return self._carts.get(id)
    
    def list_all(self) -> List[Cart]:
        return list(self._carts.values())
    
    def delete(self, id: str) -> bool:
        if id in self._carts:
            del self._carts[id]
            return True
        return False
    
    def get_by_user(self, user_id: str) -> Optional[Cart]:
        for cart in self._carts.values():
            if cart.user_id == user_id:
                return cart
        return None
