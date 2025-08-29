"""
Repository implementations for the e-commerce system.
Each entity has its own abstract repository with specific methods.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from uuid import UUID

from entities import Product, User, Cart, Order, Payment, OrderStatus, PaymentStatus

class AbstractProductRepository(ABC):
    @abstractmethod
    def save_product(self, product: Product) -> None:
        pass
    
    @abstractmethod
    def find_product_by_id(self, product_id: UUID) -> Optional[Product]:
        pass
    
    @abstractmethod
    def update_product_details(self, product: Product) -> None:
        pass
    
    @abstractmethod
    def remove_product(self, product_id: UUID) -> None:
        pass
    
    @abstractmethod
    def list_all_available_products(self) -> List[Product]:
        pass
    
    @abstractmethod
    def find_products_with_low_stock(self, threshold: int) -> List[Product]:
        pass

class AbstractUserRepository(ABC):
    @abstractmethod
    def register_new_user(self, user: User) -> None:
        pass
    
    @abstractmethod
    def find_user_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    def update_user_profile(self, user: User) -> None:
        pass
    
    @abstractmethod
    def deactivate_user(self, user_id: UUID) -> None:
        pass
    
    @abstractmethod
    def find_user_by_email(self, email: str) -> Optional[User]:
        pass

class AbstractCartRepository(ABC):
    @abstractmethod
    def create_new_cart(self, cart: Cart) -> None:
        pass
    
    @abstractmethod
    def find_cart_by_id(self, cart_id: UUID) -> Optional[Cart]:
        pass
    
    @abstractmethod
    def update_cart_items(self, cart: Cart) -> None:
        pass
    
    @abstractmethod
    def delete_abandoned_cart(self, cart_id: UUID) -> None:
        pass
    
    @abstractmethod
    def find_active_cart_by_user_id(self, user_id: UUID) -> Optional[Cart]:
        pass

class AbstractOrderRepository(ABC):
    @abstractmethod
    def create_new_order(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def find_order_by_id(self, order_id: UUID) -> Optional[Order]:
        pass
    
    @abstractmethod
    def update_order_status(self, order: Order) -> None:
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: UUID) -> None:
        pass
    
    @abstractmethod
    def find_user_order_history(self, user_id: UUID) -> List[Order]:
        pass
    
    @abstractmethod
    def find_recent_orders(self, limit: int) -> List[Order]:
        pass

class AbstractPaymentRepository(ABC):
    @abstractmethod
    def record_payment(self, payment: Payment) -> None:
        pass
    
    @abstractmethod
    def find_payment_by_id(self, payment_id: UUID) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def update_payment_status(self, payment: Payment) -> None:
        pass
    
    @abstractmethod
    def void_payment(self, payment_id: UUID) -> None:
        pass
    
    @abstractmethod
    def find_payment_by_order_id(self, order_id: UUID) -> Optional[Payment]:
        pass
    
    @abstractmethod
    def find_successful_payments_by_user(self, user_id: UUID) -> List[Payment]:
        pass

# In-Memory Implementations
class InMemoryProductRepository(AbstractProductRepository):
    def __init__(self):
        self.products: Dict[UUID, Product] = {}
    
    def save_product(self, product: Product) -> None:
        self.products[product.id] = product
    
    def find_product_by_id(self, product_id: UUID) -> Optional[Product]:
        return self.products.get(product_id)
    
    def update_product_details(self, product: Product) -> None:
        self.products[product.id] = product
    
    def remove_product(self, product_id: UUID) -> None:
        self.products.pop(product_id, None)
    
    def list_all_available_products(self) -> List[Product]:
        return [product for product in self.products.values() if product.stock > 0]
    
    def find_products_with_low_stock(self, threshold: int) -> List[Product]:
        return [product for product in self.products.values() if product.stock <= threshold]

class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self):
        self.users: Dict[UUID, User] = {}
    
    def register_new_user(self, user: User) -> None:
        self.users[user.id] = user
    
    def find_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)
    
    def update_user_profile(self, user: User) -> None:
        self.users[user.id] = user
    
    def deactivate_user(self, user_id: UUID) -> None:
        self.users.pop(user_id, None)
    
    def find_user_by_email(self, email: str) -> Optional[User]:
        return next((user for user in self.users.values() if user.email == email), None)

class InMemoryCartRepository(AbstractCartRepository):
    def __init__(self):
        self.carts: Dict[UUID, Cart] = {}
    
    def create_new_cart(self, cart: Cart) -> None:
        self.carts[cart.id] = cart
    
    def find_cart_by_id(self, cart_id: UUID) -> Optional[Cart]:
        return self.carts.get(cart_id)
    
    def update_cart_items(self, cart: Cart) -> None:
        self.carts[cart.id] = cart
    
    def delete_abandoned_cart(self, cart_id: UUID) -> None:
        self.carts.pop(cart_id, None)
    
    def find_active_cart_by_user_id(self, user_id: UUID) -> Optional[Cart]:
        return next((cart for cart in self.carts.values() if cart.user_id == user_id), None)

class InMemoryOrderRepository(AbstractOrderRepository):
    def __init__(self):
        self.orders: Dict[UUID, Order] = {}
    
    def create_new_order(self, order: Order) -> None:
        self.orders[order.id] = order
    
    def find_order_by_id(self, order_id: UUID) -> Optional[Order]:
        return self.orders.get(order_id)
    
    def update_order_status(self, order: Order) -> None:
        self.orders[order.id] = order
    
    def cancel_order(self, order_id: UUID) -> None:
        if order := self.orders.get(order_id):
            order.status = OrderStatus.CANCELLED
            self.orders[order_id] = order
    
    def find_user_order_history(self, user_id: UUID) -> List[Order]:
        return [order for order in self.orders.values() if order.user_id == user_id]
    
    def find_recent_orders(self, limit: int) -> List[Order]:
        return sorted(self.orders.values(), key=lambda x: x.created_at, reverse=True)[:limit]

class InMemoryPaymentRepository(AbstractPaymentRepository):
    def __init__(self):
        self.payments: Dict[UUID, Payment] = {}
    
    def record_payment(self, payment: Payment) -> None:
        self.payments[payment.id] = payment
    
    def find_payment_by_id(self, payment_id: UUID) -> Optional[Payment]:
        return self.payments.get(payment_id)
    
    def update_payment_status(self, payment: Payment) -> None:
        self.payments[payment.id] = payment
    
    def void_payment(self, payment_id: UUID) -> None:
        if payment := self.payments.get(payment_id):
            payment.status = PaymentStatus.FAILED
            self.payments[payment_id] = payment
    
    def find_payment_by_order_id(self, order_id: UUID) -> Optional[Payment]:
        return next((payment for payment in self.payments.values() if payment.order_id == order_id), None)
    
    def find_successful_payments_by_user(self, user_id: UUID) -> List[Payment]:
        return [
            payment for payment in self.payments.values()
            if payment.status == PaymentStatus.SUCCESS and 
            any(order.user_id == user_id for order in self.order_repository.orders.values() if order.id == payment.order_id)
        ]