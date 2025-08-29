"""
Voting System Design Patterns

This module implements various design patterns for the voting system:
- Factory Pattern: For creating repositories and managers
- Singleton Pattern: For global system access
- Strategy Pattern: For different voting algorithms
- Observer Pattern: For event-driven updates
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type, Callable
from datetime import datetime
import threading

from entities import (
    User, Vote, Candidate, Election, VotingResult,
    ElectionStatus, VoteStatus
)

from repositories import (
    AbstractUserRepository, AbstractVoteRepository, AbstractCandidateRepository,
    AbstractElectionRepository, AbstractVotingBoothRepository, AbstractVotingMachineRepository,
    AbstractVotingSystemRepository, AbstractVotingResultRepository, AbstractVotingRecordRepository,
    InMemoryUserRepository, InMemoryVoteRepository, InMemoryCandidateRepository,
    InMemoryElectionRepository, InMemoryVotingBoothRepository, InMemoryVotingMachineRepository,
    InMemoryVotingSystemRepository, InMemoryVotingResultRepository, InMemoryVotingRecordRepository
)

from managers import (
    UserManager, VoteManager, CandidateManager, ElectionManager,
    VotingBoothManager, VotingMachineManager, VotingSystemManager,
    VotingResultManager, VotingRecordManager
)


# ================================
# FACTORY PATTERN IMPLEMENTATION
# ================================

class AbstractFactory(ABC):
    """Abstract factory for creating objects"""

    @abstractmethod
    def create(self, *args, **kwargs):
        """Create an object"""
        pass


class RepositoryFactory:
    """Factory for creating repository instances"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton implementation for RepositoryFactory"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize repository instances"""
        if not hasattr(self, '_initialized'):
            # Store singleton instances of repositories
            self._user_repo: Optional[InMemoryUserRepository] = None
            self._vote_repo: Optional[InMemoryVoteRepository] = None
            self._candidate_repo: Optional[InMemoryCandidateRepository] = None
            self._election_repo: Optional[InMemoryElectionRepository] = None
            self._booth_repo: Optional[InMemoryVotingBoothRepository] = None
            self._machine_repo: Optional[InMemoryVotingMachineRepository] = None
            self._system_repo: Optional[InMemoryVotingSystemRepository] = None
            self._result_repo: Optional[InMemoryVotingResultRepository] = None
            self._record_repo: Optional[InMemoryVotingRecordRepository] = None
            self._initialized = True

    def create_user_repository(self) -> AbstractUserRepository:
        """Create user repository"""
        if self._user_repo is None:
            self._user_repo = InMemoryUserRepository()
        return self._user_repo

    def create_vote_repository(self) -> AbstractVoteRepository:
        """Create vote repository"""
        if self._vote_repo is None:
            self._vote_repo = InMemoryVoteRepository()
        return self._vote_repo

    def create_candidate_repository(self) -> AbstractCandidateRepository:
        """Create candidate repository"""
        if self._candidate_repo is None:
            self._candidate_repo = InMemoryCandidateRepository()
        return self._candidate_repo

    def create_election_repository(self) -> AbstractElectionRepository:
        """Create election repository"""
        if self._election_repo is None:
            self._election_repo = InMemoryElectionRepository()
        return self._election_repo

    def create_booth_repository(self) -> AbstractVotingBoothRepository:
        """Create voting booth repository"""
        if self._booth_repo is None:
            self._booth_repo = InMemoryVotingBoothRepository()
        return self._booth_repo

    def create_machine_repository(self) -> AbstractVotingMachineRepository:
        """Create voting machine repository"""
        if self._machine_repo is None:
            self._machine_repo = InMemoryVotingMachineRepository()
        return self._machine_repo

    def create_system_repository(self) -> AbstractVotingSystemRepository:
        """Create voting system repository"""
        if self._system_repo is None:
            self._system_repo = InMemoryVotingSystemRepository()
        return self._system_repo

    def create_result_repository(self) -> AbstractVotingResultRepository:
        """Create voting result repository"""
        if self._result_repo is None:
            self._result_repo = InMemoryVotingResultRepository()
        return self._result_repo

    def create_record_repository(self) -> AbstractVotingRecordRepository:
        """Create voting record repository"""
        if self._record_repo is None:
            self._record_repo = InMemoryVotingRecordRepository()
        return self._record_repo

    def create_all_repositories(self) -> Dict[str, Any]:
        """Create all repositories"""
        return {
            'user': self.create_user_repository(),
            'vote': self.create_vote_repository(),
            'candidate': self.create_candidate_repository(),
            'election': self.create_election_repository(),
            'booth': self.create_booth_repository(),
            'machine': self.create_machine_repository(),
            'system': self.create_system_repository(),
            'result': self.create_result_repository(),
            'record': self.create_record_repository()
        }


class ManagerFactory:
    """Factory for creating manager instances"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton implementation for ManagerFactory"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize with repository factory"""
        if not hasattr(self, '_repo_factory'):
            self._repo_factory = RepositoryFactory()

    def create_user_manager(self) -> UserManager:
        """Create user manager"""
        user_repo = self._repo_factory.create_user_repository()
        return UserManager(user_repo)

    def create_vote_manager(self) -> VoteManager:
        """Create vote manager"""
        vote_repo = self._repo_factory.create_vote_repository()
        user_repo = self._repo_factory.create_user_repository()
        election_repo = self._repo_factory.create_election_repository()
        candidate_repo = self._repo_factory.create_candidate_repository()
        return VoteManager(vote_repo, user_repo, election_repo, candidate_repo)

    def create_candidate_manager(self) -> CandidateManager:
        """Create candidate manager"""
        candidate_repo = self._repo_factory.create_candidate_repository()
        return CandidateManager(candidate_repo)

    def create_election_manager(self) -> ElectionManager:
        """Create election manager"""
        election_repo = self._repo_factory.create_election_repository()
        candidate_repo = self._repo_factory.create_candidate_repository()
        return ElectionManager(election_repo, candidate_repo)

    def create_booth_manager(self) -> VotingBoothManager:
        """Create voting booth manager"""
        booth_repo = self._repo_factory.create_booth_repository()
        return VotingBoothManager(booth_repo)

    def create_machine_manager(self) -> VotingMachineManager:
        """Create voting machine manager"""
        machine_repo = self._repo_factory.create_machine_repository()
        return VotingMachineManager(machine_repo)

    def create_system_manager(self) -> VotingSystemManager:
        """Create voting system manager"""
        system_repo = self._repo_factory.create_system_repository()
        return VotingSystemManager(system_repo)

    def create_result_manager(self) -> VotingResultManager:
        """Create voting result manager"""
        result_repo = self._repo_factory.create_result_repository()
        vote_repo = self._repo_factory.create_vote_repository()
        return VotingResultManager(result_repo, vote_repo)

    def create_record_manager(self) -> VotingRecordManager:
        """Create voting record manager"""
        record_repo = self._repo_factory.create_record_repository()
        return VotingRecordManager(record_repo)

    def create_all_managers(self) -> Dict[str, Any]:
        """Create all managers"""
        return {
            'user': self.create_user_manager(),
            'vote': self.create_vote_manager(),
            'candidate': self.create_candidate_manager(),
            'election': self.create_election_manager(),
            'booth': self.create_booth_manager(),
            'machine': self.create_machine_manager(),
            'system': self.create_system_manager(),
            'result': self.create_result_manager(),
            'record': self.create_record_manager()
        }


# ================================
# SINGLETON PATTERN IMPLEMENTATION
# ================================

class SingletonMeta(type):
    """Metaclass for implementing Singleton pattern"""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """Create or return existing instance"""
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class VotingSystemRegistry(metaclass=SingletonMeta):
    """Singleton registry for the entire voting system"""

    def __init__(self):
        """Initialize the registry"""
        if not hasattr(self, '_initialized'):
            self._repo_factory = RepositoryFactory()
            self._manager_factory = ManagerFactory()
            self._repositories = {}
            self._managers = {}
            self._initialized = True

    def initialize_system(self) -> None:
        """Initialize all system components"""
        self._repositories = self._repo_factory.create_all_repositories()
        self._managers = self._manager_factory.create_all_managers()

    def get_repository(self, name: str) -> Any:
        """Get a repository by name"""
        return self._repositories.get(name)

    def get_manager(self, name: str) -> Any:
        """Get a manager by name"""
        return self._managers.get(name)

    def get_all_repositories(self) -> Dict[str, Any]:
        """Get all repositories"""
        return self._repositories.copy()

    def get_all_managers(self) -> Dict[str, Any]:
        """Get all managers"""
        return self._managers.copy()


# ================================
# STRATEGY PATTERN IMPLEMENTATION
# ================================

class VotingAlgorithm(ABC):
    """Abstract strategy for voting algorithms"""

    @abstractmethod
    def calculate_winner(self, votes: List[Vote], candidates: List[Candidate]) -> Optional[str]:
        """Calculate winner from votes"""
        pass

    @abstractmethod
    def get_algorithm_name(self) -> str:
        """Get algorithm name"""
        pass


class FirstPastThePostAlgorithm(VotingAlgorithm):
    """First-past-the-post voting algorithm (most common)"""

    def calculate_winner(self, votes: List[Vote], candidates: List[Candidate]) -> Optional[str]:
        """Calculate winner using first-past-the-post"""
        if not votes or not candidates:
            return None

        # Count votes for each candidate
        vote_counts = {}
        for candidate in candidates:
            vote_counts[candidate.candidate_id] = 0

        valid_votes = [vote for vote in votes if vote.is_valid()]

        for vote in valid_votes:
            if vote.candidate_id in vote_counts:
                vote_counts[vote.candidate_id] += 1

        # Find candidate with most votes
        if vote_counts:
            return max(vote_counts.keys(), key=lambda x: vote_counts[x])

        return None

    def get_algorithm_name(self) -> str:
        """Get algorithm name"""
        return "First Past The Post"


class RankedChoiceAlgorithm(VotingAlgorithm):
    """Ranked choice voting algorithm"""

    def calculate_winner(self, votes: List[Vote], candidates: List[Candidate]) -> Optional[str]:
        """Calculate winner using ranked choice voting (simplified)"""
        # For simplicity, treating as first-past-the-post
        # In a real implementation, this would handle ranked preferences
        return FirstPastThePostAlgorithm().calculate_winner(votes, candidates)

    def get_algorithm_name(self) -> str:
        """Get algorithm name"""
        return "Ranked Choice"


class ApprovalVotingAlgorithm(VotingAlgorithm):
    """Approval voting algorithm"""

    def calculate_winner(self, votes: List[Vote], candidates: List[Candidate]) -> Optional[str]:
        """Calculate winner using approval voting (simplified)"""
        # For simplicity, treating as first-past-the-post
        # In a real implementation, this would handle multiple approvals
        return FirstPastThePostAlgorithm().calculate_winner(votes, candidates)

    def get_algorithm_name(self) -> str:
        """Get algorithm name"""
        return "Approval Voting"


class VotingAlgorithmFactory:
    """Factory for creating voting algorithms"""

    _algorithms = {
        'first_past_the_post': FirstPastThePostAlgorithm,
        'ranked_choice': RankedChoiceAlgorithm,
        'approval': ApprovalVotingAlgorithm
    }

    @staticmethod
    def create_algorithm(algorithm_type: str) -> VotingAlgorithm:
        """Create a voting algorithm"""
        algorithm_class = VotingAlgorithmFactory._algorithms.get(algorithm_type.lower())
        if algorithm_class:
            return algorithm_class()
        else:
            raise ValueError(f"Unknown algorithm type: {algorithm_type}")

    @staticmethod
    def get_available_algorithms(self) -> List[str]:
        """Get list of available algorithms"""
        return list(VotingAlgorithmFactory._algorithms.keys())


class ElectionProcessor:
    """Context class that uses different voting algorithms"""

    def __init__(self, algorithm: VotingAlgorithm):
        """Initialize with a voting algorithm"""
        self._algorithm = algorithm

    def set_algorithm(self, algorithm: VotingAlgorithm) -> None:
        """Change the voting algorithm"""
        self._algorithm = algorithm

    def process_election_results(self, votes: List[Vote], candidates: List[Candidate]) -> Optional[str]:
        """Process election results using current algorithm"""
        return self._algorithm.calculate_winner(votes, candidates)

    def get_algorithm_name(self) -> str:
        """Get current algorithm name"""
        return self._algorithm.get_algorithm_name()


# ================================
# OBSERVER PATTERN IMPLEMENTATION
# ================================

class EventType:
    """Enumeration of event types"""
    USER_REGISTERED = "user_registered"
    VOTE_CAST = "vote_cast"
    ELECTION_STARTED = "election_started"
    ELECTION_ENDED = "election_ended"
    CANDIDATE_ADDED = "candidate_added"
    SYSTEM_STATUS_CHANGED = "system_status_changed"


class Event:
    """Represents an event in the system"""

    def __init__(self, event_type: str, data: Dict[str, Any], timestamp: Optional[datetime] = None):
        """Initialize event"""
        self.event_type = event_type
        self.data = data
        self.timestamp = timestamp or datetime.now()


class Observer(ABC):
    """Abstract observer interface"""

    @abstractmethod
    def update(self, event: Event) -> None:
        """Handle event notification"""
        pass


class Subject(ABC):
    """Abstract subject interface"""

    def __init__(self):
        """Initialize subject"""
        self._observers: List[Observer] = []
        self._lock = threading.Lock()

    def attach(self, observer: Observer) -> None:
        """Attach an observer"""
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def detach(self, observer: Observer) -> None:
        """Detach an observer"""
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)

    def notify(self, event: Event) -> None:
        """Notify all observers"""
        with self._lock:
            for observer in self._observers:
                try:
                    observer.update(event)
                except Exception as e:
                    print(f"Error notifying observer: {e}")


class EventManager(Subject):
    """Central event manager using Observer pattern"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton implementation"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize event manager"""
        if not hasattr(self, '_initialized'):
            Subject.__init__(self)
            self._event_history: List[Event] = []
            self._lock = threading.Lock()
            self._initialized = True

    def publish_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event to all observers"""
        event = Event(event_type, data)
        with self._lock:
            self._event_history.append(event)
        self.notify(event)

    def get_event_history(self, event_type: Optional[str] = None) -> List[Event]:
        """Get event history"""
        with self._lock:
            if event_type:
                return [event for event in self._event_history if event.event_type == event_type]
            return self._event_history.copy()

    def clear_history(self) -> None:
        """Clear event history"""
        with self._lock:
            self._event_history.clear()


