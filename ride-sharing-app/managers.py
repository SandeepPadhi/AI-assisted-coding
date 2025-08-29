"""
Entity Managers for Ride Sharing Application Business Logic
"""

from typing import List, Optional
from entities import User, Driver, Trip, Vehicle, Location, Bill, TripStatus
from repositories import (
    AbstractUserRepository, AbstractDriverRepository, AbstractTripRepository,
    AbstractVehicleRepository, AbstractPaymentRepository, AbstractBillRepository
)


class UserManager:
    """Manager for user-related business logic"""

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        self.user_repository = user_repository

    def create_user(self, user_id: str, name: str, email: str, phone: str) -> User:
        """Create a new user"""
        user = User(user_id, name, email, phone)
        if user.validate_user_data():
            self.user_repository.save_user(user)
            return user
        raise ValueError("Invalid user data")

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.user_repository.get_user_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """Get all users"""
        return self.user_repository.get_all_users()

    def update_user(self, user: User) -> None:
        """Update user information"""
        if user.validate_user_data():
            self.user_repository.update_user(user)
        else:
            raise ValueError("Invalid user data")


class DriverManager:
    """Manager for driver-related business logic"""

    def __init__(self, driver_repository: AbstractDriverRepository) -> None:
        self.driver_repository = driver_repository

    def create_driver(self, driver_id: str, name: str, email: str, phone: str, license_number: str) -> Driver:
        """Create a new driver"""
        driver = Driver(driver_id, name, email, phone, license_number)
        if driver.validate_driver_data():
            self.driver_repository.save_driver(driver)
            return driver
        raise ValueError("Invalid driver data")

    def get_driver(self, driver_id: str) -> Optional[Driver]:
        """Get driver by ID"""
        return self.driver_repository.get_driver_by_id(driver_id)

    def get_available_drivers(self) -> List[Driver]:
        """Get all available drivers"""
        return self.driver_repository.get_available_drivers()

    def update_driver_availability(self, driver_id: str, available: bool) -> None:
        """Update driver availability"""
        driver = self.driver_repository.get_driver_by_id(driver_id)
        if driver:
            driver.update_availability(available)
            self.driver_repository.update_driver(driver)

    def update_driver_rating(self, driver_id: str, new_rating: float) -> None:
        """Update driver rating"""
        driver = self.driver_repository.get_driver_by_id(driver_id)
        if driver:
            driver.update_rating(new_rating)
            self.driver_repository.update_driver(driver)


