"""
Unit tests for LinkedIn entities module.

Tests all business objects and their methods including validation and business logic.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from entities import User, Profile, Message, Connection, NewsFeedItem, NewsFeed


class TestUser(unittest.TestCase):
    """Test cases for User entity."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User("user_001", "john.doe@email.com", "John", "Doe")

    def test_user_creation(self):
        """Test user creation with valid data."""
        self.assertEqual(self.user.user_id, "user_001")
        self.assertEqual(self.user.email, "john.doe@email.com")
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertIsInstance(self.user.created_at, datetime)

    def test_get_full_name(self):
        """Test getting user's full name."""
        self.assertEqual(self.user.get_full_name(), "John Doe")

    def test_validate_email_valid(self):
        """Test email validation with valid email."""
        self.assertTrue(self.user.validate_email())

    def test_validate_email_invalid_no_at(self):
        """Test email validation with invalid email (no @)."""
        user = User("user_002", "invalidemail.com", "Jane", "Smith")
        self.assertFalse(user.validate_email())

    def test_validate_email_invalid_no_dot(self):
        """Test email validation with invalid email (no .)."""
        user = User("user_003", "invalid@email", "Bob", "Johnson")
        self.assertFalse(user.validate_email())

    def test_validate_email_empty(self):
        """Test email validation with empty email."""
        user = User("user_004", "", "Alice", "Brown")
        self.assertFalse(user.validate_email())


class TestProfile(unittest.TestCase):
    """Test cases for Profile entity."""

    def setUp(self):
        """Set up test fixtures."""
        self.profile = Profile("user_001", "Software Engineer", "Experienced developer", "San Francisco")

    def test_profile_creation(self):
        """Test profile creation with valid data."""
        self.assertEqual(self.profile.user_id, "user_001")
        self.assertEqual(self.profile.headline, "Software Engineer")
        self.assertEqual(self.profile.summary, "Experienced developer")
        self.assertEqual(self.profile.location, "San Francisco")
        self.assertIsInstance(self.profile.updated_at, datetime)

    def test_profile_creation_empty_fields(self):
        """Test profile creation with empty optional fields."""
        profile = Profile("user_002")
        self.assertEqual(profile.user_id, "user_002")
        self.assertEqual(profile.headline, "")
        self.assertEqual(profile.summary, "")
        self.assertEqual(profile.location, "")

    def test_update_profile_all_fields(self):
        """Test updating all profile fields."""
        original_updated_at = self.profile.updated_at
        self.profile.update_profile("Senior Engineer", "Very experienced", "New York")
        
        self.assertEqual(self.profile.headline, "Senior Engineer")
        self.assertEqual(self.profile.summary, "Very experienced")
        self.assertEqual(self.profile.location, "New York")
        self.assertGreater(self.profile.updated_at, original_updated_at)

    def test_update_profile_partial_fields(self):
        """Test updating only some profile fields."""
        original_headline = self.profile.headline
        original_updated_at = self.profile.updated_at
        
        self.profile.update_profile(summary="Updated summary")
        
        self.assertEqual(self.profile.headline, original_headline)  # Unchanged
        self.assertEqual(self.profile.summary, "Updated summary")  # Changed
        self.assertGreater(self.profile.updated_at, original_updated_at)

    def test_update_profile_empty_fields(self):
        """Test updating profile with empty fields (should not change existing values)."""
        self.profile.update_profile("", "", "")
        
        self.assertEqual(self.profile.headline, "Software Engineer")  # Unchanged
        self.assertEqual(self.profile.summary, "Experienced developer")  # Unchanged
        self.assertEqual(self.profile.location, "San Francisco")  # Unchanged


