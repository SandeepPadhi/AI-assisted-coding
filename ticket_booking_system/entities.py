"""
Core entities for the Train Ticket Booking System
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class TicketStatus(Enum):
    """Status of a ticket booking"""
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    PENDING = "pending"


@dataclass
class User:
    """User entity - represents a customer in the system"""
    # id: unique identifier for the user across the system
    # name: display name for the user
    # email: contact information and login identifier
    # phone: contact information for notifications
    id: str
    name: str
    email: str
    phone: str

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("User name cannot be empty")
        if not self.email.strip():
            raise ValueError("User email cannot be empty")


@dataclass
class Train:
    """Train entity - represents a train service"""
    # id: unique identifier for the train
    # name: human readable train name/number
    # source: departure station
    # destination: arrival station
    # total_seats: maximum capacity of the train
    # available_seats: current available seats
    # departure_time: when the train leaves
    # arrival_time: when the train arrives
    id: str
    name: str
    source: str
    destination: str
    total_seats: int
    available_seats: int
    departure_time: datetime
    arrival_time: datetime

    def __post_init__(self):
        if self.total_seats <= 0:
            raise ValueError("Train must have positive total seats")
        if self.available_seats < 0 or self.available_seats > self.total_seats:
            raise ValueError("Available seats must be between 0 and total seats")
        if self.departure_time >= self.arrival_time:
            raise ValueError("Departure time must be before arrival time")


@dataclass
class Ticket:
    """Ticket entity - represents a booked ticket"""
    # id: unique identifier for the ticket
    # user_id: reference to the user who booked
    # train_id: reference to the train
    # seat_number: specific seat assigned
    # status: current status of the ticket
    # booking_time: when the ticket was booked
    # price: cost of the ticket
    id: str
    user_id: str
    train_id: str
    seat_number: int
    status: TicketStatus
    booking_time: datetime
    price: float

    def __post_init__(self):
        if self.seat_number <= 0:
            raise ValueError("Seat number must be positive")
        if self.price <= 0:
            raise ValueError("Ticket price must be positive")


@dataclass
class Booking:
    """Booking entity - represents a booking transaction"""
    # id: unique identifier for the booking
    # user_id: reference to the user
    # ticket_id: reference to the ticket
    # booking_time: when the booking was made
    # total_amount: total cost including any fees
    id: str
    user_id: str
    ticket_id: str
    booking_time: datetime
    total_amount: float

    def __post_init__(self):
        if self.total_amount <= 0:
            raise ValueError("Booking amount must be positive")
