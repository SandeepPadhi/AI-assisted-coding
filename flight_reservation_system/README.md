# Flight Reservation System - MVP Implementation

A minimal viable product (MVP) flight reservation system demonstrating clean architecture and incremental development.

## Quick Start

```python
# 5-line usage example
from main import FlightReservationSystem

system = FlightReservationSystem()
system.demonstrate_complete_user_journey()
```

## Core Features (MVP)

✅ **User Management**: Register users with email validation  
✅ **Flight Management**: Add flights with airport code validation  
✅ **Passenger Management**: Register passengers with passport validation  
✅ **Booking Management**: Create bookings with business rule validation  
✅ **Flight Search**: Search flights by source and destination  
✅ **Error Handling**: Comprehensive validation and custom exceptions  

## Architecture

### Design Patterns Used
- **Repository Pattern**: Data abstraction for future storage extensions
- **Service Layer Pattern**: Business logic coordination
- **Exception Hierarchy Pattern**: Granular error handling
- **Validation Pattern**: Input sanitization and business rules

### File Structure
```
flight_reservation_system/
├── main.py              # Core implementation (MVP + Features)
├── exceptions.py        # Custom exception hierarchy
├── test_mvp.py         # Unit tests for core functionality
└── README.md           # This file
```

## Running the System

### Demo
```bash
python3 main.py
```

### Tests
```bash
python3 test_mvp.py
```

## Extension Points (Post-MVP)

### Repository Extensions
- **Database Storage**: Replace in-memory with MySQL/PostgreSQL
- **Caching Layer**: Add Redis for performance
- **Search Index**: Add Elasticsearch for advanced queries

### Business Logic Extensions
- **Flight Capacity Management**: Track available seats
- **Booking Cancellation**: Add cancellation workflow
- **Payment Integration**: Add payment processing
- **Notification System**: Email/SMS confirmations

### Validation Extensions
- **Advanced Email Validation**: Domain verification
- **Passport Validation**: Government API integration
- **Flight Route Validation**: Real-time availability checking

## Trade-offs

### Simplicity vs Features
- **MVP**: Basic validation, in-memory storage, simple queries
- **Production**: Advanced validation, persistent storage, complex queries

### Performance vs Maintainability
- **Current**: Synchronous operations, simple threading
- **Scalable**: Async operations, connection pooling, caching

### Error Handling vs Complexity
- **Current**: Basic exception hierarchy, simple validation
- **Advanced**: Comprehensive logging, retry mechanisms, circuit breakers

## Testing Strategy

### Unit Tests (Current)
- Core entity creation
- Business operations
- Error scenarios
- Input validation

### Future Test Types
- Integration tests with external services
- Performance tests for scalability
- End-to-end user journey tests

## Development Phases

### ✅ Part 1: MVP Core (≤200 lines)
- Basic entities and repositories
- Core business operations
- Working demo

### ✅ Part 2: Strategic Feature (≤100 lines)
- Flight search functionality
- Enhanced demo

### ✅ Part 3: Harden Core Paths (≤150 lines)
- Input validation
- Error handling
- Business rule enforcement

### ✅ Part 4: Minimal Testing (≤100 lines)
- Unit tests for core functionality
- Error scenario coverage

## Next Steps

1. **Add Database Integration**: Replace in-memory storage
2. **Implement Booking Cancellation**: Add cancellation workflow
3. **Add Flight Capacity Management**: Track available seats
4. **Enhance Search**: Add date, price, and availability filters
5. **Add API Layer**: RESTful endpoints for web/mobile clients

---

*This MVP demonstrates systematic thinking and controlled development over flashy features, perfect for LLD interviews.*
