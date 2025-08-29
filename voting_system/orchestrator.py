"""
Voting System Orchestrator

This module contains the main system orchestrator that coordinates
all components of the voting system and provides high-level operations.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import threading

from entities import (
    User, Vote, Candidate, Election, VotingBooth, VotingMachine,
    VotingSystem, VotingResult, VotingRecord, UserStatus, ElectionStatus
)

from managers import (
    UserManager, VoteManager, CandidateManager, ElectionManager,
    VotingBoothManager, VotingMachineManager, VotingSystemManager,
    VotingResultManager, VotingRecordManager
)

from design_patterns import (
    VotingSystemRegistry, EventManager, EventType,
    VotingAlgorithmFactory, ElectionProcessor, FirstPastThePostAlgorithm
)


class VotingSystemOrchestrator:
    """Main orchestrator for the voting system"""

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
        """Initialize the orchestrator"""
        if not hasattr(self, '_initialized'):
            # Get system registry
            self._registry = VotingSystemRegistry()
            self._registry.initialize_system()

            # Get managers from registry
            self._user_manager: UserManager = self._registry.get_manager('user')
            self._vote_manager: VoteManager = self._registry.get_manager('vote')
            self._candidate_manager: CandidateManager = self._registry.get_manager('candidate')
            self._election_manager: ElectionManager = self._registry.get_manager('election')
            self._booth_manager: VotingBoothManager = self._registry.get_manager('booth')
            self._machine_manager: VotingMachineManager = self._registry.get_manager('machine')
            self._system_manager: VotingSystemManager = self._registry.get_manager('system')
            self._result_manager: VotingResultManager = self._registry.get_manager('result')
            self._record_manager: VotingRecordManager = self._registry.get_manager('record')

            # Get event manager
            self._event_manager: EventManager = EventManager()

            # Initialize voting processor with default algorithm
            self._election_processor = ElectionProcessor(FirstPastThePostAlgorithm())

            # System state
            self._system_active = True
            self._lock = threading.Lock()

            self._initialized = True

    # ================================
    # SYSTEM MANAGEMENT
    # ================================

    def initialize_system(self, system_name: str = "Default Voting System") -> VotingSystem:
        """Initialize the voting system"""
        with self._lock:
            system = self._system_manager.create_voting_system(system_name)
            self._event_manager.publish_event(
                EventType.SYSTEM_STATUS_CHANGED,
                {"system_id": system.system_id, "status": "initialized"}
            )
            return system

    def is_system_active(self) -> bool:
        """Check if system is active"""
        return self._system_active

    def shutdown_system(self) -> None:
        """Shutdown the voting system"""
        with self._lock:
            self._system_active = False
            self._event_manager.publish_event(
                EventType.SYSTEM_STATUS_CHANGED,
                {"status": "shutdown"}
            )

    def get_system_statistics(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        return self._system_manager.get_system_statistics()

    # ================================
    # USER MANAGEMENT
    # ================================

    def register_user(self, name: str, email: str, age: int) -> User:
        """Register a new user in the system"""
        if not self._system_active:
            raise RuntimeError("System is not active")

        with self._lock:
            user = self._user_manager.create_user(name, email, age)

            # Update system statistics
            systems = self._system_manager.get_all_systems()
            if systems:
                system_id = systems[0].system_id  # Get first system ID
                self._system_manager.increment_user_count(system_id)

            # Publish event
            self._event_manager.publish_event(
                EventType.USER_REGISTERED,
                {
                    "user_id": user.user_id,
                    "name": user.name,
                    "email": user.email
                }
            )

            return user

    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return self._user_manager.get_user_by_id(user_id)

    def get_all_users(self) -> List[User]:
        """Get all users"""
        return self._user_manager.get_all_users()

    def suspend_user(self, user_id: str) -> bool:
        """Suspend a user"""
        return self._user_manager.suspend_user(user_id)

    def activate_user(self, user_id: str) -> bool:
        """Activate a user"""
        return self._user_manager.activate_user(user_id)

    # ================================
    # CANDIDATE MANAGEMENT
    # ================================

    def register_candidate(self, name: str, party: str, description: str = "") -> Candidate:
        """Register a new candidate"""
        if not self._system_active:
            raise RuntimeError("System is not active")

        with self._lock:
            candidate = self._candidate_manager.create_candidate(name, party, description)

            # Publish event
            self._event_manager.publish_event(
                EventType.CANDIDATE_ADDED,
                {
                    "candidate_id": candidate.candidate_id,
                    "name": candidate.name,
                    "party": candidate.party
                }
            )

            return candidate

    def get_candidate(self, candidate_id: str) -> Optional[Candidate]:
        """Get candidate by ID"""
        return self._candidate_manager.get_candidate_by_id(candidate_id)

    def get_all_candidates(self) -> List[Candidate]:
        """Get all candidates"""
        return self._candidate_manager.get_all_candidates()

    def get_candidates_by_party(self, party: str) -> List[Candidate]:
        """Get candidates by party"""
        return self._candidate_manager.get_candidates_by_party(party)

    # ================================
    # ELECTION MANAGEMENT
    # ================================

    def create_election(self, title: str, description: str,
                       start_date: datetime, end_date: datetime,
                       candidate_ids: List[str]) -> Election:
        """Create a new election"""
        if not self._system_active:
            raise RuntimeError("System is not active")

        with self._lock:
            election = self._election_manager.create_election(
                title, description, start_date, end_date, candidate_ids
            )

            # Create voting record for the election
            self._record_manager.create_election_record(election.election_id)

            # Update system statistics
            systems = self._system_manager.get_all_systems()
            if systems:
                system_id = systems[0].system_id
                self._system_manager.increment_election_count(system_id)

            return election

    def get_election(self, election_id: str) -> Optional[Election]:
        """Get election by ID"""
        return self._election_manager.get_election_by_id(election_id)

    def get_all_elections(self) -> List[Election]:
        """Get all elections"""
        return self._election_manager.get_all_elections()

    def get_active_elections(self) -> List[Election]:
        """Get currently active elections"""
        return self._election_manager.get_active_elections()

    def start_election(self, election_id: str) -> bool:
        """Start an election"""
        with self._lock:
            success = self._election_manager.start_election(election_id)
            if success:
                election = self._election_manager.get_election_by_id(election_id)
                self._event_manager.publish_event(
                    EventType.ELECTION_STARTED,
                    {
                        "election_id": election_id,
                        "title": election.title if election else "Unknown"
                    }
                )
            return success

    def end_election(self, election_id: str) -> bool:
        """End an election and calculate results"""
        with self._lock:
            success = self._election_manager.end_election(election_id)
            if success:
                election = self._election_manager.get_election_by_id(election_id)
                self._event_manager.publish_event(
                    EventType.ELECTION_ENDED,
                    {
                        "election_id": election_id,
                        "title": election.title if election else "Unknown"
                    }
                )

        # Calculate final results outside the lock to avoid deadlock
        if success:
            self.calculate_election_results(election_id)

        return success

    def add_candidate_to_election(self, election_id: str, candidate_id: str) -> bool:
        """Add candidate to election"""
        return self._election_manager.add_candidate_to_election(election_id, candidate_id)

    def get_election_candidates(self, election_id: str) -> List[Candidate]:
        """Get candidates in an election"""
        return self._election_manager.get_election_candidates(election_id)

    # ================================
    # VOTING OPERATIONS
    # ================================

    def cast_vote(self, user_id: str, election_id: str, candidate_id: str) -> Vote:
        """Cast a vote in an election"""
        if not self._system_active:
            raise RuntimeError("System is not active")

        with self._lock:
            vote = self._vote_manager.cast_vote(user_id, election_id, candidate_id)

            # Add vote to election record
            self._record_manager.add_vote_to_record(election_id, vote)

            # Update system statistics
            systems = self._system_manager.get_all_systems()
            if systems:
                system_id = systems[0].system_id
                self._system_manager.increment_vote_count(system_id)

            # Publish event
            self._event_manager.publish_event(
                EventType.VOTE_CAST,
                {
                    "vote_id": vote.vote_id,
                    "user_id": user_id,
                    "election_id": election_id,
                    "candidate_id": candidate_id
                }
            )

            return vote

    def get_vote(self, vote_id: str) -> Optional[Vote]:
        """Get vote by ID"""
        return self._vote_manager.get_vote_by_id(vote_id)

    def get_user_votes(self, user_id: str) -> List[Vote]:
        """Get all votes by a user"""
        return self._vote_manager.get_votes_by_user(user_id)

    def get_election_votes(self, election_id: str) -> List[Vote]:
        """Get all votes in an election"""
        return self._vote_manager.get_votes_by_election(election_id)

    def has_user_voted(self, user_id: str, election_id: str) -> bool:
        """Check if user has voted in an election"""
        return self._record_manager.has_user_voted(user_id, election_id)

    def verify_vote(self, vote_id: str) -> bool:
        """Verify a vote"""
        return self._vote_manager.verify_vote(vote_id)

    # ================================
    # RESULTS AND STATISTICS
    # ================================

    def calculate_election_results(self, election_id: str) -> VotingResult:
        """Calculate election results"""
        with self._lock:
            # Get votes and candidates for the election
            votes = self._record_manager.get_all_votes_in_election(election_id)
            candidates = self._election_manager.get_election_candidates(election_id)

            # Process results using the current algorithm
            winner_id = self._election_processor.process_election_results(votes, candidates)

            # Create or update results
            result = self._result_manager.calculate_results_from_votes(election_id)

            return result

    def get_election_results(self, election_id: str) -> Optional[VotingResult]:
        """Get election results"""
        return self._result_manager.get_election_results(election_id)

    def get_candidate_results(self, election_id: str) -> Dict[str, int]:
        """Get candidate results for an election"""
        return self._result_manager.get_candidate_results(election_id)

    def get_election_winner(self, election_id: str) -> Optional[str]:
        """Get the winner of an election"""
        return self._result_manager.get_winner(election_id)

    def get_election_statistics(self, election_id: str) -> Dict[str, Any]:
        """Get detailed statistics for an election"""
        with self._lock:
            election = self._election_manager.get_election_by_id(election_id)
            if not election:
                return {}

            votes = self._record_manager.get_all_votes_in_election(election_id)
            results = self._result_manager.get_election_results(election_id)
            candidates = self._election_manager.get_election_candidates(election_id)

            stats = {
                "election_id": election_id,
                "title": election.title,
                "description": election.description,
                "status": election.status.value,
                "start_date": election.start_date,
                "end_date": election.end_date,
                "total_votes_cast": len(votes),
                "total_candidates": len(candidates),
                "voting_percentage": results.voting_percentage if results else 0.0,
                "winner": results.winner_candidate_id if results else None
            }

            return stats

    # ================================
    # VOTING INFRASTRUCTURE
    # ================================

    def create_voting_booth(self, location: str, capacity: int) -> VotingBooth:
        """Create a voting booth"""
        return self._booth_manager.create_booth(location, capacity)

    def create_voting_machine(self, booth_id: str, model: str) -> VotingMachine:
        """Create a voting machine"""
        with self._lock:
            machine = self._machine_manager.create_machine(booth_id, model)
            # Assign machine to booth
            self._booth_manager.assign_machine_to_booth(booth_id, machine.machine_id)
            return machine

    def get_available_booths(self) -> List[VotingBooth]:
        """Get available voting booths"""
        return self._booth_manager.get_available_booths()

    def add_voter_to_booth(self, booth_id: str) -> bool:
        """Add a voter to a booth"""
        return self._booth_manager.add_voter_to_booth(booth_id)

    # ================================
    # ALGORITHM MANAGEMENT
    # ================================

    def set_voting_algorithm(self, algorithm_type: str) -> None:
        """Set the voting algorithm for result calculation"""
        algorithm = VotingAlgorithmFactory.create_algorithm(algorithm_type)
        self._election_processor.set_algorithm(algorithm)

    def get_current_algorithm(self) -> str:
        """Get the current voting algorithm name"""
        return self._election_processor.get_algorithm_name()

    # ================================
    # EVENT MANAGEMENT
    # ================================

    def get_event_history(self, event_type: Optional[str] = None) -> List[Any]:
        """Get event history"""
        return self._event_manager.get_event_history(event_type)

    def clear_event_history(self) -> None:
        """Clear event history"""
        self._event_manager.clear_history()

    # ================================
    # UTILITY METHODS
    # ================================

    def get_system_health(self) -> Dict[str, Any]:
        """Get system health status"""
        with self._lock:
            try:
                stats = self.get_system_statistics()
                return {
                    "status": "healthy" if self._system_active else "inactive",
                    "total_users": stats.get("total_users", 0),
                    "total_elections": stats.get("total_elections", 0),
                    "total_votes": stats.get("total_votes", 0),
                    "active_elections": len(self.get_active_elections()),
                    "timestamp": datetime.now()
                }
            except Exception as e:
                return {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now()
                }

    def export_election_data(self, election_id: str) -> Dict[str, Any]:
        """Export all data for an election"""
        with self._lock:
            election = self._election_manager.get_election_by_id(election_id)
            if not election:
                return {}

            votes = self._record_manager.get_all_votes_in_election(election_id)
            results = self._result_manager.get_election_results(election_id)
            candidates = self._election_manager.get_election_candidates(election_id)

            return {
                "election": {
                    "id": election.election_id,
                    "title": election.title,
                    "description": election.description,
                    "status": election.status.value,
                    "start_date": election.start_date.isoformat(),
                    "end_date": election.end_date.isoformat(),
                    "total_votes_cast": election.total_votes_cast
                },
                "candidates": [
                    {
                        "id": c.candidate_id,
                        "name": c.name,
                        "party": c.party,
                        "description": c.description
                    } for c in candidates
                ],
                "votes": [
                    {
                        "id": v.vote_id,
                        "user_id": v.user_id,
                        "candidate_id": v.candidate_id,
                        "timestamp": v.timestamp.isoformat(),
                        "status": v.status.value
                    } for v in votes
                ],
                "results": {
                    "total_votes": results.total_votes if results else 0,
                    "candidate_votes": results.get_all_results() if results else {},
                    "winner": results.winner_candidate_id if results else None,
                    "voting_percentage": results.voting_percentage if results else 0.0
                } if results else None,
                "export_timestamp": datetime.now().isoformat()
            }
