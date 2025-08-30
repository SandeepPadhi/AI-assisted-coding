"""
LinkedIn Entities

Core business objects with their invariants and business logic.
"""

from datetime import datetime
from typing import Optional


class User:
    """Entity representing a LinkedIn user with basic profile information."""

    def __init__(self, user_id: str, email: str, first_name: str, last_name: str) -> None:
        self.user_id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.created_at = datetime.now()

    def get_full_name(self) -> str:
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}"

    def validate_email(self) -> bool:
        """Basic email validation."""
        return "@" in self.email and "." in self.email


class Profile:
    """Entity representing a user's profile information."""

    def __init__(self, user_id: str, headline: str = "", summary: str = "", location: str = "") -> None:
        self.user_id = user_id
        self.headline = headline
        self.summary = summary
        self.location = location
        self.updated_at = datetime.now()

    def update_profile(self, headline: str = "", summary: str = "", location: str = "") -> None:
        """Update profile information."""
        if headline:
            self.headline = headline
        if summary:
            self.summary = summary
        if location:
            self.location = location
        self.updated_at = datetime.now()


class Message:
    """Entity representing a user's message/post."""

    def __init__(self, message_id: str, author_id: str, content: str) -> None:
        self.message_id = message_id
        self.author_id = author_id
        self.content = content
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update_content(self, new_content: str) -> None:
        """Update message content."""
        if not new_content.strip():
            raise ValueError("Message content cannot be empty")
        self.content = new_content.strip()
        self.updated_at = datetime.now()

    def is_author(self, user_id: str) -> bool:
        """Check if the given user is the author of this message."""
        return self.author_id == user_id


class Connection:
    """Entity representing a connection relationship between two users."""

    def __init__(self, connection_id: str, sender_id: str, receiver_id: str) -> None:
        self.connection_id = connection_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.status = "pending"  # pending, accepted, rejected
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def accept(self) -> None:
        """Accept the connection request."""
        if self.status == "pending":
            self.status = "accepted"
            self.updated_at = datetime.now()

    def reject(self) -> None:
        """Reject the connection request."""
        if self.status == "pending":
            self.status = "rejected"
            self.updated_at = datetime.now()

    def is_pending(self) -> bool:
        """Check if connection is pending."""
        return self.status == "pending"

    def is_accepted(self) -> bool:
        """Check if connection is accepted."""
        return self.status == "accepted"

    def is_rejected(self) -> bool:
        """Check if connection is rejected."""
        return self.status == "rejected"

    def involves_user(self, user_id: str) -> bool:
        """Check if the given user is involved in this connection."""
        return self.sender_id == user_id or self.receiver_id == user_id

    def get_other_user(self, user_id: str) -> Optional[str]:
        """Get the other user in this connection."""
        if self.sender_id == user_id:
            return self.receiver_id
        elif self.receiver_id == user_id:
            return self.sender_id
        return None


class NewsFeedItem:
    """Entity representing a single item in a user's news feed."""

    def __init__(self, feed_item_id: str, user_id: str, message: Message, author: User, author_profile: Optional[Profile]):
        self.feed_item_id = feed_item_id
        self.user_id = user_id  # The user who sees this in their feed
        self.message = message
        self.author = author
        self.author_profile = author_profile
        self.feed_timestamp = datetime.now()  # When this item was added to the feed

    def get_display_content(self) -> str:
        """Get formatted content for display in the feed."""
        headline = self.author_profile.headline if self.author_profile else "Professional"
        return f"{self.author.get_full_name()} ({headline})\n{self.message.content}"


class NewsFeed:
    """Entity representing a user's complete news feed."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.feed_items: list[NewsFeedItem] = []
        self.last_updated = datetime.now()

    def add_item(self, feed_item: NewsFeedItem) -> None:
        """Add a new item to the feed."""
        self.feed_items.append(feed_item)
        self.last_updated = datetime.now()
        # Sort by message creation time (newest first)
        self.feed_items.sort(key=lambda item: item.message.created_at, reverse=True)

    def get_recent_items(self, limit: int = 20) -> list[NewsFeedItem]:
        """Get the most recent items from the feed."""
        return self.feed_items[:limit]

    def refresh_feed(self) -> None:
        """Mark the feed as refreshed."""
        self.last_updated = datetime.now()
