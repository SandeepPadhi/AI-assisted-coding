"""
Goal:
- Create a chat application.

Functional Requirements:
- users can send messages to each other.
- Users should be able to see the messages in real time.
- User should be able to see the messages in the past.
- User should be able to create a group chat.
- User should be able to add users to a group chat.
- User should be able to remove users from a group chat.
- User should be able to leave a group chat.
- User should be able to delete a group chat.
- User should be able to delete a message.
- User should be able to edit a message.

Non-Functional Requirements:
- The system should be able to scale to 1000000 users.
- The system should be able to handle 1000 messages per second.
- The system should be able to handle 1000000 users.
- The system should be able to handle 1000000 messages.
- The system should be able to handle 1000000 users.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional, Set, Dict
from uuid import UUID, uuid4

# Entities
@dataclass
class User:
    user_id: UUID
    username: str
    created_at: datetime
    
    def __init__(self, username: str):
        self.user_id = uuid4()
        self.username = self._validate_username(username)
        self.created_at = datetime.now()
    
    @staticmethod
    def _validate_username(username: str) -> str:
        if not username or not isinstance(username, str):
            raise ValueError("Username must be a non-empty string")
        if len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        return username.strip()

class MessageStatus(Enum):
    SENT = "sent"
    DELETED = "deleted"
    EDITED = "edited"

@dataclass
class Message:
    message_id: UUID
    sender_id: UUID
    receiver_id: UUID
    content: str
    status: MessageStatus
    created_at: datetime
    updated_at: datetime
    
    def __init__(self, sender_id: UUID, receiver_id: UUID, content: str):
        self.message_id = uuid4()
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = self._validate_content(content)
        self.status = MessageStatus.SENT
        self.created_at = datetime.now()
        self.updated_at = self.created_at
    
    @staticmethod
    def _validate_content(content: str) -> str:
        if not content or not isinstance(content, str):
            raise ValueError("Message content must be a non-empty string")
        if len(content) > 1000:
            raise ValueError("Message content cannot exceed 1000 characters")
        return content.strip()
    
    def edit_content(self, new_content: str) -> None:
        self.content = self._validate_content(new_content)
        self.status = MessageStatus.EDITED
        self.updated_at = datetime.now()
    
    def delete(self) -> None:
        self.content = ""
        self.status = MessageStatus.DELETED
        self.updated_at = datetime.now()

@dataclass
class Group:
    group_id: UUID
    name: str
    creator_id: UUID
    created_at: datetime
    
    def __init__(self, name: str, creator_id: UUID):
        self.group_id = uuid4()
        self.name = self._validate_name(name)
        self.creator_id = creator_id
        self.created_at = datetime.now()
    
    @staticmethod
    def _validate_name(name: str) -> str:
        if not name or not isinstance(name, str):
            raise ValueError("Group name must be a non-empty string")
        if len(name) < 3 or len(name) > 50:
            raise ValueError("Group name must be between 3 and 50 characters")
        return name.strip()

class GroupMemberRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"

@dataclass
class GroupMember:
    group_id: UUID
    user_id: UUID
    role: GroupMemberRole
    joined_at: datetime
    
    def __init__(self, group_id: UUID, user_id: UUID, role: GroupMemberRole):
        self.group_id = group_id
        self.user_id = user_id
        self.role = role
        self.joined_at = datetime.now()

@dataclass
class GroupMessage:
    message_id: UUID
    group_id: UUID
    sender_id: UUID
    content: str
    status: MessageStatus
    created_at: datetime
    updated_at: datetime
    
    def __init__(self, group_id: UUID, sender_id: UUID, content: str):
        self.message_id = uuid4()
        self.group_id = group_id
        self.sender_id = sender_id
        self.content = self._validate_content(content)
        self.status = MessageStatus.SENT
        self.created_at = datetime.now()
        self.updated_at = self.created_at
    
    @staticmethod
    def _validate_content(content: str) -> str:
        if not content or not isinstance(content, str):
            raise ValueError("Message content must be a non-empty string")
        if len(content) > 1000:
            raise ValueError("Message content cannot exceed 1000 characters")
        return content.strip()
    
    def edit_content(self, new_content: str) -> None:
        self.content = self._validate_content(new_content)
        self.status = MessageStatus.EDITED
        self.updated_at = datetime.now()
    
    def delete(self) -> None:
        self.content = ""
        self.status = MessageStatus.DELETED
        self.updated_at = datetime.now()

# Abstract Repository Classes
class AbstractUserRepository(ABC):
    @abstractmethod
    def create_user(self, username: str) -> User:
        """Creates a new user with the given username."""
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieves a user by their ID."""
        pass
    
    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieves a user by their username."""
        pass
    
    @abstractmethod
    def get_all_users(self) -> List[User]:
        """Retrieves all users in the system."""
        pass

class AbstractMessageRepository(ABC):
    @abstractmethod
    def create_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
        """Creates a new message from sender to receiver."""
        pass
    
    @abstractmethod
    def get_message_by_id(self, message_id: UUID) -> Optional[Message]:
        """Retrieves a message by its ID."""
        pass
    
    @abstractmethod
    def get_messages_between_users(self, user1_id: UUID, user2_id: UUID) -> List[Message]:
        """Retrieves all messages exchanged between two users."""
        pass
    
    @abstractmethod
    def update_message(self, message: Message) -> None:
        """Updates an existing message."""
        pass
    
    @abstractmethod
    def delete_message(self, message_id: UUID) -> None:
        """Marks a message as deleted."""
        pass

class AbstractGroupRepository(ABC):
    @abstractmethod
    def create_group(self, name: str, creator_id: UUID) -> Group:
        """Creates a new group with the given name and creator."""
        pass
    
    @abstractmethod
    def get_group_by_id(self, group_id: UUID) -> Optional[Group]:
        """Retrieves a group by its ID."""
        pass
    
    @abstractmethod
    def get_groups_by_user(self, user_id: UUID) -> List[Group]:
        """Retrieves all groups that a user is a member of."""
        pass
    
    @abstractmethod
    def delete_group(self, group_id: UUID) -> None:
        """Deletes a group and all its associated data."""
        pass

class AbstractGroupMemberRepository(ABC):
    @abstractmethod
    def add_member(self, group_id: UUID, user_id: UUID, role: GroupMemberRole) -> GroupMember:
        """Adds a user to a group with the specified role."""
        pass
    
    @abstractmethod
    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        """Removes a user from a group."""
        pass
    
    @abstractmethod
    def get_group_members(self, group_id: UUID) -> List[GroupMember]:
        """Retrieves all members of a group."""
        pass
    
    @abstractmethod
    def get_member_role(self, group_id: UUID, user_id: UUID) -> Optional[GroupMemberRole]:
        """Retrieves a user's role in a group."""
        pass
    
    @abstractmethod
    def is_user_in_group(self, group_id: UUID, user_id: UUID) -> bool:
        """Checks if a user is a member of a group."""
        pass

