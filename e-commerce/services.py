"""
External services for the e-commerce system.
"""

class PaymentService:
    def process_payment(self, amount: float) -> bool:
        # Mock implementation - always succeeds
        return True
