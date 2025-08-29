from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
import threading
from entities import Event, Participant, Notification, NotificationType


class EventRepository(ABC):
    @abstractmethod
    def save_event(self, event: Event) -> None:
        """Save a new event to the repository"""
        pass

    @abstractmethod
    def find_event_by_id(self, event_id: str) -> Optional[Event]:
        """Find an event by its ID"""
        pass

    @abstractmethod
    def find_all_events(self) -> List[Event]:
        """Retrieve all events"""
        pass

    @abstractmethod
    def find_events_by_creator(self, creator_id: str) -> List[Event]:
        """Find all events created by a specific user"""
        pass

    @abstractmethod
    def find_upcoming_events(self, minutes_ahead: int = 60) -> List[Event]:
        """Find events that are starting within specified minutes"""
        pass

    @abstractmethod
    def update_event(self, event: Event) -> None:
        """Update an existing event"""
        pass

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID. Returns True if deleted, False if not found"""
        pass


class ParticipantRepository(ABC):
    @abstractmethod
    def save_participant(self, participant: Participant) -> None:
        """Save a new participant to the repository"""
        pass

    @abstractmethod
    def find_participant_by_id(self, participant_id: str) -> Optional[Participant]:
        """Find a participant by their ID"""
        pass

    @abstractmethod
    def find_participants_by_event(self, event_id: str) -> List[Participant]:
        """Find all participants for a specific event"""
        pass

    @abstractmethod
    def find_participant_by_event_and_user(self, event_id: str, user_id: str) -> Optional[Participant]:
        """Find a participant by event and user combination"""
        pass

    @abstractmethod
    def find_all_participants(self) -> List[Participant]:
        """Retrieve all participants"""
        pass

    @abstractmethod
    def update_participant(self, participant: Participant) -> None:
        """Update an existing participant"""
        pass

    @abstractmethod
    def delete_participant(self, participant_id: str) -> bool:
        """Delete a participant by ID. Returns True if deleted, False if not found"""
        pass

    @abstractmethod
    def delete_participants_by_event(self, event_id: str) -> int:
        """Delete all participants for an event. Returns number of participants deleted"""
        pass


class NotificationRepository(ABC):
    @abstractmethod
    def save_notification(self, notification: Notification) -> None:
        """Save a new notification to the repository"""
        pass

    @abstractmethod
    def find_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Find a notification by its ID"""
        pass

    @abstractmethod
    def find_notifications_by_event(self, event_id: str) -> List[Notification]:
        """Find all notifications for a specific event"""
        pass

    @abstractmethod
    def find_notifications_by_participant(self, participant_id: str) -> List[Notification]:
        """Find all notifications for a specific participant"""
        pass

    @abstractmethod
    def find_pending_notifications(self) -> List[Notification]:
        """Find all notifications that are ready to be sent but not yet sent"""
        pass

    @abstractmethod
    def find_all_notifications(self) -> List[Notification]:
        """Retrieve all notifications"""
        pass

    @abstractmethod
    def update_notification(self, notification: Notification) -> None:
        """Update an existing notification"""
        pass

    @abstractmethod
    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification by ID. Returns True if deleted, False if not found"""
        pass

    @abstractmethod
    def mark_notification_as_sent(self, notification_id: str) -> bool:
        """Mark a notification as sent. Returns True if updated, False if not found"""
        pass


class InMemoryEventRepository(EventRepository):
    def __init__(self):
        self._events: Dict[str, Event] = {}
        self._lock = threading.RLock()

    def save_event(self, event: Event) -> None:
        """Save a new event to the repository"""
        with self._lock:
            if event.event_id in self._events:
                raise ValueError(f"Event with ID {event.event_id} already exists")
            self._events[event.event_id] = event

    def find_event_by_id(self, event_id: str) -> Optional[Event]:
        """Find an event by its ID"""
        with self._lock:
            return self._events.get(event_id)

    def find_all_events(self) -> List[Event]:
        """Retrieve all events"""
        with self._lock:
            return list(self._events.values())

    def find_events_by_creator(self, creator_id: str) -> List[Event]:
        """Find all events created by a specific user"""
        with self._lock:
            return [event for event in self._events.values()
                   if event.creator_id == creator_id]

    def find_upcoming_events(self, minutes_ahead: int = 60) -> List[Event]:
        """Find events that are starting within specified minutes"""
        with self._lock:
            return [event for event in self._events.values()
                   if event.is_upcoming(minutes_ahead)]

    def update_event(self, event: Event) -> None:
        """Update an existing event"""
        with self._lock:
            if event.event_id not in self._events:
                raise ValueError(f"Event with ID {event.event_id} not found")
            self._events[event.event_id] = event

    def delete_event(self, event_id: str) -> bool:
        """Delete an event by ID. Returns True if deleted, False if not found"""
        with self._lock:
            if event_id in self._events:
                del self._events[event_id]
                return True
            return False


class InMemoryParticipantRepository(ParticipantRepository):
    def __init__(self):
        self._participants: Dict[str, Participant] = {}
        self._event_participants: Dict[str, List[str]] = {}  # event_id -> [participant_ids]
        self._user_participants: Dict[str, List[str]] = {}   # user_id -> [participant_ids]
        self._lock = threading.RLock()

    def save_participant(self, participant: Participant) -> None:
        """Save a new participant to the repository"""
        with self._lock:
            if participant.participant_id in self._participants:
                raise ValueError(f"Participant with ID {participant.participant_id} already exists")

            self._participants[participant.participant_id] = participant

            # Update indexes
            if participant.event_id not in self._event_participants:
                self._event_participants[participant.event_id] = []
            self._event_participants[participant.event_id].append(participant.participant_id)

            if participant.user_id not in self._user_participants:
                self._user_participants[participant.user_id] = []
            self._user_participants[participant.user_id].append(participant.participant_id)

    def find_participant_by_id(self, participant_id: str) -> Optional[Participant]:
        """Find a participant by their ID"""
        with self._lock:
            return self._participants.get(participant_id)

    def find_participants_by_event(self, event_id: str) -> List[Participant]:
        """Find all participants for a specific event"""
        with self._lock:
            participant_ids = self._event_participants.get(event_id, [])
            return [self._participants[pid] for pid in participant_ids if pid in self._participants]

    def find_participant_by_event_and_user(self, event_id: str, user_id: str) -> Optional[Participant]:
        """Find a participant by event and user combination"""
        with self._lock:
            participants = self.find_participants_by_event(event_id)
            return next((p for p in participants if p.user_id == user_id), None)

    def find_all_participants(self) -> List[Participant]:
        """Retrieve all participants"""
        with self._lock:
            return list(self._participants.values())

    def update_participant(self, participant: Participant) -> None:
        """Update an existing participant"""
        with self._lock:
            if participant.participant_id not in self._participants:
                raise ValueError(f"Participant with ID {participant.participant_id} not found")
            self._participants[participant.participant_id] = participant

    def delete_participant(self, participant_id: str) -> bool:
        """Delete a participant by ID. Returns True if deleted, False if not found"""
        with self._lock:
            if participant_id not in self._participants:
                return False

            participant = self._participants[participant_id]

            # Remove from indexes
            if participant.event_id in self._event_participants:
                self._event_participants[participant.event_id].remove(participant_id)
                if not self._event_participants[participant.event_id]:
                    del self._event_participants[participant.event_id]

            if participant.user_id in self._user_participants:
                self._user_participants[participant.user_id].remove(participant_id)
                if not self._user_participants[participant.user_id]:
                    del self._user_participants[participant.user_id]

            del self._participants[participant_id]
            return True

    def delete_participants_by_event(self, event_id: str) -> int:
        """Delete all participants for an event. Returns number of participants deleted"""
        with self._lock:
            if event_id not in self._event_participants:
                return 0

            participant_ids = self._event_participants[event_id][:]
            deleted_count = 0

            for participant_id in participant_ids:
                if self.delete_participant(participant_id):
                    deleted_count += 1

            return deleted_count


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self):
        self._notifications: Dict[str, Notification] = {}
        self._event_notifications: Dict[str, List[str]] = {}  # event_id -> [notification_ids]
        self._participant_notifications: Dict[str, List[str]] = {}  # participant_id -> [notification_ids]
        self._lock = threading.RLock()

    def save_notification(self, notification: Notification) -> None:
        """Save a new notification to the repository"""
        with self._lock:
            if notification.notification_id in self._notifications:
                raise ValueError(f"Notification with ID {notification.notification_id} already exists")

            self._notifications[notification.notification_id] = notification

            # Update indexes
            if notification.event_id not in self._event_notifications:
                self._event_notifications[notification.event_id] = []
            self._event_notifications[notification.event_id].append(notification.notification_id)

            if notification.participant_id not in self._participant_notifications:
                self._participant_notifications[notification.participant_id] = []
            self._participant_notifications[notification.participant_id].append(notification.notification_id)

    def find_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Find a notification by its ID"""
        with self._lock:
            return self._notifications.get(notification_id)

    def find_notifications_by_event(self, event_id: str) -> List[Notification]:
        """Find all notifications for a specific event"""
        with self._lock:
            notification_ids = self._event_notifications.get(event_id, [])
            return [self._notifications[nid] for nid in notification_ids if nid in self._notifications]

    def find_notifications_by_participant(self, participant_id: str) -> List[Notification]:
        """Find all notifications for a specific participant"""
        with self._lock:
            notification_ids = self._participant_notifications.get(participant_id, [])
            return [self._notifications[nid] for nid in notification_ids if nid in self._notifications]

    def find_pending_notifications(self) -> List[Notification]:
        """Find all notifications that are ready to be sent but not yet sent"""
        with self._lock:
            return [notification for notification in self._notifications.values()
                   if notification.is_ready_to_send()]

    def find_all_notifications(self) -> List[Notification]:
        """Retrieve all notifications"""
        with self._lock:
            return list(self._notifications.values())

    def update_notification(self, notification: Notification) -> None:
        """Update an existing notification with additional validations"""
        if not isinstance(notification, Notification):
            raise TypeError("Provided object is not a Notification instance")
        if not notification.notification_id or not isinstance(notification.notification_id, str):
            raise ValueError("Notification must have a valid notification_id (non-empty string)")
        if not notification.event_id or not isinstance(notification.event_id, str):
            raise ValueError("Notification must have a valid event_id (non-empty string)")
        if not notification.participant_id or not isinstance(notification.participant_id, str):
            raise ValueError("Notification must have a valid participant_id (non-empty string)")
        if not notification.message or not isinstance(notification.message, str):
            raise ValueError("Notification must have a valid message (non-empty string)")
        if notification.scheduled_time is None or not isinstance(notification.scheduled_time, datetime):
            raise ValueError("Notification must have a valid scheduled_time (datetime object)")
        if notification.notification_type is None:
            raise ValueError("Notification must have a valid notification_type")
        with self._lock:
            if notification.notification_id not in self._notifications:
                raise ValueError(f"Notification with ID {notification.notification_id} not found")
            # Prevent changing the notification_id
            existing = self._notifications[notification.notification_id]
            if notification.notification_id != existing.notification_id:
                raise ValueError("Cannot change notification_id of an existing notification")
            # Optionally, prevent changing event_id and participant_id for integrity
            if notification.event_id != existing.event_id:
                raise ValueError("Cannot change event_id of an existing notification")
            if notification.participant_id != existing.participant_id:
                raise ValueError("Cannot change participant_id of an existing notification")
            self._notifications[notification.notification_id] = notification

    def delete_notification(self, notification_id: str) -> bool:
        """Delete a notification by ID. Returns True if deleted, False if not found"""
        with self._lock:
            if notification_id not in self._notifications:
                return False

            notification = self._notifications[notification_id]

            # Remove from indexes
            if notification.event_id in self._event_notifications:
                self._event_notifications[notification.event_id].remove(notification_id)
                if not self._event_notifications[notification.event_id]:
                    del self._event_notifications[notification.event_id]

            if notification.participant_id in self._participant_notifications:
                self._participant_notifications[notification.participant_id].remove(notification_id)
                if not self._participant_notifications[notification.participant_id]:
                    del self._participant_notifications[notification.participant_id]

            del self._notifications[notification_id]
            return True

    def mark_notification_as_sent(self, notification_id: str) -> bool:
        """Mark a notification as sent. Returns True if updated, False if not found"""
        with self._lock:
            notification = self.find_notification_by_id(notification_id)
            if notification:
                notification.mark_as_sent()
                return True
            return False
