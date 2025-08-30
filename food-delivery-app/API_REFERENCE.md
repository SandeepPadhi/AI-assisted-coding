# API Reference

## Overview

This document provides a comprehensive reference for all public APIs in the Food Delivery App system.

## Entity Managers

### UserManager

Manages user-related operations including creation, validation, and status management.

#### Methods

##### `create_user(id: str, name: str, email: str, phone: str) -> User`
Creates a new user with validation.

**Parameters:**
- `id` (str): Unique user identifier
- `name` (str): User's display name
- `email` (str): User's email address (validated)
- `phone` (str): User's phone number (validated)

**Returns:**
- `User`: Created user object

**Raises:**
- `ValidationError`: If input validation fails
- `UserError`: If user creation fails

**Example:**
```python
user = user_manager.create_user("user1", "John Doe", "john@example.com", "123-456-7890")
```

##### `get_user(user_id: str) -> User`
Gets a user by ID, raising exception if not found.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- `User`: User object

**Raises:**
- `EntityNotFoundError`: If user not found

**Example:**
```python
user = user_manager.get_user("user1")
```

##### `get_user_optional(user_id: str) -> Optional[User]`
Gets a user by ID, returning None if not found.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- `Optional[User]`: User object or None

**Example:**
```python
user = user_manager.get_user_optional("user1")
if user:
    print(f"Found user: {user.name}")
```

##### `list_all_users() -> List[User]`
Gets all users in the system.

**Returns:**
- `List[User]`: List of all users

**Example:**
```python
users = user_manager.list_all_users()
for user in users:
    print(f"User: {user.name}")
```

##### `deactivate_user(user_id: str) -> None`
Deactivates a user account.

**Parameters:**
- `user_id` (str): User identifier

**Raises:**
- `EntityNotFoundError`: If user not found

**Example:**
```python
user_manager.deactivate_user("user1")
```

##### `activate_user(user_id: str) -> None`
Activates a user account.

**Parameters:**
- `user_id` (str): User identifier

**Raises:**
- `EntityNotFoundError`: If user not found

**Example:**
```python
user_manager.activate_user("user1")
```

##### `validate_user_can_order(user_id: str) -> None`
Validates that a user can place an order.

**Parameters:**
- `user_id` (str): User identifier

**Raises:**
- `EntityNotFoundError`: If user not found
- `BusinessRuleViolationError`: If user is not active

**Example:**
```python
user_manager.validate_user_can_order("user1")
```

### CartManager

Manages shopping cart operations including adding/removing items and cart validation.

#### Methods

##### `create_cart(cart_id: str, user_id: str) -> Cart`
Creates a new cart for a user.

**Parameters:**
- `cart_id` (str): Unique cart identifier
- `user_id` (str): User identifier

**Returns:**
- `Cart`: Created cart object

**Raises:**
- `ValidationError`: If input validation fails
- `CartError`: If cart creation fails

**Example:**
```python
cart = cart_manager.create_cart("cart1", "user1")
```

##### `get_user_cart(user_id: str) -> Optional[Cart]`
Gets cart for a user, returning None if not found.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- `Optional[Cart]`: Cart object or None

**Example:**
```python
cart = cart_manager.get_user_cart("user1")
if cart:
    print(f"Cart has {len(cart.items)} items")
```

##### `get_user_cart_or_create(user_id: str) -> Cart`
Gets cart for a user, creating one if it doesn't exist.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- `Cart`: Cart object (created if needed)

**Example:**
```python
cart = cart_manager.get_user_cart_or_create("user1")
```

##### `add_dish_to_cart(user_id: str, dish_id: str, quantity: int = 1) -> None`
Adds a dish to the user's cart with validation.

**Parameters:**
- `user_id` (str): User identifier
- `dish_id` (str): Dish identifier
- `quantity` (int): Quantity to add (default: 1)

**Raises:**
- `ValidationError`: If quantity validation fails
- `EntityNotFoundError`: If dish not found
- `BusinessRuleViolationError`: If dish unavailable or restaurant constraint violated
- `CartError`: If cart operation fails

**Example:**
```python
cart_manager.add_dish_to_cart("user1", "dish1", 2)
```

##### `remove_dish_from_cart(user_id: str, dish_id: str) -> None`
Removes a dish from the user's cart.

**Parameters:**
- `user_id` (str): User identifier
- `dish_id` (str): Dish identifier

**Raises:**
- `EntityNotFoundError`: If cart not found

**Example:**
```python
cart_manager.remove_dish_from_cart("user1", "dish1")
```

##### `clear_cart(user_id: str) -> None`
Clears all items from the user's cart.

**Parameters:**
- `user_id` (str): User identifier

**Raises:**
- `EntityNotFoundError`: If cart not found

**Example:**
```python
cart_manager.clear_cart("user1")
```

##### `get_cart_total(user_id: str) -> float`
Calculates the total cost of items in the cart.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- `float`: Total cart value

