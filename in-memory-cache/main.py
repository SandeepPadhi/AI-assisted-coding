"""
Goal:
- Create a in-memory cache system with the following features:
    - Cache can store key-value pairs
    - Cache can store different types of data
    - Cache can store data for a certain amount of time
    - cache should take care of the eviction policy
    - cache should be thread safe
    - cache should take ttl as input and evict the data after the ttl

Non-Functional Requirements:
- The system should be able to handle 1000 requests per second
- The system should be able to scale to 1000000 requests per second


Entities:
# CacheEntry represents a single item stored in the cache.
# It holds the cached value, the time it was inserted, and the time-to-live (TTL) for expiration.
# This allows the cache to determine when an entry should be evicted based on its TTL.
- Cache

Repositories:
- AbstractCacheRepository
- InMemoryCacheRepository

Managers:
- CacheManager

SystemOrchestrator:
- CacheSystem


Design guidelines:
- Use good naming conventions
- Divide the code into entities, entity managers, repositories, system orchestrator, and external services as needed
- Use correct abstractions for future extensions
- Implement the repository in-memory, but design it so it can be extended to other storage systems
- do not sure any external libraries.
- Write the code in a way that it is easy to understand and easy to maintain.
- Keep the code modular and short which satisfies the requirements. and single responsibility principle.
- Respository function names should be self-explanatory.
- YOu can use repository class to store different entities and then extend it to in-memory or other storage systems.
- Do not use generics for now but create different abstractions for different entities.
- Each entity should be able to handle its invariants and validations and business logic.
- Use type hints for all functions and variables.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from time import time
from threading import Lock, Thread, Event
from typing import Any, Dict, Optional, List, Tuple
import time

@dataclass
class TimedCacheEntry:
    """
    Represents a single item in the cache with its metadata and expiration logic.
    
    Attributes:
        key: Unique identifier for the cache entry
        value: The actual data being cached
        creation_timestamp: Unix timestamp when the entry was created
        time_to_live_seconds: How long the entry should live in seconds
    
    Invariants:
        - key must not be empty
        - time_to_live_seconds must be positive
        - creation_timestamp must not be in the future
    """
    key: str
    value: Any
    creation_timestamp: float
    time_to_live_seconds: int

    def __post_init__(self):
        """Validate invariants after initialization."""
        if not self.key or not self.key.strip():
            raise ValueError("Cache key cannot be empty or whitespace")
        
        if self.time_to_live_seconds <= 0:
            raise ValueError("Time to live must be positive")
        
        current_time = time()
        if self.creation_timestamp > current_time:
            raise ValueError("Creation timestamp cannot be in the future")

    def is_expired(self, current_time: Optional[float] = None) -> bool:
        """
        Check if the cache entry has expired.
        
        Args:
            current_time: Optional current timestamp for testing purposes
            
        Returns:
            bool: True if the entry has expired, False otherwise
        """
        check_time = current_time if current_time is not None else time()
        return check_time > self.creation_timestamp + self.time_to_live_seconds
        
    def get_expiration_timestamp(self) -> float:
        """Get the timestamp when this entry will expire."""
        return self.creation_timestamp + self.time_to_live_seconds
        
    def get_remaining_ttl(self, current_time: Optional[float] = None) -> float:
        """
        Get remaining time to live in seconds.
        
        Args:
            current_time: Optional current timestamp for testing purposes
            
        Returns:
            float: Remaining seconds until expiration. 0 if already expired.
        """
        check_time = current_time if current_time is not None else time()
        remaining = self.get_expiration_timestamp() - check_time
        return max(0.0, remaining)

class AbstractCacheRepository(ABC):
    """Abstract base class defining the contract for cache storage implementations."""
    
    @abstractmethod
    def retrieve_cached_value(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache if it exists and hasn't expired.
        
        Args:
            key: The unique identifier for the cached value
            
        Returns:
            The cached value if found and not expired, None otherwise
        """
        pass
    
    @abstractmethod
    def store_with_expiration(self, key: str, value: Any, time_to_live_seconds: int) -> None:
        """
        Store a value in the cache with an expiration time.
        
        Args:
            key: Unique identifier for the value
            value: The data to cache
            time_to_live_seconds: Number of seconds before the value expires
            
        Raises:
            ValueError: If time_to_live_seconds is not positive or key is invalid
        """
        pass
    
    @abstractmethod
    def remove_cached_value(self, key: str) -> bool:
        """
        Remove a specific value from the cache.
        
        Args:
            key: The unique identifier of the value to remove
            
        Returns:
            bool: True if the value was found and removed, False if not found
        """
        pass
    
    @abstractmethod
    def remove_all_values(self) -> None:
        """Remove all values from the cache, regardless of their expiration status."""
        pass
    
    @abstractmethod
    def get_all_unexpired_entries(self) -> List[TimedCacheEntry]:
        """
        Retrieve all cache entries that haven't expired.
        
        Returns:
            List of all non-expired cache entries
        """
        pass
    
    @abstractmethod
    def get_entry_count(self) -> int:
        """
        Get the current number of entries in the cache.
        
        Returns:
            int: Number of entries, including expired ones
        """
        pass

