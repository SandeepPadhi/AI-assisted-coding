"""
Comprehensive unit tests for the Chat Application
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from uuid import uuid4, UUID
from typing import List, Optional

# Import all classes from main module
from main import (
    # Entities
    User, Message, Group, GroupMember, GroupMessage,
    MessageStatus, GroupMemberRole,

    # Repositories
    AbstractUserRepository, AbstractMessageRepository, AbstractGroupRepository,
    AbstractGroupMemberRepository, AbstractGroupMessageRepository,
    InMemoryUserRepository, InMemoryMessageRepository, InMemoryGroupRepository,
    InMemoryGroupMemberRepository, InMemoryGroupMessageRepository,

    # Managers
    UserManager, MessageManager, GroupManager,

    # Orchestrator
    ChatApplication
)


class TestEntities(unittest.TestCase):
    """Test entity creation, validation, and business logic"""

    def test_user_creation(self):
        """Test user creation with valid username"""
        user = User("testuser")
        self.assertEqual(user.username, "testuser")
        self.assertIsInstance(user.user_id, UUID)
        self.assertIsInstance(user.created_at, datetime)

    def test_user_validation(self):
        """Test user validation for invalid inputs"""
        # Empty username
        with self.assertRaises(ValueError):
            User("")

        # Username too short
        with self.assertRaises(ValueError):
            User("ab")

        # Username too long
        with self.assertRaises(ValueError):
            User("a" * 51)

        # Non-string username
        with self.assertRaises(ValueError):
            User(123)

    def test_message_creation(self):
        """Test message creation and validation"""
        sender_id = uuid4()
        receiver_id = uuid4()
        message = Message(sender_id, receiver_id, "Hello World!")

        self.assertEqual(message.sender_id, sender_id)
        self.assertEqual(message.receiver_id, receiver_id)
        self.assertEqual(message.content, "Hello World!")
        self.assertEqual(message.status, MessageStatus.SENT)
        self.assertIsInstance(message.message_id, UUID)

    def test_message_validation(self):
        """Test message content validation"""
        sender_id = uuid4()
        receiver_id = uuid4()

        # Empty content
        with self.assertRaises(ValueError):
            Message(sender_id, receiver_id, "")

        # Content too long
        with self.assertRaises(ValueError):
            Message(sender_id, receiver_id, "a" * 1001)

        # Non-string content
        with self.assertRaises(ValueError):
            Message(sender_id, receiver_id, 123)

    def test_message_edit(self):
        """Test message editing functionality"""
        sender_id = uuid4()
        receiver_id = uuid4()
        message = Message(sender_id, receiver_id, "Original message")

        original_updated_at = message.updated_at
        message.edit_content("Edited message")

        self.assertEqual(message.content, "Edited message")
        self.assertEqual(message.status, MessageStatus.EDITED)
        # Check that updated_at is either greater than or equal to original (due to timing resolution)
        self.assertGreaterEqual(message.updated_at, original_updated_at)

    def test_message_delete(self):
        """Test message deletion functionality"""
        sender_id = uuid4()
        receiver_id = uuid4()
        message = Message(sender_id, receiver_id, "Message to delete")

        message.delete()

        self.assertEqual(message.content, "")
        self.assertEqual(message.status, MessageStatus.DELETED)

    def test_group_creation(self):
        """Test group creation and validation"""
        creator_id = uuid4()
        group = Group("Test Group", creator_id)

        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.creator_id, creator_id)
        self.assertIsInstance(group.group_id, UUID)

    def test_group_validation(self):
        """Test group name validation"""
        creator_id = uuid4()

        # Empty name
        with self.assertRaises(ValueError):
            Group("", creator_id)

        # Name too short
        with self.assertRaises(ValueError):
            Group("ab", creator_id)

        # Name too long
        with self.assertRaises(ValueError):
            Group("a" * 51, creator_id)

    def test_group_member_creation(self):
        """Test group member creation"""
        group_id = uuid4()
        user_id = uuid4()
        member = GroupMember(group_id, user_id, GroupMemberRole.MEMBER)

        self.assertEqual(member.group_id, group_id)
        self.assertEqual(member.user_id, user_id)
        self.assertEqual(member.role, GroupMemberRole.MEMBER)
        self.assertIsInstance(member.joined_at, datetime)

    def test_group_message_creation(self):
        """Test group message creation"""
        group_id = uuid4()
        sender_id = uuid4()
        message = GroupMessage(group_id, sender_id, "Group message")

        self.assertEqual(message.group_id, group_id)
        self.assertEqual(message.sender_id, sender_id)
        self.assertEqual(message.content, "Group message")
        self.assertEqual(message.status, MessageStatus.SENT)

    def test_group_message_operations(self):
        """Test group message edit and delete"""
        group_id = uuid4()
        sender_id = uuid4()
        message = GroupMessage(group_id, sender_id, "Original group message")

        # Test edit
        message.edit_content("Edited group message")
        self.assertEqual(message.content, "Edited group message")
        self.assertEqual(message.status, MessageStatus.EDITED)

        # Test delete
        message.delete()
        self.assertEqual(message.content, "")
        self.assertEqual(message.status, MessageStatus.DELETED)


class TestInMemoryUserRepository(unittest.TestCase):
    """Test InMemoryUserRepository functionality"""

    def setUp(self):
        self.repo = InMemoryUserRepository()

    def test_create_user(self):
        """Test user creation in repository"""
        user = self.repo.create_user("testuser")
        self.assertEqual(user.username, "testuser")
        self.assertIn(user.user_id, self.repo._users)

    def test_create_duplicate_username(self):
        """Test creating user with duplicate username"""
        self.repo.create_user("testuser")
        with self.assertRaises(ValueError):
            self.repo.create_user("testuser")

    def test_get_user_by_id(self):
        """Test retrieving user by ID"""
        user = self.repo.create_user("testuser")
        retrieved = self.repo.get_user_by_id(user.user_id)
        self.assertEqual(retrieved, user)

        # Test non-existent user
        self.assertIsNone(self.repo.get_user_by_id(uuid4()))

    def test_get_user_by_username(self):
        """Test retrieving user by username"""
        user = self.repo.create_user("testuser")
        retrieved = self.repo.get_user_by_username("testuser")
        self.assertEqual(retrieved, user)

        # Test non-existent username
        self.assertIsNone(self.repo.get_user_by_username("nonexistent"))

    def test_get_all_users(self):
        """Test retrieving all users"""
        user1 = self.repo.create_user("user1")
        user2 = self.repo.create_user("user2")

        all_users = self.repo.get_all_users()
        self.assertEqual(len(all_users), 2)
        self.assertIn(user1, all_users)
        self.assertIn(user2, all_users)


class TestInMemoryMessageRepository(unittest.TestCase):
    """Test InMemoryMessageRepository functionality"""

    def setUp(self):
        self.repo = InMemoryMessageRepository()

    def test_create_message(self):
        """Test message creation in repository"""
        sender_id = uuid4()
        receiver_id = uuid4()
        message = self.repo.create_message(sender_id, receiver_id, "Hello")

        self.assertEqual(message.sender_id, sender_id)
        self.assertEqual(message.receiver_id, receiver_id)
        self.assertEqual(message.content, "Hello")
        self.assertIn(message.message_id, self.repo._messages)

    def test_get_message_by_id(self):
        """Test retrieving message by ID"""
        sender_id = uuid4()
        receiver_id = uuid4()
        message = self.repo.create_message(sender_id, receiver_id, "Hello")

        retrieved = self.repo.get_message_by_id(message.message_id)
        self.assertEqual(retrieved, message)

        # Test non-existent message
        self.assertIsNone(self.repo.get_message_by_id(uuid4()))

    def test_get_messages_between_users(self):
        """Test retrieving message history between users"""
        user1_id = uuid4()
        user2_id = uuid4()

        msg1 = self.repo.create_message(user1_id, user2_id, "Hello")
        msg2 = self.repo.create_message(user2_id, user1_id, "Hi there")
        msg3 = self.repo.create_message(user1_id, uuid4(), "Other conversation")

        messages = self.repo.get_messages_between_users(user1_id, user2_id)
        self.assertEqual(len(messages), 2)
        self.assertIn(msg1, messages)
        self.assertIn(msg2, messages)
        self.assertNotIn(msg3, messages)

        # Test chronological ordering
        self.assertLess(messages[0].created_at, messages[1].created_at)

    def test_update_message(self):
        """Test message update"""
        sender_id = uuid4()
        receiver_id = uuid4()
        message = self.repo.create_message(sender_id, receiver_id, "Original")

        message.content = "Updated"
        self.repo.update_message(message)

        retrieved = self.repo.get_message_by_id(message.message_id)
        self.assertEqual(retrieved.content, "Updated")

    def test_update_nonexistent_message(self):
        """Test updating non-existent message"""
        message = Message(uuid4(), uuid4(), "Test")
        with self.assertRaises(ValueError):
            self.repo.update_message(message)

    def test_delete_message(self):
        """Test message deletion"""
        sender_id = uuid4()
        receiver_id = uuid4()
        message = self.repo.create_message(sender_id, receiver_id, "To delete")

        self.repo.delete_message(message.message_id)

        # Message should still exist but be marked as deleted
        retrieved = self.repo.get_message_by_id(message.message_id)
        self.assertEqual(retrieved.content, "")
        self.assertEqual(retrieved.status, MessageStatus.DELETED)


class TestInMemoryGroupRepository(unittest.TestCase):
    """Test InMemoryGroupRepository functionality"""

    def setUp(self):
        self.repo = InMemoryGroupRepository()

    def test_create_group(self):
        """Test group creation"""
        creator_id = uuid4()
        group = self.repo.create_group("Test Group", creator_id)

        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.creator_id, creator_id)
        self.assertIn(group.group_id, self.repo._groups)

    def test_get_group_by_id(self):
        """Test retrieving group by ID"""
        creator_id = uuid4()
        group = self.repo.create_group("Test Group", creator_id)

        retrieved = self.repo.get_group_by_id(group.group_id)
        self.assertEqual(retrieved, group)

        # Test non-existent group
        self.assertIsNone(self.repo.get_group_by_id(uuid4()))

    def test_get_groups_by_user(self):
        """Test retrieving groups by user"""
        user1_id = uuid4()
        user2_id = uuid4()

        group1 = self.repo.create_group("Group 1", user1_id)
        group2 = self.repo.create_group("Group 2", user1_id)
        group3 = self.repo.create_group("Group 3", user2_id)

        user1_groups = self.repo.get_groups_by_user(user1_id)
        self.assertEqual(len(user1_groups), 2)
        self.assertIn(group1, user1_groups)
        self.assertIn(group2, user1_groups)
        self.assertNotIn(group3, user1_groups)

    def test_delete_group(self):
        """Test group deletion"""
        creator_id = uuid4()
        group = self.repo.create_group("Test Group", creator_id)

        self.assertIn(group.group_id, self.repo._groups)
        self.repo.delete_group(group.group_id)
        self.assertNotIn(group.group_id, self.repo._groups)


class TestInMemoryGroupMemberRepository(unittest.TestCase):
    """Test InMemoryGroupMemberRepository functionality"""

    def setUp(self):
        self.repo = InMemoryGroupMemberRepository()

    def test_add_member(self):
        """Test adding a member to group"""
        group_id = uuid4()
        user_id = uuid4()
        member = self.repo.add_member(group_id, user_id, GroupMemberRole.MEMBER)

        self.assertEqual(member.group_id, group_id)
        self.assertEqual(member.user_id, user_id)
        self.assertEqual(member.role, GroupMemberRole.MEMBER)
        self.assertIn(user_id, self.repo._group_members[group_id])

    def test_remove_member(self):
        """Test removing a member from group"""
        group_id = uuid4()
        user_id = uuid4()
        self.repo.add_member(group_id, user_id, GroupMemberRole.MEMBER)

        self.assertIn(user_id, self.repo._group_members[group_id])
        self.repo.remove_member(group_id, user_id)
        self.assertNotIn(user_id, self.repo._group_members[group_id])

    def test_get_group_members(self):
        """Test retrieving all members of a group"""
        group_id = uuid4()
        user1_id = uuid4()
        user2_id = uuid4()

        member1 = self.repo.add_member(group_id, user1_id, GroupMemberRole.ADMIN)
        member2 = self.repo.add_member(group_id, user2_id, GroupMemberRole.MEMBER)

        members = self.repo.get_group_members(group_id)
        self.assertEqual(len(members), 2)
        self.assertIn(member1, members)
        self.assertIn(member2, members)

    def test_get_member_role(self):
        """Test retrieving a member's role"""
        group_id = uuid4()
        user_id = uuid4()
        self.repo.add_member(group_id, user_id, GroupMemberRole.ADMIN)

        role = self.repo.get_member_role(group_id, user_id)
        self.assertEqual(role, GroupMemberRole.ADMIN)

        # Test non-existent member
        self.assertIsNone(self.repo.get_member_role(group_id, uuid4()))

    def test_is_user_in_group(self):
        """Test checking if user is in group"""
        group_id = uuid4()
        user_id = uuid4()

        self.assertFalse(self.repo.is_user_in_group(group_id, user_id))

        self.repo.add_member(group_id, user_id, GroupMemberRole.MEMBER)
        self.assertTrue(self.repo.is_user_in_group(group_id, user_id))


