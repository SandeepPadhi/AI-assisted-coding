"""
Unit tests for Election entity.

Tests cover:
- Election creation and validation
- Status management and transitions
- Candidate management
- Voting period validation
- Business logic validation
- Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta
from entities import Election, ElectionStatus


class TestElectionEntity:
    """Test cases for Election entity"""

    def test_election_creation_valid_data(self, sample_election_data):
        """Test successful election creation with valid data"""
        election = Election(**sample_election_data)

        assert election.election_id == sample_election_data["election_id"]
        assert election.title == sample_election_data["title"]
        assert election.description == sample_election_data["description"]
        assert election.start_date == sample_election_data["start_date"]
        assert election.end_date == sample_election_data["end_date"]
        assert election.candidate_ids == sample_election_data["candidate_ids"]
        assert election.status == ElectionStatus.SCHEDULED
        assert election.created_at is not None
        assert election.updated_at is not None
        assert election.total_votes == 0
        assert election.results == {}

    def test_election_creation_invalid_election_id(self):
        """Test election creation with invalid election ID"""
        now = datetime.now()
        with pytest.raises(ValueError, match="Invalid election ID"):
            Election("", "Title", "Description", now, now + timedelta(hours=1), ["c1"])

        with pytest.raises(ValueError, match="Invalid election ID"):
            Election("   ", "Title", "Description", now, now + timedelta(hours=1), ["c1"])

    def test_election_creation_invalid_title(self):
        """Test election creation with invalid title"""
        now = datetime.now()
        with pytest.raises(ValueError, match="Invalid title"):
            Election("election_123", "", "Description", now, now + timedelta(hours=1), ["c1"])

        with pytest.raises(ValueError, match="Invalid title"):
            Election("election_123", "   ", "Description", now, now + timedelta(hours=1), ["c1"])

    def test_election_creation_invalid_description(self):
        """Test election creation with invalid description"""
        now = datetime.now()
        with pytest.raises(ValueError, match="Invalid description"):
            Election("election_123", "Title", "", now, now + timedelta(hours=1), ["c1"])

        with pytest.raises(ValueError, match="Invalid description"):
            Election("election_123", "Title", "   ", now, now + timedelta(hours=1), ["c1"])

    def test_election_creation_invalid_dates(self):
        """Test election creation with invalid dates"""
        now = datetime.now()

        # End date before start date
        with pytest.raises(ValueError, match="End date must be after start date"):
            Election("election_123", "Title", "Description", now, now - timedelta(hours=1), ["c1"])

        # Start date in the past
        with pytest.raises(ValueError, match="Start date cannot be in the past"):
            Election("election_123", "Title", "Description", now - timedelta(hours=1), now, ["c1"])

    def test_election_creation_invalid_candidates(self):
        """Test election creation with invalid candidates"""
        now = datetime.now()
        future = now + timedelta(hours=1)

        # Empty candidate list
        with pytest.raises(ValueError, match="Election must have at least 2 candidates"):
            Election("election_123", "Title", "Description", now, future, [])

        # Single candidate
        with pytest.raises(ValueError, match="Election must have at least 2 candidates"):
            Election("election_123", "Title", "Description", now, future, ["c1"])

        # Invalid candidate IDs
        with pytest.raises(ValueError, match="Invalid candidate ID"):
            Election("election_123", "Title", "Description", now, future, ["c1", ""])

    def test_election_status_transitions(self, sample_election):
        """Test election status transitions"""
        # Start as scheduled
        assert sample_election.status == ElectionStatus.SCHEDULED

        # Start election
        sample_election.start_election()
        assert sample_election.status == ElectionStatus.ACTIVE

        # Complete election
        sample_election.complete_election()
        assert sample_election.status == ElectionStatus.COMPLETED

    def test_election_status_transition_invalid(self, sample_election):
        """Test invalid election status transitions"""
        # Cannot complete a scheduled election
        with pytest.raises(ValueError, match="Cannot complete election that is not active"):
            sample_election.complete_election()

        # Cannot start an already started election
        sample_election.start_election()
        with pytest.raises(ValueError, match="Election is not scheduled"):
            sample_election.start_election()

        # Cannot complete an already completed election
        sample_election.complete_election()
        with pytest.raises(ValueError, match="Cannot complete election that is not active"):
            sample_election.complete_election()

    def test_election_cancel(self, sample_election):
        """Test election cancellation"""
        assert sample_election.status == ElectionStatus.SCHEDULED

        sample_election.cancel_election()
        assert sample_election.status == ElectionStatus.CANCELLED

        # Cannot cancel already cancelled election
        with pytest.raises(ValueError, match="Election is not scheduled or active"):
            sample_election.cancel_election()

    def test_election_candidate_management(self, sample_election):
        """Test election candidate management"""
        original_candidates = sample_election.candidate_ids.copy()

        # Add candidate
        sample_election.add_candidate("candidate_new")
        assert "candidate_new" in sample_election.candidate_ids
        assert len(sample_election.candidate_ids) == len(original_candidates) + 1

        # Remove candidate
        sample_election.remove_candidate("candidate_new")
        assert "candidate_new" not in sample_election.candidate_ids
        assert sample_election.candidate_ids == original_candidates

    def test_election_candidate_management_invalid(self, sample_election):
        """Test invalid candidate management operations"""
        # Add invalid candidate
        with pytest.raises(ValueError, match="Invalid candidate ID"):
            sample_election.add_candidate("")

        # Remove non-existent candidate
        with pytest.raises(ValueError, match="Candidate not found in election"):
            sample_election.remove_candidate("non_existent")

        # Remove when only 2 candidates left
        sample_election.candidate_ids = ["c1", "c2"]
        with pytest.raises(ValueError, match="Election must have at least 2 candidates"):
            sample_election.remove_candidate("c1")

    def test_election_voting_period_validation(self):
        """Test election voting period validation"""
        now = datetime.now()
        future = now + timedelta(hours=1)

        # Create election starting in future
        election = Election("e1", "Title", "Desc", future, future + timedelta(hours=24), ["c1", "c2"])

        # Should not be votable yet
        assert not election.is_voting_open()
        assert election.is_voting_upcoming()

        # Simulate current time as during voting period
        during_voting = future + timedelta(hours=1)
        assert election.is_voting_open(at_time=during_voting)

        # Simulate current time as after voting period
        after_voting = future + timedelta(hours=25)
        assert not election.is_voting_open(at_time=after_voting)
        assert election.is_voting_ended(at_time=after_voting)

    def test_election_vote_recording(self, sample_election):
        """Test election vote recording"""
        # Start the election first
        sample_election.start_election()
        assert sample_election.status == ElectionStatus.ACTIVE

        # Record votes
        sample_election.record_vote("candidate_1")
        assert sample_election.total_votes == 1
        assert sample_election.results["candidate_1"] == 1

        sample_election.record_vote("candidate_1")
        assert sample_election.total_votes == 2
        assert sample_election.results["candidate_1"] == 2

        sample_election.record_vote("candidate_2")
        assert sample_election.total_votes == 3
        assert sample_election.results["candidate_2"] == 1

    def test_election_vote_recording_invalid(self, sample_election):
        """Test invalid vote recording"""
        # Cannot record votes when election is not active
        with pytest.raises(ValueError, match="Cannot record votes for inactive election"):
            sample_election.record_vote("candidate_1")

        # Start election
        sample_election.start_election()

        # Cannot record vote for invalid candidate
        with pytest.raises(ValueError, match="Invalid candidate ID"):
            sample_election.record_vote("invalid_candidate")

        with pytest.raises(ValueError, match="Candidate not in election"):
            sample_election.record_vote("candidate_not_in_election")

    def test_election_results_calculation(self, sample_election):
        """Test election results calculation"""
        # Start election and record votes
        sample_election.start_election()

        sample_election.record_vote("candidate_1")  # 2 votes
        sample_election.record_vote("candidate_1")
        sample_election.record_vote("candidate_2")  # 1 vote

        # Calculate results
        results = sample_election.calculate_results()
        expected = {
            "candidate_1": 2,
            "candidate_2": 1,
            "total_votes": 3,
            "winner": "candidate_1"
        }
        assert results == expected

    def test_election_tie_handling(self, sample_election):
        """Test election tie handling"""
        # Start election and create a tie
        sample_election.start_election()

        sample_election.record_vote("candidate_1")  # 1 vote
        sample_election.record_vote("candidate_2")  # 1 vote

        # Calculate results
        results = sample_election.calculate_results()
        expected = {
            "candidate_1": 1,
            "candidate_2": 1,
            "total_votes": 2,
            "winner": None,  # Tie
            "tied_candidates": ["candidate_1", "candidate_2"]
        }
        assert results == expected

    def test_election_string_representation(self, sample_election):
        """Test election string representation"""
        expected = f"Election(id={sample_election.election_id}, title={sample_election.title}, status={sample_election.status.value})"
        assert str(sample_election) == expected

    def test_election_equality(self, sample_election_data):
        """Test election equality comparison"""
        election1 = Election(**sample_election_data)
        election2 = Election(**sample_election_data)
        election3 = Election("different_id", "Different Title", "Different Desc",
                           datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=2),
                           ["c1", "c2"])

        assert election1 == election2
        assert election1 != election3
        assert election1 != "not_an_election"

    def test_election_hash(self, sample_election_data):
        """Test election hash function"""
        election1 = Election(**sample_election_data)
        election2 = Election(**sample_election_data)

        assert hash(election1) == hash(election2)
        assert hash(election1) == hash(sample_election_data["election_id"])

    def test_election_time_boundary_cases(self):
        """Test election time boundary cases"""
        now = datetime.now()

        # Election starting exactly now (should be valid)
        election = Election("e1", "Title", "Desc", now, now + timedelta(hours=1), ["c1", "c2"])
        assert election.start_date == now

        # Very short election (1 minute)
        election = Election("e2", "Title", "Desc", now + timedelta(minutes=1),
                           now + timedelta(minutes=2), ["c1", "c2"])
        assert election.is_voting_upcoming()

    def test_election_candidate_replacement(self, sample_election):
        """Test replacing candidates in election"""
        original_candidates = sample_election.candidate_ids.copy()

        # Replace a candidate
        sample_election.replace_candidate("candidate_1", "candidate_new")
        assert "candidate_1" not in sample_election.candidate_ids
        assert "candidate_new" in sample_election.candidate_ids

        # Cannot replace non-existent candidate
        with pytest.raises(ValueError, match="Candidate not found in election"):
            sample_election.replace_candidate("non_existent", "candidate_new2")

    def test_election_statistics(self, sample_election):
        """Test election statistics"""
        # Start election and record votes
        sample_election.start_election()

        sample_election.record_vote("candidate_1")
        sample_election.record_vote("candidate_2")
        sample_election.record_vote("candidate_1")

        stats = sample_election.get_statistics()
        assert stats["total_votes"] == 3
        assert stats["unique_candidates"] == 2
        assert stats["voting_percentage"] == 0.0  # No voters tracked
        assert "candidate_1" in stats["vote_distribution"]
        assert "candidate_2" in stats["vote_distribution"]
