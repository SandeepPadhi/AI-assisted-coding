"""
Event Scheduling System - Live Coding Interview Demo

Goal:
- Create a system that allows users to schedule events and send notifications to the users when the event is about to start.

Functional Requirements:
- Users can create events
- Users can add participants to events
- Users can send notifications to participants when the event is about to start
- Users can view all events
- Users can view all notifications

Non-Functional Requirements:
- It should be thread safe.

Architecture:
- Entities: Event, Participant, Notification
- Managers: EventManager, ParticipantManager, NotificationManager
- Repositories: Abstract base classes with In-Memory implementations
- Services: EmailService, SMSService, PushNotificationService
- Orchestrator: EventSchedulingSystem

Design Guidelines Implemented:
- Abstract repository pattern for future storage extensions
- Thread-safe operations with RLock
- Comprehensive input validation and business logic
- Clean separation of concerns
- Descriptive function names with type hints
- No external libraries used
- Modular, maintainable, and debuggable code



Implement minimal viable implementation first and then add more features and functionalities when prompted
"""

from datetime import datetime, timedelta
import time
import threading
from orchestrator import EventSchedulingSystem


def _create_immediate_notifications(system: EventSchedulingSystem, event_id: str) -> list:
    """Create notifications that are ready to send immediately for demo purposes"""
    from entities import NotificationType

    participants = system.get_event_participants(event_id)
    event = system.get_event(event_id)
    notifications = []

    for participant in participants:
        # Create immediate notifications for each type
        if participant.email:
            notification = system.notification_manager._create_notification(
                event, participant, NotificationType.EMAIL,
                f"🚨 URGENT: Event '{event.title}' is starting NOW!",
                datetime.now() - timedelta(seconds=1)  # 1 second ago - ready to send
            )
            notifications.append(notification)

        if participant.phone:
            notification = system.notification_manager._create_notification(
                event, participant, NotificationType.SMS,
                f"🚨 Event '{event.title}' starts NOW!",
                datetime.now() - timedelta(seconds=1)  # 1 second ago - ready to send
            )
            notifications.append(notification)

        # Always create push notification
        notification = system.notification_manager._create_notification(
            event, participant, NotificationType.PUSH,
            f"🚨 Event '{event.title}' is starting NOW!",
            datetime.now() - timedelta(seconds=1)  # 1 second ago - ready to send
        )
        notifications.append(notification)

    return notifications