class TestInMemoryGroupMessageRepository(unittest.TestCase):
    """Test InMemoryGroupMessageRepository functionality"""

    def setUp(self):
        self.repo = InMemoryGroupMessageRepository()

    def test_create_group_message(self):
        """Test creating a group message"""
        group_id = uuid4()
        sender_id = uuid4()
        message = self.repo.create_group_message(group_id, sender_id, "Group hello")

        self.assertEqual(message.group_id, group_id)
        self.assertEqual(message.sender_id, sender_id)
        self.assertEqual(message.content, "Group hello")
        self.assertIn(message.message_id, self.repo._messages)

    def test_get_group_message_by_id(self):
        """Test retrieving group message by ID"""
        group_id = uuid4()
        sender_id = uuid4()
        message = self.repo.create_group_message(group_id, sender_id, "Test")

        retrieved = self.repo.get_group_message_by_id(message.message_id)
        self.assertEqual(retrieved, message)

        # Test non-existent message
        self.assertIsNone(self.repo.get_group_message_by_id(uuid4()))

    def test_get_group_messages(self):
        """Test retrieving all messages in a group"""
        group1_id = uuid4()
        group2_id = uuid4()
        sender_id = uuid4()

        msg1 = self.repo.create_group_message(group1_id, sender_id, "Message 1")
        msg2 = self.repo.create_group_message(group1_id, sender_id, "Message 2")
        msg3 = self.repo.create_group_message(group2_id, sender_id, "Other group")

        group1_messages = self.repo.get_group_messages(group1_id)
        self.assertEqual(len(group1_messages), 2)
        self.assertIn(msg1, group1_messages)
        self.assertIn(msg2, group1_messages)
        self.assertNotIn(msg3, group1_messages)

        # Test chronological ordering
        self.assertLess(group1_messages[0].created_at, group1_messages[1].created_at)

    def test_update_group_message(self):
        """Test updating a group message"""
        group_id = uuid4()
        sender_id = uuid4()
        message = self.repo.create_group_message(group_id, sender_id, "Original")

        message.content = "Updated"
        self.repo.update_group_message(message)

        retrieved = self.repo.get_group_message_by_id(message.message_id)
        self.assertEqual(retrieved.content, "Updated")

    def test_update_nonexistent_group_message(self):
        """Test updating non-existent group message"""
        message = GroupMessage(uuid4(), uuid4(), "Test")
        with self.assertRaises(ValueError):
            self.repo.update_group_message(message)

    def test_delete_group_message(self):
        """Test deleting a group message"""
        group_id = uuid4()
        sender_id = uuid4()
        message = self.repo.create_group_message(group_id, sender_id, "To delete")

        self.repo.delete_group_message(message.message_id)

        retrieved = self.repo.get_group_message_by_id(message.message_id)
        self.assertEqual(retrieved.content, "")
        self.assertEqual(retrieved.status, MessageStatus.DELETED)


