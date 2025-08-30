"""
Unit tests for LinkedIn services module.

Tests all external service integrations including email, SMS, and push notification services.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import (
    MockEmailService, MockSMSService, MockPushNotificationService, NotificationService
)


class TestMockEmailService(unittest.TestCase):
    """Test cases for MockEmailService."""

    def setUp(self):
        """Set up test fixtures."""
        self.email_service = MockEmailService()

    def test_send_email(self):
        """Test sending email."""
        result = self.email_service.send_email("test@example.com", "Test Subject", "Test Body")
        
        self.assertTrue(result)
        self.assertEqual(len(self.email_service.sent_emails), 1)
        self.assertEqual(self.email_service.sent_emails[0]["to"], "test@example.com")
        self.assertEqual(self.email_service.sent_emails[0]["subject"], "Test Subject")
        self.assertEqual(self.email_service.sent_emails[0]["body"], "Test Body")

    def test_send_multiple_emails(self):
        """Test sending multiple emails."""
        self.email_service.send_email("user1@example.com", "Subject 1", "Body 1")
        self.email_service.send_email("user2@example.com", "Subject 2", "Body 2")
        
        self.assertEqual(len(self.email_service.sent_emails), 2)
        self.assertEqual(self.email_service.sent_emails[0]["to"], "user1@example.com")
        self.assertEqual(self.email_service.sent_emails[1]["to"], "user2@example.com")

    def test_send_connection_request_email(self):
        """Test sending connection request email."""
        result = self.email_service.send_connection_request_email("user@example.com", "John Doe")
        
        self.assertTrue(result)
        self.assertEqual(len(self.email_service.sent_emails), 1)
        email = self.email_service.sent_emails[0]
        self.assertEqual(email["to"], "user@example.com")
        self.assertEqual(email["subject"], "New Connection Request from John Doe")
        self.assertIn("John Doe has sent you a connection request", email["body"])

    def test_send_connection_accepted_email(self):
        """Test sending connection accepted email."""
        result = self.email_service.send_connection_accepted_email("user@example.com", "Jane Smith")
        
        self.assertTrue(result)
        self.assertEqual(len(self.email_service.sent_emails), 1)
        email = self.email_service.sent_emails[0]
        self.assertEqual(email["to"], "user@example.com")
        self.assertEqual(email["subject"], "Jane Smith accepted your connection request")
        self.assertIn("Jane Smith has accepted your connection request", email["body"])

    def test_get_sent_emails(self):
        """Test getting sent emails."""
        self.email_service.send_email("test@example.com", "Test", "Body")
        
        sent_emails = self.email_service.get_sent_emails()
        
        self.assertEqual(len(sent_emails), 1)
        self.assertEqual(sent_emails[0]["to"], "test@example.com")

    def test_clear_sent_emails(self):
        """Test clearing sent emails."""
        self.email_service.send_email("test@example.com", "Test", "Body")
        self.assertEqual(len(self.email_service.sent_emails), 1)
        
        self.email_service.clear_sent_emails()
        
        self.assertEqual(len(self.email_service.sent_emails), 0)


class TestMockSMSService(unittest.TestCase):
    """Test cases for MockSMSService."""

    def setUp(self):
        """Set up test fixtures."""
        self.sms_service = MockSMSService()

    def test_send_sms(self):
        """Test sending SMS."""
        result = self.sms_service.send_sms("+1234567890", "Test message")
        
        self.assertTrue(result)
        self.assertEqual(len(self.sms_service.sent_sms), 1)
        self.assertEqual(self.sms_service.sent_sms[0]["to"], "+1234567890")
        self.assertEqual(self.sms_service.sent_sms[0]["message"], "Test message")

    def test_send_multiple_sms(self):
        """Test sending multiple SMS."""
        self.sms_service.send_sms("+1234567890", "Message 1")
        self.sms_service.send_sms("+0987654321", "Message 2")
        
        self.assertEqual(len(self.sms_service.sent_sms), 2)
        self.assertEqual(self.sms_service.sent_sms[0]["to"], "+1234567890")
        self.assertEqual(self.sms_service.sent_sms[1]["to"], "+0987654321")

    def test_send_connection_request_sms(self):
        """Test sending connection request SMS."""
        result = self.sms_service.send_connection_request_sms("+1234567890", "John Doe")
        
        self.assertTrue(result)
        self.assertEqual(len(self.sms_service.sent_sms), 1)
        sms = self.sms_service.sent_sms[0]
        self.assertEqual(sms["to"], "+1234567890")
        self.assertIn("New connection request from John Doe", sms["message"])

    def test_get_sent_sms(self):
        """Test getting sent SMS."""
        self.sms_service.send_sms("+1234567890", "Test message")
        
        sent_sms = self.sms_service.get_sent_sms()
        
        self.assertEqual(len(sent_sms), 1)
        self.assertEqual(sent_sms[0]["to"], "+1234567890")

    def test_clear_sent_sms(self):
        """Test clearing sent SMS."""
        self.sms_service.send_sms("+1234567890", "Test message")
        self.assertEqual(len(self.sms_service.sent_sms), 1)
        
        self.sms_service.clear_sent_sms()
        
        self.assertEqual(len(self.sms_service.sent_sms), 0)


class TestMockPushNotificationService(unittest.TestCase):
    """Test cases for MockPushNotificationService."""

    def setUp(self):
        """Set up test fixtures."""
        self.push_service = MockPushNotificationService()

    def test_send_push_notification(self):
        """Test sending push notification."""
        result = self.push_service.send_push_notification("user_001", "Test Title", "Test Message")
        
        self.assertTrue(result)
        self.assertEqual(len(self.push_service.sent_notifications), 1)
        notification = self.push_service.sent_notifications[0]
        self.assertEqual(notification["user_id"], "user_001")
        self.assertEqual(notification["title"], "Test Title")
        self.assertEqual(notification["message"], "Test Message")
        self.assertEqual(notification["data"], {})

    def test_send_push_notification_with_data(self):
        """Test sending push notification with custom data."""
        custom_data = {"type": "test", "value": 123}
        result = self.push_service.send_push_notification("user_001", "Title", "Message", custom_data)
        
        self.assertTrue(result)
        notification = self.push_service.sent_notifications[0]
        self.assertEqual(notification["data"], custom_data)

    def test_send_multiple_notifications(self):
        """Test sending multiple notifications."""
        self.push_service.send_push_notification("user_001", "Title 1", "Message 1")
        self.push_service.send_push_notification("user_002", "Title 2", "Message 2")
        
        self.assertEqual(len(self.push_service.sent_notifications), 2)
        self.assertEqual(self.push_service.sent_notifications[0]["user_id"], "user_001")
        self.assertEqual(self.push_service.sent_notifications[1]["user_id"], "user_002")

    def test_send_connection_request_notification(self):
        """Test sending connection request notification."""
        result = self.push_service.send_connection_request_notification("user_001", "John Doe")
        
        self.assertTrue(result)
        self.assertEqual(len(self.push_service.sent_notifications), 1)
        notification = self.push_service.sent_notifications[0]
        self.assertEqual(notification["user_id"], "user_001")
        self.assertEqual(notification["title"], "New Connection Request")
        self.assertEqual(notification["message"], "John Doe wants to connect with you")
        self.assertEqual(notification["data"]["type"], "connection_request")
        self.assertEqual(notification["data"]["sender_name"], "John Doe")

    def test_send_new_message_notification(self):
        """Test sending new message notification."""
        result = self.push_service.send_new_message_notification("user_001", "John Doe", "Hello there!")
        
        self.assertTrue(result)
        self.assertEqual(len(self.push_service.sent_notifications), 1)
        notification = self.push_service.sent_notifications[0]
        self.assertEqual(notification["user_id"], "user_001")
        self.assertEqual(notification["title"], "New message from John Doe")
        self.assertEqual(notification["message"], "Hello there!")
        self.assertEqual(notification["data"]["type"], "new_message")
        self.assertEqual(notification["data"]["sender_name"], "John Doe")

    def test_send_new_message_notification_long_message(self):
        """Test sending new message notification with long message (should truncate)."""
        long_message = "A" * 150  # 150 characters
        result = self.push_service.send_new_message_notification("user_001", "John Doe", long_message)
        
        self.assertTrue(result)
        notification = self.push_service.sent_notifications[0]
        self.assertEqual(len(notification["message"]), 103)  # 100 chars + "..."
        self.assertTrue(notification["message"].endswith("..."))

    def test_get_sent_notifications(self):
        """Test getting sent notifications."""
        self.push_service.send_push_notification("user_001", "Title", "Message")
        
        sent_notifications = self.push_service.get_sent_notifications()
        
        self.assertEqual(len(sent_notifications), 1)
        self.assertEqual(sent_notifications[0]["user_id"], "user_001")

    def test_clear_sent_notifications(self):
        """Test clearing sent notifications."""
        self.push_service.send_push_notification("user_001", "Title", "Message")
        self.assertEqual(len(self.push_service.sent_notifications), 1)
        
        self.push_service.clear_sent_notifications()
        
        self.assertEqual(len(self.push_service.sent_notifications), 0)


class TestNotificationService(unittest.TestCase):
    """Test cases for NotificationService."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_email_service = Mock()
        self.mock_sms_service = Mock()
        self.mock_push_service = Mock()
        
        self.notification_service = NotificationService(
            self.mock_email_service,
            self.mock_sms_service,
            self.mock_push_service
        )

    def test_notify_connection_request_all_channels(self):
        """Test connection request notification through all channels."""
        self.mock_email_service.send_connection_request_email.return_value = True
        self.mock_sms_service.send_connection_request_sms.return_value = True
        self.mock_push_service.send_connection_request_notification.return_value = True
        
        result = self.notification_service.notify_connection_request(
            "user@example.com", "+1234567890", "user_001", "John Doe"
        )
        
        self.assertEqual(result["email_sent"], True)
        self.assertEqual(result["sms_sent"], True)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_email_service.send_connection_request_email.assert_called_once_with("user@example.com", "John Doe")
        self.mock_sms_service.send_connection_request_sms.assert_called_once_with("+1234567890", "John Doe")
        self.mock_push_service.send_connection_request_notification.assert_called_once_with("user_001", "John Doe")

    def test_notify_connection_request_email_only(self):
        """Test connection request notification with email only."""
        self.mock_email_service.send_connection_request_email.return_value = True
        self.mock_push_service.send_connection_request_notification.return_value = True
        
        result = self.notification_service.notify_connection_request(
            "user@example.com", None, "user_001", "John Doe"
        )
        
        self.assertEqual(result["email_sent"], True)
        self.assertEqual(result["sms_sent"], False)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_sms_service.send_connection_request_sms.assert_not_called()

    def test_notify_connection_request_sms_only(self):
        """Test connection request notification with SMS only."""
        self.mock_sms_service.send_connection_request_sms.return_value = True
        self.mock_push_service.send_connection_request_notification.return_value = True
        
        result = self.notification_service.notify_connection_request(
            None, "+1234567890", "user_001", "John Doe"
        )
        
        self.assertEqual(result["email_sent"], False)
        self.assertEqual(result["sms_sent"], True)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_email_service.send_connection_request_email.assert_not_called()

    def test_notify_connection_request_push_only(self):
        """Test connection request notification with push only."""
        self.mock_push_service.send_connection_request_notification.return_value = True
        
        result = self.notification_service.notify_connection_request(
            None, None, "user_001", "John Doe"
        )
        
        self.assertEqual(result["email_sent"], False)
        self.assertEqual(result["sms_sent"], False)
        self.assertEqual(result["push_sent"], True)

    def test_notify_connection_accepted_all_channels(self):
        """Test connection accepted notification through all channels."""
        self.mock_email_service.send_connection_accepted_email.return_value = True
        self.mock_sms_service.send_sms.return_value = True
        self.mock_push_service.send_push_notification.return_value = True
        
        result = self.notification_service.notify_connection_accepted(
            "user@example.com", "+1234567890", "user_001", "Jane Smith"
        )
        
        self.assertEqual(result["email_sent"], True)
        self.assertEqual(result["sms_sent"], True)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_email_service.send_connection_accepted_email.assert_called_once_with("user@example.com", "Jane Smith")
        self.mock_sms_service.send_sms.assert_called_once_with("+1234567890", "Jane Smith accepted your LinkedIn connection request")
        self.mock_push_service.send_push_notification.assert_called_once()

    def test_notify_connection_accepted_email_only(self):
        """Test connection accepted notification with email only."""
        self.mock_email_service.send_connection_accepted_email.return_value = True
        self.mock_push_service.send_push_notification.return_value = True
        
        result = self.notification_service.notify_connection_accepted(
            "user@example.com", None, "user_001", "Jane Smith"
        )
        
        self.assertEqual(result["email_sent"], True)
        self.assertEqual(result["sms_sent"], False)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_sms_service.send_sms.assert_not_called()

    def test_notify_new_message_all_channels(self):
        """Test new message notification through all channels."""
        self.mock_email_service.send_email.return_value = True
        self.mock_sms_service.send_sms.return_value = True
        self.mock_push_service.send_new_message_notification.return_value = True
        
        result = self.notification_service.notify_new_message(
            "user@example.com", "+1234567890", "user_001", "John Doe", "Hello there!"
        )
        
        self.assertEqual(result["email_sent"], True)
        self.assertEqual(result["sms_sent"], True)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_email_service.send_email.assert_called_once()
        self.mock_sms_service.send_sms.assert_called_once_with("+1234567890", "New message from John Doe on LinkedIn")
        self.mock_push_service.send_new_message_notification.assert_called_once_with("user_001", "John Doe", "Hello there!")

    def test_notify_new_message_email_only(self):
        """Test new message notification with email only."""
        self.mock_email_service.send_email.return_value = True
        self.mock_push_service.send_new_message_notification.return_value = True
        
        result = self.notification_service.notify_new_message(
            "user@example.com", None, "user_001", "John Doe", "Hello there!"
        )
        
        self.assertEqual(result["email_sent"], True)
        self.assertEqual(result["sms_sent"], False)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_sms_service.send_sms.assert_not_called()

    def test_notify_new_message_sms_only(self):
        """Test new message notification with SMS only."""
        self.mock_sms_service.send_sms.return_value = True
        self.mock_push_service.send_new_message_notification.return_value = True
        
        result = self.notification_service.notify_new_message(
            None, "+1234567890", "user_001", "John Doe", "Hello there!"
        )
        
        self.assertEqual(result["email_sent"], False)
        self.assertEqual(result["sms_sent"], True)
        self.assertEqual(result["push_sent"], True)
        
        self.mock_email_service.send_email.assert_not_called()

    def test_notify_new_message_push_only(self):
        """Test new message notification with push only."""
        self.mock_push_service.send_new_message_notification.return_value = True
        
        result = self.notification_service.notify_new_message(
            None, None, "user_001", "John Doe", "Hello there!"
        )
        
        self.assertEqual(result["email_sent"], False)
        self.assertEqual(result["sms_sent"], False)
        self.assertEqual(result["push_sent"], True)

    def test_notify_new_message_email_content(self):
        """Test that email notification includes correct content."""
        self.mock_email_service.send_email.return_value = True
        self.mock_push_service.send_new_message_notification.return_value = True
        
        self.notification_service.notify_new_message(
            "user@example.com", None, "user_001", "John Doe", "Hello there!"
        )
        
        call_args = self.mock_email_service.send_email.call_args
        self.assertEqual(call_args[0][0], "user@example.com")  # to_email
        self.assertEqual(call_args[0][1], "New message from John Doe")  # subject
        self.assertIn("Hello there!", call_args[0][2])  # body contains message
        self.assertIn("John Doe", call_args[0][2])  # body contains sender name


if __name__ == '__main__':
    unittest.main()
