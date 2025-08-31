"""
Flight Reservation System - MVP Implementation

Goal:
- Create a flight reservation system

Functional Requirements:
- User can search for a flight
- User can book a flight
- User can cancel a flight
- User can view their bookings

Non-Functional Requirements:
- Should be thread safe

Entities:
- Flight
- Passenger
- Booking
- User

Entity-Managers:
- FlightManager
- PassengerManager
- BookingManager
- UserManager

Repositories:
- FlightRepository
- PassengerRepository
- BookingRepository
- UserRepository

SystemOrchestrator:
- FlightReservationSystem

ExternalServices:
- None

Design Guidelines:
- Use good naming conventions
- Divide the code into entities, entity managers, repositories, system orchestrator, and external services as needed
- Use correct abstractions for future extensions
- Do not use any external libraries.
- Write the code in a way that it is easy to understand and easy to maintain.
- Keep the code modular and short which satisfies the requirements. and single responsibility principle.
- Respository function names should be self-explanatory.
- YOu can use repository class to store different entities and then extend it to in-memory or other storage systems.
- Do not use generics for now but create different abstractions for different entities.
- Each entity should be able to handle its invariants and validations and business logic.
- Use type hints for all functions and variables.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
import threading
from dataclasses import dataclass
import re

from exceptions import (
    EntityNotFoundError, EntityAlreadyExistsError, 
    InvalidBookingError, FlightCapacityError, ValidationError
)


# ============================================================================
# PART 1: MVP CORE ENTITIES (Data + Basic Invariants Only)
# ============================================================================

# Design Pattern: Value Object / Entity
# Purpose: Represent core business concept with basic invariants
# Implementation: Data class with constructor validation
# Trade-offs: Simplicity vs rich domain methods

@dataclass
class User:
    """User entity representing a system user"""
    # user_id: unique identifier for user lookup
    # name: display name for user interface
    # email: contact information for notifications
    user_id: str
    name: str
    email: str
    
    def __post_init__(self) -> None:
        # Basic null checks only in MVP
        if not self.user_id or not self.name or not self.email:
            raise ValueError("User ID, name, and email are required")
        # Extension point: add email_validation() post-MVP (Strategy Pattern)


@dataclass
class Flight:
    """Flight entity representing available flights"""
    # flight_id: unique identifier for flight lookup
    # flight_number: airline flight number for display
    # source: departure airport code
    # destination: arrival airport code
    # capacity: maximum number of seats available
    flight_id: str
    flight_number: str
    source: str
    destination: str
    capacity: int
    
    def __post_init__(self) -> None:
        # Basic null checks only in MVP
        if not self.flight_id or not self.flight_number or not self.source or not self.destination:
            raise ValueError("Flight ID, number, source, and destination are required")
        if self.capacity <= 0:
            raise ValueError("Flight capacity must be positive")
        # Extension point: add route_validation() post-MVP (Specification Pattern)


@dataclass
class Passenger:
    """Passenger entity representing a person who can book flights"""
    # passenger_id: unique identifier for passenger lookup
    # user_id: reference to the user who owns this passenger profile
    # name: passenger name for booking display
    # passport_number: travel document for international flights
    passenger_id: str
    user_id: str
    name: str
    passport_number: str
    
    def __post_init__(self) -> None:
        # Basic null checks only in MVP
        if not self.passenger_id or not self.user_id or not self.name or not self.passport_number:
            raise ValueError("Passenger ID, user ID, name, and passport number are required")
        # Extension point: add passport_validation() post-MVP (Strategy Pattern)


@dataclass
class Booking:
    """Booking entity representing a flight reservation"""
    # booking_id: unique identifier for booking lookup
    # passenger_id: reference to the passenger making the booking
    # flight_id: reference to the booked flight
    # booking_date: when the booking was made
    # status: current status of the booking (confirmed/cancelled)
    booking_id: str
    passenger_id: str
    flight_id: str
    booking_date: datetime
    status: str = "confirmed"
    
    def __post_init__(self) -> None:
        # Basic null checks only in MVP
        if not self.booking_id or not self.passenger_id or not self.flight_id:
            raise ValueError("Booking ID, passenger ID, and flight ID are required")
        if self.status not in ["confirmed", "cancelled"]:
            raise ValueError("Status must be 'confirmed' or 'cancelled'")
        # Extension point: add booking_validation() post-MVP (Business Rule Pattern)


# ============================================================================
# PART 1: MVP REPOSITORIES (Minimal Interface with Specific Names)
# ============================================================================

# MVP Repository Interface (only 4 methods max with targeted names)
class BaseRepository(ABC):
    """Abstract base repository for all entities"""
    
    @abstractmethod
    def save_entity_to_storage(self, entity) -> None:
        """Save entity to storage"""
        pass
    
    @abstractmethod
    def find_entity_by_unique_id(self, id: str):
        """Find entity by its unique ID"""
        pass
    
    @abstractmethod
    def retrieve_all_entities_from_storage(self) -> List:
        """Retrieve all entities from storage"""
        pass
    
    @abstractmethod
    def remove_entity_by_id(self, id: str) -> bool:
        """Remove entity by ID, return success status"""
        pass


class InMemoryUserRepository(BaseRepository):
    """In-memory implementation of user repository"""
    
    def __init__(self) -> None:
        self._users: Dict[str, User] = {}
        self._lock = threading.Lock()  # Thread safety for MVP
    
    def save_entity_to_storage(self, user: User) -> None:
        with self._lock:
            self._users[user.user_id] = user
    
    def find_entity_by_unique_id(self, user_id: str) -> Optional[User]:
        with self._lock:
            return self._users.get(user_id)
    
    def retrieve_all_entities_from_storage(self) -> List[User]:
        with self._lock:
            return list(self._users.values())
    
    def remove_entity_by_id(self, user_id: str) -> bool:
        with self._lock:
            if user_id in self._users:
                del self._users[user_id]
                return True
            return False


class InMemoryFlightRepository(BaseRepository):
    """In-memory implementation of flight repository"""
    
    def __init__(self) -> None:
        self._flights: Dict[str, Flight] = {}
        self._lock = threading.Lock()  # Thread safety for MVP
    
    def save_entity_to_storage(self, flight: Flight) -> None:
        with self._lock:
            self._flights[flight.flight_id] = flight
    
    def find_entity_by_unique_id(self, flight_id: str) -> Optional[Flight]:
        with self._lock:
            return self._flights.get(flight_id)
    
    def retrieve_all_entities_from_storage(self) -> List[Flight]:
        with self._lock:
            return list(self._flights.values())
    
    def remove_entity_by_id(self, flight_id: str) -> bool:
        with self._lock:
            if flight_id in self._flights:
                del self._flights[flight_id]
                return True
            return False
    
    def find_flights_by_source_and_destination(self, source: str, destination: str) -> List[Flight]:
        """Find flights by source and destination airports"""
        with self._lock:
            return [
                flight for flight in self._flights.values()
                if flight.source.lower() == source.lower() and flight.destination.lower() == destination.lower()
            ]


class InMemoryPassengerRepository(BaseRepository):
    """In-memory implementation of passenger repository"""
    
    def __init__(self) -> None:
        self._passengers: Dict[str, Passenger] = {}
        self._lock = threading.Lock()  # Thread safety for MVP
    
    def save_entity_to_storage(self, passenger: Passenger) -> None:
        with self._lock:
            self._passengers[passenger.passenger_id] = passenger
    
    def find_entity_by_unique_id(self, passenger_id: str) -> Optional[Passenger]:
        with self._lock:
            return self._passengers.get(passenger_id)
    
    def retrieve_all_entities_from_storage(self) -> List[Passenger]:
        with self._lock:
            return list(self._passengers.values())
    
    def remove_entity_by_id(self, passenger_id: str) -> bool:
        with self._lock:
            if passenger_id in self._passengers:
                del self._passengers[passenger_id]
                return True
            return False


class InMemoryBookingRepository(BaseRepository):
    """In-memory implementation of booking repository"""
    
    def __init__(self) -> None:
        self._bookings: Dict[str, Booking] = {}
        self._lock = threading.Lock()  # Thread safety for MVP
    
    def save_entity_to_storage(self, booking: Booking) -> None:
        with self._lock:
            self._bookings[booking.booking_id] = booking
    
    def find_entity_by_unique_id(self, booking_id: str) -> Optional[Booking]:
        with self._lock:
            return self._bookings.get(booking_id)
    
    def retrieve_all_entities_from_storage(self) -> List[Booking]:
        with self._lock:
            return list(self._bookings.values())
    
    def remove_entity_by_id(self, booking_id: str) -> bool:
        with self._lock:
            if booking_id in self._bookings:
                del self._bookings[booking_id]
                return True
            return False


# ============================================================================
# PART 1: MVP MANAGERS (2-3 Core Operations Max)
# ============================================================================

# Design Pattern: Application Service / Service Layer
# Purpose: Coordinate business workflows across multiple repositories
# Implementation: Stateless service with dependency injection
# Trade-offs: Clear separation of concerns vs potential over-abstraction

class UserManager:
    """Manager for user-related operations"""
    
    def __init__(self, user_repo: InMemoryUserRepository) -> None:
        self._user_repo = user_repo
    
    def _validate_user_inputs(self, user_id: str, name: str, email: str) -> None:
        """Validate user input parameters"""
        if not user_id or not user_id.strip():
            raise ValidationError("user_id", "User ID cannot be empty")
        if not name or not name.strip():
            raise ValidationError("name", "Name cannot be empty")
        if not email or not email.strip():
            raise ValidationError("email", "Email cannot be empty")
        
        # Basic email validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("email", "Invalid email format")
    
    def register_new_user_in_system(self, user_id: str, name: str, email: str) -> str:
        """Register a new user in the system"""
        # Input validation
        self._validate_user_inputs(user_id, name, email)
        
        # Check if user already exists
        existing_user = self._user_repo.find_entity_by_unique_id(user_id)
        if existing_user:
            raise EntityAlreadyExistsError("User", user_id)
        
        # Create and save user
        user = User(user_id=user_id, name=name, email=email)
        self._user_repo.save_entity_to_storage(user)
        return user_id
    
    def retrieve_user_with_business_rules(self, user_id: str) -> Optional[User]:
        """Retrieve user by ID with basic business rules"""
        if not user_id or not user_id.strip():
            raise ValidationError("user_id", "User ID cannot be empty")
        
        user = self._user_repo.find_entity_by_unique_id(user_id)
        if not user:
            raise EntityNotFoundError("User", user_id)
        
        return user
    
    # Extension point: add complex_business_workflow() post-MVP (Command Pattern)


class FlightManager:
    """Manager for flight-related operations"""
    
    def __init__(self, flight_repo: InMemoryFlightRepository) -> None:
        self._flight_repo = flight_repo
    
    def _validate_flight_inputs(self, flight_id: str, flight_number: str, 
                               source: str, destination: str, capacity: int) -> None:
        """Validate flight input parameters"""
        if not flight_id or not flight_id.strip():
            raise ValidationError("flight_id", "Flight ID cannot be empty")
        if not flight_number or not flight_number.strip():
            raise ValidationError("flight_number", "Flight number cannot be empty")
        if not source or not source.strip():
            raise ValidationError("source", "Source airport cannot be empty")
        if not destination or not destination.strip():
            raise ValidationError("destination", "Destination airport cannot be empty")
        if capacity <= 0:
            raise ValidationError("capacity", "Capacity must be positive")
        
        # Basic airport code validation (3 letters)
        if len(source) != 3 or not source.isalpha():
            raise ValidationError("source", "Source must be a 3-letter airport code")
        if len(destination) != 3 or not destination.isalpha():
            raise ValidationError("destination", "Destination must be a 3-letter airport code")
    
    def add_new_flight_to_system(self, flight_id: str, flight_number: str, 
                                source: str, destination: str, capacity: int) -> str:
        """Add a new flight to the system"""
        # Input validation
        self._validate_flight_inputs(flight_id, flight_number, source, destination, capacity)
        
        # Check if flight already exists
        existing_flight = self._flight_repo.find_entity_by_unique_id(flight_id)
        if existing_flight:
            raise EntityAlreadyExistsError("Flight", flight_id)
        
        # Create and save flight
        flight = Flight(flight_id=flight_id, flight_number=flight_number,
                       source=source, destination=destination, capacity=capacity)
        self._flight_repo.save_entity_to_storage(flight)
        return flight_id
    
    def retrieve_flight_with_business_rules(self, flight_id: str) -> Optional[Flight]:
        """Retrieve flight by ID with basic business rules"""
        if not flight_id or not flight_id.strip():
            raise ValidationError("flight_id", "Flight ID cannot be empty")
        
        flight = self._flight_repo.find_entity_by_unique_id(flight_id)
        if not flight:
            raise EntityNotFoundError("Flight", flight_id)
        
        return flight
    
    def get_all_available_flights_from_system(self) -> List[Flight]:
        """Get all flights available in the system"""
        return self._flight_repo.retrieve_all_entities_from_storage()
    
    def search_flights_by_route(self, source: str, destination: str) -> List[Flight]:
        """Search flights by source and destination route"""
        # Input validation
        if not source or not source.strip():
            raise ValidationError("source", "Source airport cannot be empty")
        if not destination or not destination.strip():
            raise ValidationError("destination", "Destination airport cannot be empty")
        
        # Pattern: Specification Pattern (extension point for complex queries)
        return self._flight_repo.find_flights_by_source_and_destination(source, destination)


class PassengerManager:
    """Manager for passenger-related operations"""
    
    def __init__(self, passenger_repo: InMemoryPassengerRepository) -> None:
        self._passenger_repo = passenger_repo
    
    def _validate_passenger_inputs(self, passenger_id: str, user_id: str, 
                                  name: str, passport_number: str) -> None:
        """Validate passenger input parameters"""
        if not passenger_id or not passenger_id.strip():
            raise ValidationError("passenger_id", "Passenger ID cannot be empty")
        if not user_id or not user_id.strip():
            raise ValidationError("user_id", "User ID cannot be empty")
        if not name or not name.strip():
            raise ValidationError("name", "Passenger name cannot be empty")
        if not passport_number or not passport_number.strip():
            raise ValidationError("passport_number", "Passport number cannot be empty")
        
        # Basic passport number validation (alphanumeric, 6-9 characters)
        if not re.match(r'^[A-Z0-9]{6,9}$', passport_number):
            raise ValidationError("passport_number", "Passport number must be 6-9 alphanumeric characters")
    
    def register_new_passenger_for_user(self, passenger_id: str, user_id: str, 
                                       name: str, passport_number: str) -> str:
        """Register a new passenger for a user"""
        # Input validation
        self._validate_passenger_inputs(passenger_id, user_id, name, passport_number)
        
        # Check if passenger already exists
        existing_passenger = self._passenger_repo.find_entity_by_unique_id(passenger_id)
        if existing_passenger:
            raise EntityAlreadyExistsError("Passenger", passenger_id)
        
        # Create and save passenger
        passenger = Passenger(passenger_id=passenger_id, user_id=user_id,
                             name=name, passport_number=passport_number)
        self._passenger_repo.save_entity_to_storage(passenger)
        return passenger_id
    
    def retrieve_passenger_with_business_rules(self, passenger_id: str) -> Optional[Passenger]:
        """Retrieve passenger by ID with basic business rules"""
        if not passenger_id or not passenger_id.strip():
            raise ValidationError("passenger_id", "Passenger ID cannot be empty")
        
        passenger = self._passenger_repo.find_entity_by_unique_id(passenger_id)
        if not passenger:
            raise EntityNotFoundError("Passenger", passenger_id)
        
        return passenger


class BookingManager:
    """Manager for booking-related operations"""
    
    def __init__(self, booking_repo: InMemoryBookingRepository,
                 passenger_repo: InMemoryPassengerRepository,
                 flight_repo: InMemoryFlightRepository) -> None:
        self._booking_repo = booking_repo
        self._passenger_repo = passenger_repo
        self._flight_repo = flight_repo
    
    def _validate_booking_inputs(self, booking_id: str, passenger_id: str, flight_id: str) -> None:
        """Validate booking input parameters"""
        if not booking_id or not booking_id.strip():
            raise ValidationError("booking_id", "Booking ID cannot be empty")
        if not passenger_id or not passenger_id.strip():
            raise ValidationError("passenger_id", "Passenger ID cannot be empty")
        if not flight_id or not flight_id.strip():
            raise ValidationError("flight_id", "Flight ID cannot be empty")
    
    def _validate_booking_business_rules(self, passenger_id: str, flight_id: str) -> None:
        """Validate booking business rules"""
        # Check if passenger exists
        passenger = self._passenger_repo.find_entity_by_unique_id(passenger_id)
        if not passenger:
            raise EntityNotFoundError("Passenger", passenger_id)
        
        # Check if flight exists
        flight = self._flight_repo.find_entity_by_unique_id(flight_id)
        if not flight:
            raise EntityNotFoundError("Flight", flight_id)
        
        # Check if passenger already has a booking for this flight
        existing_bookings = self.get_all_bookings_for_passenger(passenger_id)
        for booking in existing_bookings:
            if booking.flight_id == flight_id and booking.status == "confirmed":
                raise InvalidBookingError(f"Passenger {passenger_id} already has a confirmed booking for flight {flight_id}")
    
    def create_new_booking_for_passenger(self, booking_id: str, passenger_id: str, 
                                        flight_id: str) -> str:
        """Create a new booking for a passenger"""
        # Input validation
        self._validate_booking_inputs(booking_id, passenger_id, flight_id)
        
        # Check if booking already exists
        existing_booking = self._booking_repo.find_entity_by_unique_id(booking_id)
        if existing_booking:
            raise EntityAlreadyExistsError("Booking", booking_id)
        
        # Business rule validation
        self._validate_booking_business_rules(passenger_id, flight_id)
        
        # Create and save booking
        booking = Booking(booking_id=booking_id, passenger_id=passenger_id,
                         flight_id=flight_id, booking_date=datetime.now())
        self._booking_repo.save_entity_to_storage(booking)
        return booking_id
    
    def retrieve_booking_with_business_rules(self, booking_id: str) -> Optional[Booking]:
        """Retrieve booking by ID with basic business rules"""
        if not booking_id or not booking_id.strip():
            raise ValidationError("booking_id", "Booking ID cannot be empty")
        
        booking = self._booking_repo.find_entity_by_unique_id(booking_id)
        if not booking:
            raise EntityNotFoundError("Booking", booking_id)
        
        return booking
    
    def get_all_bookings_for_passenger(self, passenger_id: str) -> List[Booking]:
        """Get all bookings for a specific passenger"""
        if not passenger_id or not passenger_id.strip():
            raise ValidationError("passenger_id", "Passenger ID cannot be empty")
        
        all_bookings = self._booking_repo.retrieve_all_entities_from_storage()
        return [booking for booking in all_bookings if booking.passenger_id == passenger_id]
    
    def get_all_bookings_for_user(self, user_id: str) -> List[Booking]:
        """Get all bookings for a specific user (across all their passengers)"""
        if not user_id or not user_id.strip():
            raise ValidationError("user_id", "User ID cannot be empty")
        
        # Get all passengers for this user
        all_passengers = self._passenger_repo.retrieve_all_entities_from_storage()
        user_passenger_ids = [p.passenger_id for p in all_passengers if p.user_id == user_id]
        
        if not user_passenger_ids:
            return []  # User has no passengers
        
        # Get all bookings for these passengers
        all_bookings = self._booking_repo.retrieve_all_entities_from_storage()
        return [booking for booking in all_bookings if booking.passenger_id in user_passenger_ids]


# ============================================================================
# PART 1: MVP ORCHESTRATOR (Demo Only)
# ============================================================================

class FlightReservationSystem:
    """System orchestrator for flight reservation operations"""
    
    def __init__(self) -> None:
        # Initialize repositories
        self.user_repo = InMemoryUserRepository()
        self.flight_repo = InMemoryFlightRepository()
        self.passenger_repo = InMemoryPassengerRepository()
        self.booking_repo = InMemoryBookingRepository()
        
        # Initialize managers
        self.user_manager = UserManager(self.user_repo)
        self.flight_manager = FlightManager(self.flight_repo)
        self.passenger_manager = PassengerManager(self.passenger_repo)
        self.booking_manager = BookingManager(self.booking_repo, self.passenger_repo, self.flight_repo)
    
    def demonstrate_complete_user_journey(self) -> None:
        """Demonstrate a complete user journey from registration to booking"""
        print("=== Flight Reservation System - MVP Demo ===")
        
        # Step 1: Register a user
        print("\n1. Registering a new user...")
        try:
            user_id = self.user_manager.register_new_user_in_system(
                user_id="U001", name="John Doe", email="john@example.com"
            )
            print(f"   User registered with ID: {user_id}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 2: Add flights
        print("\n2. Adding flights to the system...")
        try:
            flight_id1 = self.flight_manager.add_new_flight_to_system(
                flight_id="F001", flight_number="AA123", 
                source="JFK", destination="LAX", capacity=150
            )
            flight_id2 = self.flight_manager.add_new_flight_to_system(
                flight_id="F002", flight_number="UA456", 
                source="JFK", destination="LAX", capacity=200
            )
            flight_id3 = self.flight_manager.add_new_flight_to_system(
                flight_id="F003", flight_number="DL789", 
                source="JFK", destination="ORD", capacity=180
            )
            print(f"   Flights added: {flight_id1}, {flight_id2}, {flight_id3}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 3: Search for flights
        print("\n3. Searching for flights from JFK to LAX...")
        try:
            search_results = self.flight_manager.search_flights_by_route("JFK", "LAX")
            print(f"   Found {len(search_results)} flights:")
            for flight in search_results:
                print(f"     Flight {flight.flight_number}: {flight.source} → {flight.destination} (Capacity: {flight.capacity})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 4: Register passengers for the user
        print("\n4. Registering passengers...")
        try:
            passenger_id1 = self.passenger_manager.register_new_passenger_for_user(
                passenger_id="P001", user_id="U001", 
                name="John Doe", passport_number="US123456"
            )
            passenger_id2 = self.passenger_manager.register_new_passenger_for_user(
                passenger_id="P002", user_id="U001", 
                name="Jane Doe", passport_number="US789012"
            )
            print(f"   Passengers registered with IDs: {passenger_id1}, {passenger_id2}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 5: Create bookings
        print("\n5. Creating bookings...")
        try:
            booking_id1 = self.booking_manager.create_new_booking_for_passenger(
                booking_id="B001", passenger_id="P001", flight_id="F001"
            )
            booking_id2 = self.booking_manager.create_new_booking_for_passenger(
                booking_id="B002", passenger_id="P002", flight_id="F002"
            )
            print(f"   Bookings created with IDs: {booking_id1}, {booking_id2}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 6: View bookings for individual passengers
        print("\n6. Viewing bookings for individual passengers...")
        try:
            bookings_p1 = self.booking_manager.get_all_bookings_for_passenger("P001")
            print(f"   Passenger P001 has {len(bookings_p1)} bookings:")
            for booking in bookings_p1:
                flight = self.flight_manager.retrieve_flight_with_business_rules(booking.flight_id)
                print(f"     Booking {booking.booking_id}: Flight {flight.flight_number} "
                      f"({flight.source} → {flight.destination}) - Status: {booking.status}")
            
            bookings_p2 = self.booking_manager.get_all_bookings_for_passenger("P002")
            print(f"   Passenger P002 has {len(bookings_p2)} bookings:")
            for booking in bookings_p2:
                flight = self.flight_manager.retrieve_flight_with_business_rules(booking.flight_id)
                print(f"     Booking {booking.booking_id}: Flight {flight.flight_number} "
                      f"({flight.source} → {flight.destination}) - Status: {booking.status}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 7: View all bookings for the user
        print("\n7. Viewing all bookings for user...")
        try:
            user_bookings = self.booking_manager.get_all_bookings_for_user("U001")
            print(f"   User U001 has {len(user_bookings)} total bookings:")
            for booking in user_bookings:
                flight = self.flight_manager.retrieve_flight_with_business_rules(booking.flight_id)
                passenger = self.passenger_manager.retrieve_passenger_with_business_rules(booking.passenger_id)
                print(f"     Booking {booking.booking_id}: {passenger.name} on Flight {flight.flight_number} "
                      f"({flight.source} → {flight.destination}) - Status: {booking.status}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Step 8: Demonstrate error handling
        print("\n8. Demonstrating error handling...")
        
        # Try to register duplicate user
        try:
            self.user_manager.register_new_user_in_system(
                user_id="U001", name="John Doe", email="john@example.com"
            )
        except Exception as e:
            print(f"   Expected error (duplicate user): {e}")
        
        # Try to create booking with invalid passenger
        try:
            self.booking_manager.create_new_booking_for_passenger(
                booking_id="B002", passenger_id="P999", flight_id="F001"
            )
        except Exception as e:
            print(f"   Expected error (invalid passenger): {e}")
        
        # Try to search with invalid airport code
        try:
            self.flight_manager.search_flights_by_route("", "LAX")
        except Exception as e:
            print(f"   Expected error (invalid source): {e}")
        
        print("\n=== Demo Complete ===")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Create and run the system demo
    system = FlightReservationSystem()
    system.demonstrate_complete_user_journey()