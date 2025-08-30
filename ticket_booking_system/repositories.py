"""
Repository interfaces and in-memory implementations
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from entities import User, Train, Ticket, Booking


class BaseRepository(ABC):
    """Abstract base repository interface"""
    
    @abstractmethod
    def save(self, entity) -> None:
        """Save an entity to storage"""
        pass
    
    @abstractmethod
    def get_by_id(self, entity_id: str):
        """Retrieve entity by ID"""
        pass
    
    @abstractmethod
    def list_all(self) -> List:
        """List all entities"""
        pass
    
    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        """Delete entity by ID"""
        pass


class UserRepository(BaseRepository):
    """Repository for User entities"""
    
    def __init__(self):
        self._users: Dict[str, User] = {}
    
    def save(self, user: User) -> None:
        self._users[user.id] = user
    
    def get_by_id(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)
    
    def list_all(self) -> List[User]:
        return list(self._users.values())
    
    def delete(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False


class TrainRepository(BaseRepository):
    """Repository for Train entities"""
    
    def __init__(self):
        self._trains: Dict[str, Train] = {}
    
    def save(self, train: Train) -> None:
        self._trains[train.id] = train
    
    def get_by_id(self, train_id: str) -> Optional[Train]:
        return self._trains.get(train_id)
    
    def list_all(self) -> List[Train]:
        return list(self._trains.values())
    
    def delete(self, train_id: str) -> bool:
        if train_id in self._trains:
            del self._trains[train_id]
            return True
        return False
    
    def search_trains(self, source: str, destination: str) -> List[Train]:
        """Search trains by source and destination"""
        return [
            train for train in self._trains.values()
            if train.source.lower() == source.lower() and 
               train.destination.lower() == destination.lower()
        ]


class TicketRepository(BaseRepository):
    """Repository for Ticket entities"""
    
    def __init__(self):
        self._tickets: Dict[str, Ticket] = {}
    
    def save(self, ticket: Ticket) -> None:
        self._tickets[ticket.id] = ticket
    
    def get_by_id(self, ticket_id: str) -> Optional[Ticket]:
        return self._tickets.get(ticket_id)
    
    def list_all(self) -> List[Ticket]:
        return list(self._tickets.values())
    
    def delete(self, ticket_id: str) -> bool:
        if ticket_id in self._tickets:
            del self._tickets[ticket_id]
            return True
        return False
    
    def get_tickets_by_user(self, user_id: str) -> List[Ticket]:
        """Get all tickets for a specific user"""
        return [ticket for ticket in self._tickets.values() if ticket.user_id == user_id]


class BookingRepository(BaseRepository):
    """Repository for Booking entities"""
    
    def __init__(self):
        self._bookings: Dict[str, Booking] = {}
    
    def save(self, booking: Booking) -> None:
        self._bookings[booking.id] = booking
    
    def get_by_id(self, booking_id: str) -> Optional[Booking]:
        return self._bookings.get(booking_id)
    
    def list_all(self) -> List[Booking]:
        return list(self._bookings.values())
    
    def delete(self, booking_id: str) -> bool:
        if booking_id in self._bookings:
            del self._bookings[booking_id]
            return True
        return False
    
    def get_bookings_by_user(self, user_id: str) -> List[Booking]:
        """Get all bookings for a specific user"""
        return [booking for booking in self._bookings.values() if booking.user_id == user_id]
