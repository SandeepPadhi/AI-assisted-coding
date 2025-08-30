"""
Order entity for the food delivery app.
"""
from typing import List, Dict
from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem:
    # dish_id: references the dish in the order
    # quantity: number of items of this dish
    # price: price per item at time of order
    def __init__(self, dish_id: str, quantity: int, price: float):
        self.dish_id = dish_id
        self.quantity = quantity
        self.price = price


class Order:
    # id: unique identifier for the order across the system
    # user_id: links order to its owner
    # restaurant_id: restaurant fulfilling the order
    # items: list of order items with quantities and prices
    # status: current state of the order
    # total_amount: total cost of the order
    # delivery_address: where to deliver the order
    def __init__(self, id: str, user_id: str, restaurant_id: str, delivery_address: str):
        self.id = id
        self.user_id = user_id
        self.restaurant_id = restaurant_id
        self.delivery_address = delivery_address
        self.items: List[OrderItem] = []
        self.status = OrderStatus.PENDING
        self.total_amount = 0.0

    def add_item(self, dish_id: str, quantity: int, price: float) -> None:
        self.items.append(OrderItem(dish_id, quantity, price))
        self.total_amount += price * quantity

    def update_status(self, status: OrderStatus) -> None:
        self.status = status

    def __str__(self) -> str:
        return f"Order(id={self.id}, user_id={self.user_id}, status={self.status.value}, total={self.total_amount})"
