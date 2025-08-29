"""
Search Auto Complete System - Main Implementation

This module demonstrates a complete search auto-complete system with the following features:
- User registration and management
- Search query processing with auto-complete suggestions
- Relevance-based result ranking
- Search history tracking
- Manual addition of words/suggestions to the system
- Sample data for demonstration
- System statistics and analytics

The system is built using a modular architecture with:
- Entity classes with business logic and validations
- Abstract repositories for data storage abstraction
- Manager classes for business operations
- System orchestrator for coordinating components
"""

from system_orchestrator import SearchAutoCompleteSystem


def load_sample_data(system: SearchAutoCompleteSystem) -> None:
    """Load sample data into the system for demonstration purposes."""
    print("Loading sample data...")

    # Register sample users
    users = [
        ("alice_dev", "alice@example.com"),
        ("bob_coder", "bob@example.com"),
        ("charlie_tech", "charlie@example.com"),
    ]

    for username, email in users:
        try:
            system.register_user(username, email)
            print(f"✓ Registered user: {username}")
        except Exception as e:
            print(f"✗ Error registering {username}: {e}")

    # Add sample search queries to build auto-complete database
    sample_searches = [
        # Python ecosystem
        ("alice_dev", "python programming tutorial"),
        ("alice_dev", "python data science"),
        ("alice_dev", "python machine learning"),
        ("alice_dev", "python web development"),
        ("alice_dev", "python django framework"),
        ("alice_dev", "python flask microframework"),
        ("alice_dev", "python numpy pandas"),
        ("alice_dev", "python scikit-learn tensorflow"),

        # JavaScript ecosystem
        ("bob_coder", "javascript es6 features"),
        ("bob_coder", "javascript async await"),
        ("bob_coder", "javascript promises"),
        ("bob_coder", "javascript react hooks"),
        ("bob_coder", "javascript vue composition api"),
        ("bob_coder", "javascript typescript integration"),
        ("bob_coder", "javascript node.js express"),
        ("bob_coder", "javascript webpack babel"),

        # Database technologies
        ("charlie_tech", "database mysql optimization"),
        ("charlie_tech", "database postgresql indexing"),
        ("charlie_tech", "database mongodb aggregation"),
        ("charlie_tech", "database redis caching"),
        ("charlie_tech", "database elasticsearch search"),
        ("charlie_tech", "database sqlite embedded"),
        ("charlie_tech", "database cassandra nosql"),
        ("charlie_tech", "database neo4j graph"),

        # Additional diverse queries to showcase algorithm
        ("alice_dev", "REST API development"),
        ("alice_dev", "microservices architecture"),
        ("bob_coder", "responsive web design"),
        ("bob_coder", "progressive web apps"),
        ("charlie_tech", "docker containerization"),
        ("charlie_tech", "kubernetes orchestration"),
    ]

    for username, query in sample_searches:
        try:
            search_query, suggestions = system.search_with_auto_complete(username, query)
            print(f"✓ Added search: '{query}' by {username}")
        except Exception as e:
            print(f"✗ Error adding search '{query}': {e}")

    print("Sample data loaded successfully!")


def demonstrate_user_registration(system: SearchAutoCompleteSystem) -> None:
    """Demonstrate user registration functionality."""
    print("\n=== User Registration Demo ===")

    try:
        # Register a new user
        user = system.register_user("demo_user", "demo@example.com")
        print(f"✓ Registered new user: {user.username} ({user.email})")

        # Try to register duplicate user (should fail)
        try:
            system.register_user("demo_user", "different@example.com")
        except ValueError as e:
            print(f"✓ Expected error for duplicate username: {e}")

    except Exception as e:
        print(f"✗ Error during user registration: {e}")


