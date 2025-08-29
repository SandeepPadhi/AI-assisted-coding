#!/usr/bin/env python3
"""
Quick demo of the Search Auto Complete System.
Shows the intelligent matching capabilities without user interaction.
"""

from system_orchestrator import SearchAutoCompleteSystem
from main import load_sample_data

def demo_auto_complete(system):
    """Demonstrate the auto-complete capabilities."""
    print("\n🎯 Search Auto Complete Demo")
    print("=" * 40)

    test_queries = [
        ("pyth", "Partial word completion"),
        ("frame", "Substring matching anywhere"),
        ("react", "Word within text"),
        ("mongo", "Technology name"),
        ("web dev", "Multi-word phrase"),
        ("javascrip", "Typo tolerance"),
        ("machin lern", "Multiple typos"),
        ("docker cont", "Abbreviation + word"),
    ]

    for query, description in test_queries:
        print(f"\n🔍 Query: '{query}' ({description})")
        try:
            search_query, suggestions = system.search_with_auto_complete("demo_user", query, max_results=3)
            if suggestions:
                print("💡 Suggestions:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")
            else:
                print("   No suggestions found")
        except Exception as e:
            print(f"   Error: {e}")

def main():
    """Run a quick demonstration."""
    print("🚀 Search Auto Complete System - Quick Demo")
    print("=" * 60)

    # Initialize system
    system = SearchAutoCompleteSystem()
    print("✓ System initialized")

    # Load sample data
    load_sample_data(system)
    print("✓ Sample data loaded")

    # Run demo
    demo_auto_complete(system)

    # Show some statistics
    stats = system.get_system_statistics()
    print("\n📊 Final Statistics:")
    print(f"   Total Users: {stats['total_users']}")
    print(f"   Total Queries: {stats['total_search_queries']}")
    print(f"   Total Suggestions: {stats['total_suggestions']}")
    print(f"   Average Query Frequency: {stats['average_query_frequency']:.2f}")
    print("\n🎉 Demo completed! The system is ready for interactive use.")
if __name__ == "__main__":
    main()
