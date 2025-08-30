"""
Dish entity for the food delivery app.
"""
from typing import Optional
from validators import Validators
from errors import ValidationError


class Dish:
    # id: unique identifier for the dish across the system
    # name: display name for the dish interface
    # price: cost in currency units for pricing calculations
    # restaurant_id: links dish to its restaurant
    # description: details about the dish for user information
    # is_available: prevents adding to cart when False
    def __init__(self, id: str, name: str, price: float, restaurant_id: str, description: str = "", is_available: bool = True):
        # Validate inputs
        Validators.validate_id_format(id, "Dish")
        Validators.validate_string_not_empty(name, "Dish name")
        Validators.validate_price(price)
        Validators.validate_id_format(restaurant_id, "Restaurant")
        
        self.id = id
        self.name = name
        self.price = price
        self.restaurant_id = restaurant_id
        self.description = description
        self.is_available = is_available

    def make_available(self) -> None:
        """Make the dish available for ordering."""
        self.is_available = True

    def make_unavailable(self) -> None:
        """Make the dish unavailable for ordering."""
        self.is_available = False

    def update_price(self, new_price: float) -> None:
        """Update the dish price."""
        Validators.validate_price(new_price)
        self.price = new_price

    def __str__(self) -> str:
        return f"Dish(id={self.id}, name='{self.name}', price={self.price}, restaurant_id={self.restaurant_id})"