class TestUserManager(unittest.TestCase):
    """Test UserManager functionality"""

    def setUp(self):
        self.repo = InMemoryUserRepository()
        self.manager = UserManager(self.repo)

    def test_create_user(self):
        """Test user creation through manager"""
        user = self.manager.create_user("testuser")
        self.assertEqual(user.username, "testuser")

    def test_get_user_by_id(self):
        """Test retrieving user by ID through manager"""
        user = self.manager.create_user("testuser")
        retrieved = self.manager.get_user_by_id(user.user_id)
        self.assertEqual(retrieved, user)

    def test_get_user_by_username(self):
        """Test retrieving user by username through manager"""
        user = self.manager.create_user("testuser")
        retrieved = self.manager.get_user_by_username("testuser")
        self.assertEqual(retrieved, user)

    def test_get_all_users(self):
        """Test retrieving all users through manager"""
        user1 = self.manager.create_user("user1")
        user2 = self.manager.create_user("user2")

        all_users = self.manager.get_all_users()
        self.assertEqual(len(all_users), 2)
        self.assertIn(user1, all_users)
        self.assertIn(user2, all_users)


class TestMessageManager(unittest.TestCase):
    """Test MessageManager functionality"""

    def setUp(self):
        self.user_repo = InMemoryUserRepository()
        self.message_repo = InMemoryMessageRepository()
        self.manager = MessageManager(self.message_repo, self.user_repo)

        # Create test users
        self.sender = self.user_repo.create_user("sender")
        self.receiver = self.user_repo.create_user("receiver")

    def test_send_message_success(self):
        """Test successful message sending"""
        message = self.manager.send_message(self.sender.user_id, self.receiver.user_id, "Hello")
        self.assertEqual(message.sender_id, self.sender.user_id)
        self.assertEqual(message.receiver_id, self.receiver.user_id)
        self.assertEqual(message.content, "Hello")

    def test_send_message_sender_not_found(self):
        """Test sending message with non-existent sender"""
        with self.assertRaises(ValueError) as context:
            self.manager.send_message(uuid4(), self.receiver.user_id, "Hello")
        self.assertIn("Sender not found", str(context.exception))

    def test_send_message_receiver_not_found(self):
        """Test sending message with non-existent receiver"""
        with self.assertRaises(ValueError) as context:
            self.manager.send_message(self.sender.user_id, uuid4(), "Hello")
        self.assertIn("Receiver not found", str(context.exception))

    def test_get_message_history(self):
        """Test retrieving message history"""
        msg1 = self.manager.send_message(self.sender.user_id, self.receiver.user_id, "Hello")
        msg2 = self.manager.send_message(self.receiver.user_id, self.sender.user_id, "Hi")

        history = self.manager.get_message_history(self.sender.user_id, self.receiver.user_id)
        self.assertEqual(len(history), 2)
        self.assertIn(msg1, history)
        self.assertIn(msg2, history)

    def test_get_message_history_user_not_found(self):
        """Test getting message history with non-existent user"""
        with self.assertRaises(ValueError) as context:
            self.manager.get_message_history(uuid4(), self.receiver.user_id)
        self.assertIn("User1 not found", str(context.exception))

    def test_edit_message_success(self):
        """Test successful message editing"""
        message = self.manager.send_message(self.sender.user_id, self.receiver.user_id, "Original")
        self.manager.edit_message(message.message_id, "Edited", self.sender.user_id)

        # Verify message was edited
        retrieved = self.message_repo.get_message_by_id(message.message_id)
        self.assertEqual(retrieved.content, "Edited")
        self.assertEqual(retrieved.status, MessageStatus.EDITED)

    def test_edit_message_not_found(self):
        """Test editing non-existent message"""
        with self.assertRaises(ValueError) as context:
            self.manager.edit_message(uuid4(), "Edited", self.sender.user_id)
        self.assertIn("Message not found", str(context.exception))

    def test_edit_message_wrong_sender(self):
        """Test editing message by wrong sender"""
        message = self.manager.send_message(self.sender.user_id, self.receiver.user_id, "Original")
        with self.assertRaises(ValueError) as context:
            self.manager.edit_message(message.message_id, "Edited", self.receiver.user_id)
        self.assertIn("Only the sender can edit", str(context.exception))

    def test_delete_message_success(self):
        """Test successful message deletion"""
        message = self.manager.send_message(self.sender.user_id, self.receiver.user_id, "To delete")
        self.manager.delete_message(message.message_id, self.sender.user_id)

        retrieved = self.message_repo.get_message_by_id(message.message_id)
        self.assertEqual(retrieved.status, MessageStatus.DELETED)

    def test_delete_message_wrong_sender(self):
        """Test deleting message by wrong sender"""
        message = self.manager.send_message(self.sender.user_id, self.receiver.user_id, "To delete")
        with self.assertRaises(ValueError) as context:
            self.manager.delete_message(message.message_id, self.receiver.user_id)
        self.assertIn("Only the sender can delete", str(context.exception))


