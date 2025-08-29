"""
Main execution file for the e-commerce system.
"""
from datetime import datetime
from uuid import uuid4

from entities import Order, OrderStatus, Payment, PaymentStatus, User
from repositories import (InMemoryCartRepository, InMemoryOrderRepository, 
                        InMemoryPaymentRepository, InMemoryProductRepository, 
                        InMemoryUserRepository)
from managers import CartManager, ProductManager
from services import PaymentService

class ECommerceSystem:
    def __init__(self):
        # Initialize repositories
        self.product_repository = InMemoryProductRepository()
        self.user_repository = InMemoryUserRepository()
        self.cart_repository = InMemoryCartRepository()
        self.order_repository = InMemoryOrderRepository()
        self.payment_repository = InMemoryPaymentRepository()
        
        # Initialize managers
        self.product_manager = ProductManager(self.product_repository)
        self.cart_manager = CartManager(self.cart_repository, self.product_manager)
        
        # Initialize services
        self.payment_service = PaymentService()
    
    def create_user(self, name: str, email: str) -> User:
        if self.user_repository.find_user_by_email(email):
            raise ValueError("User with this email already exists")
        
        user = User(id=uuid4(), name=name, email=email)
        self.user_repository.register_new_user(user)
        return user
    
    def create_product(self, name: str, description: str, price: float, stock: int):
        return self.product_manager.create_product(name, description, price, stock)
    
    def add_to_cart(self, user_id: uuid4, product_id: uuid4, quantity: int) -> None:
        cart = self.cart_repository.find_active_cart_by_user_id(user_id)
        if not cart:
            cart = self.cart_manager.create_cart(user_id)
        
        self.cart_manager.add_to_cart(cart.id, product_id, quantity)
    
    def checkout(self, user_id: uuid4) -> Order:
        cart = self.cart_repository.find_active_cart_by_user_id(user_id)
        if not cart or not cart.items:
            raise ValueError("Cart is empty")
        
        total_amount = self.cart_manager.get_cart_total(cart.id)
        
        # Process payment
        if not self.payment_service.process_payment(total_amount):
            raise ValueError("Payment failed")
        
        # Create order
        order = Order(
            id=uuid4(),
            user_id=user_id,
            items=cart.items.copy(),
            total_amount=total_amount,
            status=OrderStatus.PAID,
            created_at=datetime.now()
        )
        self.order_repository.create_new_order(order)
        
        # Create payment record
        payment = Payment(
            id=uuid4(),
            order_id=order.id,
            amount=total_amount,
            status=PaymentStatus.SUCCESS,
            timestamp=datetime.now()
        )
        self.payment_repository.record_payment(payment)
        
        # Update product stock
        for item in cart.items:
            self.product_manager.update_stock(item.product_id, -item.quantity)
        
        # Clear cart
        cart.clear()
        self.cart_repository.update_cart_items(cart)
        
        return order
    
    def get_order_history(self, user_id: uuid4):
        return self.order_repository.find_user_order_history(user_id)

def main():
    # Initialize system
    system = ECommerceSystem()
    
    # Create a user
    user = system.create_user("John Doe", "john@example.com")
    print(f"Created user: {user}")
    
    # Create some products
    laptop = system.create_product("Laptop", "High-performance laptop", 999.99, 10)
    phone = system.create_product("Phone", "Smartphone", 499.99, 20)
    print(f"Created products: {laptop}, {phone}")
    
    # Add products to cart
    system.add_to_cart(user.id, laptop.id, 1)
    system.add_to_cart(user.id, phone.id, 2)
    print("Added products to cart")
    
    # Checkout
    order = system.checkout(user.id)
    print(f"Created order: {order}")
    
    # Get order history
    orders = system.get_order_history(user.id)
    print(f"Order history: {orders}")

if __name__ == "__main__":
    main()