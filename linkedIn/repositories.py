"""
LinkedIn Repositories

Abstract base classes and in-memory implementations for entity storage.
Designed to be extended for other storage systems (e.g., MySQL).
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional

from entities import User, Profile, Message, Connection, NewsFeed, NewsFeedItem


class AbstractUserRepository(ABC):
    """Abstract base class for user repository operations."""

    @abstractmethod
    def save_user(self, user: User) -> None:
        """Save a user to the repository."""
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email."""
        pass

    @abstractmethod
    def get_all_users(self) -> List[User]:
        """Retrieve all users."""
        pass


class InMemoryUserRepository(AbstractUserRepository):
    """In-memory implementation of user repository."""

    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self.email_index: Dict[str, str] = {}  # email -> user_id

    def save_user(self, user: User) -> None:
        """Save a user to the in-memory store."""
        self.users[user.user_id] = user
        self.email_index[user.email] = user.user_id

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Retrieve a user by their ID from in-memory store."""
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Retrieve a user by their email from in-memory store."""
        user_id = self.email_index.get(email)
        if user_id:
            return self.users.get(user_id)
        return None

    def get_all_users(self) -> List[User]:
        """Retrieve all users from in-memory store."""
        return list(self.users.values())


class AbstractProfileRepository(ABC):
    """Abstract base class for profile repository operations."""

    @abstractmethod
    def save_profile(self, profile: Profile) -> None:
        """Save a profile to the repository."""
        pass

    @abstractmethod
    def get_profile_by_user_id(self, user_id: str) -> Optional[Profile]:
        """Retrieve a profile by user ID."""
        pass

    @abstractmethod
    def get_all_profiles(self) -> List[Profile]:
        """Retrieve all profiles."""
        pass


class InMemoryProfileRepository(AbstractProfileRepository):
    """In-memory implementation of profile repository."""

    def __init__(self) -> None:
        self.profiles: Dict[str, Profile] = {}  # user_id -> profile

    def save_profile(self, profile: Profile) -> None:
        """Save a profile to the in-memory store."""
        self.profiles[profile.user_id] = profile

    def get_profile_by_user_id(self, user_id: str) -> Optional[Profile]:
        """Retrieve a profile by user ID from in-memory store."""
        return self.profiles.get(user_id)

    def get_all_profiles(self) -> List[Profile]:
        """Retrieve all profiles from in-memory store."""
        return list(self.profiles.values())


