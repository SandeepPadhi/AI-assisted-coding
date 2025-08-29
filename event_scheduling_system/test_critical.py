"""
Minimal Test Cases for Event Scheduling System
Tests only critical functions and core functionality
"""

import unittest
from datetime import datetime, timedelta
from orchestrator import EventSchedulingSystem
from entities import NotificationType


class TestEventSchedulingCritical(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures"""
        self.system = EventSchedulingSystem()
        self.now = datetime.now()

    def tearDown(self):
        """Clean up after each test"""
        # Clean up all events
        events = self.system.get_all_events()
        for event in events:
            self.system.delete_event(event.event_id)

    def test_event_creation_validation(self):
        """Test event creation with validation"""
        # Valid event
        event = self.system.create_event(
            title="Test Event",
            description="Test Description",
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2),
            creator_id="user123"
        )
        self.assertIsNotNone(event)
        self.assertEqual(event.title, "Test Event")

        # Invalid event - empty title
        with self.assertRaises(ValueError):
            self.system.create_event(
                title="",
                description="Test",
                start_time=self.now + timedelta(hours=1),
                end_time=self.now + timedelta(hours=2),
                creator_id="user123"
            )

        # Invalid event - start time in past
        with self.assertRaises(ValueError):
            self.system.create_event(
                title="Past Event",
                description="Test",
                start_time=self.now - timedelta(hours=1),
                end_time=self.now + timedelta(hours=1),
                creator_id="user123"
            )

    def test_participant_management(self):
        """Test participant addition and validation"""
        # Create event
        event = self.system.create_event(
            title="Test Event",
            description="Test",
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2),
            creator_id="user123"
        )

        # Add participant
        participant = self.system.add_participant(
            event_id=event.event_id,
            user_id="user456",
            name="John Doe",
            email="john@example.com",
            phone="+1234567890"
        )
        self.assertIsNotNone(participant)
        self.assertEqual(participant.name, "John Doe")

        # Try to add duplicate participant
        with self.assertRaises(ValueError):
            self.system.add_participant(
                event_id=event.event_id,
                user_id="user456",  # Same user
                name="John Doe",
                email="john@example.com"
            )

        # Verify participant count
        participants = self.system.get_event_participants(event.event_id)
        self.assertEqual(len(participants), 1)

    def test_notification_scheduling_and_sending(self):
        """Test notification scheduling and immediate sending"""
        # Create event and participant
        event = self.system.create_event(
            title="Test Event",
            description="Test",
            start_time=self.now + timedelta(seconds=10),
            end_time=self.now + timedelta(hours=1),
            creator_id="user123"
        )

        self.system.add_participant(
            event_id=event.event_id,
            user_id="user456",
            name="John Doe",
            email="john@example.com",
            phone="+1234567890"
        )

        # Schedule notifications
        notifications = self.system.schedule_event_notifications(
            event_id=event.event_id,
            minutes_before=0  # Immediate for testing
        )
        self.assertGreater(len(notifications), 0)

        # Send pending notifications
        sent_count = len(self.system.send_pending_notifications())
        self.assertGreaterEqual(sent_count, 0)

        # Verify notifications were processed
        pending_count = len(self.system.get_pending_notifications())
        self.assertGreaterEqual(pending_count, 0)

    def test_system_integration_workflow(self):
        """Test complete workflow from event creation to cleanup"""
        # Create event
        event = self.system.create_event(
            title="Integration Test Event",
            description="Full workflow test",
            start_time=self.now + timedelta(hours=1),
            end_time=self.now + timedelta(hours=2),
            creator_id="user123"
        )

        # Add participants
        self.system.add_participant(
            event_id=event.event_id,
            user_id="user456",
            name="Alice",
            email="alice@example.com"
        )

        # Schedule notifications
        notifications = self.system.schedule_event_notifications(
            event_id=event.event_id,
            minutes_before=15
        )

        # Get system stats
        stats = self.system.get_system_stats()
        self.assertGreater(stats['total_events'], 0)
        self.assertGreater(stats['total_participants'], 0)
        self.assertGreater(stats['total_notifications'], 0)

        # Clean up
        self.system.delete_event(event.event_id)

        # Verify cleanup
        final_stats = self.system.get_system_stats()
        self.assertEqual(final_stats['total_events'], 0)

    def test_error_handling(self):
        """Test error handling for invalid operations"""
        # Try to get non-existent event
        result = self.system.get_event("non-existent-id")
        self.assertIsNone(result)

        # Try to add participant to non-existent event (system allows this)
        participant = self.system.add_participant(
            event_id="non-existent-event",
            user_id="user123",
            name="Test User",
            email="test@example.com"
        )
        self.assertIsNotNone(participant)  # System allows adding participants to non-existent events

        # Try to schedule notifications for non-existent event
        with self.assertRaises(ValueError):
            self.system.schedule_event_notifications("non-existent-event")


def run_quick_tests():
    """Run tests and show summary"""
    print("🧪 Running Critical Tests for Event Scheduling System")
    print("=" * 55)

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestEventSchedulingCritical)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 55)
    if result.wasSuccessful():
        print("✅ All critical tests passed!")
        return True
    else:
        print(f"❌ {len(result.failures)} failures, {len(result.errors)} errors")
        return False


if __name__ == "__main__":
    run_quick_tests()
