"""
Comprehensive test suite for the e-commerce system.
"""
import unittest
from datetime import datetime
from functools import wraps
from uuid import uuid4

from entities import User, Product, Cart, Order, OrderStatus, Payment, PaymentStatus
# Repositories are used through ECommerceSystem
from managers import ProductManager, CartManager
from services import PaymentService
from main import ECommerceSystem

def print_test_info(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"\n{'='*50}")
        print(f"Running: {func.__name__.replace('_', ' ').title()}")
        print(f"Description: {func.__doc__.strip()}")
        print(f"{'='*50}")
        result = func(*args, **kwargs)
        print(f"✅ Test completed successfully\n")
        return result
    return wrapper

class TestECommerceSystem(unittest.TestCase):
    def setUp(self):
        """Initialize a fresh system for each test."""
        self.system = ECommerceSystem()
        self.user = self.system.create_user("Test User", "test@example.com")
        
    @print_test_info
    def test_user_creation(self):
        """Test user creation and validation."""
        # Test successful user creation
        print("Testing: Create user with valid details")
        user = self.system.create_user("John Doe", "john@example.com")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.email, "john@example.com")
        print("✓ User created successfully")
        
        # Test duplicate email
        print("\nTesting: Attempt to create user with duplicate email")
        with self.assertRaises(ValueError):
            self.system.create_user("Jane Doe", "john@example.com")
        print("✓ Duplicate email prevented")
        
        # Test invalid email
        print("\nTesting: Attempt to create user with invalid email")
        with self.assertRaises(ValueError):
            self.system.create_user("Invalid", "invalid-email")
        print("✓ Invalid email prevented")

    @print_test_info
    def test_product_management(self):
        """Test product creation and stock management."""
        # Test product creation
        print("Testing: Create product with valid details")
        product = self.system.create_product("Test Product", "Description", 99.99, 10)
        self.assertEqual(product.name, "Test Product")
        self.assertEqual(product.stock, 10)
        print("✓ Product created successfully")
        
        # Test invalid product creation
        print("\nTesting: Attempt to create product with negative price")
        with self.assertRaises(ValueError):
            self.system.create_product("Invalid", "Description", -10, 10)
        print("✓ Negative price prevented")
        
        print("\nTesting: Attempt to create product with negative stock")
        with self.assertRaises(ValueError):
            self.system.create_product("Invalid", "Description", 10, -1)
        print("✓ Negative stock prevented")
        
        # Test low stock detection
        print("\nTesting: Low stock detection")
        products = self.system.product_manager.get_low_stock_products(threshold=15)
        self.assertIn(product, products)
        print("✓ Low stock detection working")

    @print_test_info
    def test_cart_operations(self):
        """Test cart operations including add, remove, and checkout."""
        # Create products
        print("Testing: Setting up products")
        laptop = self.system.create_product("Laptop", "Description", 999.99, 5)
        phone = self.system.create_product("Phone", "Description", 499.99, 10)
        print("✓ Products created")
        
        # Test adding to cart
        print("\nTesting: Adding items to cart")
        self.system.add_to_cart(self.user.id, laptop.id, 1)
        self.system.add_to_cart(self.user.id, phone.id, 2)
        
        cart = self.system.cart_repository.find_active_cart_by_user_id(self.user.id)
        self.assertEqual(len(cart.items), 2)
        print("✓ Items added to cart successfully")
        
        # Test adding more than available stock
        print("\nTesting: Attempt to add more than available stock")
        with self.assertRaises(ValueError):
            self.system.add_to_cart(self.user.id, laptop.id, 10)
        print("✓ Prevented exceeding stock limit")
        
        # Test cart total calculation
        print("\nTesting: Cart total calculation")
        total = self.system.cart_manager.get_cart_total(cart.id)
        expected_total = 999.99 + (2 * 499.99)
        self.assertAlmostEqual(total, expected_total, places=2)
        print(f"✓ Cart total calculated correctly: ${total:.2f}")

    @print_test_info
    def test_checkout_process(self):
        """Test the complete checkout process."""
        # Setup products and cart
        print("Testing: Setting up products and cart")
        laptop = self.system.create_product("Laptop", "Description", 999.99, 5)
        phone = self.system.create_product("Phone", "Description", 499.99, 10)
        self.system.add_to_cart(self.user.id, laptop.id, 1)
        self.system.add_to_cart(self.user.id, phone.id, 2)
        print("✓ Cart setup complete")
        
        # Test successful checkout
        print("\nTesting: Processing checkout")
        order = self.system.checkout(self.user.id)
        self.assertEqual(order.status, OrderStatus.PAID)
        self.assertEqual(len(order.items), 2)
        print("✓ Order created successfully")
        
        # Verify stock was updated
        print("\nTesting: Stock update verification")
        updated_laptop = self.system.product_manager.get_product(laptop.id)
        updated_phone = self.system.product_manager.get_product(phone.id)
        self.assertEqual(updated_laptop.stock, 4)
        self.assertEqual(updated_phone.stock, 8)
        print("✓ Stock levels updated correctly")
        
        # Verify cart was cleared
        print("\nTesting: Cart clearing")
        cart = self.system.cart_repository.find_active_cart_by_user_id(self.user.id)
        self.assertEqual(len(cart.items), 0)
        print("✓ Cart cleared after checkout")
        
        # Verify payment was recorded
        print("\nTesting: Payment verification")
        payment = self.system.payment_repository.find_payment_by_order_id(order.id)
        self.assertIsNotNone(payment)
        self.assertEqual(payment.status, PaymentStatus.SUCCESS)
        print("✓ Payment recorded successfully")

    @print_test_info
    def test_order_history(self):
        """Test order history functionality."""
        print("Testing: Creating multiple orders")
        # Create and checkout multiple orders
        for i in range(3):
            product = self.system.create_product(f"Product {i}", "Description", 99.99, 5)
            self.system.add_to_cart(self.user.id, product.id, 1)
            self.system.checkout(self.user.id)
            print(f"✓ Order {i+1} created and processed")
        
        # Test order history
        print("\nTesting: Retrieving order history")
        history = self.system.get_order_history(self.user.id)
        self.assertEqual(len(history), 3)
        print(f"✓ Found {len(history)} orders in history")
        
        # Verify orders are for the correct user
        print("\nTesting: Order ownership verification")
        for order in history:
            self.assertEqual(order.user_id, self.user.id)
            self.assertEqual(order.status, OrderStatus.PAID)
        print("✓ All orders verified for correct user and status")

    @print_test_info
    def test_edge_cases(self):
        """Test various edge cases and error conditions."""
        # Test checkout with empty cart
        print("Testing: Checkout with empty cart")
        with self.assertRaises(ValueError):
            self.system.checkout(self.user.id)
        print("✓ Empty cart checkout prevented")
        
        # Test adding non-existent product to cart
        print("\nTesting: Adding non-existent product")
        with self.assertRaises(ValueError):
            self.system.add_to_cart(self.user.id, uuid4(), 1)
        print("✓ Non-existent product addition prevented")
        
        # Test getting order history for non-existent user
        print("\nTesting: Order history for non-existent user")
        history = self.system.get_order_history(uuid4())
        self.assertEqual(len(history), 0)
        print("✓ Empty history returned for non-existent user")
        
        # Test product stock depletion
        print("\nTesting: Product stock depletion scenario")
        product = self.system.create_product("Limited Item", "Description", 99.99, 1)
        self.system.add_to_cart(self.user.id, product.id, 1)
        self.system.checkout(self.user.id)
        print("✓ Limited stock item purchased")
        
        # Attempt to buy out-of-stock product
        print("\nTesting: Purchase attempt for out-of-stock product")
        with self.assertRaises(ValueError):
            self.system.add_to_cart(self.user.id, product.id, 1)
        print("✓ Out-of-stock purchase prevented")

def main():
    unittest.main(verbosity=1)

if __name__ == "__main__":
    main()