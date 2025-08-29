"""
Voting System Entities

This module contains all the entity classes for the voting system.
Each entity encapsulates its business logic, validations, and invariants.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from abc import ABC, abstractmethod
import uuid
import threading


class UserStatus(Enum):
    """Enumeration for user status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ElectionStatus(Enum):
    """Enumeration for election status"""
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VoteStatus(Enum):
    """Enumeration for vote status"""
    CAST = "cast"
    VERIFIED = "verified"
    INVALID = "invalid"


# ================================
# ABSTRACT ENTITY BASE CLASSES
# ================================

class AbstractEntity(ABC):
    """Abstract base class for all entities"""

    def __init__(self, entity_id: str) -> None:
        """Initialize entity with ID"""
        self._entity_id = entity_id

    @property
    @abstractmethod
    def entity_id(self) -> str:
        """Get entity ID"""
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate entity data"""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """String representation"""
        pass


class AbstractUser(AbstractEntity):
    """Abstract base class for User entity"""

    def __init__(self, user_id: str, name: str, email: str, age: int) -> None:
        """Initialize abstract user"""
        super().__init__(user_id)
        self._name = name
        self._email = email
        self._age = age
        self._status = UserStatus.ACTIVE
        self._registration_date = datetime.now()
        self._has_voted_in_election: Dict[str, bool] = {}

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def user_id(self) -> str:
        return self._entity_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def email(self) -> str:
        return self._email

    @property
    def age(self) -> int:
        return self._age

    @property
    def status(self) -> UserStatus:
        return self._status

    @property
    def registration_date(self) -> datetime:
        return self._registration_date

    @property
    def has_voted_in_election(self) -> Dict[str, bool]:
        return self._has_voted_in_election

    @abstractmethod
    def can_vote_in_election(self, election_id: str) -> bool:
        """Check if user can vote in election"""
        pass

    @abstractmethod
    def mark_as_voted_in_election(self, election_id: str) -> None:
        """Mark user as voted in election"""
        pass

    @abstractmethod
    def update_status(self, status: UserStatus) -> None:
        """Update user status"""
        pass


class AbstractCandidate(AbstractEntity):
    """Abstract base class for Candidate entity"""

    def __init__(self, candidate_id: str, name: str, party: str, description: str = "") -> None:
        """Initialize abstract candidate"""
        super().__init__(candidate_id)
        self._name = name
        self._party = party
        self._description = description
        self._is_active = True

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def candidate_id(self) -> str:
        return self._entity_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def party(self) -> str:
        return self._party

    @property
    def description(self) -> str:
        return self._description

    @property
    def is_active(self) -> bool:
        return self._is_active

    @abstractmethod
    def deactivate(self) -> None:
        """Deactivate candidate"""
        pass

    @abstractmethod
    def activate(self) -> None:
        """Activate candidate"""
        pass


class AbstractElection(AbstractEntity):
    """Abstract base class for Election entity"""

    def __init__(self, election_id: str, title: str, description: str,
                 start_date: datetime, end_date: datetime, candidates: List[Any]) -> None:
        """Initialize abstract election"""
        super().__init__(election_id)
        self._title = title
        self._description = description
        self._start_date = start_date
        self._end_date = end_date
        self._candidates = candidates.copy()
        self._status = ElectionStatus.SCHEDULED
        self._created_date = datetime.now()
        self._total_votes_cast = 0

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def election_id(self) -> str:
        return self._entity_id

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    @property
    def start_date(self) -> datetime:
        return self._start_date

    @property
    def end_date(self) -> datetime:
        return self._end_date

    @property
    def candidates(self) -> List[Any]:
        return self._candidates

    @property
    def candidate_ids(self) -> List[str]:
        """Get candidate IDs from candidates list"""
        return [c.candidate_id if hasattr(c, 'candidate_id') else str(c) for c in self._candidates]

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp (alias for created_date)"""
        return self._created_date

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp (alias for created_date for now)"""
        return self._created_date

    @property
    def total_votes(self) -> int:
        """Get total votes cast (alias for total_votes_cast)"""
        return self._total_votes_cast

    @property
    def results(self) -> Dict[str, int]:
        """Get election results (empty dict for now)"""
        return {}

    @property
    def status(self) -> ElectionStatus:
        return self._status

    @property
    def created_date(self) -> datetime:
        return self._created_date

    @property
    def total_votes_cast(self) -> int:
        return self._total_votes_cast

    @abstractmethod
    def is_active(self) -> bool:
        """Check if election is active"""
        pass

    @abstractmethod
    def can_accept_votes(self) -> bool:
        """Check if election can accept votes"""
        pass

    @abstractmethod
    def start_election(self) -> None:
        """Start the election"""
        pass

    @abstractmethod
    def end_election(self) -> None:
        """End the election"""
        pass

    @abstractmethod
    def add_candidate(self, candidate: Any) -> None:
        """Add candidate to election"""
        pass

    @abstractmethod
    def remove_candidate(self, candidate_id: str) -> None:
        """Remove candidate from election"""
        pass

    @abstractmethod
    def increment_vote_count(self) -> None:
        """Increment vote count"""
        pass


class AbstractVote(AbstractEntity):
    """Abstract base class for Vote entity"""

    def __init__(self, vote_id: str, user_id: str, election_id: str, candidate_id: str,
                 timestamp: Optional[datetime] = None) -> None:
        """Initialize abstract vote"""
        super().__init__(vote_id)
        self._user_id = user_id
        self._election_id = election_id
        self._candidate_id = candidate_id
        self._timestamp = timestamp or datetime.now()
        self._status = VoteStatus.CAST
        self._verification_code = str(uuid.uuid4())[:8].upper()

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def vote_id(self) -> str:
        return self._entity_id

    @property
    def user_id(self) -> str:
        return self._user_id

    @property
    def election_id(self) -> str:
        return self._election_id

    @property
    def candidate_id(self) -> str:
        return self._candidate_id

    @property
    def timestamp(self) -> datetime:
        return self._timestamp

    @property
    def status(self) -> VoteStatus:
        return self._status

    @property
    def verification_code(self) -> str:
        return self._verification_code

    @abstractmethod
    def verify_vote(self) -> None:
        """Verify the vote"""
        pass

    @abstractmethod
    def invalidate_vote(self) -> None:
        """Invalidate the vote"""
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if vote is valid"""
        pass


