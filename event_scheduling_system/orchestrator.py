from typing import List, Optional
from datetime import datetime, timedelta
import threading
import time
from entities import Event, Participant, Notification, NotificationType
from repositories import (
    EventRepository, ParticipantRepository, NotificationRepository,
    InMemoryEventRepository, InMemoryParticipantRepository, InMemoryNotificationRepository
)
from managers import EventManager, ParticipantManager, NotificationManager
from services import NotificationDispatcher, EmailService, SMSService, PushNotificationService


class EventSchedulingSystem:
    """Main orchestrator for the event scheduling system"""

    def __init__(self):
        # Initialize repositories
        self.event_repository: EventRepository = InMemoryEventRepository()
        self.participant_repository: ParticipantRepository = InMemoryParticipantRepository()
        self.notification_repository: NotificationRepository = InMemoryNotificationRepository()

        # Initialize managers
        self.event_manager = EventManager(self.event_repository)
        self.participant_manager = ParticipantManager(self.participant_repository)
        self.notification_manager = NotificationManager(
            self.notification_repository, self.event_repository, self.participant_repository
        )

        # Initialize notification dispatcher and services
        self.notification_dispatcher = NotificationDispatcher()
        self.notification_dispatcher.register_service(EmailService())
        self.notification_dispatcher.register_service(SMSService())
        self.notification_dispatcher.register_service(PushNotificationService())

        # Background notification processor
        self._notification_processor_thread: Optional[threading.Thread] = None
        self._stop_processing = threading.Event()
        self._lock = threading.RLock()

    # Event Management Methods
    def create_event(self, title: str, description: str,
                    start_time: datetime, end_time: datetime,
                    creator_id: str) -> Event:
        """Create a new event"""
        return self.event_manager.create_event(title, description, start_time, end_time, creator_id)

    def get_event(self, event_id: str) -> Optional[Event]:
        """Get an event by ID"""
        return self.event_manager.get_event(event_id)

    def get_all_events(self) -> List[Event]:
        """Get all events"""
        return self.event_manager.get_all_events()

    def update_event(self, event_id: str, title: Optional[str] = None,
                    description: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> Event:
        """Update an existing event"""
        return self.event_manager.update_event(event_id, title, description, start_time, end_time)

    def delete_event(self, event_id: str) -> bool:
        """Delete an event and all its associated data"""
        with self._lock:
            # Remove all participants first
            self.participant_manager.remove_all_participants_from_event(event_id)

            # Remove all notifications
            event_notifications = self.notification_manager.get_event_notifications(event_id)
            for notification in event_notifications:
                self.notification_manager.delete_notification(notification.notification_id)

            # Delete the event
            return self.event_manager.delete_event(event_id)

    # Participant Management Methods
    def add_participant(self, event_id: str, user_id: str,
                       name: str, email: str,
                       phone: Optional[str] = None) -> Participant:
        """Add a participant to an event"""
        return self.participant_manager.add_participant(event_id, user_id, name, email, phone)

    def get_event_participants(self, event_id: str) -> List[Participant]:
        """Get all participants for an event"""
        return self.participant_manager.get_event_participants(event_id)

    def remove_participant(self, participant_id: str) -> bool:
        """Remove a participant from an event"""
        with self._lock:
            # Remove all notifications for this participant first
            participant_notifications = self.notification_manager.get_participant_notifications(participant_id)
            for notification in participant_notifications:
                self.notification_manager.delete_notification(notification.notification_id)

            # Remove the participant
            return self.participant_manager.remove_participant(participant_id)

    def update_participant_contact(self, participant_id: str,
                                  name: Optional[str] = None,
                                  email: Optional[str] = None,
                                  phone: Optional[str] = None) -> Participant:
        """Update a participant's contact information"""
        return self.participant_manager.update_participant_contact(participant_id, name, email, phone)

    # Notification Management Methods
    def schedule_event_notifications(self, event_id: str,
                                    minutes_before: int = 60) -> List[Notification]:
        """Schedule notifications for all participants of an event"""
        return self.notification_manager.schedule_event_notifications(event_id, minutes_before)

    def send_pending_notifications(self) -> List[Notification]:
        """Send all pending notifications and return those that were sent"""
        pending_notifications = self.notification_manager.get_pending_notifications()

        if not pending_notifications:
            return []

        sent_notifications = []

        for notification in pending_notifications:
            if self.notification_dispatcher.send_notification(notification):
                self.notification_manager.mark_notification_sent(notification.notification_id)
                sent_notifications.append(notification)

        return sent_notifications

    def get_event_notifications(self, event_id: str) -> List[Notification]:
        """Get all notifications for an event"""
        return self.notification_manager.get_event_notifications(event_id)

    def get_pending_notifications(self) -> List[Notification]:
        """Get all pending notifications"""
        return self.notification_manager.get_pending_notifications()

    # Background Processing Methods
    def start_notification_processor(self, check_interval_seconds: int = 30) -> None:
        """Start the background notification processor"""
        with self._lock:
            if self._notification_processor_thread and self._notification_processor_thread.is_alive():
                print("⚠️  Notification processor is already running")
                return

            self._stop_processing.clear()
            self._notification_processor_thread = threading.Thread(
                target=self._notification_processor_loop,
                args=(check_interval_seconds,),
                daemon=True
            )
            self._notification_processor_thread.start()
            print("🔔 Started background notification processor")

    def stop_notification_processor(self) -> None:
        """Stop the background notification processor"""
        with self._lock:
            if not self._notification_processor_thread or not self._notification_processor_thread.is_alive():
                print("⚠️  Notification processor is not running")
                return

            self._stop_processing.set()
            self._notification_processor_thread.join(timeout=5.0)
            print("🔔 Stopped background notification processor")

    def _notification_processor_loop(self, check_interval_seconds: int) -> None:
        """Background loop to process pending notifications"""
        while not self._stop_processing.is_set():
            try:
                sent_notifications = self.send_pending_notifications()
                if sent_notifications:
                    print(f"📤 Processed {len(sent_notifications)} notifications")

                # Wait before next check
                self._stop_processing.wait(check_interval_seconds)

            except Exception as e:
                print(f"❌ Error in notification processor: {e}")
                self._stop_processing.wait(5)  # Wait 5 seconds before retrying

    # Utility Methods
    def get_upcoming_events(self, minutes_ahead: int = 60) -> List[Event]:
        """Get events that are starting soon"""
        return self.event_manager.get_upcoming_events(minutes_ahead)

    def get_system_stats(self) -> dict:
        """Get system statistics"""
        with self._lock:
            return {
                "total_events": len(self.event_manager.get_all_events()),
                "total_participants": len(self.participant_manager.get_all_participants()),
                "total_notifications": len(self.notification_manager.get_all_notifications()),
                "pending_notifications": len(self.notification_manager.get_pending_notifications()),
                "notification_processor_running": (
                    self._notification_processor_thread is not None and
                    self._notification_processor_thread.is_alive()
                )
            }

    def cleanup_old_notifications(self, days_old: int = 30) -> int:
        """Clean up old notifications. Returns number of notifications deleted"""
        with self._lock:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            all_notifications = self.notification_manager.get_all_notifications()

            deleted_count = 0
            for notification in all_notifications:
                if notification.sent_at and notification.sent_at < cutoff_date:
                    if self.notification_manager.delete_notification(notification.notification_id):
                        deleted_count += 1

            return deleted_count
