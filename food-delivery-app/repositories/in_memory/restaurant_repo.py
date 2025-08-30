"""
In-memory restaurant repository implementation.
"""
from typing import List, Optional
from entities.restaurant import Restaurant
from repositories.base_repository import BaseRepository


class InMemoryRestaurantRepository(BaseRepository[Restaurant]):
    def __init__(self):
        self._restaurants: dict[str, Restaurant] = {}
    
    def save(self, restaurant: Restaurant) -> Restaurant:
        self._restaurants[restaurant.id] = restaurant
        return restaurant
    
    def get_by_id(self, id: str) -> Optional[Restaurant]:
        return self._restaurants.get(id)
    
    def list_all(self) -> List[Restaurant]:
        return list(self._restaurants.values())
    
    def delete(self, id: str) -> bool:
        if id in self._restaurants:
            del self._restaurants[id]
            return True
        return False
