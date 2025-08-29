"""
Unit Tests for Ride Sharing Application
Tests focus on the most critical business functions
"""

import unittest
from entities import User, Driver, Trip, Location, CreditCardPayment, UPIPayment, CashPayment, TripStatus
from repositories import InMemoryUserRepository, InMemoryDriverRepository, InMemoryTripRepository, InMemoryPaymentRepository, InMemoryBillRepository
from managers import UserManager, DriverManager, TripManager, PaymentManager, BillManager
from orchestrator import RideSharingAppSystem


class TestUserManagement(unittest.TestCase):
    """Test user registration and management"""

    def setUp(self):
        self.user_repo = InMemoryUserRepository()
        self.user_manager = UserManager(self.user_repo)

    def test_user_registration_success(self):
        """Test successful user registration"""
        user = self.user_manager.create_user("user001", "John Doe", "john@example.com", "1234567890")

        self.assertEqual(user.user_id, "user001")
        self.assertEqual(user.name, "John Doe")
        self.assertEqual(user.email, "john@example.com")
        self.assertTrue(user.validate_user_data())

    def test_user_registration_failure_invalid_data(self):
        """Test user registration with invalid data"""
        with self.assertRaises(ValueError):
            self.user_manager.create_user("", "", "", "")  # Empty data

    def test_get_user_by_id(self):
        """Test retrieving user by ID"""
        user = self.user_manager.create_user("user001", "John Doe", "john@example.com", "1234567890")
        retrieved_user = self.user_manager.get_user("user001")

        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_id, user.user_id)
        self.assertEqual(retrieved_user.name, user.name)

    def test_get_nonexistent_user(self):
        """Test retrieving non-existent user"""
        user = self.user_manager.get_user("nonexistent")
        self.assertIsNone(user)


class TestDriverManagement(unittest.TestCase):
    """Test driver registration and management"""

    def setUp(self):
        self.driver_repo = InMemoryDriverRepository()
        self.driver_manager = DriverManager(self.driver_repo)

    def test_driver_registration_success(self):
        """Test successful driver registration"""
        driver = self.driver_manager.create_driver("driver001", "Bob Wilson", "bob@example.com", "5551234567", "DL123456")

        self.assertEqual(driver.driver_id, "driver001")
        self.assertEqual(driver.name, "Bob Wilson")
        self.assertEqual(driver.license_number, "DL123456")
        self.assertTrue(driver.is_available)
        self.assertEqual(driver.rating, 5.0)

    def test_driver_availability_update(self):
        """Test driver availability updates"""
        driver = self.driver_manager.create_driver("driver001", "Bob Wilson", "bob@example.com", "5551234567", "DL123456")

        # Initially available
        self.assertTrue(driver.is_available)

        # Update to unavailable
        self.driver_manager.update_driver_availability("driver001", False)
        updated_driver = self.driver_manager.get_driver("driver001")
        self.assertFalse(updated_driver.is_available)

    def test_driver_rating_update(self):
        """Test driver rating updates"""
        driver = self.driver_manager.create_driver("driver001", "Bob Wilson", "bob@example.com", "5551234567", "DL123456")

        # Initial rating
        self.assertEqual(driver.rating, 5.0)

        # Update rating
        self.driver_manager.update_driver_rating("driver001", 4.0)
        updated_driver = self.driver_manager.get_driver("driver001")
        self.assertEqual(updated_driver.rating, 4.0)  # First rating becomes the new rating


class TestTripLifecycle(unittest.TestCase):
    """Test complete trip lifecycle"""

    def setUp(self):
        self.trip_repo = InMemoryTripRepository()
        self.trip_manager = TripManager(self.trip_repo)

    def test_trip_request_creation(self):
        """Test creating a trip request"""
        pickup = Location(37.7749, -122.4194)
        dropoff = Location(37.7849, -122.4094)

        trip = self.trip_manager.create_trip_request("trip001", "user001", pickup, dropoff)

        self.assertEqual(trip.trip_id, "trip001")
        self.assertEqual(trip.user_id, "user001")
        self.assertEqual(trip.status, TripStatus.REQUESTED)
        self.assertIsNotNone(trip.pickup_location)
        self.assertIsNotNone(trip.dropoff_location)

    def test_trip_acceptance(self):
        """Test accepting a trip request"""
        pickup = Location(37.7749, -122.4194)
        dropoff = Location(37.7849, -122.4094)

        trip = self.trip_manager.create_trip_request("trip001", "user001", pickup, dropoff)
        self.assertEqual(trip.status, TripStatus.REQUESTED)

        # Accept trip
        success = self.trip_manager.accept_trip("trip001", "driver001")
        self.assertTrue(success)

        # Check updated trip
        updated_trip = self.trip_manager.get_trip("trip001")
        self.assertEqual(updated_trip.status, TripStatus.ACCEPTED)
        self.assertEqual(updated_trip.driver_id, "driver001")
        self.assertIsNotNone(updated_trip.accepted_at)

    def test_trip_completion(self):
        """Test completing a trip"""
        pickup = Location(37.7749, -122.4194)
        dropoff = Location(37.7849, -122.4094)

        trip = self.trip_manager.create_trip_request("trip001", "user001", pickup, dropoff)
        self.trip_manager.accept_trip("trip001", "driver001")
        self.trip_manager.start_trip("trip001")

        # Complete trip
        success = self.trip_manager.complete_trip("trip001", 10.0, 18.50)
        self.assertTrue(success)

        # Check completed trip
        completed_trip = self.trip_manager.get_trip("trip001")
        self.assertEqual(completed_trip.status, TripStatus.COMPLETED)
        self.assertEqual(completed_trip.distance_km, 10.0)
        self.assertEqual(completed_trip.fare_amount, 18.50)
        self.assertIsNotNone(completed_trip.completed_at)


