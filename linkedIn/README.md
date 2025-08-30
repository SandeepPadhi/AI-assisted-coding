# LinkedIn System - Modular Architecture

A comprehensive LinkedIn-like system implemented with a clean, modular architecture following OOP principles and design patterns.

## Architecture Overview

The system is divided into 5 main layers:

### 1. Entities (`entities.py`)
Core business objects with their invariants and business logic:
- **User**: Basic user information with email validation
- **Profile**: User profile details (headline, summary, location)
- **Message**: User posts with content management
- **Connection**: Relationship between users with status management
- **NewsFeedItem**: Individual items in a user's news feed
- **NewsFeed**: Complete news feed for a user

### 2. Repositories (`repositories.py`)
Abstract base classes and in-memory implementations for data storage:
- **AbstractUserRepository** / **InMemoryUserRepository**
- **AbstractProfileRepository** / **InMemoryProfileRepository**
- **AbstractMessageRepository** / **InMemoryMessageRepository**
- **AbstractConnectionRepository** / **InMemoryConnectionRepository**
- **AbstractNewsFeedRepository** / **InMemoryNewsFeedRepository**

### 3. Managers (`managers.py`)
Business logic managers that handle operations and rules:
- **UserManager**: User creation and validation
- **ProfileManager**: Profile management operations
- **MessageManager**: Message posting, updating, and deletion
- **ConnectionManager**: Connection requests, acceptance, and management
- **NewsFeedManager**: News feed generation and management

### 4. Services (`services.py`)
External service integrations with mock implementations:
- **EmailService**: Email notifications for connections and messages
- **SMSService**: SMS notifications
- **PushNotificationService**: Push notifications
- **NotificationService**: Coordinates all notification channels

### 5. Orchestrator (`orchestrator.py`)
Main system coordinator that ties everything together:
- **LinkedInSystem**: High-level operations and system coordination

## Features

### Phase 1: User Profile Management
- User creation with email validation
- Profile creation and updates
- User retrieval and management

### Phase 2: Messaging System
- Post messages with content validation
- Update and delete messages (author-only)
- Retrieve user messages and all system messages

### Phase 3: Connection System
- Send connection requests
- Accept/reject connection requests
- Manage connection status
- Notification system integration

### Phase 4: News Feed System
- Generate personalized news feeds
- Content aggregation from connections
- Chronological ordering
- Feed refresh and updates

## Usage

### Running the Demo
```bash
cd linkedIn
python main.py
```

### Using the System Programmatically
```python
from orchestrator import LinkedInSystem

# Initialize the system
linkedin = LinkedInSystem()

# Create users
user, profile = linkedin.create_user_with_profile(
    "user_001", "john@example.com", "John", "Doe",
    "Software Engineer", "Experienced developer", "San Francisco"
)

# Post a message
message = linkedin.post_message("msg_001", "user_001", "Hello LinkedIn!")

# Send connection request
connection = linkedin.send_connection_request("conn_001", "user_001", "user_002")

# Get news feed
feed_items = linkedin.get_user_feed("user_001")
```

## Design Principles

### 1. Single Responsibility Principle
Each class has a single, well-defined responsibility:
- Entities handle their own business logic and validation
- Repositories handle data storage operations
- Managers handle business operations
- Services handle external integrations

### 2. Dependency Inversion
- Abstract base classes for repositories and services
- Managers depend on abstractions, not concrete implementations
- Easy to extend with different storage systems (MySQL, PostgreSQL, etc.)

### 3. Encapsulation
- Internal state is protected
- Business rules are enforced at the entity level
- Clear interfaces between layers

### 4. Extensibility
- Repository pattern allows easy storage system changes
- Service abstractions allow different notification providers
- Manager pattern allows business logic modifications

## Testing

The system includes mock implementations for external services, making it easy to test:
- Mock email service logs emails instead of sending
- Mock SMS service logs SMS instead of sending
- Mock push notification service logs notifications

## Future Enhancements

### Storage Extensions
- MySQL repository implementations
- Redis caching layer
- Elasticsearch for search functionality

### Service Extensions
- Real email service (SendGrid, AWS SES)
- Real SMS service (Twilio, AWS SNS)
- Real push notification service (Firebase, OneSignal)

### Additional Features
- Message reactions and comments
- Advanced search and filtering
- Analytics and insights
- Real-time messaging
- Group functionality

## File Structure
```
linkedIn/
├── entities.py          # Core business objects
├── repositories.py      # Data storage abstractions
├── managers.py          # Business logic managers
├── services.py          # External service integrations
├── orchestrator.py      # Main system coordination
├── main.py             # Demo and execution
└── README.md           # This file
```

## Analysis & Improvements

### Current Strengths
- Clean separation of concerns
- Extensible architecture
- Comprehensive error handling
- Type hints throughout
- Mock services for testing

### Areas for Improvement
1. **Error Handling**: Add more specific exception types
2. **Validation**: Implement more robust input validation
3. **Performance**: Add caching mechanisms
4. **Security**: Add authentication and authorization
5. **Testing**: Add comprehensive unit and integration tests
6. **Logging**: Add structured logging throughout
7. **Configuration**: Add configuration management
8. **Documentation**: Add API documentation

Would you like to add more complexity or features to the project? (e.g., new entity, service, validation, etc.)
