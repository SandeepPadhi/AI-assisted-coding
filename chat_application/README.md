# Chat Application

A comprehensive chat application built in Python that supports both direct messaging and group chats with full CRUD operations.

## Features

### Core Functionality
- **User Management**: Create users with unique usernames
- **Direct Messaging**: Send, receive, edit, and delete messages between users
- **Group Chats**: Create groups, manage members, send group messages
- **Message History**: View conversation history and message status tracking
- **Permission System**: Role-based access control (admin/member roles)

### Key Components

#### Entities (Data Models)
- `User`: User account with username validation
- `Message`: Direct messages with status tracking (sent/edited/deleted)
- `Group`: Group chat rooms
- `GroupMember`: Group membership with roles (admin/member)
- `GroupMessage`: Group messages with status tracking

#### Repositories (Data Access Layer)
- `AbstractUserRepository`: Interface for user data operations
- `AbstractMessageRepository`: Interface for direct message operations
- `AbstractGroupRepository`: Interface for group operations
- `AbstractGroupMemberRepository`: Interface for group membership operations
- `AbstractGroupMessageRepository`: Interface for group message operations
- `InMemoryUserRepository`: In-memory implementation of user repository
- `InMemoryMessageRepository`: In-memory implementation of message repository
- `InMemoryGroupRepository`: In-memory implementation of group repository
- `InMemoryGroupMemberRepository`: In-memory implementation of group member repository
- `InMemoryGroupMessageRepository`: In-memory implementation of group message repository

#### Managers (Business Logic Layer)
- `UserManager`: Handles user-related operations
- `MessageManager`: Handles direct messaging operations
- `GroupManager`: Handles group and group messaging operations

#### Orchestrator
- `ChatApplication`: Main application class that coordinates all components

## Architecture

The application follows a clean architecture pattern with:
- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Injection**: Repositories are injected into managers
- **Abstract Base Classes**: Enables easy extension to different storage backends
- **Type Hints**: Full type annotation for better code maintainability
- **Input Validation**: Comprehensive validation at entity level
- **Error Handling**: Meaningful error messages for all failure cases

## Usage

### Basic Usage
```python
from main import ChatApplication

# Create application instance
app = ChatApplication()

# Create users
alice = app.create_user("alice")
bob = app.create_user("bob")

# Direct messaging
message = app.send_message(alice.user_id, bob.user_id, "Hello Bob!")
app.edit_message(message.message_id, "Hello Bob! How are you?", alice.user_id)
app.delete_message(message.message_id, alice.user_id)

# Group chat
group = app.create_group("Study Group", alice.user_id)
app.add_group_member(group.group_id, bob.user_id, alice.user_id)
group_message = app.send_group_message(group.group_id, alice.user_id, "Welcome!")
```

### Running the Demo
```bash
python3 main.py
```

This will run a comprehensive demo showing all features of the chat application.

## Testing

### Running Tests
```bash
# Run all tests
python3 -m unittest tests -v

# Run specific test class
python3 -m unittest tests.TestChatApplication -v

# Run specific test method
python3 -m unittest tests.TestChatApplication.test_direct_messaging_workflow -v
```

### Test Coverage

The test suite includes **84 comprehensive tests** covering:

#### Entity Tests (8 tests)
- User creation and validation
- Message creation, editing, deletion, and validation
- Group creation and validation
- Group member creation
- Group message operations

#### Repository Tests (21 tests)
- InMemoryUserRepository: User CRUD operations
- InMemoryMessageRepository: Message CRUD and conversation retrieval
- InMemoryGroupRepository: Group CRUD and user-group relationships
- InMemoryGroupMemberRepository: Membership management
- InMemoryGroupMessageRepository: Group message operations

#### Manager Tests (30 tests)
- UserManager: User management operations
- MessageManager: Direct messaging with validation and permissions
- GroupManager: Complete group management including admin controls

#### Integration Tests (21 tests)
- ChatApplication orchestrator: End-to-end workflows
- Complex scenarios: Multiple conversations, large groups, admin transitions
- Message status tracking across all operations
- Permission system validation

#### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete user workflows
- **Edge Case Tests**: Error conditions and boundary cases
- **Permission Tests**: Access control validation

## Design Principles

### SOLID Principles
- **Single Responsibility**: Each class has one clear purpose
- **Open/Closed**: Abstract repositories allow extension without modification
- **Liskov Substitution**: Implementations can be substituted for abstractions
- **Interface Segregation**: Specific interfaces for each repository type
- **Dependency Inversion**: High-level modules don't depend on low-level modules

### Clean Architecture
- **Entities**: Core business objects with validation
- **Use Cases**: Managers implementing business logic
- **Interface Adapters**: Repositories providing data access
- **Frameworks & Drivers**: External concerns (currently in-memory storage)

### Security & Validation
- **Input Validation**: All user inputs validated at entity level
- **Permission Checks**: Role-based access control for sensitive operations
- **Data Integrity**: Business rules enforced at manager level
- **Error Handling**: Meaningful error messages for all failure scenarios

## Extension Points

### Storage Backends
The abstract repository pattern allows easy extension to different storage systems:
- Database repositories (PostgreSQL, MySQL, MongoDB)
- File-based storage
- In-memory with persistence
- Distributed storage systems

### Additional Features
The modular design supports adding:
- Message reactions and threads
- File/image sharing
- User presence and typing indicators
- Message encryption
- Rate limiting and spam protection
- Push notifications
- Message search and filtering

## Performance Considerations

### Current Implementation
- **In-Memory Storage**: Fast access, limited by available RAM
- **Efficient Indexing**: Hash maps for O(1) lookups
- **Minimal Data Structures**: UUID keys, sets for relationships

### Scalability Improvements
- **Database Integration**: Persistent storage with indexing
- **Caching Layer**: Redis for frequently accessed data
- **Message Pagination**: Handle large conversation histories
- **Connection Pooling**: Efficient database connections
- **Async Processing**: Handle high message volumes

## Requirements Fulfillment

✅ **Users can send messages to each other**
✅ **Users can see messages in real time** (simulated in current implementation)
✅ **Users can see past messages**
✅ **Users can create group chats**
✅ **Users can add/remove users from group chats**
✅ **Users can leave group chats**
✅ **Users can delete group chats**
✅ **Users can delete/edit messages**
✅ **Scalable architecture** (repository pattern enables scaling)
✅ **Modular design** with single responsibility principle
✅ **Type hints** throughout the codebase
✅ **Abstract base classes** for future storage extensions

The implementation provides a solid foundation that can be extended to meet the non-functional requirements for 1M users and high message throughput through appropriate infrastructure choices.