class AbstractGroupMessageRepository(ABC):
    @abstractmethod
    def create_group_message(self, group_id: UUID, sender_id: UUID, content: str) -> GroupMessage:
        """Creates a new message in a group."""
        pass
    
    @abstractmethod
    def get_group_message_by_id(self, message_id: UUID) -> Optional[GroupMessage]:
        """Retrieves a group message by its ID."""
        pass
    
    @abstractmethod
    def get_group_messages(self, group_id: UUID) -> List[GroupMessage]:
        """Retrieves all messages in a group."""
        pass
    
    @abstractmethod
    def update_group_message(self, message: GroupMessage) -> None:
        """Updates an existing group message."""
        pass
    
    @abstractmethod
    def delete_group_message(self, message_id: UUID) -> None:
        """Marks a group message as deleted."""
        pass

# In-Memory Repository Implementations
class InMemoryUserRepository(AbstractUserRepository):
    def __init__(self):
        self._users: Dict[UUID, User] = {}
        self._username_index: Dict[str, UUID] = {}
    
    def create_user(self, username: str) -> User:
        if username.lower() in {u.lower() for u in self._username_index.keys()}:
            raise ValueError(f"Username '{username}' is already taken")
        user = User(username)
        self._users[user.user_id] = user
        self._username_index[user.username] = user.user_id
        return user
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self._users.get(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        user_id = self._username_index.get(username)
        return self._users.get(user_id) if user_id else None
    
    def get_all_users(self) -> List[User]:
        return list(self._users.values())

class InMemoryMessageRepository(AbstractMessageRepository):
    def __init__(self):
        self._messages: Dict[UUID, Message] = {}
        self._user_messages: Dict[UUID, Set[UUID]] = {}
    
    def create_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
        message = Message(sender_id, receiver_id, content)
        self._messages[message.message_id] = message
        
        # Index for both sender and receiver
        if sender_id not in self._user_messages:
            self._user_messages[sender_id] = set()
        if receiver_id not in self._user_messages:
            self._user_messages[receiver_id] = set()
        
        self._user_messages[sender_id].add(message.message_id)
        self._user_messages[receiver_id].add(message.message_id)
        
        return message
    
    def get_message_by_id(self, message_id: UUID) -> Optional[Message]:
        return self._messages.get(message_id)
    
    def get_messages_between_users(self, user1_id: UUID, user2_id: UUID) -> List[Message]:
        messages = []
        user1_messages = self._user_messages.get(user1_id, set())
        user2_messages = self._user_messages.get(user2_id, set())
        
        # Find messages that involve both users
        common_message_ids = user1_messages.intersection(user2_messages)
        for message_id in common_message_ids:
            message = self._messages[message_id]
            if (message.sender_id == user1_id and message.receiver_id == user2_id) or \
               (message.sender_id == user2_id and message.receiver_id == user1_id):
                messages.append(message)
        
        return sorted(messages, key=lambda m: m.created_at)
    
    def update_message(self, message: Message) -> None:
        if message.message_id not in self._messages:
            raise ValueError("Message not found")
        self._messages[message.message_id] = message
    
    def delete_message(self, message_id: UUID) -> None:
        if message_id in self._messages:
            message = self._messages[message_id]
            message.delete()
            self._messages[message_id] = message

class InMemoryGroupRepository(AbstractGroupRepository):
    def __init__(self):
        self._groups: Dict[UUID, Group] = {}
        self._user_groups: Dict[UUID, Set[UUID]] = {}
    
    def create_group(self, name: str, creator_id: UUID) -> Group:
        group = Group(name, creator_id)
        self._groups[group.group_id] = group
        
        if creator_id not in self._user_groups:
            self._user_groups[creator_id] = set()
        self._user_groups[creator_id].add(group.group_id)
        
        return group
    
    def get_group_by_id(self, group_id: UUID) -> Optional[Group]:
        return self._groups.get(group_id)
    
    def get_groups_by_user(self, user_id: UUID) -> List[Group]:
        group_ids = self._user_groups.get(user_id, set())
        return [self._groups[gid] for gid in group_ids if gid in self._groups]
    
    def delete_group(self, group_id: UUID) -> None:
        if group_id in self._groups:
            # Remove group from all user_groups sets
            for user_groups in self._user_groups.values():
                user_groups.discard(group_id)
            del self._groups[group_id]

class InMemoryGroupMemberRepository(AbstractGroupMemberRepository):
    def __init__(self):
        self._members: Dict[tuple[UUID, UUID], GroupMember] = {}  # (group_id, user_id) -> GroupMember
        self._group_members: Dict[UUID, Set[UUID]] = {}  # group_id -> Set[user_id]
    
    def add_member(self, group_id: UUID, user_id: UUID, role: GroupMemberRole) -> GroupMember:
        member = GroupMember(group_id, user_id, role)
        self._members[(group_id, user_id)] = member
        
        if group_id not in self._group_members:
            self._group_members[group_id] = set()
        self._group_members[group_id].add(user_id)
        
        return member
    
    def remove_member(self, group_id: UUID, user_id: UUID) -> None:
        key = (group_id, user_id)
        if key in self._members:
            del self._members[key]
            self._group_members[group_id].discard(user_id)
    
    def get_group_members(self, group_id: UUID) -> List[GroupMember]:
        return [
            member for key, member in self._members.items()
            if key[0] == group_id
        ]
    
    def get_member_role(self, group_id: UUID, user_id: UUID) -> Optional[GroupMemberRole]:
        member = self._members.get((group_id, user_id))
        return member.role if member else None
    
    def is_user_in_group(self, group_id: UUID, user_id: UUID) -> bool:
        return (group_id, user_id) in self._members

class InMemoryGroupMessageRepository(AbstractGroupMessageRepository):
    def __init__(self):
        self._messages: Dict[UUID, GroupMessage] = {}
        self._group_messages: Dict[UUID, Set[UUID]] = {}  # group_id -> Set[message_id]
    
    def create_group_message(self, group_id: UUID, sender_id: UUID, content: str) -> GroupMessage:
        message = GroupMessage(group_id, sender_id, content)
        self._messages[message.message_id] = message
        
        if group_id not in self._group_messages:
            self._group_messages[group_id] = set()
        self._group_messages[group_id].add(message.message_id)
        
        return message
    
    def get_group_message_by_id(self, message_id: UUID) -> Optional[GroupMessage]:
        return self._messages.get(message_id)
    
    def get_group_messages(self, group_id: UUID) -> List[GroupMessage]:
        message_ids = self._group_messages.get(group_id, set())
        messages = [self._messages[mid] for mid in message_ids if mid in self._messages]
        return sorted(messages, key=lambda m: m.created_at)
    
    def update_group_message(self, message: GroupMessage) -> None:
        if message.message_id not in self._messages:
            raise ValueError("Message not found")
        self._messages[message.message_id] = message
    
    def delete_group_message(self, message_id: UUID) -> None:
        if message_id in self._messages:
            message = self._messages[message_id]
            message.delete()
            self._messages[message_id] = message

# Entity Managers
class UserManager:
    def __init__(self, user_repository: AbstractUserRepository):
        self._user_repository = user_repository
    
    def create_user(self, username: str) -> User:
        """Creates a new user with the given username."""
        return self._user_repository.create_user(username)
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """Retrieves a user by their ID."""
        return self._user_repository.get_user_by_id(user_id)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Retrieves a user by their username."""
        return self._user_repository.get_user_by_username(username)
    
    def get_all_users(self) -> List[User]:
        """Retrieves all users in the system."""
        return self._user_repository.get_all_users()

class MessageManager:
    def __init__(
        self,
        message_repository: AbstractMessageRepository,
        user_repository: AbstractUserRepository
    ):
        self._message_repository = message_repository
        self._user_repository = user_repository
    
    def send_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
        """Sends a message from one user to another."""
        # Validate users exist
        sender = self._user_repository.get_user_by_id(sender_id)
        receiver = self._user_repository.get_user_by_id(receiver_id)
        
        if not sender:
            raise ValueError("Sender not found")
        if not receiver:
            raise ValueError("Receiver not found")
        
        return self._message_repository.create_message(sender_id, receiver_id, content)
    
    def get_message_history(self, user1_id: UUID, user2_id: UUID) -> List[Message]:
        """Gets the message history between two users."""
        # Validate users exist
        user1 = self._user_repository.get_user_by_id(user1_id)
        user2 = self._user_repository.get_user_by_id(user2_id)
        
        if not user1:
            raise ValueError("User1 not found")
        if not user2:
            raise ValueError("User2 not found")
        
        return self._message_repository.get_messages_between_users(user1_id, user2_id)
    
    def edit_message(self, message_id: UUID, new_content: str, user_id: UUID) -> None:
        """Edits a message if the user is the sender."""
        message = self._message_repository.get_message_by_id(message_id)
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != user_id:
            raise ValueError("Only the sender can edit the message")
        
        message.edit_content(new_content)
        self._message_repository.update_message(message)
    
    def delete_message(self, message_id: UUID, user_id: UUID) -> None:
        """Deletes a message if the user is the sender."""
        message = self._message_repository.get_message_by_id(message_id)
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != user_id:
            raise ValueError("Only the sender can delete the message")
        
        self._message_repository.delete_message(message_id)

class GroupManager:
    def __init__(
        self,
        group_repository: AbstractGroupRepository,
        group_member_repository: AbstractGroupMemberRepository,
        group_message_repository: AbstractGroupMessageRepository,
        user_repository: AbstractUserRepository
    ):
        self._group_repository = group_repository
        self._group_member_repository = group_member_repository
        self._group_message_repository = group_message_repository
        self._user_repository = user_repository
    
    def create_group(self, name: str, creator_id: UUID) -> Group:
        """Creates a new group and adds the creator as an admin."""
        # Validate creator exists
        creator = self._user_repository.get_user_by_id(creator_id)
        if not creator:
            raise ValueError("Creator not found")
        
        group = self._group_repository.create_group(name, creator_id)
        self._group_member_repository.add_member(group.group_id, creator_id, GroupMemberRole.ADMIN)
        return group
    
    def add_member(self, group_id: UUID, user_id: UUID, admin_id: UUID) -> None:
        """Adds a member to a group if the admin has permission."""
        # Validate group exists
        group = self._group_repository.get_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        
        # Validate user exists
        user = self._user_repository.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Check if admin has permission
        admin_role = self._group_member_repository.get_member_role(group_id, admin_id)
        if admin_role != GroupMemberRole.ADMIN:
            raise ValueError("Only admins can add members")
        
        # Check if user is already in group
        if self._group_member_repository.is_user_in_group(group_id, user_id):
            raise ValueError("User is already in the group")
        
        self._group_member_repository.add_member(group_id, user_id, GroupMemberRole.MEMBER)
    
    def remove_member(self, group_id: UUID, user_id: UUID, admin_id: UUID) -> None:
        """Removes a member from a group if the admin has permission."""
        # Validate group exists
        group = self._group_repository.get_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        
        # Check if admin has permission
        admin_role = self._group_member_repository.get_member_role(group_id, admin_id)
        if admin_role != GroupMemberRole.ADMIN:
            raise ValueError("Only admins can remove members")
        
        # Check if user is in group
        if not self._group_member_repository.is_user_in_group(group_id, user_id):
            raise ValueError("User is not in the group")
        
        # Don't allow removing the last admin
        if self._group_member_repository.get_member_role(group_id, user_id) == GroupMemberRole.ADMIN:
            admin_count = sum(
                1 for member in self._group_member_repository.get_group_members(group_id)
                if member.role == GroupMemberRole.ADMIN
            )
            if admin_count <= 1:
                raise ValueError("Cannot remove the last admin")
        
        self._group_member_repository.remove_member(group_id, user_id)
    
    def leave_group(self, group_id: UUID, user_id: UUID) -> None:
        """Allows a user to leave a group."""
        # Validate group exists
        group = self._group_repository.get_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        
        # Check if user is in group
        if not self._group_member_repository.is_user_in_group(group_id, user_id):
            raise ValueError("User is not in the group")
        
        # Don't allow leaving if last admin
        if self._group_member_repository.get_member_role(group_id, user_id) == GroupMemberRole.ADMIN:
            admin_count = sum(
                1 for member in self._group_member_repository.get_group_members(group_id)
                if member.role == GroupMemberRole.ADMIN
            )
            if admin_count <= 1:
                raise ValueError("Cannot leave as the last admin")
        
        self._group_member_repository.remove_member(group_id, user_id)
    
    def delete_group(self, group_id: UUID, admin_id: UUID) -> None:
        """Deletes a group if the admin has permission."""
        # Validate group exists
        group = self._group_repository.get_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        
        # Check if admin has permission
        admin_role = self._group_member_repository.get_member_role(group_id, admin_id)
        if admin_role != GroupMemberRole.ADMIN:
            raise ValueError("Only admins can delete the group")
        
        self._group_repository.delete_group(group_id)
    
    def send_group_message(self, group_id: UUID, sender_id: UUID, content: str) -> GroupMessage:
        """Sends a message to a group if the sender is a member."""
        # Validate group exists
        group = self._group_repository.get_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        
        # Check if sender is in group
        if not self._group_member_repository.is_user_in_group(group_id, sender_id):
            raise ValueError("Only group members can send messages")
        
        return self._group_message_repository.create_group_message(group_id, sender_id, content)
    
    def get_group_messages(self, group_id: UUID, user_id: UUID) -> List[GroupMessage]:
        """Gets all messages in a group if the user is a member."""
        # Validate group exists
        group = self._group_repository.get_group_by_id(group_id)
        if not group:
            raise ValueError("Group not found")
        
        # Check if user is in group
        if not self._group_member_repository.is_user_in_group(group_id, user_id):
            raise ValueError("Only group members can view messages")
        
        return self._group_message_repository.get_group_messages(group_id)
    
    def edit_group_message(self, message_id: UUID, new_content: str, user_id: UUID) -> None:
        """Edits a group message if the user is the sender."""
        message = self._group_message_repository.get_group_message_by_id(message_id)
        if not message:
            raise ValueError("Message not found")
        
        if message.sender_id != user_id:
            raise ValueError("Only the sender can edit the message")
        
        message.edit_content(new_content)
        self._group_message_repository.update_group_message(message)
    
    def delete_group_message(self, message_id: UUID, user_id: UUID) -> None:
        """Deletes a group message if the user is the sender or an admin."""
        message = self._group_message_repository.get_group_message_by_id(message_id)
        if not message:
            raise ValueError("Message not found")
        
        # Allow deletion if user is sender or admin
        is_sender = message.sender_id == user_id
        is_admin = self._group_member_repository.get_member_role(message.group_id, user_id) == GroupMemberRole.ADMIN
        
        if not (is_sender or is_admin):
            raise ValueError("Only the sender or group admin can delete the message")
        
        self._group_message_repository.delete_group_message(message_id)

class ChatApplication:
    """Main orchestrator for the chat application."""
    
    def __init__(self):
        # Initialize repositories
        self._user_repository = InMemoryUserRepository()
        self._message_repository = InMemoryMessageRepository()
        self._group_repository = InMemoryGroupRepository()
        self._group_member_repository = InMemoryGroupMemberRepository()
        self._group_message_repository = InMemoryGroupMessageRepository()
        
        # Initialize managers
        self._user_manager = UserManager(self._user_repository)
        self._message_manager = MessageManager(self._message_repository, self._user_repository)
        self._group_manager = GroupManager(
            self._group_repository,
            self._group_member_repository,
            self._group_message_repository,
            self._user_repository
        )
    
    # User Management
    def create_user(self, username: str) -> User:
        """Creates a new user."""
        return self._user_manager.create_user(username)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Gets a user by their username."""
        return self._user_manager.get_user_by_username(username)
    
    def get_all_users(self) -> List[User]:
        """Gets all users in the system."""
        return self._user_manager.get_all_users()
    
    # Direct Messaging
    def send_message(self, sender_id: UUID, receiver_id: UUID, content: str) -> Message:
        """Sends a direct message from one user to another."""
        return self._message_manager.send_message(sender_id, receiver_id, content)
    
    def get_message_history(self, user1_id: UUID, user2_id: UUID) -> List[Message]:
        """Gets the message history between two users."""
        return self._message_manager.get_message_history(user1_id, user2_id)
    
    def edit_message(self, message_id: UUID, new_content: str, user_id: UUID) -> None:
        """Edits a direct message."""
        self._message_manager.edit_message(message_id, new_content, user_id)
    
    def delete_message(self, message_id: UUID, user_id: UUID) -> None:
        """Deletes a direct message."""
        self._message_manager.delete_message(message_id, user_id)
    
    # Group Management
    def create_group(self, name: str, creator_id: UUID) -> Group:
        """Creates a new group chat."""
        return self._group_manager.create_group(name, creator_id)
    
    def add_group_member(self, group_id: UUID, user_id: UUID, admin_id: UUID) -> None:
        """Adds a user to a group chat."""
        self._group_manager.add_member(group_id, user_id, admin_id)
    
    def remove_group_member(self, group_id: UUID, user_id: UUID, admin_id: UUID) -> None:
        """Removes a user from a group chat."""
        self._group_manager.remove_member(group_id, user_id, admin_id)
    
    def leave_group(self, group_id: UUID, user_id: UUID) -> None:
        """Allows a user to leave a group chat."""
        self._group_manager.leave_group(group_id, user_id)
    
    def delete_group(self, group_id: UUID, admin_id: UUID) -> None:
        """Deletes a group chat."""
        self._group_manager.delete_group(group_id, admin_id)
    
    # Group Messaging
    def send_group_message(self, group_id: UUID, sender_id: UUID, content: str) -> GroupMessage:
        """Sends a message to a group chat."""
        return self._group_manager.send_group_message(group_id, sender_id, content)
    
    def get_group_messages(self, group_id: UUID, user_id: UUID) -> List[GroupMessage]:
        """Gets all messages in a group chat."""
        return self._group_manager.get_group_messages(group_id, user_id)
    
    def edit_group_message(self, message_id: UUID, new_content: str, user_id: UUID) -> None:
        """Edits a group message."""
        self._group_manager.edit_group_message(message_id, new_content, user_id)
    
    def delete_group_message(self, message_id: UUID, user_id: UUID) -> None:
        """Deletes a group message."""
        self._group_manager.delete_group_message(message_id, user_id)

def main():
    # Example usage
    print("=== Chat Application Demo ===\n")
    chat_app = ChatApplication()

    # Create users
    print("1. Creating users...")
    alice = chat_app.create_user("Alice")
    print(f"   ✓ Created user: {alice.username} (ID: {alice.user_id})")

    bob = chat_app.create_user("Bob")
    print(f"   ✓ Created user: {bob.username} (ID: {bob.user_id})")

    charlie = chat_app.create_user("Charlie")
    print(f"   ✓ Created user: {charlie.username} (ID: {charlie.user_id})")

    print(f"\n   Total users: {len(chat_app.get_all_users())}\n")

    # Direct messaging
    print("2. Direct messaging...")
    message = chat_app.send_message(alice.user_id, bob.user_id, "Hello Bob!")
    print(f"   ✓ Alice sent: '{message.content}'")

    reply = chat_app.send_message(bob.user_id, alice.user_id, "Hi Alice!")
    print(f"   ✓ Bob sent: '{reply.content}'")

    # View message history
    print("\n3. Viewing message history between Alice and Bob...")
    messages = chat_app.get_message_history(alice.user_id, bob.user_id)
    for i, msg in enumerate(messages, 1):
        sender = "Alice" if msg.sender_id == alice.user_id else "Bob"
        print(f"   {i}. {sender}: '{msg.content}' ({msg.status.value})")

    # Edit and delete messages
    print("\n4. Editing and deleting messages...")
    chat_app.edit_message(message.message_id, "Hello Bob! How are you?", alice.user_id)
    print(f"   ✓ Alice edited message to: '{message.content}'")

    chat_app.delete_message(message.message_id, alice.user_id)
    print("   ✓ Alice deleted the message")
    # Group chat
    print("\n5. Creating group chat...")
    group = chat_app.create_group("Fun Group", alice.user_id)
    print(f"   ✓ Created group: '{group.name}' (ID: {group.group_id})")

    print("   Adding members...")
    chat_app.add_group_member(group.group_id, bob.user_id, alice.user_id)
    print(f"   ✓ Added Bob to '{group.name}'")

    chat_app.add_group_member(group.group_id, charlie.user_id, alice.user_id)
    print(f"   ✓ Added Charlie to '{group.name}'")

    # Group messaging
    print("\n6. Group messaging...")
    group_msg = chat_app.send_group_message(group.group_id, alice.user_id, "Welcome everyone!")
    print(f"   ✓ Alice sent to group: '{group_msg.content}'")

    group_reply = chat_app.send_group_message(group.group_id, bob.user_id, "Thanks for adding me!")
    print(f"   ✓ Bob sent to group: '{group_reply.content}'")

    # View group messages
    print(f"\n7. Viewing messages in '{group.name}'...")
    group_messages = chat_app.get_group_messages(group.group_id, charlie.user_id)
    for i, msg in enumerate(group_messages, 1):
        sender = "Alice" if msg.sender_id == alice.user_id else "Bob"
        print(f"   {i}. {sender}: '{msg.content}' ({msg.status.value})")

    # Edit and delete group messages
    print("\n8. Editing and deleting group messages...")
    chat_app.edit_group_message(group_msg.message_id, "Welcome to the group!", alice.user_id)
    print(f"   ✓ Alice edited group message to: '{group_msg.content}'")

    chat_app.delete_group_message(group_msg.message_id, alice.user_id)
    print("   ✓ Alice deleted the group message")
    # Group management
    print("\n9. Group management...")
    chat_app.remove_group_member(group.group_id, charlie.user_id, alice.user_id)
    print(f"   ✓ Removed Charlie from '{group.name}'")

    chat_app.leave_group(group.group_id, bob.user_id)
    print(f"   ✓ Bob left '{group.name}'")

    chat_app.delete_group(group.group_id, alice.user_id)
    print(f"   ✓ Alice deleted '{group.name}'")

    print("\n=== Demo completed successfully! ===")
    print("\nAll features demonstrated:")
    print("✓ User creation and management")
    print("✓ Direct messaging (send, view, edit, delete)")
    print("✓ Group creation and member management")
    print("✓ Group messaging (send, view, edit, delete)")
    print("✓ Group administration (add, remove, leave, delete)")

if __name__ == "__main__":
    main()