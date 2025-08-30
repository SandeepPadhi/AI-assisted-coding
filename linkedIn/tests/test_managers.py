"""
Unit tests for LinkedIn managers module.

Tests all business logic managers and their operations including validation and business rules.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities import User, Profile, Message, Connection, NewsFeedItem
from managers import UserManager, ProfileManager, MessageManager, ConnectionManager, NewsFeedManager


class TestUserManager(unittest.TestCase):
    """Test cases for UserManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.manager = UserManager(self.mock_repository)
        self.user = User("user_001", "john@email.com", "John", "Doe")

    def test_create_user_valid_data(self):
        """Test creating user with valid data."""
        self.mock_repository.get_user_by_email.return_value = None
        
        result = self.manager.create_user("user_001", "john@email.com", "John", "Doe")
        
        self.assertEqual(result.user_id, "user_001")
        self.assertEqual(result.email, "john@email.com")
        self.assertEqual(result.first_name, "John")
        self.assertEqual(result.last_name, "Doe")
        self.mock_repository.save_user.assert_called_once_with(result)

    def test_create_user_missing_fields_raises_error(self):
        """Test creating user with missing fields raises error."""
        with self.assertRaises(ValueError) as context:
            self.manager.create_user("", "john@email.com", "John", "Doe")
        self.assertIn("All user fields are required", str(context.exception))

    def test_create_user_duplicate_email_raises_error(self):
        """Test creating user with duplicate email raises error."""
        self.mock_repository.get_user_by_email.return_value = self.user
        
        with self.assertRaises(ValueError) as context:
            self.manager.create_user("user_002", "john@email.com", "Jane", "Smith")
        self.assertIn("already exists", str(context.exception))

    def test_create_user_invalid_email_raises_error(self):
        """Test creating user with invalid email raises error."""
        self.mock_repository.get_user_by_email.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.manager.create_user("user_001", "invalid-email", "John", "Doe")
        self.assertIn("Invalid email format", str(context.exception))

    def test_get_user_existing(self):
        """Test getting existing user."""
        self.mock_repository.get_user_by_id.return_value = self.user
        
        result = self.manager.get_user("user_001")
        
        self.assertEqual(result, self.user)
        self.mock_repository.get_user_by_id.assert_called_once_with("user_001")

    def test_get_user_nonexistent(self):
        """Test getting non-existent user."""
        self.mock_repository.get_user_by_id.return_value = None
        
        result = self.manager.get_user("nonexistent")
        
        self.assertIsNone(result)

    def test_get_all_users(self):
        """Test getting all users."""
        users = [self.user, User("user_002", "jane@email.com", "Jane", "Smith")]
        self.mock_repository.get_all_users.return_value = users
        
        result = self.manager.get_all_users()
        
        self.assertEqual(result, users)
        self.mock_repository.get_all_users.assert_called_once()