class LoggingObserver(Observer):
    """Observer that logs events"""

    def update(self, event: Event) -> None:
        """Log the event"""
        print(f"[LOG] {event.timestamp} - {event.event_type}: {event.data}")


class NotificationObserver(Observer):
    """Observer that sends notifications"""

    def update(self, event: Event) -> None:
        """Send notification for important events"""
        if event.event_type in [EventType.ELECTION_STARTED, EventType.ELECTION_ENDED]:
            print(f"[NOTIFICATION] Important event: {event.event_type}")
            print(f"Details: {event.data}")


class StatisticsObserver(Observer):
    """Observer that updates statistics"""

    def __init__(self):
        """Initialize statistics"""
        self._stats = {
            'total_users': 0,
            'total_votes': 0,
            'total_elections': 0
        }
        self._lock = threading.Lock()

    def update(self, event: Event) -> None:
        """Update statistics based on events"""
        with self._lock:
            if event.event_type == EventType.USER_REGISTERED:
                self._stats['total_users'] += 1
            elif event.event_type == EventType.VOTE_CAST:
                self._stats['total_votes'] += 1
            elif event.event_type == EventType.ELECTION_STARTED:
                self._stats['total_elections'] += 1

    def get_statistics(self) -> Dict[str, int]:
        """Get current statistics"""
        with self._lock:
            return self._stats.copy()


# ================================
# SYSTEM INITIALIZER
# ================================

class VotingSystemInitializer:
    """Initializer that sets up the entire voting system with all patterns"""

    @staticmethod
    def initialize_system() -> VotingSystemRegistry:
        """Initialize the complete voting system"""
        # Get singleton registry
        registry = VotingSystemRegistry()

        # Initialize repositories and managers
        registry.initialize_system()

        # Get event manager singleton
        event_manager = EventManager()

        # Attach observers
        event_manager.attach(LoggingObserver())
        event_manager.attach(NotificationObserver())
        event_manager.attach(StatisticsObserver())

        print("Voting System initialized successfully with all design patterns!")
        return registry

    @staticmethod
    def get_system() -> VotingSystemRegistry:
        """Get the initialized system"""
        return VotingSystemRegistry()
