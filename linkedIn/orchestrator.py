"""
LinkedIn System Orchestrator

Main system orchestrator coordinating all managers, repositories, and services.
"""

from typing import List, Optional

from entities import User, Profile, Message, Connection, NewsFeedItem
from repositories import (
    InMemoryUserRepository, InMemoryProfileRepository, InMemoryMessageRepository,
    InMemoryConnectionRepository, InMemoryNewsFeedRepository
)
from managers import UserManager, ProfileManager, MessageManager, ConnectionManager, NewsFeedManager
from services import MockEmailService, MockSMSService, MockPushNotificationService, NotificationService


class LinkedInSystem:
    """Main system orchestrator coordinating all components."""

    def __init__(self) -> None:
        # Initialize repositories
        self.user_repository = InMemoryUserRepository()
        self.profile_repository = InMemoryProfileRepository()
        self.message_repository = InMemoryMessageRepository()
        self.connection_repository = InMemoryConnectionRepository()
        self.feed_repository = InMemoryNewsFeedRepository()

        # Initialize managers
        self.user_manager = UserManager(self.user_repository)
        self.profile_manager = ProfileManager(self.profile_repository)
        self.message_manager = MessageManager(self.message_repository, self.user_repository)
        self.connection_manager = ConnectionManager(self.connection_repository, self.user_repository)
        self.feed_manager = NewsFeedManager(self.feed_repository, self.message_repository,
                                          self.connection_manager, self.user_repository,
                                          self.profile_repository)

        # Initialize external services
        self.email_service = MockEmailService()
        self.sms_service = MockSMSService()
        self.push_service = MockPushNotificationService()
        self.notification_service = NotificationService(self.email_service, self.sms_service, self.push_service)

    # User and Profile Operations
    def create_user_with_profile(self, user_id: str, email: str, first_name: str, last_name: str,
                               headline: str = "", summary: str = "", location: str = "") -> tuple[User, Profile]:
        """Create a user along with their profile."""
        user = self.user_manager.create_user(user_id, email, first_name, last_name)
        profile = self.profile_manager.create_profile(user_id, headline, summary, location)
        return user, profile

    def get_user_profile(self, user_id: str) -> tuple[Optional[User], Optional[Profile]]:
        """Retrieve both user and profile information."""
        user = self.user_manager.get_user(user_id)
        profile = self.profile_manager.get_profile(user_id)
        return user, profile

    def update_user_profile(self, user_id: str, headline: str = "", summary: str = "", location: str = "") -> Optional[Profile]:
        """Update a user's profile."""
        return self.profile_manager.update_profile(user_id, headline, summary, location)

    def get_all_users(self) -> List[User]:
        """Get all users in the system."""
        return self.user_manager.get_all_users()

    # Message Operations
    def post_message(self, message_id: str, author_id: str, content: str) -> Message:
        """Post a new message."""
        return self.message_manager.post_message(message_id, author_id, content)

    def get_user_messages(self, user_id: str) -> List[Message]:
        """Get all messages posted by a user."""
        return self.message_manager.get_user_messages(user_id)

    def get_all_messages(self) -> List[Message]:
        """Get all messages in the system."""
        return self.message_manager.get_all_messages()

    def update_message(self, message_id: str, user_id: str, new_content: str) -> Optional[Message]:
        """Update a message if user is the author."""
        return self.message_manager.update_message(message_id, user_id, new_content)

    def delete_message(self, message_id: str, user_id: str) -> bool:
        """Delete a message if user is the author."""
        return self.message_manager.delete_message(message_id, user_id)

    # Connection Operations
    def send_connection_request(self, connection_id: str, sender_id: str, receiver_id: str) -> Connection:
        """Send a connection request with notifications."""
        connection = self.connection_manager.send_connection_request(connection_id, sender_id, receiver_id)
        
        # Send notifications
        sender_user = self.user_manager.get_user(sender_id)
        receiver_user = self.user_manager.get_user(receiver_id)
        
        if sender_user and receiver_user:
            # For now, we'll use mock phone numbers - in a real system, these would come from user profiles
            receiver_phone = None  # Would be retrieved from user profile in real system
            self.notification_service.notify_connection_request(
                receiver_user.email, receiver_phone, receiver_id, sender_user.get_full_name()
            )
        
        return connection

    def accept_connection_request(self, connection_id: str, user_id: str) -> Optional[Connection]:
        """Accept a connection request with notifications."""
        connection = self.connection_manager.accept_connection_request(connection_id, user_id)
        
        if connection:
            # Send notifications
            accepter_user = self.user_manager.get_user(user_id)
            sender_user = self.user_manager.get_user(connection.sender_id)
            
            if accepter_user and sender_user:
                # For now, we'll use mock phone numbers
                sender_phone = None  # Would be retrieved from user profile in real system
                self.notification_service.notify_connection_accepted(
                    sender_user.email, sender_phone, connection.sender_id, accepter_user.get_full_name()
                )
        
        return connection

    def reject_connection_request(self, connection_id: str, user_id: str) -> Optional[Connection]:
        """Reject a connection request."""
        return self.connection_manager.reject_connection_request(connection_id, user_id)

    def get_user_connections(self, user_id: str, status: Optional[str] = None) -> List[Connection]:
        """Get user's connections, optionally filtered by status."""
        return self.connection_manager.get_user_connections(user_id, status)

    def get_accepted_connections(self, user_id: str) -> List[Connection]:
        """Get user's accepted connections."""
        return self.connection_manager.get_accepted_connections(user_id)

    def get_pending_requests(self, user_id: str) -> List[Connection]:
        """Get user's pending connection requests."""
        return self.connection_manager.get_pending_requests(user_id)

    def get_sent_requests(self, user_id: str) -> List[Connection]:
        """Get connection requests sent by the user."""
        return self.connection_manager.get_sent_requests(user_id)

    def get_received_requests(self, user_id: str) -> List[Connection]:
        """Get connection requests received by the user."""
        return self.connection_manager.get_received_requests(user_id)

    def remove_connection(self, connection_id: str, user_id: str) -> bool:
        """Remove a connection."""
        return self.connection_manager.remove_connection(connection_id, user_id)

    def are_connected(self, user_id1: str, user_id2: str) -> bool:
        """Check if two users are connected."""
        return self.connection_manager.are_connected(user_id1, user_id2)

    # News Feed Operations
    def get_user_feed(self, user_id: str, limit: int = 20) -> List[NewsFeedItem]:
        """Get a user's news feed."""
        return self.feed_manager.get_user_feed(user_id, limit)

    def refresh_user_feed(self, user_id: str) -> None:
        """Refresh a user's news feed."""
        self.feed_manager.refresh_user_feed(user_id)

    def get_feed_item_count(self, user_id: str) -> int:
        """Get the number of items in a user's feed."""
        return self.feed_manager.get_feed_item_count(user_id)

    # Notification Operations
    def get_notification_stats(self) -> dict:
        """Get statistics about sent notifications for testing purposes."""
        return {
            "emails_sent": len(self.email_service.get_sent_emails()),
            "sms_sent": len(self.sms_service.get_sent_sms()),
            "push_notifications_sent": len(self.push_service.get_sent_notifications())
        }

    def clear_notification_history(self) -> None:
        """Clear notification history for testing purposes."""
        self.email_service.clear_sent_emails()
        self.sms_service.clear_sent_sms()
        self.push_service.clear_sent_notifications()

    # System Information
    def get_system_stats(self) -> dict:
        """Get overall system statistics."""
        return {
            "total_users": len(self.user_manager.get_all_users()),
            "total_messages": len(self.message_manager.get_all_messages()),
            "total_connections": len(self.connection_repository.get_all_connections()),
            "total_feeds": len(self.feed_repository.feeds),
            "notifications": self.get_notification_stats()
        }
