"""
Unit tests for LinkedIn repositories module.

Tests all repository implementations including abstract base classes and in-memory storage.
"""

import unittest
from unittest.mock import Mock, patch

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities import User, Profile, Message, Connection, NewsFeed, NewsFeedItem
from repositories import (
    InMemoryUserRepository, InMemoryProfileRepository, InMemoryMessageRepository,
    InMemoryConnectionRepository, InMemoryNewsFeedRepository
)


class TestInMemoryUserRepository(unittest.TestCase):
    """Test cases for InMemoryUserRepository."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = InMemoryUserRepository()
        self.user1 = User("user_001", "john@email.com", "John", "Doe")
        self.user2 = User("user_002", "jane@email.com", "Jane", "Smith")

    def test_save_user(self):
        """Test saving a user."""
        self.repository.save_user(self.user1)
        
        self.assertIn("user_001", self.repository.users)
        self.assertEqual(self.repository.users["user_001"], self.user1)
        self.assertIn("john@email.com", self.repository.email_index)
        self.assertEqual(self.repository.email_index["john@email.com"], "user_001")

    def test_save_multiple_users(self):
        """Test saving multiple users."""
        self.repository.save_user(self.user1)
        self.repository.save_user(self.user2)
        
        self.assertEqual(len(self.repository.users), 2)
        self.assertEqual(len(self.repository.email_index), 2)

    def test_get_user_by_id_existing(self):
        """Test getting user by ID when user exists."""
        self.repository.save_user(self.user1)
        retrieved_user = self.repository.get_user_by_id("user_001")
        
        self.assertEqual(retrieved_user, self.user1)

    def test_get_user_by_id_nonexistent(self):
        """Test getting user by ID when user doesn't exist."""
        retrieved_user = self.repository.get_user_by_id("nonexistent")
        
        self.assertIsNone(retrieved_user)

    def test_get_user_by_email_existing(self):
        """Test getting user by email when user exists."""
        self.repository.save_user(self.user1)
        retrieved_user = self.repository.get_user_by_email("john@email.com")
        
        self.assertEqual(retrieved_user, self.user1)

    def test_get_user_by_email_nonexistent(self):
        """Test getting user by email when user doesn't exist."""
        retrieved_user = self.repository.get_user_by_email("nonexistent@email.com")
        
        self.assertIsNone(retrieved_user)

    def test_get_all_users_empty(self):
        """Test getting all users when repository is empty."""
        users = self.repository.get_all_users()
        
        self.assertEqual(len(users), 0)

    def test_get_all_users_with_data(self):
        """Test getting all users when repository has data."""
        self.repository.save_user(self.user1)
        self.repository.save_user(self.user2)
        users = self.repository.get_all_users()
        
        self.assertEqual(len(users), 2)
        self.assertIn(self.user1, users)
        self.assertIn(self.user2, users)


class TestInMemoryProfileRepository(unittest.TestCase):
    """Test cases for InMemoryProfileRepository."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = InMemoryProfileRepository()
        self.profile1 = Profile("user_001", "Software Engineer", "Experienced", "SF")
        self.profile2 = Profile("user_002", "Product Manager", "Skilled", "NY")

    def test_save_profile(self):
        """Test saving a profile."""
        self.repository.save_profile(self.profile1)
        
        self.assertIn("user_001", self.repository.profiles)
        self.assertEqual(self.repository.profiles["user_001"], self.profile1)

    def test_save_multiple_profiles(self):
        """Test saving multiple profiles."""
        self.repository.save_profile(self.profile1)
        self.repository.save_profile(self.profile2)
        
        self.assertEqual(len(self.repository.profiles), 2)

    def test_get_profile_by_user_id_existing(self):
        """Test getting profile by user ID when profile exists."""
        self.repository.save_profile(self.profile1)
        retrieved_profile = self.repository.get_profile_by_user_id("user_001")
        
        self.assertEqual(retrieved_profile, self.profile1)

    def test_get_profile_by_user_id_nonexistent(self):
        """Test getting profile by user ID when profile doesn't exist."""
        retrieved_profile = self.repository.get_profile_by_user_id("nonexistent")
        
        self.assertIsNone(retrieved_profile)

    def test_get_all_profiles_empty(self):
        """Test getting all profiles when repository is empty."""
        profiles = self.repository.get_all_profiles()
        
        self.assertEqual(len(profiles), 0)

    def test_get_all_profiles_with_data(self):
        """Test getting all profiles when repository has data."""
        self.repository.save_profile(self.profile1)
        self.repository.save_profile(self.profile2)
        profiles = self.repository.get_all_profiles()
        
        self.assertEqual(len(profiles), 2)
        self.assertIn(self.profile1, profiles)
        self.assertIn(self.profile2, profiles)


