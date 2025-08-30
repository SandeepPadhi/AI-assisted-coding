"""
Payment manager for orchestrating payment-related business rules.
"""
from typing import Optional, Tuple
from entities.payment import Payment, PaymentMethod, PaymentStatus
from repositories.in_memory.payment_repo import InMemoryPaymentRepository
from services.payment_gateway import PaymentGateway


class PaymentManager:
    def __init__(self, payment_repository: InMemoryPaymentRepository, 
                 payment_gateway: PaymentGateway):
        self.payment_repository = payment_repository
        self.payment_gateway = payment_gateway
    
    def process_payment_for_order(self, payment_id: str, order_id: str, 
                                 amount: float, payment_method: PaymentMethod, 
                                 user_id: str) -> Tuple[bool, str]:
        """Process payment for an order through the payment gateway."""
        
        # Create payment record
        payment = Payment(id=payment_id, order_id=order_id, 
                         amount=amount, payment_method=payment_method, 
                         user_id=user_id)
        
        # Update status to processing
        payment.update_status(PaymentStatus.PROCESSING)
        self.payment_repository.save(payment)
        
        # Process payment through gateway
        success, transaction_id, error_message = self.payment_gateway.process_payment(
            amount, payment_method, user_id, order_id
        )
        
        # Update payment status based on result
        if success:
            payment.update_status(PaymentStatus.SUCCESSFUL, transaction_id)
            self.payment_repository.save(payment)
            return True, "Payment processed successfully"
        else:
            payment.update_status(PaymentStatus.FAILED)
            self.payment_repository.save(payment)
            return False, error_message
    
    def get_payment_by_order(self, order_id: str) -> Optional[Payment]:
        """Get payment information for an order."""
        return self.payment_repository.get_by_order(order_id)
    
    def get_user_payments(self, user_id: str) -> list[Payment]:
        """Get all payments for a user."""
        return self.payment_repository.get_by_user(user_id)
    
    def refund_payment(self, payment_id: str) -> Tuple[bool, str]:
        """Process a refund for a payment."""
        payment = self.payment_repository.get_by_id(payment_id)
        if not payment:
            return False, "Payment not found"
        
        if not payment.is_successful():
            return False, "Cannot refund unsuccessful payment"
        
        if not payment.transaction_id:
            return False, "No transaction ID for refund"
        
        # Process refund through gateway
        success, error_message = self.payment_gateway.refund_payment(
            payment.transaction_id, payment.amount
        )
        
        if success:
            payment.update_status(PaymentStatus.REFUNDED)
            self.payment_repository.save(payment)
            return True, "Refund processed successfully"
        else:
            return False, error_message
