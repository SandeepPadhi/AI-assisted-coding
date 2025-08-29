"""
Voting System Repositories

This module contains abstract repository base classes and concrete implementations
for data access operations. Following the Repository Pattern for clean data access.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
import threading

from entities import (
    User, Vote, Candidate, Election, VotingBooth, VotingMachine,
    VotingSystem, VotingResult, VotingRecord, UserStatus, ElectionStatus, VoteStatus
)


class AbstractUserRepository(ABC):
    """Abstract repository for User entities"""

    @abstractmethod
    def save(self, user: User) -> None:
        """Save a user to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        """Find all users"""
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        pass

    @abstractmethod
    def exists(self, user_id: str) -> bool:
        """Check if user exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total users"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email"""
        pass

    @abstractmethod
    def find_by_status(self, status: UserStatus) -> List[User]:
        """Find users by status"""
        pass

    @abstractmethod
    def find_users_eligible_to_vote_in_election(self, election_id: str) -> List[User]:
        """Find users eligible to vote in election"""
        pass

    @abstractmethod
    def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """Update user status"""
        pass


class AbstractVoteRepository(ABC):
    """Abstract repository for Vote entities"""

    @abstractmethod
    def save(self, vote: Vote) -> None:
        """Save a vote to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, vote_id: str) -> Optional[Vote]:
        """Find vote by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[Vote]:
        """Find all votes"""
        pass

    @abstractmethod
    def delete(self, vote_id: str) -> bool:
        """Delete vote by ID"""
        pass

    @abstractmethod
    def exists(self, vote_id: str) -> bool:
        """Check if vote exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total votes"""
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> List[Vote]:
        """Find votes by user ID"""
        pass

    @abstractmethod
    def find_by_election_id(self, election_id: str) -> List[Vote]:
        """Find votes by election ID"""
        pass

    @abstractmethod
    def find_by_candidate_id(self, candidate_id: str) -> List[Vote]:
        """Find votes by candidate ID"""
        pass

    @abstractmethod
    def find_by_status(self, status: VoteStatus) -> List[Vote]:
        """Find votes by status"""
        pass

    @abstractmethod
    def count_votes_in_election(self, election_id: str) -> int:
        """Count votes in election"""
        pass

    @abstractmethod
    def count_votes_for_candidate(self, candidate_id: str, election_id: str) -> int:
        """Count votes for candidate in election"""
        pass


