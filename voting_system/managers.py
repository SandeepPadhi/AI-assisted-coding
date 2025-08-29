"""
Voting System Managers

This module contains all the entity managers that handle business logic
and coordinate with repositories for data operations.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, TypeVar, Generic
from datetime import datetime
import uuid
import threading

from entities import (
    User, Vote, Candidate, Election, VotingBooth, VotingMachine,
    VotingSystem, VotingResult, VotingRecord, UserStatus, ElectionStatus, VoteStatus
)

from repositories import (
    AbstractUserRepository, AbstractVoteRepository, AbstractCandidateRepository,
    AbstractElectionRepository, AbstractVotingBoothRepository, AbstractVotingMachineRepository,
    AbstractVotingSystemRepository, AbstractVotingResultRepository, AbstractVotingRecordRepository
)

# Generic type for managers
T = TypeVar('T')


class AbstractManager(ABC, Generic[T]):
    """Abstract base class for all managers"""

    def __init__(self, repository: Any) -> None:
        """Initialize manager with repository"""
        self.repository = repository
        self._lock = threading.Lock()


class UserManager(AbstractManager[User]):
    """Manager for User entities with business logic"""

    def __init__(self, user_repository: AbstractUserRepository) -> None:
        """Initialize UserManager with repository"""
        super().__init__(user_repository)
        self.user_repository: AbstractUserRepository = user_repository

    def create_user(self, name: str, email: str, age: int) -> User:
        """Create a new user with validation"""
        with self._lock:
            # Check if email already exists
            existing_user = self.user_repository.find_by_email(email)
            if existing_user:
                raise ValueError(f"User with email {email} already exists")

            user_id = f"user_{uuid.uuid4().hex[:8]}"
            user = User(user_id=user_id, name=name, email=email, age=age)
            self.user_repository.save(user)
            return user

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self.user_repository.find_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.user_repository.find_by_email(email)

    def get_all_users(self) -> List[User]:
        """Get all users"""
        return self.user_repository.find_all()

    def get_users_by_status(self, status: UserStatus) -> List[User]:
        """Get users by status"""
        return self.user_repository.find_by_status(status)

    def get_users_eligible_for_election(self, election_id: str) -> List[User]:
        """Get users eligible to vote in an election"""
        return self.user_repository.find_users_eligible_to_vote_in_election(election_id)

    def update_user_status(self, user_id: str, status: UserStatus) -> bool:
        """Update user status"""
        return self.user_repository.update_user_status(user_id, status)

    def suspend_user(self, user_id: str) -> bool:
        """Suspend a user"""
        return self.update_user_status(user_id, UserStatus.SUSPENDED)

    def activate_user(self, user_id: str) -> bool:
        """Activate a user"""
        return self.update_user_status(user_id, UserStatus.ACTIVE)

    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        return self.user_repository.delete(user_id)

    def get_user_count(self) -> int:
        """Get total user count"""
        return self.user_repository.count()


class VoteManager(AbstractManager[Vote]):
    """Manager for Vote entities with business logic"""

    def __init__(self, vote_repository: AbstractVoteRepository,
                 user_repository: AbstractUserRepository,
                 election_repository: AbstractElectionRepository,
                 candidate_repository: AbstractCandidateRepository) -> None:
        """Initialize VoteManager with repositories"""
        super().__init__(vote_repository)
        self.vote_repository: AbstractVoteRepository = vote_repository
        self.user_repository: AbstractUserRepository = user_repository
        self.election_repository: AbstractElectionRepository = election_repository
        self.candidate_repository: AbstractCandidateRepository = candidate_repository

    def cast_vote(self, user_id: str, election_id: str, candidate_id: str) -> Vote:
        """Cast a vote with comprehensive validation"""
        with self._lock:
            # Validate user exists and is active
            user = self.user_repository.find_by_id(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            if user.status != UserStatus.ACTIVE:
                raise ValueError(f"User {user_id} is not active")

            # Validate election exists and is active
            election = self.election_repository.find_by_id(election_id)
            if not election:
                raise ValueError(f"Election {election_id} not found")
            if not election.can_accept_votes():
                raise ValueError(f"Election {election_id} is not accepting votes")

            # Validate candidate exists and is in election
            candidate = self.candidate_repository.find_by_id(candidate_id)
            if not candidate:
                raise ValueError(f"Candidate {candidate_id} not found")
            if not candidate.is_active:
                raise ValueError(f"Candidate {candidate_id} is not active")

            # Check if candidate is in the election
            if candidate_id not in [c.candidate_id for c in election.candidates]:
                raise ValueError(f"Candidate {candidate_id} is not participating in election {election_id}")

            # Check if user can vote in this election
            if not user.can_vote_in_election(election_id):
                raise ValueError(f"User {user_id} has already voted in election {election_id}")

            # Create and save vote
            vote_id = f"vote_{uuid.uuid4().hex[:8]}"
            vote = Vote(vote_id=vote_id, user_id=user_id, election_id=election_id, candidate_id=candidate_id)

            # Mark user as voted
            user.mark_as_voted_in_election(election_id)

            # Update repositories
            self.user_repository.save(user)
            self.vote_repository.save(vote)

            # Update election vote count
            election.increment_vote_count()
            self.election_repository.save(election)

            return vote

    def get_vote_by_id(self, vote_id: str) -> Optional[Vote]:
        """Get vote by ID"""
        return self.vote_repository.find_by_id(vote_id)

    def get_votes_by_user(self, user_id: str) -> List[Vote]:
        """Get all votes by a user"""
        return self.vote_repository.find_by_user_id(user_id)

    def get_votes_by_election(self, election_id: str) -> List[Vote]:
        """Get all votes in an election"""
        return self.vote_repository.find_by_election_id(election_id)

    def get_votes_by_candidate(self, candidate_id: str) -> List[Vote]:
        """Get all votes for a candidate"""
        return self.vote_repository.find_by_candidate_id(candidate_id)

    def get_votes_by_status(self, status: VoteStatus) -> List[Vote]:
        """Get votes by status"""
        return self.vote_repository.find_by_status(status)

    def verify_vote(self, vote_id: str) -> bool:
        """Verify a vote"""
        with self._lock:
            vote = self.vote_repository.find_by_id(vote_id)
            if vote:
                vote.verify_vote()
                self.vote_repository.save(vote)
                return True
            return False

    def count_votes_in_election(self, election_id: str) -> int:
        """Count total votes in an election"""
        return self.vote_repository.count_votes_in_election(election_id)

    def count_votes_for_candidate_in_election(self, candidate_id: str, election_id: str) -> int:
        """Count votes for a specific candidate in an election"""
        return self.vote_repository.count_votes_for_candidate(candidate_id, election_id)


class CandidateManager(AbstractManager[Candidate]):
    """Manager for Candidate entities with business logic"""

    def __init__(self, candidate_repository: AbstractCandidateRepository) -> None:
        """Initialize CandidateManager with repository"""
        super().__init__(candidate_repository)
        self.candidate_repository: AbstractCandidateRepository = candidate_repository

    def create_candidate(self, name: str, party: str, description: str = "") -> Candidate:
        """Create a new candidate"""
        with self._lock:
            candidate_id = f"candidate_{uuid.uuid4().hex[:8]}"
            candidate = Candidate(candidate_id=candidate_id, name=name, party=party, description=description)
            self.candidate_repository.save(candidate)
            return candidate

    def get_candidate_by_id(self, candidate_id: str) -> Optional[Candidate]:
        """Get candidate by ID"""
        return self.candidate_repository.find_by_id(candidate_id)

    def get_all_candidates(self) -> List[Candidate]:
        """Get all candidates"""
        return self.candidate_repository.find_all()

    def get_candidates_by_party(self, party: str) -> List[Candidate]:
        """Get candidates by party"""
        return self.candidate_repository.find_by_party(party)

    def get_active_candidates(self) -> List[Candidate]:
        """Get all active candidates"""
        return self.candidate_repository.find_active_candidates()

    def deactivate_candidate(self, candidate_id: str) -> bool:
        """Deactivate a candidate"""
        return self.candidate_repository.deactivate_candidate(candidate_id)

    def activate_candidate(self, candidate_id: str) -> bool:
        """Activate a candidate"""
        return self.candidate_repository.activate_candidate(candidate_id)

    def update_candidate(self, candidate_id: str, name: Optional[str] = None,
                        party: Optional[str] = None, description: Optional[str] = None) -> bool:
        """Update candidate information"""
        with self._lock:
            candidate = self.candidate_repository.find_by_id(candidate_id)
            if candidate:
                if name is not None:
                    candidate.name = name
                if party is not None:
                    candidate.party = party
                if description is not None:
                    candidate.description = description
                self.candidate_repository.save(candidate)
                return True
            return False

    def delete_candidate(self, candidate_id: str) -> bool:
        """Delete a candidate"""
        return self.candidate_repository.delete(candidate_id)


class ElectionManager(AbstractManager[Election]):
    """Manager for Election entities with business logic"""

    def __init__(self, election_repository: AbstractElectionRepository,
                 candidate_repository: AbstractCandidateRepository) -> None:
        """Initialize ElectionManager with repositories"""
        super().__init__(election_repository)
        self.election_repository: AbstractElectionRepository = election_repository
        self.candidate_repository: AbstractCandidateRepository = candidate_repository

    def create_election(self, title: str, description: str, start_date: datetime,
                       end_date: datetime, candidate_ids: List[str]) -> Election:
        """Create a new election with candidates"""
        with self._lock:
            # Validate candidates exist
            candidates = []
            for candidate_id in candidate_ids:
                candidate = self.candidate_repository.find_by_id(candidate_id)
                if not candidate:
                    raise ValueError(f"Candidate {candidate_id} not found")
                if not candidate.is_active:
                    raise ValueError(f"Candidate {candidate_id} is not active")
                candidates.append(candidate)

            election_id = f"election_{uuid.uuid4().hex[:8]}"
            election = Election(election_id=election_id, title=title, description=description,
                              start_date=start_date, end_date=end_date, candidates=candidates)
            self.election_repository.save(election)
            return election

    def get_election_by_id(self, election_id: str) -> Optional[Election]:
        """Get election by ID"""
        return self.election_repository.find_by_id(election_id)

    def get_all_elections(self) -> List[Election]:
        """Get all elections"""
        return self.election_repository.find_all()

    def get_elections_by_status(self, status: ElectionStatus) -> List[Election]:
        """Get elections by status"""
        return self.election_repository.find_by_status(status)

    def get_active_elections(self) -> List[Election]:
        """Get currently active elections"""
        return self.election_repository.find_active_elections()

    def start_election(self, election_id: str) -> bool:
        """Start an election"""
        return self.election_repository.update_election_status(election_id, ElectionStatus.ACTIVE)

    def end_election(self, election_id: str) -> bool:
        """End an election"""
        return self.election_repository.update_election_status(election_id, ElectionStatus.COMPLETED)

    def add_candidate_to_election(self, election_id: str, candidate_id: str) -> bool:
        """Add candidate to election"""
        with self._lock:
            candidate = self.candidate_repository.find_by_id(candidate_id)
            if not candidate:
                raise ValueError(f"Candidate {candidate_id} not found")

            return self.election_repository.add_candidate_to_election(election_id, candidate)

    def remove_candidate_from_election(self, election_id: str, candidate_id: str) -> bool:
        """Remove candidate from election"""
        return self.election_repository.remove_candidate_from_election(election_id, candidate_id)

    def get_election_candidates(self, election_id: str) -> List[Candidate]:
        """Get candidates in an election"""
        election = self.election_repository.find_by_id(election_id)
        if election:
            return election.candidates
        return []

    def get_election_statistics(self, election_id: str) -> Dict[str, Any]:
        """Get election statistics"""
        election = self.election_repository.find_by_id(election_id)
        if not election:
            return {}

        return {
            "election_id": election_id,
            "title": election.title,
            "status": election.status.value,
            "candidate_count": len(election.candidates),
            "total_votes": election.total_votes_cast,
            "start_date": election.start_date,
            "end_date": election.end_date
        }


class VotingBoothManager(AbstractManager[VotingBooth]):
    """Manager for VotingBooth entities with business logic"""

    def __init__(self, booth_repository: AbstractVotingBoothRepository) -> None:
        """Initialize VotingBoothManager with repository"""
        super().__init__(booth_repository)
        self.booth_repository: AbstractVotingBoothRepository = booth_repository

    def create_booth(self, location: str, capacity: int) -> VotingBooth:
        """Create a new voting booth"""
        with self._lock:
            booth_id = f"booth_{uuid.uuid4().hex[:8]}"
            booth = VotingBooth(booth_id=booth_id, location=location, capacity=capacity)
            self.booth_repository.save(booth)
            return booth

    def get_booth_by_id(self, booth_id: str) -> Optional[VotingBooth]:
        """Get booth by ID"""
        return self.booth_repository.find_by_id(booth_id)

    def get_all_booths(self) -> List[VotingBooth]:
        """Get all booths"""
        return self.booth_repository.find_all()

    def get_booths_by_location(self, location: str) -> List[VotingBooth]:
        """Get booths by location"""
        return self.booth_repository.find_by_location(location)

    def get_available_booths(self) -> List[VotingBooth]:
        """Get booths that can accommodate more voters"""
        return self.booth_repository.find_available_booths()

    def assign_machine_to_booth(self, booth_id: str, machine_id: str) -> bool:
        """Assign a machine to a booth"""
        return self.booth_repository.assign_machine_to_booth(booth_id, machine_id)

    def remove_machine_from_booth(self, booth_id: str, machine_id: str) -> bool:
        """Remove a machine from a booth"""
        return self.booth_repository.remove_machine_from_booth(booth_id, machine_id)

    def add_voter_to_booth(self, booth_id: str) -> bool:
        """Add a voter to a booth"""
        with self._lock:
            booth = self.booth_repository.find_by_id(booth_id)
            if booth and booth.can_accommodate_voter():
                booth.add_voter()
                self.booth_repository.save(booth)
                return True
            return False

    def remove_voter_from_booth(self, booth_id: str) -> bool:
        """Remove a voter from a booth"""
        with self._lock:
            booth = self.booth_repository.find_by_id(booth_id)
            if booth:
                booth.remove_voter()
                self.booth_repository.save(booth)
                return True
            return False


class VotingMachineManager(AbstractManager[VotingMachine]):
    """Manager for VotingMachine entities with business logic"""

    def __init__(self, machine_repository: AbstractVotingMachineRepository) -> None:
        """Initialize VotingMachineManager with repository"""
        super().__init__(machine_repository)
        self.machine_repository: AbstractVotingMachineRepository = machine_repository

    def create_machine(self, booth_id: str, model: str) -> VotingMachine:
        """Create a new voting machine"""
        with self._lock:
            machine_id = f"machine_{uuid.uuid4().hex[:8]}"
            machine = VotingMachine(machine_id=machine_id, booth_id=booth_id, model=model)
            self.machine_repository.save(machine)
            return machine

    def get_machine_by_id(self, machine_id: str) -> Optional[VotingMachine]:
        """Get machine by ID"""
        return self.machine_repository.find_by_id(machine_id)

    def get_all_machines(self) -> List[VotingMachine]:
        """Get all machines"""
        return self.machine_repository.find_all()

    def get_machines_by_booth(self, booth_id: str) -> List[VotingMachine]:
        """Get machines assigned to a booth"""
        return self.machine_repository.find_by_booth_id(booth_id)

    def get_available_machines(self) -> List[VotingMachine]:
        """Get machines that are available for use"""
        return self.machine_repository.find_available_machines()

    def get_machines_needing_maintenance(self) -> List[VotingMachine]:
        """Get machines that need maintenance"""
        return self.machine_repository.find_machines_needing_maintenance()

    def start_voting_session(self, machine_id: str) -> bool:
        """Start a voting session on a machine"""
        with self._lock:
            machine = self.machine_repository.find_by_id(machine_id)
            if machine:
                machine.start_voting_session()
                self.machine_repository.save(machine)
                return True
            return False

    def end_voting_session(self, machine_id: str) -> bool:
        """End a voting session on a machine"""
        with self._lock:
            machine = self.machine_repository.find_by_id(machine_id)
            if machine:
                machine.end_voting_session()
                self.machine_repository.save(machine)
                return True
            return False

    def perform_machine_maintenance(self, machine_id: str) -> bool:
        """Perform maintenance on a machine"""
        with self._lock:
            machine = self.machine_repository.find_by_id(machine_id)
            if machine:
                machine.perform_maintenance()
                self.machine_repository.save(machine)
                return True
            return False

    def update_machine_status(self, machine_id: str, is_active: bool) -> bool:
        """Update machine active status"""
        return self.machine_repository.update_machine_status(machine_id, is_active)


class VotingResultManager(AbstractManager[VotingResult]):
    """Manager for VotingResult entities with business logic"""

    def __init__(self, result_repository: AbstractVotingResultRepository,
                 vote_repository: AbstractVoteRepository) -> None:
        """Initialize VotingResultManager with repositories"""
        super().__init__(result_repository)
        self.result_repository: AbstractVotingResultRepository = result_repository
        self.vote_repository: AbstractVoteRepository = vote_repository

    def create_election_results(self, election_id: str) -> VotingResult:
        """Create voting results for an election"""
        with self._lock:
            result = VotingResult(election_id=election_id)
            self.result_repository.save(result)
            return result

    def get_election_results(self, election_id: str) -> Optional[VotingResult]:
        """Get election results"""
        return self.result_repository.find_by_election_id(election_id)

    def get_candidate_results(self, election_id: str) -> Dict[str, int]:
        """Get candidate results for an election"""
        return self.result_repository.get_candidate_results(election_id)

    def calculate_results_from_votes(self, election_id: str) -> VotingResult:
        """Calculate results from votes in an election"""
        with self._lock:
            # Get all votes for the election
            votes = self.vote_repository.find_by_election_id(election_id)

            # Create or get existing result
            result = self.result_repository.find_by_election_id(election_id)
            if not result:
                result = VotingResult(election_id=election_id)

            # Count votes for each candidate
            for vote in votes:
                if vote.is_valid():
                    result.add_vote(vote.candidate_id)

            self.result_repository.save(result)
            return result

    def get_winner(self, election_id: str) -> Optional[str]:
        """Get the winner of an election"""
        result = self.result_repository.find_by_election_id(election_id)
        if result:
            return result.winner_candidate_id
        return None


class VotingRecordManager(AbstractManager[VotingRecord]):
    """Manager for VotingRecord entities with business logic"""

    def __init__(self, record_repository: AbstractVotingRecordRepository) -> None:
        """Initialize VotingRecordManager with repository"""
        super().__init__(record_repository)
        self.record_repository: AbstractVotingRecordRepository = record_repository

    def create_election_record(self, election_id: str) -> VotingRecord:
        """Create a voting record for an election"""
        with self._lock:
            record = VotingRecord(election_id=election_id)
            self.record_repository.save(record)
            return record

    def get_election_record(self, election_id: str) -> Optional[VotingRecord]:
        """Get voting record for an election"""
        return self.record_repository.find_by_election_id(election_id)

    def add_vote_to_record(self, election_id: str, vote: Vote) -> bool:
        """Add a vote to the election record"""
        return self.record_repository.add_vote_to_record(election_id, vote)

    def has_user_voted(self, user_id: str, election_id: str) -> bool:
        """Check if user has voted in an election"""
        return self.record_repository.has_user_voted_in_election(user_id, election_id)

    def get_user_vote(self, user_id: str, election_id: str) -> Optional[Vote]:
        """Get user's vote in an election"""
        return self.record_repository.get_user_vote_in_election(user_id, election_id)

    def get_all_votes_in_election(self, election_id: str) -> List[Vote]:
        """Get all votes in an election"""
        return self.record_repository.get_all_votes_in_election(election_id)

    def get_vote_count_in_election(self, election_id: str) -> int:
        """Get total vote count in an election"""
        record = self.record_repository.find_by_election_id(election_id)
        if record:
            return record.get_vote_count()
        return 0