class TestInMemoryMessageRepository(unittest.TestCase):
    """Test cases for InMemoryMessageRepository."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = InMemoryMessageRepository()
        self.message1 = Message("msg_001", "user_001", "Hello world!")
        self.message2 = Message("msg_002", "user_001", "Second message")
        self.message3 = Message("msg_003", "user_002", "From user 2")

    def test_save_message(self):
        """Test saving a message."""
        self.repository.save_message(self.message1)
        
        self.assertIn("msg_001", self.repository.messages)
        self.assertEqual(self.repository.messages["msg_001"], self.message1)
        self.assertIn("user_001", self.repository.author_index)
        self.assertIn("msg_001", self.repository.author_index["user_001"])

    def test_save_multiple_messages(self):
        """Test saving multiple messages."""
        self.repository.save_message(self.message1)
        self.repository.save_message(self.message2)
        self.repository.save_message(self.message3)
        
        self.assertEqual(len(self.repository.messages), 3)
        self.assertEqual(len(self.repository.author_index["user_001"]), 2)
        self.assertEqual(len(self.repository.author_index["user_002"]), 1)

    def test_get_message_by_id_existing(self):
        """Test getting message by ID when message exists."""
        self.repository.save_message(self.message1)
        retrieved_message = self.repository.get_message_by_id("msg_001")
        
        self.assertEqual(retrieved_message, self.message1)

    def test_get_message_by_id_nonexistent(self):
        """Test getting message by ID when message doesn't exist."""
        retrieved_message = self.repository.get_message_by_id("nonexistent")
        
        self.assertIsNone(retrieved_message)

    def test_get_messages_by_author_existing(self):
        """Test getting messages by author when messages exist."""
        self.repository.save_message(self.message1)
        self.repository.save_message(self.message2)
        self.repository.save_message(self.message3)
        
        user1_messages = self.repository.get_messages_by_author("user_001")
        user2_messages = self.repository.get_messages_by_author("user_002")
        
        self.assertEqual(len(user1_messages), 2)
        self.assertEqual(len(user2_messages), 1)
        self.assertIn(self.message1, user1_messages)
        self.assertIn(self.message2, user1_messages)
        self.assertIn(self.message3, user2_messages)

    def test_get_messages_by_author_nonexistent(self):
        """Test getting messages by author when no messages exist."""
        messages = self.repository.get_messages_by_author("nonexistent")
        
        self.assertEqual(len(messages), 0)

    def test_get_all_messages_empty(self):
        """Test getting all messages when repository is empty."""
        messages = self.repository.get_all_messages()
        
        self.assertEqual(len(messages), 0)

    def test_get_all_messages_with_data(self):
        """Test getting all messages when repository has data."""
        self.repository.save_message(self.message1)
        self.repository.save_message(self.message2)
        self.repository.save_message(self.message3)
        
        messages = self.repository.get_all_messages()
        
        self.assertEqual(len(messages), 3)
        # Should be sorted by creation time (newest first)
        self.assertEqual(messages[0], self.message3)  # Latest
        self.assertEqual(messages[1], self.message2)
        self.assertEqual(messages[2], self.message1)  # Earliest

    def test_delete_message_existing(self):
        """Test deleting an existing message."""
        self.repository.save_message(self.message1)
        self.repository.save_message(self.message2)
        
        result = self.repository.delete_message("msg_001")
        
        self.assertTrue(result)
        self.assertNotIn("msg_001", self.repository.messages)
        self.assertNotIn("msg_001", self.repository.author_index["user_001"])
        self.assertIn("msg_002", self.repository.messages)  # Other message still exists

    def test_delete_message_nonexistent(self):
        """Test deleting a non-existent message."""
        result = self.repository.delete_message("nonexistent")
        
        self.assertFalse(result)

    def test_delete_message_cleans_up_author_index(self):
        """Test that deleting a message cleans up empty author index entries."""
        self.repository.save_message(self.message1)
        self.repository.delete_message("msg_001")
        
        self.assertNotIn("user_001", self.repository.author_index)