**Example:**
```python
total = cart_manager.get_cart_total("user1")
print(f"Cart total: ${total:.2f}")
```

### OrderManager

Manages order operations including placement, status updates, and payment integration.

#### Methods

##### `place_order(order_id: str, user_id: str, delivery_address: str, payment_method: PaymentMethod = None) -> Order`
Places an order with comprehensive validation.

**Parameters:**
- `order_id` (str): Unique order identifier
- `user_id` (str): User identifier
- `delivery_address` (str): Delivery address (validated)
- `payment_method` (PaymentMethod, optional): Payment method for the order

**Returns:**
- `Order`: Created order object

**Raises:**
- `ValidationError`: If input validation fails
- `EntityNotFoundError`: If user, cart, or dish not found
- `BusinessRuleViolationError`: If business rules violated
- `OrderError`: If order placement fails
- `PaymentError`: If payment processing fails

**Example:**
```python
order = order_manager.place_order(
    "order1", "user1", "123 Main St", PaymentMethod.CREDIT_CARD
)
```

##### `get_order(order_id: str) -> Order`
Gets order by ID, raising exception if not found.

**Parameters:**
- `order_id` (str): Order identifier

**Returns:**
- `Order`: Order object

**Raises:**
- `EntityNotFoundError`: If order not found

**Example:**
```python
order = order_manager.get_order("order1")
```

##### `get_order_optional(order_id: str) -> Optional[Order]`
Gets order by ID, returning None if not found.

**Parameters:**
- `order_id` (str): Order identifier

**Returns:**
- `Optional[Order]`: Order object or None

**Example:**
```python
order = order_manager.get_order_optional("order1")
```

##### `get_user_orders(user_id: str) -> List[Order]`
Gets all orders for a user.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- `List[Order]`: List of user's orders

**Example:**
```python
orders = order_manager.get_user_orders("user1")
for order in orders:
    print(f"Order: {order.id}, Status: {order.status.value}")
```

##### `update_order_status(order_id: str, status: OrderStatus) -> None`
Updates order status with validation.

**Parameters:**
- `order_id` (str): Order identifier
- `status` (OrderStatus): New order status

**Raises:**
- `EntityNotFoundError`: If order not found
- `BusinessRuleViolationError`: If status transition invalid

**Example:**
```python
order_manager.update_order_status("order1", OrderStatus.CONFIRMED)
```

### PaymentManager

Manages payment processing and payment-related operations.

#### Methods

##### `process_payment_for_order(payment_id: str, order_id: str, amount: float, payment_method: PaymentMethod, user_id: str) -> Tuple[bool, str]`
Processes payment for an order through the payment gateway.

**Parameters:**
- `payment_id` (str): Unique payment identifier
- `order_id` (str): Order identifier
- `amount` (float): Payment amount
- `payment_method` (PaymentMethod): Payment method
- `user_id` (str): User identifier

**Returns:**
- `Tuple[bool, str]`: (success, message)

**Example:**
```python
success, message = payment_manager.process_payment_for_order(
    "payment1", "order1", 49.97, PaymentMethod.CREDIT_CARD, "user1"
)
```

##### `get_payment_by_order(order_id: str) -> Optional[Payment]`
Gets payment information for an order.

**Parameters:**
- `order_id` (str): Order identifier

**Returns:**
- `Optional[Payment]`: Payment object or None

**Example:**
```python
payment = payment_manager.get_payment_by_order("order1")
if payment:
    print(f"Payment status: {payment.status.value}")
```

##### `get_user_payments(user_id: str) -> List[Payment]`
Gets all payments for a user.

**Parameters:**
- `user_id` (str): User identifier

**Returns:**
- `List[Payment]`: List of user's payments

**Example:**
```python
payments = payment_manager.get_user_payments("user1")
for payment in payments:
    print(f"Payment: {payment.id}, Amount: ${payment.amount}")
```

##### `refund_payment(payment_id: str) -> Tuple[bool, str]`
Processes a refund for a payment.

**Parameters:**
- `payment_id` (str): Payment identifier

**Returns:**
- `Tuple[bool, str]`: (success, message)

**Raises:**
- `EntityNotFoundError`: If payment not found
- `BusinessRuleViolationError`: If payment cannot be refunded

**Example:**
```python
success, message = payment_manager.refund_payment("payment1")
```

## Validation Utilities

### Validators

Static validation methods for input validation.

#### Methods

##### `validate_email(email: str) -> None`
Validates email format.

**Parameters:**
- `email` (str): Email address to validate

**Raises:**
- `ValidationError`: If email format is invalid

**Example:**
```python
Validators.validate_email("user@example.com")
```

##### `validate_phone(phone: str) -> None`
Validates phone number format.

**Parameters:**
- `phone` (str): Phone number to validate

**Raises:**
- `ValidationError`: If phone format is invalid

**Example:**
```python
Validators.validate_phone("123-456-7890")
```

##### `validate_price(price: float) -> None`
Validates price is positive and reasonable.