class TestPaymentProcessing(unittest.TestCase):
    """Test payment processing with different methods"""

    def setUp(self):
        self.payment_repo = InMemoryPaymentRepository()
        self.payment_manager = PaymentManager(self.payment_repo)

    def test_credit_card_payment_creation(self):
        """Test creating credit card payment"""
        payment = self.payment_manager.create_credit_card_payment(
            "pay001", "trip001", 25.50,
            "4111111111111111", "12/25", "123", "John Doe"
        )

        self.assertEqual(payment.payment_id, "pay001")
        self.assertEqual(payment.trip_id, "trip001")
        self.assertEqual(payment.amount, 25.50)
        self.assertEqual(payment.payment_method, "credit_card")
        self.assertEqual(payment.card_holder_name, "John Doe")

    def test_credit_card_payment_validation(self):
        """Test credit card payment validation"""
        # Valid payment
        payment = CreditCardPayment(
            "pay001", "trip001", 25.50,
            "4111111111111111", "12/25", "123", "John Doe"
        )
        self.assertTrue(payment.validate_payment_data())

        # Invalid card number (too short)
        invalid_payment = CreditCardPayment(
            "pay002", "trip001", 25.50,
            "4111", "12/25", "123", "John Doe"
        )
        self.assertFalse(invalid_payment.validate_payment_data())

    def test_upi_payment_creation(self):
        """Test creating UPI payment"""
        payment = self.payment_manager.create_upi_payment(
            "pay002", "trip001", 25.50, "john@paytm", "gpay"
        )

        self.assertEqual(payment.payment_id, "pay002")
        self.assertEqual(payment.upi_id, "john@paytm")
        self.assertEqual(payment.upi_app, "gpay")
        self.assertEqual(payment.payment_method, "upi")

    def test_cash_payment_creation(self):
        """Test creating cash payment"""
        payment = self.payment_manager.create_cash_payment("pay003", "trip001", 25.50)

        self.assertEqual(payment.payment_id, "pay003")
        self.assertEqual(payment.amount, 25.50)
        self.assertEqual(payment.payment_method, "cash")

    def test_payment_processing_simulation(self):
        """Test payment processing (simulated)"""
        payment = CashPayment("pay001", "trip001", 25.50)

        # Process payment
        result = payment.process_payment()
        self.assertTrue(result)
        self.assertEqual(payment.status, "completed")
        self.assertIsNotNone(payment.processed_at)


class TestBillGeneration(unittest.TestCase):
    """Test bill generation and calculations"""

    def setUp(self):
        self.bill_repo = InMemoryBillRepository()
        self.bill_manager = BillManager(self.bill_repo)

    def test_bill_generation(self):
        """Test bill generation with correct calculations"""
        bill = self.bill_manager.generate_bill("bill001", "trip001", "user001", "driver001", 10.0)

        self.assertEqual(bill.bill_id, "bill001")
        self.assertEqual(bill.trip_id, "trip001")
        self.assertEqual(bill.user_id, "user001")
        self.assertEqual(bill.driver_id, "driver001")

        # Check calculations (base_fare=2.0, per_km_rate=1.5, tax_rate=0.1)
        expected_base = 2.0
        expected_distance = 10.0 * 1.5
        expected_subtotal = expected_base + expected_distance
        expected_tax = expected_subtotal * 0.1
        expected_total = expected_subtotal + expected_tax

        self.assertEqual(bill.base_fare, expected_base)
        self.assertEqual(bill.distance_fare, expected_distance)
        self.assertEqual(bill.tax_amount, expected_tax)
        self.assertEqual(bill.total_amount, expected_total)