class User(AbstractUser):
    """Represents a user who can vote in the system"""

    def __init__(self, user_id: str, name: str, email: str, age: int) -> None:
        """Initialize a user with validation"""
        super().__init__(user_id, name, email, age)
        self._validate_user_data(user_id, name, email, age)

    def _validate_user_data(self, user_id: str, name: str, email: str, age: int) -> None:
        """Validate user data during initialization"""
        if not user_id or not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("User ID must be a non-empty string")

        if not name or not isinstance(name, str) or len(name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")

        if not email or not isinstance(email, str) or "@" not in email or email.count("@") != 1 or email.startswith("@") or email.endswith("@"):
            raise ValueError("Valid email address is required")

        if not isinstance(age, int) or age < 18:
            raise ValueError("User must be at least 18 years old")

    def validate(self) -> None:
        """Validate user data"""
        self._validate_user_data(self.user_id, self.name, self.email, self.age)

    def can_vote_in_election(self, election_id: str) -> bool:
        """Check if user can vote in a specific election"""
        if self.status != UserStatus.ACTIVE:
            return False

        # User can vote if they haven't voted in this election yet
        return not self.has_voted_in_election.get(election_id, False)

    def mark_as_voted_in_election(self, election_id: str) -> None:
        """Mark that user has voted in an election"""
        self.has_voted_in_election[election_id] = True

    def update_status(self, new_status: UserStatus) -> None:
        """Update user status"""
        if not isinstance(new_status, UserStatus):
            raise ValueError("Invalid user status")
        self._status = new_status

    def __str__(self) -> str:
        return f"User(id={self.user_id}, name={self.name}, status={self.status.value})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, User):
            return False
        return (self.user_id == other.user_id and
                self.name == other.name and
                self.email == other.email and
                self.age == other.age and
                self.status == other.status)

    def __hash__(self) -> int:
        return hash(self.user_id)


class Candidate(AbstractCandidate):
    """Represents a candidate who can receive votes"""

    def __init__(self, candidate_id: str, name: str, party: str, description: str = "") -> None:
        """Initialize a candidate with validation"""
        super().__init__(candidate_id, name, party, description)
        self._validate_candidate_data(candidate_id, name, party, description)
        self._is_verified = False
        self._created_at = datetime.now()
        self._updated_at = datetime.now()

    def _validate_candidate_data(self, candidate_id: str, name: str, party: str, description: str = None) -> None:
        """Validate candidate data during initialization"""
        if not candidate_id or not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("Invalid candidate ID")

        if not name or not isinstance(name, str) or not name.strip() or len(name.strip()) < 2:
            raise ValueError("Invalid name")

        # Check if name contains only alphabetic characters and spaces
        if not all(c.isalpha() or c.isspace() for c in name):
            raise ValueError("Invalid name")

        if not party or not isinstance(party, str) or not party.strip():
            raise ValueError("Invalid party")

        if description is not None and (not description or not isinstance(description, str) or not description.strip()):
            raise ValueError("Invalid description")git s

    def validate(self) -> None:
        """Validate candidate data"""
        self._validate_candidate_data(self.candidate_id, self.name, self.party)

    def deactivate(self) -> None:
        """Deactivate the candidate"""
        self._is_active = False

    def activate(self) -> None:
        """Activate the candidate"""
        self._is_active = True

    @property
    def verified(self) -> bool:
        """Check if candidate is verified"""
        return self._is_verified

    def verify(self) -> None:
        """Verify the candidate"""
        if not self._is_verified:
            self._is_verified = True
            self._updated_at = datetime.now()

    def unverify(self) -> None:
        """Unverify the candidate"""
        if self._is_verified:
            self._is_verified = False
            self._updated_at = datetime.now()

    def update_description(self, new_description: str) -> None:
        """Update candidate description"""
        if not new_description or not isinstance(new_description, str) or not new_description.strip():
            raise ValueError("Invalid description")
        self._description = new_description
        self._updated_at = datetime.now()

    def update_party(self, new_party: str) -> None:
        """Update candidate party"""
        if not new_party or not isinstance(new_party, str) or not new_party.strip():
            raise ValueError("Invalid party")
        self._party = new_party
        self._updated_at = datetime.now()

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp"""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp"""
        return self._updated_at

    def __str__(self) -> str:
        return f"Candidate(id={self.candidate_id}, name={self.name}, party={self.party}, verified={self.verified})"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        if not isinstance(other, Candidate):
            return False
        return (self.candidate_id == other.candidate_id and
                self.name == other.name and
                self.party == other.party and
                self.verified == other.verified)

    def __hash__(self) -> int:
        return hash(self.candidate_id)


class Election(AbstractElection):
    """Represents an election event"""

    def __init__(self, election_id: str, title: str, description: str,
                 start_date: datetime, end_date: datetime,
                 candidates: List[Any] = None, candidate_ids: List[str] = None) -> None:
        """Initialize an election with validation - accepts both Candidate objects and candidate IDs"""
        # Handle backward compatibility
        if candidates is None and candidate_ids is not None:
            candidates = candidate_ids
        elif candidates is None:
            candidates = []

        super().__init__(election_id, title, description, start_date, end_date, candidates)
        self._validate_election_data(election_id, title, start_date, end_date, candidates)

    def _validate_election_data(self, election_id: str, title: str,
                               start_date: datetime, end_date: datetime,
                               candidates: List[Any]) -> None:
        """Validate election data during initialization"""
        if not election_id or not isinstance(election_id, str) or not election_id.strip():
            raise ValueError("Election ID must be a non-empty string")

        if not title or not isinstance(title, str) or not title.strip():
            raise ValueError("Election title is required")

        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("Valid start and end dates are required")

        if start_date >= end_date:
            raise ValueError("End date must be after start date")

        if not candidates or len(candidates) < 2:
            raise ValueError("Election must have at least 2 candidates")

        # Check for duplicate candidate IDs
        candidate_ids = [c.candidate_id if hasattr(c, 'candidate_id') else str(c) for c in candidates]
        if len(candidate_ids) != len(set(candidate_ids)):
            raise ValueError("Duplicate candidate IDs are not allowed")

    def validate(self) -> None:
        """Validate election data"""
        self._validate_election_data(self.election_id, self.title, self.start_date, self.end_date, self.candidates)

    def is_active(self) -> bool:
        """Check if election is currently active"""
        now = datetime.now()
        return (self.status == ElectionStatus.ACTIVE and
                self.start_date <= now <= self.end_date)

    def can_accept_votes(self) -> bool:
        """Check if election can accept votes"""
        return self.status == ElectionStatus.ACTIVE and self.is_active()

    def start_election(self) -> None:
        """Start the election"""
        if self.status != ElectionStatus.SCHEDULED:
            raise ValueError("Only scheduled elections can be started")

        now = datetime.now()
        if now < self.start_date:
            raise ValueError("Cannot start election before scheduled start date")

        self._status = ElectionStatus.ACTIVE

    def end_election(self) -> None:
        """End the election"""
        if self.status != ElectionStatus.ACTIVE:
            raise ValueError("Only active elections can be ended")

        self._status = ElectionStatus.COMPLETED

    def add_candidate(self, candidate: Candidate) -> None:
        """Add a candidate to the election"""
        if self.status != ElectionStatus.SCHEDULED:
            raise ValueError("Cannot add candidates to non-scheduled elections")

        if any(c.candidate_id == candidate.candidate_id for c in self.candidates):
            raise ValueError("Candidate with this ID already exists in the election")

        self._candidates.append(candidate)

    def remove_candidate(self, candidate_id: str) -> None:
        """Remove a candidate from the election"""
        if self.status != ElectionStatus.SCHEDULED:
            raise ValueError("Cannot remove candidates from non-scheduled elections")

        self._candidates = [c for c in self._candidates if c.candidate_id != candidate_id]

        if len(self._candidates) < 2:
            raise ValueError("Election must have at least 2 candidates")

    def increment_vote_count(self) -> None:
        """Increment the total vote count"""
        self._total_votes_cast += 1

    def __str__(self) -> str:
        return f"Election(id={self.election_id}, title={self.title}, status={self.status.value})"


class Vote(AbstractVote):
    """Represents a single vote cast by a user"""

    def __init__(self, vote_id: str, user_id: str, election_id: str,
                 candidate_id: str, timestamp: Optional[datetime] = None) -> None:
        """Initialize a vote with validation"""
        super().__init__(vote_id, user_id, election_id, candidate_id, timestamp)
        self._validate_vote_data(vote_id, user_id, election_id, candidate_id)

    def _validate_vote_data(self, vote_id: str, user_id: str,
                           election_id: str, candidate_id: str) -> None:
        """Validate vote data during initialization"""
        if not vote_id or not isinstance(vote_id, str) or not vote_id.strip():
            raise ValueError("Vote ID must be a non-empty string")

        if not user_id or not isinstance(user_id, str) or not user_id.strip():
            raise ValueError("User ID is required")

        if not election_id or not isinstance(election_id, str) or not election_id.strip():
            raise ValueError("Election ID is required")

        if not candidate_id or not isinstance(candidate_id, str) or not candidate_id.strip():
            raise ValueError("Candidate ID is required")

    def validate(self) -> None:
        """Validate vote data"""
        self._validate_vote_data(self.vote_id, self.user_id, self.election_id, self.candidate_id)

    def verify_vote(self) -> None:
        """Mark vote as verified"""
        self._status = VoteStatus.VERIFIED

    def invalidate_vote(self) -> None:
        """Mark vote as invalid"""
        self._status = VoteStatus.INVALID

    def is_valid(self) -> bool:
        """Check if vote is valid"""
        return self.status in [VoteStatus.CAST, VoteStatus.VERIFIED]

    def __str__(self) -> str:
        return f"Vote(id={self.vote_id}, user={self.user_id}, candidate={self.candidate_id}, status={self.status.value})"


class AbstractVotingBooth(AbstractEntity):
    """Abstract base class for VotingBooth entity"""

    def __init__(self, booth_id: str, location: str, capacity: int) -> None:
        """Initialize abstract voting booth"""
        super().__init__(booth_id)
        self._location = location
        self._capacity = capacity
        self._is_active = True
        self._current_occupancy = 0
        self._assigned_machine_ids: List[str] = []

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def booth_id(self) -> str:
        return self._entity_id

    @property
    def location(self) -> str:
        return self._location

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def current_occupancy(self) -> int:
        return self._current_occupancy

    @property
    def assigned_machine_ids(self) -> List[str]:
        return self._assigned_machine_ids

    @abstractmethod
    def can_accommodate_voter(self) -> bool:
        """Check if booth can accommodate another voter"""
        pass

    @abstractmethod
    def add_voter(self) -> None:
        """Add a voter to the booth"""
        pass

    @abstractmethod
    def remove_voter(self) -> None:
        """Remove a voter from the booth"""
        pass

    @abstractmethod
    def assign_machine(self, machine_id: str) -> None:
        """Assign a voting machine to this booth"""
        pass

    @abstractmethod
    def remove_machine(self, machine_id: str) -> None:
        """Remove a voting machine from this booth"""
        pass


class VotingBooth(AbstractVotingBooth):
    """Represents a physical voting booth location"""

    def __init__(self, booth_id: str, location: str, capacity: int) -> None:
        """Initialize a voting booth with validation"""
        super().__init__(booth_id, location, capacity)
        self._validate_booth_data(booth_id, location, capacity)

    def _validate_booth_data(self, booth_id: str, location: str, capacity: int) -> None:
        """Validate booth data during initialization"""
        if not booth_id or not isinstance(booth_id, str):
            raise ValueError("Booth ID must be a non-empty string")

        if not location or not isinstance(location, str):
            raise ValueError("Location is required")

        if not isinstance(capacity, int) or capacity <= 0:
            raise ValueError("Capacity must be a positive integer")

    def validate(self) -> None:
        """Validate booth data"""
        self._validate_booth_data(self.booth_id, self.location, self.capacity)

    def can_accommodate_voter(self) -> bool:
        """Check if booth can accommodate another voter"""
        return self.is_active and self.current_occupancy < self.capacity

    def add_voter(self) -> None:
        """Add a voter to the booth"""
        if not self.can_accommodate_voter():
            raise ValueError("Booth is at full capacity")

        self._current_occupancy += 1

    def remove_voter(self) -> None:
        """Remove a voter from the booth"""
        if self.current_occupancy > 0:
            self._current_occupancy -= 1

    def assign_machine(self, machine_id: str) -> None:
        """Assign a voting machine to this booth"""
        if machine_id not in self.assigned_machine_ids:
            self._assigned_machine_ids.append(machine_id)

    def remove_machine(self, machine_id: str) -> None:
        """Remove a voting machine from this booth"""
        if machine_id in self.assigned_machine_ids:
            self._assigned_machine_ids.remove(machine_id)

    @property
    def occupancy(self) -> int:
        """Get current occupancy (alias for current_occupancy)"""
        return self.current_occupancy

    def increase_occupancy(self) -> None:
        """Increase occupancy by one (alias for add_voter)"""
        self.add_voter()

    def decrease_occupancy(self) -> None:
        """Decrease occupancy by one (alias for remove_voter)"""
        self.remove_voter()

    def is_full(self) -> bool:
        """Check if booth is at full capacity"""
        return self.current_occupancy >= self.capacity

    def deactivate(self) -> None:
        """Deactivate the booth"""
        self._is_active = False

    def activate(self) -> None:
        """Activate the booth"""
        self._is_active = True

    def __str__(self) -> str:
        return f"VotingBooth(id={self.booth_id}, location={self.location}, occupancy={self.current_occupancy}/{self.capacity})"


class AbstractVotingMachine(AbstractEntity):
    """Abstract base class for VotingMachine entity"""

    def __init__(self, machine_id: str, booth_id: str, model: str) -> None:
        """Initialize abstract voting machine"""
        super().__init__(machine_id)
        self._booth_id = booth_id
        self._model = model
        self._is_active = True
        self._is_in_use = False
        self._total_votes_processed = 0
        self._last_maintenance_date: Optional[datetime] = None

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def machine_id(self) -> str:
        return self._entity_id

    @property
    def booth_id(self) -> str:
        return self._booth_id

    @property
    def model(self) -> str:
        return self._model

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def is_in_use(self) -> bool:
        return self._is_in_use

    @property
    def total_votes_processed(self) -> int:
        return self._total_votes_processed

    @property
    def last_maintenance_date(self) -> Optional[datetime]:
        return self._last_maintenance_date

    @abstractmethod
    def start_voting_session(self) -> None:
        """Start a voting session on this machine"""
        pass

    @abstractmethod
    def end_voting_session(self) -> None:
        """End the current voting session"""
        pass

    @abstractmethod
    def perform_maintenance(self) -> None:
        """Perform maintenance on the machine"""
        pass

    @abstractmethod
    def deactivate(self) -> None:
        """Deactivate the machine"""
        pass


class VotingMachine(AbstractVotingMachine):
    """Represents a voting machine"""

    def __init__(self, machine_id: str, model: str, booth_id: str = None) -> None:
        """Initialize a voting machine with validation"""
        super().__init__(machine_id, booth_id or "", model)
        self._validate_machine_data(machine_id, booth_id or "", model)
        self._created_at = datetime.now()

    def _validate_machine_data(self, machine_id: str, booth_id: str, model: str) -> None:
        """Validate machine data during initialization"""
        if not machine_id or not isinstance(machine_id, str):
            raise ValueError("Machine ID must be a non-empty string")

        # Booth ID is optional in the simplified constructor
        if booth_id and not isinstance(booth_id, str):
            raise ValueError("Booth ID must be a string if provided")

        if not model or not isinstance(model, str):
            raise ValueError("Machine model is required")

    def validate(self) -> None:
        """Validate machine data"""
        self._validate_machine_data(self.machine_id, self.booth_id, self.model)

    @property
    def assigned_booth_id(self) -> Optional[str]:
        """Get assigned booth ID (alias for booth_id, returns None if empty)"""
        return self.booth_id if self.booth_id else None

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp"""
        return self._created_at

    def start_voting_session(self) -> None:
        """Start a voting session on this machine"""
        if not self.is_active:
            raise ValueError("Cannot start session on inactive machine")

        if self.is_in_use:
            raise ValueError("Machine is already in use")

        self._is_in_use = True

    def end_voting_session(self) -> None:
        """End the current voting session"""
        self._is_in_use = False
        self._total_votes_processed += 1

    def perform_maintenance(self) -> None:
        """Perform maintenance on the machine"""
        self._last_maintenance_date = datetime.now()

    def deactivate(self) -> None:
        """Deactivate the machine"""
        self._is_active = False
        self._is_in_use = False

    def __str__(self) -> str:
        return f"VotingMachine(id={self.machine_id}, model={self.model}, active={self.is_active})"


class AbstractVotingResult(AbstractEntity):
    """Abstract base class for VotingResult entity"""

    def __init__(self, election_id: str) -> None:
        """Initialize abstract voting result"""
        super().__init__(election_id)
        self._candidate_votes: Dict[str, int] = {}
        self._total_votes = 0
        self._voting_percentage = 0.0
        self._winner_candidate_id: Optional[str] = None
        self._generated_at = datetime.now()

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def election_id(self) -> str:
        return self._entity_id

    @property
    def candidate_votes(self) -> Dict[str, int]:
        return self._candidate_votes

    @property
    def total_votes(self) -> int:
        return self._total_votes

    @property
    def voting_percentage(self) -> float:
        return self._voting_percentage

    @property
    def winner_candidate_id(self) -> Optional[str]:
        return self._winner_candidate_id

    @property
    def generated_at(self) -> datetime:
        return self._generated_at

    @abstractmethod
    def add_vote(self, candidate_id: str) -> None:
        """Add a vote for a candidate"""
        pass

    @abstractmethod
    def get_candidate_vote_count(self, candidate_id: str) -> int:
        """Get vote count for a specific candidate"""
        pass

    @abstractmethod
    def get_all_results(self) -> Dict[str, int]:
        """Get all candidate results"""
        pass

    @abstractmethod
    def set_voting_percentage(self, percentage: float) -> None:
        """Set the voting percentage"""
        pass


class AbstractVotingRecord(AbstractEntity):
    """Abstract base class for VotingRecord entity"""

    def __init__(self, election_id: str) -> None:
        """Initialize abstract voting record"""
        super().__init__(election_id)
        self._votes: List[Vote] = []
        self._user_votes: Dict[str, Vote] = {}
        self._created_at = datetime.now()
        self._lock = threading.Lock()

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def election_id(self) -> str:
        return self._entity_id

    @property
    def votes(self) -> List[Vote]:
        return self._votes

    @property
    def user_votes(self) -> Dict[str, Vote]:
        return self._user_votes

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @abstractmethod
    def add_vote(self, vote: Vote) -> None:
        """Add a vote to the record"""
        pass

    @abstractmethod
    def get_vote_by_user(self, user_id: str) -> Optional[Vote]:
        """Get vote by user ID"""
        pass

    @abstractmethod
    def get_all_votes(self) -> List[Vote]:
        """Get all votes in the record"""
        pass

    @abstractmethod
    def get_vote_count(self) -> int:
        """Get total number of votes"""
        pass

    @abstractmethod
    def has_user_voted(self, user_id: str) -> bool:
        """Check if a user has voted"""
        pass


class AbstractVotingSystem(AbstractEntity):
    """Abstract base class for VotingSystem entity"""

    def __init__(self, system_id: str, name: str) -> None:
        """Initialize abstract voting system"""
        super().__init__(system_id)
        self._name = name
        self._is_active = True
        self._created_at = datetime.now()
        self._total_elections = 0
        self._total_users = 0
        self._total_votes_cast = 0

    @property
    def entity_id(self) -> str:
        return self._entity_id

    @property
    def system_id(self) -> str:
        return self._entity_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def total_elections(self) -> int:
        return self._total_elections

    @property
    def total_users(self) -> int:
        return self._total_users

    @property
    def total_votes_cast(self) -> int:
        return self._total_votes_cast

    @abstractmethod
    def increment_election_count(self) -> None:
        """Increment the total election count"""
        pass

    @abstractmethod
    def increment_user_count(self) -> None:
        """Increment the total user count"""
        pass

    @abstractmethod
    def increment_vote_count(self) -> None:
        """Increment the total vote count"""
        pass

    @abstractmethod
    def deactivate(self) -> None:
        """Deactivate the voting system"""
        pass

    @abstractmethod
    def activate(self) -> None:
        """Activate the voting system"""
        pass


class VotingResult(AbstractVotingResult):
    """Represents the results of an election"""

    def __init__(self, election_id: str) -> None:
        """Initialize voting results for an election"""
        super().__init__(election_id)

    def validate(self) -> None:
        """Validate result data"""
        if self.election_id is None or self.election_id == "":
            raise ValueError("Election ID is required")

    def add_vote(self, candidate_id: str) -> None:
        """Add a vote for a candidate"""
        if candidate_id not in self.candidate_votes:
            self._candidate_votes[candidate_id] = 0

        self._candidate_votes[candidate_id] += 1
        self._total_votes += 1
        self._calculate_winner()

    def get_candidate_vote_count(self, candidate_id: str) -> int:
        """Get vote count for a specific candidate"""
        return self.candidate_votes.get(candidate_id, 0)

    def get_all_results(self) -> Dict[str, int]:
        """Get all candidate results"""
        return self.candidate_votes.copy()

    def _calculate_winner(self) -> None:
        """Calculate the winner based on current votes"""
        if not self.candidate_votes:
            self._winner_candidate_id = None
            return

        self._winner_candidate_id = max(self.candidate_votes.keys(),
                                        key=lambda x: self.candidate_votes[x])

    def set_voting_percentage(self, percentage: float) -> None:
        """Set the voting percentage"""
        if not 0 <= percentage <= 100:
            raise ValueError("Voting percentage must be between 0 and 100")
        self._voting_percentage = percentage

    def __str__(self) -> str:
        return f"VotingResult(election={self.election_id}, total_votes={self.total_votes}, winner={self.winner_candidate_id})"


class VotingRecord(AbstractVotingRecord):
    """Represents a complete record of all votes in an election"""

    def __init__(self, election_id: str) -> None:
        """Initialize a voting record for an election"""
        super().__init__(election_id)

    def validate(self) -> None:
        """Validate record data"""
        if self.election_id is None or self.election_id == "":
            raise ValueError("Election ID is required")

    def add_vote(self, vote: Vote) -> None:
        """Add a vote to the record"""
        with self._lock:
            if vote.user_id in self.user_votes:
                raise ValueError(f"User {vote.user_id} has already voted in this election")

            self._votes.append(vote)
            self._user_votes[vote.user_id] = vote

    def get_vote_by_user(self, user_id: str) -> Optional[Vote]:
        """Get vote by user ID"""
        with self._lock:
            return self.user_votes.get(user_id)

    def get_all_votes(self) -> List[Vote]:
        """Get all votes in the record"""
        with self._lock:
            return self.votes.copy()

    def get_vote_count(self) -> int:
        """Get total number of votes"""
        with self._lock:
            return len(self.votes)

    def has_user_voted(self, user_id: str) -> bool:
        """Check if a user has voted"""
        with self._lock:
            return user_id in self.user_votes

    def __str__(self) -> str:
        return f"VotingRecord(election={self.election_id}, votes={len(self.votes)})"


class VotingSystem(AbstractVotingSystem):
    """Represents the overall voting system"""

    def __init__(self, system_id: str, name: str) -> None:
        """Initialize the voting system"""
        super().__init__(system_id, name)

    def validate(self) -> None:
        """Validate system data"""
        if self.system_id is None or self.system_id == "":
            raise ValueError("System ID is required")
        if self.name is None or self.name == "":
            raise ValueError("System name is required")

    def increment_election_count(self) -> None:
        """Increment the total election count"""
        self._total_elections += 1

    def increment_user_count(self) -> None:
        """Increment the total user count"""
        self._total_users += 1

    def increment_vote_count(self) -> None:
        """Increment the total vote count"""
        self._total_votes_cast += 1

    def deactivate(self) -> None:
        """Deactivate the voting system"""
        self._is_active = False

    def activate(self) -> None:
        """Activate the voting system"""
        self._is_active = True

    @property
    def total_votes(self) -> int:
        """Get total votes cast (alias for total_votes_cast)"""
        return self.total_votes_cast

    def update_statistics(self, users: int = 0, elections: int = 0, votes: int = 0) -> None:
        """Update system statistics"""
        for _ in range(users):
            self.increment_user_count()
        for _ in range(elections):
            self.increment_election_count()
        for _ in range(votes):
            self.increment_vote_count()

    def __str__(self) -> str:
        return f"VotingSystem(id={self.system_id}, name={self.name}, active={self.is_active})"