class TestMessage(unittest.TestCase):
    """Test cases for Message entity."""

    def setUp(self):
        """Set up test fixtures."""
        self.message = Message("msg_001", "user_001", "Hello LinkedIn!")

    def test_message_creation(self):
        """Test message creation with valid data."""
        self.assertEqual(self.message.message_id, "msg_001")
        self.assertEqual(self.message.author_id, "user_001")
        self.assertEqual(self.message.content, "Hello LinkedIn!")
        self.assertIsInstance(self.message.created_at, datetime)
        self.assertIsInstance(self.message.updated_at, datetime)

    def test_update_content_valid(self):
        """Test updating message content with valid content."""
        original_updated_at = self.message.updated_at
        self.message.update_content("Updated content")
        
        self.assertEqual(self.message.content, "Updated content")
        self.assertGreater(self.message.updated_at, original_updated_at)

    def test_update_content_empty_raises_error(self):
        """Test updating message content with empty content raises error."""
        with self.assertRaises(ValueError) as context:
            self.message.update_content("")
        self.assertIn("Message content cannot be empty", str(context.exception))

    def test_update_content_whitespace_only_raises_error(self):
        """Test updating message content with whitespace only raises error."""
        with self.assertRaises(ValueError) as context:
            self.message.update_content("   \n\t   ")
        self.assertIn("Message content cannot be empty", str(context.exception))

    def test_update_content_trims_whitespace(self):
        """Test that update_content trims whitespace."""
        self.message.update_content("  trimmed content  ")
        self.assertEqual(self.message.content, "trimmed content")

    def test_is_author_true(self):
        """Test is_author returns True for actual author."""
        self.assertTrue(self.message.is_author("user_001"))

    def test_is_author_false(self):
        """Test is_author returns False for non-author."""
        self.assertFalse(self.message.is_author("user_002"))


class TestConnection(unittest.TestCase):
    """Test cases for Connection entity."""

    def setUp(self):
        """Set up test fixtures."""
        self.connection = Connection("conn_001", "user_001", "user_002")

    def test_connection_creation(self):
        """Test connection creation with valid data."""
        self.assertEqual(self.connection.connection_id, "conn_001")
        self.assertEqual(self.connection.sender_id, "user_001")
        self.assertEqual(self.connection.receiver_id, "user_002")
        self.assertEqual(self.connection.status, "pending")
        self.assertIsInstance(self.connection.created_at, datetime)
        self.assertIsInstance(self.connection.updated_at, datetime)

    def test_accept_connection(self):
        """Test accepting a connection request."""
        original_updated_at = self.connection.updated_at
        self.connection.accept()
        
        self.assertEqual(self.connection.status, "accepted")
        self.assertGreater(self.connection.updated_at, original_updated_at)

    def test_reject_connection(self):
        """Test rejecting a connection request."""
        original_updated_at = self.connection.updated_at
        self.connection.reject()
        
        self.assertEqual(self.connection.status, "rejected")
        self.assertGreater(self.connection.updated_at, original_updated_at)

    def test_accept_already_accepted_connection(self):
        """Test accepting an already accepted connection (should not change status)."""
        self.connection.accept()
        original_updated_at = self.connection.updated_at
        self.connection.accept()  # Try to accept again
        
        self.assertEqual(self.connection.status, "accepted")
        self.assertEqual(self.connection.updated_at, original_updated_at)  # Should not change

    def test_reject_already_rejected_connection(self):
        """Test rejecting an already rejected connection (should not change status)."""
        self.connection.reject()
        original_updated_at = self.connection.updated_at
        self.connection.reject()  # Try to reject again
        
        self.assertEqual(self.connection.status, "rejected")
        self.assertEqual(self.connection.updated_at, original_updated_at)  # Should not change

    def test_is_pending(self):
        """Test is_pending method."""
        self.assertTrue(self.connection.is_pending())
        
        self.connection.accept()
        self.assertFalse(self.connection.is_pending())

    def test_is_accepted(self):
        """Test is_accepted method."""
        self.assertFalse(self.connection.is_accepted())
        
        self.connection.accept()
        self.assertTrue(self.connection.is_accepted())

    def test_is_rejected(self):
        """Test is_rejected method."""
        self.assertFalse(self.connection.is_rejected())
        
        self.connection.reject()
        self.assertTrue(self.connection.is_rejected())

    def test_involves_user_sender(self):
        """Test involves_user with sender."""
        self.assertTrue(self.connection.involves_user("user_001"))

    def test_involves_user_receiver(self):
        """Test involves_user with receiver."""
        self.assertTrue(self.connection.involves_user("user_002"))

    def test_involves_user_neither(self):
        """Test involves_user with user not involved."""
        self.assertFalse(self.connection.involves_user("user_003"))

    def test_get_other_user_sender(self):
        """Test get_other_user when given sender."""
        other_user = self.connection.get_other_user("user_001")
        self.assertEqual(other_user, "user_002")

    def test_get_other_user_receiver(self):
        """Test get_other_user when given receiver."""
        other_user = self.connection.get_other_user("user_002")
        self.assertEqual(other_user, "user_001")

    def test_get_other_user_neither(self):
        """Test get_other_user when given user not involved."""
        other_user = self.connection.get_other_user("user_003")
        self.assertIsNone(other_user)