class TestRideSharingAppIntegration(unittest.TestCase):
    """Test end-to-end integration scenarios"""

    def setUp(self):
        self.system = RideSharingAppSystem()

    def test_complete_ride_flow(self):
        """Test complete ride flow from request to payment"""
        # Register user and driver
        user = self.system.register_user("John Doe", "john@example.com", "1234567890")
        driver = self.system.register_driver("Bob Wilson", "bob@example.com", "5551234567", "DL123456")
        self.system.register_vehicle_for_driver(driver.driver_id, "Toyota", "Camry", 2020, "ABC123")

        # Request and accept ride
        trip = self.system.request_ride(user.user_id, 37.7749, -122.4194, 37.7849, -122.4094)
        self.system.accept_ride(trip.trip_id, driver.driver_id)

        # Start and complete ride
        self.system.start_ride(trip.trip_id)
        success = self.system.complete_ride(trip.trip_id, 5.0)
        self.assertTrue(success)

        # Pay with cash
        payment_success = self.system.pay_with_cash(trip.trip_id)
        self.assertTrue(payment_success)

        # Check bill
        bill = self.system.get_trip_bill(trip.trip_id)
        self.assertIsNotNone(bill)
        self.assertEqual(bill.distance_fare, 7.5)  # 5km * $1.50

    def test_multiple_payment_methods(self):
        """Test using different payment methods for different trips"""
        # Register user and driver
        user = self.system.register_user("Jane Smith", "jane@example.com", "9876543210")
        driver = self.system.register_driver("Alice Brown", "alice@example.com", "5559876543", "DL789012")

        # Trip 1 - Pay with credit card
        trip1 = self.system.request_ride(user.user_id, 37.7749, -122.4194, 37.7849, -122.4094)
        self.system.accept_ride(trip1.trip_id, driver.driver_id)
        self.system.start_ride(trip1.trip_id)
        self.system.complete_ride(trip1.trip_id, 8.0)

        card_payment = self.system.pay_with_credit_card(
            trip1.trip_id,
            "4111111111111111",  # Valid test card number
            "12/26",
            "123",
            "Jane Smith"
        )
        self.assertTrue(card_payment)

        # Trip 2 - Pay with UPI
        trip2 = self.system.request_ride(user.user_id, 37.7849, -122.4094, 37.7949, -122.3994)
        self.system.accept_ride(trip2.trip_id, driver.driver_id)
        self.system.start_ride(trip2.trip_id)
        self.system.complete_ride(trip2.trip_id, 6.0)

        upi_payment = self.system.pay_with_upi(
            trip2.trip_id,
            "jane@paytm",
            "gpay"
        )
        self.assertTrue(upi_payment)

    def test_driver_rating_system(self):
        """Test driver rating functionality"""
        user = self.system.register_user("Test User", "test@example.com", "1112223333")
        driver = self.system.register_driver("Test Driver", "driver@example.com", "4445556666", "DL999999")

        # Rate driver
        initial_rating = driver.rating
        self.system.rate_driver(driver.driver_id, 4.5)

        # Check updated rating
        updated_driver = self.system.driver_manager.get_driver(driver.driver_id)
        self.assertEqual(updated_driver.rating, 4.5)  # First rating becomes the new rating

    def test_trip_cancellation(self):
        """Test trip cancellation functionality"""
        # Register user and driver
        user = self.system.register_user("Cancel User", "cancel@example.com", "7778889999")
        driver = self.system.register_driver("Cancel Driver", "cancel@example.com", "6667778888", "DL888888")

        # Request and accept ride
        trip = self.system.request_ride(user.user_id, 37.7749, -122.4194, 37.7849, -122.4094)
        self.system.accept_ride(trip.trip_id, driver.driver_id)

        # Cancel trip
        success = self.system.cancel_ride(trip.trip_id)
        self.assertTrue(success)

        # Check cancelled status
        cancelled_trip = self.system.get_trip(trip.trip_id)
        self.assertEqual(cancelled_trip.status.value, "cancelled")

    def test_payment_failure_scenarios(self):
        """Test payment failure scenarios"""
        # Register user and driver
        user = self.system.register_user("Fail User", "fail@example.com", "0001112222")
        driver = self.system.register_driver("Fail Driver", "fail@example.com", "3334445555", "DL777777")

        # Create and complete trip
        trip = self.system.request_ride(user.user_id, 37.7749, -122.4194, 37.7849, -122.4094)
        self.system.accept_ride(trip.trip_id, driver.driver_id)
        self.system.start_ride(trip.trip_id)
        self.system.complete_ride(trip.trip_id, 5.0)

        # Try to pay for non-existent trip
        result = self.system.pay_with_cash("nonexistent_trip")
        self.assertFalse(result)

        # Try to pay with invalid credit card (should raise ValueError due to validation)
        with self.assertRaises(ValueError):
            self.system.pay_with_credit_card(
                trip.trip_id,
                "invalid_card",  # Invalid format
                "12/25",
                "123",
                "Test User"
            )

    def test_vehicle_management(self):
        """Test vehicle registration and management"""
        # Register driver
        driver = self.system.register_driver("Vehicle Driver", "vehicle@example.com", "9990001111", "DL666666")

        # Register vehicle
        vehicle = self.system.register_vehicle_for_driver(
            driver.driver_id, "Honda", "Civic", 2022, "XYZ789"
        )

        self.assertEqual(vehicle.make, "Honda")
        self.assertEqual(vehicle.model, "Civic")
        self.assertEqual(vehicle.year, 2022)
        self.assertEqual(vehicle.license_plate, "XYZ789")

        # Get vehicles by driver
        vehicles = self.system.vehicle_manager.get_vehicles_by_driver(driver.driver_id)
        self.assertEqual(len(vehicles), 1)
        self.assertEqual(vehicles[0].vehicle_id, vehicle.vehicle_id)


if __name__ == '__main__':
    unittest.main(verbosity=2)