class AbstractCandidateRepository(ABC):
    """Abstract repository for Candidate entities"""

    @abstractmethod
    def save(self, candidate: Candidate) -> None:
        """Save a candidate to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Find candidate by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[Candidate]:
        """Find all candidates"""
        pass

    @abstractmethod
    def delete(self, candidate_id: str) -> bool:
        """Delete candidate by ID"""
        pass

    @abstractmethod
    def exists(self, candidate_id: str) -> bool:
        """Check if candidate exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total candidates"""
        pass

    @abstractmethod
    def find_by_party(self, party: str) -> List[Candidate]:
        """Find candidates by party"""
        pass

    @abstractmethod
    def find_active_candidates(self) -> List[Candidate]:
        """Find active candidates"""
        pass

    @abstractmethod
    def deactivate_candidate(self, candidate_id: str) -> bool:
        """Deactivate candidate"""
        pass

    @abstractmethod
    def activate_candidate(self, candidate_id: str) -> bool:
        """Activate candidate"""
        pass


class AbstractElectionRepository(ABC):
    """Abstract repository for Election entities"""

    @abstractmethod
    def save(self, election: Election) -> None:
        """Save an election to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, election_id: str) -> Optional[Election]:
        """Find election by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[Election]:
        """Find all elections"""
        pass

    @abstractmethod
    def delete(self, election_id: str) -> bool:
        """Delete election by ID"""
        pass

    @abstractmethod
    def exists(self, election_id: str) -> bool:
        """Check if election exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total elections"""
        pass

    @abstractmethod
    def find_by_status(self, status: ElectionStatus) -> List[Election]:
        """Find elections by status"""
        pass

    @abstractmethod
    def find_active_elections(self) -> List[Election]:
        """Find active elections"""
        pass

    @abstractmethod
    def find_elections_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Election]:
        """Find elections in date range"""
        pass

    @abstractmethod
    def update_election_status(self, election_id: str, status: ElectionStatus) -> bool:
        """Update election status"""
        pass

    @abstractmethod
    def add_candidate_to_election(self, election_id: str, candidate: Candidate) -> bool:
        """Add candidate to election"""
        pass

    @abstractmethod
    def remove_candidate_from_election(self, election_id: str, candidate_id: str) -> bool:
        """Remove candidate from election"""
        pass


class AbstractVotingBoothRepository(ABC):
    """Abstract repository for VotingBooth entities"""

    @abstractmethod
    def save(self, booth: VotingBooth) -> None:
        """Save a voting booth to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, booth_id: str) -> Optional[VotingBooth]:
        """Find voting booth by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[VotingBooth]:
        """Find all voting booths"""
        pass

    @abstractmethod
    def delete(self, booth_id: str) -> bool:
        """Delete voting booth by ID"""
        pass

    @abstractmethod
    def exists(self, booth_id: str) -> bool:
        """Check if voting booth exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total voting booths"""
        pass

    @abstractmethod
    def find_by_location(self, location: str) -> List[VotingBooth]:
        """Find voting booths by location"""
        pass

    @abstractmethod
    def find_available_booths(self) -> List[VotingBooth]:
        """Find booths that can accommodate more voters"""
        pass

    @abstractmethod
    def assign_machine_to_booth(self, booth_id: str, machine_id: str) -> bool:
        """Assign a machine to a booth"""
        pass

    @abstractmethod
    def remove_machine_from_booth(self, booth_id: str, machine_id: str) -> bool:
        """Remove a machine from a booth"""
        pass


class AbstractVotingMachineRepository(ABC):
    """Abstract repository for VotingMachine entities"""

    @abstractmethod
    def save(self, machine: VotingMachine) -> None:
        """Save a voting machine to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, machine_id: str) -> Optional[VotingMachine]:
        """Find voting machine by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[VotingMachine]:
        """Find all voting machines"""
        pass

    @abstractmethod
    def delete(self, machine_id: str) -> bool:
        """Delete voting machine by ID"""
        pass

    @abstractmethod
    def exists(self, machine_id: str) -> bool:
        """Check if voting machine exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total voting machines"""
        pass

    @abstractmethod
    def find_by_booth_id(self, booth_id: str) -> List[VotingMachine]:
        """Find machines assigned to a booth"""
        pass

    @abstractmethod
    def find_available_machines(self) -> List[VotingMachine]:
        """Find machines that are available for use"""
        pass

    @abstractmethod
    def find_machines_needing_maintenance(self) -> List[VotingMachine]:
        """Find machines that need maintenance"""
        pass

    @abstractmethod
    def update_machine_status(self, machine_id: str, is_active: bool) -> bool:
        """Update machine active status"""
        pass


class AbstractVotingSystemRepository(ABC):
    """Abstract repository for VotingSystem entities"""

    @abstractmethod
    def save(self, system: VotingSystem) -> None:
        """Save a voting system to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, system_id: str) -> Optional[VotingSystem]:
        """Find voting system by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[VotingSystem]:
        """Find all voting systems"""
        pass

    @abstractmethod
    def delete(self, system_id: str) -> bool:
        """Delete voting system by ID"""
        pass

    @abstractmethod
    def exists(self, system_id: str) -> bool:
        """Check if voting system exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total voting systems"""
        pass

    @abstractmethod
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        pass

    @abstractmethod
    def update_system_status(self, system_id: str, is_active: bool) -> bool:
        """Update system status"""
        pass


class AbstractVotingResultRepository(ABC):
    """Abstract repository for VotingResult entities"""

    @abstractmethod
    def save(self, result: VotingResult) -> None:
        """Save a voting result to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, result_id: str) -> Optional[VotingResult]:
        """Find voting result by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[VotingResult]:
        """Find all voting results"""
        pass

    @abstractmethod
    def delete(self, result_id: str) -> bool:
        """Delete voting result by ID"""
        pass

    @abstractmethod
    def exists(self, result_id: str) -> bool:
        """Check if voting result exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total voting results"""
        pass

    @abstractmethod
    def find_by_election_id(self, election_id: str) -> Optional[VotingResult]:
        """Find voting results for an election"""
        pass

    @abstractmethod
    def update_vote_count(self, election_id: str, candidate_id: str) -> bool:
        """Update vote count for a candidate in an election"""
        pass

    @abstractmethod
    def get_candidate_results(self, election_id: str) -> Dict[str, int]:
        """Get all candidate results for an election"""
        pass


class AbstractVotingRecordRepository(ABC):
    """Abstract repository for VotingRecord entities"""

    @abstractmethod
    def save(self, record: VotingRecord) -> None:
        """Save a voting record to the repository"""
        pass

    @abstractmethod
    def find_by_id(self, record_id: str) -> Optional[VotingRecord]:
        """Find voting record by ID"""
        pass

    @abstractmethod
    def find_all(self) -> List[VotingRecord]:
        """Find all voting records"""
        pass

    @abstractmethod
    def delete(self, record_id: str) -> bool:
        """Delete voting record by ID"""
        pass

    @abstractmethod
    def exists(self, record_id: str) -> bool:
        """Check if voting record exists"""
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total voting records"""
        pass

    @abstractmethod
    def find_by_election_id(self, election_id: str) -> Optional[VotingRecord]:
        """Find voting record for an election"""
        pass

    @abstractmethod
    def add_vote_to_record(self, election_id: str, vote: Vote) -> bool:
        """Add a vote to the election record"""
        pass

    @abstractmethod
    def has_user_voted_in_election(self, user_id: str, election_id: str) -> bool:
        """Check if user has voted in an election"""
        pass

    @abstractmethod
    def get_user_vote_in_election(self, user_id: str, election_id: str) -> Optional[Vote]:
        """Get user's vote in an election"""
        pass

    @abstractmethod
    def get_all_votes_in_election(self, election_id: str) -> List[Vote]:
        """Get all votes in an election"""
        pass


