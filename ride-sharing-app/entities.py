"""
Entities for the Ride Sharing Application
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class TripStatus(Enum):
    """Enumeration for trip statuses"""
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Location:
    """Represents a geographical location"""

    def __init__(self, latitude: float, longitude: float, address: str = "") -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.address = address

    def calculate_distance(self, other_location: 'Location') -> float:
        """Calculate approximate distance between two locations in kilometers"""
        # Simplified distance calculation using Euclidean distance
        # In real implementation, would use Haversine formula
        lat_diff = self.latitude - other_location.latitude
        lon_diff = self.longitude - other_location.longitude
        return (lat_diff ** 2 + lon_diff ** 2) ** 0.5 * 111  # Rough conversion to km


class User:
    """Represents a user who can request rides"""

    def __init__(self, user_id: str, name: str, email: str, phone: str) -> None:
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = datetime.now()

    def validate_user_data(self) -> bool:
        """Validate user data"""
        return bool(self.name and self.email and self.phone and self.user_id)


class Driver:
    """Represents a driver who can accept rides"""

    def __init__(self, driver_id: str, name: str, email: str, phone: str, license_number: str) -> None:
        self.driver_id = driver_id
        self.name = name
        self.email = email
        self.phone = phone
        self.license_number = license_number
        self.is_available = True
        self.rating = 5.0
        self.total_rides = 0
        self.created_at = datetime.now()

    def validate_driver_data(self) -> bool:
        """Validate driver data"""
        return bool(self.name and self.email and self.phone and self.driver_id and self.license_number)

    def update_availability(self, available: bool) -> None:
        """Update driver availability"""
        self.is_available = available

    def update_rating(self, new_rating: float) -> None:
        """Update driver rating"""
        if 1.0 <= new_rating <= 5.0:
            # Calculate weighted average
            self.rating = (self.rating * self.total_rides + new_rating) / (self.total_rides + 1)
            self.total_rides += 1


class Vehicle:
    """Represents a driver's vehicle"""

    def __init__(self, vehicle_id: str, driver_id: str, make: str, model: str, year: int, license_plate: str) -> None:
        self.vehicle_id = vehicle_id
        self.driver_id = driver_id
        self.make = make
        self.model = model
        self.year = year
        self.license_plate = license_plate

    def validate_vehicle_data(self) -> bool:
        """Validate vehicle data"""
        return bool(self.vehicle_id and self.driver_id and self.make and self.model and self.license_plate)


class Trip:
    """Represents a ride trip"""

    def __init__(self, trip_id: str, user_id: str, driver_id: Optional[str] = None) -> None:
        self.trip_id = trip_id
        self.user_id = user_id
        self.driver_id = driver_id
        self.status = TripStatus.REQUESTED
        self.pickup_location: Optional[Location] = None
        self.dropoff_location: Optional[Location] = None
        self.requested_at = datetime.now()
        self.accepted_at: Optional[datetime] = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.distance_km: Optional[float] = None
        self.fare_amount: Optional[float] = None

    def set_locations(self, pickup: Location, dropoff: Location) -> None:
        """Set pickup and dropoff locations"""
        self.pickup_location = pickup
        self.dropoff_location = dropoff

    def accept_trip(self, driver_id: str) -> None:
        """Accept the trip"""
        self.driver_id = driver_id
        self.status = TripStatus.ACCEPTED
        self.accepted_at = datetime.now()

    def start_trip(self) -> None:
        """Start the trip"""
        self.status = TripStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete_trip(self, distance_km: float, fare_amount: float) -> None:
        """Complete the trip"""
        self.status = TripStatus.COMPLETED
        self.completed_at = datetime.now()
        self.distance_km = distance_km
        self.fare_amount = fare_amount

    def cancel_trip(self) -> None:
        """Cancel the trip"""
        self.status = TripStatus.CANCELLED


from abc import ABC, abstractmethod


class Payment(ABC):
    """Abstract base class for payment transactions"""

    def __init__(self, payment_id: str, trip_id: str, amount: float) -> None:
        self.payment_id = payment_id
        self.trip_id = trip_id
        self.amount = amount
        self.status = "pending"  # pending, completed, failed
        self.processed_at: Optional[datetime] = None

    @abstractmethod
    def process_payment(self) -> bool:
        """Process the payment - implemented by concrete payment methods"""
        pass

    @abstractmethod
    def validate_payment_data(self) -> bool:
        """Validate payment data - implemented by concrete payment methods"""
        pass

    def mark_completed(self) -> None:
        """Mark payment as completed"""
        self.status = "completed"
        self.processed_at = datetime.now()

    def mark_failed(self) -> None:
        """Mark payment as failed"""
        self.status = "failed"


