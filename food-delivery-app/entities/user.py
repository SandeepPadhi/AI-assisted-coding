"""
User entity for the food delivery app.
"""
from typing import Optional
from validators import Validators
from errors import ValidationError


class User:
    # id: unique identifier for the user across the system
    # name: display name for the user interface
    # email: contact information and login credential
    # phone: contact information for delivery coordination
    # is_active: prevents ordering when False
    def __init__(self, id: str, name: str, email: str, phone: str, is_active: bool = True):
        # Validate inputs
        Validators.validate_id_format(id, "User")
        Validators.validate_string_not_empty(name, "Name")
        Validators.validate_email(email)
        Validators.validate_phone(phone)
        
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone
        self.is_active = is_active

    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False

    def activate(self) -> None:
        """Activate the user account."""
        self.is_active = True

    def can_place_order(self) -> bool:
        """Check if user can place an order."""
        return self.is_active

    def __str__(self) -> str:
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"
