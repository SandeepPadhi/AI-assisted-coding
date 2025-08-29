"""
Core entities for the e-commerce system.
"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List
from uuid import UUID

# Enums
class OrderStatus(Enum):
    PENDING = "PENDING"
    PAID = "PAID"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

class PaymentStatus(Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

# Base Entities
@dataclass
class Product:
    id: UUID
    name: str
    description: str
    price: float
    stock: int

    def __post_init__(self):
        if self.price < 0:
            raise ValueError("Price cannot be negative")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")

@dataclass
class User:
    id: UUID
    name: str
    email: str
    
    def __post_init__(self):
        if not self.email or '@' not in self.email:
            raise ValueError("Invalid email address")

@dataclass
class CartItem:
    product_id: UUID
    quantity: int
    
    def __post_init__(self):
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

@dataclass
class Cart:
    id: UUID
    user_id: UUID
    items: List[CartItem]
    
    def add_item(self, product_id: UUID, quantity: int) -> None:
        for item in self.items:
            if item.product_id == product_id:
                item.quantity += quantity
                return
        self.items.append(CartItem(product_id, quantity))
    
    def remove_item(self, product_id: UUID) -> None:
        self.items = [item for item in self.items if item.product_id != product_id]
    
    def clear(self) -> None:
        self.items = []

@dataclass
class Payment:
    id: UUID
    order_id: UUID
    amount: float
    status: PaymentStatus
    timestamp: datetime
    
    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive")

@dataclass
class Order:
    id: UUID
    user_id: UUID
    items: List[CartItem]
    total_amount: float
    status: OrderStatus
    created_at: datetime
    
    def __post_init__(self):
        if self.total_amount <= 0:
            raise ValueError("Order amount must be positive")
