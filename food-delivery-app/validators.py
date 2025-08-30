"""
Input validation utilities for the food delivery app.
"""
import re
from typing import Optional
from errors import ValidationError


class Validators:
    """Static validation methods for input validation."""
    
    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format."""
        if not email or not isinstance(email, str):
            raise ValidationError("Email is required and must be a string")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError(f"Invalid email format: {email}")
    
    @staticmethod
    def validate_phone(phone: str) -> None:
        """Validate phone number format."""
        if not phone or not isinstance(phone, str):
            raise ValidationError("Phone number is required and must be a string")
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        if len(digits_only) < 10:
            raise ValidationError(f"Phone number must have at least 10 digits: {phone}")
    
    @staticmethod
    def validate_price(price: float) -> None:
        """Validate price is positive and reasonable."""
        if not isinstance(price, (int, float)):
            raise ValidationError("Price must be a number")
        
        if price <= 0:
            raise ValidationError("Price must be greater than zero")
        
        if price > 10000:  # Reasonable upper limit
            raise ValidationError("Price seems unreasonably high")
    
    @staticmethod
    def validate_quantity(quantity: int) -> None:
        """Validate quantity is positive and reasonable."""
        if not isinstance(quantity, int):
            raise ValidationError("Quantity must be an integer")
        
        if quantity <= 0:
            raise ValidationError("Quantity must be greater than zero")
        
        if quantity > 100:  # Reasonable upper limit
            raise ValidationError("Quantity seems unreasonably high")
    
    @staticmethod
    def validate_string_not_empty(value: str, field_name: str) -> None:
        """Validate that a string is not empty."""
        if not value or not isinstance(value, str) or not value.strip():
            raise ValidationError(f"{field_name} is required and cannot be empty")
    
    @staticmethod
    def validate_id_format(id_value: str, entity_name: str) -> None:
        """Validate ID format."""
        if not id_value or not isinstance(id_value, str):
            raise ValidationError(f"{entity_name} ID is required and must be a string")
        
        if not re.match(r'^[a-zA-Z0-9_-]+$', id_value):
            raise ValidationError(f"{entity_name} ID contains invalid characters")
    
    @staticmethod
    def validate_address(address: str) -> None:
        """Validate delivery address."""
        if not address or not isinstance(address, str):
            raise ValidationError("Delivery address is required and must be a string")
        
        if len(address.strip()) < 10:
            raise ValidationError("Delivery address seems too short")
        
        if len(address) > 200:
            raise ValidationError("Delivery address is too long")
