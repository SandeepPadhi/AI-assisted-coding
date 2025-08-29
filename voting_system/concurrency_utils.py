"""
Concurrency Utilities for Voting System

This module provides comprehensive concurrency handling utilities
for the voting system including thread safety, request queuing,
rate limiting, and deadlock prevention.
"""

import threading
import time
import queue
from typing import Any, Callable, Optional, Dict, List
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Request:
    """Represents a queued request"""
    def __init__(self, request_id: str, operation: Callable, args: tuple,
                 kwargs: dict, timestamp: datetime, priority: int = 1):
        self.request_id = request_id
        self.operation = operation
        self.args = args
        self.kwargs = kwargs
        self.timestamp = timestamp
        self.priority = priority

    def __lt__(self, other):
        """Less than comparison for PriorityQueue"""
        if not isinstance(other, Request):
            return NotImplemented
        # Higher priority (lower number) comes first
        # If priorities are equal, use timestamp (FIFO)
        if self.priority != other.priority:
            return self.priority < other.priority
        return self.timestamp < other.timestamp

    def __str__(self):
        return f"Request(id={self.request_id}, priority={self.priority})"


class RateLimiter:
    """Rate limiter using token bucket algorithm"""

    def __init__(self, rate_per_second: float, burst_size: int = 10):
        """Initialize rate limiter"""
        self.rate_per_second = rate_per_second
        self.burst_size = burst_size
        self.tokens = burst_size
        self.last_update = time.time()
        self.lock = threading.Lock()

    def acquire(self, tokens: int = 1) -> bool:
        """Try to acquire tokens"""
        with self.lock:
            now = time.time()
            time_passed = now - self.last_update
            self.tokens = min(self.burst_size,
                            self.tokens + time_passed * self.rate_per_second)
            self.last_update = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def wait_for_tokens(self, tokens: int = 1, timeout: float = 1.0) -> bool:
        """Wait for tokens to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.acquire(tokens):
                return True
            time.sleep(0.01)  # Small sleep to prevent busy waiting
        return False


class RequestQueue:
    """Thread-safe request queue with priority support"""

    def __init__(self, max_size: int = 1000):
        """Initialize request queue"""
        self.queue = queue.PriorityQueue(maxsize=max_size)
        self.request_counter = 0
        self.lock = threading.Lock()

    def add_request(self, operation: Callable, args: tuple = (),
                   kwargs: dict = None, priority: int = 1) -> str:
        """Add a request to the queue"""
        if kwargs is None:
            kwargs = {}

        with self.lock:
            self.request_counter += 1
            request_id = f"req_{self.request_counter}"

            request = Request(
                request_id=request_id,
                operation=operation,
                args=args,
                kwargs=kwargs,
                timestamp=datetime.now(),
                priority=priority
            )

            # Put the request directly (Request class now handles priority comparison)
            self.queue.put(request)
            logger.info(f"Queued request {request_id} with priority {priority}")
            return request_id

    def get_request(self, timeout: float = 1.0) -> Optional[Request]:
        """Get next request from queue"""
        try:
            request = self.queue.get(timeout=timeout)
            logger.info(f"Retrieved request {request.request_id}")
            return request
        except queue.Empty:
            return None

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return self.queue.qsize()

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return self.queue.empty()

    def clear(self) -> None:
        """Clear all requests from queue"""
        with self.lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except queue.Empty:
                    break


class WorkerPool:
    """Pool of worker threads for processing requests"""

    def __init__(self, num_workers: int = 4, request_queue: Optional[RequestQueue] = None):
        """Initialize worker pool"""
        self.num_workers = num_workers
        self.request_queue = request_queue or RequestQueue()
        self.workers: List[threading.Thread] = []
        self.active = False
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()

    def start(self) -> None:
        """Start the worker pool"""
        with self.lock:
            if self.active:
                return

            self.active = True
            self.shutdown_event.clear()

            for i in range(self.num_workers):
                worker = threading.Thread(
                    target=self._worker_loop,
                    name=f"Worker-{i+1}",
                    daemon=True
                )
                worker.start()
                self.workers.append(worker)

            logger.info(f"Started worker pool with {self.num_workers} workers")

    def stop(self) -> None:
        """Stop the worker pool"""
        with self.lock:
            if not self.active:
                return

            self.active = False
            self.shutdown_event.set()

            # Wait for workers to finish
            for worker in self.workers:
                worker.join(timeout=5.0)

            self.workers.clear()
            logger.info("Stopped worker pool")

    def submit_request(self, operation: Callable, args: tuple = (),
                      kwargs: dict = None, priority: int = 1) -> str:
        """Submit a request for processing"""
        return self.request_queue.add_request(operation, args, kwargs, priority)

    def _worker_loop(self) -> None:
        """Main worker loop"""
        logger.info(f"Worker {threading.current_thread().name} started")

        while not self.shutdown_event.is_set():
            try:
                request = self.request_queue.get_request(timeout=0.5)
                if request:
                    self._process_request(request)
            except Exception as e:
                logger.error(f"Worker error: {e}")

        logger.info(f"Worker {threading.current_thread().name} stopped")

    def _process_request(self, request: Request) -> None:
        """Process a single request"""
        try:
            logger.info(f"Processing request {request.request_id}")
            start_time = time.time()

            # Execute the operation
            result = request.operation(*request.args, **request.kwargs)

            processing_time = time.time() - start_time
            logger.info(f"Completed request {request.request_id} in {processing_time:.3f}s")

        except Exception as e:
            logger.error(f"Error processing request {request.request_id}: {e}")


class ResourceLockManager:
    """Manager for preventing deadlocks with resource locks"""

    def __init__(self):
        """Initialize lock manager"""
        self.locks: Dict[str, threading.Lock] = {}
        self.lock_order: Dict[str, int] = {}  # Resource -> order number
        self.lock = threading.Lock()

    def acquire_locks(self, resource_ids: List[str], timeout: float = 5.0) -> bool:
        """Acquire multiple locks in order to prevent deadlocks"""
        if not resource_ids:
            return True

        # Sort resources by their predefined order
        sorted_resources = sorted(resource_ids, key=lambda x: self._get_resource_order(x))

        acquired_locks = []
        start_time = time.time()

        try:
            for resource_id in sorted_resources:
                if time.time() - start_time > timeout:
                    break

                lock = self._get_lock(resource_id)
                if lock.acquire(timeout=max(0.1, timeout - (time.time() - start_time))):
                    acquired_locks.append(lock)
                else:
                    break

            # If we couldn't acquire all locks, release the ones we got
            if len(acquired_locks) != len(sorted_resources):
                for lock in acquired_locks:
                    lock.release()
                return False

            return True

        except Exception:
            # Release any locks we acquired
            for lock in acquired_locks:
                try:
                    lock.release()
                except:
                    pass
            return False

    def release_locks(self, resource_ids: List[str]) -> None:
        """Release multiple locks"""
        for resource_id in resource_ids:
            lock = self.locks.get(resource_id)
            if lock:
                try:
                    lock.release()
                except RuntimeError:
                    # Lock not owned by this thread
                    pass

    def set_resource_order(self, resource_id: str, order: int) -> None:
        """Set the lock order for a resource"""
        with self.lock:
            self.lock_order[resource_id] = order

    def _get_resource_order(self, resource_id: str) -> int:
        """Get the lock order for a resource"""
        return self.lock_order.get(resource_id, 0)

    def _get_lock(self, resource_id: str) -> threading.Lock:
        """Get or create a lock for a resource"""
        with self.lock:
            if resource_id not in self.locks:
                self.locks[resource_id] = threading.RLock()  # Reentrant lock
            return self.locks[resource_id]


@contextmanager
def acquire_resources(lock_manager: ResourceLockManager, resource_ids: List[str],
                     timeout: float = 5.0):
    """Context manager for acquiring multiple resources safely"""
    if lock_manager.acquire_locks(resource_ids, timeout):
        try:
            yield
        finally:
            lock_manager.release_locks(resource_ids)
    else:
        raise TimeoutError(f"Could not acquire locks for resources: {resource_ids}")


class ConcurrencyManager:
    """Central manager for all concurrency-related functionality"""

    def __init__(self, num_workers: int = 4, rate_limit: float = 10.0):
        """Initialize concurrency manager"""
        self.request_queue = RequestQueue()
        self.worker_pool = WorkerPool(num_workers, self.request_queue)
        self.rate_limiter = RateLimiter(rate_limit)
        self.lock_manager = ResourceLockManager()
        self.lock = threading.Lock()

        # Set up resource lock ordering to prevent deadlocks
        self._setup_resource_ordering()

    def start(self) -> None:
        """Start the concurrency system"""
        with self.lock:
            self.worker_pool.start()
            logger.info("Concurrency system started")

    def stop(self) -> None:
        """Stop the concurrency system"""
        with self.lock:
            self.worker_pool.stop()
            self.request_queue.clear()
            logger.info("Concurrency system stopped")

    def submit_operation(self, operation: Callable, args: tuple = (),
                        kwargs: dict = None, priority: int = 1,
                        rate_limited: bool = True) -> str:
        """Submit an operation for concurrent execution"""
        if kwargs is None:
            kwargs = {}

        # Apply rate limiting if requested
        if rate_limited and not self.rate_limiter.acquire():
            raise RuntimeError("Rate limit exceeded")

        # Submit to worker pool
        return self.worker_pool.submit_request(operation, args, kwargs, priority)

    def execute_with_resources(self, operation: Callable, resource_ids: List[str],
                              args: tuple = (), kwargs: dict = None,
                              timeout: float = 5.0) -> Any:
        """Execute operation with resource locking"""
        if kwargs is None:
            kwargs = {}

        with acquire_resources(self.lock_manager, resource_ids, timeout):
            return operation(*args, **kwargs)

    def get_system_status(self) -> Dict[str, Any]:
        """Get concurrency system status"""
        return {
            "active": self.worker_pool.active,
            "queue_size": self.request_queue.get_queue_size(),
            "num_workers": self.worker_pool.num_workers,
            "rate_limiter_tokens": self.rate_limiter.tokens,
            "active_locks": len(self.lock_manager.locks)
        }

    def _setup_resource_ordering(self) -> None:
        """Set up resource lock ordering to prevent deadlocks"""
        # Define lock order for different resource types
        resource_order = {
            # User resources
            "user": 1,
            "user_repository": 1,

            # Candidate resources
            "candidate": 2,
            "candidate_repository": 2,

            # Election resources
            "election": 3,
            "election_repository": 3,

            # Vote resources
            "vote": 4,
            "vote_repository": 4,
            "voting_record": 4,

            # Result resources
            "result": 5,
            "result_repository": 5,

            # Infrastructure resources
            "booth": 6,
            "booth_repository": 6,
            "machine": 7,
            "machine_repository": 7,

            # System resources
            "system": 8,
            "system_repository": 8
        }

        for resource, order in resource_order.items():
            self.lock_manager.set_resource_order(resource, order)


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 60.0):
        """Initialize circuit breaker"""
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self.lock = threading.Lock()

    def call(self, operation: Callable, *args, **kwargs) -> Any:
        """Execute operation with circuit breaker protection"""
        with self.lock:
            if self.state == "OPEN":
                if self._should_attempt_reset():
                    self.state = "HALF_OPEN"
                else:
                    raise RuntimeError("Circuit breaker is OPEN")

            try:
                result = operation(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise e

    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit"""
        if self.last_failure_time is None:
            return True

        time_since_failure = time.time() - self.last_failure_time
        return time_since_failure >= self.recovery_timeout

    def _on_success(self) -> None:
        """Handle successful operation"""
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            self.failure_count = 0
            logger.info("Circuit breaker reset to CLOSED state")

    def _on_failure(self) -> None:
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")

    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status"""
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time
        }


# Global concurrency manager instance
_global_concurrency_manager: Optional[ConcurrencyManager] = None
_concurrency_lock = threading.Lock()


def get_concurrency_manager() -> ConcurrencyManager:
    """Get the global concurrency manager instance"""
    global _global_concurrency_manager

    if _global_concurrency_manager is None:
        with _concurrency_lock:
            if _global_concurrency_manager is None:
                _global_concurrency_manager = ConcurrencyManager()

    return _global_concurrency_manager


def initialize_concurrency_system(num_workers: int = 4, rate_limit: float = 10.0) -> ConcurrencyManager:
    """Initialize the global concurrency system"""
    global _global_concurrency_manager

    with _concurrency_lock:
        if _global_concurrency_manager is not None:
            _global_concurrency_manager.stop()

        _global_concurrency_manager = ConcurrencyManager(num_workers, rate_limit)
        _global_concurrency_manager.start()

        logger.info("Global concurrency system initialized")
        return _global_concurrency_manager