class VotingSystemManager(AbstractManager[VotingSystem]):
    """Manager for VotingSystem entities with business logic"""

    def __init__(self, system_repository: AbstractVotingSystemRepository) -> None:
        """Initialize VotingSystemManager with repository"""
        super().__init__(system_repository)
        self.system_repository: AbstractVotingSystemRepository = system_repository

    def create_voting_system(self, name: str) -> VotingSystem:
        """Create a new voting system"""
        with self._lock:
            system_id = f"system_{uuid.uuid4().hex[:8]}"
            system = VotingSystem(system_id=system_id, name=name)
            self.system_repository.save(system)
            return system

    def get_system_by_id(self, system_id: str) -> Optional[VotingSystem]:
        """Get system by ID"""
        return self.system_repository.find_by_id(system_id)

    def get_all_systems(self) -> List[VotingSystem]:
        """Get all systems"""
        return self.system_repository.find_all()

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        return self.system_repository.get_system_statistics()

    def update_system_status(self, system_id: str, is_active: bool) -> bool:
        """Update system status"""
        return self.system_repository.update_system_status(system_id, is_active)

    def increment_election_count(self, system_id: str) -> bool:
        """Increment election count for a system"""
        with self._lock:
            system = self.system_repository.find_by_id(system_id)
            if system:
                system.increment_election_count()
                self.system_repository.save(system)
                return True
            return False

    def increment_user_count(self, system_id: str) -> bool:
        """Increment user count for a system"""
        with self._lock:
            system = self.system_repository.find_by_id(system_id)
            if system:
                system.increment_user_count()
                self.system_repository.save(system)
                return True
            return False

    def increment_vote_count(self, system_id: str) -> bool:
        """Increment vote count for a system"""
        with self._lock:
            system = self.system_repository.find_by_id(system_id)
            if system:
                system.increment_vote_count()
                self.system_repository.save(system)
                return True
            return False
