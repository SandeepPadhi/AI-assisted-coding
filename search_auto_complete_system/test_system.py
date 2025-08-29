#!/usr/bin/env python3
"""
Simple test to verify the Search Auto Complete System works.
"""

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        print("Testing imports...")
        from system_orchestrator import SearchAutoCompleteSystem
        from entities import User, SearchQuery, SearchResult
        from managers import UserManager, SearchQueryManager, SearchResultManager
        from in_memory_repositories import InMemoryUserRepository, InMemorySearchQueryRepository, InMemorySearchResultRepository
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_basic_functionality():
    """Test basic system functionality."""
    try:
        print("Testing basic functionality...")

        # Create system
        from system_orchestrator import SearchAutoCompleteSystem
        system = SearchAutoCompleteSystem()
        print("✓ System initialized")

        # Create a user
        user = system.register_user("test_user", "test@example.com")
        print(f"✓ User created: {user.username}")

        # Test a simple search
        search_query, suggestions = system.search_with_auto_complete("test_user", "python", max_results=2)
        print(f"✓ Search completed: '{search_query.query_text}'")

        if suggestions:
            print(f"✓ Found {len(suggestions)} suggestions")
        else:
            print("✓ No suggestions (expected for new system)")

        # Get statistics
        stats = system.get_system_statistics()
        print(f"✓ Statistics: {stats['total_users']} users, {stats['total_search_queries']} queries")

        return True
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing Search Auto Complete System")
    print("=" * 40)

    success = True

    # Test imports
    if not test_imports():
        success = False

    # Test basic functionality
    if not test_basic_functionality():
        success = False

    if success:
        print("\n🎉 All tests passed! The system is working correctly.")
        print("\nYou can now run:")
        print("• python3 main.py (full interactive system)")
        print("• python3 quick_demo.py (demo without interaction)")
        print("• python3 run_interactive.py (direct interactive mode)")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()
    # There is no code in this file that attempts to open a terminal.
    # If you are referring to running this script and expecting a new terminal window to open,
    # Python scripts do not open a new terminal by themselves; they run in the terminal you invoke them from.
    # If you are running this from an IDE or code editor and not seeing a terminal,
    # check your IDE's settings or try running the script from a system terminal (e.g., Command Prompt, Terminal.app, bash).
    # If you want to launch a new terminal window programmatically, you would need to use OS-specific commands,
    # but that is not standard for test scripts or main entry points in this project