class TestProfileManager(unittest.TestCase):
    """Test cases for ProfileManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_repository = Mock()
        self.manager = ProfileManager(self.mock_repository)
        self.profile = Profile("user_001", "Software Engineer", "Experienced", "SF")

    def test_create_profile(self):
        """Test creating a new profile."""
        result = self.manager.create_profile("user_001", "Software Engineer", "Experienced", "SF")
        
        self.assertEqual(result.user_id, "user_001")
        self.assertEqual(result.headline, "Software Engineer")
        self.assertEqual(result.summary, "Experienced")
        self.assertEqual(result.location, "SF")
        self.mock_repository.save_profile.assert_called_once_with(result)

    def test_create_profile_empty_fields(self):
        """Test creating profile with empty fields."""
        result = self.manager.create_profile("user_001")
        
        self.assertEqual(result.user_id, "user_001")
        self.assertEqual(result.headline, "")
        self.assertEqual(result.summary, "")
        self.assertEqual(result.location, "")

    def test_update_profile_existing(self):
        """Test updating existing profile."""
        self.mock_repository.get_profile_by_user_id.return_value = self.profile
        
        result = self.manager.update_profile("user_001", "Senior Engineer", "Very experienced", "NY")
        
        self.assertEqual(result.headline, "Senior Engineer")
        self.assertEqual(result.summary, "Very experienced")
        self.assertEqual(result.location, "NY")
        self.mock_repository.save_profile.assert_called_once_with(result)

    def test_update_profile_nonexistent(self):
        """Test updating non-existent profile."""
        self.mock_repository.get_profile_by_user_id.return_value = None
        
        result = self.manager.update_profile("user_001", "New headline")
        
        self.assertIsNone(result)

    def test_get_profile_existing(self):
        """Test getting existing profile."""
        self.mock_repository.get_profile_by_user_id.return_value = self.profile
        
        result = self.manager.get_profile("user_001")
        
        self.assertEqual(result, self.profile)
        self.mock_repository.get_profile_by_user_id.assert_called_once_with("user_001")

    def test_get_profile_nonexistent(self):
        """Test getting non-existent profile."""
        self.mock_repository.get_profile_by_user_id.return_value = None
        
        result = self.manager.get_profile("nonexistent")
        
        self.assertIsNone(result)


class TestMessageManager(unittest.TestCase):
    """Test cases for MessageManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_message_repository = Mock()
        self.mock_user_repository = Mock()
        self.manager = MessageManager(self.mock_message_repository, self.mock_user_repository)
        self.user = User("user_001", "john@email.com", "John", "Doe")
        self.message = Message("msg_001", "user_001", "Hello world!")

    def test_post_message_valid(self):
        """Test posting valid message."""
        self.mock_user_repository.get_user_by_id.return_value = self.user
        self.mock_message_repository.get_message_by_id.return_value = None
        
        result = self.manager.post_message("msg_001", "user_001", "Hello world!")
        
        self.assertEqual(result.message_id, "msg_001")
        self.assertEqual(result.author_id, "user_001")
        self.assertEqual(result.content, "Hello world!")
        self.mock_message_repository.save_message.assert_called_once_with(result)

    def test_post_message_missing_fields_raises_error(self):
        """Test posting message with missing fields raises error."""
        with self.assertRaises(ValueError) as context:
            self.manager.post_message("", "user_001", "Hello world!")
        self.assertIn("Message ID, author ID, and content are required", str(context.exception))

    def test_post_message_empty_content_raises_error(self):
        """Test posting message with empty content raises error."""
        with self.assertRaises(ValueError) as context:
            self.manager.post_message("msg_001", "user_001", "")
        self.assertIn("Message content cannot be empty", str(context.exception))

    def test_post_message_nonexistent_author_raises_error(self):
        """Test posting message with non-existent author raises error."""
        self.mock_user_repository.get_user_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.manager.post_message("msg_001", "nonexistent", "Hello world!")
        self.assertIn("does not exist", str(context.exception))

    def test_post_message_duplicate_id_raises_error(self):
        """Test posting message with duplicate ID raises error."""
        self.mock_user_repository.get_user_by_id.return_value = self.user
        self.mock_message_repository.get_message_by_id.return_value = self.message
        
        with self.assertRaises(ValueError) as context:
            self.manager.post_message("msg_001", "user_001", "Hello world!")
        self.assertIn("already exists", str(context.exception))

    def test_get_message_existing(self):
        """Test getting existing message."""
        self.mock_message_repository.get_message_by_id.return_value = self.message
        
        result = self.manager.get_message("msg_001")
        
        self.assertEqual(result, self.message)

    def test_get_message_nonexistent(self):
        """Test getting non-existent message."""
        self.mock_message_repository.get_message_by_id.return_value = None
        
        result = self.manager.get_message("nonexistent")
        
        self.assertIsNone(result)

    def test_get_user_messages(self):
        """Test getting user messages."""
        messages = [self.message, Message("msg_002", "user_001", "Second message")]
        self.mock_message_repository.get_messages_by_author.return_value = messages
        
        result = self.manager.get_user_messages("user_001")
        
        self.assertEqual(result, messages)
        self.mock_message_repository.get_messages_by_author.assert_called_once_with("user_001")

    def test_get_all_messages(self):
        """Test getting all messages."""
        messages = [self.message, Message("msg_002", "user_002", "From user 2")]
        self.mock_message_repository.get_all_messages.return_value = messages
        
        result = self.manager.get_all_messages()
        
        self.assertEqual(result, messages)

    def test_update_message_valid(self):
        """Test updating message with valid data."""
        self.mock_message_repository.get_message_by_id.return_value = self.message
        
        result = self.manager.update_message("msg_001", "user_001", "Updated content")
        
        self.assertEqual(result.content, "Updated content")
        self.mock_message_repository.save_message.assert_called_once_with(result)

    def test_update_message_nonexistent(self):
        """Test updating non-existent message."""
        self.mock_message_repository.get_message_by_id.return_value = None
        
        result = self.manager.update_message("nonexistent", "user_001", "Updated content")
        
        self.assertIsNone(result)

    def test_update_message_unauthorized_raises_error(self):
        """Test updating message by non-author raises error."""
        self.mock_message_repository.get_message_by_id.return_value = self.message
        
        with self.assertRaises(ValueError) as context:
            self.manager.update_message("msg_001", "user_002", "Updated content")
        self.assertIn("Only the author can update their message", str(context.exception))

    def test_delete_message_valid(self):
        """Test deleting message by author."""
        self.mock_message_repository.get_message_by_id.return_value = self.message
        self.mock_message_repository.delete_message.return_value = True
        
        result = self.manager.delete_message("msg_001", "user_001")
        
        self.assertTrue(result)
        self.mock_message_repository.delete_message.assert_called_once_with("msg_001")

    def test_delete_message_nonexistent(self):
        """Test deleting non-existent message."""
        self.mock_message_repository.get_message_by_id.return_value = None
        
        result = self.manager.delete_message("nonexistent", "user_001")
        
        self.assertFalse(result)

    def test_delete_message_unauthorized_raises_error(self):
        """Test deleting message by non-author raises error."""
        self.mock_message_repository.get_message_by_id.return_value = self.message
        
        with self.assertRaises(ValueError) as context:
            self.manager.delete_message("msg_001", "user_002")
        self.assertIn("Only the author can delete their message", str(context.exception))


