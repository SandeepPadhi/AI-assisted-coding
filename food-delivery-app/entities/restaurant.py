"""
Restaurant entity for the food delivery app.
"""
from typing import Optional


class Restaurant:
    # id: unique identifier for the restaurant across the system
    # name: display name for the restaurant interface
    # cuisine: type of cuisine for filtering and categorization
    # address: location for delivery coordination
    # is_active: prevents ordering when False
    def __init__(self, id: str, name: str, cuisine: str, address: str, is_active: bool = True):
        self.id = id
        self.name = name
        self.cuisine = cuisine
        self.address = address
        self.is_active = is_active

    def __str__(self) -> str:
        return f"Restaurant(id={self.id}, name='{self.name}', cuisine='{self.cuisine}')"