class ThreadSafeInMemoryCache(AbstractCacheRepository):
    """
    Thread-safe in-memory implementation of the cache repository with automatic cleanup.
    
    This implementation includes a background thread that periodically removes expired entries,
    ensuring that memory is freed even if entries are not accessed after expiration.
    """
    
    def __init__(self, cleanup_interval_seconds: int = 1):
        """
        Initialize the cache with automatic cleanup.
        
        Args:
            cleanup_interval_seconds: How often to check for and remove expired entries
        
        Raises:
            ValueError: If cleanup_interval_seconds is not positive
        """
        if cleanup_interval_seconds <= 0:
            raise ValueError("Cleanup interval must be positive")
            
        self._cache: Dict[str, TimedCacheEntry] = {}
        self._lock = Lock()
        
        # Setup for background cleanup
        self._cleanup_interval = cleanup_interval_seconds
        self._stop_cleanup = Event()
        self._cleanup_thread = Thread(
            target=self._periodic_cleanup,
            name="CacheCleanupThread",
            daemon=True  # Thread will exit when main program exits
        )
        self._cleanup_thread.start()
    
    def retrieve_cached_value(self, key: str) -> Optional[Any]:
        if not key or not key.strip():
            raise ValueError("Cache key cannot be empty or whitespace")
            
        with self._lock:
            if key not in self._cache:
                return None
            
            entry = self._cache[key]
            if entry.is_expired():
                self._remove_expired_entry(key)
                return None
            
            return entry.value
    
    def store_with_expiration(self, key: str, value: Any, time_to_live_seconds: int) -> None:
        if not key or not key.strip():
            raise ValueError("Cache key cannot be empty or whitespace")
            
        if time_to_live_seconds <= 0:
            raise ValueError("Time to live must be positive")
        
        entry = TimedCacheEntry(
            key=key,
            value=value,
            creation_timestamp=time(),
            time_to_live_seconds=time_to_live_seconds
        )
        
        with self._lock:
            self._cache[key] = entry
    
    def remove_cached_value(self, key: str) -> bool:
        if not key or not key.strip():
            raise ValueError("Cache key cannot be empty or whitespace")
            
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False
    
    def remove_all_values(self) -> None:
        """
        Remove all values from the cache and stop the cleanup thread.
        This ensures no resources are wasted if the cache is cleared but not destroyed.
        """
        with self._lock:
            self._cache.clear()
            # Stop the cleanup thread since cache is empty
            self.stop_cleanup()
    
    def get_all_unexpired_entries(self) -> List[TimedCacheEntry]:
        with self._lock:
            current_time = time()
            unexpired = [
                entry for entry in self._cache.values()
                if not entry.is_expired(current_time)
            ]
            
            # Clean up expired entries while we're here
            for key, entry in list(self._cache.items()):
                if entry.is_expired(current_time):
                    self._remove_expired_entry(key)
                    
            return unexpired
    
    def get_entry_count(self) -> int:
        with self._lock:
            return len(self._cache)
    
    def _remove_expired_entry(self, key: str) -> None:
        """Internal method to remove an expired entry."""
        del self._cache[key]
        
    def _periodic_cleanup(self) -> None:
        """
        Periodically check for and remove expired entries.
        This runs in a background thread until stop_cleanup is called.
        
        Note:
            - This method runs in its own thread
            - The wait() call only blocks this cleanup thread
            - Main thread and other operations continue normally
            - If stop_cleanup is called, wait() returns immediately
        """
        while not self._stop_cleanup.is_set():
            # Sleep first to allow initial entries to be added
            # This wait() only blocks the cleanup thread, not the main program
            # Other threads can still read/write to cache while this thread waits
            self._stop_cleanup.wait(self._cleanup_interval)
            
            with self._lock:
                current_time = time()
                # Create list of keys to avoid modifying dict during iteration
                expired_keys = [
                    key for key, entry in self._cache.items()
                    if entry.is_expired(current_time)
                ]
                
                # Remove expired entries
                for key in expired_keys:
                    self._remove_expired_entry(key)
                    
    def stop_cleanup(self) -> None:
        """
        Gracefully stop the background cleanup thread.
        
        This method:
        1. Signals the cleanup thread to stop by setting the stop event
        2. Waits for the thread to finish its current operation
        3. Times out after 2x cleanup interval if thread doesn't stop
        
        This ensures:
        - No abrupt thread termination
        - No memory leaks
        - No hanging on thread shutdown
        
        Note:
        - Safe to call multiple times
        - Safe to call even if thread already stopped
        - Non-blocking (will return after timeout even if thread stuck)
        """
        self._stop_cleanup.set()
        if self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=self._cleanup_interval * 2)
            
    def __del__(self):
        """Ensure cleanup thread is stopped when object is destroyed."""
        self.stop_cleanup()

