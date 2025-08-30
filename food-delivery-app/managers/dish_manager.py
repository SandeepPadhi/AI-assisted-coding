"""
Dish manager for orchestrating dish-related business rules.
"""
from typing import List, Optional
from entities.dish import Dish
from repositories.base_repository import BaseRepository
from repositories.in_memory.dish_repo import InMemoryDishRepository


class DishManager:
    def __init__(self, dish_repository: InMemoryDishRepository):
        self.dish_repository = dish_repository
    
    def create_dish(self, id: str, name: str, price: float, restaurant_id: str, description: str = "") -> Dish:
        dish = Dish(id=id, name=name, price=price, restaurant_id=restaurant_id, description=description)
        return self.dish_repository.save(dish)
    
    def get_dish(self, dish_id: str) -> Optional[Dish]:
        return self.dish_repository.get_by_id(dish_id)
    
    def list_dishes_by_restaurant(self, restaurant_id: str) -> List[Dish]:
        return self.dish_repository.get_by_restaurant(restaurant_id)
    
    def list_all_dishes(self) -> List[Dish]:
        return self.dish_repository.list_all()
    
    def update_dish_availability(self, dish_id: str, is_available: bool) -> bool:
        dish = self.dish_repository.get_by_id(dish_id)
        if dish:
            dish.is_available = is_available
            self.dish_repository.save(dish)
            return True
        return False