class TestInMemoryConnectionRepository(unittest.TestCase):
    """Test cases for InMemoryConnectionRepository."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = InMemoryConnectionRepository()
        self.connection1 = Connection("conn_001", "user_001", "user_002")
        self.connection2 = Connection("conn_002", "user_002", "user_003")
        self.connection3 = Connection("conn_003", "user_001", "user_003")

    def test_save_connection(self):
        """Test saving a connection."""
        self.repository.save_connection(self.connection1)
        
        self.assertIn("conn_001", self.repository.connections)
        self.assertEqual(self.repository.connections["conn_001"], self.connection1)
        self.assertIn("user_001", self.repository.user_index)
        self.assertIn("user_002", self.repository.user_index)
        self.assertIn("conn_001", self.repository.user_index["user_001"])
        self.assertIn("conn_001", self.repository.user_index["user_002"])

    def test_save_multiple_connections(self):
        """Test saving multiple connections."""
        self.repository.save_connection(self.connection1)
        self.repository.save_connection(self.connection2)
        self.repository.save_connection(self.connection3)
        
        self.assertEqual(len(self.repository.connections), 3)
        self.assertEqual(len(self.repository.user_index["user_001"]), 2)
        self.assertEqual(len(self.repository.user_index["user_002"]), 2)
        self.assertEqual(len(self.repository.user_index["user_003"]), 2)

    def test_get_connection_by_id_existing(self):
        """Test getting connection by ID when connection exists."""
        self.repository.save_connection(self.connection1)
        retrieved_connection = self.repository.get_connection_by_id("conn_001")
        
        self.assertEqual(retrieved_connection, self.connection1)

    def test_get_connection_by_id_nonexistent(self):
        """Test getting connection by ID when connection doesn't exist."""
        retrieved_connection = self.repository.get_connection_by_id("nonexistent")
        
        self.assertIsNone(retrieved_connection)

    def test_get_connections_by_user_all(self):
        """Test getting all connections for a user."""
        self.repository.save_connection(self.connection1)
        self.repository.save_connection(self.connection2)
        self.repository.save_connection(self.connection3)
        
        user1_connections = self.repository.get_connections_by_user("user_001")
        user2_connections = self.repository.get_connections_by_user("user_002")
        
        self.assertEqual(len(user1_connections), 2)
        self.assertEqual(len(user2_connections), 2)
        self.assertIn(self.connection1, user1_connections)
        self.assertIn(self.connection3, user1_connections)
        self.assertIn(self.connection1, user2_connections)
        self.assertIn(self.connection2, user2_connections)

    def test_get_connections_by_user_with_status_filter(self):
        """Test getting connections for a user filtered by status."""
        self.repository.save_connection(self.connection1)
        self.connection1.accept()
        self.repository.save_connection(self.connection2)
        
        accepted_connections = self.repository.get_connections_by_user("user_001", "accepted")
        pending_connections = self.repository.get_connections_by_user("user_001", "pending")
        
        self.assertEqual(len(accepted_connections), 1)
        self.assertEqual(len(pending_connections), 1)
        self.assertIn(self.connection1, accepted_connections)
        self.assertIn(self.connection3, pending_connections)

    def test_get_connections_by_user_nonexistent(self):
        """Test getting connections for a non-existent user."""
        connections = self.repository.get_connections_by_user("nonexistent")
        
        self.assertEqual(len(connections), 0)

    def test_get_connection_between_users_existing(self):
        """Test getting connection between users when connection exists."""
        self.repository.save_connection(self.connection1)
        
        connection = self.repository.get_connection_between_users("user_001", "user_002")
        
        self.assertEqual(connection, self.connection1)

    def test_get_connection_between_users_reverse_order(self):
        """Test getting connection between users in reverse order."""
        self.repository.save_connection(self.connection1)
        
        connection = self.repository.get_connection_between_users("user_002", "user_001")
        
        self.assertEqual(connection, self.connection1)

    def test_get_connection_between_users_nonexistent(self):
        """Test getting connection between users when no connection exists."""
        connection = self.repository.get_connection_between_users("user_001", "user_999")
        
        self.assertIsNone(connection)

    def test_get_all_connections_empty(self):
        """Test getting all connections when repository is empty."""
        connections = self.repository.get_all_connections()
        
        self.assertEqual(len(connections), 0)

    def test_get_all_connections_with_data(self):
        """Test getting all connections when repository has data."""
        self.repository.save_connection(self.connection1)
        self.repository.save_connection(self.connection2)
        
        connections = self.repository.get_all_connections()
        
        self.assertEqual(len(connections), 2)
        self.assertIn(self.connection1, connections)
        self.assertIn(self.connection2, connections)

    def test_delete_connection_existing(self):
        """Test deleting an existing connection."""
        self.repository.save_connection(self.connection1)
        self.repository.save_connection(self.connection2)
        
        result = self.repository.delete_connection("conn_001")
        
        self.assertTrue(result)
        self.assertNotIn("conn_001", self.repository.connections)
        self.assertNotIn("conn_001", self.repository.user_index["user_001"])
        self.assertNotIn("conn_001", self.repository.user_index["user_002"])
        self.assertIn("conn_002", self.repository.connections)  # Other connection still exists

    def test_delete_connection_nonexistent(self):
        """Test deleting a non-existent connection."""
        result = self.repository.delete_connection("nonexistent")
        
        self.assertFalse(result)

    def test_delete_connection_cleans_up_user_index(self):
        """Test that deleting a connection cleans up empty user index entries."""
        self.repository.save_connection(self.connection1)
        self.repository.delete_connection("conn_001")
        
        self.assertNotIn("user_001", self.repository.user_index)
        self.assertNotIn("user_002", self.repository.user_index)


