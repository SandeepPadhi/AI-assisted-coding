"""
Unit tests for Vote Repository.

Tests cover:
- Vote CRUD operations
- Status-based queries
- User and election-based queries
- Verification status management
- Thread-safe operations
- Bulk operations
"""

import pytest
import threading
from datetime import datetime, timedelta
from entities import Vote, VoteStatus
from repositories import InMemoryVoteRepository


class TestInMemoryVoteRepository:
    """Test cases for InMemoryVoteRepository"""

    def test_repository_initialization(self, vote_repository):
        """Test repository initialization"""
        assert vote_repository is not None
        assert hasattr(vote_repository, '_storage')
        assert hasattr(vote_repository, '_lock')

    def test_save_vote_valid(self, vote_repository, sample_vote):
        """Test saving a valid vote"""
        vote_repository.save(sample_vote)

        assert sample_vote.vote_id in vote_repository._storage
        assert vote_repository._storage[sample_vote.vote_id] == sample_vote

    def test_find_by_id_existing(self, vote_repository, sample_vote):
        """Test finding existing vote by ID"""
        vote_repository.save(sample_vote)

        found_vote = vote_repository.find_by_id(sample_vote.vote_id)

        assert found_vote is not None
        assert found_vote == sample_vote

    def test_find_all_empty(self, vote_repository):
        """Test finding all votes when repository is empty"""
        votes = vote_repository.find_all()
        assert isinstance(votes, list)
        assert len(votes) == 0

    def test_find_all_with_votes(self, vote_repository):
        """Test finding all votes"""
        votes = []
        now = datetime.now()

        for i in range(3):
            vote = Vote(f"vote_{i}", f"user_{i}", f"election_{i}", f"candidate_{i}", now)
            votes.append(vote)
            vote_repository.save(vote)

        found_votes = vote_repository.find_all()
        assert len(found_votes) == 3
        assert set(found_votes) == set(votes)

    def test_exists_by_id(self, vote_repository, sample_vote):
        """Test checking if vote exists by ID"""
        assert not vote_repository.exists_by_id(sample_vote.vote_id)

        vote_repository.save(sample_vote)
        assert vote_repository.exists_by_id(sample_vote.vote_id)

    def test_delete_by_id(self, vote_repository, sample_vote):
        """Test deleting vote by ID"""
        vote_repository.save(sample_vote)
        assert vote_repository.exists_by_id(sample_vote.vote_id)

        result = vote_repository.delete_by_id(sample_vote.vote_id)
        assert result is True
        assert not vote_repository.exists_by_id(sample_vote.vote_id)

    def test_count(self, vote_repository):
        """Test counting votes"""
        assert vote_repository.count() == 0

        now = datetime.now()
        for i in range(5):
            vote = Vote(f"vote_{i}", f"user_{i}", "election_123", f"candidate_{i}", now)
            vote_repository.save(vote)

        assert vote_repository.count() == 5

    def test_find_by_user_id(self, vote_repository):
        """Test finding votes by user ID"""
        now = datetime.now()

        # Create votes for different users
        user_votes = {}
        for user_id in ["user_a", "user_b", "user_c"]:
            user_votes[user_id] = []
            for i in range(2):
                vote = Vote(f"vote_{user_id}_{i}", user_id, "election_123",
                          f"candidate_{i}", now)
                user_votes[user_id].append(vote)
                vote_repository.save(vote)

        # Test finding votes for each user
        for user_id, expected_votes in user_votes.items():
            found_votes = vote_repository.find_by_user_id(user_id)
            assert len(found_votes) == 2
            assert set(found_votes) == set(expected_votes)

    def test_find_by_election_id(self, vote_repository):
        """Test finding votes by election ID"""
        now = datetime.now()

        # Create votes for different elections
        election_votes = {}
        for election_id in ["election_a", "election_b"]:
            election_votes[election_id] = []
            for i in range(3):
                vote = Vote(f"vote_{election_id}_{i}", f"user_{i}", election_id,
                          "candidate_123", now)
                election_votes[election_id].append(vote)
                vote_repository.save(vote)

        # Test finding votes for each election
        for election_id, expected_votes in election_votes.items():
            found_votes = vote_repository.find_by_election_id(election_id)
            assert len(found_votes) == 3
            assert set(found_votes) == set(expected_votes)

    def test_find_by_candidate_id(self, vote_repository):
        """Test finding votes by candidate ID"""
        now = datetime.now()

        # Create votes for different candidates
        candidate_votes = {}
        for candidate_id in ["candidate_a", "candidate_b"]:
            candidate_votes[candidate_id] = []
            for i in range(2):
                vote = Vote(f"vote_{candidate_id}_{i}", f"user_{i}", "election_123",
                          candidate_id, now)
                candidate_votes[candidate_id].append(vote)
                vote_repository.save(vote)

        # Test finding votes for each candidate
        for candidate_id, expected_votes in candidate_votes.items():
            found_votes = vote_repository.find_by_candidate_id(candidate_id)
            assert len(found_votes) == 2
            assert set(found_votes) == set(expected_votes)

    def test_find_by_status(self, vote_repository):
        """Test finding votes by status"""
        now = datetime.now()

        # Create votes with different statuses
        cast_vote = Vote("cast", "user_1", "election_1", "candidate_1", now)
        verified_vote = Vote("verified", "user_2", "election_2", "candidate_2", now)
        invalid_vote = Vote("invalid", "user_3", "election_3", "candidate_3", now)

        verified_vote.verify("hash_123")
        invalid_vote.invalidate()

        vote_repository.save(cast_vote)
        vote_repository.save(verified_vote)
        vote_repository.save(invalid_vote)

        # Test finding by each status
        cast_votes = vote_repository.find_by_status(VoteStatus.CAST)
        verified_votes = vote_repository.find_by_status(VoteStatus.VERIFIED)
        invalid_votes = vote_repository.find_by_status(VoteStatus.INVALID)

        assert len(cast_votes) == 1
        assert len(verified_votes) == 1
        assert len(invalid_votes) == 1

        assert cast_votes[0] == cast_vote
        assert verified_votes[0] == verified_vote
        assert invalid_votes[0] == invalid_vote

    def test_find_verified_votes(self, vote_repository):
        """Test finding verified votes"""
        now = datetime.now()

        verified_vote = Vote("verified", "user_1", "election_1", "candidate_1", now)
        unverified_vote = Vote("unverified", "user_2", "election_2", "candidate_2", now)

        verified_vote.verify("hash_123")

        vote_repository.save(verified_vote)
        vote_repository.save(unverified_vote)

        verified_votes = vote_repository.find_verified_votes()
        assert len(verified_votes) == 1
        assert verified_votes[0] == verified_vote

    def test_find_invalid_votes(self, vote_repository):
        """Test finding invalid votes"""
        now = datetime.now()

        valid_vote = Vote("valid", "user_1", "election_1", "candidate_1", now)
        invalid_vote = Vote("invalid", "user_2", "election_2", "candidate_2", now)

        invalid_vote.invalidate()

        vote_repository.save(valid_vote)
        vote_repository.save(invalid_vote)

        invalid_votes = vote_repository.find_invalid_votes()
        assert len(invalid_votes) == 1
        assert invalid_votes[0] == invalid_vote

    def test_find_votes_by_user_and_election(self, vote_repository):
        """Test finding votes by user and election combination"""
        now = datetime.now()

        # Create votes for different user-election combinations
        votes_data = [
            ("user_a", "election_1"),
            ("user_a", "election_2"),
            ("user_b", "election_1"),
            ("user_b", "election_2"),
        ]

        votes = []
        for i, (user_id, election_id) in enumerate(votes_data):
            vote = Vote(f"vote_{i}", user_id, election_id, "candidate_123", now)
            votes.append(vote)
            vote_repository.save(vote)

        # Test finding votes for specific user-election combinations
        user_a_election_1 = vote_repository.find_votes_by_user_and_election("user_a", "election_1")
        assert len(user_a_election_1) == 1
        assert user_a_election_1[0].user_id == "user_a"
        assert user_a_election_1[0].election_id == "election_1"

        user_b_election_2 = vote_repository.find_votes_by_user_and_election("user_b", "election_2")
        assert len(user_b_election_2) == 1
        assert user_b_election_2[0].user_id == "user_b"
        assert user_b_election_2[0].election_id == "election_2"

    def test_count_by_election(self, vote_repository):
        """Test counting votes by election"""
        now = datetime.now()

        # Create votes for different elections
        for i in range(5):
            vote = Vote(f"vote_e1_{i}", f"user_{i}", "election_1", "candidate_1", now)
            vote_repository.save(vote)

        for i in range(3):
            vote = Vote(f"vote_e2_{i}", f"user_{i}", "election_2", "candidate_2", now)
            vote_repository.save(vote)

        assert vote_repository.count_by_election("election_1") == 5
        assert vote_repository.count_by_election("election_2") == 3
        assert vote_repository.count_by_election("non_existent") == 0

    def test_count_by_candidate(self, vote_repository):
        """Test counting votes by candidate"""
        now = datetime.now()

        # Create votes for different candidates
        for i in range(4):
            vote = Vote(f"vote_c1_{i}", "user_1", "election_1", "candidate_1", now)
            vote_repository.save(vote)

        for i in range(6):
            vote = Vote(f"vote_c2_{i}", "user_2", "election_1", "candidate_2", now)
            vote_repository.save(vote)

        assert vote_repository.count_by_candidate("candidate_1") == 4
        assert vote_repository.count_by_candidate("candidate_2") == 6
        assert vote_repository.count_by_candidate("non_existent") == 0

    def test_get_vote_statistics_by_election(self, vote_repository):
        """Test getting vote statistics by election"""
        now = datetime.now()

        # Create votes for an election
        candidates = ["candidate_a", "candidate_b", "candidate_c"]
        vote_counts = [5, 3, 7]

        for candidate, count in zip(candidates, vote_counts):
            for i in range(count):
                vote = Vote(f"vote_{candidate}_{i}", f"user_{i}", "election_123", candidate, now)
                vote_repository.save(vote)

        stats = vote_repository.get_vote_statistics_by_election("election_123")

        assert stats["total_votes"] == 15
        assert stats["unique_candidates"] == 3
        assert stats["candidate_breakdown"]["candidate_a"] == 5
        assert stats["candidate_breakdown"]["candidate_b"] == 3
        assert stats["candidate_breakdown"]["candidate_c"] == 7

    def test_thread_safety_operations(self, vote_repository):
        """Test thread safety of vote repository operations"""
        results = []
        errors = []

        def vote_operation(operation_id):
            try:
                now = datetime.now()
                vote = Vote(f"vote_{operation_id}", f"user_{operation_id}", "election_123",
                          "candidate_123", now)
                vote_repository.save(vote)
                results.append(operation_id)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(20):
            thread = threading.Thread(target=vote_operation, args=[i])
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        assert len(results) == 20
        assert len(errors) == 0
        assert vote_repository.count() == 20

    def test_bulk_operations(self, vote_repository):
        """Test bulk operations"""
        now = datetime.now()
        votes = []

        for i in range(200):
            vote = Vote(f"vote_{i}", f"user_{i % 10}", "election_123",
                      f"candidate_{i % 5}", now)
            votes.append(vote)
            vote_repository.save(vote)

        assert vote_repository.count() == 200

        # Bulk delete
        for vote in votes:
            vote_repository.delete_by_id(vote.vote_id)

        assert vote_repository.count() == 0

    def test_status_transition_tracking(self, vote_repository):
        """Test status transition tracking"""
        now = datetime.now()
        vote = Vote("vote_123", "user_1", "election_1", "candidate_1", now)

        vote_repository.save(vote)

        # Initially cast
        cast_votes = vote_repository.find_by_status(VoteStatus.CAST)
        assert len(cast_votes) == 1

        # Verify vote
        vote.verify("hash_123")

        verified_votes = vote_repository.find_by_status(VoteStatus.VERIFIED)
        cast_votes_after = vote_repository.find_by_status(VoteStatus.CAST)

        assert len(verified_votes) == 1
        assert len(cast_votes_after) == 0

    def test_verification_management(self, vote_repository):
        """Test verification management operations"""
        now = datetime.now()

        # Create multiple votes
        votes = []
        for i in range(5):
            vote = Vote(f"vote_{i}", f"user_{i}", "election_1", "candidate_1", now)
            votes.append(vote)
            vote_repository.save(vote)

        # Verify some votes
        for i in range(3):
            votes[i].verify(f"hash_{i}")

        verified_votes = vote_repository.find_verified_votes()
        assert len(verified_votes) == 3

        # Invalidate one vote
        votes[0].invalidate()

        verified_after = vote_repository.find_verified_votes()
        invalid_votes = vote_repository.find_invalid_votes()

        assert len(verified_after) == 2
        assert len(invalid_votes) == 1

    def test_repository_isolation(self):
        """Test repository isolation"""
        repo1 = InMemoryVoteRepository()
        repo2 = InMemoryVoteRepository()

        now = datetime.now()
        vote = Vote("vote_123", "user_1", "election_1", "candidate_1", now)
        repo1.save(vote)

        assert repo1.exists_by_id("vote_123")
        assert not repo2.exists_by_id("vote_123")

    def test_error_handling(self, vote_repository):
        """Test error handling"""
        with pytest.raises(AttributeError):
            vote_repository.save(None)

        with pytest.raises(TypeError):
            vote_repository.find_by_id(None)

    def test_large_dataset_queries(self, vote_repository):
        """Test queries on large datasets"""
        now = datetime.now()

        # Create many votes
        for i in range(1000):
            vote = Vote(f"vote_{i}", f"user_{i % 100}", f"election_{i % 10}",
                      f"candidate_{i % 5}", now)
            vote_repository.save(vote)

        assert vote_repository.count() == 1000

        # Test various queries still work
        all_votes = vote_repository.find_all()
        assert len(all_votes) == 1000

        user_votes = vote_repository.find_by_user_id("user_5")
        assert len(user_votes) == 10  # 1000 / 100 = 10

        election_votes = vote_repository.find_by_election_id("election_3")
        assert len(election_votes) == 100  # 1000 / 10 = 100

        candidate_votes = vote_repository.find_by_candidate_id("candidate_2")
        assert len(candidate_votes) == 200  # 1000 / 5 = 200
