"""
System orchestrator for the food delivery app.
"""
from entities.user import User
from entities.restaurant import Restaurant
from entities.dish import Dish
from entities.cart import Cart
from entities.order import Order, OrderStatus
from entities.payment import PaymentMethod

from repositories.in_memory.user_repo import InMemoryUserRepository
from repositories.in_memory.restaurant_repo import InMemoryRestaurantRepository
from repositories.in_memory.dish_repo import InMemoryDishRepository
from repositories.in_memory.cart_repo import InMemoryCartRepository
from repositories.in_memory.order_repo import InMemoryOrderRepository
from repositories.in_memory.payment_repo import InMemoryPaymentRepository

from managers.user_manager import UserManager
from managers.restaurant_manager import RestaurantManager
from managers.dish_manager import DishManager
from managers.cart_manager import CartManager
from managers.order_manager import OrderManager
from managers.payment_manager import PaymentManager

from services.mock_payment_gateway import MockPaymentGateway
from design_patterns import RepositoryFactory, PaymentStrategyFactory
from errors import FoodDeliveryError


class FoodDeliveryAppSystem:
    def __init__(self):
        # Initialize repositories
        self.user_repository = InMemoryUserRepository()
        self.restaurant_repository = InMemoryRestaurantRepository()
        self.dish_repository = InMemoryDishRepository()
        self.cart_repository = InMemoryCartRepository()
        self.order_repository = InMemoryOrderRepository()
        self.payment_repository = InMemoryPaymentRepository()
        
        # Initialize services
        self.payment_gateway = MockPaymentGateway(success_rate=0.95)
        
        # Initialize managers
        self.user_manager = UserManager(self.user_repository)
        self.restaurant_manager = RestaurantManager(self.restaurant_repository)
        self.dish_manager = DishManager(self.dish_repository)
        self.cart_manager = CartManager(self.cart_repository, self.dish_repository)
        self.payment_manager = PaymentManager(self.payment_repository, self.payment_gateway)
        self.order_manager = OrderManager(self.order_repository, self.cart_repository, 
                                        self.dish_repository, self.payment_manager)
    
    def run_demo(self) -> None:
        """Run a demonstration of the food delivery app functionality."""
        print("=== Food Delivery App Demo ===\n")
        
        try:
            # 1. Create a user
            print("1. Creating a user...")
            user = self.user_manager.create_user("user1", "John Doe", "john@example.com", "123-456-7890")
            print(f"   Created: {user}\n")
            
            # 2. Create a restaurant
            print("2. Creating a restaurant...")
            restaurant = self.restaurant_manager.create_restaurant("rest1", "Pizza Palace", "Italian", "123 Main St")
            print(f"   Created: {restaurant}\n")
            
            # 3. Add dishes to the restaurant
            print("3. Adding dishes to the restaurant...")
            dish1 = self.dish_manager.create_dish("dish1", "Margherita Pizza", 15.99, "rest1", "Classic tomato and mozzarella")
            dish2 = self.dish_manager.create_dish("dish2", "Pepperoni Pizza", 17.99, "rest1", "Spicy pepperoni with cheese")
            print(f"   Created: {dish1}")
            print(f"   Created: {dish2}\n")
            
            # 4. Show all restaurants
            print("4. Listing all restaurants...")
            restaurants = self.restaurant_manager.list_all_restaurants()
            for r in restaurants:
                print(f"   {r}")
            print()
            
            # 5. Show dishes in the restaurant
            print("5. Listing dishes in Pizza Palace...")
            dishes = self.dish_manager.list_dishes_by_restaurant("rest1")
            for d in dishes:
                print(f"   {d}")
            print()
            
            # 6. Add dishes to cart
            print("6. Adding dishes to cart...")
            self.cart_manager.add_dish_to_cart("user1", "dish1", 2)
            self.cart_manager.add_dish_to_cart("user1", "dish2", 1)
            print(f"   Added Margherita Pizza (2x): Success")
            print(f"   Added Pepperoni Pizza (1x): Success\n")
            
            # 7. Show cart contents
            print("7. Showing cart contents...")
            cart = self.cart_manager.get_user_cart("user1")
            if cart:
                print(f"   Cart: {cart}")
                print(f"   Total items: {cart.get_total_items()}")
                print(f"   Cart total: ${self.cart_manager.get_cart_total('user1'):.2f}")
            print()
            
            # 8. Place order with payment
            print("8. Placing order with payment...")
            order = self.order_manager.place_order("order1", "user1", "456 Oak Avenue, Downtown", 
                                                 PaymentMethod.CREDIT_CARD)
            print(f"   Order placed: {order}")
            print(f"   Total amount: ${order.total_amount:.2f}")
            print()
            
            # 9. Update order status
            print("9. Updating order status...")
            self.order_manager.update_order_status("order1", OrderStatus.CONFIRMED)
            updated_order = self.order_manager.get_order("order1")
            print(f"   Order status: {updated_order.status.value}")
            print()
            
            # 10. Show payment information
            print("10. Showing payment information...")
            payment = self.payment_manager.get_payment_by_order("order1")
            if payment:
                print(f"   Payment: {payment}")
                print(f"   Transaction ID: {payment.transaction_id}")
            print()
            
            # 11. Show user's order history
            print("11. Showing user's order history...")
            user_orders = self.order_manager.get_user_orders("user1")
            for o in user_orders:
                print(f"   {o}")
            
            # 12. Show user's payment history
            print("12. Showing user's payment history...")
            user_payments = self.payment_manager.get_user_payments("user1")
            for p in user_payments:
                print(f"   {p}")
            
            # 13. Demonstrate error handling
            print("13. Demonstrating error handling...")
            try:
                self.cart_manager.add_dish_to_cart("user1", "nonexistent_dish", 1)
            except Exception as e:
                print(f"   Expected error caught: {type(e).__name__}: {e}")
            
            try:
                self.order_manager.place_order("order2", "user1", "Short", PaymentMethod.CREDIT_CARD)
            except Exception as e:
                print(f"   Expected error caught: {type(e).__name__}: {e}")
            
            print("\n=== Demo Complete ===")
            
        except FoodDeliveryError as e:
            print(f"Demo failed with error: {type(e).__name__}: {e}")
        except Exception as e:
            print(f"Unexpected error during demo: {type(e).__name__}: {e}")


if __name__ == "__main__":
    system = FoodDeliveryAppSystem()
    system.run_demo()
