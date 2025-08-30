# Food Delivery App

A robust, production-ready food delivery system following clean architecture principles with comprehensive error handling, validation, and design patterns.

## 🏗️ Architecture Overview

The system follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    System Orchestrator                      │
│                    (orchestrator.py)                        │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Entity Managers                        │
│  (user_manager.py, cart_manager.py, order_manager.py, etc.) │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                      Entities                               │
│  (user.py, restaurant.py, dish.py, cart.py, order.py, etc.) │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Repositories                             │
│  (base_repository.py + in_memory implementations)           │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    External Services                        │
│  (payment_gateway.py + mock implementations)                │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
food-delivery-app/
├─ entities/                    # Core business objects
│  ├─ __init__.py
│  ├─ user.py                  # User entity with validation
│  ├─ restaurant.py            # Restaurant entity
│  ├─ dish.py                  # Dish entity with price validation
│  ├─ cart.py                  # Cart and CartItem entities
│  ├─ order.py                 # Order and OrderItem entities
│  └─ payment.py               # Payment entity with status tracking
├─ managers/                   # Business logic orchestration
│  ├─ __init__.py
│  ├─ user_manager.py          # User operations with validation
│  ├─ restaurant_manager.py    # Restaurant operations
│  ├─ dish_manager.py          # Dish operations
│  ├─ cart_manager.py          # Cart operations with business rules
│  ├─ order_manager.py         # Order operations with payment integration
│  └─ payment_manager.py       # Payment processing
├─ repositories/               # Data access layer
│  ├─ __init__.py
│  ├─ base_repository.py       # Abstract repository interface
│  └─ in_memory/               # In-memory implementations
│     ├─ __init__.py
│     ├─ user_repo.py
│     ├─ restaurant_repo.py
│     ├─ dish_repo.py
│     ├─ cart_repo.py
│     ├─ order_repo.py
│     └─ payment_repo.py
├─ services/                   # External service interfaces
│  ├─ __init__.py
│  ├─ payment_gateway.py       # Abstract payment gateway
│  └─ mock_payment_gateway.py  # Mock implementation
├─ errors.py                   # Custom exception hierarchy
├─ validators.py               # Input validation utilities
├─ design_patterns.py          # Factory and Strategy patterns
├─ orchestrator.py             # System wiring and demo
└─ README.md                   # This file
```

## 🚀 Quick Start

### Running the Demo

```bash
cd food-delivery-app
python3 orchestrator.py
```

### Basic Usage

```python
from orchestrator import FoodDeliveryAppSystem

# Initialize the system
system = FoodDeliveryAppSystem()

# Create a user
user = system.user_manager.create_user(
    id="user1", 
    name="John Doe", 
    email="john@example.com", 
    phone="123-456-7890"
)

# Create a restaurant
restaurant = system.restaurant_manager.create_restaurant(
    id="rest1", 
    name="Pizza Palace", 
    cuisine="Italian", 
    address="123 Main St"
)

# Add dishes
dish = system.dish_manager.create_dish(
    id="dish1", 
    name="Margherita Pizza", 
    price=15.99, 
    restaurant_id="rest1"
)

# Add to cart
system.cart_manager.add_dish_to_cart("user1", "dish1", quantity=2)

# Place order with payment
order = system.order_manager.place_order(
    order_id="order1",
    user_id="user1", 
    delivery_address="456 Oak Avenue, Downtown",
    payment_method=PaymentMethod.CREDIT_CARD
)
```

## 🔧 Core Features

### 1. User Management
- **User Creation**: With email and phone validation
- **User Activation/Deactivation**: Control user ordering capabilities
- **User Validation**: Ensure users can place orders

```python
# Create user with validation
user = system.user_manager.create_user("user1", "John", "john@email.com", "123-456-7890")

# Deactivate user
system.user_manager.deactivate_user("user1")

# Validate user can order
system.user_manager.validate_user_can_order("user1")
```

### 2. Restaurant & Dish Management
- **Restaurant Operations**: Create and manage restaurants
- **Dish Management**: Add dishes with price validation
- **Availability Control**: Make dishes available/unavailable

```python
# Create restaurant
restaurant = system.restaurant_manager.create_restaurant("rest1", "Pizza Place", "Italian", "123 St")

# Add dish with validation
dish = system.dish_manager.create_dish("dish1", "Pizza", 15.99, "rest1")

