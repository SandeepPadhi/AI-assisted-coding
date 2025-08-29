"""
Unit tests for User entity.

Tests cover:
- User creation and validation
- Property access and modification
- Status management
- Business logic validation
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta
from entities import User, UserStatus


class TestUserEntity:
    """Test cases for User entity"""

    def test_user_creation_valid_data(self, sample_user_data):
        """Test successful user creation with valid data"""
        user = User(**sample_user_data)

        assert user.user_id == sample_user_data["user_id"]
        assert user.name == sample_user_data["name"]
        assert user.email == sample_user_data["email"]
        assert user.age == sample_user_data["age"]
        assert user.status == UserStatus.ACTIVE
        assert user.registration_date is not None
        assert isinstance(user.has_voted_in_election, dict)

    def test_user_creation_invalid_user_id(self):
        """Test user creation with invalid user ID"""
        with pytest.raises(ValueError, match="User ID must be a non-empty string"):
            User("", "John Doe", "john@example.com", 30)

        with pytest.raises(ValueError, match="User ID must be a non-empty string"):
            User("   ", "John Doe", "john@example.com", 30)

    def test_user_creation_invalid_name(self):
        """Test user creation with invalid name"""
        with pytest.raises(ValueError, match="Name must be at least 2 characters long"):
            User("user_123", "", "john@example.com", 30)

        with pytest.raises(ValueError, match="Name must be at least 2 characters long"):
            User("user_123", "   ", "john@example.com", 30)

        with pytest.raises(ValueError, match="Name must be at least 2 characters long"):
            User("user_123", "J", "john@example.com", 30)  # Too short

    def test_user_creation_invalid_email(self):
        """Test user creation with invalid email"""
        with pytest.raises(ValueError, match="Valid email address is required"):
            User("user_123", "John Doe", "", 30)

        with pytest.raises(ValueError, match="Valid email address is required"):
            User("user_123", "John Doe", "invalid-email", 30)

        with pytest.raises(ValueError, match="Valid email address is required"):
            User("user_123", "John Doe", "john@", 30)

    def test_user_creation_invalid_age(self):
        """Test user creation with invalid age"""
        with pytest.raises(ValueError, match="User must be at least 18 years old"):
            User("user_123", "John Doe", "john@example.com", 17)  # Under 18

        with pytest.raises(ValueError, match="User must be at least 18 years old"):
            User("user_123", "John Doe", "john@example.com", 0)

        with pytest.raises(ValueError, match="User must be at least 18 years old"):
            User("user_123", "John Doe", "john@example.com", -5)

    def test_user_property_access(self, sample_user):
        """Test user property access"""
        assert sample_user.user_id == "user_123"
        assert sample_user.name == "John Doe"
        assert sample_user.email == "john.doe@example.com"
        assert sample_user.age == 30
        assert sample_user.status == UserStatus.ACTIVE

    def test_user_status_update_valid(self, sample_user):
        """Test valid user status updates"""
        assert sample_user.status == UserStatus.ACTIVE

        # Update to inactive
        sample_user.update_status(UserStatus.INACTIVE)
        assert sample_user.status == UserStatus.INACTIVE

        # Update to suspended
        sample_user.update_status(UserStatus.SUSPENDED)
        assert sample_user.status == UserStatus.SUSPENDED

        # Update back to active
        sample_user.update_status(UserStatus.ACTIVE)
        assert sample_user.status == UserStatus.ACTIVE

    def test_user_status_update_invalid(self, sample_user):
        """Test invalid user status updates"""
        with pytest.raises(ValueError, match="Invalid user status"):
            sample_user.update_status("invalid_status")

        with pytest.raises(ValueError, match="Invalid user status"):
            sample_user.update_status(None)

    def test_user_validation_method(self, sample_user):
        """Test user validation method"""
        # Should not raise for valid user
        sample_user.validate()

        # Test validation with invalid data
        sample_user._name = ""
        with pytest.raises(ValueError):
            sample_user.validate()

    def test_user_string_representation(self, sample_user):
        """Test user string representation"""
        expected = f"User(id={sample_user.user_id}, name={sample_user.name}, status={sample_user.status.value})"
        assert str(sample_user) == expected
        assert repr(sample_user) == expected

    def test_user_equality(self, sample_user_data):
        """Test user equality comparison"""
        user1 = User(**sample_user_data)
        user2 = User(**sample_user_data)
        user3 = User("different_id", "Different Name", "different@example.com", 25)

        assert user1 == user2
        assert user1 != user3
        assert user1 != "not_a_user"

    def test_user_hash(self, sample_user_data):
        """Test user hash function"""
        user1 = User(**sample_user_data)
        user2 = User(**sample_user_data)

        assert hash(user1) == hash(user2)
        assert hash(user1) == hash(sample_user_data["user_id"])

    def test_user_registration_date(self, sample_user):
        """Test user registration date"""
        assert sample_user.registration_date is not None
        assert isinstance(sample_user.registration_date, datetime)

    def test_user_age_boundary_cases(self):
        """Test user age boundary cases"""
        # Exactly 18 should be valid
        user = User("user_18", "Eighteen", "eighteen@example.com", 18)
        assert user.age == 18

        # Exactly 150 should be valid
        user = User("user_150", "OneFifty", "onefifty@example.com", 150)
        assert user.age == 150

    def test_user_email_case_insensitive(self):
        """Test that email is stored as provided (case sensitivity)"""
        user1 = User("user1", "Test", "TEST@EXAMPLE.COM", 25)
        user2 = User("user2", "Test", "test@example.com", 25)

        assert user1.email == "TEST@EXAMPLE.COM"
        assert user2.email == "test@example.com"
        assert user1.email != user2.email

    def test_user_name_normalization(self):
        """Test user name handling with various formats"""
        # Test with extra spaces
        user = User("user1", "  John   Doe  ", "john@example.com", 30)
        assert user.name == "  John   Doe  "  # Should preserve original format

        # Test with special characters that should be allowed
        user = User("user2", "José María", "jose@example.com", 30)
        assert user.name == "José María"

        user = User("user3", "O'Connor", "oconnor@example.com", 30)
        assert user.name == "O'Connor"
