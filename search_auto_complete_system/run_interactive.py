#!/usr/bin/env python3
"""
Standalone interactive mode for Search Auto Complete System.
Run this file directly to start interactive mode without the menu.
"""

from main import load_sample_data, interactive_mode
from system_orchestrator import SearchAutoCompleteSystem

def main():
    """Run interactive mode directly."""
    print("🚀 Search Auto Complete System - Interactive Mode")
    print("=" * 60)

    # Initialize the system
    system = SearchAutoCompleteSystem()
    print("✓ System initialized with in-memory repositories")

    # Load sample data
    load_sample_data(system)

    # Start interactive mode
    interactive_mode(system)

if __name__ == "__main__":
    main()
