"""
Custom exceptions for the food delivery app.
"""


class FoodDeliveryError(Exception):
    """Base exception for all food delivery app errors."""
    pass


class ValidationError(FoodDeliveryError):
    """Raised when input validation fails."""
    pass


class EntityNotFoundError(FoodDeliveryError):
    """Raised when an entity is not found in the repository."""
    pass


class BusinessRuleViolationError(FoodDeliveryError):
    """Raised when a business rule is violated."""
    pass


class PaymentError(FoodDeliveryError):
    """Raised when payment processing fails."""
    pass


class OrderError(FoodDeliveryError):
    """Raised when order operations fail."""
    pass


class CartError(FoodDeliveryError):
    """Raised when cart operations fail."""
    pass


class RestaurantError(FoodDeliveryError):
    """Raised when restaurant operations fail."""
    pass


class UserError(FoodDeliveryError):
    """Raised when user operations fail."""
    pass


class DishError(FoodDeliveryError):
    """Raised when dish operations fail."""
    pass