class AbstractMessageRepository(ABC):
    """Abstract base class for message repository operations."""

    @abstractmethod
    def save_message(self, message: Message) -> None:
        """Save a message to the repository."""
        pass

    @abstractmethod
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """Retrieve a message by its ID."""
        pass

    @abstractmethod
    def get_messages_by_author(self, author_id: str) -> List[Message]:
        """Retrieve all messages by a specific author."""
        pass

    @abstractmethod
    def get_all_messages(self) -> List[Message]:
        """Retrieve all messages."""
        pass

    @abstractmethod
    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID. Returns True if deleted, False if not found."""
        pass


class InMemoryMessageRepository(AbstractMessageRepository):
    """In-memory implementation of message repository."""

    def __init__(self) -> None:
        self.messages: Dict[str, Message] = {}  # message_id -> message
        self.author_index: Dict[str, List[str]] = {}  # author_id -> list of message_ids

    def save_message(self, message: Message) -> None:
        """Save a message to the in-memory store."""
        self.messages[message.message_id] = message

        # Update author index
        if message.author_id not in self.author_index:
            self.author_index[message.author_id] = []
        if message.message_id not in self.author_index[message.author_id]:
            self.author_index[message.author_id].append(message.message_id)

    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        """Retrieve a message by its ID from in-memory store."""
        return self.messages.get(message_id)

    def get_messages_by_author(self, author_id: str) -> List[Message]:
        """Retrieve all messages by a specific author from in-memory store."""
        message_ids = self.author_index.get(author_id, [])
        return [self.messages[mid] for mid in message_ids if mid in self.messages]

    def get_all_messages(self) -> List[Message]:
        """Retrieve all messages from in-memory store, sorted by creation time (newest first)."""
        return sorted(self.messages.values(), key=lambda m: m.created_at, reverse=True)

    def delete_message(self, message_id: str) -> bool:
        """Delete a message by its ID from in-memory store."""
        if message_id not in self.messages:
            return False

        message = self.messages[message_id]

        # Remove from main storage
        del self.messages[message_id]

        # Remove from author index
        if message.author_id in self.author_index:
            if message_id in self.author_index[message.author_id]:
                self.author_index[message.author_id].remove(message_id)
            # Clean up empty author entries
            if not self.author_index[message.author_id]:
                del self.author_index[message.author_id]

        return True


class AbstractConnectionRepository(ABC):
    """Abstract base class for connection repository operations."""

    @abstractmethod
    def save_connection(self, connection: Connection) -> None:
        """Save a connection to the repository."""
        pass

    @abstractmethod
    def get_connection_by_id(self, connection_id: str) -> Optional[Connection]:
        """Retrieve a connection by its ID."""
        pass

    @abstractmethod
    def get_connections_by_user(self, user_id: str, status: Optional[str] = None) -> List[Connection]:
        """Retrieve all connections for a user, optionally filtered by status."""
        pass

    @abstractmethod
    def get_connection_between_users(self, user_id1: str, user_id2: str) -> Optional[Connection]:
        """Get connection between two specific users if it exists."""
        pass

    @abstractmethod
    def get_all_connections(self) -> List[Connection]:
        """Retrieve all connections."""
        pass

    @abstractmethod
    def delete_connection(self, connection_id: str) -> bool:
        """Delete a connection by its ID. Returns True if deleted, False if not found."""
        pass


class InMemoryConnectionRepository(AbstractConnectionRepository):
    """In-memory implementation of connection repository."""

    def __init__(self) -> None:
        self.connections: Dict[str, Connection] = {}  # connection_id -> connection
        self.user_index: Dict[str, List[str]] = {}  # user_id -> list of connection_ids

    def save_connection(self, connection: Connection) -> None:
        """Save a connection to the in-memory store."""
        self.connections[connection.connection_id] = connection

        # Update user index for both users
        for user_id in [connection.sender_id, connection.receiver_id]:
            if user_id not in self.user_index:
                self.user_index[user_id] = []
            if connection.connection_id not in self.user_index[user_id]:
                self.user_index[user_id].append(connection.connection_id)

    def get_connection_by_id(self, connection_id: str) -> Optional[Connection]:
        """Retrieve a connection by its ID from in-memory store."""
        return self.connections.get(connection_id)

    def get_connections_by_user(self, user_id: str, status: Optional[str] = None) -> List[Connection]:
        """Retrieve all connections for a user from in-memory store."""
        connection_ids = self.user_index.get(user_id, [])
        connections = [self.connections[cid] for cid in connection_ids if cid in self.connections]

        if status:
            connections = [c for c in connections if c.status == status]

        return connections

    def get_connection_between_users(self, user_id1: str, user_id2: str) -> Optional[Connection]:
        """Get connection between two specific users if it exists."""
        user1_connections = self.get_connections_by_user(user_id1)

        for connection in user1_connections:
            if connection.involves_user(user_id2):
                return connection

        return None

    def get_all_connections(self) -> List[Connection]:
        """Retrieve all connections from in-memory store."""
        return list(self.connections.values())

    def delete_connection(self, connection_id: str) -> bool:
        """Delete a connection by its ID from in-memory store."""
        if connection_id not in self.connections:
            return False

        connection = self.connections[connection_id]

        # Remove from main storage
        del self.connections[connection_id]

        # Remove from user indices
        for user_id in [connection.sender_id, connection.receiver_id]:
            if user_id in self.user_index:
                if connection_id in self.user_index[user_id]:
                    self.user_index[user_id].remove(connection_id)
                # Clean up empty user entries
                if not self.user_index[user_id]:
                    del self.user_index[user_id]

        return True


class AbstractNewsFeedRepository(ABC):
    """Abstract base class for news feed repository operations."""

    @abstractmethod
    def save_feed_item(self, feed_item: NewsFeedItem) -> None:
        """Save a feed item to the repository."""
        pass

    @abstractmethod
    def get_user_feed(self, user_id: str) -> NewsFeed:
        """Get or create a user's news feed."""
        pass

    @abstractmethod
    def get_feed_items_for_user(self, user_id: str, limit: int = 20) -> List[NewsFeedItem]:
        """Get feed items for a user."""
        pass

    @abstractmethod
    def refresh_user_feed(self, user_id: str) -> None:
        """Mark a user's feed as refreshed."""
        pass

    @abstractmethod
    def clear_user_feed(self, user_id: str) -> None:
        """Clear all items from a user's feed."""
        pass


class InMemoryNewsFeedRepository(AbstractNewsFeedRepository):
    """In-memory implementation of news feed repository."""

    def __init__(self):
        self.feeds: Dict[str, NewsFeed] = {}  # user_id -> NewsFeed

    def save_feed_item(self, feed_item: NewsFeedItem) -> None:
        """Save a feed item to the in-memory store."""
        if feed_item.user_id not in self.feeds:
            self.feeds[feed_item.user_id] = NewsFeed(feed_item.user_id)

        self.feeds[feed_item.user_id].add_item(feed_item)

    def get_user_feed(self, user_id: str) -> NewsFeed:
        """Get or create a user's news feed."""
        if user_id not in self.feeds:
            self.feeds[user_id] = NewsFeed(user_id)
        return self.feeds[user_id]

    def get_feed_items_for_user(self, user_id: str, limit: int = 20) -> List[NewsFeedItem]:
        """Get feed items for a user."""
        if user_id not in self.feeds:
            return []
        return self.feeds[user_id].get_recent_items(limit)

    def refresh_user_feed(self, user_id: str) -> None:
        """Mark a user's feed as refreshed."""
        if user_id in self.feeds:
            self.feeds[user_id].refresh_feed()

    def clear_user_feed(self, user_id: str) -> None:
        """Clear all items from a user's feed."""
        if user_id in self.feeds:
            self.feeds[user_id].feed_items.clear()
            self.feeds[user_id].refresh_feed()
