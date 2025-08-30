"""
Payment entity for the food delivery app.
"""
from typing import Optional
from enum import Enum


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"
    CASH_ON_DELIVERY = "cash_on_delivery"


class Payment:
    # id: unique identifier for the payment across the system
    # order_id: links payment to its order
    # amount: payment amount in currency units
    # payment_method: type of payment method used
    # status: current state of the payment
    # transaction_id: external payment gateway transaction reference
    # user_id: user making the payment
    def __init__(self, id: str, order_id: str, amount: float, payment_method: PaymentMethod, user_id: str):
        self.id = id
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = PaymentStatus.PENDING
        self.transaction_id: Optional[str] = None
        self.user_id = user_id

    def update_status(self, status: PaymentStatus, transaction_id: Optional[str] = None) -> None:
        self.status = status
        if transaction_id:
            self.transaction_id = transaction_id

    def is_successful(self) -> bool:
        return self.status == PaymentStatus.SUCCESSFUL

    def __str__(self) -> str:
        return f"Payment(id={self.id}, order_id={self.order_id}, amount={self.amount}, status={self.status.value})"
