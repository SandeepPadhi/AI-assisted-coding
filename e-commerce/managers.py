"""
Entity managers for the e-commerce system.
"""
from typing import List, Optional
from uuid import UUID, uuid4

from entities import Product, Cart
from repositories import AbstractProductRepository, AbstractCartRepository

class ProductManager:
    def __init__(self, product_repository: AbstractProductRepository):
        self.product_repository = product_repository
    
    def create_product(self, name: str, description: str, price: float, stock: int) -> Product:
        product = Product(id=uuid4(), name=name, description=description, price=price, stock=stock)
        self.product_repository.save_product(product)
        return product
    
    def get_product(self, id: UUID) -> Optional[Product]:
        return self.product_repository.find_product_by_id(id)
    
    def update_stock(self, id: UUID, quantity: int) -> None:
        product = self.get_product(id)
        if not product:
            raise ValueError("Product not found")
        if product.stock + quantity < 0:
            raise ValueError("Insufficient stock")
        product.stock += quantity
        self.product_repository.update_product_details(product)
    
    def get_all_products(self) -> List[Product]:
        return self.product_repository.list_all_available_products()
    
    def get_low_stock_products(self, threshold: int = 5) -> List[Product]:
        return self.product_repository.find_products_with_low_stock(threshold)

class CartManager:
    def __init__(self, cart_repository: AbstractCartRepository, product_manager: ProductManager):
        self.cart_repository = cart_repository
        self.product_manager = product_manager
    
    def create_cart(self, user_id: UUID) -> Cart:
        cart = Cart(id=uuid4(), user_id=user_id, items=[])
        self.cart_repository.create_new_cart(cart)
        return cart
    
    def add_to_cart(self, cart_id: UUID, product_id: UUID, quantity: int) -> None:
        cart = self.cart_repository.find_cart_by_id(cart_id)
        if not cart:
            raise ValueError("Cart not found")
        
        product = self.product_manager.get_product(product_id)
        if not product:
            raise ValueError("Product not found")
        
        if product.stock < quantity:
            raise ValueError("Insufficient stock")
        
        cart.add_item(product_id, quantity)
        self.cart_repository.update_cart_items(cart)
    
    def remove_from_cart(self, cart_id: UUID, product_id: UUID) -> None:
        cart = self.cart_repository.find_cart_by_id(cart_id)
        if not cart:
            raise ValueError("Cart not found")
        
        cart.remove_item(product_id)
        self.cart_repository.update_cart_items(cart)
    
    def get_cart_total(self, cart_id: UUID) -> float:
        cart = self.cart_repository.find_cart_by_id(cart_id)
        if not cart:
            raise ValueError("Cart not found")
        
        total = 0.0
        for item in cart.items:
            product = self.product_manager.get_product(item.product_id)
            if not product:
                raise ValueError(f"Product {item.product_id} not found")
            total += product.price * item.quantity
        
        return total