"""
Integration tests for complete voting workflow.

Tests cover:
- End-to-end voting process
- User registration to vote casting
- Election lifecycle management
- System integration
- Error scenarios in workflows
"""

import pytest
from datetime import datetime, timedelta
from entities import User, Candidate, Election, Vote, ElectionStatus, VoteStatus


@pytest.mark.integration
class TestVotingWorkflowIntegration:
    """Integration tests for complete voting workflows"""

    def test_complete_voting_workflow(self, orchestrator):
        """Test complete voting workflow from user registration to results"""
        # Phase 1: User Registration
        user = orchestrator.register_user("John Doe", "john@example.com", 30)
        assert user is not None
        assert user.status.name == "ACTIVE"

        # Phase 2: Candidate Registration
        candidate1 = orchestrator.register_candidate("Jane Smith", "Democratic Party", "Education focus")
        candidate2 = orchestrator.register_candidate("Bob Johnson", "Republican Party", "Economy focus")
        assert candidate1 is not None
        assert candidate2 is not None

        # Phase 3: Election Creation
        now = datetime.now()
        election = orchestrator.create_election(
            title="City Mayor Election",
            description="Vote for your next mayor",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=24),
            candidate_ids=[candidate1.candidate_id, candidate2.candidate_id]
        )
        assert election is not None
        assert len(election.candidate_ids) == 2

        # Phase 4: Start Election
        success = orchestrator.start_election(election.election_id)
        assert success is True

        # Verify election is active
        active_election = orchestrator.get_election_by_id(election.election_id)
        assert active_election.status == ElectionStatus.ACTIVE

        # Phase 5: Cast Vote
        vote = orchestrator.cast_vote(user.user_id, election.election_id, candidate1.candidate_id)
        assert vote is not None
        assert vote.user_id == user.user_id
        assert vote.election_id == election.election_id
        assert vote.candidate_id == candidate1.candidate_id
        assert vote.status == VoteStatus.CAST

        # Phase 6: End Election
        end_success = orchestrator.end_election(election.election_id)
        assert end_success is True

        # Verify election is completed
        completed_election = orchestrator.get_election_by_id(election.election_id)
        assert completed_election.status == ElectionStatus.COMPLETED

        # Phase 7: Get Results
        results = orchestrator.get_election_results(election.election_id)
        assert results is not None
        assert results["total_votes"] == 1
        assert results["candidate_1"] == 1

    def test_multiple_users_voting_workflow(self, orchestrator):
        """Test workflow with multiple users voting"""
        # Register multiple users
        users = []
        for i in range(5):
            user = orchestrator.register_user(f"User {i}", f"user{i}@example.com", 25 + i)
            users.append(user)

        # Register candidates
        candidate1 = orchestrator.register_candidate("Candidate A", "Party A", "Platform A")
        candidate2 = orchestrator.register_candidate("Candidate B", "Party B", "Platform B")

        # Create election
        now = datetime.now()
        election = orchestrator.create_election(
            title="Multi-User Election",
            description="Testing multiple votes",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=[candidate1.candidate_id, candidate2.candidate_id]
        )

        # Start election
        orchestrator.start_election(election.election_id)

        # Cast votes (some for candidate1, some for candidate2)
        votes = []
        for i, user in enumerate(users):
            candidate_id = candidate1.candidate_id if i % 2 == 0 else candidate2.candidate_id
            vote = orchestrator.cast_vote(user.user_id, election.election_id, candidate_id)
            votes.append(vote)

        # Verify all votes were cast
        assert len(votes) == 5
        for vote in votes:
            assert vote.status == VoteStatus.CAST

        # End election and check results
        orchestrator.end_election(election.election_id)
        results = orchestrator.get_election_results(election.election_id)

        assert results["total_votes"] == 5
        # Should have 3 votes for candidate1 (indices 0, 2, 4) and 2 for candidate2 (indices 1, 3)
        assert results[candidate1.candidate_id] == 3
        assert results[candidate2.candidate_id] == 2

    def test_election_without_candidates(self, orchestrator):
        """Test attempting to create election without candidates"""
        now = datetime.now()

        with pytest.raises(ValueError, match="Election must have at least 2 candidates"):
            orchestrator.create_election(
                title="Invalid Election",
                description="Should fail",
                start_date=now + timedelta(hours=1),
                end_date=now + timedelta(hours=2),
                candidate_ids=[]
            )

    def test_voting_before_election_starts(self, orchestrator):
        """Test attempting to vote before election starts"""
        # Setup
        user = orchestrator.register_user("John Doe", "john@example.com", 30)
        candidate = orchestrator.register_candidate("Jane Smith", "Party", "Platform")

        now = datetime.now()
        election = orchestrator.create_election(
            title="Future Election",
            description="Starts in future",
            start_date=now + timedelta(hours=1),  # Starts in 1 hour
            end_date=now + timedelta(hours=2),
            candidate_ids=[candidate.candidate_id]
        )

        # Try to vote before election starts
        with pytest.raises(ValueError, match="Election is not active"):
            orchestrator.cast_vote(user.user_id, election.election_id, candidate.candidate_id)

    def test_voting_after_election_ends(self, orchestrator):
        """Test attempting to vote after election ends"""
        # Setup
        user = orchestrator.register_user("John Doe", "john@example.com", 30)
        candidate = orchestrator.register_candidate("Jane Smith", "Party", "Platform")

        now = datetime.now()
        election = orchestrator.create_election(
            title="Past Election",
            description="Already ended",
            start_date=now - timedelta(hours=2),
            end_date=now - timedelta(hours=1),  # Ended 1 hour ago
            candidate_ids=[candidate.candidate_id]
        )

        # Try to vote after election ends
        with pytest.raises(ValueError, match="Election is not active"):
            orchestrator.cast_vote(user.user_id, election.election_id, candidate.candidate_id)

    def test_duplicate_vote_prevention(self, orchestrator):
        """Test that users cannot vote multiple times in same election"""
        # Setup
        user = orchestrator.register_user("John Doe", "john@example.com", 30)
        candidate1 = orchestrator.register_candidate("Candidate A", "Party A", "Platform A")
        candidate2 = orchestrator.register_candidate("Candidate B", "Party B", "Platform B")

        now = datetime.now()
        election = orchestrator.create_election(
            title="Single Vote Election",
            description="Each user can vote only once",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=[candidate1.candidate_id, candidate2.candidate_id]
        )

        orchestrator.start_election(election.election_id)

        # Cast first vote
        vote1 = orchestrator.cast_vote(user.user_id, election.election_id, candidate1.candidate_id)
        assert vote1 is not None

        # Try to cast second vote - should fail
        with pytest.raises(ValueError, match="User has already voted in this election"):
            orchestrator.cast_vote(user.user_id, election.election_id, candidate2.candidate_id)

    def test_invalid_candidate_vote(self, orchestrator):
        """Test voting for candidate not in election"""
        # Setup
        user = orchestrator.register_user("John Doe", "john@example.com", 30)
        candidate1 = orchestrator.register_candidate("Candidate A", "Party A", "Platform A")
        candidate2 = orchestrator.register_candidate("Candidate B", "Party B", "Platform B")  # Not in election

        now = datetime.now()
        election = orchestrator.create_election(
            title="Limited Candidates",
            description="Only candidate A can be voted for",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=[candidate1.candidate_id]  # Only candidate1
        )

        orchestrator.start_election(election.election_id)

        # Try to vote for candidate not in election
        with pytest.raises(ValueError, match="Invalid candidate for this election"):
            orchestrator.cast_vote(user.user_id, election.election_id, candidate2.candidate_id)

    def test_user_not_found_voting(self, orchestrator):
        """Test voting with non-existent user"""
        candidate = orchestrator.register_candidate("Jane Smith", "Party", "Platform")

        now = datetime.now()
        election = orchestrator.create_election(
            title="Test Election",
            description="For testing",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=[candidate.candidate_id]
        )

        orchestrator.start_election(election.election_id)

        # Try to vote with non-existent user
        with pytest.raises(ValueError, match="User not found"):
            orchestrator.cast_vote("nonexistent_user", election.election_id, candidate.candidate_id)

    def test_election_not_found_voting(self, orchestrator):
        """Test voting in non-existent election"""
        user = orchestrator.register_user("John Doe", "john@example.com", 30)
        candidate = orchestrator.register_candidate("Jane Smith", "Party", "Platform")

        # Try to vote in non-existent election
        with pytest.raises(ValueError, match="Election not found"):
            orchestrator.cast_vote(user.user_id, "nonexistent_election", candidate.candidate_id)

    def test_candidate_not_found_voting(self, orchestrator):
        """Test voting for non-existent candidate"""
        user = orchestrator.register_user("John Doe", "john@example.com", 30)

        now = datetime.now()
        election = orchestrator.create_election(
            title="Test Election",
            description="For testing",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=["candidate_123"]  # Non-existent candidate
        )

        orchestrator.start_election(election.election_id)

        # Try to vote for non-existent candidate
        with pytest.raises(ValueError, match="Candidate not found"):
            orchestrator.cast_vote(user.user_id, election.election_id, "nonexistent_candidate")

    def test_election_state_transitions(self, orchestrator):
        """Test proper election state transitions during workflow"""
        # Setup
        candidate = orchestrator.register_candidate("Jane Smith", "Party", "Platform")

        now = datetime.now()
        election = orchestrator.create_election(
            title="State Test Election",
            description="Testing state transitions",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=[candidate.candidate_id]
        )

        # Initially scheduled
        assert election.status == ElectionStatus.SCHEDULED

        # Start election
        orchestrator.start_election(election.election_id)
        started_election = orchestrator.get_election_by_id(election.election_id)
        assert started_election.status == ElectionStatus.ACTIVE

        # End election
        orchestrator.end_election(election.election_id)
        ended_election = orchestrator.get_election_by_id(election.election_id)
        assert ended_election.status == ElectionStatus.COMPLETED

    def test_concurrent_voting_simulation(self, orchestrator):
        """Test concurrent voting simulation"""
        import threading
        import time

        # Setup
        candidate = orchestrator.register_candidate("Jane Smith", "Party", "Platform")

        now = datetime.now()
        election = orchestrator.create_election(
            title="Concurrent Election",
            description="Testing concurrent votes",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=[candidate.candidate_id]
        )

        orchestrator.start_election(election.election_id)

        # Create multiple users and votes
        results = []
        errors = []

        def cast_vote_worker(user_id):
            try:
                user = orchestrator.register_user(f"User {user_id}", f"user{user_id}@example.com", 25)
                vote = orchestrator.cast_vote(user.user_id, election.election_id, candidate.candidate_id)
                results.append(vote)
            except Exception as e:
                errors.append(str(e))

        # Start concurrent voting
        threads = []
        for i in range(10):
            thread = threading.Thread(target=cast_vote_worker, args=[i])
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # Verify results
        assert len(results) == 10
        assert len(errors) == 0

        # End election and check results
        orchestrator.end_election(election.election_id)
        final_results = orchestrator.get_election_results(election.election_id)

        assert final_results["total_votes"] == 10
        assert final_results[candidate.candidate_id] == 10

    def test_system_statistics_tracking(self, orchestrator):
        """Test that system properly tracks statistics throughout workflow"""
        # Initial state
        initial_stats = orchestrator.get_system_statistics()
        assert initial_stats["total_users"] == 0
        assert initial_stats["total_elections"] == 0

        # Add users
        users = []
        for i in range(3):
            user = orchestrator.register_user(f"User {i}", f"user{i}@example.com", 25 + i)
            users.append(user)

        # Add candidates
        candidates = []
        for i in range(2):
            candidate = orchestrator.register_candidate(f"Candidate {i}", f"Party {i}", f"Platform {i}")
            candidates.append(candidate)

        # Create election
        now = datetime.now()
        election = orchestrator.create_election(
            title="Statistics Test Election",
            description="Testing statistics tracking",
            start_date=now + timedelta(minutes=1),
            end_date=now + timedelta(hours=1),
            candidate_ids=[c.candidate_id for c in candidates]
        )

        # Start election
        orchestrator.start_election(election.election_id)

        # Cast votes
        for user in users:
            candidate_id = candidates[0].candidate_id  # All vote for first candidate
            orchestrator.cast_vote(user.user_id, election.election_id, candidate_id)

        # End election
        orchestrator.end_election(election.election_id)

        # Check final statistics
        final_stats = orchestrator.get_system_statistics()
        assert final_stats["total_users"] == 3
        assert final_stats["total_elections"] == 1
        assert final_stats["total_votes"] == 3
        assert final_stats["active_elections"] == 0  # Election ended
        assert final_stats["completed_elections"] == 1
