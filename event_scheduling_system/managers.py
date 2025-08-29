import uuid
from typing import List, Optional
from datetime import datetime, timedelta
import threading
from entities import Event, Participant, Notification, NotificationType
from repositories import (
    EventRepository, ParticipantRepository, NotificationRepository
)


class EventManager:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository
        self._lock = threading.RLock()

    def create_event(self, title: str, description: str,
                    start_time: datetime, end_time: datetime,
                    creator_id: str) -> Event:
        """Create a new event and save it to the repository"""
        with self._lock:
            event_id = str(uuid.uuid4())
            event = Event(event_id, title, description, start_time, end_time, creator_id)
            self.event_repository.save_event(event)
            return event

    def get_event(self, event_id: str) -> Optional[Event]:
        """Retrieve an event by its ID"""
        return self.event_repository.find_event_by_id(event_id)

    def get_all_events(self) -> List[Event]:
        """Retrieve all events"""
        return self.event_repository.find_all_events()

    def get_events_by_creator(self, creator_id: str) -> List[Event]:
        """Get all events created by a specific user"""
        return self.event_repository.find_events_by_creator(creator_id)

    def get_upcoming_events(self, minutes_ahead: int = 60) -> List[Event]:
        """Get events that are starting within specified minutes"""
        return self.event_repository.find_upcoming_events(minutes_ahead)

    def update_event(self, event_id: str, title: Optional[str] = None,
                    description: Optional[str] = None,
                    start_time: Optional[datetime] = None,
                    end_time: Optional[datetime] = None) -> Event:
        """Update an existing event's details"""
        with self._lock:
            event = self.event_repository.find_event_by_id(event_id)
            if not event:
                raise ValueError(f"Event with ID {event_id} not found")

            event.update_details(title, description, start_time, end_time)
            self.event_repository.update_event(event)
            return event

    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID. Returns True if deleted, False if not found"""
        with self._lock:
            return self.event_repository.delete_event(event_id)

    def get_event_participants_count(self, event_id: str) -> int:
        """Get the number of participants for an event"""
        # This will be implemented when we have the participant repository
        # For now, return 0
        return 0


class ParticipantManager:
    def __init__(self, participant_repository: ParticipantRepository):
        self.participant_repository = participant_repository
        self._lock = threading.RLock()

    def add_participant(self, event_id: str, user_id: str,
                       name: str, email: str,
                       phone: Optional[str] = None) -> Participant:
        """Add a participant to an event"""
        with self._lock:
            # Check if participant already exists for this event and user
            existing_participant = self.participant_repository.find_participant_by_event_and_user(
                event_id, user_id
            )
            if existing_participant:
                raise ValueError(f"User {user_id} is already a participant in event {event_id}")

            participant_id = str(uuid.uuid4())
            participant = Participant(participant_id, event_id, user_id, name, email, phone)
            self.participant_repository.save_participant(participant)
            return participant

    def get_participant(self, participant_id: str) -> Optional[Participant]:
        """Retrieve a participant by their ID"""
        return self.participant_repository.find_participant_by_id(participant_id)

    def get_event_participants(self, event_id: str) -> List[Participant]:
        """Get all participants for a specific event"""
        return self.participant_repository.find_participants_by_event(event_id)

    def get_all_participants(self) -> List[Participant]:
        """Retrieve all participants across all events"""
        return self.participant_repository.find_all_participants()

    def update_participant_contact(self, participant_id: str,
                                  name: Optional[str] = None,
                                  email: Optional[str] = None,
                                  phone: Optional[str] = None) -> Participant:
        """Update a participant's contact information"""
        with self._lock:
            participant = self.participant_repository.find_participant_by_id(participant_id)
            if not participant:
                raise ValueError(f"Participant with ID {participant_id} not found")

            participant.update_contact_info(name, email, phone)
            self.participant_repository.update_participant(participant)
            return participant

    def remove_participant(self, participant_id: str) -> bool:
        """Remove a participant from an event. Returns True if removed, False if not found"""
        with self._lock:
            return self.participant_repository.delete_participant(participant_id)

    def remove_all_participants_from_event(self, event_id: str) -> int:
        """Remove all participants from an event. Returns number of participants removed"""
        with self._lock:
            return self.participant_repository.delete_participants_by_event(event_id)