class TestGroupManager(unittest.TestCase):
    """Test GroupManager functionality"""

    def setUp(self):
        self.user_repo = InMemoryUserRepository()
        self.group_repo = InMemoryGroupRepository()
        self.group_member_repo = InMemoryGroupMemberRepository()
        self.group_message_repo = InMemoryGroupMessageRepository()

        self.manager = GroupManager(
            self.group_repo,
            self.group_member_repo,
            self.group_message_repo,
            self.user_repo
        )

        # Create test users
        self.creator = self.user_repo.create_user("creator")
        self.user1 = self.user_repo.create_user("user1")
        self.user2 = self.user_repo.create_user("user2")

    def test_create_group_success(self):
        """Test successful group creation"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.assertEqual(group.name, "Test Group")
        self.assertEqual(group.creator_id, self.creator.user_id)

        # Verify creator is added as admin
        role = self.group_member_repo.get_member_role(group.group_id, self.creator.user_id)
        self.assertEqual(role, GroupMemberRole.ADMIN)

    def test_create_group_creator_not_found(self):
        """Test creating group with non-existent creator"""
        with self.assertRaises(ValueError) as context:
            self.manager.create_group("Test Group", uuid4())
        self.assertIn("Creator not found", str(context.exception))

    def test_add_member_success(self):
        """Test successfully adding a member to group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)

        self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)

        # Verify user was added
        self.assertTrue(self.group_member_repo.is_user_in_group(group.group_id, self.user1.user_id))
        role = self.group_member_repo.get_member_role(group.group_id, self.user1.user_id)
        self.assertEqual(role, GroupMemberRole.MEMBER)

    def test_add_member_group_not_found(self):
        """Test adding member to non-existent group"""
        with self.assertRaises(ValueError) as context:
            self.manager.add_member(uuid4(), self.user1.user_id, self.creator.user_id)
        self.assertIn("Group not found", str(context.exception))

    def test_add_member_user_not_found(self):
        """Test adding non-existent user to group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.add_member(group.group_id, uuid4(), self.creator.user_id)
        self.assertIn("User not found", str(context.exception))

    def test_add_member_not_admin(self):
        """Test adding member by non-admin"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.add_member(group.group_id, self.user1.user_id, self.user2.user_id)
        self.assertIn("Only admins can add members", str(context.exception))

    def test_add_member_already_in_group(self):
        """Test adding user who is already in group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)

        with self.assertRaises(ValueError) as context:
            self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)
        self.assertIn("User is already in the group", str(context.exception))

    def test_remove_member_success(self):
        """Test successfully removing a member from group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)

        self.manager.remove_member(group.group_id, self.user1.user_id, self.creator.user_id)

        # Verify user was removed
        self.assertFalse(self.group_member_repo.is_user_in_group(group.group_id, self.user1.user_id))

    def test_remove_member_not_admin(self):
        """Test removing member by non-admin"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.remove_member(group.group_id, self.creator.user_id, self.user1.user_id)
        self.assertIn("Only admins can remove members", str(context.exception))

    def test_remove_member_not_in_group(self):
        """Test removing user who is not in group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.remove_member(group.group_id, self.user1.user_id, self.creator.user_id)
        self.assertIn("User is not in the group", str(context.exception))

    def test_remove_last_admin(self):
        """Test removing the last admin from group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.remove_member(group.group_id, self.creator.user_id, self.creator.user_id)
        self.assertIn("Cannot remove the last admin", str(context.exception))

    def test_leave_group_success(self):
        """Test successfully leaving a group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)

        self.manager.leave_group(group.group_id, self.user1.user_id)

        # Verify user left
        self.assertFalse(self.group_member_repo.is_user_in_group(group.group_id, self.user1.user_id))

    def test_leave_group_not_in_group(self):
        """Test leaving a group user is not in"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.leave_group(group.group_id, self.user1.user_id)
        self.assertIn("User is not in the group", str(context.exception))

    def test_leave_last_admin(self):
        """Test leaving as the last admin"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.leave_group(group.group_id, self.creator.user_id)
        self.assertIn("Cannot leave as the last admin", str(context.exception))

    def test_delete_group_success(self):
        """Test successfully deleting a group"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.assertIn(group.group_id, self.group_repo._groups)

        self.manager.delete_group(group.group_id, self.creator.user_id)
        self.assertNotIn(group.group_id, self.group_repo._groups)

    def test_delete_group_not_admin(self):
        """Test deleting group by non-admin"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.delete_group(group.group_id, self.user1.user_id)
        self.assertIn("Only admins can delete the group", str(context.exception))

    def test_send_group_message_success(self):
        """Test successfully sending a group message"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)

        message = self.manager.send_group_message(group.group_id, self.user1.user_id, "Hello group")

        self.assertEqual(message.group_id, group.group_id)
        self.assertEqual(message.sender_id, self.user1.user_id)
        self.assertEqual(message.content, "Hello group")

    def test_send_group_message_not_member(self):
        """Test sending message by non-member"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.send_group_message(group.group_id, self.user1.user_id, "Hello")
        self.assertIn("Only group members can send messages", str(context.exception))

    def test_get_group_messages_success(self):
        """Test successfully retrieving group messages"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        msg1 = self.manager.send_group_message(group.group_id, self.creator.user_id, "Message 1")
        msg2 = self.manager.send_group_message(group.group_id, self.creator.user_id, "Message 2")

        messages = self.manager.get_group_messages(group.group_id, self.creator.user_id)
        self.assertEqual(len(messages), 2)
        self.assertIn(msg1, messages)
        self.assertIn(msg2, messages)

    def test_get_group_messages_not_member(self):
        """Test retrieving messages by non-member"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        with self.assertRaises(ValueError) as context:
            self.manager.get_group_messages(group.group_id, self.user1.user_id)
        self.assertIn("Only group members can view messages", str(context.exception))

    def test_edit_group_message_success(self):
        """Test successfully editing a group message"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        message = self.manager.send_group_message(group.group_id, self.creator.user_id, "Original")

        self.manager.edit_group_message(message.message_id, "Edited", self.creator.user_id)

        retrieved = self.group_message_repo.get_group_message_by_id(message.message_id)
        self.assertEqual(retrieved.content, "Edited")
        self.assertEqual(retrieved.status, MessageStatus.EDITED)

    def test_edit_group_message_wrong_sender(self):
        """Test editing group message by wrong sender"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        message = self.manager.send_group_message(group.group_id, self.creator.user_id, "Original")

        with self.assertRaises(ValueError) as context:
            self.manager.edit_group_message(message.message_id, "Edited", self.user1.user_id)
        self.assertIn("Only the sender can edit", str(context.exception))

    def test_delete_group_message_by_sender(self):
        """Test deleting group message by sender"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        message = self.manager.send_group_message(group.group_id, self.creator.user_id, "To delete")

        self.manager.delete_group_message(message.message_id, self.creator.user_id)

        retrieved = self.group_message_repo.get_group_message_by_id(message.message_id)
        self.assertEqual(retrieved.status, MessageStatus.DELETED)

    def test_delete_group_message_by_admin(self):
        """Test deleting group message by admin"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)

        message = self.manager.send_group_message(group.group_id, self.user1.user_id, "To delete")

        self.manager.delete_group_message(message.message_id, self.creator.user_id)

        retrieved = self.group_message_repo.get_group_message_by_id(message.message_id)
        self.assertEqual(retrieved.status, MessageStatus.DELETED)

    def test_delete_group_message_by_non_admin_member(self):
        """Test deleting group message by non-admin member who is not the sender"""
        group = self.manager.create_group("Test Group", self.creator.user_id)
        self.manager.add_member(group.group_id, self.user1.user_id, self.creator.user_id)
        self.manager.add_member(group.group_id, self.user2.user_id, self.creator.user_id)

        message = self.manager.send_group_message(group.group_id, self.user1.user_id, "To delete")

        with self.assertRaises(ValueError) as context:
            self.manager.delete_group_message(message.message_id, self.user2.user_id)
        self.assertIn("Only the sender or group admin can delete", str(context.exception))


