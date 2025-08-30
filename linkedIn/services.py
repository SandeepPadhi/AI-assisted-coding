"""
LinkedIn External Services

External service integrations for email, SMS, and push notifications.
Uses abstract base classes and in-memory/mock implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional


class AbstractEmailService(ABC):
    """Abstract base class for email service operations."""

    @abstractmethod
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send an email to the specified recipient."""
        pass

    @abstractmethod
    def send_connection_request_email(self, to_email: str, sender_name: str) -> bool:
        """Send a connection request notification email."""
        pass

    @abstractmethod
    def send_connection_accepted_email(self, to_email: str, accepter_name: str) -> bool:
        """Send a connection accepted notification email."""
        pass


class MockEmailService(AbstractEmailService):
    """Mock implementation of email service for testing and development."""

    def __init__(self) -> None:
        self.sent_emails: List[dict] = []

    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Mock email sending - logs the email instead of actually sending."""
        email_data = {
            "to": to_email,
            "subject": subject,
            "body": body
        }
        self.sent_emails.append(email_data)
        print(f"[MOCK EMAIL] To: {to_email}, Subject: {subject}")
        return True

    def send_connection_request_email(self, to_email: str, sender_name: str) -> bool:
        """Send a connection request notification email."""
        subject = f"New Connection Request from {sender_name}"
        body = f"""
        Hi there!
        
        {sender_name} has sent you a connection request on LinkedIn.
        Log in to your account to accept or decline this request.
        
        Best regards,
        LinkedIn Team
        """
        return self.send_email(to_email, subject, body)

    def send_connection_accepted_email(self, to_email: str, accepter_name: str) -> bool:
        """Send a connection accepted notification email."""
        subject = f"{accepter_name} accepted your connection request"
        body = f"""
        Great news!
        
        {accepter_name} has accepted your connection request on LinkedIn.
        You can now see their posts in your news feed and send them messages.
        
        Best regards,
        LinkedIn Team
        """
        return self.send_email(to_email, subject, body)

    def get_sent_emails(self) -> List[dict]:
        """Get all sent emails for testing purposes."""
        return self.sent_emails.copy()

    def clear_sent_emails(self) -> None:
        """Clear the sent emails list for testing purposes."""
        self.sent_emails.clear()


class AbstractSMSService(ABC):
    """Abstract base class for SMS service operations."""

    @abstractmethod
    def send_sms(self, phone_number: str, message: str) -> bool:
        """Send an SMS to the specified phone number."""
        pass

    @abstractmethod
    def send_connection_request_sms(self, phone_number: str, sender_name: str) -> bool:
        """Send a connection request notification SMS."""
        pass


class MockSMSService(AbstractSMSService):
    """Mock implementation of SMS service for testing and development."""

    def __init__(self) -> None:
        self.sent_sms: List[dict] = []

    def send_sms(self, phone_number: str, message: str) -> bool:
        """Mock SMS sending - logs the SMS instead of actually sending."""
        sms_data = {
            "to": phone_number,
            "message": message
        }
        self.sent_sms.append(sms_data)
        print(f"[MOCK SMS] To: {phone_number}, Message: {message[:50]}...")
        return True

    def send_connection_request_sms(self, phone_number: str, sender_name: str) -> bool:
        """Send a connection request notification SMS."""
        message = f"New connection request from {sender_name} on LinkedIn. Log in to respond."
        return self.send_sms(phone_number, message)

    def get_sent_sms(self) -> List[dict]:
        """Get all sent SMS for testing purposes."""
        return self.sent_sms.copy()

    def clear_sent_sms(self) -> None:
        """Clear the sent SMS list for testing purposes."""
        self.sent_sms.clear()


class AbstractPushNotificationService(ABC):
    """Abstract base class for push notification service operations."""

    @abstractmethod
    def send_push_notification(self, user_id: str, title: str, message: str, data: Optional[dict] = None) -> bool:
        """Send a push notification to the specified user."""
        pass

    @abstractmethod
    def send_connection_request_notification(self, user_id: str, sender_name: str) -> bool:
        """Send a connection request push notification."""
        pass

    @abstractmethod
    def send_new_message_notification(self, user_id: str, sender_name: str, message_preview: str) -> bool:
        """Send a new message push notification."""
        pass


class MockPushNotificationService(AbstractPushNotificationService):
    """Mock implementation of push notification service for testing and development."""

    def __init__(self) -> None:
        self.sent_notifications: List[dict] = []

    def send_push_notification(self, user_id: str, title: str, message: str, data: Optional[dict] = None) -> bool:
        """Mock push notification sending - logs the notification instead of actually sending."""
        notification_data = {
            "user_id": user_id,
            "title": title,
            "message": message,
            "data": data or {}
        }
        self.sent_notifications.append(notification_data)
        print(f"[MOCK PUSH] To: {user_id}, Title: {title}, Message: {message}")
        return True

    def send_connection_request_notification(self, user_id: str, sender_name: str) -> bool:
        """Send a connection request push notification."""
        title = "New Connection Request"
        message = f"{sender_name} wants to connect with you"
        data = {"type": "connection_request", "sender_name": sender_name}
        return self.send_push_notification(user_id, title, message, data)

    def send_new_message_notification(self, user_id: str, sender_name: str, message_preview: str) -> bool:
        """Send a new message push notification."""
        title = f"New message from {sender_name}"
        message = message_preview[:100] + "..." if len(message_preview) > 100 else message_preview
        data = {"type": "new_message", "sender_name": sender_name}
        return self.send_push_notification(user_id, title, message, data)

    def get_sent_notifications(self) -> List[dict]:
        """Get all sent notifications for testing purposes."""
        return self.sent_notifications.copy()

    def clear_sent_notifications(self) -> None:
        """Clear the sent notifications list for testing purposes."""
        self.sent_notifications.clear()


class NotificationService:
    """Service that coordinates multiple notification channels."""

    def __init__(self, email_service: AbstractEmailService, 
                 sms_service: AbstractSMSService,
                 push_service: AbstractPushNotificationService) -> None:
        self.email_service = email_service
        self.sms_service = sms_service
        self.push_service = push_service

    def notify_connection_request(self, user_email: str, user_phone: Optional[str], 
                                user_id: str, sender_name: str) -> dict:
        """Send connection request notifications through all available channels."""
        results = {
            "email_sent": False,
            "sms_sent": False,
            "push_sent": False
        }

        # Send email notification
        if user_email:
            results["email_sent"] = self.email_service.send_connection_request_email(user_email, sender_name)

        # Send SMS notification
        if user_phone:
            results["sms_sent"] = self.sms_service.send_connection_request_sms(user_phone, sender_name)

        # Send push notification
        results["push_sent"] = self.push_service.send_connection_request_notification(user_id, sender_name)

        return results

    def notify_connection_accepted(self, user_email: str, user_phone: Optional[str], 
                                 user_id: str, accepter_name: str) -> dict:
        """Send connection accepted notifications through all available channels."""
        results = {
            "email_sent": False,
            "sms_sent": False,
            "push_sent": False
        }

        # Send email notification
        if user_email:
            results["email_sent"] = self.email_service.send_connection_accepted_email(user_email, accepter_name)

        # Send SMS notification
        if user_phone:
            message = f"{accepter_name} accepted your LinkedIn connection request"
            results["sms_sent"] = self.sms_service.send_sms(user_phone, message)

        # Send push notification
        title = "Connection Accepted"
        message = f"{accepter_name} accepted your connection request"
        data = {"type": "connection_accepted", "accepter_name": accepter_name}
        results["push_sent"] = self.push_service.send_push_notification(user_id, title, message, data)

        return results

    def notify_new_message(self, user_email: str, user_phone: Optional[str], 
                          user_id: str, sender_name: str, message_preview: str) -> dict:
        """Send new message notifications through all available channels."""
        results = {
            "email_sent": False,
            "sms_sent": False,
            "push_sent": False
        }

        # Send email notification
        if user_email:
            subject = f"New message from {sender_name}"
            body = f"""
            You have a new message from {sender_name} on LinkedIn:
            
            "{message_preview}"
            
            Log in to your account to read the full message.
            
            Best regards,
            LinkedIn Team
            """
            results["email_sent"] = self.email_service.send_email(user_email, subject, body)

        # Send SMS notification
        if user_phone:
            message = f"New message from {sender_name} on LinkedIn"
            results["sms_sent"] = self.sms_service.send_sms(user_phone, message)

        # Send push notification
        results["push_sent"] = self.push_service.send_new_message_notification(user_id, sender_name, message_preview)

        return results
