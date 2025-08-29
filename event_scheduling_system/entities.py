from datetime import datetime, timedelta
from typing import List, Optional
from enum import Enum


class NotificationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"


class Event:
    def __init__(self, event_id: str, title: str, description: str,
                 start_time: datetime, end_time: datetime, creator_id: str):
        self._validate_inputs(title, description, start_time, end_time)

        self.event_id = event_id
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.creator_id = creator_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def _validate_inputs(self, title: str, description: str,
                        start_time: datetime, end_time: datetime) -> None:
        if not title or not title.strip():
            raise ValueError("Event title cannot be empty")

        if not description or not description.strip():
            raise ValueError("Event description cannot be empty")

        if start_time >= end_time:
            raise ValueError("Event start time must be before end time")

        if start_time <= datetime.now():
            raise ValueError("Event start time must be in the future")

    def update_details(self, title: Optional[str] = None,
                      description: Optional[str] = None,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> None:
        if title is not None:
            if not title or not title.strip():
                raise ValueError("Event title cannot be empty")
            self.title = title

        if description is not None:
            if not description or not description.strip():
                raise ValueError("Event description cannot be empty")
            self.description = description

        if start_time is not None or end_time is not None:
            new_start = start_time if start_time is not None else self.start_time
            new_end = end_time if end_time is not None else self.end_time

            if new_start >= new_end:
                raise ValueError("Event start time must be before end time")
            if new_start <= datetime.now():
                raise ValueError("Event start time must be in the future")

            self.start_time = new_start
            self.end_time = new_end

        self.updated_at = datetime.now()

    def is_upcoming(self, minutes_ahead: int = 60) -> bool:
        """Check if event is starting within specified minutes"""
        from datetime import timedelta
        check_time = datetime.now() + timedelta(minutes=minutes_ahead)
        return self.start_time <= check_time and self.start_time > datetime.now()

    def get_duration_minutes(self) -> int:
        """Get event duration in minutes"""
        duration = self.end_time - self.start_time
        return int(duration.total_seconds() / 60)


class Participant:
    def __init__(self, participant_id: str, event_id: str, user_id: str,
                 name: str, email: str, phone: Optional[str] = None):
        self._validate_inputs(name, email, phone)

        self.participant_id = participant_id
        self.event_id = event_id
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
        self.joined_at = datetime.now()

    def _validate_inputs(self, name: str, email: str, phone: Optional[str]) -> None:
        if not name or not name.strip():
            raise ValueError("Participant name cannot be empty")

        if not email or not email.strip():
            raise ValueError("Participant email cannot be empty")

        if "@" not in email or "." not in email:
            raise ValueError("Invalid email format")

        if phone and (not phone.strip() or len(phone.strip()) < 10):
            raise ValueError("Invalid phone number format")

    def update_contact_info(self, name: Optional[str] = None,
                           email: Optional[str] = None,
                           phone: Optional[str] = None) -> None:
        if name is not None:
            if not name or not name.strip():
                raise ValueError("Participant name cannot be empty")
            self.name = name

        if email is not None:
            if not email or not email.strip():
                raise ValueError("Participant email cannot be empty")
            if "@" not in email or "." not in email:
                raise ValueError("Invalid email format")
            self.email = email

        if phone is not None:
            if phone and (not phone.strip() or len(phone.strip()) < 10):
                raise ValueError("Invalid phone number format")
            self.phone = phone


class Notification:
    def __init__(self, notification_id: str, event_id: str, participant_id: str,
                 notification_type: NotificationType, message: str,
                 scheduled_time: datetime):
        self._validate_inputs(message, scheduled_time)

        self.notification_id = notification_id
        self.event_id = event_id
        self.participant_id = participant_id
        self.notification_type = notification_type
        self.message = message
        self.scheduled_time = scheduled_time
        self.sent_at: Optional[datetime] = None
        self.is_sent = False
        self.created_at = datetime.now()

    def _validate_inputs(self, message: str, scheduled_time: datetime) -> None:
        if not message or not message.strip():
            raise ValueError("Notification message cannot be empty")

        # Allow notifications within the last minute (for immediate/demo purposes)
        if scheduled_time <= datetime.now() - timedelta(minutes=1):
            raise ValueError("Scheduled time cannot be more than 1 minute in the past")

    def mark_as_sent(self) -> None:
        """Mark notification as sent"""
        self.sent_at = datetime.now()
        self.is_sent = True

    def is_ready_to_send(self) -> bool:
        """Check if notification is ready to be sent"""
        return not self.is_sent and datetime.now() >= self.scheduled_time

    def get_time_until_send(self) -> int:
        """Get minutes until notification should be sent"""
        if self.is_sent or datetime.now() >= self.scheduled_time:
            return 0

        time_diff = self.scheduled_time - datetime.now()
        return max(0, int(time_diff.total_seconds() / 60))