# Control availability
system.dish_manager.update_dish_availability("dish1", False)
```

### 3. Cart Management
- **Single Restaurant Constraint**: Can't mix restaurants in cart
- **Quantity Validation**: Reasonable quantity limits
- **Cart Operations**: Add, remove, clear items

```python
# Add items to cart
system.cart_manager.add_dish_to_cart("user1", "dish1", 2)

# Get cart total
total = system.cart_manager.get_cart_total("user1")

# Clear cart
system.cart_manager.clear_cart("user1")
```

### 4. Order Management
- **Order Placement**: With comprehensive validation
- **Payment Integration**: Automatic payment processing
- **Status Management**: Order status transitions with validation

```python
# Place order with payment
order = system.order_manager.place_order(
    "order1", "user1", "123 Main St", PaymentMethod.CREDIT_CARD
)

# Update order status
system.order_manager.update_order_status("order1", OrderStatus.CONFIRMED)

# Get order details
order = system.order_manager.get_order("order1")
```

### 5. Payment Processing
- **Multiple Payment Methods**: Credit card, digital wallet, cash on delivery
- **Payment Status Tracking**: Pending → Processing → Successful/Failed
- **Refund Support**: Process refunds for successful payments

```python
# Process payment
success, message = system.payment_manager.process_payment_for_order(
    "payment1", "order1", 49.97, PaymentMethod.CREDIT_CARD, "user1"
)

# Get payment details
payment = system.payment_manager.get_payment_by_order("order1")

# Process refund
success, message = system.payment_manager.refund_payment("payment1")
```

## 🛡️ Error Handling & Validation

### Exception Hierarchy

```python
FoodDeliveryError (base)
├─ ValidationError           # Input validation failures
├─ EntityNotFoundError       # Entity not found in repository
├─ BusinessRuleViolationError # Business rule violations
├─ PaymentError              # Payment processing failures
├─ OrderError                # Order operation failures
├─ CartError                 # Cart operation failures
├─ UserError                 # User operation failures
└─ DishError                 # Dish operation failures
```

### Input Validation

The system includes comprehensive validation for:

- **Email Format**: RFC-compliant email validation
- **Phone Numbers**: Minimum 10 digits required
- **Prices**: Positive values with reasonable upper limits
- **Quantities**: Positive integers with reasonable limits
- **Addresses**: Minimum length and format validation
- **IDs**: Alphanumeric format validation

```python
from validators import Validators

# Validate email
Validators.validate_email("user@example.com")

# Validate price
Validators.validate_price(15.99)

# Validate quantity
Validators.validate_quantity(5)
```

### Business Rule Validation

- **User Activation**: Only active users can place orders
- **Dish Availability**: Only available dishes can be added to cart
- **Restaurant Constraint**: Cart can only contain dishes from one restaurant
- **Order Status Transitions**: Valid status transitions enforced
- **Payment Requirements**: Orders require valid payment methods

## 🎨 Design Patterns

### 1. Factory Pattern (RepositoryFactory)

```python
from design_patterns import RepositoryFactory

# Create repository instances
user_repo = RepositoryFactory.create_repository(User)
restaurant_repo = RepositoryFactory.create_repository(Restaurant)

# Register new repository types
RepositoryFactory.register_repository(CustomEntity, CustomRepository)
```

### 2. Strategy Pattern (PaymentStrategy)

```python
from design_patterns import PaymentStrategyFactory

# Create payment strategies
credit_card_strategy = PaymentStrategyFactory.create_strategy("credit_card")
digital_wallet_strategy = PaymentStrategyFactory.create_strategy("digital_wallet")

# Register new payment strategies
PaymentStrategyFactory.register_strategy("crypto", CryptoPaymentStrategy)
```

## 🔄 Core Workflows

### 1. Complete Order Flow

```python
# 1. Create user
user = system.user_manager.create_user("user1", "John", "john@email.com", "123-456-7890")

# 2. Create restaurant and dishes
restaurant = system.restaurant_manager.create_restaurant("rest1", "Pizza Place", "Italian", "123 St")
dish = system.dish_manager.create_dish("dish1", "Pizza", 15.99, "rest1")

# 3. Add to cart
system.cart_manager.add_dish_to_cart("user1", "dish1", 2)

# 4. Place order with payment
order = system.order_manager.place_order(
    "order1", "user1", "456 Oak Ave", PaymentMethod.CREDIT_CARD
)

