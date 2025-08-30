"""
Unit tests for LinkedIn orchestrator module.

Tests the main system coordinator and its high-level operations.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orchestrator import LinkedInSystem
from entities import User, Profile, Message, Connection, NewsFeedItem


class TestLinkedInSystem(unittest.TestCase):
    """Test cases for LinkedInSystem orchestrator."""

    def setUp(self):
        """Set up test fixtures."""
        self.system = LinkedInSystem()
        self.user = User("user_001", "john@email.com", "John", "Doe")
        self.profile = Profile("user_001", "Software Engineer", "Experienced", "SF")
        self.message = Message("msg_001", "user_001", "Hello world!")
        self.connection = Connection("conn_001", "user_001", "user_002")

    def test_create_user_with_profile(self):
        """Test creating user with profile."""
        user, profile = self.system.create_user_with_profile(
            "user_001", "john@email.com", "John", "Doe",
            "Software Engineer", "Experienced", "SF"
        )
        
        self.assertEqual(user.user_id, "user_001")
        self.assertEqual(user.email, "john@email.com")
        self.assertEqual(profile.user_id, "user_001")
        self.assertEqual(profile.headline, "Software Engineer")

    def test_get_user_profile(self):
        """Test getting user profile."""
        # First create a user and profile
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        
        user, profile = self.system.get_user_profile("user_001")
        
        self.assertIsNotNone(user)
        self.assertIsNotNone(profile)
        self.assertEqual(user.user_id, "user_001")
        self.assertEqual(profile.user_id, "user_001")

    def test_get_user_profile_nonexistent(self):
        """Test getting user profile for non-existent user."""
        user, profile = self.system.get_user_profile("nonexistent")
        
        self.assertIsNone(user)
        self.assertIsNone(profile)

    def test_update_user_profile(self):
        """Test updating user profile."""
        # First create a user and profile
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        
        updated_profile = self.system.update_user_profile(
            "user_001", "Senior Engineer", "Very experienced", "NY"
        )
        
        self.assertIsNotNone(updated_profile)
        self.assertEqual(updated_profile.headline, "Senior Engineer")
        self.assertEqual(updated_profile.summary, "Very experienced")
        self.assertEqual(updated_profile.location, "NY")

    def test_get_all_users(self):
        """Test getting all users."""
        # Create some users
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        users = self.system.get_all_users()
        
        self.assertEqual(len(users), 2)
        user_ids = [user.user_id for user in users]
        self.assertIn("user_001", user_ids)
        self.assertIn("user_002", user_ids)

    def test_post_message(self):
        """Test posting a message."""
        # First create a user
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        
        message = self.system.post_message("msg_001", "user_001", "Hello LinkedIn!")
        
        self.assertEqual(message.message_id, "msg_001")
        self.assertEqual(message.author_id, "user_001")
        self.assertEqual(message.content, "Hello LinkedIn!")

    def test_get_user_messages(self):
        """Test getting user messages."""
        # First create a user and post messages
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.post_message("msg_001", "user_001", "First message")
        self.system.post_message("msg_002", "user_001", "Second message")
        
        messages = self.system.get_user_messages("user_001")
        
        self.assertEqual(len(messages), 2)
        message_contents = [msg.content for msg in messages]
        self.assertIn("First message", message_contents)
        self.assertIn("Second message", message_contents)

    def test_get_all_messages(self):
        """Test getting all messages."""
        # Create users and post messages
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.post_message("msg_001", "user_001", "Message from John")
        self.system.post_message("msg_002", "user_002", "Message from Jane")
        
        messages = self.system.get_all_messages()
        
        self.assertEqual(len(messages), 2)
        message_contents = [msg.content for msg in messages]
        self.assertIn("Message from John", message_contents)
        self.assertIn("Message from Jane", message_contents)

    def test_update_message(self):
        """Test updating a message."""
        # First create a user and post a message
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.post_message("msg_001", "user_001", "Original message")
        
        updated_message = self.system.update_message("msg_001", "user_001", "Updated message")
        
        self.assertIsNotNone(updated_message)
        self.assertEqual(updated_message.content, "Updated message")

    def test_delete_message(self):
        """Test deleting a message."""
        # First create a user and post a message
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.post_message("msg_001", "user_001", "Test message")
        
        # Verify message exists
        messages = self.system.get_all_messages()
        self.assertEqual(len(messages), 1)
        
        # Delete the message
        result = self.system.delete_message("msg_001", "user_001")
        
        self.assertTrue(result)
        
        # Verify message is deleted
        messages = self.system.get_all_messages()
        self.assertEqual(len(messages), 0)

    def test_send_connection_request(self):
        """Test sending connection request."""
        # Create users
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        connection = self.system.send_connection_request("conn_001", "user_001", "user_002")
        
        self.assertEqual(connection.connection_id, "conn_001")
        self.assertEqual(connection.sender_id, "user_001")
        self.assertEqual(connection.receiver_id, "user_002")
        self.assertEqual(connection.status, "pending")

    def test_accept_connection_request(self):
        """Test accepting connection request."""
        # Create users and send connection request
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        
        accepted_connection = self.system.accept_connection_request("conn_001", "user_002")
        
        self.assertIsNotNone(accepted_connection)
        self.assertEqual(accepted_connection.status, "accepted")

    def test_reject_connection_request(self):
        """Test rejecting connection request."""
        # Create users and send connection request
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        
        rejected_connection = self.system.reject_connection_request("conn_001", "user_002")
        
        self.assertIsNotNone(rejected_connection)
        self.assertEqual(rejected_connection.status, "rejected")

    def test_get_user_connections(self):
        """Test getting user connections."""
        # Create users and establish connections
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.create_user_with_profile("user_003", "bob@email.com", "Bob", "Johnson")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        self.system.send_connection_request("conn_002", "user_001", "user_003")
        
        # Get all connections for user_001
        connections = self.system.get_user_connections("user_001")
        self.assertEqual(len(connections), 2)
        
        # Get accepted connections for user_001
        accepted_connections = self.system.get_user_connections("user_001", "accepted")
        self.assertEqual(len(accepted_connections), 1)
        
        # Get pending connections for user_001
        pending_connections = self.system.get_user_connections("user_001", "pending")
        self.assertEqual(len(pending_connections), 1)

    def test_get_accepted_connections(self):
        """Test getting accepted connections."""
        # Create users and establish accepted connection
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        accepted_connections = self.system.get_accepted_connections("user_001")
        
        self.assertEqual(len(accepted_connections), 1)
        self.assertEqual(accepted_connections[0].status, "accepted")

    def test_get_pending_requests(self):
        """Test getting pending requests."""
        # Create users and send connection requests
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.create_user_with_profile("user_003", "bob@email.com", "Bob", "Johnson")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.send_connection_request("conn_002", "user_003", "user_001")
        
        pending_requests = self.system.get_pending_requests("user_001")
        
        self.assertEqual(len(pending_requests), 2)

    def test_get_sent_requests(self):
        """Test getting sent requests."""
        # Create users and send connection requests
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.create_user_with_profile("user_003", "bob@email.com", "Bob", "Johnson")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.send_connection_request("conn_002", "user_001", "user_003")
        
        sent_requests = self.system.get_sent_requests("user_001")
        
        self.assertEqual(len(sent_requests), 2)

    def test_get_received_requests(self):
        """Test getting received requests."""
        # Create users and send connection requests
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.create_user_with_profile("user_003", "bob@email.com", "Bob", "Johnson")
        
        self.system.send_connection_request("conn_001", "user_002", "user_001")
        self.system.send_connection_request("conn_002", "user_003", "user_001")
        
        received_requests = self.system.get_received_requests("user_001")
        
        self.assertEqual(len(received_requests), 2)

    def test_remove_connection(self):
        """Test removing a connection."""
        # Create users and establish connection
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        # Verify connection exists
        accepted_connections = self.system.get_accepted_connections("user_001")
        self.assertEqual(len(accepted_connections), 1)
        
        # Remove connection
        result = self.system.remove_connection("conn_001", "user_001")
        
        self.assertTrue(result)
        
        # Verify connection is removed
        accepted_connections = self.system.get_accepted_connections("user_001")
        self.assertEqual(len(accepted_connections), 0)

    def test_are_connected(self):
        """Test checking if users are connected."""
        # Create users and establish connection
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        # Initially not connected
        self.assertFalse(self.system.are_connected("user_001", "user_002"))
        
        # Send and accept connection request
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        # Now connected
        self.assertTrue(self.system.are_connected("user_001", "user_002"))

    def test_get_user_feed(self):
        """Test getting user feed."""
        # Create users, establish connection, and post messages
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        self.system.post_message("msg_001", "user_002", "Message from Jane")
        
        # Refresh feed and get items
        self.system.refresh_user_feed("user_001")
        feed_items = self.system.get_user_feed("user_001")
        
        self.assertEqual(len(feed_items), 1)
        self.assertEqual(feed_items[0].message.content, "Message from Jane")

    def test_refresh_user_feed(self):
        """Test refreshing user feed."""
        # Create users and establish connection
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        # Post message and refresh feed
        self.system.post_message("msg_001", "user_002", "Message from Jane")
        self.system.refresh_user_feed("user_001")
        
        feed_items = self.system.get_user_feed("user_001")
        self.assertEqual(len(feed_items), 1)

    def test_get_feed_item_count(self):
        """Test getting feed item count."""
        # Create users, establish connection, and post messages
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        self.system.post_message("msg_001", "user_002", "Message 1")
        self.system.post_message("msg_002", "user_002", "Message 2")
        
        self.system.refresh_user_feed("user_001")
        count = self.system.get_feed_item_count("user_001")
        
        self.assertEqual(count, 2)

    def test_get_notification_stats(self):
        """Test getting notification statistics."""
        stats = self.system.get_notification_stats()
        
        self.assertIn("emails_sent", stats)
        self.assertIn("sms_sent", stats)
        self.assertIn("push_notifications_sent", stats)
        
        # Initially should be 0
        self.assertEqual(stats["emails_sent"], 0)
        self.assertEqual(stats["sms_sent"], 0)
        self.assertEqual(stats["push_notifications_sent"], 0)

    def test_clear_notification_history(self):
        """Test clearing notification history."""
        # Send some notifications first
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        
        # Check that notifications were sent
        stats_before = self.system.get_notification_stats()
        self.assertGreater(stats_before["emails_sent"], 0)
        
        # Clear history
        self.system.clear_notification_history()
        
        # Check that notifications are cleared
        stats_after = self.system.get_notification_stats()
        self.assertEqual(stats_after["emails_sent"], 0)
        self.assertEqual(stats_after["sms_sent"], 0)
        self.assertEqual(stats_after["push_notifications_sent"], 0)

    def test_get_system_stats(self):
        """Test getting system statistics."""
        # Create some data
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        self.system.post_message("msg_001", "user_001", "Message 1")
        self.system.post_message("msg_002", "user_002", "Message 2")
        
        self.system.send_connection_request("conn_001", "user_001", "user_002")
        self.system.accept_connection_request("conn_001", "user_002")
        
        self.system.refresh_user_feed("user_001")
        
        stats = self.system.get_system_stats()
        
        self.assertIn("total_users", stats)
        self.assertIn("total_messages", stats)
        self.assertIn("total_connections", stats)
        self.assertIn("total_feeds", stats)
        self.assertIn("notifications", stats)
        
        self.assertEqual(stats["total_users"], 2)
        self.assertEqual(stats["total_messages"], 2)
        self.assertEqual(stats["total_connections"], 1)
        self.assertEqual(stats["total_feeds"], 1)

    def test_error_handling_invalid_user_creation(self):
        """Test error handling for invalid user creation."""
        with self.assertRaises(ValueError):
            self.system.create_user_with_profile("", "john@email.com", "John", "Doe")

    def test_error_handling_duplicate_user(self):
        """Test error handling for duplicate user creation."""
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        
        with self.assertRaises(ValueError):
            self.system.create_user_with_profile("user_002", "john@email.com", "Jane", "Smith")

    def test_error_handling_invalid_message(self):
        """Test error handling for invalid message posting."""
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        
        with self.assertRaises(ValueError):
            self.system.post_message("msg_001", "user_001", "")

    def test_error_handling_unauthorized_message_update(self):
        """Test error handling for unauthorized message update."""
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        self.system.create_user_with_profile("user_002", "jane@email.com", "Jane", "Smith")
        
        self.system.post_message("msg_001", "user_001", "Original message")
        
        with self.assertRaises(ValueError):
            self.system.update_message("msg_001", "user_002", "Unauthorized update")

    def test_error_handling_self_connection(self):
        """Test error handling for self-connection attempt."""
        self.system.create_user_with_profile("user_001", "john@email.com", "John", "Doe")
        
        with self.assertRaises(ValueError):
            self.system.send_connection_request("conn_001", "user_001", "user_001")


if __name__ == '__main__':
    unittest.main()
