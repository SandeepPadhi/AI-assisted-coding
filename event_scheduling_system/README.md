# Event Scheduling System

A comprehensive event scheduling system built in Python that allows users to create events, manage participants, and send automated notifications when events are about to start.

## Features

- **Event Management**: Create, update, and delete events with full validation
- **Participant Management**: Add and manage event participants with contact information
- **Notification System**: Automated notifications via Email, SMS, and Push notifications
- **Background Processing**: Automatic notification processing with configurable intervals
- **Thread Safety**: All operations are thread-safe with proper locking mechanisms
- **Extensible Architecture**: Repository pattern allows easy extension to different storage systems

## Architecture

### Core Components

1. **Entities** (`entities.py`)
   - `Event`: Core event entity with business logic and validation
   - `Participant`: Event participant with contact information
   - `Notification`: Notification entity with scheduling and delivery tracking

2. **Repositories** (`repositories.py`)
   - Abstract base classes for data persistence
   - In-memory implementations for demonstration
   - Thread-safe operations with RLock

3. **Managers** (`managers.py`)
   - `EventManager`: Handles event CRUD operations
   - `ParticipantManager`: Manages event participants
   - `NotificationManager`: Coordinates notification scheduling and delivery

4. **Services** (`services.py`)
   - `EmailService`: Mock email notification service
   - `SMSService`: Mock SMS notification service
   - `PushNotificationService`: Mock push notification service
   - `NotificationDispatcher`: Routes notifications to appropriate services

5. **Orchestrator** (`orchestrator.py`)
   - `EventSchedulingSystem`: Main system orchestrator providing high-level API

## Design Principles

- **Single Responsibility**: Each class has a focused, well-defined purpose
- **Open/Closed Principle**: Easy to extend with new storage systems or notification types
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Thread Safety**: All operations are thread-safe for concurrent access
- **Clean Code**: Descriptive function names, comprehensive type hints, and clear documentation

## Usage

### Running the Demo

```bash
python3 main.py
```

Choose between:
1. **Automated Demo**: Comprehensive demonstration of all features
2. **Interactive Demo**: Manual testing with command-line interface

### Basic Usage Example

```python
from orchestrator import EventSchedulingSystem
from datetime import datetime, timedelta

# Initialize system
system = EventSchedulingSystem()

# Create an event
event = system.create_event(
    title="Team Meeting",
    description="Weekly team sync",
    start_time=datetime.now() + timedelta(hours=1),
    end_time=datetime.now() + timedelta(hours=2),
    creator_id="user123"
)

# Add participants
participant = system.add_participant(
    event_id=event.event_id,
    user_id="user456",
    name="John Doe",
    email="john@example.com",
    phone="+1234567890"
)

# Schedule notifications
notifications = system.schedule_event_notifications(
    event_id=event.event_id,
    minutes_before=15
)

# Start background notification processor
system.start_notification_processor()
```

## API Reference

### EventSchedulingSystem Methods

#### Event Management
- `create_event(title, description, start_time, end_time, creator_id)`: Create new event
- `get_event(event_id)`: Get event by ID
- `get_all_events()`: Get all events
- `update_event(event_id, ...)`: Update event details
- `delete_event(event_id)`: Delete event and all associated data

#### Participant Management
- `add_participant(event_id, user_id, name, email, phone=None)`: Add participant
- `get_event_participants(event_id)`: Get event participants
- `remove_participant(participant_id)`: Remove participant
- `update_participant_contact(participant_id, ...)`: Update participant contact info

#### Notification Management
- `schedule_event_notifications(event_id, minutes_before=60)`: Schedule notifications
- `send_pending_notifications()`: Send ready notifications
- `get_event_notifications(event_id)`: Get event notifications

#### System Management
- `start_notification_processor(check_interval_seconds=30)`: Start background processor
- `stop_notification_processor()`: Stop background processor
- `get_system_stats()`: Get system statistics
- `cleanup_old_notifications(days_old=30)`: Clean up old notifications

## Validation & Business Rules

### Event Validation
- Title and description are required
- Start time must be before end time
- Start time must be in the future
- Creator ID is required

### Participant Validation
- Name and email are required
- Email must be valid format
- Phone must be valid format (if provided)
- Duplicate participants not allowed for same event

### Notification Validation
- Message is required
- Scheduled time must be in the future
- Supports Email, SMS, and Push notification types

## Thread Safety

All repository operations use `threading.RLock()` to ensure thread safety:
- Event repository operations are atomic
- Participant operations maintain data consistency
- Notification operations are thread-safe
- Background notification processor runs in separate thread

## Extensibility

### Adding New Storage Systems

1. Implement the abstract repository interfaces
2. Replace in-memory repositories in `EventSchedulingSystem`

```python
class MySQLRepository(EventRepository):
    def save_event(self, event: Event) -> None:
        # MySQL implementation
        pass

# Use in system
system = EventSchedulingSystem()
system.event_repository = MySQLRepository()
```

### Adding New Notification Types

1. Add new notification type to `NotificationType` enum
2. Create new notification service
3. Register service with dispatcher

```python
class SlackService(NotificationService):
    def get_service_type(self) -> NotificationType:
        return NotificationType.SLACK

# Register service
dispatcher.register_service(SlackService())
```

## Demo Output

The automated demo demonstrates:
- Event creation and validation
- Participant management
- Notification scheduling (with immediate notifications for demo purposes)
- Background processing with real-time notification sending
- Error handling (duplicate participant detection)
- System cleanup

### Notification Timing in Demo

The demo creates two types of notifications:
1. **Immediate notifications**: Scheduled 1 second in the past for instant demonstration
2. **Future notifications**: Scheduled 15 minutes before events (traditional use case)

This shows both immediate notification capabilities and standard event reminder functionality.

### Understanding Notification States

- **PENDING**: Notification is scheduled but not yet due to be sent
- **READY**: Notification is due to be sent (scheduled_time <= current_time)
- **SENT**: Notification has been successfully delivered

The system automatically transitions notifications from PENDING → READY → SENT based on timing and delivery success.

### Background Notification Processor

The system includes a background notification processor that:
- Runs in a separate thread for non-blocking operation
- Automatically checks for and sends pending notifications
- Can be configured with custom check intervals
- Provides clean start/stop lifecycle management

**Important**: The demo includes proper cleanup to avoid resource leaks, which is why you see "Stopped background notification processor" messages. This ensures the system shuts down gracefully.

## Testing

Run the critical test suite to verify core functionality:

```bash
python3 test_critical.py
```

The test suite covers:
- **Event Creation & Validation**: Tests event creation with proper validation
- **Participant Management**: Tests participant addition and duplicate prevention
- **Notification System**: Tests notification scheduling and sending
- **Integration Workflow**: Tests complete end-to-end functionality
- **Error Handling**: Tests system behavior with invalid inputs

All tests are designed to be fast and focused on critical system functionality.

## Requirements

- Python 3.7+
- No external dependencies (uses only standard library)

## Future Enhancements

- Database persistence (MySQL, PostgreSQL)
- Real notification services (SendGrid, Twilio, FCM)
- Web API with REST endpoints
- User authentication and authorization
- Event recurrence patterns
- Calendar integration
- Advanced notification templates
- Analytics and reporting
