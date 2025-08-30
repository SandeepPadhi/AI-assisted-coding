"""
Cart entity for the food delivery app.
"""
from typing import Dict, List


class CartItem:
    # dish_id: references the dish being added to cart
    # quantity: number of items of this dish
    def __init__(self, dish_id: str, quantity: int):
        self.dish_id = dish_id
        self.quantity = quantity


class Cart:
    # id: unique identifier for the cart across the system
    # user_id: links cart to its owner
    # items: list of cart items with quantities
    # restaurant_id: ensures all items are from same restaurant
    def __init__(self, id: str, user_id: str, restaurant_id: str = None):
        self.id = id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.items: List[CartItem] = []

    def add_item(self, dish_id: str, quantity: int = 1) -> None:
        # Check if item already exists and update quantity
        for item in self.items:
            if item.dish_id == dish_id:
                item.quantity += quantity
                return
        # Add new item
        self.items.append(CartItem(dish_id, quantity))

    def remove_item(self, dish_id: str) -> None:
        self.items = [item for item in self.items if item.dish_id != dish_id]

    def get_total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def __str__(self) -> str:
        return f"Cart(id={self.id}, user_id={self.user_id}, items_count={len(self.items)})"
