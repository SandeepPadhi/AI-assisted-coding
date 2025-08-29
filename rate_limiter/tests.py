import unittest
import time
import functools
from typing import Callable, Any
from datetime import datetime

def print_test_info(func: Callable) -> Callable:
    """Decorator to print information about test execution"""
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        test_name = func.__name__.replace('test_', '').replace('_', ' ').title()
        print(f"\n{'='*80}")
        print(f"Running Test: {test_name}")
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")
        
        try:
            result = func(*args, **kwargs)
            print(f"\n✅ Test Passed: {test_name}")
            return result
        except Exception as e:
            print(f"\n❌ Test Failed: {test_name}")
            print(f"Error: {str(e)}")
            raise
        finally:
            print(f"{'='*80}\n")
    
    return wrapper

from main import (
    User, Request, RateLimitResult, FixedWindowRateLimiter,
    InMemoryRateLimiterRepository, RateLimiterManager, RateLimiterSystem
)

class TestRateLimiterEntities(unittest.TestCase):
    @print_test_info
    def test_user_creation(self):
        user = User(user_id="test_id", name="Test User")
        self.assertEqual(user.user_id, "test_id")
        self.assertEqual(user.name, "Test User")

    @print_test_info
    def test_request_creation(self):
        request = Request(request_id="req_1", user_id="user_1", timestamp=123.45)
        self.assertEqual(request.request_id, "req_1")
        self.assertEqual(request.user_id, "user_1")
        self.assertEqual(request.timestamp, 123.45)

    @print_test_info
    def test_rate_limit_result(self):
        result1 = RateLimitResult(is_allowed=True)
        self.assertTrue(result1.is_allowed)
        self.assertEqual(result1.wait_time, 0)

        result2 = RateLimitResult(is_allowed=False, wait_time=1.5)
        self.assertFalse(result2.is_allowed)
        self.assertEqual(result2.wait_time, 1.5)

class TestFixedWindowRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = FixedWindowRateLimiter(requests_per_second=2)

    @print_test_info
    def test_within_limit(self):
        result1 = self.limiter.is_allowed("user1")
        self.assertTrue(result1.is_allowed)
        result2 = self.limiter.is_allowed("user1")
        self.assertTrue(result2.is_allowed)

    @print_test_info
    def test_exceeds_limit(self):
        # First two requests should be allowed
        self.limiter.is_allowed("user1")
        self.limiter.is_allowed("user1")
        # Third request should be denied
        result = self.limiter.is_allowed("user1")
        self.assertFalse(result.is_allowed)
        self.assertGreater(result.wait_time, 0)

    @print_test_info
    def test_different_users(self):
        # Both users should be allowed their first requests
        result1 = self.limiter.is_allowed("user1")
        result2 = self.limiter.is_allowed("user2")
        self.assertTrue(result1.is_allowed)
        self.assertTrue(result2.is_allowed)

    @print_test_info
    def test_window_reset(self):
        # Make two requests
        self.limiter.is_allowed("user1")
        self.limiter.is_allowed("user1")
        # Wait for window to reset
        time.sleep(1.1)
        # Should be allowed again
        result = self.limiter.is_allowed("user1")
        self.assertTrue(result.is_allowed)

    @print_test_info
    def test_custom_request_limit(self):
        limiter = FixedWindowRateLimiter(requests_per_second=3)
        # All three requests should be allowed
        self.assertTrue(limiter.is_allowed("user1").is_allowed)
        self.assertTrue(limiter.is_allowed("user1").is_allowed)
        self.assertTrue(limiter.is_allowed("user1").is_allowed)
        # Fourth request should be denied
        self.assertFalse(limiter.is_allowed("user1").is_allowed)

class TestInMemoryRepository(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRateLimiterRepository()
        self.test_user = User(user_id="test_id", name="Test User")

    @print_test_info
    def test_save_and_get_user(self):
        self.repo.save_user(self.test_user)
        retrieved_user = self.repo.get_user("test_id")
        self.assertEqual(retrieved_user.user_id, self.test_user.user_id)
        self.assertEqual(retrieved_user.name, self.test_user.name)

    @print_test_info
    def test_get_nonexistent_user(self):
        self.assertIsNone(self.repo.get_user("nonexistent"))

    @print_test_info
    def test_save_and_get_requests(self):
        request = Request(request_id="req_1", user_id="test_id", timestamp=time.time())
        self.repo.save_request(request)
        requests = self.repo.get_user_requests("test_id")
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].request_id, "req_1")

    @print_test_info
    def test_get_requests_empty_user(self):
        requests = self.repo.get_user_requests("nonexistent")
        self.assertEqual(len(requests), 0)

class TestRateLimiterManager(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryRateLimiterRepository()
        self.algorithm = FixedWindowRateLimiter(requests_per_second=2)
        self.manager = RateLimiterManager(self.repo, self.algorithm)
        self.test_user = User(user_id="test_id", name="Test User")

    @print_test_info
    def test_register_user(self):
        self.manager.register_user(self.test_user)
        retrieved_user = self.repo.get_user("test_id")
        self.assertEqual(retrieved_user.user_id, self.test_user.user_id)

    @print_test_info
    def test_process_request_unregistered_user(self):
        with self.assertRaises(ValueError):
            self.manager.process_request("nonexistent")

    @print_test_info
    def test_process_request_success(self):
        self.manager.register_user(self.test_user)
        result = self.manager.process_request("test_id")
        self.assertTrue(result.is_allowed)
        requests = self.repo.get_user_requests("test_id")
        self.assertEqual(len(requests), 1)

class TestRateLimiterSystem(unittest.TestCase):
    def setUp(self):
        self.system = RateLimiterSystem(requests_per_second=2)

    @print_test_info
    def test_system_integration(self):
        # Register user
        self.system.register_user("test_id", "Test User")
        
        # First two requests should be allowed
        result1 = self.system.make_request("test_id")
        result2 = self.system.make_request("test_id")
        self.assertTrue(result1.is_allowed)
        self.assertTrue(result2.is_allowed)
        
        # Third request should be denied
        result3 = self.system.make_request("test_id")
        self.assertFalse(result3.is_allowed)

    @print_test_info
    def test_system_with_different_limits(self):
        system = RateLimiterSystem(requests_per_second=3)
        system.register_user("test_id", "Test User")
        
        # First three requests should be allowed
        self.assertTrue(system.make_request("test_id").is_allowed)
        self.assertTrue(system.make_request("test_id").is_allowed)
        self.assertTrue(system.make_request("test_id").is_allowed)
        
        # Fourth request should be denied
        self.assertFalse(system.make_request("test_id").is_allowed)

    @print_test_info
    def test_unregistered_user(self):
        with self.assertRaises(ValueError):
            self.system.make_request("nonexistent")

if __name__ == '__main__':
    unittest.main()