class TestChatApplication(unittest.TestCase):
    """Test ChatApplication orchestrator functionality"""

    def setUp(self):
        self.app = ChatApplication()

    def test_create_user(self):
        """Test user creation through ChatApplication"""
        user = self.app.create_user("testuser")
        self.assertEqual(user.username, "testuser")

        # Verify user exists
        retrieved = self.app.get_user_by_username("testuser")
        self.assertEqual(retrieved, user)

    def test_get_all_users(self):
        """Test getting all users through ChatApplication"""
        user1 = self.app.create_user("user1")
        user2 = self.app.create_user("user2")

        all_users = self.app.get_all_users()
        self.assertEqual(len(all_users), 2)
        self.assertIn(user1, all_users)
        self.assertIn(user2, all_users)

    def test_direct_messaging_workflow(self):
        """Test complete direct messaging workflow"""
        alice = self.app.create_user("alice")
        bob = self.app.create_user("bob")

        # Send message
        message = self.app.send_message(alice.user_id, bob.user_id, "Hello Bob!")
        self.assertEqual(message.sender_id, alice.user_id)
        self.assertEqual(message.receiver_id, bob.user_id)

        # View message history
        messages = self.app.get_message_history(alice.user_id, bob.user_id)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0], message)

        # Edit message
        self.app.edit_message(message.message_id, "Hello Bob! How are you?", alice.user_id)
        retrieved = self.app._message_repository.get_message_by_id(message.message_id)
        self.assertEqual(retrieved.content, "Hello Bob! How are you?")

        # Delete message
        self.app.delete_message(message.message_id, alice.user_id)
        retrieved = self.app._message_repository.get_message_by_id(message.message_id)
        self.assertEqual(retrieved.status, MessageStatus.DELETED)

    def test_group_chat_workflow(self):
        """Test complete group chat workflow"""
        alice = self.app.create_user("alice")
        bob = self.app.create_user("bob")
        charlie = self.app.create_user("charlie")

        # Create group
        group = self.app.create_group("Study Group", alice.user_id)
        self.assertEqual(group.creator_id, alice.user_id)

        # Add members
        self.app.add_group_member(group.group_id, bob.user_id, alice.user_id)
        self.app.add_group_member(group.group_id, charlie.user_id, alice.user_id)

        # Send group messages
        msg1 = self.app.send_group_message(group.group_id, alice.user_id, "Welcome everyone!")
        msg2 = self.app.send_group_message(group.group_id, bob.user_id, "Thanks for the invite!")

        # View group messages
        messages = self.app.get_group_messages(group.group_id, charlie.user_id)
        self.assertEqual(len(messages), 2)
        self.assertIn(msg1, messages)
        self.assertIn(msg2, messages)

        # Edit group message
        self.app.edit_group_message(msg1.message_id, "Welcome to the study group!", alice.user_id)
        retrieved = self.app._group_message_repository.get_group_message_by_id(msg1.message_id)
        self.assertEqual(retrieved.content, "Welcome to the study group!")

        # Delete group message
        self.app.delete_group_message(msg1.message_id, alice.user_id)
        retrieved = self.app._group_message_repository.get_group_message_by_id(msg1.message_id)
        self.assertEqual(retrieved.status, MessageStatus.DELETED)

        # Remove member
        self.app.remove_group_member(group.group_id, charlie.user_id, alice.user_id)
        self.assertFalse(self.app._group_member_repository.is_user_in_group(group.group_id, charlie.user_id))

        # Member leaves
        self.app.leave_group(group.group_id, bob.user_id)
        self.assertFalse(self.app._group_member_repository.is_user_in_group(group.group_id, bob.user_id))

        # Delete group
        self.app.delete_group(group.group_id, alice.user_id)
        self.assertIsNone(self.app._group_repository.get_group_by_id(group.group_id))


