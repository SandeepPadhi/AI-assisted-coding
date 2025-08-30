"""
Entity managers for business logic orchestration
"""
import uuid
from datetime import datetime
from typing import List, Optional
from entities import User, Train, Ticket, Booking, TicketStatus
from repositories import UserRepository, TrainRepository, TicketRepository, BookingRepository


class UserManager:
    """Manages user-related business operations"""
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    def create_user(self, name: str, email: str, phone: str) -> User:
        """Create a new user"""
        user_id = str(uuid.uuid4())
        user = User(id=user_id, name=name, email=email, phone=phone)
        self._user_repository.save(user)
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._user_repository.get_by_id(user_id)


class TrainManager:
    """Manages train-related business operations"""
    
    def __init__(self, train_repository: TrainRepository):
        self._train_repository = train_repository
    
    def search_trains(self, source: str, destination: str) -> List[Train]:
        """Search for trains between source and destination"""
        return self._train_repository.search_trains(source, destination)
    
    def get_train_by_id(self, train_id: str) -> Optional[Train]:
        """Get train by ID"""
        return self._train_repository.get_by_id(train_id)
    
    def update_train_seats(self, train_id: str, seats_to_reserve: int) -> bool:
        """Update available seats on a train"""
        train = self._train_repository.get_by_id(train_id)
        if not train or train.available_seats < seats_to_reserve:
            return False
        
        train.available_seats -= seats_to_reserve
        self._train_repository.save(train)
        return True


class TicketManager:
    """Manages ticket-related business operations"""
    
    def __init__(self, ticket_repository: TicketRepository, train_manager: TrainManager):
        self._ticket_repository = ticket_repository
        self._train_manager = train_manager
    
    def book_ticket(self, user_id: str, train_id: str, price: float) -> Optional[Ticket]:
        """Book a ticket for a user on a specific train"""
        train = self._train_manager.get_train_by_id(train_id)
        if not train or train.available_seats <= 0:
            return None
        
        # Reserve a seat
        if not self._train_manager.update_train_seats(train_id, 1):
            return None
        
        ticket_id = str(uuid.uuid4())
        seat_number = train.total_seats - train.available_seats + 1
        
        ticket = Ticket(
            id=ticket_id,
            user_id=user_id,
            train_id=train_id,
            seat_number=seat_number,
            status=TicketStatus.CONFIRMED,
            booking_time=datetime.now(),
            price=price
        )
        
        self._ticket_repository.save(ticket)
        return ticket
    
    def cancel_ticket(self, ticket_id: str) -> bool:
        """Cancel a ticket and free up the seat"""
        ticket = self._ticket_repository.get_by_id(ticket_id)
        if not ticket or ticket.status == TicketStatus.CANCELLED:
            return False
        
        # Update ticket status
        ticket.status = TicketStatus.CANCELLED
        self._ticket_repository.save(ticket)
        
        # Free up the seat by updating the train
        train = self._train_manager.get_train_by_id(ticket.train_id)
        if train:
            train.available_seats += 1
            self._train_manager._train_repository.save(train)
        
        return True
    
    def get_user_tickets(self, user_id: str) -> List[Ticket]:
        """Get all tickets for a user"""
        return self._ticket_repository.get_tickets_by_user(user_id)


class BookingManager:
    """Manages booking-related business operations"""
    
    def __init__(self, booking_repository: BookingRepository, ticket_repository: TicketRepository):
        self._booking_repository = booking_repository
        self._ticket_repository = ticket_repository
    
    def create_booking(self, user_id: str, ticket_id: str, total_amount: float) -> Booking:
        """Create a booking for a ticket"""
        booking_id = str(uuid.uuid4())
        booking = Booking(
            id=booking_id,
            user_id=user_id,
            ticket_id=ticket_id,
            booking_time=datetime.now(),
            total_amount=total_amount
        )
        self._booking_repository.save(booking)
        return booking
    
    def get_user_bookings(self, user_id: str) -> List[Booking]:
        """Get all bookings for a user"""
        return self._booking_repository.get_bookings_by_user(user_id)