def demonstrate_search_auto_complete(system: SearchAutoCompleteSystem) -> None:
    """Demonstrate advanced search auto-complete functionality."""
    print("\n=== Advanced Search Auto Complete Demo ===")

    # Test various matching strategies
    test_queries = [
        # 1. EXACT PREFIX MATCHING
        ("alice_dev", "python", "Exact prefix matching"),
        ("alice_dev", "javascript", "Exact prefix matching"),
        ("charlie_tech", "database", "Exact prefix matching"),

        # 2. PARTIAL WORD COMPLETION (e.g., "pyth" -> "python")
        ("alice_dev", "pyth", "Partial word completion"),
        ("alice_dev", "djan", "Partial word completion"),
        ("bob_coder", "javascrip", "Partial word completion (with typo)"),

        # 3. SUBSTRING MATCHING (anywhere in text)
        ("alice_dev", "frame", "Substring matching - find 'framework'"),
        ("bob_coder", "reac", "Substring matching - find 'react'"),
        ("charlie_tech", "mongo", "Substring matching - find 'mongodb'"),

        # 4. WORD-BASED MATCHING
        ("alice_dev", "web dev", "Word-based matching"),
        ("bob_coder", "node express", "Word-based matching"),
        ("charlie_tech", "mysql opt", "Word-based matching"),

        # 5. FUZZY MATCHING & TYPOS
        ("alice_dev", "machin lern", "Fuzzy matching with typos"),
        ("bob_coder", "asyn await", "Fuzzy matching with typos"),
        ("charlie_tech", "cassanra", "Typo tolerance"),

        # 6. MULTI-WORD PHRASES
        ("alice_dev", "rest api", "Multi-word phrase completion"),
        ("bob_coder", "progressive web", "Multi-word phrase completion"),
        ("charlie_tech", "docker cont", "Multi-word phrase completion"),

        # 7. ABBREVIATIONS & ACRONYMS
        ("alice_dev", "ml", "Abbreviation matching"),
        ("bob_coder", "pwa", "Abbreviation matching"),
        ("charlie_tech", "nosql", "Technology acronym"),
    ]

    for username, partial_query, description in test_queries:
        try:
            search_query, suggestions = system.search_with_auto_complete(username, partial_query, max_results=5)
            print(f"\nQuery: '{partial_query}' ({description})")
            if suggestions:
                print(f"✓ Suggestions: {suggestions}")
            else:
                print("✗ No suggestions found")
        except Exception as e:
            print(f"✗ Error getting suggestions for '{partial_query}': {e}")


def demonstrate_adding_words_to_system(system: SearchAutoCompleteSystem) -> None:
    """Demonstrate adding new words/suggestions to the system."""
    print("\n=== Adding Words to System Demo ===")

    try:
        # Get a user's recent search query
        alice_searches = system.get_user_search_history("alice_dev")
        if alice_searches:
            recent_query = alice_searches[0]
            print(f"Adding manual suggestions for query: '{recent_query.query_text}'")

            # Add new words/suggestions manually
            new_suggestions = [
                ("python best practices guide", 0.95),
                ("python code review checklist", 0.90),
                ("python performance optimization", 0.85),
                ("python security guidelines", 0.80),
                ("python testing frameworks", 0.75),
            ]

            for suggestion_text, score in new_suggestions:
                result = system.add_manual_suggestion(recent_query.query_id, suggestion_text, score)
                print(f"✓ Added suggestion: '{suggestion_text}' (relevance: {score})")

            # Test auto-complete with new suggestions
            search_query, suggestions = system.search_with_auto_complete("alice_dev", "python", max_results=8)
            print(f"\nUpdated suggestions for 'python': {suggestions}")

    except Exception as e:
        print(f"✗ Error adding words to system: {e}")


def demonstrate_search_history(system: SearchAutoCompleteSystem) -> None:
    """Demonstrate search history functionality."""
    print("\n=== Search History Demo ===")

    for username in ["alice_dev", "bob_coder", "charlie_tech"]:
        try:
            history = system.get_user_search_history(username)
            print(f"\n{username}'s search history ({len(history)} queries):")
            for i, query in enumerate(history[:3], 1):  # Show top 3
                print(f"  {i}. '{query.query_text}' (frequency: {query.frequency_count})")
        except Exception as e:
            print(f"✗ Error getting history for {username}: {e}")


def demonstrate_popular_searches(system: SearchAutoCompleteSystem) -> None:
    """Demonstrate popular searches functionality."""
    print("\n=== Popular Searches Demo ===")

    try:
        popular_searches = system.get_popular_searches(limit=5)
        print("Top 5 most popular searches across all users:")
        for i, query in enumerate(popular_searches, 1):
            print(f"  {i}. '{query.query_text}' (frequency: {query.frequency_count})")
    except Exception as e:
        print(f"✗ Error getting popular searches: {e}")


def demonstrate_system_statistics(system: SearchAutoCompleteSystem) -> None:
    """Demonstrate system statistics functionality."""
    print("\n=== System Statistics Demo ===")

    try:
        stats = system.get_system_statistics()
        print("System Statistics:")
        print(f"  Total Users: {stats['total_users']}")
        print(f"  Total Search Queries: {stats['total_search_queries']}")
        print(f"  Total Suggestions: {stats['total_suggestions']}")
        print(f"  Average Query Frequency: {stats['average_query_frequency']}")
    except Exception as e:
        print(f"✗ Error getting system statistics: {e}")


