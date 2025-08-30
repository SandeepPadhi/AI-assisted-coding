"""
LinkedIn Managers

Entity managers handling business operations and rules for entities.
"""

from typing import List, Optional

from entities import User, Profile, Message, Connection, NewsFeedItem
from repositories import (
    AbstractUserRepository, AbstractProfileRepository, AbstractMessageRepository,
    AbstractConnectionRepository, AbstractNewsFeedRepository
)


class UserManager:
    """Manager class handling user-related business logic."""

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        self.user_repository = user_repository

    def create_user(self, user_id: str, email: str, first_name: str, last_name: str) -> User:
        """Create a new user with validation."""
        if not user_id or not email or not first_name or not last_name:
            raise ValueError("All user fields are required")

        # Check if user already exists
        existing_user = self.user_repository.get_user_by_email(email)
        if existing_user:
            raise ValueError(f"User with email {email} already exists")

        # Create and validate user
        user = User(user_id, email, first_name, last_name)
        if not user.validate_email():
            raise ValueError("Invalid email format")

        self.user_repository.save_user(user)
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieve a user by ID."""
        return self.user_repository.get_user_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        return self.user_repository.get_all_users()


class ProfileManager:
    """Manager class handling profile-related business logic."""

    def __init__(self, profile_repository: AbstractProfileRepository) -> None:
        self.profile_repository = profile_repository

    def create_profile(self, user_id: str, headline: str = "", summary: str = "", location: str = "") -> Profile:
        """Create a new profile for a user."""
        profile = Profile(user_id, headline, summary, location)
        self.profile_repository.save_profile(profile)
        return profile

    def update_profile(self, user_id: str, headline: str = "", summary: str = "", location: str = "") -> Optional[Profile]:
        """Update an existing profile."""
        profile = self.profile_repository.get_profile_by_user_id(user_id)
        if not profile:
            return None

        profile.update_profile(headline, summary, location)
        self.profile_repository.save_profile(profile)
        return profile

    def get_profile(self, user_id: str) -> Optional[Profile]:
        """Retrieve a profile by user ID."""
        return self.profile_repository.get_profile_by_user_id(user_id)


class MessageManager:
    """Manager class handling message-related business logic."""

    def __init__(self, message_repository: AbstractMessageRepository, user_repository: AbstractUserRepository) -> None:
        self.message_repository = message_repository
        self.user_repository = user_repository

    def post_message(self, message_id: str, author_id: str, content: str) -> Message:
        """Create and post a new message."""
        if not message_id or not author_id or not content:
            raise ValueError("Message ID, author ID, and content are required")

        if not content.strip():
            raise ValueError("Message content cannot be empty")

        # Verify author exists
        author = self.user_repository.get_user_by_id(author_id)
        if not author:
            raise ValueError(f"Author with ID {author_id} does not exist")

        # Check for duplicate message ID
        existing_message = self.message_repository.get_message_by_id(message_id)
        if existing_message:
            raise ValueError(f"Message with ID {message_id} already exists")

        message = Message(message_id, author_id, content.strip())
        self.message_repository.save_message(message)
        return message

    def get_message(self, message_id: str) -> Optional[Message]:
        """Retrieve a message by its ID."""
        return self.message_repository.get_message_by_id(message_id)

    def get_user_messages(self, user_id: str) -> List[Message]:
        """Retrieve all messages posted by a specific user."""
        return self.message_repository.get_messages_by_author(user_id)

    def get_all_messages(self) -> List[Message]:
        """Retrieve all messages in the system."""
        return self.message_repository.get_all_messages()

    def update_message(self, message_id: str, user_id: str, new_content: str) -> Optional[Message]:
        """Update a message if the user is the author."""
        message = self.message_repository.get_message_by_id(message_id)
        if not message:
            return None

        if not message.is_author(user_id):
            raise ValueError("Only the author can update their message")

        message.update_content(new_content)
        self.message_repository.save_message(message)
        return message

    def delete_message(self, message_id: str, user_id: str) -> bool:
        """Delete a message if the user is the author."""
        message = self.message_repository.get_message_by_id(message_id)
        if not message:
            return False

        if not message.is_author(user_id):
            raise ValueError("Only the author can delete their message")

        return self.message_repository.delete_message(message_id)


class ConnectionManager:
    """Manager class handling connection-related business logic."""

    def __init__(self, connection_repository: AbstractConnectionRepository, user_repository: AbstractUserRepository) -> None:
        self.connection_repository = connection_repository
        self.user_repository = user_repository

    def send_connection_request(self, connection_id: str, sender_id: str, receiver_id: str) -> Connection:
        """Send a connection request from sender to receiver."""
        if not connection_id or not sender_id or not receiver_id:
            raise ValueError("Connection ID, sender ID, and receiver ID are required")

        if sender_id == receiver_id:
            raise ValueError("Cannot connect to yourself")

        # Verify both users exist
        sender = self.user_repository.get_user_by_id(sender_id)
        receiver = self.user_repository.get_user_by_id(receiver_id)
        if not sender:
            raise ValueError(f"Sender with ID {sender_id} does not exist")
        if not receiver:
            raise ValueError(f"Receiver with ID {receiver_id} does not exist")

        # Check if connection already exists
        existing_connection = self.connection_repository.get_connection_between_users(sender_id, receiver_id)
        if existing_connection:
            raise ValueError("Connection already exists between these users")

        # Check for duplicate connection ID
        existing_conn_by_id = self.connection_repository.get_connection_by_id(connection_id)
        if existing_conn_by_id:
            raise ValueError(f"Connection with ID {connection_id} already exists")

        connection = Connection(connection_id, sender_id, receiver_id)
        self.connection_repository.save_connection(connection)
        return connection

    def accept_connection_request(self, connection_id: str, user_id: str) -> Optional[Connection]:
        """Accept a connection request if the user is the receiver."""
        connection = self.connection_repository.get_connection_by_id(connection_id)
        if not connection:
            return None

        if connection.receiver_id != user_id:
            raise ValueError("Only the receiver can accept the connection request")

        if not connection.is_pending():
            raise ValueError("Connection request is not pending")

        connection.accept()
        self.connection_repository.save_connection(connection)
        return connection

    def reject_connection_request(self, connection_id: str, user_id: str) -> Optional[Connection]:
        """Reject a connection request if the user is the receiver."""
        connection = self.connection_repository.get_connection_by_id(connection_id)
        if not connection:
            return None

        if connection.receiver_id != user_id:
            raise ValueError("Only the receiver can reject the connection request")

        if not connection.is_pending():
            raise ValueError("Connection request is not pending")

        connection.reject()
        self.connection_repository.save_connection(connection)
        return connection

    def get_connection(self, connection_id: str) -> Optional[Connection]:
        """Retrieve a connection by its ID."""
        return self.connection_repository.get_connection_by_id(connection_id)

    def get_user_connections(self, user_id: str, status: Optional[str] = None) -> List[Connection]:
        """Get all connections for a user, optionally filtered by status."""
        return self.connection_repository.get_connections_by_user(user_id, status)

    def get_accepted_connections(self, user_id: str) -> List[Connection]:
        """Get all accepted connections for a user."""
        return self.get_user_connections(user_id, "accepted")

    def get_pending_requests(self, user_id: str) -> List[Connection]:
        """Get all pending connection requests for a user (both sent and received)."""
        all_connections = self.connection_repository.get_connections_by_user(user_id)
        return [c for c in all_connections if c.is_pending()]

    def get_sent_requests(self, user_id: str) -> List[Connection]:
        """Get all pending connection requests sent by the user."""
        pending_connections = self.get_pending_requests(user_id)
        return [c for c in pending_connections if c.sender_id == user_id]

    def get_received_requests(self, user_id: str) -> List[Connection]:
        """Get all pending connection requests received by the user."""
        pending_connections = self.get_pending_requests(user_id)
        return [c for c in pending_connections if c.receiver_id == user_id]

    def remove_connection(self, connection_id: str, user_id: str) -> bool:
        """Remove a connection if the user is involved in it."""
        connection = self.connection_repository.get_connection_by_id(connection_id)
        if not connection:
            return False

        if not connection.involves_user(user_id):
            raise ValueError("User is not involved in this connection")

        return self.connection_repository.delete_connection(connection_id)

    def are_connected(self, user_id1: str, user_id2: str) -> bool:
        """Check if two users are connected (accepted connection)."""
        connection = self.connection_repository.get_connection_between_users(user_id1, user_id2)
        return connection is not None and connection.is_accepted()


class NewsFeedManager:
    """Manager class handling news feed-related business logic."""

    def __init__(self, feed_repository: AbstractNewsFeedRepository,
                 message_repository: AbstractMessageRepository,
                 connection_manager: 'ConnectionManager',
                 user_repository: AbstractUserRepository,
                 profile_repository: AbstractProfileRepository) -> None:
        self.feed_repository = feed_repository
        self.message_repository = message_repository
        self.connection_manager = connection_manager
        self.user_repository = user_repository
        self.profile_repository = profile_repository

    def generate_feed_for_user(self, user_id: str) -> 'NewsFeed':
        """Generate or refresh a user's news feed based on their connections."""
        # Clear existing feed to regenerate
        self.feed_repository.clear_user_feed(user_id)

        # Get user's accepted connections
        accepted_connections = self.connection_manager.get_accepted_connections(user_id)

        # Get connected user IDs
        connected_user_ids = set()
        for connection in accepted_connections:
            other_user_id = connection.get_other_user(user_id)
            if other_user_id:
                connected_user_ids.add(other_user_id)

        # Get messages from connected users
        feed_items = []
        for connected_user_id in connected_user_ids:
            user_messages = self.message_repository.get_messages_by_author(connected_user_id)

            for message in user_messages:
                author = self.user_repository.get_user_by_id(connected_user_id)
                author_profile = self.profile_repository.get_profile_by_user_id(connected_user_id)

                if author:
                    feed_item_id = f"feed_{user_id}_{message.message_id}"
                    feed_item = NewsFeedItem(feed_item_id, user_id, message, author, author_profile)
                    feed_items.append(feed_item)

        # Save feed items
        for feed_item in feed_items:
            self.feed_repository.save_feed_item(feed_item)

        # Mark feed as refreshed
        self.feed_repository.refresh_user_feed(user_id)

        return self.feed_repository.get_user_feed(user_id)

    def get_user_feed(self, user_id: str, limit: int = 20) -> List[NewsFeedItem]:
        """Get a user's news feed items."""
        return self.feed_repository.get_feed_items_for_user(user_id, limit)

    def refresh_user_feed(self, user_id: str) -> None:
        """Refresh a user's feed by regenerating it."""
        self.generate_feed_for_user(user_id)

    def get_feed_item_count(self, user_id: str) -> int:
        """Get the number of items in a user's feed."""
        return len(self.feed_repository.get_feed_items_for_user(user_id, limit=1000))
