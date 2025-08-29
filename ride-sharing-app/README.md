# Ride Sharing Application

A complete ride sharing application built with clean architecture principles in Python.

## Features

- **User Management**: Register users and manage their profiles
- **Driver Management**: Register drivers with vehicle information and ratings
- **Ride Requests**: Users can request rides with pickup/dropoff locations
- **Ride Matching**: Drivers can accept available ride requests
- **Trip Lifecycle**: Complete trip management from request to completion
- **Billing System**: Automatic bill generation with distance-based pricing
- **Payment Processing**: Integrated payment handling
- **Rating System**: Users can rate drivers after trips
- **Trip History**: View trip history for both users and drivers

## Architecture

The application follows clean architecture principles:

- **Entities** (`entities.py`): Core business entities with validation
- **Repositories** (`repositories.py`): Abstract data access layer with in-memory implementation
- **Managers** (`managers.py`): Business logic layer for each entity
- **Orchestrator** (`orchestrator.py`): Main system coordinator

## Quick Start

1. **Run the demo**:
   ```bash
   python3 demo.py
   ```

2. **Use programmatically**:
   ```python
   from orchestrator import RideSharingAppSystem

   system = RideSharingAppSystem()

   # Register a user
   user = system.register_user("John Doe", "john@example.com", "123-456-7890")

   # Register a driver
   driver = system.register_driver("Bob Wilson", "bob@example.com", "555-123-4567", "DL123456")

   # Register vehicle
   vehicle = system.register_vehicle_for_driver(driver.driver_id, "Toyota", "Camry", 2020, "ABC-123")

   # Request a ride
   trip = system.request_ride(user.user_id, 37.7749, -122.4194, 37.7849, -122.4094)

   # Driver accepts
   system.accept_ride(trip.trip_id, driver.driver_id)

   # Complete the ride
   system.start_ride(trip.trip_id)
   system.complete_ride(trip.trip_id, 10.0)  # 10 km distance

   # Process payment
   system.process_payment(trip.trip_id)
   bill = system.get_trip_bill(trip.trip_id)
   ```

## Design Principles

- ✅ Clean Architecture with clear separation of concerns
- ✅ Abstract repositories for easy database migration
- ✅ Single Responsibility Principle (SRP)
- ✅ Type hints for all functions
- ✅ Self-explanatory function names
- ✅ No external dependencies
- ✅ Modular and maintainable code

## File Structure

```
ride-sharing-app/
├── main.py          # Project overview and documentation
├── entities.py      # Core business entities
├── repositories.py  # Abstract repositories and in-memory implementations
├── managers.py      # Business logic managers
├── orchestrator.py  # Main system coordinator
├── demo.py          # Comprehensive demonstration
└── README.md        # This file
```

## Extension Points

The system is designed for easy extension:

- **Database Integration**: Replace in-memory repositories with database implementations
- **API Layer**: Add REST endpoints using Flask/FastAPI
- **Real-time Features**: Integrate WebSocket for live updates
- **Payment Gateways**: Connect to Stripe, PayPal, etc.
- **GPS Tracking**: Add real-time location tracking
- **Mobile Apps**: Create iOS/Android apps using the same backend

## Requirements

- Python 3.7+
- No external dependencies (pure Python)

## License

This project is open source and available under the MIT License.