class TestInMemoryNewsFeedRepository(unittest.TestCase):
    """Test cases for InMemoryNewsFeedRepository."""

    def setUp(self):
        """Set up test fixtures."""
        self.repository = InMemoryNewsFeedRepository()
        self.user = User("user_001", "john@email.com", "John", "Doe")
        self.profile = Profile("user_001", "Engineer", "Experienced", "SF")
        self.message = Message("msg_001", "user_001", "Hello world!")
        self.feed_item = NewsFeedItem("feed_001", "user_002", self.message, self.user, self.profile)

    def test_save_feed_item_new_user(self):
        """Test saving feed item for a new user."""
        self.repository.save_feed_item(self.feed_item)
        
        self.assertIn("user_002", self.repository.feeds)
        feed = self.repository.feeds["user_002"]
        self.assertEqual(len(feed.feed_items), 1)
        self.assertEqual(feed.feed_items[0], self.feed_item)

    def test_save_feed_item_existing_user(self):
        """Test saving feed item for an existing user."""
        self.repository.save_feed_item(self.feed_item)
        
        # Create and save another feed item for the same user
        message2 = Message("msg_002", "user_001", "Second message")
        feed_item2 = NewsFeedItem("feed_002", "user_002", message2, self.user, self.profile)
        self.repository.save_feed_item(feed_item2)
        
        feed = self.repository.feeds["user_002"]
        self.assertEqual(len(feed.feed_items), 2)

    def test_get_user_feed_existing(self):
        """Test getting user feed when feed exists."""
        self.repository.save_feed_item(self.feed_item)
        feed = self.repository.get_user_feed("user_002")
        
        self.assertEqual(feed.user_id, "user_002")
        self.assertEqual(len(feed.feed_items), 1)

    def test_get_user_feed_nonexistent(self):
        """Test getting user feed when feed doesn't exist."""
        feed = self.repository.get_user_feed("nonexistent")
        
        self.assertEqual(feed.user_id, "nonexistent")
        self.assertEqual(len(feed.feed_items), 0)

    def test_get_feed_items_for_user_existing(self):
        """Test getting feed items for user when items exist."""
        self.repository.save_feed_item(self.feed_item)
        
        # Create and save another feed item
        message2 = Message("msg_002", "user_001", "Second message")
        feed_item2 = NewsFeedItem("feed_002", "user_002", message2, self.user, self.profile)
        self.repository.save_feed_item(feed_item2)
        
        items = self.repository.get_feed_items_for_user("user_002")
        self.assertEqual(len(items), 2)

    def test_get_feed_items_for_user_with_limit(self):
        """Test getting feed items for user with limit."""
        self.repository.save_feed_item(self.feed_item)
        
        # Create and save another feed item
        message2 = Message("msg_002", "user_001", "Second message")
        feed_item2 = NewsFeedItem("feed_002", "user_002", message2, self.user, self.profile)
        self.repository.save_feed_item(feed_item2)
        
        items = self.repository.get_feed_items_for_user("user_002", limit=1)
        self.assertEqual(len(items), 1)

    def test_get_feed_items_for_user_nonexistent(self):
        """Test getting feed items for non-existent user."""
        items = self.repository.get_feed_items_for_user("nonexistent")
        
        self.assertEqual(len(items), 0)

    def test_refresh_user_feed_existing(self):
        """Test refreshing user feed when feed exists."""
        self.repository.save_feed_item(self.feed_item)
        original_updated = self.repository.feeds["user_002"].last_updated
        
        self.repository.refresh_user_feed("user_002")
        
        self.assertGreater(self.repository.feeds["user_002"].last_updated, original_updated)

    def test_refresh_user_feed_nonexistent(self):
        """Test refreshing user feed when feed doesn't exist."""
        # Should not raise an error
        self.repository.refresh_user_feed("nonexistent")

    def test_clear_user_feed_existing(self):
        """Test clearing user feed when feed exists."""
        self.repository.save_feed_item(self.feed_item)
        
        self.repository.clear_user_feed("user_002")
        
        self.assertEqual(len(self.repository.feeds["user_002"].feed_items), 0)

    def test_clear_user_feed_nonexistent(self):
        """Test clearing user feed when feed doesn't exist."""
        # Should not raise an error
        self.repository.clear_user_feed("nonexistent")


if __name__ == '__main__':
    unittest.main()
