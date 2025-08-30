# Train Ticket Booking System

A complete train ticket booking system implemented in Python following clean architecture principles.

## Features

- **User Management**: Create and manage users
- **Train Search**: Search for trains by source and destination
- **Ticket Booking**: Book tickets with seat allocation
- **Ticket Cancellation**: Cancel tickets and free up seats
- **Booking Management**: Track booking transactions

## Architecture

The system follows a layered architecture with clear separation of concerns:

### Entities (`entities.py`)
- **User**: Customer information with validation
- **Train**: Train details with seat management
- **Ticket**: Ticket information with status tracking
- **Booking**: Booking transaction records

### Repositories (`repositories.py`)
- **BaseRepository**: Abstract interface for all repositories
- **UserRepository**: User data persistence
- **TrainRepository**: Train data with search functionality
- **TicketRepository**: Ticket data with user-specific queries
- **BookingRepository**: Booking transaction data

### Managers (`managers.py`)
- **UserManager**: User creation and retrieval
- **TrainManager**: Train search and seat management
- **TicketManager**: Ticket booking and cancellation logic
- **BookingManager**: Booking transaction management

### System Orchestrator (`orchestrator.py`)
- **TrainTicketBookingSystem**: Main system that wires all components

## Usage

Run the demo to see the system in action:

```bash
python3 main.py
```

The demo will:
1. Create a new user
2. Search for trains between Mumbai and Delhi
3. Book a ticket on the first available train
4. Create a booking transaction
5. Display user's tickets
6. Cancel the ticket and show updated seat availability

## Design Patterns Used

- **Repository Pattern**: Abstract data access layer
- **Dependency Injection**: Managers receive repositories as dependencies
- **Single Responsibility**: Each class has one clear purpose
- **Encapsulation**: Internal state is protected with clear public APIs

## Extensibility

The system is designed for easy extension:

- **Database Integration**: Replace in-memory repositories with database implementations
- **External Services**: Add payment gateways, notification services
- **Additional Features**: Seat preferences, multiple ticket booking, refund processing
- **Validation**: Add more business rules and validation logic

## Code Quality

- **Type Hints**: All functions and variables are properly typed
- **Error Handling**: Basic validation and error checking
- **Documentation**: Clear docstrings and comments
- **Modular Design**: Easy to test and maintain