# 5. Update order status
system.order_manager.update_order_status("order1", OrderStatus.CONFIRMED)
```

### 2. Error Handling Example

```python
try:
    # This will fail - dish doesn't exist
    system.cart_manager.add_dish_to_cart("user1", "nonexistent_dish", 1)
except EntityNotFoundError as e:
    print(f"Dish not found: {e}")

try:
    # This will fail - address too short
    system.order_manager.place_order("order2", "user1", "Short", PaymentMethod.CREDIT_CARD)
except ValidationError as e:
    print(f"Validation failed: {e}")
```

## 🧪 Testing

The system is designed for easy testing:

```python
# Mock repositories for testing
from repositories.in_memory.user_repo import InMemoryUserRepository
user_repo = InMemoryUserRepository()

# Mock payment gateway
from services.mock_payment_gateway import MockPaymentGateway
payment_gateway = MockPaymentGateway(success_rate=0.95)

# Test error scenarios
try:
    system.cart_manager.add_dish_to_cart("user1", "nonexistent_dish", 1)
except EntityNotFoundError:
    print("Expected error caught")
```

## 📈 Performance Considerations

### Current Optimizations
- **In-Memory Storage**: Fast access for development and testing
- **Validation Caching**: Validation results could be cached
- **Efficient Queries**: Repository methods optimized for common operations

### Scalability Features
- **Repository Pattern**: Easy to switch to database implementations
- **Service Abstraction**: Payment gateways can be swapped
- **Modular Design**: Components can be scaled independently

## 🔒 Security Features

### Input Validation
- **Email Validation**: Prevents invalid email formats
- **Phone Validation**: Ensures proper phone number format
- **Price Validation**: Prevents negative or unreasonable prices
- **ID Validation**: Alphanumeric format enforcement

### Business Logic Security
- **User Activation**: Prevents inactive users from ordering
- **Dish Availability**: Prevents ordering unavailable items
- **Payment Validation**: Ensures valid payment methods
- **Order Status Control**: Prevents invalid status transitions

## 🚀 Future Enhancements

### Potential Additions
1. **Database Integration**: PostgreSQL/MySQL repositories
2. **Authentication System**: User login and session management
3. **Real Payment Gateways**: Stripe, PayPal integration
4. **Notification System**: Email/SMS notifications
5. **Delivery Tracking**: Real-time order tracking
6. **Rating System**: Restaurant and dish ratings
7. **Inventory Management**: Stock tracking for dishes
8. **Analytics**: Order analytics and reporting

### Performance Improvements
1. **Caching Layer**: Redis for frequently accessed data
2. **Async Processing**: Background payment processing
3. **Database Indexing**: Optimized queries for large datasets
4. **Load Balancing**: Multiple service instances

## 📝 API Documentation

### User Manager API

```python
class UserManager:
    def create_user(id: str, name: str, email: str, phone: str) -> User
    def get_user(user_id: str) -> User
    def get_user_optional(user_id: str) -> Optional[User]
    def list_all_users() -> List[User]
    def deactivate_user(user_id: str) -> None
    def activate_user(user_id: str) -> None
    def validate_user_can_order(user_id: str) -> None
```

### Cart Manager API

```python
class CartManager:
    def create_cart(cart_id: str, user_id: str) -> Cart
    def get_user_cart(user_id: str) -> Optional[Cart]
    def get_user_cart_or_create(user_id: str) -> Cart
    def add_dish_to_cart(user_id: str, dish_id: str, quantity: int = 1) -> None
    def remove_dish_from_cart(user_id: str, dish_id: str) -> None
    def clear_cart(user_id: str) -> None
    def get_cart_total(user_id: str) -> float
```

### Order Manager API

```python
class OrderManager:
    def place_order(order_id: str, user_id: str, delivery_address: str, 
                   payment_method: PaymentMethod = None) -> Order
    def get_order(order_id: str) -> Order
    def get_order_optional(order_id: str) -> Optional[Order]
    def get_user_orders(user_id: str) -> List[Order]
    def update_order_status(order_id: str, status: OrderStatus) -> None
```

## 🤝 Contributing

This system demonstrates clean architecture principles and can be extended with:

1. **New Entities**: Add new business objects
2. **New Managers**: Implement new business logic
3. **New Repositories**: Add different storage backends
4. **New Services**: Integrate external services
5. **New Validators**: Add custom validation rules
6. **New Design Patterns**: Implement additional patterns

## 📄 License

This project is for educational and demonstration purposes.
