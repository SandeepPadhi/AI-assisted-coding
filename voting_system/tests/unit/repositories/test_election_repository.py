"""
Unit tests for Election Repository.

Tests cover:
- Election CRUD operations
- Status-based queries
- Date-based queries
- Thread-safe operations
- Candidate relationship management
"""

import pytest
import threading
from datetime import datetime, timedelta
from entities import Election, ElectionStatus
from repositories import InMemoryElectionRepository


class TestInMemoryElectionRepository:
    """Test cases for InMemoryElectionRepository"""

    def test_repository_initialization(self, election_repository):
        """Test repository initialization"""
        assert election_repository is not None
        assert hasattr(election_repository, '_storage')
        assert hasattr(election_repository, '_lock')

    def test_save_election_valid(self, election_repository, sample_election):
        """Test saving a valid election"""
        election_repository.save(sample_election)

        assert sample_election.election_id in election_repository._storage
        assert election_repository._storage[sample_election.election_id] == sample_election

    def test_find_by_id_existing(self, election_repository, sample_election):
        """Test finding existing election by ID"""
        election_repository.save(sample_election)

        found_election = election_repository.find_by_id(sample_election.election_id)

        assert found_election is not None
        assert found_election == sample_election

    def test_find_all_empty(self, election_repository):
        """Test finding all elections when repository is empty"""
        elections = election_repository.find_all()
        assert isinstance(elections, list)
        assert len(elections) == 0

    def test_find_all_with_elections(self, election_repository):
        """Test finding all elections"""
        elections = []
        now = datetime.now()

        for i in range(3):
            election = Election(f"election_{i}", f"Election {i}", f"Description {i}",
                              now + timedelta(hours=i+1), now + timedelta(hours=i+2),
                              ["candidate_1", "candidate_2"])
            elections.append(election)
            election_repository.save(election)

        found_elections = election_repository.find_all()
        assert len(found_elections) == 3
        assert set(found_elections) == set(elections)

    def test_exists_by_id(self, election_repository, sample_election):
        """Test checking if election exists by ID"""
        assert not election_repository.exists_by_id(sample_election.election_id)

        election_repository.save(sample_election)
        assert election_repository.exists_by_id(sample_election.election_id)

    def test_delete_by_id(self, election_repository, sample_election):
        """Test deleting election by ID"""
        election_repository.save(sample_election)
        assert election_repository.exists_by_id(sample_election.election_id)

        result = election_repository.delete_by_id(sample_election.election_id)
        assert result is True
        assert not election_repository.exists_by_id(sample_election.election_id)

    def test_count(self, election_repository):
        """Test counting elections"""
        assert election_repository.count() == 0

        now = datetime.now()
        for i in range(5):
            election = Election(f"election_{i}", f"Election {i}", "Description",
                              now + timedelta(hours=1), now + timedelta(hours=2),
                              ["candidate_1", "candidate_2"])
            election_repository.save(election)

        assert election_repository.count() == 5

    def test_find_by_status(self, election_repository):
        """Test finding elections by status"""
        now = datetime.now()

        # Create elections with different statuses
        scheduled = Election("scheduled", "Scheduled Election", "Desc",
                           now + timedelta(hours=1), now + timedelta(hours=2),
                           ["c1", "c2"])

        active = Election("active", "Active Election", "Desc",
                         now + timedelta(hours=1), now + timedelta(hours=2),
                         ["c1", "c2"])
        active.start_election()

        completed = Election("completed", "Completed Election", "Desc",
                           now + timedelta(hours=1), now + timedelta(hours=2),
                           ["c1", "c2"])
        completed.start_election()
        completed.complete_election()

        cancelled = Election("cancelled", "Cancelled Election", "Desc",
                           now + timedelta(hours=1), now + timedelta(hours=2),
                           ["c1", "c2"])
        cancelled.cancel_election()

        election_repository.save(scheduled)
        election_repository.save(active)
        election_repository.save(completed)
        election_repository.save(cancelled)

        # Test finding by each status
        scheduled_elections = election_repository.find_by_status(ElectionStatus.SCHEDULED)
        active_elections = election_repository.find_by_status(ElectionStatus.ACTIVE)
        completed_elections = election_repository.find_by_status(ElectionStatus.COMPLETED)
        cancelled_elections = election_repository.find_by_status(ElectionStatus.CANCELLED)

        assert len(scheduled_elections) == 1
        assert len(active_elections) == 1
        assert len(completed_elections) == 1
        assert len(cancelled_elections) == 1

        assert scheduled_elections[0] == scheduled
        assert active_elections[0] == active
        assert completed_elections[0] == completed
        assert cancelled_elections[0] == cancelled

    def test_find_active_elections(self, election_repository):
        """Test finding active elections"""
        now = datetime.now()

        # Create active and inactive elections
        active1 = Election("active1", "Active 1", "Desc",
                          now + timedelta(hours=1), now + timedelta(hours=2), ["c1", "c2"])
        active2 = Election("active2", "Active 2", "Desc",
                          now + timedelta(hours=1), now + timedelta(hours=2), ["c1", "c2"])
        inactive = Election("inactive", "Inactive", "Desc",
                           now + timedelta(hours=1), now + timedelta(hours=2), ["c1", "c2"])

        active1.start_election()
        active2.start_election()
        # inactive remains scheduled

        election_repository.save(active1)
        election_repository.save(active2)
        election_repository.save(inactive)

        active_elections = election_repository.find_active_elections()
        assert len(active_elections) == 2
        assert set(active_elections) == {active1, active2}

    def test_find_upcoming_elections(self, election_repository):
        """Test finding upcoming elections"""
        now = datetime.now()
        future = now + timedelta(hours=2)

        # Create elections at different times
        upcoming1 = Election("upcoming1", "Upcoming 1", "Desc",
                           now + timedelta(minutes=30), now + timedelta(hours=1), ["c1", "c2"])
        upcoming2 = Election("upcoming2", "Upcoming 2", "Desc",
                           now + timedelta(hours=1), now + timedelta(hours=2), ["c1", "c2"])
        past = Election("past", "Past", "Desc",
                       now - timedelta(hours=2), now - timedelta(hours=1), ["c1", "c2"])

        election_repository.save(upcoming1)
        election_repository.save(upcoming2)
        election_repository.save(past)

        upcoming_elections = election_repository.find_upcoming_elections()
        assert len(upcoming_elections) == 2
        assert set(upcoming_elections) == {upcoming1, upcoming2}

    def test_find_elections_by_date_range(self, election_repository):
        """Test finding elections by date range"""
        # Create elections with different date ranges
        base_date = datetime.now()

        elections_data = [
            (base_date + timedelta(days=1), base_date + timedelta(days=2)),  # Within range
            (base_date + timedelta(days=3), base_date + timedelta(days=4)),  # Within range
            (base_date + timedelta(days=10), base_date + timedelta(days=11)), # Outside range
            (base_date - timedelta(days=5), base_date - timedelta(days=4)),  # Outside range
        ]

        elections = []
        for i, (start_date, end_date) in enumerate(elections_data):
            election = Election(f"election_{i}", f"Election {i}", "Description",
                              start_date, end_date, ["c1", "c2"])
            elections.append(election)
            election_repository.save(election)

        # Find elections in date range
        start_range = base_date + timedelta(days=1)
        end_range = base_date + timedelta(days=5)

        found_elections = election_repository.find_elections_by_date_range(start_range, end_range)
        assert len(found_elections) == 2
        assert set(found_elections) == {elections[0], elections[1]}

    def test_find_elections_with_candidate(self, election_repository):
        """Test finding elections that include a specific candidate"""
        # Create elections with different candidate sets
        election1 = Election("election1", "Election 1", "Desc",
                           datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=2),
                           ["candidate_a", "candidate_b"])

        election2 = Election("election2", "Election 2", "Desc",
                           datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=2),
                           ["candidate_b", "candidate_c"])

        election3 = Election("election3", "Election 3", "Desc",
                           datetime.now() + timedelta(hours=1), datetime.now() + timedelta(hours=2),
                           ["candidate_c", "candidate_d"])

        election_repository.save(election1)
        election_repository.save(election2)
        election_repository.save(election3)

        # Find elections with candidate_b
        elections_with_b = election_repository.find_elections_with_candidate("candidate_b")
        assert len(elections_with_b) == 2
        assert set(elections_with_b) == {election1, election2}

        # Find elections with candidate_a
        elections_with_a = election_repository.find_elections_with_candidate("candidate_a")
        assert len(elections_with_a) == 1
        assert elections_with_a[0] == election1

    def test_thread_safety_operations(self, election_repository):
        """Test thread safety of election repository operations"""
        results = []
        errors = []

        def election_operation(operation_id):
            try:
                now = datetime.now()
                election = Election(f"election_{operation_id}", f"Election {operation_id}", "Description",
                                  now + timedelta(hours=1), now + timedelta(hours=2),
                                  ["candidate_1", "candidate_2"])
                election_repository.save(election)
                results.append(operation_id)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(15):
            thread = threading.Thread(target=election_operation, args=[i])
            threads.append(thread)
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        assert len(results) == 15
        assert len(errors) == 0
        assert election_repository.count() == 15

    def test_bulk_operations(self, election_repository):
        """Test bulk operations"""
        now = datetime.now()
        elections = []

        for i in range(100):
            election = Election(f"election_{i}", f"Election {i}", "Description",
                              now + timedelta(hours=i+1), now + timedelta(hours=i+2),
                              ["candidate_1", "candidate_2"])
            elections.append(election)
            election_repository.save(election)

        assert election_repository.count() == 100

        # Bulk delete
        for election in elections:
            election_repository.delete_by_id(election.election_id)

        assert election_repository.count() == 0

    def test_status_transition_tracking(self, election_repository):
        """Test that repository tracks status changes"""
        now = datetime.now()
        election = Election("election_123", "Test Election", "Description",
                          now + timedelta(hours=1), now + timedelta(hours=2),
                          ["c1", "c2"])

        election_repository.save(election)

        # Initially scheduled
        scheduled = election_repository.find_by_status(ElectionStatus.SCHEDULED)
        assert len(scheduled) == 1

        # Start election
        election.start_election()
        # Note: Since we're working with the same object reference, the repository
        # will see the updated status

        active = election_repository.find_by_status(ElectionStatus.ACTIVE)
        assert len(active) == 1

    def test_date_based_queries_edge_cases(self, election_repository):
        """Test edge cases in date-based queries"""
        now = datetime.now()

        # Create elections at exact boundaries
        election_at_start = Election("start", "At Start", "Desc",
                                   now, now + timedelta(hours=1), ["c1", "c2"])
        election_at_end = Election("end", "At End", "Desc",
                                 now + timedelta(hours=2), now + timedelta(hours=3), ["c1", "c2"])

        election_repository.save(election_at_start)
        election_repository.save(election_at_end)

        # Test range that includes start boundary
        range_elections = election_repository.find_elections_by_date_range(now, now + timedelta(hours=1))
        assert len(range_elections) == 1
        assert range_elections[0] == election_at_start

    def test_candidate_relationship_integrity(self, election_repository):
        """Test candidate relationship integrity"""
        now = datetime.now()

        # Create election with candidates
        election = Election("election_123", "Test", "Desc",
                          now + timedelta(hours=1), now + timedelta(hours=2),
                          ["candidate_a", "candidate_b", "candidate_c"])

        election_repository.save(election)

        # Test finding elections with each candidate
        for candidate_id in ["candidate_a", "candidate_b", "candidate_c"]:
            elections_with_candidate = election_repository.find_elections_with_candidate(candidate_id)
            assert len(elections_with_candidate) == 1
            assert elections_with_candidate[0] == election

        # Test non-existent candidate
        no_elections = election_repository.find_elections_with_candidate("non_existent")
        assert len(no_elections) == 0

    def test_repository_isolation(self):
        """Test repository isolation"""
        repo1 = InMemoryElectionRepository()
        repo2 = InMemoryElectionRepository()

        now = datetime.now()
        election = Election("election_123", "Test", "Desc",
                          now + timedelta(hours=1), now + timedelta(hours=2), ["c1", "c2"])
        repo1.save(election)

        assert repo1.exists_by_id("election_123")
        assert not repo2.exists_by_id("election_123")

    def test_error_handling(self, election_repository):
        """Test error handling"""
        with pytest.raises(AttributeError):
            election_repository.save(None)

        with pytest.raises(TypeError):
            election_repository.find_by_id(None)

    def test_large_dataset_queries(self, election_repository):
        """Test queries on large datasets"""
        now = datetime.now()

        # Create many elections
        for i in range(500):
            election = Election(f"election_{i}", f"Election {i}", "Description",
                              now + timedelta(hours=i+1), now + timedelta(hours=i+2),
                              ["candidate_1", "candidate_2"])
            election_repository.save(election)

        assert election_repository.count() == 500

        # Test various queries still work
        all_elections = election_repository.find_all()
        assert len(all_elections) == 500

        scheduled_elections = election_repository.find_by_status(ElectionStatus.SCHEDULED)
        assert len(scheduled_elections) == 500

        upcoming_elections = election_repository.find_upcoming_elections()
        assert len(upcoming_elections) == 500