class TestNewsFeedItem(unittest.TestCase):
    """Test cases for NewsFeedItem entity."""

    def setUp(self):
        """Set up test fixtures."""
        self.user = User("user_001", "john@email.com", "John", "Doe")
        self.profile = Profile("user_001", "Software Engineer", "Experienced", "SF")
        self.message = Message("msg_001", "user_001", "Hello world!")
        self.feed_item = NewsFeedItem("feed_001", "user_002", self.message, self.user, self.profile)

    def test_feed_item_creation(self):
        """Test news feed item creation."""
        self.assertEqual(self.feed_item.feed_item_id, "feed_001")
        self.assertEqual(self.feed_item.user_id, "user_002")
        self.assertEqual(self.feed_item.message, self.message)
        self.assertEqual(self.feed_item.author, self.user)
        self.assertEqual(self.feed_item.author_profile, self.profile)
        self.assertIsInstance(self.feed_item.feed_timestamp, datetime)

    def test_get_display_content_with_profile(self):
        """Test get_display_content with profile."""
        content = self.feed_item.get_display_content()
        expected = "John Doe (Software Engineer)\nHello world!"
        self.assertEqual(content, expected)

    def test_get_display_content_without_profile(self):
        """Test get_display_content without profile."""
        feed_item = NewsFeedItem("feed_002", "user_002", self.message, self.user, None)
        content = feed_item.get_display_content()
        expected = "John Doe (Professional)\nHello world!"
        self.assertEqual(content, expected)


class TestNewsFeed(unittest.TestCase):
    """Test cases for NewsFeed entity."""

    def setUp(self):
        """Set up test fixtures."""
        self.feed = NewsFeed("user_001")
        self.user = User("user_001", "john@email.com", "John", "Doe")
        self.profile = Profile("user_001", "Engineer", "Experienced", "SF")
        
        # Create messages with different timestamps
        self.message1 = Message("msg_001", "user_001", "First message")
        self.message2 = Message("msg_002", "user_001", "Second message")
        self.message3 = Message("msg_003", "user_001", "Third message")
        
        # Create feed items
        self.feed_item1 = NewsFeedItem("feed_001", "user_001", self.message1, self.user, self.profile)
        self.feed_item2 = NewsFeedItem("feed_002", "user_001", self.message2, self.user, self.profile)
        self.feed_item3 = NewsFeedItem("feed_003", "user_001", self.message3, self.user, self.profile)

    def test_feed_creation(self):
        """Test news feed creation."""
        self.assertEqual(self.feed.user_id, "user_001")
        self.assertEqual(len(self.feed.feed_items), 0)
        self.assertIsInstance(self.feed.last_updated, datetime)

    def test_add_item(self):
        """Test adding items to feed."""
        original_updated = self.feed.last_updated
        self.feed.add_item(self.feed_item1)
        
        self.assertEqual(len(self.feed.feed_items), 1)
        self.assertEqual(self.feed.feed_items[0], self.feed_item1)
        self.assertGreater(self.feed.last_updated, original_updated)

    def test_add_multiple_items(self):
        """Test adding multiple items to feed."""
        self.feed.add_item(self.feed_item1)
        self.feed.add_item(self.feed_item2)
        self.feed.add_item(self.feed_item3)
        
        self.assertEqual(len(self.feed.feed_items), 3)

    def test_get_recent_items_default_limit(self):
        """Test getting recent items with default limit."""
        self.feed.add_item(self.feed_item1)
        self.feed.add_item(self.feed_item2)
        self.feed.add_item(self.feed_item3)
        
        recent_items = self.feed.get_recent_items()
        self.assertEqual(len(recent_items), 3)  # Default limit is 20

    def test_get_recent_items_custom_limit(self):
        """Test getting recent items with custom limit."""
        self.feed.add_item(self.feed_item1)
        self.feed.add_item(self.feed_item2)
        self.feed.add_item(self.feed_item3)
        
        recent_items = self.feed.get_recent_items(limit=2)
        self.assertEqual(len(recent_items), 2)

    def test_get_recent_items_limit_exceeds_items(self):
        """Test getting recent items when limit exceeds available items."""
        self.feed.add_item(self.feed_item1)
        
        recent_items = self.feed.get_recent_items(limit=5)
        self.assertEqual(len(recent_items), 1)

    def test_refresh_feed(self):
        """Test refreshing feed."""
        original_updated = self.feed.last_updated
        self.feed.refresh_feed()
        
        self.assertGreater(self.feed.last_updated, original_updated)


if __name__ == '__main__':
    unittest.main()