**Parameters:**
- `price` (float): Price to validate

**Raises:**
- `ValidationError`: If price is invalid

**Example:**
```python
Validators.validate_price(15.99)
```

##### `validate_quantity(quantity: int) -> None`
Validates quantity is positive and reasonable.

**Parameters:**
- `quantity` (int): Quantity to validate

**Raises:**
- `ValidationError`: If quantity is invalid

**Example:**
```python
Validators.validate_quantity(5)
```

##### `validate_string_not_empty(value: str, field_name: str) -> None`
Validates that a string is not empty.

**Parameters:**
- `value` (str): String to validate
- `field_name` (str): Field name for error message

**Raises:**
- `ValidationError`: If string is empty

**Example:**
```python
Validators.validate_string_not_empty("John", "Name")
```

##### `validate_id_format(id_value: str, entity_name: str) -> None`
Validates ID format.

**Parameters:**
- `id_value` (str): ID to validate
- `entity_name` (str): Entity name for error message

**Raises:**
- `ValidationError`: If ID format is invalid

**Example:**
```python
Validators.validate_id_format("user1", "User")
```

##### `validate_address(address: str) -> None`
Validates delivery address.

**Parameters:**
- `address` (str): Address to validate

**Raises:**
- `ValidationError`: If address is invalid

**Example:**
```python
Validators.validate_address("123 Main Street, City, State 12345")
```

## Design Patterns

### RepositoryFactory

Factory for creating repository instances.

#### Methods

##### `create_repository(entity_type: Type) -> BaseRepository`
Creates a repository instance for the given entity type.

**Parameters:**
- `entity_type` (Type): Entity type class

**Returns:**
- `BaseRepository`: Repository instance

**Raises:**
- `ValueError`: If no repository found for entity type

**Example:**
```python
user_repo = RepositoryFactory.create_repository(User)
```

##### `register_repository(entity_type: Type, repository_class: Type[BaseRepository]) -> None`
Registers a new repository class for an entity type.

**Parameters:**
- `entity_type` (Type): Entity type class
- `repository_class` (Type[BaseRepository]): Repository class

**Example:**
```python
RepositoryFactory.register_repository(CustomEntity, CustomRepository)
```

### PaymentStrategyFactory

Factory for creating payment strategies.

#### Methods

##### `create_strategy(payment_method: str) -> PaymentStrategy`
Creates a payment strategy for the given method.

**Parameters:**
- `payment_method` (str): Payment method name

**Returns:**
- `PaymentStrategy`: Payment strategy instance

**Raises:**
- `ValueError`: If payment method is unknown

**Example:**
```python
strategy = PaymentStrategyFactory.create_strategy("credit_card")
```

##### `register_strategy(method: str, strategy_class: Type[PaymentStrategy]) -> None`
Registers a new payment strategy.

**Parameters:**
- `method` (str): Payment method name
- `strategy_class` (Type[PaymentStrategy]): Strategy class

**Example:**
```python
PaymentStrategyFactory.register_strategy("crypto", CryptoPaymentStrategy)
```

## Error Types

### FoodDeliveryError
Base exception for all food delivery app errors.

### ValidationError
Raised when input validation fails.

### EntityNotFoundError
Raised when an entity is not found in the repository.

### BusinessRuleViolationError
Raised when a business rule is violated.

### PaymentError
Raised when payment processing fails.

### OrderError
Raised when order operations fail.

### CartError
Raised when cart operations fail.

### UserError
Raised when user operations fail.

### DishError
Raised when dish operations fail.

## Enums

### PaymentMethod
```python
class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    DIGITAL_WALLET = "digital_wallet"
    CASH_ON_DELIVERY = "cash_on_delivery"
```

### PaymentStatus
```python
class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    REFUNDED = "refunded"
```

### OrderStatus
```python
class OrderStatus(Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

## Usage Examples

### Complete Order Flow
```python
# Initialize system
system = FoodDeliveryAppSystem()

# Create user
user = system.user_manager.create_user("user1", "John", "john@email.com", "123-456-7890")

# Create restaurant and dish
restaurant = system.restaurant_manager.create_restaurant("rest1", "Pizza Place", "Italian", "123 St")
dish = system.dish_manager.create_dish("dish1", "Pizza", 15.99, "rest1")

# Add to cart
system.cart_manager.add_dish_to_cart("user1", "dish1", 2)

# Place order
order = system.order_manager.place_order(
    "order1", "user1", "456 Oak Ave", PaymentMethod.CREDIT_CARD
)

# Update status
system.order_manager.update_order_status("order1", OrderStatus.CONFIRMED)
```

### Error Handling
```python
try:
    system.cart_manager.add_dish_to_cart("user1", "nonexistent_dish", 1)
except EntityNotFoundError as e:
    print(f"Dish not found: {e}")
except BusinessRuleViolationError as e:
    print(f"Business rule violated: {e}")
except ValidationError as e:
    print(f"Validation failed: {e}")
```
