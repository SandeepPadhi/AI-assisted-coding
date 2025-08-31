"""
Unit tests for Flight Reservation System MVP

Design Pattern: Test Fixture Pattern
Purpose: Verify core functionality with isolated test cases
Implementation: Arrange-Act-Assert pattern with setup/teardown
Trade-offs: Test coverage vs maintenance overhead

Focus on 3-4 most crucial MVP functions:
1. User registration (core entity creation)
2. Flight booking (core business operation)
3. Flight search (core query functionality)
4. Error handling (validation and business rules)
"""

import unittest
from datetime import datetime
from typing import List

from main import (
    User, Flight, Passenger, Booking,
    InMemoryUserRepository, InMemoryFlightRepository, 
    InMemoryPassengerRepository, InMemoryBookingRepository,
    UserManager, FlightManager, PassengerManager, BookingManager
)
from exceptions import (
    EntityNotFoundError, EntityAlreadyExistsError, 
    InvalidBookingError, ValidationError
)


class TestFlightReservationMVP(unittest.TestCase):
    """Test suite for Flight Reservation System MVP core functions"""
    
    def setUp(self) -> None:
        """Set up test fixtures before each test method"""
        # Initialize repositories
        self.user_repo = InMemoryUserRepository()
        self.flight_repo = InMemoryFlightRepository()
        self.passenger_repo = InMemoryPassengerRepository()
        self.booking_repo = InMemoryBookingRepository()
        
        # Initialize managers
        self.user_manager = UserManager(self.user_repo)
        self.flight_manager = FlightManager(self.flight_repo)
        self.passenger_manager = PassengerManager(self.passenger_repo)
        self.booking_manager = BookingManager(
            self.booking_repo, self.passenger_repo, self.flight_repo
        )
    
    def tearDown(self) -> None:
        """Clean up after each test method"""
        # Repositories are in-memory, so no cleanup needed
        pass
    
    def test_user_registration_success(self) -> None:
        """Test successful user registration - core entity creation"""
        # Arrange
        user_id = "U001"
        name = "John Doe"
        email = "john@example.com"
        
        # Act
        result_id = self.user_manager.register_new_user_in_system(user_id, name, email)
        
        # Assert
        self.assertEqual(result_id, user_id)
        user = self.user_repo.find_entity_by_unique_id(user_id)
        self.assertIsNotNone(user)
        self.assertEqual(user.name, name)
        self.assertEqual(user.email, email)
    
    def test_user_registration_duplicate_error(self) -> None:
        """Test user registration with duplicate ID - error handling"""
        # Arrange
        user_id = "U001"
        name = "John Doe"
        email = "john@example.com"
        
        # Act - Register first user
        self.user_manager.register_new_user_in_system(user_id, name, email)
        
        # Act & Assert - Try to register duplicate
        with self.assertRaises(EntityAlreadyExistsError) as context:
            self.user_manager.register_new_user_in_system(user_id, name, email)
        
        self.assertIn("User with ID 'U001' already exists", str(context.exception))
    
    def test_flight_booking_success(self) -> None:
        """Test successful flight booking - core business operation"""
        # Arrange - Create prerequisites
        user_id = self.user_manager.register_new_user_in_system("U001", "John Doe", "john@example.com")
        flight_id = self.flight_manager.add_new_flight_to_system("F001", "AA123", "JFK", "LAX", 150)
        passenger_id = self.passenger_manager.register_new_passenger_for_user("P001", "U001", "John Doe", "US123456")
        
        # Act
        booking_id = self.booking_manager.create_new_booking_for_passenger("B001", passenger_id, flight_id)
        
        # Assert
        self.assertEqual(booking_id, "B001")
        booking = self.booking_repo.find_entity_by_unique_id(booking_id)
        self.assertIsNotNone(booking)
        self.assertEqual(booking.passenger_id, passenger_id)
        self.assertEqual(booking.flight_id, flight_id)
        self.assertEqual(booking.status, "confirmed")
    
    def test_flight_search_functionality(self) -> None:
        """Test flight search by route - core query functionality"""
        # Arrange - Add multiple flights
        self.flight_manager.add_new_flight_to_system("F001", "AA123", "JFK", "LAX", 150)
        self.flight_manager.add_new_flight_to_system("F002", "UA456", "JFK", "LAX", 200)
        self.flight_manager.add_new_flight_to_system("F003", "DL789", "JFK", "ORD", 180)
        
        # Act
        search_results = self.flight_manager.search_flights_by_route("JFK", "LAX")
        
        # Assert
        self.assertEqual(len(search_results), 2)
        flight_numbers = [flight.flight_number for flight in search_results]
        self.assertIn("AA123", flight_numbers)
        self.assertIn("UA456", flight_numbers)
        self.assertNotIn("DL789", flight_numbers)  # Different route
    
    def test_booking_with_invalid_passenger_error(self) -> None:
        """Test booking with non-existent passenger - business rule validation"""
        # Arrange - Create flight but no passenger
        flight_id = self.flight_manager.add_new_flight_to_system("F001", "AA123", "JFK", "LAX", 150)
        
        # Act & Assert - Try to book with invalid passenger
        with self.assertRaises(EntityNotFoundError) as context:
            self.booking_manager.create_new_booking_for_passenger("B001", "P999", flight_id)
        
        self.assertIn("Passenger with ID 'P999' not found", str(context.exception))
    
    def test_duplicate_booking_prevention(self) -> None:
        """Test prevention of duplicate bookings - business rule validation"""
        # Arrange - Create booking
        user_id = self.user_manager.register_new_user_in_system("U001", "John Doe", "john@example.com")
        flight_id = self.flight_manager.add_new_flight_to_system("F001", "AA123", "JFK", "LAX", 150)
        passenger_id = self.passenger_manager.register_new_passenger_for_user("P001", "U001", "John Doe", "US123456")
        
        # Act - Create first booking
        self.booking_manager.create_new_booking_for_passenger("B001", passenger_id, flight_id)
        
        # Act & Assert - Try to create duplicate booking
        with self.assertRaises(InvalidBookingError) as context:
            self.booking_manager.create_new_booking_for_passenger("B002", passenger_id, flight_id)
        
        self.assertIn("already has a confirmed booking", str(context.exception))
    
    def test_invalid_email_validation(self) -> None:
        """Test email validation - input validation"""
        # Act & Assert - Try to register with invalid email
        with self.assertRaises(ValidationError) as context:
            self.user_manager.register_new_user_in_system("U001", "John Doe", "invalid-email")
        
        self.assertIn("Invalid email format", str(context.exception))
    
    def test_get_all_bookings_for_user(self) -> None:
        """Test getting all bookings for a user - user booking view functionality"""
        # Arrange - Create user with multiple passengers and bookings
        self.user_manager.register_new_user_in_system("U001", "John Doe", "john@example.com")
        self.flight_manager.add_new_flight_to_system("F001", "AA123", "JFK", "LAX", 150)
        self.flight_manager.add_new_flight_to_system("F002", "UA456", "JFK", "ORD", 200)
        
        # Create multiple passengers for the user
        self.passenger_manager.register_new_passenger_for_user("P001", "U001", "John Doe", "US123456")
        self.passenger_manager.register_new_passenger_for_user("P002", "U001", "Jane Doe", "US789012")
        
        # Create bookings for different passengers
        self.booking_manager.create_new_booking_for_passenger("B001", "P001", "F001")
        self.booking_manager.create_new_booking_for_passenger("B002", "P002", "F002")
        
        # Act
        user_bookings = self.booking_manager.get_all_bookings_for_user("U001")
        
        # Assert
        self.assertEqual(len(user_bookings), 2)
        booking_ids = [booking.booking_id for booking in user_bookings]
        self.assertIn("B001", booking_ids)
        self.assertIn("B002", booking_ids)


def run_mvp_tests() -> None:
    """Run the MVP test suite and display results"""
    print("=== Flight Reservation System - MVP Unit Tests ===")
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestFlightReservationMVP)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Display summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n=== Failures ===")
        for test, traceback in result.failures:
            print(f"FAIL: {test}")
            print(traceback)
    
    if result.errors:
        print(f"\n=== Errors ===")
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(traceback)
    
    if result.wasSuccessful():
        print(f"\n✅ All MVP tests passed!")
    else:
        print(f"\n❌ Some tests failed!")


if __name__ == "__main__":
    run_mvp_tests()
