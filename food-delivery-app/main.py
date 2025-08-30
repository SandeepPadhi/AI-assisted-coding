"""
Food Delivery App

Goal:
- Create a food delivery app.


Functional Requirements:
- User can see the list of all restaurants
- User can see the list of all dishes in a restaurant
- User can add a dish to the cart
- User can place an order

Non-Functional Requirements:
- The system should be able to handle 1000 requests per second
- The system should be able to scale to 1000000 requests per second


Entities:
- Restaurant
- Dish
- Cart
- Order
- User


EntityManagers:
- RestaurantManager
- DishManager
- CartManager
- OrderManager
- UserManager   

Repositories:
- RestaurantRepository
- DishRepository
- CartRepository
- OrderRepository
- UserRepository

SystemOrchestrator:
- FoodDeliveryAppSystem

ExternalServices:
- None


"""