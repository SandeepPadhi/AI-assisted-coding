"""
Order manager for orchestrating order-related business rules.
"""
from typing import List, Optional
from entities.order import Order, OrderStatus
from entities.cart import Cart
from entities.dish import Dish
from entities.payment import PaymentMethod
from repositories.base_repository import BaseRepository
from repositories.in_memory.order_repo import InMemoryOrderRepository
from errors import EntityNotFoundError, OrderError, BusinessRuleViolationError
from validators import Validators


class OrderManager:
    def __init__(self, order_repository: InMemoryOrderRepository, 
                 cart_repository: BaseRepository[Cart],
                 dish_repository: BaseRepository[Dish],
                 payment_manager=None):
        self.order_repository = order_repository
        self.cart_repository = cart_repository
        self.dish_repository = dish_repository
        self.payment_manager = payment_manager
    
    def place_order(self, order_id: str, user_id: str, delivery_address: str, 
                   payment_method: PaymentMethod = None) -> Order:
        """Place an order with comprehensive validation."""
        try:
            # Validate inputs
            Validators.validate_id_format(order_id, "Order")
            Validators.validate_id_format(user_id, "User")
            Validators.validate_address(delivery_address)
            
            # Get user's cart
            cart = self.cart_repository.get_by_user(user_id)
            if not cart:
                raise BusinessRuleViolationError(f"No cart found for user: {user_id}")
            
            if not cart.items:
                raise BusinessRuleViolationError(f"Cart is empty for user: {user_id}")
            
            # Create order
            order = Order(id=order_id, user_id=user_id, 
                         restaurant_id=cart.restaurant_id, 
                         delivery_address=delivery_address)
            
            # Add items from cart to order
            for cart_item in cart.items:
                dish = self.dish_repository.get_by_id(cart_item.dish_id)
                if not dish:
                    raise EntityNotFoundError(f"Dish not found: {cart_item.dish_id}")
                
                if not dish.is_available:
                    raise BusinessRuleViolationError(f"Dish {cart_item.dish_id} is not available")
                
                order.add_item(cart_item.dish_id, cart_item.quantity, dish.price)
            
            if not order.items:
                raise BusinessRuleViolationError("No valid items found in cart for order")
            
            # Save order
            self.order_repository.save(order)
            
            # Process payment if payment manager is available and payment method provided
            if self.payment_manager and payment_method:
                payment_id = f"payment_{order_id}"
                success, message = self.payment_manager.process_payment_for_order(
                    payment_id, order_id, order.total_amount, payment_method, user_id
                )
                if not success:
                    # Update order status to indicate payment failure
                    order.update_status(OrderStatus.CANCELLED)
                    self.order_repository.save(order)
                    raise OrderError(f"Payment failed for order {order_id}: {message}")
            
            return order
            
        except Exception as e:
            if isinstance(e, (EntityNotFoundError, BusinessRuleViolationError, OrderError)):
                raise
            raise OrderError(f"Failed to place order: {str(e)}")
    
    def get_order(self, order_id: str) -> Order:
        """Get order by ID, raising exception if not found."""
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise EntityNotFoundError(f"Order not found with ID: {order_id}")
        return order
    
    def get_order_optional(self, order_id: str) -> Optional[Order]:
        """Get order by ID, returning None if not found."""
        return self.order_repository.get_by_id(order_id)
    
    def get_user_orders(self, user_id: str) -> List[Order]:
        """Get all orders for a user."""
        return self.order_repository.get_by_user(user_id)
    
    def update_order_status(self, order_id: str, status: OrderStatus) -> None:
        """Update order status with validation."""
        order = self.get_order(order_id)
        
        # Validate status transition
        if order.status == OrderStatus.DELIVERED and status != OrderStatus.DELIVERED:
            raise BusinessRuleViolationError("Cannot change status of delivered order")
        
        if order.status == OrderStatus.CANCELLED and status != OrderStatus.CANCELLED:
            raise BusinessRuleViolationError("Cannot change status of cancelled order")
        
        order.update_status(status)
        self.order_repository.save(order)
