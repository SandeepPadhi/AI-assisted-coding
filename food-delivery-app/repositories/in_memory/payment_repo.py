"""
In-memory payment repository implementation.
"""
from typing import List, Optional
from entities.payment import Payment
from repositories.base_repository import BaseRepository


class InMemoryPaymentRepository(BaseRepository[Payment]):
    def __init__(self):
        self._payments: dict[str, Payment] = {}
    
    def save(self, payment: Payment) -> Payment:
        self._payments[payment.id] = payment
        return payment
    
    def get_by_id(self, id: str) -> Optional[Payment]:
        return self._payments.get(id)
    
    def list_all(self) -> List[Payment]:
        return list(self._payments.values())
    
    def delete(self, id: str) -> bool:
        if id in self._payments:
            del self._payments[id]
            return True
        return False
    
    def get_by_order(self, order_id: str) -> Optional[Payment]:
        for payment in self._payments.values():
            if payment.order_id == order_id:
                return payment
        return None
    
    def get_by_user(self, user_id: str) -> List[Payment]:
        return [payment for payment in self._payments.values() if payment.user_id == user_id]
