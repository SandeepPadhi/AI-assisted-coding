"""
In-memory dish repository implementation.
"""
from typing import List, Optional
from entities.dish import Dish
from repositories.base_repository import BaseRepository


class InMemoryDishRepository(BaseRepository[Dish]):
    def __init__(self):
        self._dishes: dict[str, Dish] = {}
    
    def save(self, dish: Dish) -> Dish:
        self._dishes[dish.id] = dish
        return dish
    
    def get_by_id(self, id: str) -> Optional[Dish]:
        return self._dishes.get(id)
    
    def list_all(self) -> List[Dish]:
        return list(self._dishes.values())
    
    def delete(self, id: str) -> bool:
        if id in self._dishes:
            del self._dishes[id]
            return True
        return False
    
    def get_by_restaurant(self, restaurant_id: str) -> List[Dish]:
        return [dish for dish in self._dishes.values() if dish.restaurant_id == restaurant_id]
