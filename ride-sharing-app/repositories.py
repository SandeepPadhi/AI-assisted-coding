"""
Abstract Repositories and In-Memory Implementations for Ride Sharing Application
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from entities import Payment

from entities import User, Driver, Trip, Vehicle, Location, Bill


class AbstractUserRepository(ABC):
    """Abstract base class for user repository"""

    @abstractmethod
    def save_user(self, user: User) -> None:
        """Save a user to the repository"""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID"""
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        """Retrieve all users"""
        pass

    @abstractmethod
    def update_user(self, user: User) -> None:
        """Update an existing user"""
        pass

    @abstractmethod
    def delete_user(self, user_id: str) -> None:
        """Delete a user by ID"""
        pass


class InMemoryUserRepository(AbstractUserRepository):
    """In-memory implementation of user repository"""

    def __init__(self) -> None:
        self.users: Dict[str, User] = {}

    def save_user(self, user: User) -> None:
        """Save a user to the in-memory storage"""
        if user.validate_user_data():
            self.users[user.user_id] = user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID from in-memory storage"""
        return self.users.get(user_id)

    def get_all_users(self) -> List[User]:
        """Retrieve all users from in-memory storage"""
        return list(self.users.values())

    def update_user(self, user: User) -> None:
        """Update an existing user in in-memory storage"""
        if user.user_id in self.users and user.validate_user_data():
            self.users[user.user_id] = user

    def delete_user(self, user_id: str) -> None:
        """Delete a user by ID from in-memory storage"""
        if user_id in self.users:
            del self.users[user_id]


class AbstractDriverRepository(ABC):
    """Abstract base class for driver repository"""

    @abstractmethod
    def save_driver(self, driver: Driver) -> None:
        """Save a driver to the repository"""
        pass

    @abstractmethod
    def get_driver_by_id(self, driver_id: str) -> Optional[Driver]:
        """Retrieve a driver by ID"""
        pass

    @abstractmethod
    def get_available_drivers(self) -> List[Driver]:
        """Retrieve all available drivers"""
        pass

    @abstractmethod
    def update_driver(self, driver: Driver) -> None:
        """Update an existing driver"""
        pass

    @abstractmethod
    def delete_driver(self, driver_id: str) -> None:
        """Delete a driver by ID"""
        pass


class InMemoryDriverRepository(AbstractDriverRepository):
    """In-memory implementation of driver repository"""

    def __init__(self) -> None:
        self.drivers: Dict[str, Driver] = {}

    def save_driver(self, driver: Driver) -> None:
        """Save a driver to the in-memory storage"""
        if driver.validate_driver_data():
            self.drivers[driver.driver_id] = driver

    def get_driver_by_id(self, driver_id: str) -> Optional[Driver]:
        """Retrieve a driver by ID from in-memory storage"""
        return self.drivers.get(driver_id)

    def get_available_drivers(self) -> List[Driver]:
        """Retrieve all available drivers from in-memory storage"""
        return [driver for driver in self.drivers.values() if driver.is_available]

    def update_driver(self, driver: Driver) -> None:
        """Update an existing driver in in-memory storage"""
        if driver.driver_id in self.drivers and driver.validate_driver_data():
            self.drivers[driver.driver_id] = driver

    def delete_driver(self, driver_id: str) -> None:
        """Delete a driver by ID from in-memory storage"""
        if driver_id in self.drivers:
            del self.drivers[driver_id]


class AbstractVehicleRepository(ABC):
    """Abstract base class for vehicle repository"""

    @abstractmethod
    def save_vehicle(self, vehicle: Vehicle) -> None:
        """Save a vehicle to the repository"""
        pass

    @abstractmethod
    def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Retrieve a vehicle by ID"""
        pass

    @abstractmethod
    def get_vehicles_by_driver_id(self, driver_id: str) -> List[Vehicle]:
        """Retrieve vehicles by driver ID"""
        pass

    @abstractmethod
    def update_vehicle(self, vehicle: Vehicle) -> None:
        """Update an existing vehicle"""
        pass

    @abstractmethod
    def delete_vehicle(self, vehicle_id: str) -> None:
        """Delete a vehicle by ID"""
        pass


