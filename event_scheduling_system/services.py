from abc import ABC, abstractmethod
from typing import Optional
import time
import threading
from entities import Notification, NotificationType


class NotificationService(ABC):
    @abstractmethod
    def send_notification(self, notification: Notification) -> bool:
        """Send a notification. Returns True if sent successfully, False otherwise"""
        pass

    @abstractmethod
    def get_service_type(self) -> NotificationType:
        """Get the type of notification this service handles"""
        pass


class EmailService(NotificationService):
    def __init__(self, smtp_server: str = "smtp.example.com",
                 smtp_port: int = 587, username: str = "",
                 password: str = ""):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self._lock = threading.RLock()

    def send_notification(self, notification: Notification) -> bool:
        """Send an email notification"""
        with self._lock:
            if notification.notification_type != NotificationType.EMAIL:
                return False

            try:
                # Simulate email sending with a delay
                print("📧 [EMAIL SERVICE] Sending email notification...")
                print(f"   To: {notification.participant_id}")  # In real app, this would be actual email
                print(f"   Subject: Event Notification")
                print(f"   Message: {notification.message}")
                print("   Status: SENT ✅")
                time.sleep(0.1)  # Simulate network delay
                return True
            except Exception as e:
                print(f"❌ [EMAIL SERVICE] Failed to send email: {e}")
                return False

    def get_service_type(self) -> NotificationType:
        return NotificationType.EMAIL


class SMSService(NotificationService):
    def __init__(self, api_key: str = "", api_secret: str = "",
                 provider_url: str = "https://api.sms-provider.com"):
        self.api_key = api_key
        self.api_secret = api_secret
        self.provider_url = provider_url
        self._lock = threading.RLock()

    def send_notification(self, notification: Notification) -> bool:
        """Send an SMS notification"""
        with self._lock:
            if notification.notification_type != NotificationType.SMS:
                return False

            try:
                # Simulate SMS sending with a delay
                print("📱 [SMS SERVICE] Sending SMS notification...")
                print(f"   To: {notification.participant_id}")  # In real app, this would be actual phone
                print(f"   Message: {notification.message}")
                print("   Status: SENT ✅")
                time.sleep(0.15)  # Simulate network delay
                return True
            except Exception as e:
                print(f"❌ [SMS SERVICE] Failed to send SMS: {e}")
                return False

    def get_service_type(self) -> NotificationType:
        return NotificationType.SMS


class PushNotificationService(NotificationService):
    def __init__(self, app_id: str = "", server_key: str = "",
                 fcm_url: str = "https://fcm.googleapis.com/fcm/send"):
        self.app_id = app_id
        self.server_key = server_key
        self.fcm_url = fcm_url
        self._lock = threading.RLock()

    def send_notification(self, notification: Notification) -> bool:
        """Send a push notification"""
        with self._lock:
            if notification.notification_type != NotificationType.PUSH:
                return False

            try:
                # Simulate push notification sending with a delay
                print("🔔 [PUSH SERVICE] Sending push notification...")
                print(f"   To: {notification.participant_id}")  # In real app, this would be device token
                print(f"   Title: Event Reminder")
                print(f"   Message: {notification.message}")
                print("   Status: SENT ✅")
                time.sleep(0.05)  # Simulate network delay
                return True
            except Exception as e:
                print(f"❌ [PUSH SERVICE] Failed to send push notification: {e}")
                return False

    def get_service_type(self) -> NotificationType:
        return NotificationType.PUSH


class NotificationDispatcher:
    """Dispatcher to route notifications to appropriate services"""

    def __init__(self):
        self.services: dict[NotificationType, NotificationService] = {}
        self._lock = threading.RLock()

    def register_service(self, service: NotificationService) -> None:
        """Register a notification service"""
        with self._lock:
            self.services[service.get_service_type()] = service

    def send_notification(self, notification: Notification) -> bool:
        """Send a notification using the appropriate service"""
        with self._lock:
            service = self.services.get(notification.notification_type)
            if not service:
                print(f"❌ No service registered for notification type: {notification.notification_type}")
                return False

            return service.send_notification(notification)

    def send_bulk_notifications(self, notifications: list[Notification]) -> dict[str, bool]:
        """Send multiple notifications. Returns dict of notification_id -> success"""
        results = {}
        for notification in notifications:
            notification_id = notification.notification_id
            success = self.send_notification(notification)
            results[notification_id] = success
        return results
