"""
Restaurant manager for orchestrating restaurant-related business rules.
"""
from typing import List, Optional
from entities.restaurant import Restaurant
from repositories.base_repository import BaseRepository


class RestaurantManager:
    def __init__(self, restaurant_repository: BaseRepository[Restaurant]):
        self.restaurant_repository = restaurant_repository
    
    def create_restaurant(self, id: str, name: str, cuisine: str, address: str) -> Restaurant:
        restaurant = Restaurant(id=id, name=name, cuisine=cuisine, address=address)
        return self.restaurant_repository.save(restaurant)
    
    def get_restaurant(self, restaurant_id: str) -> Optional[Restaurant]:
        return self.restaurant_repository.get_by_id(restaurant_id)
    
    def list_all_restaurants(self) -> List[Restaurant]:
        return self.restaurant_repository.list_all()
    
    def list_restaurants_by_cuisine(self, cuisine: str) -> List[Restaurant]:
        return [r for r in self.restaurant_repository.list_all() if r.cuisine.lower() == cuisine.lower()]