class InMemoryVehicleRepository(AbstractVehicleRepository):
    """In-memory implementation of vehicle repository"""

    def __init__(self) -> None:
        self.vehicles: Dict[str, Vehicle] = {}

    def save_vehicle(self, vehicle: Vehicle) -> None:
        """Save a vehicle to the in-memory storage"""
        if vehicle.validate_vehicle_data():
            self.vehicles[vehicle.vehicle_id] = vehicle

    def get_vehicle_by_id(self, vehicle_id: str) -> Optional[Vehicle]:
        """Retrieve a vehicle by ID from in-memory storage"""
        return self.vehicles.get(vehicle_id)

    def get_vehicles_by_driver_id(self, driver_id: str) -> List[Vehicle]:
        """Retrieve vehicles by driver ID from in-memory storage"""
        return [vehicle for vehicle in self.vehicles.values() if vehicle.driver_id == driver_id]

    def update_vehicle(self, vehicle: Vehicle) -> None:
        """Update an existing vehicle in in-memory storage"""
        if vehicle.vehicle_id in self.vehicles and vehicle.validate_vehicle_data():
            self.vehicles[vehicle.vehicle_id] = vehicle

    def delete_vehicle(self, vehicle_id: str) -> None:
        """Delete a vehicle by ID from in-memory storage"""
        if vehicle_id in self.vehicles:
            del self.vehicles[vehicle_id]


class AbstractTripRepository(ABC):
    """Abstract base class for trip repository"""

    @abstractmethod
    def save_trip(self, trip: Trip) -> None:
        """Save a trip to the repository"""
        pass

    @abstractmethod
    def get_trip_by_id(self, trip_id: str) -> Optional[Trip]:
        """Retrieve a trip by ID"""
        pass

    @abstractmethod
    def get_trips_by_user_id(self, user_id: str) -> List[Trip]:
        """Retrieve trips by user ID"""
        pass

    @abstractmethod
    def get_trips_by_driver_id(self, driver_id: str) -> List[Trip]:
        """Retrieve trips by driver ID"""
        pass

    @abstractmethod
    def get_requested_trips(self) -> List[Trip]:
        """Retrieve all requested trips"""
        pass

    @abstractmethod
    def update_trip(self, trip: Trip) -> None:
        """Update an existing trip"""
        pass

    @abstractmethod
    def delete_trip(self, trip_id: str) -> None:
        """Delete a trip by ID"""
        pass


class InMemoryTripRepository(AbstractTripRepository):
    """In-memory implementation of trip repository"""

    def __init__(self) -> None:
        self.trips: Dict[str, Trip] = {}

    def save_trip(self, trip: Trip) -> None:
        """Save a trip to the in-memory storage"""
        self.trips[trip.trip_id] = trip

    def get_trip_by_id(self, trip_id: str) -> Optional[Trip]:
        """Retrieve a trip by ID from in-memory storage"""
        return self.trips.get(trip_id)

    def get_trips_by_user_id(self, user_id: str) -> List[Trip]:
        """Retrieve trips by user ID from in-memory storage"""
        return [trip for trip in self.trips.values() if trip.user_id == user_id]

    def get_trips_by_driver_id(self, driver_id: str) -> List[Trip]:
        """Retrieve trips by driver ID from in-memory storage"""
        return [trip for trip in self.trips.values() if trip.driver_id == driver_id]

    def get_requested_trips(self) -> List[Trip]:
        """Retrieve all requested trips from in-memory storage"""
        return [trip for trip in self.trips.values() if trip.status.name == "REQUESTED"]

    def update_trip(self, trip: Trip) -> None:
        """Update an existing trip in in-memory storage"""
        if trip.trip_id in self.trips:
            self.trips[trip.trip_id] = trip

    def delete_trip(self, trip_id: str) -> None:
        """Delete a trip by ID from in-memory storage"""
        if trip_id in self.trips:
            del self.trips[trip_id]


