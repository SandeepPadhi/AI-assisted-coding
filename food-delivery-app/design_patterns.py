"""
Design patterns for the food delivery app.
"""
from abc import ABC, abstractmethod
from typing import Dict, Type
from repositories.base_repository import BaseRepository
from repositories.in_memory.user_repo import InMemoryUserRepository
from repositories.in_memory.restaurant_repo import InMemoryRestaurantRepository
from repositories.in_memory.dish_repo import InMemoryDishRepository
from repositories.in_memory.cart_repo import InMemoryCartRepository
from repositories.in_memory.order_repo import InMemoryOrderRepository
from repositories.in_memory.payment_repo import InMemoryPaymentRepository
from entities.user import User
from entities.restaurant import Restaurant
from entities.dish import Dish
from entities.cart import Cart
from entities.order import Order
from entities.payment import Payment


class RepositoryFactory:
    """Factory pattern for creating repository instances."""
    
    _repositories: Dict[Type, Type[BaseRepository]] = {
        User: InMemoryUserRepository,
        Restaurant: InMemoryRestaurantRepository,
        Dish: InMemoryDishRepository,
        Cart: InMemoryCartRepository,
        Order: InMemoryOrderRepository,
        Payment: InMemoryPaymentRepository,
    }
    
    @classmethod
    def create_repository(cls, entity_type: Type) -> BaseRepository:
        """Create a repository instance for the given entity type."""
        if entity_type not in cls._repositories:
            raise ValueError(f"No repository found for entity type: {entity_type}")
        
        return cls._repositories[entity_type]()
    
    @classmethod
    def register_repository(cls, entity_type: Type, repository_class: Type[BaseRepository]) -> None:
        """Register a new repository class for an entity type."""
        cls._repositories[entity_type] = repository_class


class PaymentStrategy(ABC):
    """Strategy pattern for different payment processing strategies."""
    
    @abstractmethod
    def process_payment(self, amount: float, user_id: str, order_id: str) -> tuple[bool, str, str]:
        """Process payment using this strategy."""
        pass
    
    @abstractmethod
    def get_processing_fee(self, amount: float) -> float:
        """Get processing fee for this payment method."""
        pass


class CreditCardStrategy(PaymentStrategy):
    """Credit card payment strategy."""
    
    def process_payment(self, amount: float, user_id: str, order_id: str) -> tuple[bool, str, str]:
        """Process credit card payment."""
        # Simulate credit card processing
        import random
        success = random.random() > 0.05  # 95% success rate
        transaction_id = f"cc_txn_{order_id}_{random.randint(1000, 9999)}"
        message = "Credit card payment processed successfully" if success else "Credit card payment failed"
        return success, transaction_id, message
    
    def get_processing_fee(self, amount: float) -> float:
        """Credit card processing fee: 2.5% + $0.30."""
        return amount * 0.025 + 0.30


class DigitalWalletStrategy(PaymentStrategy):
    """Digital wallet payment strategy."""
    
    def process_payment(self, amount: float, user_id: str, order_id: str) -> tuple[bool, str, str]:
        """Process digital wallet payment."""
        # Simulate digital wallet processing
        import random
        success = random.random() > 0.02  # 98% success rate
        transaction_id = f"dw_txn_{order_id}_{random.randint(1000, 9999)}"
        message = "Digital wallet payment processed successfully" if success else "Digital wallet payment failed"
        return success, transaction_id, message
    
    def get_processing_fee(self, amount: float) -> float:
        """Digital wallet processing fee: 1.5%."""
        return amount * 0.015


class CashOnDeliveryStrategy(PaymentStrategy):
    """Cash on delivery payment strategy."""
    
    def process_payment(self, amount: float, user_id: str, order_id: str) -> tuple[bool, str, str]:
        """Process cash on delivery payment."""
        # Cash on delivery is always successful (payment happens at delivery)
        transaction_id = f"cod_txn_{order_id}_0000"
        message = "Cash on delivery payment scheduled"
        return True, transaction_id, message
    
    def get_processing_fee(self, amount: float) -> float:
        """Cash on delivery processing fee: $2.00."""
        return 2.00


class PaymentStrategyFactory:
    """Factory for creating payment strategies."""
    
    _strategies = {
        "credit_card": CreditCardStrategy,
        "digital_wallet": DigitalWalletStrategy,
        "cash_on_delivery": CashOnDeliveryStrategy,
    }
    
    @classmethod
    def create_strategy(cls, payment_method: str) -> PaymentStrategy:
        """Create a payment strategy for the given method."""
        if payment_method not in cls._strategies:
            raise ValueError(f"Unknown payment method: {payment_method}")
        
        return cls._strategies[payment_method]()
    
    @classmethod
    def register_strategy(cls, method: str, strategy_class: Type[PaymentStrategy]) -> None:
        """Register a new payment strategy."""
        cls._strategies[method] = strategy_class