# Concrete In-Memory Repository Implementations


class InMemoryUserRepository(AbstractUserRepository):
    """In-memory implementation of User repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, User] = {}
        self._lock = threading.Lock()

    def save(self, user: User) -> None:
        """Save a user to the repository"""
        with self._lock:
            self._storage[user.user_id] = user

    def find_by_id(self, user_id: str) -> Optional[User]:
        """Find user by ID"""
        with self._lock:
            return self._storage.get(user_id)

    def find_all(self) -> List[User]:
        """Find all users"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, user_id: str) -> bool:
        """Delete user by ID"""
        with self._lock:
            if user_id in self._storage:
                del self._storage[user_id]
                return True
            return False

    def exists(self, user_id: str) -> bool:
        """Check if user exists"""
        with self._lock:
            return user_id in self._storage

    def count(self) -> int:
        """Count total users"""
        with self._lock:
            return len(self._storage)

    def find_by_email(self, email: str) -> Optional[User]:
        """Find user by email address"""
        with self._lock:
            for user in self._storage.values():
                if user.email == email:
                    return user
            return None

    def find_by_status(self, status: UserStatus) -> List[User]:
        """Find users by status"""
        with self._lock:
            return [user for user in self._storage.values() if user.status == status]

    def find_users_eligible_to_vote_in_election(self, election_id: str) -> List[User]:
        """Find users who can vote in a specific election"""
        with self._lock:
            return [user for user in self._storage.values()
                    if user.status == UserStatus.ACTIVE and user.can_vote_in_election(election_id)]

    def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """Update user status"""
        with self._lock:
            user = self._storage.get(user_id)
            if user:
                user.update_status(status)
                return True
            return False


