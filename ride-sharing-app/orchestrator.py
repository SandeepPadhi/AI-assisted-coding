"""
System Orchestrator for Ride Sharing Application
"""

import uuid
from typing import List, Optional
from entities import User, Driver, Trip, Vehicle, Location, CreditCardPayment, UPIPayment, CashPayment, Bill, TripStatus
from managers import (
    UserManager, DriverManager, VehicleManager, TripManager,
    PaymentManager, BillManager
)
from repositories import (
    InMemoryUserRepository, InMemoryDriverRepository, InMemoryTripRepository,
    InMemoryVehicleRepository, InMemoryPaymentRepository, InMemoryBillRepository
)


class RideSharingAppSystem:
    """Main system orchestrator that coordinates all components"""

    def __init__(self) -> None:
        # Initialize repositories
        self.user_repo = InMemoryUserRepository()
        self.driver_repo = InMemoryDriverRepository()
        self.trip_repo = InMemoryTripRepository()
        self.vehicle_repo = InMemoryVehicleRepository()
        self.payment_repo = InMemoryPaymentRepository()
        self.bill_repo = InMemoryBillRepository()

        # Initialize managers
        self.user_manager = UserManager(self.user_repo)
        self.driver_manager = DriverManager(self.driver_repo)
        self.vehicle_manager = VehicleManager(self.vehicle_repo)
        self.trip_manager = TripManager(self.trip_repo)
        self.payment_manager = PaymentManager(self.payment_repo)
        self.bill_manager = BillManager(self.bill_repo)

    # User Management
    def register_user(self, name: str, email: str, phone: str) -> User:
        """Register a new user"""
        user_id = str(uuid.uuid4())[:8]
        return self.user_manager.create_user(user_id, name, email, phone)

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.user_manager.get_user(user_id)

    def get_all_users(self) -> List[User]:
        """Get all users"""
        return self.user_manager.get_all_users()

    # Driver Management
    def register_driver(self, name: str, email: str, phone: str, license_number: str) -> Driver:
        """Register a new driver"""
        driver_id = str(uuid.uuid4())[:8]
        return self.driver_manager.create_driver(driver_id, name, email, phone, license_number)

    def register_vehicle_for_driver(self, driver_id: str, make: str, model: str, year: int, license_plate: str) -> Vehicle:
        """Register a vehicle for a driver"""
        vehicle_id = str(uuid.uuid4())[:8]
        return self.vehicle_manager.create_vehicle(vehicle_id, driver_id, make, model, year, license_plate)

    def get_available_drivers(self) -> List[Driver]:
        """Get all available drivers"""
        return self.driver_manager.get_available_drivers()

    def update_driver_availability(self, driver_id: str, available: bool) -> None:
        """Update driver availability"""
        self.driver_manager.update_driver_availability(driver_id, available)

    # Trip Management
    def request_ride(self, user_id: str, pickup_lat: float, pickup_lon: float,
                    dropoff_lat: float, dropoff_lon: float) -> Trip:
        """Request a new ride"""
        trip_id = str(uuid.uuid4())[:8]
        pickup_location = Location(pickup_lat, pickup_lon)
        dropoff_location = Location(dropoff_lat, dropoff_lon)
        return self.trip_manager.create_trip_request(trip_id, user_id, pickup_location, dropoff_location)

    def accept_ride(self, trip_id: str, driver_id: str) -> bool:
        """Accept a ride request"""
        success = self.trip_manager.accept_trip(trip_id, driver_id)
        if success:
            # Update driver availability
            self.update_driver_availability(driver_id, False)
        return success

    def start_ride(self, trip_id: str) -> bool:
        """Start a ride"""
        return self.trip_manager.start_trip(trip_id)

    def complete_ride(self, trip_id: str, distance_km: float) -> bool:
        """Complete a ride and generate bill (payment handled separately)"""
        trip = self.trip_manager.get_trip(trip_id)
        if not trip or not trip.driver_id:
            return False

        # Calculate fare (simple calculation)
        base_fare = 2.0
        per_km_rate = 1.5
        fare_amount = base_fare + (distance_km * per_km_rate)

        success = self.trip_manager.complete_trip(trip_id, distance_km, fare_amount)
        if success:
            # Make driver available again
            self.update_driver_availability(trip.driver_id, True)

            # Generate bill
            bill_id = str(uuid.uuid4())[:8]
            self.bill_manager.generate_bill(bill_id, trip_id, trip.user_id, trip.driver_id, distance_km)

        return success

    def pay_with_cash(self, trip_id: str) -> bool:
        """Process payment with cash for a completed trip"""
        trip = self.trip_manager.get_trip(trip_id)
        if not trip or trip.status.value != "completed":
            return False

        # Get bill amount
        bill = self.get_trip_bill(trip_id)
        if not bill:
            return False

        # Create cash payment
        self.create_cash_payment(trip_id, bill.total_amount)

        # Process the payment
        return self.process_payment(trip_id)

    def pay_with_credit_card(self, trip_id: str, card_number: str, expiry_date: str,
                           cvv: str, card_holder_name: str) -> bool:
        """Process payment with credit card for a completed trip"""
        trip = self.trip_manager.get_trip(trip_id)
        if not trip or trip.status.value != "completed":
            return False

        # Get bill amount
        bill = self.get_trip_bill(trip_id)
        if not bill:
            return False

        # Create credit card payment
        self.create_credit_card_payment(
            trip_id, bill.total_amount, card_number, expiry_date, cvv, card_holder_name
        )

        # Process the payment
        return self.process_payment(trip_id)

    def pay_with_upi(self, trip_id: str, upi_id: str, upi_app: str = "default") -> bool:
        """Process payment with UPI for a completed trip"""
        trip = self.trip_manager.get_trip(trip_id)
        if not trip or trip.status.value != "completed":
            return False

        # Get bill amount
        bill = self.get_trip_bill(trip_id)
        if not bill:
            return False

        # Create UPI payment
        self.create_upi_payment(trip_id, bill.total_amount, upi_id, upi_app)

        # Process the payment
        return self.process_payment(trip_id)

    def cancel_ride(self, trip_id: str) -> bool:
        """Cancel a ride"""
        trip = self.trip_manager.get_trip(trip_id)
        success = self.trip_manager.cancel_trip(trip_id)
        if success and trip and trip.driver_id:
            # Make driver available again if they were assigned
            self.update_driver_availability(trip.driver_id, True)
        return success

    def get_trip(self, trip_id: str) -> Optional[Trip]:
        """Get trip by ID"""
        return self.trip_manager.get_trip(trip_id)

    def get_user_trip_history(self, user_id: str) -> List[Trip]:
        """Get trip history for a user"""
        return self.trip_manager.get_user_trips(user_id)

    def get_driver_trip_history(self, driver_id: str) -> List[Trip]:
        """Get trip history for a driver"""
        return self.trip_manager.get_driver_trips(driver_id)

    def get_requested_rides(self) -> List[Trip]:
        """Get all requested rides (for drivers to see available rides)"""
        return self.trip_manager.get_requested_trips()

    # Payment and Billing
    def create_credit_card_payment(self, trip_id: str, amount: float,
                                  card_number: str, expiry_date: str, cvv: str,
                                  card_holder_name: str) -> CreditCardPayment:
        """Create a credit card payment for a trip"""
        payment_id = str(uuid.uuid4())[:8]
        return self.payment_manager.create_credit_card_payment(
            payment_id, trip_id, amount, card_number, expiry_date, cvv, card_holder_name
        )

    def create_upi_payment(self, trip_id: str, amount: float,
                          upi_id: str, upi_app: str = "default") -> UPIPayment:
        """Create a UPI payment for a trip"""
        payment_id = str(uuid.uuid4())[:8]
        return self.payment_manager.create_upi_payment(payment_id, trip_id, amount, upi_id, upi_app)

    def create_cash_payment(self, trip_id: str, amount: float) -> CashPayment:
        """Create a cash payment for a trip"""
        payment_id = str(uuid.uuid4())[:8]
        return self.payment_manager.create_cash_payment(payment_id, trip_id, amount)

    def process_payment(self, trip_id: str) -> bool:
        """Process payment for a trip"""
        payments = self.payment_manager.get_payments_by_trip(trip_id)
        if payments:
            payment = payments[0]  # Get the first payment
            return self.payment_manager.process_payment(payment.payment_id)
        return False

    def get_trip_bill(self, trip_id: str) -> Optional[Bill]:
        """Get bill for a trip"""
        bills = self.bill_manager.get_bills_by_trip(trip_id)
        return bills[0] if bills else None

    def get_user_bills(self, user_id: str) -> List[Bill]:
        """Get all bills for a user"""
        return self.bill_manager.get_bills_by_user(user_id)

    def get_payments_by_method(self, payment_method: str) -> List:
        """Get payments by payment method"""
        return self.payment_manager.get_payments_by_method(payment_method)

    # Rating System
    def rate_driver(self, driver_id: str, rating: float) -> None:
        """Rate a driver after trip completion"""
        self.driver_manager.update_driver_rating(driver_id, rating)
