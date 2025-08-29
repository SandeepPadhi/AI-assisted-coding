#!/usr/bin/env python3
"""Minimal test to debug pytest issues"""

import sys
sys.path.insert(0, '.')

from entities import User
import pytest

class TestMinimal:
    """Minimal test class"""

    def test_user_empty_id(self):
        """Test that empty user ID raises ValueError"""
        print("Testing empty user ID validation...")

        # This should raise ValueError
        with pytest.raises(ValueError) as exc_info:
            User("", "John Doe", "john@example.com", 30)

        print(f"Exception raised: {exc_info.value}")
        assert "User ID must be a non-empty string" in str(exc_info.value)
        print("✅ Test passed!")

if __name__ == "__main__":
    test = TestMinimal()
    test.test_user_empty_id()
