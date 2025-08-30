"""
Cart manager for orchestrating cart-related business rules.
"""
from typing import Optional
from entities.cart import Cart
from entities.dish import Dish
from repositories.base_repository import BaseRepository
from repositories.in_memory.cart_repo import InMemoryCartRepository
from errors import EntityNotFoundError, CartError, BusinessRuleViolationError
from validators import Validators


class CartManager:
    def __init__(self, cart_repository: InMemoryCartRepository, dish_repository: BaseRepository[Dish]):
        self.cart_repository = cart_repository
        self.dish_repository = dish_repository
    
    def create_cart(self, cart_id: str, user_id: str) -> Cart:
        """Create a new cart for a user."""
        try:
            Validators.validate_id_format(cart_id, "Cart")
            Validators.validate_id_format(user_id, "User")
            cart = Cart(id=cart_id, user_id=user_id)
            return self.cart_repository.save(cart)
        except Exception as e:
            raise CartError(f"Failed to create cart: {str(e)}")
    
    def get_user_cart(self, user_id: str) -> Optional[Cart]:
        """Get cart for a user, returning None if not found."""
        return self.cart_repository.get_by_user(user_id)
    
    def get_user_cart_or_create(self, user_id: str) -> Cart:
        """Get cart for a user, creating one if it doesn't exist."""
        cart = self.get_user_cart(user_id)
        if not cart:
            cart = self.create_cart(f"cart_{user_id}", user_id)
        return cart
    
    def add_dish_to_cart(self, user_id: str, dish_id: str, quantity: int = 1) -> None:
        """Add a dish to the user's cart with validation."""
        try:
            Validators.validate_quantity(quantity)
            
            # Get or create cart for user
            cart = self.get_user_cart_or_create(user_id)
            
            # Validate dish exists and is available
            dish = self.dish_repository.get_by_id(dish_id)
            if not dish:
                raise EntityNotFoundError(f"Dish not found with ID: {dish_id}")
            
            if not dish.is_available:
                raise BusinessRuleViolationError(f"Dish {dish_id} is not available")
            
            # Validate restaurant constraint
            if cart.restaurant_id and cart.restaurant_id != dish.restaurant_id:
                raise BusinessRuleViolationError(
                    f"Cannot add dish from restaurant {dish.restaurant_id} to cart with restaurant {cart.restaurant_id}"
                )
            
            # Set restaurant_id if not set
            if not cart.restaurant_id:
                cart.restaurant_id = dish.restaurant_id
            
            cart.add_item(dish_id, quantity)
            self.cart_repository.save(cart)
            
        except Exception as e:
            if isinstance(e, (EntityNotFoundError, BusinessRuleViolationError)):
                raise
            raise CartError(f"Failed to add dish to cart: {str(e)}")
    
    def remove_dish_from_cart(self, user_id: str, dish_id: str) -> None:
        """Remove a dish from the user's cart."""
        cart = self.get_user_cart(user_id)
        if not cart:
            raise EntityNotFoundError(f"No cart found for user: {user_id}")
        
        cart.remove_item(dish_id)
        self.cart_repository.save(cart)
    
    def clear_cart(self, user_id: str) -> None:
        """Clear all items from the user's cart."""
        cart = self.get_user_cart(user_id)
        if not cart:
            raise EntityNotFoundError(f"No cart found for user: {user_id}")
        
        cart.items.clear()
        self.cart_repository.save(cart)
    
    def get_cart_total(self, user_id: str) -> float:
        """Calculate the total cost of items in the cart."""
        cart = self.get_user_cart(user_id)
        if not cart:
            return 0.0
        
        total = 0.0
        for item in cart.items:
            dish = self.dish_repository.get_by_id(item.dish_id)
            if dish:
                total += dish.price * item.quantity
        
        return total
