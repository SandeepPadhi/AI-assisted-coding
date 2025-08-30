"""
In-memory order repository implementation.
"""
from typing import List, Optional
from entities.order import Order
from repositories.base_repository import BaseRepository


class InMemoryOrderRepository(BaseRepository[Order]):
    def __init__(self):
        self._orders: dict[str, Order] = {}
    
    def save(self, order: Order) -> Order:
        self._orders[order.id] = order
        return order
    
    def get_by_id(self, id: str) -> Optional[Order]:
        return self._orders.get(id)
    
    def list_all(self) -> List[Order]:
        return list(self._orders.values())
    
    def delete(self, id: str) -> bool:
        if id in self._orders:
            del self._orders[id]
            return True
        return False
    
    def get_by_user(self, user_id: str) -> List[Order]:
        return [order for order in self._orders.values() if order.user_id == user_id]