class InMemoryVoteRepository(AbstractVoteRepository):
    """In-memory implementation of Vote repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, Vote] = {}
        self._lock = threading.Lock()

    def save(self, vote: Vote) -> None:
        """Save a vote to the repository"""
        with self._lock:
            self._storage[vote.vote_id] = vote

    def find_by_id(self, vote_id: str) -> Optional[Vote]:
        """Find vote by ID"""
        with self._lock:
            return self._storage.get(vote_id)

    def find_all(self) -> List[Vote]:
        """Find all votes"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, vote_id: str) -> bool:
        """Delete vote by ID"""
        with self._lock:
            if vote_id in self._storage:
                del self._storage[vote_id]
                return True
            return False

    def exists(self, vote_id: str) -> bool:
        """Check if vote exists"""
        with self._lock:
            return vote_id in self._storage

    def count(self) -> int:
        """Count total votes"""
        with self._lock:
            return len(self._storage)

    def find_by_user_id(self, user_id: str) -> List[Vote]:
        """Find all votes by a user"""
        with self._lock:
            return [vote for vote in self._storage.values() if vote.user_id == user_id]

    def find_by_election_id(self, election_id: str) -> List[Vote]:
        """Find all votes in an election"""
        with self._lock:
            return [vote for vote in self._storage.values() if vote.election_id == election_id]

    def find_by_candidate_id(self, candidate_id: str) -> List[Vote]:
        """Find all votes for a candidate"""
        with self._lock:
            return [vote for vote in self._storage.values() if vote.candidate_id == candidate_id]

    def find_by_status(self, status: VoteStatus) -> List[Vote]:
        """Find votes by status"""
        with self._lock:
            return [vote for vote in self._storage.values() if vote.status == status]

    def count_votes_in_election(self, election_id: str) -> int:
        """Count total votes in an election"""
        with self._lock:
            return len([vote for vote in self._storage.values()
                       if vote.election_id == election_id and vote.is_valid()])

    def count_votes_for_candidate(self, candidate_id: str, election_id: str) -> int:
        """Count votes for a specific candidate in an election"""
        with self._lock:
            return len([vote for vote in self._storage.values()
                       if vote.candidate_id == candidate_id and
                       vote.election_id == election_id and
                       vote.is_valid()])