class AbstractPaymentRepository(ABC):
    """Abstract base class for payment repository"""

    @abstractmethod
    def save_payment(self, payment) -> None:
        """Save a payment to the repository"""
        pass

    @abstractmethod
    def get_payment_by_id(self, payment_id: str):
        """Retrieve a payment by ID"""
        pass

    @abstractmethod
    def get_payments_by_trip_id(self, trip_id: str) -> List:
        """Retrieve payments by trip ID"""
        pass

    @abstractmethod
    def get_payments_by_method(self, payment_method: str) -> List:
        """Retrieve payments by payment method"""
        pass

    @abstractmethod
    def update_payment(self, payment) -> None:
        """Update an existing payment"""
        pass


class InMemoryPaymentRepository(AbstractPaymentRepository):
    """In-memory implementation of payment repository"""

    def __init__(self) -> None:
        # Import locally to avoid circular imports
        from entities import Payment
        self.payments: Dict[str, Payment] = {}

    def save_payment(self, payment) -> None:
        """Save a payment to the in-memory storage"""
        if payment.validate_payment_data():
            self.payments[payment.payment_id] = payment

    def get_payment_by_id(self, payment_id: str):
        """Retrieve a payment by ID from in-memory storage"""
        return self.payments.get(payment_id)

    def get_payments_by_trip_id(self, trip_id: str) -> List:
        """Retrieve payments by trip ID from in-memory storage"""
        return [payment for payment in self.payments.values() if payment.trip_id == trip_id]

    def get_payments_by_method(self, payment_method: str) -> List:
        """Retrieve payments by payment method from in-memory storage"""
        return [payment for payment in self.payments.values()
                if hasattr(payment, 'payment_method') and payment.payment_method == payment_method]

    def update_payment(self, payment) -> None:
        """Update an existing payment in in-memory storage"""
        if payment.payment_id in self.payments and payment.validate_payment_data():
            self.payments[payment.payment_id] = payment


class AbstractBillRepository(ABC):
    """Abstract base class for bill repository"""

    @abstractmethod
    def save_bill(self, bill: Bill) -> None:
        """Save a bill to the repository"""
        pass

    @abstractmethod
    def get_bill_by_id(self, bill_id: str) -> Optional[Bill]:
        """Retrieve a bill by ID"""
        pass

    @abstractmethod
    def get_bills_by_trip_id(self, trip_id: str) -> List[Bill]:
        """Retrieve bills by trip ID"""
        pass

    @abstractmethod
    def get_bills_by_user_id(self, user_id: str) -> List[Bill]:
        """Retrieve bills by user ID"""
        pass

    @abstractmethod
    def update_bill(self, bill: Bill) -> None:
        """Update an existing bill"""
        pass


class InMemoryBillRepository(AbstractBillRepository):
    """In-memory implementation of bill repository"""

    def __init__(self) -> None:
        self.bills: Dict[str, Bill] = {}

    def save_bill(self, bill: Bill) -> None:
        """Save a bill to the in-memory storage"""
        if bill.validate_bill_data():
            self.bills[bill.bill_id] = bill

    def get_bill_by_id(self, bill_id: str) -> Optional[Bill]:
        """Retrieve a bill by ID from in-memory storage"""
        return self.bills.get(bill_id)

    def get_bills_by_trip_id(self, trip_id: str) -> List[Bill]:
        """Retrieve bills by trip ID from in-memory storage"""
        return [bill for bill in self.bills.values() if bill.trip_id == trip_id]

    def get_bills_by_user_id(self, user_id: str) -> List[Bill]:
        """Retrieve bills by user ID from in-memory storage"""
        return [bill for bill in self.bills.values() if bill.user_id == user_id]

    def update_bill(self, bill: Bill) -> None:
        """Update an existing bill in in-memory storage"""
        if bill.bill_id in self.bills and bill.validate_bill_data():
            self.bills[bill.bill_id] = bill