def demo_event_scheduling_system():
    """Comprehensive demo of the event scheduling system"""
    print("🎯 EVENT SCHEDULING SYSTEM DEMO")
    print("=" * 50)

    # Initialize the system
    system = EventSchedulingSystem()

    try:
        # 1. Create Events
        print("\n📅 Creating Events...")
        now = datetime.now()

        # Event 1: Team Meeting
        team_meeting = system.create_event(
            title="Team Standup Meeting",
            description="Daily standup to discuss progress and blockers",
            start_time=now + timedelta(seconds=30),  # 30 seconds from now
            end_time=now + timedelta(minutes=30),   # 30 minutes duration
            creator_id="user_alice"
        )
        print(f"✅ Created event: {team_meeting.title} (ID: {team_meeting.event_id})")

        # Event 2: Project Review
        project_review = system.create_event(
            title="Q4 Project Review",
            description="Review project milestones and plan next quarter",
            start_time=now + timedelta(hours=2),    # 2 hours from now
            end_time=now + timedelta(hours=3),      # 1 hour duration
            creator_id="user_bob"
        )
        print(f"✅ Created event: {project_review.title} (ID: {project_review.event_id})")

        # 2. Add Participants
        print("\n👥 Adding Participants...")

        # Add participants to team meeting
        alice = system.add_participant(
            event_id=team_meeting.event_id,
            user_id="user_alice",
            name="Alice Johnson",
            email="alice@company.com",
            phone="+1234567890"
        )
        print(f"✅ Added participant: {alice.name}")

        bob = system.add_participant(
            event_id=team_meeting.event_id,
            user_id="user_bob",
            name="Bob Smith",
            email="bob@company.com",
            phone="+1234567891"
        )
        print(f"✅ Added participant: {bob.name}")

        charlie = system.add_participant(
            event_id=team_meeting.event_id,
            user_id="user_charlie",
            name="Charlie Brown",
            email="charlie@company.com"  # No phone for SMS testing
        )
        print(f"✅ Added participant: {charlie.name}")

        # Add participants to project review
        david = system.add_participant(
            event_id=project_review.event_id,
            user_id="user_david",
            name="David Wilson",
            email="david@company.com",
            phone="+1234567892"
        )
        print(f"✅ Added participant: {david.name}")

        # 3. Schedule Notifications
        print("\n🔔 Scheduling Notifications...")

        # Schedule notifications for team meeting (immediately for demo)
        team_notifications = _create_immediate_notifications(system, team_meeting.event_id)
        print(f"✅ Scheduled {len(team_notifications)} notifications for team meeting")

        # Schedule notifications for project review (15 minutes before)
        review_notifications = system.schedule_event_notifications(
            event_id=project_review.event_id,
            minutes_before=15
        )
        print(f"✅ Scheduled {len(review_notifications)} notifications for project review")

        # 4. View System State
        print("\n📊 System Statistics:")
        stats = system.get_system_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")

        # 5. Start Background Notification Processor
        print("\n🔄 Starting Background Notification Processor...")
        system.start_notification_processor(check_interval_seconds=2)

        # 6. Simulate Event Timing
        print("\n⏰ Waiting a moment for notification processing...")
        time.sleep(2)  # Brief pause for demo clarity

        # 7. Check and Send Pending Notifications
        print("\n📤 Processing Pending Notifications...")
        sent_notifications = system.send_pending_notifications()
        print(f"✅ Sent {len(sent_notifications)} notifications")

        # 8. View Upcoming Events
        print("\n🔍 Upcoming Events (next 24 hours):")
        upcoming = system.get_upcoming_events(1440)  # 24 hours
        for event in upcoming:
            participants = system.get_event_participants(event.event_id)
            print(f"   📅 {event.title} at {event.start_time.strftime('%H:%M')} ({len(participants)} participants)")

        # 9. View Event Notifications
        print("\n📋 Team Meeting Notifications:")
        notifications = system.get_event_notifications(team_meeting.event_id)
        for notification in notifications:
            status = "✅ SENT" if notification.is_sent else "⏳ PENDING (scheduled for past - ready to send)"
            print(f"   {notification.notification_type.value.upper()}: {status}")

        # Show why notifications were ready
        print("\n💡 Note: Demo notifications were scheduled 1 second ago, making them immediately ready to send")

        # 10. Demonstrate Error Handling
        print("\n🚫 Testing Error Handling...")

        try:
            # Try to add duplicate participant
            system.add_participant(
                event_id=team_meeting.event_id,
                user_id="user_alice",  # Already exists
                name="Alice Johnson",
                email="alice@company.com"
            )
        except ValueError as e:
            print(f"✅ Caught expected error: {e}")

        try:
            # Try to get non-existent event
            system.get_event("non-existent-id")
        except Exception:
            print("✅ Handled non-existent event gracefully")

        # 11. Cleanup Demo
        print("\n🧹 Cleaning up demo data...")
        system.stop_notification_processor()

        # Delete events (this will also clean up participants and notifications)
        system.delete_event(team_meeting.event_id)
        system.delete_event(project_review.event_id)

        final_stats = system.get_system_stats()
        print(f"✅ Cleanup complete. Final stats: {final_stats}")

        print("\n🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ensure notification processor is stopped (suppress normal warnings)
        try:
            # Only stop if it's actually running to avoid confusing output
            if (hasattr(system, '_notification_processor_thread') and
                system._notification_processor_thread and
                system._notification_processor_thread.is_alive()):
                system.stop_notification_processor()
        except:
            pass


def interactive_demo():
    """Simple interactive demo for manual testing"""
    print("🎯 INTERACTIVE EVENT SCHEDULING SYSTEM")
    print("Commands:")
    print("  create - Create a new event")
    print("  add - Add participant to event")
    print("  notify - Schedule notifications for event")
    print("  send - Send pending notifications")
    print("  list - List all events")
    print("  stats - Show system statistics")
    print("  exit - Exit demo")

    system = EventSchedulingSystem()
    system.start_notification_processor()

    try:
        while True:
            command = input("\n> ").strip().lower()

            if command == "exit":
                break
            elif command == "create":
                title = input("Event title: ")
                description = input("Description: ")
                hours_from_now = int(input("Hours from now: "))
                duration_hours = int(input("Duration (hours): "))
                creator_id = input("Creator ID: ")

                start_time = datetime.now() + timedelta(hours=hours_from_now)
                end_time = start_time + timedelta(hours=duration_hours)

                event = system.create_event(title, description, start_time, end_time, creator_id)
                print(f"Created event: {event.title} (ID: {event.event_id})")

            elif command == "add":
                event_id = input("Event ID: ")
                user_id = input("User ID: ")
                name = input("Name: ")
                email = input("Email: ")
                phone = input("Phone (optional): ") or None

                participant = system.add_participant(event_id, user_id, name, email, phone)
                print(f"Added participant: {participant.name}")

            elif command == "notify":
                event_id = input("Event ID: ")
                minutes_before = int(input("Minutes before event: ") or "60")

                notifications = system.schedule_event_notifications(event_id, minutes_before)
                print(f"Scheduled {len(notifications)} notifications")

            elif command == "send":
                sent = system.send_pending_notifications()
                print(f"Sent {len(sent)} notifications")

            elif command == "list":
                events = system.get_all_events()
                for event in events:
                    participants = system.get_event_participants(event.event_id)
                    print(f"{event.event_id}: {event.title} ({len(participants)} participants)")

            elif command == "stats":
                stats = system.get_system_stats()
                for key, value in stats.items():
                    print(f"{key}: {value}")

            else:
                print("Unknown command. Try: create, add, notify, send, list, stats, exit")

    finally:
        # Ensure notification processor is stopped (suppress normal warnings)
        try:
            # Only stop if it's actually running to avoid confusing output
            if (hasattr(system, '_notification_processor_thread') and
                system._notification_processor_thread and
                system._notification_processor_thread.is_alive()):
                system.stop_notification_processor()
        except:
            pass


if __name__ == "__main__":
    print("Choose demo mode:")
    print("1. Automated comprehensive demo")
    print("2. Interactive demo")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "2":
        interactive_demo()
    else:
        demo_event_scheduling_system()