class NotificationManager:
    def __init__(self, notification_repository: NotificationRepository,
                 event_repository: EventRepository,
                 participant_repository: ParticipantRepository):
        self.notification_repository = notification_repository
        self.event_repository = event_repository
        self.participant_repository = participant_repository
        self._lock = threading.RLock()

    def schedule_event_notifications(self, event_id: str,
                                    minutes_before: int = 60) -> List[Notification]:
        """Schedule notifications for all participants of an event"""
        with self._lock:
            event = self.event_repository.find_event_by_id(event_id)
            if not event:
                raise ValueError(f"Event with ID {event_id} not found")

            participants = self.participant_repository.find_participants_by_event(event_id)
            if not participants:
                return []

            # Calculate notification time
            notification_time = event.start_time - timedelta(minutes=minutes_before)

            notifications = []
            for participant in participants:
                # Create notification for each type if contact info is available
                if participant.email:
                    email_notification = self._create_notification(
                        event, participant, NotificationType.EMAIL,
                        f"Event '{event.title}' is starting at {event.start_time.strftime('%Y-%m-%d %H:%M')}",
                        notification_time
                    )
                    notifications.append(email_notification)

                if participant.phone:
                    sms_notification = self._create_notification(
                        event, participant, NotificationType.SMS,
                        f"Event '{event.title}' starts at {event.start_time.strftime('%H:%M')}",
                        notification_time
                    )
                    notifications.append(sms_notification)

                # Always create push notification
                push_notification = self._create_notification(
                    event, participant, NotificationType.PUSH,
                    f"⏰ Event '{event.title}' is starting soon!",
                    notification_time
                )
                notifications.append(push_notification)

            return notifications

    def _create_notification(self, event: Event, participant: Participant,
                            notification_type: NotificationType,
                            message: str, scheduled_time: datetime) -> Notification:
        """Create a notification for a participant"""
        notification_id = str(uuid.uuid4())
        notification = Notification(
            notification_id, event.event_id, participant.participant_id,
            notification_type, message, scheduled_time
        )
        self.notification_repository.save_notification(notification)
        return notification

    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """Retrieve a notification by its ID"""
        return self.notification_repository.find_notification_by_id(notification_id)

    def get_event_notifications(self, event_id: str) -> List[Notification]:
        """Get all notifications for a specific event"""
        return self.notification_repository.find_notifications_by_event(event_id)

    def get_participant_notifications(self, participant_id: str) -> List[Notification]:
        """Get all notifications for a specific participant"""
        return self.notification_repository.find_notifications_by_participant(participant_id)

    def get_pending_notifications(self) -> List[Notification]:
        """Get all notifications that are ready to be sent"""
        return self.notification_repository.find_pending_notifications()

    def get_all_notifications(self) -> List[Notification]:
        """Retrieve all notifications"""
        return self.notification_repository.find_all_notifications()

    def mark_notification_sent(self, notification_id: str) -> bool:
        """Mark a notification as sent. Returns True if marked, False if not found"""
        with self._lock:
            return self.notification_repository.mark_notification_as_sent(notification_id)

    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification by ID. Returns True if deleted, False if not found"""
        with self._lock:
            return self.notification_repository.delete_notification(notification_id)

    def process_pending_notifications(self) -> List[Notification]:
        """Process and mark pending notifications as sent. Returns processed notifications"""
        with self._lock:
            pending_notifications = self.get_pending_notifications()
            processed_notifications = []

            for notification in pending_notifications:
                if self.mark_notification_sent(notification.notification_id):
                    processed_notifications.append(notification)

            return processed_notifications
