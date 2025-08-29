"""
Unit tests for User Repository.

Tests cover:
- User CRUD operations
- Thread-safe operations
- Error handling
- Data validation
- Repository-specific functionality
"""

import pytest
import threading
import time
from datetime import datetime, timedelta
from entities import User, UserStatus
from repositories import InMemoryUserRepository


class TestInMemoryUserRepository:
    """Test cases for InMemoryUserRepository"""

    def test_repository_initialization(self, user_repository):
        """Test repository initialization"""
        assert user_repository is not None
        assert hasattr(user_repository, '_storage')
        assert hasattr(user_repository, '_lock')
        assert isinstance(user_repository._storage, dict)
        assert isinstance(user_repository._lock, threading.Lock)

    def test_save_user_valid(self, user_repository, sample_user):
        """Test saving a valid user"""
        result = user_repository.save(sample_user)

        assert result is None  # save() returns None
        assert sample_user.user_id in user_repository._storage
        assert user_repository._storage[sample_user.user_id] == sample_user

    def test_save_user_duplicate(self, user_repository, sample_user):
        """Test saving duplicate user (should overwrite)"""
        # Save user first time
        user_repository.save(sample_user)
        original_created = sample_user.created_at

        # Modify and save again
        sample_user.name = "Updated Name"
        user_repository.save(sample_user)

        # Should still be the same user with updated data
        assert user_repository._storage[sample_user.user_id].name == "Updated Name"
        assert user_repository._storage[sample_user.user_id].created_at == original_created

    def test_find_by_id_existing(self, user_repository, sample_user):
        """Test finding existing user by ID"""
        user_repository.save(sample_user)

        found_user = user_repository.find_by_id(sample_user.user_id)

        assert found_user is not None
        assert found_user == sample_user
        assert found_user.user_id == sample_user.user_id

    def test_find_by_id_nonexistent(self, user_repository):
        """Test finding non-existent user by ID"""
        found_user = user_repository.find_by_id("nonexistent_id")

        assert found_user is None

    def test_find_all_empty(self, user_repository):
        """Test finding all users when repository is empty"""
        users = user_repository.find_all()

        assert isinstance(users, list)
        assert len(users) == 0

    def test_find_all_with_users(self, user_repository):
        """Test finding all users"""
        # Create and save multiple users
        users = []
        for i in range(3):
            user = User(f"user_{i}", f"User {i}", f"user{i}@example.com", 25 + i)
            users.append(user)
            user_repository.save(user)

        found_users = user_repository.find_all()

        assert len(found_users) == 3
        assert set(found_users) == set(users)

    def test_exists_by_id(self, user_repository, sample_user):
        """Test checking if user exists by ID"""
        # User doesn't exist initially
        assert not user_repository.exists_by_id(sample_user.user_id)

        # Save user
        user_repository.save(sample_user)

        # User exists now
        assert user_repository.exists_by_id(sample_user.user_id)

        # Non-existent user
        assert not user_repository.exists_by_id("nonexistent_id")

    def test_delete_by_id_existing(self, user_repository, sample_user):
        """Test deleting existing user by ID"""
        user_repository.save(sample_user)
        assert user_repository.exists_by_id(sample_user.user_id)

        result = user_repository.delete_by_id(sample_user.user_id)

        assert result is True
        assert not user_repository.exists_by_id(sample_user.user_id)

    def test_delete_by_id_nonexistent(self, user_repository):
        """Test deleting non-existent user by ID"""
        result = user_repository.delete_by_id("nonexistent_id")

        assert result is False

    def test_count_empty(self, user_repository):
        """Test counting users when repository is empty"""
        assert user_repository.count() == 0

    def test_count_with_users(self, user_repository):
        """Test counting users"""
        # Create and save users
        for i in range(5):
            user = User(f"user_{i}", f"User {i}", f"user{i}@example.com", 25)
            user_repository.save(user)

        assert user_repository.count() == 5

    def test_find_by_email_existing(self, user_repository, sample_user):
        """Test finding user by email"""
        user_repository.save(sample_user)

        found_user = user_repository.find_by_email(sample_user.email)

        assert found_user is not None
        assert found_user == sample_user
        assert found_user.email == sample_user.email

    def test_find_by_email_nonexistent(self, user_repository):
        """Test finding non-existent user by email"""
        found_user = user_repository.find_by_email("nonexistent@example.com")

        assert found_user is None

    def test_find_by_email_case_insensitive(self, user_repository):
        """Test email search is case insensitive"""
        user = User("user_123", "John", "JOHN@EXAMPLE.COM", 30)
        user_repository.save(user)

        # Search with different cases
        found1 = user_repository.find_by_email("john@example.com")
        found2 = user_repository.find_by_email("JOHN@example.com")
        found3 = user_repository.find_by_email("John@Example.Com")

        assert found1 == user
        assert found2 == user
        assert found3 == user

    def test_find_by_status(self, user_repository):
        """Test finding users by status"""
        # Create users with different statuses
        active_user = User("active", "Active", "active@example.com", 25)
        inactive_user = User("inactive", "Inactive", "inactive@example.com", 26)
        suspended_user = User("suspended", "Suspended", "suspended@example.com", 27)

        inactive_user.update_status(UserStatus.INACTIVE)
        suspended_user.update_status(UserStatus.SUSPENDED)

        user_repository.save(active_user)
        user_repository.save(inactive_user)
        user_repository.save(suspended_user)

        # Find by status
        active_users = user_repository.find_by_status(UserStatus.ACTIVE)
        inactive_users = user_repository.find_by_status(UserStatus.INACTIVE)
        suspended_users = user_repository.find_by_status(UserStatus.SUSPENDED)

        assert len(active_users) == 1
        assert len(inactive_users) == 1
        assert len(suspended_users) == 1

        assert active_users[0] == active_user
        assert inactive_users[0] == inactive_user
        assert suspended_users[0] == suspended_user

    def test_thread_safety_save(self, user_repository):
        """Test thread safety of save operations"""
        results = []
        errors = []

        def save_user(user_id):
            try:
                user = User(user_id, f"User {user_id}", f"{user_id}@example.com", 25)
                user_repository.save(user)
                results.append(user_id)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_user, args=[f"user_{i}"])
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 10
        assert len(errors) == 0
        assert user_repository.count() == 10

    def test_thread_safety_read_write(self, user_repository):
        """Test thread safety of concurrent read/write operations"""
        # Pre-populate with some users
        for i in range(5):
            user = User(f"user_{i}", f"User {i}", f"user{i}@example.com", 25)
            user_repository.save(user)

        results = []
        errors = []

        def read_write_operation(operation_id):
            try:
                if operation_id % 2 == 0:
                    # Read operation
                    users = user_repository.find_all()
                    results.append(f"read_{len(users)}")
                else:
                    # Write operation
                    user = User(f"new_user_{operation_id}", f"New User {operation_id}",
                              f"new{operation_id}@example.com", 30)
                    user_repository.save(user)
                    results.append(f"write_{user.user_id}")
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=read_write_operation, args=[i])
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 20
        assert len(errors) == 0
        # Should have original 5 + 10 new users (odd operations)
        assert user_repository.count() == 15

    def test_bulk_operations(self, user_repository):
        """Test bulk save and delete operations"""
        # Create many users
        users = []
        for i in range(100):
            user = User(f"user_{i}", f"User {i}", f"user{i}@example.com", 25)
            users.append(user)

        # Bulk save
        for user in users:
            user_repository.save(user)

        assert user_repository.count() == 100

        # Bulk delete
        for user in users:
            user_repository.delete_by_id(user.user_id)

        assert user_repository.count() == 0

    def test_data_integrity(self, user_repository, sample_user):
        """Test data integrity across operations"""
        # Save user
        user_repository.save(sample_user)
        original_data = {
            "user_id": sample_user.user_id,
            "name": sample_user.name,
            "email": sample_user.email,
            "age": sample_user.age,
            "status": sample_user.status
        }

        # Retrieve and verify
        retrieved = user_repository.find_by_id(sample_user.user_id)
        assert retrieved.user_id == original_data["user_id"]
        assert retrieved.name == original_data["name"]
        assert retrieved.email == original_data["email"]
        assert retrieved.age == original_data["age"]
        assert retrieved.status == original_data["status"]

    def test_repository_isolation(self):
        """Test that repositories are isolated"""
        repo1 = InMemoryUserRepository()
        repo2 = InMemoryUserRepository()

        # Add user to repo1
        user = User("user_123", "Test", "test@example.com", 25)
        repo1.save(user)

        # Should not be in repo2
        assert repo1.exists_by_id("user_123")
        assert not repo2.exists_by_id("user_123")
        assert repo1.count() == 1
        assert repo2.count() == 0

    def test_error_handling_invalid_user(self, user_repository):
        """Test error handling with invalid user objects"""
        # Try to save None
        with pytest.raises(AttributeError):
            user_repository.save(None)

        # Try to find with None ID
        with pytest.raises(TypeError):
            user_repository.find_by_id(None)

    def test_memory_usage(self, user_repository):
        """Test memory usage with many users"""
        # Create many users to test memory handling
        for i in range(1000):
            user = User(f"user_{i}", f"User {i}", f"user{i}@example.com", 25)
            user_repository.save(user)

        assert user_repository.count() == 1000

        # Verify we can still access all users
        for i in range(1000):
            user_id = f"user_{i}"
            assert user_repository.exists_by_id(user_id)
            user = user_repository.find_by_id(user_id)
            assert user is not None
            assert user.user_id == user_id

    def test_repository_reset(self, user_repository):
        """Test repository reset functionality"""
        # Add some users
        for i in range(5):
            user = User(f"user_{i}", f"User {i}", f"user{i}@example.com", 25)
            user_repository.save(user)

        assert user_repository.count() == 5

        # Manually clear storage (simulating reset)
        user_repository._storage.clear()

        assert user_repository.count() == 0
        for i in range(5):
            assert not user_repository.exists_by_id(f"user_{i}")
