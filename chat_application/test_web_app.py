#!/usr/bin/env python3
"""
Simple test script to verify the web application functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from main import ChatApplication
        from web_app import app, chat_app
        from uuid import UUID
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_chat_app():
    """Test basic ChatApplication functionality"""
    try:
        from main import ChatApplication
        chat_app = ChatApplication()

        # Create test users
        user1 = chat_app.create_user("testuser1")
        user2 = chat_app.create_user("testuser2")

        # Test get_user_by_id
        retrieved_user = chat_app.get_user_by_id(user1.user_id)
        assert retrieved_user is not None
        assert retrieved_user.username == "testuser1"
        print("✅ ChatApplication basic functionality works")

        # Test message sending
        message = chat_app.send_message(user1.user_id, user2.user_id, "Test message")
        assert message.content == "Test message"
        print("✅ Message sending works")

        # Test message history
        messages = chat_app.get_message_history(user1.user_id, user2.user_id)
        assert len(messages) == 1
        print("✅ Message history works")

        return True
    except Exception as e:
        print(f"❌ ChatApplication test failed: {e}")
        return False

def test_uuid_conversion():
    """Test UUID conversion functionality"""
    try:
        from uuid import UUID

        # Test string to UUID conversion
        test_uuid_str = "12345678-1234-5678-9012-123456789012"
        test_uuid = UUID(test_uuid_str)
        assert str(test_uuid) == test_uuid_str
        print("✅ UUID conversion works")

        return True
    except Exception as e:
        print(f"❌ UUID conversion test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Chat Application Web Interface")
    print("=" * 50)

    tests = [
        ("Import Test", test_imports),
        ("Chat App Test", test_chat_app),
        ("UUID Conversion Test", test_uuid_conversion)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The web application should work correctly.")
        print("\n🚀 To start the web application:")
        print("   source venv/bin/activate")
        print("   python3 web_app.py")
        print("   Open http://localhost:5000 in your browser")
    else:
        print("❌ Some tests failed. Please check the errors above.")

    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