def demonstrate_repeated_searches(system: SearchAutoCompleteSystem) -> None:
    """Demonstrate how repeated searches affect frequency and suggestions."""
    print("\n=== Repeated Searches Demo ===")

    try:
        # Perform the same search multiple times
        query_text = "python programming"
        print(f"Performing repeated searches for: '{query_text}'")

        for i in range(3):
            search_query, suggestions = system.search_with_auto_complete("alice_dev", query_text)
            print(f"  Search {i+1}: frequency now {search_query.frequency_count}")

        # Check if it appears in popular searches
        popular_searches = system.get_popular_searches(limit=3)
        print(f"\nTop 3 popular searches after repeated queries:")
        for i, query in enumerate(popular_searches, 1):
            print(f"  {i}. '{query.query_text}' (frequency: {query.frequency_count})")

    except Exception as e:
        print(f"✗ Error with repeated searches: {e}")


def interactive_mode(system: SearchAutoCompleteSystem) -> None:
    """Interactive terminal interface for the search auto-complete system."""
    print("\n🎯 Interactive Search Auto-Complete Mode")
    print("=" * 50)
    print("Type your queries and see intelligent suggestions!")
    print("Commands: 'history' - show search history, 'stats' - show statistics, 'exit' - quit")
    print("-" * 50)

    # Default user for interactive mode
    current_user = "interactive_user"

    # Try to get/create user
    try:
        user = system.get_user_by_username(current_user)
        if not user:
            user = system.register_user(current_user, f"{current_user}@example.com")
            print(f"✓ Created user: {current_user}")
    except Exception as e:
        print(f"Error setting up user: {e}")
        return

    while True:
        try:
            # Get user input
            query = input(f"\n🔍 [{current_user}] Search: ").strip()

            if not query:
                continue

            # Handle special commands
            if query.lower() == 'exit':
                print("👋 Goodbye!")
                break
            elif query.lower() == 'history':
                history = system.get_user_search_history(current_user)
                print(f"\n📚 Your search history ({len(history)} queries):")
                for i, search_query in enumerate(history[:10], 1):
                    print(f"  {i}. '{search_query.query_text}' (searched {search_query.frequency_count} times)")
                continue
            elif query.lower() == 'stats':
                stats = system.get_system_statistics()
                print("\n📊 System Statistics:")
                print(f"  Total Users: {stats['total_users']}")
                print(f"  Total Search Queries: {stats['total_search_queries']}")
                print(f"  Total Suggestions: {stats['total_suggestions']}")
                print(f"  Average Query Frequency: {stats['average_query_frequency']:.2f}")
                continue
            elif query.lower() == 'help':
                print("\n📖 Available Commands:")
                print("  • Type any search query to get suggestions")
                print("  • 'history' - View your search history")
                print("  • 'stats' - View system statistics")
                print("  • 'exit' - Quit interactive mode")
                print("  • 'help' - Show this help message")
                continue

            # Process the search query
            search_query, suggestions = system.search_with_auto_complete(current_user, query, max_results=8)

            # Display results
            if suggestions:
                print(f"💡 Suggestions for '{query}':")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
                print(f"   (Query frequency: {search_query.frequency_count})")
            else:
                print(f"🤔 No suggestions found for '{query}'")
                print("💡 Try: partial words, common typos, or different keywords!")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("💡 Try again or type 'help' for commands")


def main() -> None:
    """Main entry point with mode selection."""
    print("🚀 Search Auto Complete System")
    print("=" * 60)

    # Initialize the system
    system = SearchAutoCompleteSystem()
    print("✓ System initialized with in-memory repositories")

    # Load sample data
    load_sample_data(system)

    while True:
        print("\n" + "=" * 40)
        print("Choose a mode:")
        print("1. 🎬 Run Demo (show all features)")
        print("2. 🎯 Interactive Mode (chat with the system)")
        print("3. ❌ Exit")
        print("=" * 40)

        try:
            choice = input("Enter your choice (1-3): ").strip()

            if choice == '1':
                print("\n🎬 Running Demo Mode...")
                # Run demonstrations
                demonstrate_user_registration(system)
                demonstrate_search_auto_complete(system)
                demonstrate_adding_words_to_system(system)
                demonstrate_search_history(system)
                demonstrate_popular_searches(system)
                demonstrate_repeated_searches(system)
                demonstrate_system_statistics(system)

                print("\n" + "=" * 60)
                print("🎉 Demo completed successfully!")

            elif choice == '2':
                print("\n🎯 Entering Interactive Mode...")
                interactive_mode(system)

            elif choice == '3':
                print("👋 Goodbye!")
                break

            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")

        except KeyboardInterrupt:
            print("\n\n👋 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

    print("\nKey Features Available:")
    print("• Intelligent auto-complete with 7 matching algorithms")
    print("• Typo tolerance and fuzzy matching")
    print("• Multi-word phrase completion")
    print("• Search history and frequency tracking")
    print("• Real-time suggestions as you type")
    print("• Comprehensive analytics and statistics")


if __name__ == "__main__":
    main()