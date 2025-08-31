"""
Custom exceptions for Flight Reservation System

Design Pattern: Exception Hierarchy
Purpose: Provide specific error types for different failure scenarios
Implementation: Custom exception classes with descriptive messages
Trade-offs: Granular error handling vs exception proliferation
"""


class FlightReservationError(Exception):
    """Base exception for all flight reservation system errors"""
    pass


class EntityNotFoundError(FlightReservationError):
    """Raised when an entity is not found in the system"""
    
    def __init__(self, entity_type: str, entity_id: str) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(f"{entity_type} with ID '{entity_id}' not found")


class EntityAlreadyExistsError(FlightReservationError):
    """Raised when trying to create an entity that already exists"""
    
    def __init__(self, entity_type: str, entity_id: str) -> None:
        self.entity_type = entity_type
        self.entity_id = entity_id
        # Even though FlightReservationError does not define its own __init__, it inherits from Exception,
        # which does have an __init__ that accepts a message. So, super() here calls Exception.__init__.
        super().__init__(f"{entity_type} with ID '{entity_id}' already exists")


class InvalidBookingError(FlightReservationError):
    """Raised when a booking operation is invalid"""
    
    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid booking: {message}")


class FlightCapacityError(FlightReservationError):
    """Raised when flight capacity constraints are violated"""
    
    def __init__(self, flight_id: str, message: str) -> None:
        self.flight_id = flight_id
        super().__init__(f"Flight {flight_id} capacity error: {message}")


class ValidationError(FlightReservationError):
    """Raised when input validation fails"""
    
    def __init__(self, field: str, message: str) -> None:
        self.field = field
        super().__init__(f"Validation error for {field}: {message}")
