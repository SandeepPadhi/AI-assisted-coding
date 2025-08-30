"""
Payment gateway interface for external payment processing.
"""
from abc import ABC, abstractmethod
from typing import Optional, Tuple
from entities.payment import Payment, PaymentMethod, PaymentStatus


class PaymentGateway(ABC):
    """Abstract base class for payment gateways."""
    
    @abstractmethod
    def process_payment(self, amount: float, payment_method: PaymentMethod, 
                       user_id: str, order_id: str) -> Tuple[bool, Optional[str], str]:
        """
        Process a payment through the gateway.
        
        Returns:
            Tuple of (success: bool, transaction_id: Optional[str], error_message: str)
        """
        pass
    
    @abstractmethod
    def refund_payment(self, transaction_id: str, amount: float) -> Tuple[bool, str]:
        """
        Process a refund through the gateway.
        
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        pass