class TestConnectionManager(unittest.TestCase):
    """Test cases for ConnectionManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_connection_repository = Mock()
        self.mock_user_repository = Mock()
        self.manager = ConnectionManager(self.mock_connection_repository, self.mock_user_repository)
        self.user1 = User("user_001", "john@email.com", "John", "Doe")
        self.user2 = User("user_002", "jane@email.com", "Jane", "Smith")
        self.connection = Connection("conn_001", "user_001", "user_002")

    def test_send_connection_request_valid(self):
        """Test sending valid connection request."""
        self.mock_user_repository.get_user_by_id.side_effect = [self.user1, self.user2]
        self.mock_connection_repository.get_connection_between_users.return_value = None
        self.mock_connection_repository.get_connection_by_id.return_value = None
        
        result = self.manager.send_connection_request("conn_001", "user_001", "user_002")
        
        self.assertEqual(result.connection_id, "conn_001")
        self.assertEqual(result.sender_id, "user_001")
        self.assertEqual(result.receiver_id, "user_002")
        self.mock_connection_repository.save_connection.assert_called_once_with(result)

    def test_send_connection_request_missing_fields_raises_error(self):
        """Test sending connection request with missing fields raises error."""
        with self.assertRaises(ValueError) as context:
            self.manager.send_connection_request("", "user_001", "user_002")
        self.assertIn("Connection ID, sender ID, and receiver ID are required", str(context.exception))

    def test_send_connection_request_self_connection_raises_error(self):
        """Test sending connection request to self raises error."""
        with self.assertRaises(ValueError) as context:
            self.manager.send_connection_request("conn_001", "user_001", "user_001")
        self.assertIn("Cannot connect to yourself", str(context.exception))

    def test_send_connection_request_nonexistent_sender_raises_error(self):
        """Test sending connection request with non-existent sender raises error."""
        self.mock_user_repository.get_user_by_id.side_effect = [None, self.user2]
        
        with self.assertRaises(ValueError) as context:
            self.manager.send_connection_request("conn_001", "nonexistent", "user_002")
        self.assertIn("does not exist", str(context.exception))

    def test_send_connection_request_nonexistent_receiver_raises_error(self):
        """Test sending connection request with non-existent receiver raises error."""
        self.mock_user_repository.get_user_by_id.side_effect = [self.user1, None]
        
        with self.assertRaises(ValueError) as context:
            self.manager.send_connection_request("conn_001", "user_001", "nonexistent")
        self.assertIn("does not exist", str(context.exception))

    def test_send_connection_request_existing_connection_raises_error(self):
        """Test sending connection request when connection already exists raises error."""
        self.mock_user_repository.get_user_by_id.side_effect = [self.user1, self.user2]
        self.mock_connection_repository.get_connection_between_users.return_value = self.connection
        
        with self.assertRaises(ValueError) as context:
            self.manager.send_connection_request("conn_001", "user_001", "user_002")
        self.assertIn("already exists", str(context.exception))

    def test_send_connection_request_duplicate_id_raises_error(self):
        """Test sending connection request with duplicate ID raises error."""
        self.mock_user_repository.get_user_by_id.side_effect = [self.user1, self.user2]
        self.mock_connection_repository.get_connection_between_users.return_value = None
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        with self.assertRaises(ValueError) as context:
            self.manager.send_connection_request("conn_001", "user_001", "user_002")
        self.assertIn("already exists", str(context.exception))

    def test_accept_connection_request_valid(self):
        """Test accepting valid connection request."""
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        result = self.manager.accept_connection_request("conn_001", "user_002")
        
        self.assertEqual(result.status, "accepted")
        self.mock_connection_repository.save_connection.assert_called_once_with(result)

    def test_accept_connection_request_nonexistent(self):
        """Test accepting non-existent connection request."""
        self.mock_connection_repository.get_connection_by_id.return_value = None
        
        result = self.manager.accept_connection_request("nonexistent", "user_002")
        
        self.assertIsNone(result)

    def test_accept_connection_request_unauthorized_raises_error(self):
        """Test accepting connection request by non-receiver raises error."""
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        with self.assertRaises(ValueError) as context:
            self.manager.accept_connection_request("conn_001", "user_001")
        self.assertIn("Only the receiver can accept", str(context.exception))

    def test_accept_connection_request_not_pending_raises_error(self):
        """Test accepting non-pending connection request raises error."""
        self.connection.accept()  # Make it accepted
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        with self.assertRaises(ValueError) as context:
            self.manager.accept_connection_request("conn_001", "user_002")
        self.assertIn("not pending", str(context.exception))

    def test_reject_connection_request_valid(self):
        """Test rejecting valid connection request."""
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        result = self.manager.reject_connection_request("conn_001", "user_002")
        
        self.assertEqual(result.status, "rejected")
        self.mock_connection_repository.save_connection.assert_called_once_with(result)

    def test_reject_connection_request_unauthorized_raises_error(self):
        """Test rejecting connection request by non-receiver raises error."""
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        with self.assertRaises(ValueError) as context:
            self.manager.reject_connection_request("conn_001", "user_001")
        self.assertIn("Only the receiver can reject", str(context.exception))

    def test_get_connection_existing(self):
        """Test getting existing connection."""
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        result = self.manager.get_connection("conn_001")
        
        self.assertEqual(result, self.connection)

    def test_get_connection_nonexistent(self):
        """Test getting non-existent connection."""
        self.mock_connection_repository.get_connection_by_id.return_value = None
        
        result = self.manager.get_connection("nonexistent")
        
        self.assertIsNone(result)

    def test_get_user_connections(self):
        """Test getting user connections."""
        connections = [self.connection]
        self.mock_connection_repository.get_connections_by_user.return_value = connections
        
        result = self.manager.get_user_connections("user_001")
        
        self.assertEqual(result, connections)
        self.mock_connection_repository.get_connections_by_user.assert_called_once_with("user_001", None)

    def test_get_user_connections_with_status(self):
        """Test getting user connections with status filter."""
        connections = [self.connection]
        self.mock_connection_repository.get_connections_by_user.return_value = connections
        
        result = self.manager.get_user_connections("user_001", "accepted")
        
        self.assertEqual(result, connections)
        self.mock_connection_repository.get_connections_by_user.assert_called_once_with("user_001", "accepted")

    def test_get_accepted_connections(self):
        """Test getting accepted connections."""
        connections = [self.connection]
        self.mock_connection_repository.get_connections_by_user.return_value = connections
        
        result = self.manager.get_accepted_connections("user_001")
        
        self.assertEqual(result, connections)
        self.mock_connection_repository.get_connections_by_user.assert_called_once_with("user_001", "accepted")

    def test_remove_connection_valid(self):
        """Test removing connection by involved user."""
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        self.mock_connection_repository.delete_connection.return_value = True
        
        result = self.manager.remove_connection("conn_001", "user_001")
        
        self.assertTrue(result)
        self.mock_connection_repository.delete_connection.assert_called_once_with("conn_001")

    def test_remove_connection_unauthorized_raises_error(self):
        """Test removing connection by non-involved user raises error."""
        self.mock_connection_repository.get_connection_by_id.return_value = self.connection
        
        with self.assertRaises(ValueError) as context:
            self.manager.remove_connection("conn_001", "user_999")
        self.assertIn("not involved", str(context.exception))

    def test_are_connected_true(self):
        """Test checking if users are connected (true case)."""
        self.connection.accept()
        self.mock_connection_repository.get_connection_between_users.return_value = self.connection
        
        result = self.manager.are_connected("user_001", "user_002")
        
        self.assertTrue(result)

    def test_are_connected_false(self):
        """Test checking if users are connected (false case)."""
        self.mock_connection_repository.get_connection_between_users.return_value = None
        
        result = self.manager.are_connected("user_001", "user_002")
        
        self.assertFalse(result)


class TestNewsFeedManager(unittest.TestCase):
    """Test cases for NewsFeedManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_feed_repository = Mock()
        self.mock_message_repository = Mock()
        self.mock_connection_manager = Mock()
        self.mock_user_repository = Mock()
        self.mock_profile_repository = Mock()
        
        self.manager = NewsFeedManager(
            self.mock_feed_repository,
            self.mock_message_repository,
            self.mock_connection_manager,
            self.mock_user_repository,
            self.mock_profile_repository
        )
        
        self.user = User("user_001", "john@email.com", "John", "Doe")
        self.profile = Profile("user_001", "Engineer", "Experienced", "SF")
        self.message = Message("msg_001", "user_001", "Hello world!")
        self.connection = Connection("conn_001", "user_001", "user_002")
        self.connection.accept()

    def test_get_user_feed(self):
        """Test getting user feed."""
        feed_items = [Mock(), Mock()]
        self.mock_feed_repository.get_feed_items_for_user.return_value = feed_items
        
        result = self.manager.get_user_feed("user_001")
        
        self.assertEqual(result, feed_items)
        self.mock_feed_repository.get_feed_items_for_user.assert_called_once_with("user_001", 20)

    def test_get_user_feed_with_limit(self):
        """Test getting user feed with custom limit."""
        feed_items = [Mock()]
        self.mock_feed_repository.get_feed_items_for_user.return_value = feed_items
        
        result = self.manager.get_user_feed("user_001", limit=10)
        
        self.assertEqual(result, feed_items)
        self.mock_feed_repository.get_feed_items_for_user.assert_called_once_with("user_001", 10)

    def test_refresh_user_feed(self):
        """Test refreshing user feed."""
        self.manager.refresh_user_feed("user_001")
        
        self.mock_feed_repository.clear_user_feed.assert_called_once_with("user_001")

    def test_get_feed_item_count(self):
        """Test getting feed item count."""
        feed_items = [Mock(), Mock(), Mock()]
        self.mock_feed_repository.get_feed_items_for_user.return_value = feed_items
        
        result = self.manager.get_feed_item_count("user_001")
        
        self.assertEqual(result, 3)
        self.mock_feed_repository.get_feed_items_for_user.assert_called_once_with("user_001", 1000)


if __name__ == '__main__':
    unittest.main()