class VehicleManager:
    """Manager for vehicle-related business logic"""

    def __init__(self, vehicle_repository: AbstractVehicleRepository) -> None:
        self.vehicle_repository = vehicle_repository

    def create_vehicle(self, vehicle_id: str, driver_id: str, make: str, model: str, year: int, license_plate: str) -> Vehicle:
        """Create a new vehicle"""
        vehicle = Vehicle(vehicle_id, driver_id, make, model, year, license_plate)
        if vehicle.validate_vehicle_data():
            self.vehicle_repository.save_vehicle(vehicle)
            return vehicle
        raise ValueError("Invalid vehicle data")

    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get vehicle by ID"""
        return self.vehicle_repository.get_vehicle_by_id(vehicle_id)

    def get_vehicles_by_driver(self, driver_id: str) -> List[Vehicle]:
        """Get vehicles by driver ID"""
        return self.vehicle_repository.get_vehicles_by_driver_id(driver_id)


class TripManager:
    """Manager for trip-related business logic"""

    def __init__(self, trip_repository: AbstractTripRepository) -> None:
        self.trip_repository = trip_repository

    def create_trip_request(self, trip_id: str, user_id: str, pickup: Location, dropoff: Location) -> Trip:
        """Create a new trip request"""
        trip = Trip(trip_id, user_id)
        trip.set_locations(pickup, dropoff)
        self.trip_repository.save_trip(trip)
        return trip

    def accept_trip(self, trip_id: str, driver_id: str) -> bool:
        """Accept a trip request"""
        trip = self.trip_repository.get_trip_by_id(trip_id)
        if trip and trip.status == TripStatus.REQUESTED:
            trip.accept_trip(driver_id)
            self.trip_repository.update_trip(trip)
            return True
        return False

    def start_trip(self, trip_id: str) -> bool:
        """Start a trip"""
        trip = self.trip_repository.get_trip_by_id(trip_id)
        if trip and trip.status == TripStatus.ACCEPTED:
            trip.start_trip()
            self.trip_repository.update_trip(trip)
            return True
        return False

    def complete_trip(self, trip_id: str, distance_km: float, fare_amount: float) -> bool:
        """Complete a trip"""
        trip = self.trip_repository.get_trip_by_id(trip_id)
        if trip and trip.status == TripStatus.IN_PROGRESS:
            trip.complete_trip(distance_km, fare_amount)
            self.trip_repository.update_trip(trip)
            return True
        return False

    def cancel_trip(self, trip_id: str) -> bool:
        """Cancel a trip"""
        trip = self.trip_repository.get_trip_by_id(trip_id)
        if trip and trip.status in [TripStatus.REQUESTED, TripStatus.ACCEPTED]:
            trip.cancel_trip()
            self.trip_repository.update_trip(trip)
            return True
        return False

    def get_trip(self, trip_id: str) -> Optional[Trip]:
        """Get trip by ID"""
        return self.trip_repository.get_trip_by_id(trip_id)

    def get_user_trips(self, user_id: str) -> List[Trip]:
        """Get trips by user ID"""
        return self.trip_repository.get_trips_by_user_id(user_id)

    def get_driver_trips(self, driver_id: str) -> List[Trip]:
        """Get trips by driver ID"""
        return self.trip_repository.get_trips_by_driver_id(driver_id)

    def get_requested_trips(self) -> List[Trip]:
        """Get all requested trips"""
        return self.trip_repository.get_requested_trips()


class PaymentManager:
    """Manager for payment-related business logic"""

    def __init__(self, payment_repository: AbstractPaymentRepository) -> None:
        self.payment_repository = payment_repository

    def create_credit_card_payment(self, payment_id: str, trip_id: str, amount: float,
                                  card_number: str, expiry_date: str, cvv: str,
                                  card_holder_name: str):
        """Create a new credit card payment"""
        # Import locally to avoid circular imports
        from entities import CreditCardPayment

        payment = CreditCardPayment(payment_id, trip_id, amount, card_number, expiry_date, cvv, card_holder_name)
        if payment.validate_payment_data():
            self.payment_repository.save_payment(payment)
            return payment
        raise ValueError("Invalid credit card payment data")

    def create_upi_payment(self, payment_id: str, trip_id: str, amount: float,
                          upi_id: str, upi_app: str = "default"):
        """Create a new UPI payment"""
        # Import locally to avoid circular imports
        from entities import UPIPayment

        payment = UPIPayment(payment_id, trip_id, amount, upi_id, upi_app)
        if payment.validate_payment_data():
            self.payment_repository.save_payment(payment)
            return payment
        raise ValueError("Invalid UPI payment data")

    def create_cash_payment(self, payment_id: str, trip_id: str, amount: float):
        """Create a new cash payment"""
        # Import locally to avoid circular imports
        from entities import CashPayment

        payment = CashPayment(payment_id, trip_id, amount)
        if payment.validate_payment_data():
            self.payment_repository.save_payment(payment)
            return payment
        raise ValueError("Invalid cash payment data")

    def process_payment(self, payment_id: str) -> bool:
        """Process a payment"""
        payment = self.payment_repository.get_payment_by_id(payment_id)
        if payment:
            return payment.process_payment()
        return False

    def get_payment(self, payment_id: str):
        """Get payment by ID"""
        return self.payment_repository.get_payment_by_id(payment_id)

    def get_payments_by_trip(self, trip_id: str) -> List:
        """Get payments by trip ID"""
        return self.payment_repository.get_payments_by_trip_id(trip_id)

    def get_payments_by_method(self, payment_method: str) -> List:
        """Get payments by payment method"""
        return self.payment_repository.get_payments_by_method(payment_method)


class BillManager:
    """Manager for bill-related business logic"""

    def __init__(self, bill_repository: AbstractBillRepository) -> None:
        self.bill_repository = bill_repository

    def generate_bill(self, bill_id: str, trip_id: str, user_id: str, driver_id: str, distance_km: float) -> Bill:
        """Generate a bill for a completed trip"""
        bill = Bill(bill_id, trip_id, user_id, driver_id)
        bill.calculate_bill(distance_km)
        if bill.validate_bill_data():
            self.bill_repository.save_bill(bill)
            return bill
        raise ValueError("Invalid bill data")

    def get_bill(self, bill_id: str) -> Optional[Bill]:
        """Get bill by ID"""
        return self.bill_repository.get_bill_by_id(bill_id)

    def get_bills_by_user(self, user_id: str) -> List[Bill]:
        """Get bills by user ID"""
        return self.bill_repository.get_bills_by_user_id(user_id)

    def get_bills_by_trip(self, trip_id: str) -> List[Bill]:
        """Get bills by trip ID"""
        return self.bill_repository.get_bills_by_trip_id(trip_id)
