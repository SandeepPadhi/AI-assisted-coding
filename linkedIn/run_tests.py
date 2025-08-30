"""
Test runner for LinkedIn system.

Runs all unit tests and provides a comprehensive test report.
"""

import unittest
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all test modules
from tests.test_entities import (
    TestUser, TestProfile, TestMessage, TestConnection, 
    TestNewsFeedItem, TestNewsFeed
)
from tests.test_repositories import (
    TestInMemoryUserRepository, TestInMemoryProfileRepository,
    TestInMemoryMessageRepository, TestInMemoryConnectionRepository,
    TestInMemoryNewsFeedRepository
)
from tests.test_managers import (
    TestUserManager, TestProfileManager, TestMessageManager,
    TestConnectionManager, TestNewsFeedManager
)
from tests.test_services import (
    TestMockEmailService, TestMockSMSService, TestMockPushNotificationService,
    TestNotificationService
)
from tests.test_orchestrator import TestLinkedInSystem


def run_all_tests():
    """Run all unit tests and return results."""
    print("=" * 80)
    print("LINKEDIN SYSTEM - COMPREHENSIVE UNIT TEST SUITE")
    print("=" * 80)
    print(f"Test execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add entity tests
    print("Loading Entity Tests...")
    entity_tests = [
        TestUser, TestProfile, TestMessage, TestConnection, 
        TestNewsFeedItem, TestNewsFeed
    ]
    for test_class in entity_tests:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    # Add repository tests
    print("Loading Repository Tests...")
    repository_tests = [
        TestInMemoryUserRepository, TestInMemoryProfileRepository,
        TestInMemoryMessageRepository, TestInMemoryConnectionRepository,
        TestInMemoryNewsFeedRepository
    ]
    for test_class in repository_tests:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    # Add manager tests
    print("Loading Manager Tests...")
    manager_tests = [
        TestUserManager, TestProfileManager, TestMessageManager,
        TestConnectionManager, TestNewsFeedManager
    ]
    for test_class in manager_tests:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    # Add service tests
    print("Loading Service Tests...")
    service_tests = [
        TestMockEmailService, TestMockSMSService, TestMockPushNotificationService,
        TestNotificationService
    ]
    for test_class in service_tests:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    # Add orchestrator tests
    print("Loading Orchestrator Tests...")
    orchestrator_tests = [TestLinkedInSystem]
    for test_class in orchestrator_tests:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))

    print(f"Total test classes loaded: {len(entity_tests) + len(repository_tests) + len(manager_tests) + len(service_tests) + len(orchestrator_tests)}")
    print()

    # Run tests
    print("=" * 80)
    print("EXECUTING TESTS")
    print("=" * 80)
    
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)

    # Print summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print()

    # Print detailed results
    if result.failures:
        print("FAILURES:")
        print("-" * 40)
        for test, traceback in result.failures:
            print(f"FAIL: {test}")
            print(traceback)
            print()

    if result.errors:
        print("ERRORS:")
        print("-" * 40)
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(traceback)
            print()

    # Print test coverage summary
    print("=" * 80)
    print("TEST COVERAGE SUMMARY")
    print("=" * 80)
    
    coverage_summary = {
        "Entities": {
            "User": "✓ User creation, validation, and business logic",
            "Profile": "✓ Profile management and updates",
            "Message": "✓ Message posting, updating, and validation",
            "Connection": "✓ Connection status management and validation",
            "NewsFeedItem": "✓ Feed item creation and display",
            "NewsFeed": "✓ Feed management and item aggregation"
        },
        "Repositories": {
            "UserRepository": "✓ CRUD operations with email indexing",
            "ProfileRepository": "✓ Profile storage and retrieval",
            "MessageRepository": "✓ Message storage with author indexing",
            "ConnectionRepository": "✓ Connection management with user indexing",
            "NewsFeedRepository": "✓ Feed storage and item management"
        },
        "Managers": {
            "UserManager": "✓ User business logic and validation",
            "ProfileManager": "✓ Profile business operations",
            "MessageManager": "✓ Message business logic and authorization",
            "ConnectionManager": "✓ Connection business rules and validation",
            "NewsFeedManager": "✓ Feed generation and management"
        },
        "Services": {
            "EmailService": "✓ Email notification functionality",
            "SMSService": "✓ SMS notification functionality",
            "PushNotificationService": "✓ Push notification functionality",
            "NotificationService": "✓ Multi-channel notification coordination"
        },
        "Orchestrator": {
            "LinkedInSystem": "✓ System coordination and high-level operations"
        }
    }

    for category, components in coverage_summary.items():
        print(f"\n{category}:")
        for component, description in components.items():
            print(f"  {component}: {description}")

    print()
    print("=" * 80)
    print("TEST EXECUTION COMPLETE")
    print("=" * 80)
    print(f"Test execution completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return result


def run_specific_test_category(category):
    """Run tests for a specific category."""
    categories = {
        "entities": [TestUser, TestProfile, TestMessage, TestConnection, TestNewsFeedItem, TestNewsFeed],
        "repositories": [TestInMemoryUserRepository, TestInMemoryProfileRepository, TestInMemoryMessageRepository, TestInMemoryConnectionRepository, TestInMemoryNewsFeedRepository],
        "managers": [TestUserManager, TestProfileManager, TestMessageManager, TestConnectionManager, TestNewsFeedManager],
        "services": [TestMockEmailService, TestMockSMSService, TestMockPushNotificationService, TestNotificationService],
        "orchestrator": [TestLinkedInSystem]
    }
    
    if category not in categories:
        print(f"Unknown category: {category}")
        print(f"Available categories: {', '.join(categories.keys())}")
        return
    
    print(f"Running tests for category: {category}")
    test_suite = unittest.TestSuite()
    
    for test_class in categories[category]:
        test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(test_class))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print(f"\nCategory '{category}' test results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific category
        category = sys.argv[1].lower()
        run_specific_test_category(category)
    else:
        # Run all tests
        run_all_tests()
