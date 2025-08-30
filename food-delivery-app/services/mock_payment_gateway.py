"""
Mock payment gateway implementation for testing and development.
"""
import random
import time
from typing import Optional, Tuple
from services.payment_gateway import PaymentGateway
from entities.payment import PaymentMethod


class MockPaymentGateway(PaymentGateway):
    """Mock implementation of payment gateway for testing."""
    
    def __init__(self, success_rate: float = 0.95):
        # success_rate: probability of successful payment (0.0 to 1.0)
        self.success_rate = success_rate
    
    def process_payment(self, amount: float, payment_method: PaymentMethod, 
                       user_id: str, order_id: str) -> Tuple[bool, Optional[str], str]:
        """Simulate payment processing with configurable success rate."""
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Generate transaction ID
        transaction_id = f"txn_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Simulate payment success/failure based on success rate
        if random.random() < self.success_rate:
            return True, transaction_id, "Payment processed successfully"
        else:
            return False, None, "Payment failed: insufficient funds"
    
    def refund_payment(self, transaction_id: str, amount: float) -> Tuple[bool, str]:
        """Simulate refund processing."""
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Mock refunds are always successful
        return True, "Refund processed successfully"
