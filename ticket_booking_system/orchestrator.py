"""
System orchestrator for the Train Ticket Booking System
"""
from datetime import datetime, timedelta
from repositories import UserRepository, TrainRepository, TicketRepository, BookingRepository
from managers import UserManager, TrainManager, TicketManager, BookingManager
from entities import User, Train, Ticket, Booking, TicketStatus


class TrainTicketBookingSystem:
    """Main system orchestrator that wires all components together"""
    
    def __init__(self):
        # Initialize repositories
        self.user_repository = UserRepository()
        self.train_repository = TrainRepository()
        self.ticket_repository = TicketRepository()
        self.booking_repository = BookingRepository()
        
        # Initialize managers
        self.user_manager = UserManager(self.user_repository)
        self.train_manager = TrainManager(self.train_repository)
        self.ticket_manager = TicketManager(self.ticket_repository, self.train_manager)
        self.booking_manager = BookingManager(self.booking_repository, self.ticket_repository)
        
        # Initialize with sample data
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize the system with sample trains"""
        # Create sample trains
        train1 = Train(
            id="T001",
            name="Express 123",
            source="Mumbai",
            destination="Delhi",
            total_seats=100,
            available_seats=50,
            departure_time=datetime.now() + timedelta(hours=2),
            arrival_time=datetime.now() + timedelta(hours=8)
        )
        
        train2 = Train(
            id="T002", 
            name="Local 456",
            source="Mumbai",
            destination="Delhi",
            total_seats=80,
            available_seats=30,
            departure_time=datetime.now() + timedelta(hours=4),
            arrival_time=datetime.now() + timedelta(hours=10)
        )
        
        self.train_repository.save(train1)
        self.train_repository.save(train2)
    
    def run_demo(self):
        """Run a demonstration of the ticket booking system"""
        print("=== Train Ticket Booking System Demo ===\n")
        
        # 1. Create a user
        print("1. Creating a new user...")
        user = self.user_manager.create_user("John Doe", "john@example.com", "1234567890")
        print(f"   Created user: {user.name} (ID: {user.id})\n")
        
        # 2. Search for trains
        print("2. Searching for trains from Mumbai to Delhi...")
        trains = self.train_manager.search_trains("Mumbai", "Delhi")
        for train in trains:
            print(f"   Train: {train.name} - Available seats: {train.available_seats}")
        print()
        
        if not trains:
            print("   No trains found!")
            return
        
        # 3. Book a ticket
        print("3. Booking a ticket...")
        selected_train = trains[0]
        ticket = self.ticket_manager.book_ticket(user.id, selected_train.id, 500.0)
        
        if ticket:
            print(f"   Ticket booked successfully!")
            print(f"   Ticket ID: {ticket.id}")
            print(f"   Seat Number: {ticket.seat_number}")
            print(f"   Status: {ticket.status.value}")
            print(f"   Price: ${ticket.price}")
        else:
            print("   Failed to book ticket - no seats available")
            return
        print()
        
        # 4. Create a booking
        print("4. Creating a booking...")
        booking = self.booking_manager.create_booking(user.id, ticket.id, ticket.price)
        print(f"   Booking created: {booking.id}")
        print(f"   Total amount: ${booking.total_amount}")
        print()
        
        # 5. Show user's tickets
        print("5. User's tickets:")
        user_tickets = self.ticket_manager.get_user_tickets(user.id)
        for t in user_tickets:
            train = self.train_manager.get_train_by_id(t.train_id)
            print(f"   Ticket {t.id}: {train.name} - Seat {t.seat_number} - {t.status.value}")
        print()
        
        # 6. Cancel a ticket
        print("6. Cancelling the ticket...")
        if self.ticket_manager.cancel_ticket(ticket.id):
            print("   Ticket cancelled successfully!")
            
            # Show updated train availability
            updated_train = self.train_manager.get_train_by_id(selected_train.id)
            print(f"   Updated available seats: {updated_train.available_seats}")
        else:
            print("   Failed to cancel ticket")
        print()
        
        print("=== Demo completed successfully! ===")
