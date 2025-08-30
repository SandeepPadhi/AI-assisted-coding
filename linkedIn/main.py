"""
LinkedIn System Demo

This file contains the demonstration of the LinkedIn system functionality.
The system is now modularized into separate files:
- entities.py: Core business objects
- repositories.py: Data storage abstractions
- managers.py: Business logic managers
- services.py: External service integrations
- orchestrator.py: Main system coordination
"""

from orchestrator import LinkedInSystem


def demo() -> None:
    """Demonstrate the LinkedIn system functionality with all phases."""
    print("=== LinkedIn System - Modular Architecture Demo ===\n")

    # Initialize the system
    linkedin = LinkedInSystem()

    try:
        # Phase 1: User Profile Management
        print("="*50)
        print("PHASE 1: USER PROFILE MANAGEMENT")
        print("="*50 + "\n")

        # Create users with profiles
        print("Creating users...")

        user1, profile1 = linkedin.create_user_with_profile(
            "user_001",
            "john.doe@email.com",
            "John",
            "Doe",
            "Software Engineer at Tech Corp",
            "Passionate software engineer with 5 years of experience",
            "San Francisco, CA"
        )

        user2, profile2 = linkedin.create_user_with_profile(
            "user_002",
            "jane.smith@email.com",
            "Jane",
            "Smith",
            "Product Manager at Startup Inc",
            "Experienced product manager focused on user experience",
            "New York, NY"
        )

        print("✓ Users created successfully!\n")

        # Display user information
        print("User Profiles:")
        for i, (user, profile) in enumerate([(user1, profile1), (user2, profile2)], 1):
            print(f"User {i}:")
            print(f"  ID: {user.user_id}")
            print(f"  Name: {user.get_full_name()}")
            print(f"  Email: {user.email}")
            print(f"  Headline: {profile.headline}")
            print(f"  Summary: {profile.summary}")
            print(f"  Location: {profile.location}")
            print()

        # Test profile updates
        print("Updating Jane's profile...")
        updated_profile = linkedin.update_user_profile(
            "user_002",
            headline="Senior Product Manager at Startup Inc",
            summary="Experienced product manager focused on user experience and growth"
        )

        if updated_profile:
            print("✓ Profile updated successfully!")
            print(f"  New Headline: {updated_profile.headline}")
            print(f"  New Summary: {updated_profile.summary}")
            print()

        # Phase 2: Messaging System
        print("="*50)
        print("PHASE 2: MESSAGING SYSTEM")
        print("="*50 + "\n")

        # Test posting messages
        print("Posting messages...")

        message1 = linkedin.post_message(
            "msg_001",
            "user_001",
            "Excited to share my journey as a software engineer! #TechLife"
        )

        message2 = linkedin.post_message(
            "msg_002",
            "user_002",
            "Looking forward to connecting with fellow product managers in the industry!"
        )

        message3 = linkedin.post_message(
            "msg_003",
            "user_001",
            "Just shipped a major feature update. Collaboration and teamwork made it possible!"
        )

        print("✓ Messages posted successfully!\n")

        # Display all messages
        print("All Messages (Newest First):")
        all_messages = linkedin.get_all_messages()
        for i, msg in enumerate(all_messages, 1):
            user, profile = linkedin.get_user_profile(msg.author_id)
            if user and profile:
                print(f"Message {i}:")
                print(f"  Author: {user.get_full_name()}")
                print(f"  Headline: {profile.headline}")
                print(f"  Content: {msg.content}")
                print(f"  Posted: {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()

        # Phase 3: Connection System
        print("="*50)
        print("PHASE 3: CONNECTION SYSTEM")
        print("="*50 + "\n")

        # Create additional users for connection testing
        print("Creating additional users for connection testing...")

        user3, profile3 = linkedin.create_user_with_profile(
            "user_003",
            "alice.dev@email.com",
            "Alice",
            "Developer",
            "Full Stack Developer at StartupXYZ",
            "Passionate developer with expertise in React and Node.js",
            "Austin, TX"
        )

        user4, profile4 = linkedin.create_user_with_profile(
            "user_004",
            "bob.manager@email.com",
            "Bob",
            "Manager",
            "Engineering Manager at BigTech",
            "Experienced manager focused on team growth and product delivery",
            "Seattle, WA"
        )

        print("✓ Additional users created!\n")

        # Test sending connection requests
        print("Sending connection requests...")

        connection1 = linkedin.send_connection_request("conn_001", "user_001", "user_002")
        connection2 = linkedin.send_connection_request("conn_002", "user_003", "user_001")
        connection3 = linkedin.send_connection_request("conn_003", "user_004", "user_001")
        connection4 = linkedin.send_connection_request("conn_004", "user_002", "user_003")

        print("✓ Connection requests sent successfully!")
        print("✓ Notifications sent via email, SMS, and push notifications!\n")

        # Display pending requests for each user
        print("Pending Connection Requests:")
        for user_id, user in [("user_001", user1), ("user_002", user2), ("user_003", user3), ("user_004", user4)]:
            received_requests = linkedin.get_received_requests(user_id)
            sent_requests = linkedin.get_sent_requests(user_id)

            if received_requests or sent_requests:
                print(f"\n{user.get_full_name()}:")
                if received_requests:
                    print(f"  Received requests: {len(received_requests)}")
                    for req in received_requests:
                        sender_user, _ = linkedin.get_user_profile(req.sender_id)
                        if sender_user:
                            print(f"    - From: {sender_user.get_full_name()}")
                if sent_requests:
                    print(f"  Sent requests: {len(sent_requests)}")
                    for req in sent_requests:
                        receiver_user, _ = linkedin.get_user_profile(req.receiver_id)
                        if receiver_user:
                            print(f"    - To: {receiver_user.get_full_name()}")
        print()

        # Test accepting connection requests
        print("Accepting connection requests...")

        # John accepts Alice's request
        accepted_conn1 = linkedin.accept_connection_request("conn_002", "user_001")
        if accepted_conn1:
            print("✓ John accepted Alice's connection request!")

        # Jane accepts John's request
        accepted_conn2 = linkedin.accept_connection_request("conn_001", "user_002")
        if accepted_conn2:
            print("✓ Jane accepted John's connection request!")

        print()

        # Test rejecting connection request
        print("Rejecting connection request...")
        rejected_conn = linkedin.reject_connection_request("conn_003", "user_001")
        if rejected_conn:
            print("✓ John rejected Bob's connection request!")
        print()

        # Display accepted connections
        print("Accepted Connections:")
        for user_id, user in [("user_001", user1), ("user_002", user2), ("user_003", user3)]:
            accepted_connections = linkedin.get_accepted_connections(user_id)
            if accepted_connections:
                print(f"\n{user.get_full_name()} is connected to:")
                for conn in accepted_connections:
                    other_user_id = conn.get_other_user(user_id)
                    if other_user_id:
                        other_user, _ = linkedin.get_user_profile(other_user_id)
                        if other_user:
                            print(f"  - {other_user.get_full_name()}")
        print()

        # Phase 4: News Feed System
        print("="*50)
        print("PHASE 4: NEWS FEED SYSTEM")
        print("="*50 + "\n")

        # Generate news feeds for users
        print("Generating news feeds for all users...")

        # Generate feeds for John and Jane (who are connected)
        linkedin.refresh_user_feed("user_001")  # John's feed
        linkedin.refresh_user_feed("user_002")  # Jane's feed

        print("✓ News feeds generated!\n")

        # Display John's news feed
        print("John's News Feed:")
        john_feed = linkedin.get_user_feed("user_001")
        if john_feed:
            for i, feed_item in enumerate(john_feed, 1):
                print(f"{i}. {feed_item.get_display_content()}")
                print(f"   Posted: {feed_item.message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("  (No items in feed)")
        print()

        # Display Jane's news feed
        print("Jane's News Feed:")
        jane_feed = linkedin.get_user_feed("user_002")
        if jane_feed:
            for i, feed_item in enumerate(jane_feed, 1):
                print(f"{i}. {feed_item.get_display_content()}")
                print(f"   Posted: {feed_item.message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        else:
            print("  (No items in feed)")
        print()

        # Post a new message from Jane and refresh feeds
        print("Jane posts a new message...")
        new_message = linkedin.post_message(
            "msg_006",
            "user_002",
            "Just launched a new product feature! The team collaboration was incredible. #ProductLaunch"
        )

        # Refresh feeds to include the new message
        linkedin.refresh_user_feed("user_001")  # John's feed should now include Jane's new message

        print("✓ New message posted and feeds refreshed!\n")

        # Show updated John feed
        print("John's Updated News Feed (should include Jane's new message):")
        updated_john_feed = linkedin.get_user_feed("user_001")
        if updated_john_feed:
            for i, feed_item in enumerate(updated_john_feed, 1):
                print(f"{i}. {feed_item.get_display_content()}")
                print(f"   Posted: {feed_item.message.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                print()
        print()

        # Show system statistics
        print("="*50)
        print("SYSTEM STATISTICS")
        print("="*50 + "\n")

        stats = linkedin.get_system_stats()
        print(f"Total Users: {stats['total_users']}")
        print(f"Total Messages: {stats['total_messages']}")
        print(f"Total Connections: {stats['total_connections']}")
        print(f"Total Feeds: {stats['total_feeds']}")
        print(f"Emails Sent: {stats['notifications']['emails_sent']}")
        print(f"SMS Sent: {stats['notifications']['sms_sent']}")
        print(f"Push Notifications Sent: {stats['notifications']['push_notifications_sent']}")
        print()

        print("\n=== MODULAR LINKEDIN SYSTEM COMPLETE! ===")
        print("✅ All phases successfully implemented with modular architecture:")
        print("• Phase 1: User Profile Management ✅")
        print("• Phase 2: Messaging System ✅")
        print("• Phase 3: Connection System with Notifications ✅")
        print("• Phase 4: News Feed System ✅")
        print("\n🎉 SYSTEM ARCHITECTURE:")
        print("• Entities: Core business objects with invariants ✅")
        print("• Repositories: Abstract storage with in-memory implementations ✅")
        print("• Managers: Business logic and operations ✅")
        print("• Services: External integrations (email, SMS, push) ✅")
        print("• Orchestrator: System coordination and high-level operations ✅")

    except Exception as e:
        print(f"Error during demo: {e}")


if __name__ == "__main__":
    demo()