class InMemoryCandidateRepository(AbstractCandidateRepository):
    """In-memory implementation of Candidate repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, Candidate] = {}
        self._lock = threading.Lock()

    def save(self, candidate: Candidate) -> None:
        """Save a candidate to the repository"""
        with self._lock:
            self._storage[candidate.candidate_id] = candidate

    def find_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Find candidate by ID"""
        with self._lock:
            return self._storage.get(candidate_id)

    def find_all(self) -> List[Candidate]:
        """Find all candidates"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, candidate_id: str) -> bool:
        """Delete candidate by ID"""
        with self._lock:
            if candidate_id in self._storage:
                del self._storage[candidate_id]
                return True
            return False

    def exists(self, candidate_id: str) -> bool:
        """Check if candidate exists"""
        with self._lock:
            return candidate_id in self._storage

    def count(self) -> int:
        """Count total candidates"""
        with self._lock:
            return len(self._storage)

    def find_by_party(self, party: str) -> List[Candidate]:
        """Find candidates by party"""
        with self._lock:
            return [candidate for candidate in self._storage.values() if candidate.party == party]

    def find_active_candidates(self) -> List[Candidate]:
        """Find all active candidates"""
        with self._lock:
            return [candidate for candidate in self._storage.values() if candidate.is_active]

    def deactivate_candidate(self, candidate_id: str) -> bool:
        """Deactivate a candidate"""
        with self._lock:
            candidate = self._storage.get(candidate_id)
            if candidate:
                candidate.deactivate()
                return True
            return False

    def activate_candidate(self, candidate_id: str) -> bool:
        """Activate a candidate"""
        with self._lock:
            candidate = self._storage.get(candidate_id)
            if candidate:
                candidate.activate()
                return True
            return False


class InMemoryElectionRepository(AbstractElectionRepository):
    """In-memory implementation of Election repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, Election] = {}
        self._lock = threading.Lock()

    def save(self, election: Election) -> None:
        """Save an election to the repository"""
        with self._lock:
            self._storage[election.election_id] = election

    def find_by_id(self, election_id: str) -> Optional[Election]:
        """Find election by ID"""
        with self._lock:
            return self._storage.get(election_id)

    def find_all(self) -> List[Election]:
        """Find all elections"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, election_id: str) -> bool:
        """Delete election by ID"""
        with self._lock:
            if election_id in self._storage:
                del self._storage[election_id]
                return True
            return False

    def exists(self, election_id: str) -> bool:
        """Check if election exists"""
        with self._lock:
            return election_id in self._storage

    def count(self) -> int:
        """Count total elections"""
        with self._lock:
            return len(self._storage)

    def find_by_status(self, status: ElectionStatus) -> List[Election]:
        """Find elections by status"""
        with self._lock:
            return [election for election in self._storage.values() if election.status == status]

    def find_active_elections(self) -> List[Election]:
        """Find currently active elections"""
        with self._lock:
            return [election for election in self._storage.values()
                    if election.status == ElectionStatus.ACTIVE and election.is_active()]

    def find_elections_in_date_range(self, start_date: datetime, end_date: datetime) -> List[Election]:
        """Find elections within a date range"""
        with self._lock:
            return [election for election in self._storage.values()
                    if election.start_date >= start_date and election.end_date <= end_date]

    def update_election_status(self, election_id: str, status: ElectionStatus) -> bool:
        """Update election status"""
        with self._lock:
            election = self._storage.get(election_id)
            if election:
                if status == ElectionStatus.ACTIVE:
                    election.start_election()
                elif status == ElectionStatus.COMPLETED:
                    election.end_election()
                else:
                    election._status = status
                return True
            return False

    def add_candidate_to_election(self, election_id: str, candidate: Candidate) -> bool:
        """Add candidate to election"""
        with self._lock:
            election = self._storage.get(election_id)
            if election:
                election.add_candidate(candidate)
                return True
            return False

    def remove_candidate_from_election(self, election_id: str, candidate_id: str) -> bool:
        """Remove candidate from election"""
        with self._lock:
            election = self._storage.get(election_id)
            if election:
                election.remove_candidate(candidate_id)
                return True
            return False


class InMemoryVotingBoothRepository(AbstractVotingBoothRepository):
    """In-memory implementation of VotingBooth repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, VotingBooth] = {}
        self._lock = threading.Lock()

    def save(self, booth: VotingBooth) -> None:
        """Save a voting booth to the repository"""
        with self._lock:
            self._storage[booth.booth_id] = booth

    def find_by_id(self, booth_id: str) -> Optional[VotingBooth]:
        """Find voting booth by ID"""
        with self._lock:
            return self._storage.get(booth_id)

    def find_all(self) -> List[VotingBooth]:
        """Find all voting booths"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, booth_id: str) -> bool:
        """Delete voting booth by ID"""
        with self._lock:
            if booth_id in self._storage:
                del self._storage[booth_id]
                return True
            return False

    def exists(self, booth_id: str) -> bool:
        """Check if voting booth exists"""
        with self._lock:
            return booth_id in self._storage

    def count(self) -> int:
        """Count total voting booths"""
        with self._lock:
            return len(self._storage)

    def find_by_location(self, location: str) -> List[VotingBooth]:
        """Find voting booths by location"""
        with self._lock:
            return [booth for booth in self._storage.values() if booth.location == location]

    def find_available_booths(self) -> List[VotingBooth]:
        """Find booths that can accommodate more voters"""
        with self._lock:
            return [booth for booth in self._storage.values() if booth.can_accommodate_voter()]

    def assign_machine_to_booth(self, booth_id: str, machine_id: str) -> bool:
        """Assign a machine to a booth"""
        with self._lock:
            booth = self._storage.get(booth_id)
            if booth:
                booth.assign_machine(machine_id)
                return True
            return False

    def remove_machine_from_booth(self, booth_id: str, machine_id: str) -> bool:
        """Remove a machine from a booth"""
        with self._lock:
            booth = self._storage.get(booth_id)
            if booth:
                booth.remove_machine(machine_id)
                return True
            return False


class InMemoryVotingMachineRepository(AbstractVotingMachineRepository):
    """In-memory implementation of VotingMachine repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, VotingMachine] = {}
        self._lock = threading.Lock()

    def save(self, machine: VotingMachine) -> None:
        """Save a voting machine to the repository"""
        with self._lock:
            self._storage[machine.machine_id] = machine

    def find_by_id(self, machine_id: str) -> Optional[VotingMachine]:
        """Find voting machine by ID"""
        with self._lock:
            return self._storage.get(machine_id)

    def find_all(self) -> List[VotingMachine]:
        """Find all voting machines"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, machine_id: str) -> bool:
        """Delete voting machine by ID"""
        with self._lock:
            if machine_id in self._storage:
                del self._storage[machine_id]
                return True
            return False

    def exists(self, machine_id: str) -> bool:
        """Check if voting machine exists"""
        with self._lock:
            return machine_id in self._storage

    def count(self) -> int:
        """Count total voting machines"""
        with self._lock:
            return len(self._storage)

    def find_by_booth_id(self, booth_id: str) -> List[VotingMachine]:
        """Find machines assigned to a booth"""
        with self._lock:
            return [machine for machine in self._storage.values() if machine.booth_id == booth_id]

    def find_available_machines(self) -> List[VotingMachine]:
        """Find machines that are available for use"""
        with self._lock:
            return [machine for machine in self._storage.values()
                    if machine.is_active and not machine.is_in_use]

    def find_machines_needing_maintenance(self) -> List[VotingMachine]:
        """Find machines that need maintenance"""
        with self._lock:
            return [machine for machine in self._storage.values()
                    if machine.last_maintenance_date is None or
                    (datetime.now() - machine.last_maintenance_date).days > 30]

    def update_machine_status(self, machine_id: str, is_active: bool) -> bool:
        """Update machine active status"""
        with self._lock:
            machine = self._storage.get(machine_id)
            if machine:
                if is_active:
                    machine._is_active = True
                else:
                    machine.deactivate()
                return True
            return False


class InMemoryVotingSystemRepository(AbstractVotingSystemRepository):
    """In-memory implementation of VotingSystem repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, VotingSystem] = {}
        self._lock = threading.Lock()

    def save(self, system: VotingSystem) -> None:
        """Save a voting system to the repository"""
        with self._lock:
            self._storage[system.system_id] = system

    def find_by_id(self, system_id: str) -> Optional[VotingSystem]:
        """Find voting system by ID"""
        with self._lock:
            return self._storage.get(system_id)

    def find_all(self) -> List[VotingSystem]:
        """Find all voting systems"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, system_id: str) -> bool:
        """Delete voting system by ID"""
        with self._lock:
            if system_id in self._storage:
                del self._storage[system_id]
                return True
            return False

    def exists(self, system_id: str) -> bool:
        """Check if voting system exists"""
        with self._lock:
            return system_id in self._storage

    def count(self) -> int:
        """Count total voting systems"""
        with self._lock:
            return len(self._storage)

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        with self._lock:
            if not self._storage:
                return {
                    "total_systems": 0,
                    "active_systems": 0,
                    "total_elections": 0,
                    "total_users": 0,
                    "total_votes": 0
                }

            # Get statistics from all systems
            total_systems = len(self._storage)
            active_systems = len([s for s in self._storage.values() if s.is_active])
            total_elections = sum(s.total_elections for s in self._storage.values())
            total_users = sum(s.total_users for s in self._storage.values())
            total_votes = sum(s.total_votes_cast for s in self._storage.values())

            return {
                "total_systems": total_systems,
                "active_systems": active_systems,
                "total_elections": total_elections,
                "total_users": total_users,
                "total_votes": total_votes
            }

    def update_system_status(self, system_id: str, is_active: bool) -> bool:
        """Update system status"""
        with self._lock:
            system = self._storage.get(system_id)
            if system:
                if is_active:
                    system.activate()
                else:
                    system.deactivate()
                return True
            return False


class InMemoryVotingResultRepository(AbstractVotingResultRepository):
    """In-memory implementation of VotingResult repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, VotingResult] = {}
        self._lock = threading.Lock()

    def save(self, result: VotingResult) -> None:
        """Save a voting result to the repository"""
        with self._lock:
            self._storage[result.election_id] = result

    def find_by_id(self, result_id: str) -> Optional[VotingResult]:
        """Find voting result by ID"""
        with self._lock:
            return self._storage.get(result_id)

    def find_all(self) -> List[VotingResult]:
        """Find all voting results"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, result_id: str) -> bool:
        """Delete voting result by ID"""
        with self._lock:
            if result_id in self._storage:
                del self._storage[result_id]
                return True
            return False

    def exists(self, result_id: str) -> bool:
        """Check if voting result exists"""
        with self._lock:
            return result_id in self._storage

    def count(self) -> int:
        """Count total voting results"""
        with self._lock:
            return len(self._storage)

    def find_by_election_id(self, election_id: str) -> Optional[VotingResult]:
        """Find voting results for an election"""
        with self._lock:
            return self._storage.get(election_id)

    def update_vote_count(self, election_id: str, candidate_id: str) -> bool:
        """Update vote count for a candidate in an election"""
        with self._lock:
            result = self._storage.get(election_id)
            if result:
                result.add_vote(candidate_id)
                return True
            return False

    def get_candidate_results(self, election_id: str) -> Dict[str, int]:
        """Get all candidate results for an election"""
        with self._lock:
            result = self._storage.get(election_id)
            if result:
                return result.get_all_results()
            return {}


class InMemoryVotingRecordRepository(AbstractVotingRecordRepository):
    """In-memory implementation of VotingRecord repository"""

    def __init__(self) -> None:
        """Initialize the repository with thread-safe storage"""
        self._storage: Dict[str, VotingRecord] = {}
        self._lock = threading.Lock()

    def save(self, record: VotingRecord) -> None:
        """Save a voting record to the repository"""
        with self._lock:
            self._storage[record.election_id] = record

    def find_by_id(self, record_id: str) -> Optional[VotingRecord]:
        """Find voting record by ID"""
        with self._lock:
            return self._storage.get(record_id)

    def find_all(self) -> List[VotingRecord]:
        """Find all voting records"""
        with self._lock:
            return list(self._storage.values())

    def delete(self, record_id: str) -> bool:
        """Delete voting record by ID"""
        with self._lock:
            if record_id in self._storage:
                del self._storage[record_id]
                return True
            return False

    def exists(self, record_id: str) -> bool:
        """Check if voting record exists"""
        with self._lock:
            return record_id in self._storage

    def count(self) -> int:
        """Count total voting records"""
        with self._lock:
            return len(self._storage)

    def find_by_election_id(self, election_id: str) -> Optional[VotingRecord]:
        """Find voting record for an election"""
        with self._lock:
            return self._storage.get(election_id)

    def add_vote_to_record(self, election_id: str, vote: Vote) -> bool:
        """Add a vote to the election record"""
        with self._lock:
            record = self._storage.get(election_id)
            if record:
                record.add_vote(vote)
                return True
            return False

    def has_user_voted_in_election(self, user_id: str, election_id: str) -> bool:
        """Check if user has voted in an election"""
        with self._lock:
            record = self._storage.get(election_id)
            if record:
                return record.has_user_voted(user_id)
            return False

    def get_user_vote_in_election(self, user_id: str, election_id: str) -> Optional[Vote]:
        """Get user's vote in an election"""
        with self._lock:
            record = self._storage.get(election_id)
            if record:
                return record.get_vote_by_user(user_id)
            return None

    def get_all_votes_in_election(self, election_id: str) -> List[Vote]:
        """Get all votes in an election"""
        with self._lock:
            record = self._storage.get(election_id)
            if record:
                return record.get_all_votes()
            return []