class TestIntegration(unittest.TestCase):
    """Integration tests for complex scenarios"""

    def setUp(self):
        self.app = ChatApplication()

    def test_multiple_conversations(self):
        """Test multiple users having multiple conversations"""
        users = []
        for i in range(5):
            user = self.app.create_user(f"user{i}")
            users.append(user)

        # Create multiple conversations
        conversations = []
        for i in range(len(users)):
            for j in range(i + 1, len(users)):
                msg = self.app.send_message(users[i].user_id, users[j].user_id, f"Message from {i} to {j}")
                conversations.append((users[i], users[j], msg))

        # Verify all conversations exist
        for sender, receiver, original_msg in conversations:
            history = self.app.get_message_history(sender.user_id, receiver.user_id)
            self.assertEqual(len(history), 1)
            self.assertEqual(history[0], original_msg)

    def test_large_group_scenario(self):
        """Test scenario with large group and many messages"""
        admin = self.app.create_user("admin")

        # Create large group
        group = self.app.create_group("Large Group", admin.user_id)

        # Add many members
        members = []
        for i in range(10):
            member = self.app.create_user(f"member{i}")
            members.append(member)
            self.app.add_group_member(group.group_id, member.user_id, admin.user_id)

        # Send many messages
        messages = []
        for i, member in enumerate(members):
            msg = self.app.send_group_message(group.group_id, member.user_id, f"Message {i}")
            messages.append(msg)

        # Verify all messages are visible to admin
        group_messages = self.app.get_group_messages(group.group_id, admin.user_id)
        self.assertEqual(len(group_messages), len(messages))

        # Verify all members are in the group
        group_members = self.app._group_member_repository.get_group_members(group.group_id)
        self.assertEqual(len(group_members), 11)  # 10 members + 1 admin

    def test_admin_role_transitions(self):
        """Test complex admin role transitions"""
        user1 = self.app.create_user("user1")
        user2 = self.app.create_user("user2")
        user3 = self.app.create_user("user3")

        # User1 creates group and is admin
        group = self.app.create_group("Test Group", user1.user_id)

        # Add user2 as member
        self.app.add_group_member(group.group_id, user2.user_id, user1.user_id)

        # Add user3 as admin
        self.app.add_group_member(group.group_id, user3.user_id, user1.user_id)
        # Manually change user3 to admin (simulating promotion)
        member_record = self.app._group_member_repository._members[(group.group_id, user3.user_id)]
        member_record.role = GroupMemberRole.ADMIN

        # Now user1 can leave (user3 is still admin)
        self.app.leave_group(group.group_id, user1.user_id)

        # Verify user3 is still admin and can manage the group
        self.app.add_group_member(group.group_id, user1.user_id, user3.user_id)  # Re-add user1

        # User2 (member) cannot add people
        with self.assertRaises(ValueError):
            self.app.add_group_member(group.group_id, self.app.create_user("user4").user_id, user2.user_id)

    def test_message_status_tracking(self):
        """Test comprehensive message status tracking"""
        alice = self.app.create_user("alice")
        bob = self.app.create_user("bob")

        # Create and track direct message statuses
        msg1 = self.app.send_message(alice.user_id, bob.user_id, "Original message")
        self.assertEqual(msg1.status, MessageStatus.SENT)

        self.app.edit_message(msg1.message_id, "Edited message", alice.user_id)
        msg1_updated = self.app._message_repository.get_message_by_id(msg1.message_id)
        self.assertEqual(msg1_updated.status, MessageStatus.EDITED)

        self.app.delete_message(msg1.message_id, alice.user_id)
        msg1_deleted = self.app._message_repository.get_message_by_id(msg1.message_id)
        self.assertEqual(msg1_deleted.status, MessageStatus.DELETED)

        # Create and track group message statuses
        group = self.app.create_group("Test Group", alice.user_id)
        self.app.add_group_member(group.group_id, bob.user_id, alice.user_id)

        gmsg1 = self.app.send_group_message(group.group_id, alice.user_id, "Group message")
        self.assertEqual(gmsg1.status, MessageStatus.SENT)

        self.app.edit_group_message(gmsg1.message_id, "Edited group message", alice.user_id)
        gmsg1_updated = self.app._group_message_repository.get_group_message_by_id(gmsg1.message_id)
        self.assertEqual(gmsg1_updated.status, MessageStatus.EDITED)

        self.app.delete_group_message(gmsg1.message_id, alice.user_id)
        gmsg1_deleted = self.app._group_message_repository.get_group_message_by_id(gmsg1.message_id)
        self.assertEqual(gmsg1_deleted.status, MessageStatus.DELETED)


if __name__ == '__main__':
    unittest.main()
