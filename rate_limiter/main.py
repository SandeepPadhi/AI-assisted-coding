"""
Goal: 
- Create a rate limiter system that can be used to limit the number of requests to a resource.

Requirements:
- The system should be able to handle 2 requests per second for a given user.

Non-Functional Requirements:
- The system should be able to scale to 1000000 requests per second

Entities:
- RateLimiter
- User
- Request

EntityManagers:
- RateLimiterManager

SystemOrchestrator:
- RateLimiterSystem

ExternalServices:
- None

Repositories:
- AbstractRateLimiterRepository
- InMemoryRateLimiterRepository

RateLimiterAlgorithm:
- LeakyBucket
- TokenBucket
- FixedWindow
- SlidingWindow
- SlidingLog
- SlidingWindowLog

Design Guidelines:
- Use good naming conventions
- Divide the code into entities, entity managers, repositories, system orchestrator, and external services as needed
- Use correct abstractions for future extensions
- Do not use any external libraries.
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
from datetime import datetime
from typing import Dict, List, Optional
import time
from enum import Enum

# Entities
@dataclass
class User:
    user_id: str
    name: str

@dataclass
class Request:
    request_id: str
    user_id: str
    timestamp: float
    
class RateLimitResult:
    def __init__(self, is_allowed: bool, wait_time: float = 0):
        self.is_allowed = is_allowed
        self.wait_time = wait_time

# Rate Limiter Algorithm Strategy
class RateLimiterAlgorithm(ABC):
    @abstractmethod
    def is_allowed(self, user_id: str) -> RateLimitResult:
        pass

class FixedWindowRateLimiter(RateLimiterAlgorithm):
    def __init__(self, requests_per_second: int = 2):
        self.requests_per_second = requests_per_second
        self.user_requests: Dict[str, List[float]] = {}
        
    def is_allowed(self, user_id: str) -> RateLimitResult:
        current_time = time.time()
        window_start = current_time - 1  # 1 second window
        
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
            
        # Remove old requests
        self.user_requests[user_id] = [
            timestamp for timestamp in self.user_requests[user_id]
            if timestamp > window_start
        ]
        
        current_requests = len(self.user_requests[user_id])
        if current_requests < self.requests_per_second:
            self.user_requests[user_id].append(current_time)
            return RateLimitResult(True)
            
        # Calculate wait time based on the oldest request in the window
        oldest_request = min(self.user_requests[user_id])
        wait_time = oldest_request + 1.0 - current_time  # Wait until the oldest request expires
        return RateLimitResult(False, max(0.001, wait_time))  # Ensure minimum wait time

# Abstract Repository
class AbstractRateLimiterRepository(ABC):
    @abstractmethod
    def save_user(self, user: User) -> None:
        pass
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def save_request(self, request: Request) -> None:
        pass
    
    @abstractmethod
    def get_user_requests(self, user_id: str) -> List[Request]:
        pass

# In-Memory Repository Implementation
class InMemoryRateLimiterRepository(AbstractRateLimiterRepository):
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.requests: Dict[str, List[Request]] = {}
        
    def save_user(self, user: User) -> None:
        self.users[user.user_id] = user
        
    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)
        
    def save_request(self, request: Request) -> None:
        if request.user_id not in self.requests:
            self.requests[request.user_id] = []
        self.requests[request.user_id].append(request)
        
    def get_user_requests(self, user_id: str) -> List[Request]:
        return self.requests.get(user_id, [])

# Rate Limiter Manager
class RateLimiterManager:
    def __init__(self, repository: AbstractRateLimiterRepository, algorithm: RateLimiterAlgorithm):
        self.repository = repository
        self.algorithm = algorithm
        
    def register_user(self, user: User) -> None:
        self.repository.save_user(user)
        
    def process_request(self, user_id: str) -> RateLimitResult:
        user = self.repository.get_user(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")
            
        result = self.algorithm.is_allowed(user_id)
        if result.is_allowed:
            request = Request(
                request_id=f"{user_id}_{time.time()}",
                user_id=user_id,
                timestamp=time.time()
            )
            self.repository.save_request(request)
        return result

# System Orchestrator
class RateLimiterSystem:
    def __init__(self, requests_per_second: int = 2):
        self.repository = InMemoryRateLimiterRepository()
        self.algorithm = FixedWindowRateLimiter(requests_per_second=requests_per_second)
        self.manager = RateLimiterManager(self.repository, self.algorithm)
        
    def register_user(self, user_id: str, name: str) -> None:
        user = User(user_id=user_id, name=name)
        self.manager.register_user(user)
        
    def make_request(self, user_id: str) -> RateLimitResult:
        return self.manager.process_request(user_id)

# Demo usage
def demo():
    # Create rate limiter system with 3 requests per second
    system = RateLimiterSystem(requests_per_second=3)
    
    # Register a user
    system.register_user("user1", "John Doe")
    
    # Make some requests
    print("Making requests for user1:")
    for i in range(4):
        result = system.make_request("user1")
        if result.is_allowed:
            print(f"Request {i+1}: Allowed")
        else:
            print(f"Request {i+1}: Rate limited. Wait for {result.wait_time:.2f} seconds")
        time.sleep(0.1)  # Small delay between requests


if __name__ == "__main__":
    demo()