class CreditCardPayment(Payment):
    """Credit card payment implementation"""

    def __init__(self, payment_id: str, trip_id: str, amount: float,
                 card_number: str, expiry_date: str, cvv: str, card_holder_name: str) -> None:
        super().__init__(payment_id, trip_id, amount)
        self.card_number = card_number
        self.expiry_date = expiry_date
        self.cvv = cvv
        self.card_holder_name = card_holder_name
        self.payment_method = "credit_card"

    def validate_payment_data(self) -> bool:
        """Validate credit card payment data"""
        if not (self.payment_id and self.trip_id and self.amount > 0):
            return False

        # Basic card number validation (should be 16 digits)
        if not (self.card_number and len(self.card_number.replace(" ", "")) == 16):
            return False

        # Basic expiry validation (MM/YY format)
        if not (self.expiry_date and len(self.expiry_date) == 5 and "/" in self.expiry_date):
            return False

        # CVV validation (3-4 digits)
        if not (self.cvv and 3 <= len(self.cvv) <= 4 and self.cvv.isdigit()):
            return False

        # Card holder name validation
        if not (self.card_holder_name and len(self.card_holder_name.strip()) > 0):
            return False

        return True

    def process_payment(self) -> bool:
        """Process credit card payment (simplified simulation)"""
        if not self.validate_payment_data():
            self.mark_failed()
            return False

        # In real implementation, this would integrate with payment gateway
        # Simulate processing time and success rate
        import random
        success = random.random() > 0.05  # 95% success rate

        if success:
            self.mark_completed()
            return True
        else:
            self.mark_failed()
            return False


class UPIPayment(Payment):
    """UPI payment implementation"""

    def __init__(self, payment_id: str, trip_id: str, amount: float, upi_id: str, upi_app: str = "default") -> None:
        super().__init__(payment_id, trip_id, amount)
        self.upi_id = upi_id
        self.upi_app = upi_app  # gpay, phonepe, paytm, etc.
        self.payment_method = "upi"

    def validate_payment_data(self) -> bool:
        """Validate UPI payment data"""
        if not (self.payment_id and self.trip_id and self.amount > 0):
            return False

        # UPI ID validation (basic format check)
        if not (self.upi_id and "@" in self.upi_id):
            return False

        # UPI app validation
        valid_apps = ["gpay", "phonepe", "paytm", "amazonpay", "default"]
        if self.upi_app not in valid_apps:
            return False

        return True

    def process_payment(self) -> bool:
        """Process UPI payment (simplified simulation)"""
        if not self.validate_payment_data():
            self.mark_failed()
            return False

        # In real implementation, this would integrate with UPI gateway
        # Simulate processing time and success rate
        import random
        success = random.random() > 0.03  # 97% success rate for UPI

        if success:
            self.mark_completed()
            return True
        else:
            self.mark_failed()
            return False


class CashPayment(Payment):
    """Cash payment implementation"""

    def __init__(self, payment_id: str, trip_id: str, amount: float) -> None:
        super().__init__(payment_id, trip_id, amount)
        self.payment_method = "cash"

    def validate_payment_data(self) -> bool:
        """Validate cash payment data"""
        return bool(self.payment_id and self.trip_id and self.amount > 0)

    def process_payment(self) -> bool:
        """Process cash payment (cash is collected by driver)"""
        if not self.validate_payment_data():
            self.mark_failed()
            return False

        # Cash payments are typically marked as completed when collected
        self.mark_completed()
        return True


class Bill:
    """Represents a bill for a completed trip"""

    def __init__(self, bill_id: str, trip_id: str, user_id: str, driver_id: str) -> None:
        self.bill_id = bill_id
        self.trip_id = trip_id
        self.user_id = user_id
        self.driver_id = driver_id
        self.base_fare = 0.0
        self.distance_fare = 0.0
        self.total_amount = 0.0
        self.tax_amount = 0.0
        self.generated_at = datetime.now()

    def calculate_bill(self, distance_km: float, base_fare: float = 2.0, per_km_rate: float = 1.5, tax_rate: float = 0.1) -> None:
        """Calculate the bill amount"""
        self.base_fare = base_fare
        self.distance_fare = distance_km * per_km_rate
        subtotal = self.base_fare + self.distance_fare
        self.tax_amount = subtotal * tax_rate
        self.total_amount = subtotal + self.tax_amount

    def validate_bill_data(self) -> bool:
        """Validate bill data"""
        return bool(self.bill_id and self.trip_id and self.user_id and self.driver_id)