class CacheManager:
    """
    Manages cache operations with additional features beyond basic storage.
    Provides a higher-level interface for cache operations.
    """
    
    def __init__(self, repository: AbstractCacheRepository):
        self._repository = repository
    
    def retrieve_value(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The unique identifier for the cached value
            
        Returns:
            The cached value if found and not expired, None otherwise
            
        Raises:
            ValueError: If key is invalid
        """
        return self._repository.retrieve_cached_value(key)
    
    def store_value(self, key: str, value: Any, time_to_live_seconds: int) -> None:
        """
        Store a value in the cache with expiration.
        
        Args:
            key: Unique identifier for the value
            value: The data to cache
            time_to_live_seconds: Number of seconds before the value expires
            
        Raises:
            ValueError: If time_to_live_seconds is not positive or key is invalid
        """
        self._repository.store_with_expiration(key, value, time_to_live_seconds)
    
    def remove_value(self, key: str) -> bool:
        """
        Remove a specific value from the cache.
        
        Args:
            key: The unique identifier of the value to remove
            
        Returns:
            bool: True if the value was found and removed, False if not found
            
        Raises:
            ValueError: If key is invalid
        """
        return self._repository.remove_cached_value(key)
    
    def clear_cache(self) -> None:
        """Remove all values from the cache."""
        self._repository.remove_all_values()
    
    def get_active_entries(self) -> List[TimedCacheEntry]:
        """
        Get all non-expired entries in the cache.
        
        Returns:
            List of all cache entries that haven't expired
        """
        return self._repository.get_all_unexpired_entries()
    
    def get_cache_size(self) -> int:
        """
        Get the current number of entries in the cache.
        
        Returns:
            int: Total number of entries in the cache
        """
        return self._repository.get_entry_count()

class CacheSystem:
    """
    Main system orchestrator for the cache.
    Provides a simplified interface for common cache operations.
    """
    
    def __init__(self, cleanup_interval_seconds: int = 1):
        """
        Initialize the cache system.
        
        Args:
            cleanup_interval_seconds: How often to check for and remove expired entries
            
        Raises:
            ValueError: If cleanup_interval_seconds is not positive
        """
        self._repository = ThreadSafeInMemoryCache(cleanup_interval_seconds)
        self.cache_manager = CacheManager(self._repository)
        
    def shutdown(self) -> None:
        """
        Gracefully shutdown the cache system.
        This stops the background cleanup thread.
        """
        self._repository.stop_cleanup()
    
    def get_cached_value(self, key: str) -> Optional[Any]:
        """Retrieve a value from the cache."""
        return self.cache_manager.retrieve_value(key)
    
    def cache_value(self, key: str, value: Any, time_to_live_seconds: int) -> None:
        """Store a value in the cache with expiration."""
        self.cache_manager.store_value(key, value, time_to_live_seconds)
    
    def remove_cached_value(self, key: str) -> bool:
        """Remove a value from the cache."""
        return self.cache_manager.remove_value(key)
    
    def clear_all_values(self) -> None:
        """Remove all values from the cache."""
        self.cache_manager.clear_cache()
    
    def get_active_entry_count(self) -> int:
        """Get number of entries currently in the cache."""
        return self.cache_manager.get_cache_size()

def demo_cache_system():
    """
    Demonstrate the cache system's functionality with automatic cleanup.
    Shows that the main thread continues to work while cleanup thread runs in background.
    """
    try:
        # Create a new cache system with 1-second cleanup interval
        cache = CacheSystem(cleanup_interval_seconds=1)
        
        # Store some values with different TTLs
        cache.cache_value("short_lived", "I expire quickly", time_to_live_seconds=2)
        cache.cache_value("medium_lived", "I last a bit longer", time_to_live_seconds=4)
        cache.cache_value("long_lived", "I last the longest", time_to_live_seconds=60)
        
        # Show initial cache state
        print(f"Initial cache size: {cache.get_active_entry_count()}")  # Should be 3
        
        # Retrieve values immediately
        print("\nInitial values:")
        print("Short lived value:", cache.get_cached_value("short_lived"))
        print("Medium lived value:", cache.get_cached_value("medium_lived"))
        print("Long lived value:", cache.get_cached_value("long_lived"))
        
        # While waiting for expiration, we can still use the cache
        print("\nWaiting 3 seconds for short-lived value to expire...")
        print("Meanwhile, we can still use the cache:")
        
        # Demonstrate that we can still use cache while cleanup thread is waiting
        for i in range(3):
            time.sleep(1)  # This sleep is in main thread
            print(f"Second {i+1}: Adding new value...")
            cache.cache_value(f"temp_key_{i}", f"temp_value_{i}", time_to_live_seconds=5)
            print(f"Cache size: {cache.get_active_entry_count()}")
        
        # Check cache size - short-lived should be automatically removed
        print(f"\nCache size after 3 seconds: {cache.get_active_entry_count()}")  # Should be 2
        print("Short lived value after expiry:", cache.get_cached_value("short_lived"))  # Should be None
        print("Medium lived value still exists:", cache.get_cached_value("medium_lived") is not None)
        print("Long lived value still exists:", cache.get_cached_value("long_lived") is not None)
        
        # Wait for medium-lived value to expire
        print("\nWaiting 2 more seconds for medium-lived value to expire...")
        time.sleep(2)
        
        # Check cache size again - medium-lived should be automatically removed
        print(f"\nCache size after 5 seconds total: {cache.get_active_entry_count()}")  # Should be 1
        print("Medium lived value after expiry:", cache.get_cached_value("medium_lived"))  # Should be None
        print("Long lived value still exists:", cache.get_cached_value("long_lived") is not None)
        
        # Manually remove long-lived value
        print("\nManually removing long-lived value...")
        cache.remove_cached_value("long_lived")
        print(f"Cache size after manual removal: {cache.get_active_entry_count()}")  # Should be 0
        
    finally:
        # Always shutdown the cache system properly
        cache.shutdown()
        print("\nCache system shutdown completed")

if __name__ == "__main__":
    demo_cache_system()