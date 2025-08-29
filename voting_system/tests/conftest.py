"""
Pytest configuration and fixtures for voting system tests.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Add the parent directory to the path so we can import the voting system modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from entities import (
    User, Candidate, Election, Vote, VotingBooth, VotingMachine, VotingSystem,
    UserStatus, ElectionStatus, VoteStatus
)
from repositories import (
    InMemoryUserRepository, InMemoryCandidateRepository, InMemoryElectionRepository,
    InMemoryVoteRepository, InMemoryVotingBoothRepository, InMemoryVotingMachineRepository,
    InMemoryVotingSystemRepository
)
from managers import (
    UserManager, CandidateManager, ElectionManager, VoteManager
)
from orchestrator import VotingSystemOrchestrator
from design_patterns import RepositoryFactory, EventManager
from concurrency_utils import RequestQueue, WorkerPool, Request


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "user_id": "user_123",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "age": 30
    }


@pytest.fixture
def sample_candidate_data():
    """Sample candidate data for testing"""
    return {
        "candidate_id": "candidate_123",
        "name": "Jane Smith",
        "party": "Democratic Party",
        "description": "Experienced leader with focus on education"
    }


@pytest.fixture
def sample_election_data():
    """Sample election data for testing"""
    now = datetime.now()
    return {
        "election_id": "election_123",
        "title": "City Mayor Election",
        "description": "Vote for your next mayor",
        "start_date": now + timedelta(minutes=1),
        "end_date": now + timedelta(hours=24),
        "candidate_ids": ["candidate_1", "candidate_2"]
    }


@pytest.fixture
def sample_vote_data():
    """Sample vote data for testing"""
    return {
        "vote_id": "vote_123",
        "user_id": "user_123",
        "election_id": "election_123",
        "candidate_id": "candidate_456",
        "timestamp": datetime.now()
    }


@pytest.fixture
def user_repository():
    """In-memory user repository fixture"""
    return InMemoryUserRepository()


@pytest.fixture
def candidate_repository():
    """In-memory candidate repository fixture"""
    return InMemoryCandidateRepository()


@pytest.fixture
def election_repository():
    """In-memory election repository fixture"""
    return InMemoryElectionRepository()


@pytest.fixture
def vote_repository():
    """In-memory vote repository fixture"""
    return InMemoryVoteRepository()


@pytest.fixture
def voting_booth_repository():
    """In-memory voting booth repository fixture"""
    return InMemoryVotingBoothRepository()


@pytest.fixture
def voting_machine_repository():
    """In-memory voting machine repository fixture"""
    return InMemoryVotingMachineRepository()


@pytest.fixture
def voting_system_repository():
    """In-memory voting system repository fixture"""
    return InMemoryVotingSystemRepository()


@pytest.fixture
def repository_factory():
    """Repository factory fixture"""
    return RepositoryFactory()


@pytest.fixture
def event_manager():
    """Event manager fixture"""
    return EventManager()


@pytest.fixture
def user_manager(user_repository):
    """User manager fixture"""
    return UserManager(user_repository)


@pytest.fixture
def candidate_manager(candidate_repository):
    """Candidate manager fixture"""
    return CandidateManager(candidate_repository)


@pytest.fixture
def election_manager(election_repository, candidate_repository):
    """Election manager fixture"""
    return ElectionManager(election_repository, candidate_repository)


@pytest.fixture
def vote_manager(vote_repository, user_repository, election_repository, candidate_repository):
    """Vote manager fixture"""
    return VoteManager(vote_repository, user_repository, election_repository, candidate_repository)


@pytest.fixture
def orchestrator(user_manager, candidate_manager, election_manager, vote_manager,
                voting_booth_repository, voting_machine_repository, voting_system_repository,
                event_manager):
    """Voting system orchestrator fixture"""
    return VotingSystemOrchestrator(
        user_manager=user_manager,
        candidate_manager=candidate_manager,
        election_manager=election_manager,
        vote_manager=vote_manager,
        voting_booth_repository=voting_booth_repository,
        voting_machine_repository=voting_machine_repository,
        voting_system_repository=voting_system_repository,
        event_manager=event_manager
    )


@pytest.fixture
def sample_user(sample_user_data):
    """Sample user instance"""
    return User(**sample_user_data)


@pytest.fixture
def sample_candidate(sample_candidate_data):
    """Sample candidate instance"""
    return Candidate(**sample_candidate_data)


@pytest.fixture
def sample_election(sample_election_data):
    """Sample election instance"""
    return Election(**sample_election_data)


@pytest.fixture
def sample_vote(sample_vote_data):
    """Sample vote instance"""
    return Vote(**sample_vote_data)


@pytest.fixture
def worker_pool():
    """Worker pool fixture"""
    return WorkerPool(num_workers=2)


@pytest.fixture
def request_queue():
    """Request queue fixture"""
    return RequestQueue()


@pytest.fixture(autouse=True)
def cleanup_event_manager():
    """Clean up event manager after each test"""
    yield
    EventManager()._observers.clear()


# Custom test markers
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning"),
]


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "functional: marks tests as functional tests")
    config.addinivalue_line("markers", "concurrency: marks tests as concurrency tests")
