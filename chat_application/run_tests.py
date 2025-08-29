#!/usr/bin/env python3
"""
Test runner for Chat Application
Provides a clean interface to run all tests with summary
"""

import unittest
import sys
from datetime import datetime

def run_tests():
    """Run all tests and provide a summary"""
    print("=" * 60)
    print("CHAT APPLICATION TEST SUITE")
    print("=" * 60)
    print(f"Test run started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Discover and run tests
    loader = unittest.TestLoader()
    start_dir = '.'
    suite = loader.discover(start_dir, pattern='tests.py')

    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Total tests run: {result.testsRun}")
    print(f"Tests passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests failed: {len(result.failures)}")
    print(f"Tests with errors: {len(result.errors)}")

    if result.failures:
        print(f"\nFAILED TESTS ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")

    if result.errors:
        print(f"\nERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")

    print(f"\nTest run completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(run_tests())
